#!/usr/bin/env python3
"""run.py: plan, send and track one model run. Append-only; safe to stop and restart.

    python harness/run.py plan  --model qwen3.5-9b --scope pilot            # writes runs/<run_id>/
    python harness/run.py go    runs/<run_id> --base-url http://127.0.0.1:8000/v1
    python harness/run.py status runs/<run_id>

plan    picks the requests, removes exact repeats (the `none` prompt is the same at k = 1, 3, 5, so it is
        sent once and answers all three), shuffles the order with a fixed seed (conditions interleaved,
        so a server or provider change mid-run cannot line up with one condition), and writes
        planned.jsonl plus manifest.json with the EXPECTED number of outputs and the hash of every
        data file. Nothing is sent.
go      sends the planned requests. Every model response is written once, as it arrives, to raw.jsonl
        (raw_restricted.jsonl for the review set: that file must never be committed). A response is a
        result even when it is broken JSON, and so is HTTP 400 or 422 (the server refused that request,
        for example a schema it cannot enforce); a result is never sent again. Transport failures (no
        response, 408, 424, 429, 5xx) are retried, and every attempt is logged in attempts.jsonl.
        HTTP 401, 403, 404 or 413 (wrong key, model id, region or size) stop the whole run and record
        nothing, and so does a session whose first 10 results contain no ok (circuit breaker).
        Restarting `go` skips requests that already have a result. A local (vLLM) run needs
        --server-info. At the end it writes SUMMARY.md: expected vs actual, finish reasons, parse rungs.
        --max-usd stops sending once the run's cost reaches that many USD: the cost of each reply is its
        usage (prompt and completion tokens, reasoning included) times the model's `price` in
        configs/models.yaml, summed over every session of the run; requests already in flight are
        counted at the run's mean cost so far, so the total overshoots by at most a few replies. The
        requests not sent stay planned; `go` with a higher cap carries on. Exit code 3.
status  prints expected / done / missing for a run.
spend   the cost so far of one or more runs, and their total (for a cap shared by several models).

Scopes:
  pilot   the 60 pilot documents: none (once per document), max_k_shown, min_k_shown and min_k_enforced
          at k = 3 and 5. 7 prompts per document, 420 per model.
  full    every request of the pilot + full documents (26,784 planned ids with min_k_shown_fewer_ok; 25,668
          sent after the `none` repeats are removed). A model's `conditions` list in configs/models.yaml can
          narrow it (22,320 sends for a Bedrock model).
  robustness  the two robustness arms on the pilot documents (data/requests_robustness.jsonl): LlamaIndex
          schema block (no 2-item example) and a base sentence without "all"; none, max_k_shown,
          min_k_shown, min_k_enforced at k = 3 and 5. 840 sends per model.
  dev     the 312 reserve documents (never in the study; data/requests_dev.jsonl), same 4 conditions at
          k = 3 and 5: model outputs here are what the item matcher is tuned on. 2,184 sends per model.
  custom  filters only (--splits, --conditions, --k, --wordings, --sets, --docs).
  --repeat-of RUN  the repeat check: the same requests as a seeded sample (--repeat-n, default 300) of an
          earlier run, under a new run id; compare with harness/repeat_check.py.
"""
import argparse
import datetime as dt
import fcntl
import json
import os
import platform
import random
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

PILOT_CONDITIONS = ["none", "max_k_shown", "min_k_shown", "min_k_enforced"]
# What an HTTP status means for a request:
RETRY_STATUS = {408, 409, 424, 425, 429, 500, 502, 503, 504}   # transport: retried, every attempt logged
RESULT_STATUS = {400, 422}        # the server refused THIS request (e.g. a schema it cannot enforce): a result
ABORT_STATUS = {401, 403, 404, 413}   # wrong key, model id, region or size: the whole run stops, nothing recorded
FINAL = lambda s: s == "ok" or s in {f"http_{c}" for c in RESULT_STATUS}


def build_body(mcfg, req_defaults, message, response_format=None, logprobs=0, max_tokens=None, seed=None):
    """The one request body every script sends (run.py and enforce_test.py), so they cannot drift.

    Uses max_completion_tokens (vLLM v0.31.0 prefers it over the deprecated max_tokens, and Bedrock's
    OpenAI-compatible endpoint maps it to maxTokens); a model can name another field with
    `max_tokens_field` (Together documents only max_tokens). A model's `request:` block in models.yaml
    overrides the defaults (used by the sampled-decoding check and the thinking pair). `extra_body` is merged in last, for
    provider-specific fields such as Together's `reasoning: {enabled: false}`.
    """
    rq = {**req_defaults, **(mcfg.get("request") or {})}
    b = {"model": mcfg.get("api_model") or mcfg.get("served_name") or mcfg["hf_repo"],
         "messages": [{"role": "user", "content": message}],
         "temperature": rq["temperature"], "top_p": rq["top_p"],
         mcfg.get("max_tokens_field", "max_completion_tokens"):
             max_tokens or mcfg.get("max_tokens", rq["max_tokens"])}
    for extra in ("top_k", "presence_penalty", "repetition_penalty"):
        if extra in rq:
            b[extra] = rq[extra]
    if mcfg.get("send_seed", True):
        b["seed"] = rq["seed"] if seed is None else seed
    if mcfg.get("chat_template_kwargs") and mcfg.get("backend") == "vllm":
        b["chat_template_kwargs"] = mcfg["chat_template_kwargs"]
    if mcfg.get("reasoning_effort"):
        b["reasoning_effort"] = mcfg["reasoning_effort"]
    if response_format:
        b["response_format"] = response_format
    if logprobs:
        b["logprobs"], b["top_logprobs"] = True, logprobs
    thinks = mcfg.get("reasoning_effort") or (mcfg.get("chat_template_kwargs") or {}).get("enable_thinking")
    if mcfg.get("backend") == "vllm" and not thinks:
        # the generated token ids, so teacher_forced.py reads the exact path; not for thinking runs, which it
        # does not read and whose ids (thousands per reply) would push raw.jsonl past GitHub's 100 MB limit
        b["return_token_ids"] = True
    for key, value in (mcfg.get("extra_body") or {}).items():
        b[key] = value
    return b


def cost_usd(usage, price):
    """USD for one reply: usage tokens times the model's price (USD per million tokens, `in` and `out`).
    Completion tokens include reasoning tokens on every provider used here (OpenAI usage format). None
    when the price or the usage is missing."""
    if not price or not isinstance(usage, dict):
        return None
    tin, tout = usage.get("prompt_tokens") or 0, usage.get("completion_tokens") or 0
    return (tin * price["in"] + tout * price["out"]) / 1e6


def price_of(manifest):
    """The price a run is charged at: the one stored with the run when it was planned, else the current
    entry in configs/models.yaml (runs planned before prices were added)."""
    p = (manifest.get("model") or {}).get("price")
    if p:
        return p
    try:
        return (load_models()[1].get(manifest["model_key"]) or {}).get("price")
    except (OSError, KeyError):
        return None


def json_schema_format(field, schema):
    return {"type": "json_schema", "json_schema": {"name": field, "schema": schema, "strict": True}}


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds")


def load_models():
    cfg = yaml.safe_load((common.ROOT / "configs" / "models.yaml").read_text(encoding="utf-8"))
    return cfg["defaults"], cfg["models"]


def git_state():
    def run(*a):
        try:
            return subprocess.run(["git", *a], cwd=common.ROOT, capture_output=True, text=True, timeout=10).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            return ""
    return {"commit": run("rev-parse", "HEAD"), "branch": run("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty_files": [l for l in run("status", "--porcelain").splitlines()
                            if l and not l[3:].startswith("runs/")][:50]}


# ---------------------------------------------------------------------------------------------
def select(args, model_cfg):
    reqs = common.load_requests()
    docs = common.load_documents()
    allowed = set(model_cfg.get("conditions") or [])
    out = []
    for r in reqs:
        if r["doc_id"] not in docs:
            raise SystemExit(f"{r['doc_id']} has no text: rebuild data/ (python data/build.py) to create data/local/")
        arm = r.get("arm")
        if args.scope == "robustness":
            if arm in (None, "dev"):
                continue
        elif args.scope == "dev":
            if arm != "dev":
                continue
        elif arm:            # pilot, full and custom never include robustness or dev requests
            continue
        if args.scope in ("robustness", "dev"):
            keep = r["k"] in (3, 5) or r["condition"] == "none"
        elif args.scope == "pilot":
            keep = (r["split"] == "pilot" and r["condition"] in PILOT_CONDITIONS
                    and (r["k"] in (3, 5) or r["condition"] == "none"))
        elif args.scope == "full":
            keep = r["split"] in ("pilot", "full")
        else:
            keep = True
        if args.splits:
            keep &= r["split"] in args.splits
        if args.conditions:
            keep &= r["condition"] in args.conditions
        if args.k:
            keep &= r["k"] in args.k or (args.scope == "pilot" and r["condition"] == "none")
        if args.wordings:
            keep &= r["wording_id"] in args.wordings
        if args.sets:
            keep &= r["set"] in args.sets
        if args.docs:
            keep &= r["doc_id"] in args.docs
        if allowed:
            keep &= r["condition"] in allowed
        if keep:
            out.append(r)
    return out, docs


def plan(args):
    defaults, models = load_models()
    if args.model not in models:
        raise SystemExit(f"unknown model key {args.model}; see configs/models.yaml")
    mcfg = models[args.model]
    if args.docs_file:
        args.docs = {l.strip() for l in Path(args.docs_file).read_text().splitlines() if l.strip()}
    if args.repeat_of:
        # the repeat check: the same planned requests as an earlier run, a seeded sample of them
        src = common.read_jsonl(Path(args.repeat_of) / "planned.jsonl")
        pick = {r["request_id"] for r in random.Random(20261015).sample(src, min(args.repeat_n, len(src)))}
        args.scope, args.docs = "repeat", None
        req_index = {r["request_id"]: r for r in common.load_requests()}
        reqs, docs = [req_index[i] for i in sorted(pick)], common.load_documents()
    else:
        reqs, docs = select(args, mcfg)
    if not reqs:
        raise SystemExit("no request matches these filters")
    prompts = common.load_prompts()
    # one send per distinct (message, schema sent, enforced?) -> the other ids reuse its answer
    canon, order = {}, []
    for r in reqs:
        msg = common.user_message(r, docs[r["doc_id"]], prompts)
        sent_schema = common.schema_of(r, prompts) if r["enforce_schema"] else None
        key = (common.sha256_text(msg), json.dumps(sent_schema, sort_keys=True), r["enforce_schema"])
        if key in canon:
            canon[key]["also_answers"].append(r["request_id"])
            continue
        row = {"request_id": r["request_id"], "also_answers": [], "doc_id": r["doc_id"], "set": r["set"],
               "split": r["split"], "condition": r["condition"], "k": r["k"], "n": r["n"],
               "wording_id": r["wording_id"], "schema_id": r["schema_id"], "enforce_schema": r["enforce_schema"],
               "prompt_sha256": key[0], "restricted": not docs[r["doc_id"]].get("redistributable", True),
               "arm": r.get("arm")}
        canon[key] = row
        order.append(row)
    seed = args.seed if args.seed is not None else 20261014
    random.Random(seed).shuffle(order)
    run_id = args.run_id or f"{dt.date.today().isoformat()}_{args.model}_{args.scope}"
    run_dir = common.ROOT / "runs" / run_id
    if run_dir.exists() and any(run_dir.glob("raw*.jsonl")):
        raise SystemExit(f"{run_dir} already has outputs; pick a new --run-id (runs are never overwritten)")
    run_dir.mkdir(parents=True, exist_ok=True)
    with open(run_dir / "planned.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for row in order:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    req_defaults = dict(defaults["request"])
    manifest = {
        "run_id": run_id, "created_utc": now(), "harness_version": common.HARNESS_VERSION,
        "model_key": args.model, "model": mcfg, "request_defaults": req_defaults,
        "scope": args.scope, "filters": {k: (sorted(v) if isinstance(v, (set, list)) else v) for k, v in
                                         vars(args).items() if k in ("splits", "conditions", "k", "wordings", "sets") and v},
        "docs_filter_count": len(args.docs) if args.docs else None,
        "shuffle_seed": seed, "request_seed": args.request_seed,
        "repeat_of": str(args.repeat_of) if args.repeat_of else None,
        "expected_outputs": len(order),
        "expected_request_ids_covered": sum(1 + len(r["also_answers"]) for r in order),
        "by_condition": dict(Counter(r["condition"] for r in order)),
        "documents": len({r["doc_id"] for r in order}),
        "restricted_outputs_expected": sum(r["restricted"] for r in order),
        "data_sha256": common.data_hashes(), "git": git_state(),
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print(f"planned {run_dir}: {manifest['expected_outputs']} requests to send, covering "
          f"{manifest['expected_request_ids_covered']} request ids on {manifest['documents']} documents")
    print("by condition:", manifest["by_condition"])
    return run_dir


# ---------------------------------------------------------------------------------------------
class Sender:
    def __init__(self, run_dir, base_url, api_key, timeout, max_attempts):
        self.run_dir = Path(run_dir)
        self.base = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.max_attempts = max_attempts
        self.lock = threading.Lock()
        self.manifest = json.loads((self.run_dir / "manifest.json").read_text(encoding="utf-8"))
        self.logprobs = 0
        self.mcfg = self.manifest["model"]
        self.req_defaults = self.manifest["request_defaults"]
        self.docs = common.load_documents()
        self.prompts = common.load_prompts()
        self._req_index = {r["request_id"]: r for r in common.load_requests()}
        self.abort = None                 # set to a reason string: workers stop sending
        self.first_statuses = []          # circuit breaker on the first results of a session
        self.breaker = True
        self.files = {False: open(self.run_dir / "raw.jsonl", "a", encoding="utf-8", newline="\n"),
                      True: open(self.run_dir / "raw_restricted.jsonl", "a", encoding="utf-8", newline="\n")}
        self.attempts = open(self.run_dir / "attempts.jsonl", "a", encoding="utf-8", newline="\n")
        self.written = 0
        # spending stop: every reply's cost is added as it arrives; earlier sessions count too
        self.price = price_of(self.manifest)
        self.max_usd = None
        self.spent, self.n_costed = run_cost(self.run_dir, self.price)
        self.in_flight = 0
        self.budget_stop = None

    def _admit(self):
        """True if one more request may be sent under --max-usd (in-flight requests at the mean cost)."""
        with self.lock:
            if self.max_usd is not None:
                mean = self.spent / self.n_costed if self.n_costed else 0.0
                if self.spent + self.in_flight * mean >= self.max_usd:
                    self.budget_stop = self.budget_stop or (
                        f"spending stop: {self.spent:.4f} USD spent (cap {self.max_usd} USD), "
                        f"{self.in_flight} requests still in flight")
                    return False
            self.in_flight += 1
            return True

    def body(self, row):
        full = self._req_index[row.get("source_request_id") or row["request_id"]]
        msg = common.user_message(full, self.docs[row["doc_id"]], self.prompts)
        if common.sha256_text(msg) != row["prompt_sha256"]:
            raise RuntimeError(f"{row['request_id']}: prompt changed since planning (data files differ)")
        rf = (json_schema_format(common.field_of(full, self.prompts), common.schema_of(full, self.prompts))
              if row["enforce_schema"] else None)
        b = build_body(self.mcfg, self.req_defaults, msg, rf, self.logprobs,
                       seed=self.manifest.get("request_seed"))
        if row.get("followup"):
            # a second turn (harness/retry_arm.py): the model's own first reply, then the correction message
            b["messages"] += [{"role": "assistant", "content": row["followup"]["assistant"]},
                              {"role": "user", "content": row["followup"]["user"]}]
        return b

    def post(self, payload):
        data = json.dumps(payload).encode("utf-8")
        # Together sits behind Cloudflare, which refuses the default "Python-urllib" User-Agent (error 1010)
        headers = {"Content-Type": "application/json", "User-Agent": "pad-to-k-harness/1"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = urllib.request.Request(self.base + "/chat/completions", data=data, headers=headers, method="POST")
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8")), (time.time() - t0) * 1000, None
        except urllib.error.HTTPError as e:
            try:
                text = e.read().decode("utf-8", errors="replace")[:4000]
            except Exception:  # noqa: BLE001
                text = ""
            try:
                body = json.loads(text)
            except json.JSONDecodeError:
                body = {"error_text": text}
            return e.code, body, (time.time() - t0) * 1000, None
        except Exception as e:  # noqa: BLE001  (no usable response: a transport failure, retried and logged)
            return None, None, (time.time() - t0) * 1000, f"{type(e).__name__}: {e}"

    def one(self, row):
        if self.abort or self.budget_stop:
            return "not_sent"
        payload = self.body(row)
        if not self._admit():
            return "not_sent"
        try:
            return self._one(row, payload)
        finally:
            with self.lock:
                self.in_flight -= 1

    def _one(self, row, payload):
        attempt, status, resp, ms, err = 0, None, None, 0.0, None
        while attempt < self.max_attempts:
            attempt += 1
            status, resp, ms, err = self.post(payload)
            transport = status is None or status in RETRY_STATUS
            with self.lock:
                self.attempts.write(json.dumps({"request_id": row["request_id"], "attempt": attempt, "utc": now(),
                                                "http_status": status, "error": err, "latency_ms": round(ms),
                                                "retrying": transport and attempt < self.max_attempts}) + "\n")
                self.attempts.flush()
            if not transport or self.abort:
                break
            if attempt < self.max_attempts:
                time.sleep(min(60, 2 ** attempt))
        if status in ABORT_STATUS:
            with self.lock:
                self.abort = self.abort or f"HTTP {status} on {row['request_id']}: {json.dumps(resp)[:600]}"
            return "not_sent"
        if status is not None and status != 200 and status not in RESULT_STATUS and status not in RETRY_STATUS:
            with self.lock:
                self.abort = self.abort or f"unexpected HTTP {status}: {json.dumps(resp)[:600]}"
            return "not_sent"
        choice = (resp or {}).get("choices", [{}])[0] if isinstance(resp, dict) and resp.get("choices") else {}
        msg = choice.get("message") or {}
        rec = {k: row[k] for k in ("request_id", "also_answers", "doc_id", "set", "condition", "k", "n",
                                   "wording_id", "schema_id", "enforce_schema", "prompt_sha256")}
        rec["arm"] = row.get("arm")
        if row.get("followup"):
            rec["retry_of"] = {"request_id": row["source_request_id"], "run_id": row["followup"]["run_id"]}
        rec.update({
            "run_id": self.manifest["run_id"], "model_key": self.manifest["model_key"],
            "backend": self.mcfg.get("backend"), "api_model": payload["model"],
            "model_revision": self.mcfg.get("revision"), "utc": now(), "attempts": attempt,
            "http_status": status, "transport_error": err, "latency_ms": round(ms),
            "status": ("ok" if status == 200 and choice else
                       "transport_failed" if status is None or status in RETRY_STATUS or status == 200
                       else f"http_{status}"),
            "request_params": {k: v for k, v in payload.items() if k not in ("messages",)},
            "schema_sha256": (common.sha256_text(json.dumps(payload["response_format"], sort_keys=True))
                              if "response_format" in payload else None),
            "content": msg.get("content"),
            "reasoning_content": msg.get("reasoning_content") or msg.get("reasoning"),
            "finish_reason": choice.get("finish_reason"),
            "usage": (resp or {}).get("usage") if isinstance(resp, dict) else None,
            "service_tier": (resp or {}).get("service_tier") if isinstance(resp, dict) else None,
            "system_fingerprint": (resp or {}).get("system_fingerprint") if isinstance(resp, dict) else None,
            "response_model": (resp or {}).get("model") if isinstance(resp, dict) else None,
            "logprobs": choice.get("logprobs") if self.logprobs else None,
            "token_ids": choice.get("token_ids"),
            "prompt_token_ids_sha256": (common.sha256_text(json.dumps(resp["prompt_token_ids"]))
                                        if isinstance(resp, dict) and resp.get("prompt_token_ids") else None),
            "error_body": resp if status not in (200, None) else None,
        })
        rec["cost_usd"] = cost_usd(rec["usage"], self.price)
        with self.lock:
            if rec["cost_usd"] is not None:
                self.spent += rec["cost_usd"]
                self.n_costed += 1
            f = self.files[row["restricted"]]
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            self.written += 1
            if self.written % 200 == 0:
                os.fsync(f.fileno())
            if self.breaker and len(self.first_statuses) < 10:
                self.first_statuses.append(rec["status"])
                if len(self.first_statuses) == 10 and "ok" not in self.first_statuses:
                    self.abort = (f"circuit breaker: the first 10 results of this session are all {set(self.first_statuses)}; "
                                  "probably a request-format or server problem. Fix it and plan a new run id "
                                  "(or pass --no-circuit-breaker if this is expected).")
        return rec["status"]


def run_records(run_dir):
    recs = []
    for name in ("raw.jsonl", "raw_restricted.jsonl"):
        p = Path(run_dir) / name
        if p.exists():
            recs += common.read_jsonl(p)
    return recs


def run_cost(run_dir, price):
    """(USD spent, replies costed) over every record of a run, transport failures with a usage included."""
    costs = [cost_usd(r.get("usage"), price) for r in run_records(run_dir)]
    costs = [c for c in costs if c is not None]
    return sum(costs), len(costs)


def done_ids(run_dir):
    ids = {}
    for name in ("raw.jsonl", "raw_restricted.jsonl"):
        p = Path(run_dir) / name
        if p.exists():
            for line in open(p, encoding="utf-8"):
                if line.strip():
                    r = json.loads(line)
                    ids[r["request_id"]] = r["status"]
    return ids


def server_snapshot(base, api_key):
    info = {}
    for path in ("/models",):
        try:
            req = urllib.request.Request(base.rstrip("/") + path,
                                         headers={"Authorization": f"Bearer {api_key}"} if api_key else {})
            with urllib.request.urlopen(req, timeout=20) as r:
                info[path] = json.loads(r.read().decode("utf-8"))
        except Exception as e:  # noqa: BLE001  (a missing endpoint is information, not a failure)
            info[path] = f"unavailable: {type(e).__name__}"
    root = base.rstrip("/").rsplit("/v1", 1)[0]
    try:
        with urllib.request.urlopen(root + "/version", timeout=10) as r:
            info["/version"] = json.loads(r.read().decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        info["/version"] = f"unavailable: {type(e).__name__}"
    return info


def go(args):
    run_dir = Path(args.run_dir)
    planned = common.read_jsonl(run_dir / "planned.jsonl")
    lock = open(run_dir / ".lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit(f"another `go` is already running on {run_dir}")
    man = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    pinned = man["model"].get("base_url")
    if pinned and args.base_url and args.base_url.rstrip("/") != pinned.rstrip("/"):
        raise SystemExit(f"{man['model_key']} is served at {pinned} (base_url in configs/models.yaml); "
                         "leave out --base-url for it")
    args.base_url = args.base_url or pinned
    if not args.base_url:
        raise SystemExit("give --base-url (this model has no base_url in configs/models.yaml)")
    if man["model"].get("backend") == "vllm" and not args.server_info and not args.no_server_info:
        raise SystemExit("a local run needs --server-info runs/servers/<file>.json (written by serve.py up), "
                         "so every output can be traced to the exact server; --no-server-info only for tests")
    have = done_ids(run_dir)
    todo = [r for r in planned if not FINAL(have.get(r["request_id"]))]
    retry_failed = [r for r in todo if r["request_id"] in have]
    if retry_failed and not args.resend_transport_failures:
        print(f"{len(retry_failed)} requests ended in transport failure earlier; pass "
              f"--resend-transport-failures to send them again (the earlier record stays in raw.jsonl)")
        todo = [r for r in todo if r["request_id"] not in have]
    if args.limit:
        todo = todo[: args.limit]
    api_key = os.environ.get(args.api_key_env) if args.api_key_env else None
    sender = Sender(run_dir, args.base_url, api_key, args.timeout, args.max_attempts)
    sender.logprobs = args.logprobs
    sender.breaker = not args.no_circuit_breaker
    if args.max_usd is not None:
        if not sender.price:
            raise SystemExit(f"--max-usd needs a price for {man['model_key']} in configs/models.yaml")
        sender.max_usd = args.max_usd
        if sender.spent >= args.max_usd:
            raise SystemExit(f"this run has already cost {sender.spent:.4f} USD, at or above --max-usd {args.max_usd}")
    session = {"utc_start": now(), "base_url_host": args.base_url.split("/")[2], "workers": args.workers,
               "to_send": len(todo), "already_done": len(have), "host": platform.node(),
               "server": server_snapshot(args.base_url, api_key),
               "server_info_file": json.loads(Path(args.server_info).read_text()) if args.server_info else None,
               "git": git_state(), "data_sha256": common.data_hashes(),
               "max_usd": args.max_usd, "spent_usd_before": round(sender.spent, 6)}
    # compared on the files the run was planned with (a data file added later does not change its prompts)
    planned_hashes = sender.manifest["data_sha256"]
    if {k: session["data_sha256"].get(k) for k in planned_hashes} != planned_hashes:
        raise SystemExit("data files changed since this run was planned; plan a new run")
    with open(run_dir / "sessions.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(session) + "\n")
    print(f"sending {len(todo)} requests with {args.workers} workers ({len(have)} already have a result)"
          + (f"; spent so far {sender.spent:.4f} USD, cap {args.max_usd} USD" if args.max_usd is not None else ""))
    counts, t0 = Counter(), time.time()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for i, status in enumerate(pool.map(sender.one, todo), 1):
            counts[status] += 1
            if i % max(1, len(todo) // 20) == 0 or i == len(todo):
                rate = i / max(1e-9, time.time() - t0)
                cost = f"  {sender.spent:.4f} USD" if sender.price else ""
                print(f"  {i}/{len(todo)}  {dict(counts)}  {rate:.1f} req/s{cost}", flush=True)
    for f in sender.files.values():
        f.close()
    sender.attempts.close()
    write_summary(run_dir)
    if sender.abort:
        print(f"\nRUN STOPPED: {sender.abort}")
        sys.exit(2)
    if sender.budget_stop:
        print(f"\nSENDING STOPPED: {sender.budget_stop}. {counts['not_sent']} requests not sent; "
              "they stay planned (go again with a higher --max-usd to carry on)")
        sys.exit(3)


def write_summary(run_dir):
    run_dir = Path(run_dir)
    man = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    planned_ids = {r["request_id"] for r in common.read_jsonl(run_dir / "planned.jsonl")}
    recs = []
    for name in ("raw.jsonl", "raw_restricted.jsonl"):
        p = run_dir / name
        if p.exists():
            recs += common.read_jsonl(p)
    latest = {}
    for r in recs:
        latest[r["request_id"]] = r
    stray = set(latest) - planned_ids
    prompts = common.load_prompts()
    st, fin, rung, cond_ok, errs = Counter(), Counter(), Counter(), Counter(), Counter()
    tok_in = tok_out = 0
    for r in latest.values():
        st[r["status"]] += 1
        fin[r.get("finish_reason")] += 1
        if r["status"] == "ok":
            field = prompts["lists"][r["schema_id"].split("|")[0]]["field"]
            rung[common.parse_output(r.get("content"), field)["parse_rung"]] += 1
            cond_ok[r["condition"]] += 1
            u = r.get("usage") or {}
            tok_in += u.get("prompt_tokens") or 0
            tok_out += u.get("completion_tokens") or 0
        elif r.get("error_body") or r.get("transport_error"):
            errs[(r["status"], json.dumps(r.get("error_body") or r.get("transport_error"))[:160])] += 1
    exp = man["expected_outputs"]
    results = sum(1 for r in latest.values() if FINAL(r["status"]))
    lines = [f"# Run {man['run_id']}", "",
             f"- model: {man['model_key']} ({man['model'].get('hf_repo') or man['model'].get('api_model')}, "
             f"revision {man['model'].get('revision')})",
             f"- planned: {man['created_utc']}, git {man['git']['commit'][:12]}",
             f"- EXPECTED outputs: {exp}; results: {results} (ok {st['ok']}); "
             f"transport failures: {st['transport_failed']}; never sent: {len(planned_ids - set(latest))}; "
             f"MISSING: {exp - results}",
             f"- status: {dict(st)}", f"- finish_reason: {dict(fin)}",
             f"- parse rung (ok outputs): {dict(rung)}", f"- ok by condition: {dict(cond_ok)}",
             f"- tokens: {tok_in} in, {tok_out} out"]
    price = price_of(man)
    if price:
        lines.append(f"- cost: {run_cost(run_dir, price)[0]:.4f} USD at {price['in']} / {price['out']} USD "
                     f"per million tokens in / out ({price.get('tier', 'standard')} tier)")
    if stray:
        lines.append(f"- WARNING: {len(stray)} records are not in planned.jsonl")
    if errs:
        lines += ["- distinct errors (status, message, count):"]
        lines += [f"  - {k[0]} x{v}: {k[1]}" for k, v in errs.most_common(8)]
    lines += ["", "The counts match only if MISSING is 0. An http_400 or http_422 is a result (the server",
              "refused that request); if every request has one, the request format is wrong: plan a new run."]
    (run_dir / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


def status(args):
    write_summary(args.run_dir)


def spend(args):
    total = 0.0
    for d in args.run_dirs:
        man = json.loads((Path(d) / "manifest.json").read_text(encoding="utf-8"))
        price = price_of(man)
        usd, n = run_cost(d, price)
        total += usd
        print(f"{d}: {usd:.4f} USD over {n} replies" + ("" if price else " (no price in configs/models.yaml)"))
    print(f"total: {total:.4f} USD")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--model", required=True)
    p.add_argument("--scope", choices=["pilot", "full", "robustness", "dev", "custom"], default="pilot")
    p.add_argument("--run-id")
    p.add_argument("--splits", nargs="*")
    p.add_argument("--conditions", nargs="*")
    p.add_argument("--k", nargs="*", type=int)
    p.add_argument("--wordings", nargs="*")
    p.add_argument("--sets", nargs="*")
    p.add_argument("--docs", nargs="*")
    p.add_argument("--docs-file", help="text file with one doc_id per line")
    p.add_argument("--seed", type=int, help="shuffle seed (default 20261014)")
    p.add_argument("--request-seed", type=int, help="seed sent with every request (sampled-decoding check)")
    p.add_argument("--repeat-of", type=Path, help="repeat check: re-plan a seeded sample of this run's requests")
    p.add_argument("--repeat-n", type=int, default=300)
    g = sub.add_parser("go")
    g.add_argument("run_dir")
    g.add_argument("--base-url", help="OpenAI-compatible base, e.g. http://127.0.0.1:8000/v1 (default: the "
                                       "model's base_url in configs/models.yaml)")
    g.add_argument("--api-key-env", help="name of the env var holding the key (Bedrock: AWS_BEARER_TOKEN_BEDROCK)")
    g.add_argument("--workers", type=int, default=32)
    g.add_argument("--timeout", type=float, default=600)
    g.add_argument("--max-attempts", type=int, default=5)
    g.add_argument("--limit", type=int)
    g.add_argument("--logprobs", type=int, default=0, help="top_logprobs to request (0 = none)")
    g.add_argument("--server-info", help="server_info.json written by harness/serve.py")
    g.add_argument("--resend-transport-failures", action="store_true")
    g.add_argument("--no-server-info", action="store_true", help="allow a local run without --server-info (tests only)")
    g.add_argument("--no-circuit-breaker", action="store_true")
    g.add_argument("--max-usd", type=float, help="stop sending once this run has cost this many USD (needs `price`)")
    s = sub.add_parser("status")
    s.add_argument("run_dir")
    c = sub.add_parser("spend")
    c.add_argument("run_dirs", nargs="+")
    args = ap.parse_args()
    if args.cmd == "plan":
        args.docs = set(args.docs) if args.docs else None
        plan(args)
    elif args.cmd == "go":
        go(args)
    elif args.cmd == "spend":
        spend(args)
    else:
        status(args)


if __name__ == "__main__":
    main()
