#!/usr/bin/env python3
"""enforce_test.py: prove the count rule reaches the model, on this engine, before any counted run.

    python harness/enforce_test.py --model qwen3.5-9b --base-url http://127.0.0.1:8000/v1
    python harness/enforce_test.py --model bedrock-qwen3-235b \
        --base-url https://bedrock-runtime.us-east-1.amazonaws.com/openai/v1 --api-key-env AWS_BEARER_TOKEN_BEDROCK

Run it on every model x engine version x flag set, and again after any upgrade. It sends about 20
requests (greedy) and writes runs/enforce/<model>-<utc>/report.md and raw.jsonl. Read every raw
output yourself before you trust the verdicts.

Verdict rules (from the plan):
  - E02-E06 fail  -> this engine does not enforce minItems/maxItems: no enforced cells on it.
  - E07 accepted  -> the engine does not check impossible bounds (note it; never send min > max).
  - E08 a closed short list -> the padding cell cannot be scored on this engine.
  - E10/E11 fail  -> the study's own enforced schemas do not work here.
  - E16 differs   -> the server adds the schema to the prompt by itself: report that engine apart.
  - E14 differs   -> repeated identical requests disagree: measure and report the flip rate.
Bedrock serverless documents minItems as "only values 0 and 1", so E02, E03, E07, E08, E10, E11 are
expected to come back as HTTP 400 there; that is the documented limit, not a bug in this script.
"""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
import run as runner  # noqa: E402

DOC = ("Meeting notes, 12 March.\nPriya will send the revised budget to finance by Friday.\n"
       "The team talked about moving the offsite to March, but nothing was decided.")
ASK = "List the action items in this document.\n\nDocument:\n\"\"\"\n" + DOC + "\n\"\"\""


def schema(min_items=None, max_items=None):
    arr = {"type": "array", "items": {"type": "string"}}
    if min_items is not None:
        arr["minItems"] = min_items
    if max_items is not None:
        arr["maxItems"] = max_items
    return {"type": "object", "properties": {"action_items": arr}, "required": ["action_items"],
            "additionalProperties": False}


def rf(s):
    return {"type": "json_schema", "json_schema": {"name": "action_items", "schema": s, "strict": True}}


def study_requests(n_max=1):
    """Two real reserve documents (never used in the study) with n <= n_max, in the study's own format."""
    docs = common.load_documents()
    prompts = common.load_prompts()
    reqs = [r for r in common.load_requests() if r["condition"] in ("min_k_enforced", "min_k_escape", "min_k_shown")
            and r["k"] == 5]
    by_doc = {}
    for r in reqs:
        by_doc.setdefault(r["doc_id"], {})[r["condition"]] = r
    # reserve documents have no requests; borrow the request shape from a study document of the same set
    chosen = []
    for d in sorted(docs.values(), key=lambda d: d["doc_id"]):
        if d["split"] == "reserve" and d["n"] <= n_max and d.get("redistributable", True) and d["set"] in ("emails", "clinical"):
            tmpl = next((v for v in by_doc.values() if next(iter(v.values()))["set"] == d["set"]), None)
            if tmpl:
                chosen.append((d, tmpl))
        if len(chosen) == 2:
            break
    out = []
    for d, tmpl in chosen:
        for cond, r in tmpl.items():
            field = common.field_of(r, prompts)
            out.append({"doc": d, "req": r, "cond": cond, "field": field,
                        "msg": common.user_message(r, d, prompts), "schema": common.schema_of(r, prompts)})
    return out


def rendered_prompt(snd, body, out_dir):
    """Local vLLM only: the exact text the chat template feeds the model around one user message, written to
    rendered_prompt.txt, so a default system prompt or a date line added by the template is visible. Compares
    the token count of the rendered chat with that of the bare user message."""
    root = snd.base[:-3] if snd.base.endswith("/v1") else snd.base

    def call(path, payload):
        req = urllib.request.Request(root + path, data=json.dumps(payload).encode("utf-8"),
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    try:
        chat = {"model": body["model"], "messages": body["messages"], "add_generation_prompt": True}
        if body.get("chat_template_kwargs"):
            chat["chat_template_kwargs"] = body["chat_template_kwargs"]
        toks = call("/tokenize", chat)["tokens"]
        bare = call("/tokenize", {"model": body["model"], "prompt": body["messages"][0]["content"],
                                  "add_special_tokens": False})["count"]
        text = call("/detokenize", {"model": body["model"], "tokens": toks})["prompt"]
    except Exception as e:  # noqa: BLE001
        return f"Rendered prompt: unavailable ({e})."
    (out_dir / "rendered_prompt.txt").write_text(text, encoding="utf-8")
    extra = len(toks) - bare
    return (f"Rendered prompt (rendered_prompt.txt): the chat template adds {extra} tokens around the user message "
            f"({'look for a default system prompt or a date line' if extra > 40 else 'template markers only'}).")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True)
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--api-key-env")
    ap.add_argument("--skip-unsatisfiable", action="store_true",
                    help="skip E07 (min > max); REQUIRED on llama.cpp, which can crash on it (issue #29462)")
    ap.add_argument("--repeats", type=int, default=5)
    args = ap.parse_args()
    defaults, models = runner.load_models()
    m = models[args.model]
    xb = m.get("extra_body") or {}
    # thinking is on through reasoning_effort, the chat template, or (Together) extra_body
    reasons = bool(m.get("reasoning_effort") or (m.get("chat_template_kwargs") or {}).get("enable_thinking")
                   or (xb.get("reasoning") or {}).get("enabled")
                   or (xb.get("chat_template_kwargs") or {}).get("enable_thinking"))
    api_key = os.environ.get(args.api_key_env) if args.api_key_env else None
    utc = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = common.ROOT / "runs" / "enforce" / f"{args.model}-{utc}"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "manifest.json").write_text(json.dumps({"model_key": args.model, "model": m, "utc": utc}, indent=1))
    snd = runner.Sender.__new__(runner.Sender)          # reuse the HTTP code only
    snd.base, snd.api_key, snd.timeout = args.base_url.rstrip("/"), api_key, 600

    def payload(msg, response_format=None, max_tokens=256, logprobs=0):
        # the same builder the runs use (run.build_body), so the test sends what the runs send
        mt = max(max_tokens, m.get("max_tokens", 0)) if reasons else max_tokens
        return runner.build_body(m, defaults["request"], msg, response_format, logprobs, max_tokens=mt)

    tests = [
        ("E01", "no bounds", payload(ASK, rf(schema())), lambda n, st, fin: n is not None),
        ("E02", "minItems 3", payload(ASK, rf(schema(3))), lambda n, st, fin: n is not None and n >= 3),
        ("E03", "minItems 5", payload(ASK, rf(schema(5))), lambda n, st, fin: n is not None and n >= 5),
        ("E04", "maxItems 2", payload(ASK, rf(schema(None, 2))), lambda n, st, fin: n is not None and n <= 2 and fin == "stop"),
        ("E05", "minItems = maxItems = 2", payload(ASK, rf(schema(2, 2))), lambda n, st, fin: n == 2 and fin == "stop"),
        ("E06", "minItems = maxItems = 0", payload(ASK, rf(schema(0, 0))), lambda n, st, fin: n == 0 and fin == "stop"),
        ("E08", "minItems 40 with a small token budget", payload(ASK, rf(schema(40)), 256),
         # the cap cuts the list off (finish "length", salvaged or not): fine; a list CLOSED short of 40 fails
         lambda n, st, fin: (n is not None and n >= 40) or fin == "length"),
        ("E09", "no maxItems, ask for every risk (runaway check, informational)",
         payload("List every risk you can think of for the plan in this document.\n\nDocument:\n\"\"\"\n" + DOC + "\n\"\"\"",
                 rf(schema()), 512), lambda n, st, fin: True),
        ("E13", "logprobs on minItems 3 (is ']' ever offered before item 3?)",
         payload(ASK, rf(schema(3)), 256, 20), lambda n, st, fin: True),
        ("E16a", "same prompt WITHOUT response_format (prompt token count)", payload(ASK), lambda n, st, fin: True),
        ("E16b", "same prompt WITH response_format, no count (prompt token count)", payload(ASK, rf(schema())),
         lambda n, st, fin: True),
    ]
    if not args.skip_unsatisfiable:
        tests.append(("E07", "minItems 3 > maxItems 2 (should be rejected)", payload(ASK, rf(schema(3, 2))),
                      lambda n, st, fin: st is not None and 400 <= st < 500))
    study = study_requests()
    field_by_msg = {s["msg"]: s["field"] for s in study}
    for i, s in enumerate(study):
        k = s["req"]["k"]
        enforced = s["cond"] != "min_k_shown"
        code = {"min_k_enforced": "E10", "min_k_escape": "E11", "min_k_shown": "E12"}[s["cond"]] + "abcdefgh"[i // 3]
        p = payload(s["msg"], rf(s["schema"]) if enforced else None, 512)
        check = (lambda n, st, fin, k=k: n is not None and n >= k) if enforced else (lambda n, st, fin: True)
        tests.append((code, f"study schema {s['cond']} k={k} on reserve doc {s['doc']['doc_id']} (n={s['doc']['n']})", p, check))
        if s["cond"] == "min_k_enforced" and i < 3:
            for rep in range(args.repeats):
                tests.append((f"E14-{rep}", f"repeat of {code} (determinism)", p, lambda n, st, fin: True))

    def send(t):
        code, desc, p, check = t
        st, resp, ms, err = snd.post(p)
        choice = (resp or {}).get("choices", [{}])[0] if isinstance(resp, dict) and resp.get("choices") else {}
        msg = choice.get("message") or {}
        field = p.get("response_format", {}).get("json_schema", {}).get("name") or "action_items"
        field = field_by_msg.get(p["messages"][0]["content"], field)
        parsed = common.parse_output(msg.get("content"), field)
        n = len(parsed["items"]) if parsed["items"] is not None else None
        fin = choice.get("finish_reason")
        verdict = "PASS" if check(n, st, fin) else "FAIL"
        if code == "E08" and n is not None and n < 40 and parsed["parse_rung"] != "truncated_salvage":
            verdict = "FAIL"      # a list CLOSED short of 40, even if white space then ran on to the cap
        if st and st >= 400 and code not in ("E07",):
            verdict = f"HTTP {st}"
        return {"test": code, "what": desc, "verdict": verdict, "http_status": st, "transport_error": err,
                "n_items": n, "finish_reason": fin, "parse_rung": parsed["parse_rung"],
                "usage": (resp or {}).get("usage") if isinstance(resp, dict) else None, "latency_ms": round(ms),
                "content": msg.get("content"), "reasoning_content": msg.get("reasoning_content") or msg.get("reasoning"),
                "logprobs": choice.get("logprobs") if code == "E13" else None,
                "error_body": resp if st not in (200, None) else None, "request": p}

    # concurrent, so the repeats share batches with other requests (a fair determinism test)
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(send, tests))
    with open(out_dir / "raw.jsonl", "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    by = {r["test"]: r for r in results}
    lines = [f"# Enforcement test: {args.model} at {utc}", "", f"Endpoint host: {args.base_url.split('/')[2]}", "",
             "| test | what | verdict | items | finish | parse | prompt tokens |", "|---|---|---|---|---|---|---|"]
    for r in results:
        pt = (r["usage"] or {}).get("prompt_tokens")
        lines.append(f"| {r['test']} | {r['what']} | {r['verdict']} | {r['n_items']} | {r['finish_reason']} | "
                     f"{r['parse_rung']} | {pt} |")
    reps = [by[t]["content"] for t in by if t.startswith("E14")]
    base10 = next((by[t]["content"] for t in by if t.startswith("E10")), None)
    if reps:
        same = sum(c == base10 for c in reps)
        lines += ["", f"Determinism: {same} of {len(reps)} repeats identical to the first E10 output."]
    a, b = by.get("E16a"), by.get("E16b")
    if a and b and a["usage"] and b["usage"]:
        d = (b["usage"].get("prompt_tokens") or 0) - (a["usage"].get("prompt_tokens") or 0)
        lines += [f"Schema-in-prompt check: prompt tokens with response_format minus without = {d} "
                  f"({'the server adds text to the prompt' if d else 'nothing added'})."]
    lp = by.get("E13", {}).get("logprobs")
    if lp and lp.get("content"):
        # look only where the model wrote an item separator after item 1 and item 2: under minItems 3,
        # closing the list there is forbidden, so ']' can only be offered if logprobs are pre-mask
        seps, in_str, esc = [], False, False
        for tok in lp["content"]:                   # a token holding a "," outside any JSON string
            has_sep = False
            for ch in tok.get("token") or "":
                if esc:
                    esc = False
                elif in_str and ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = not in_str
                elif ch == "," and not in_str:
                    has_sep = True
            if has_sep:
                seps.append(tok)
        seps = seps[:2]
        offered = any(any("]" in (alt.get("token") or "") and (alt.get("logprob") or -1e9) > -1000
                          for alt in (tok.get("top_logprobs") or [])) for tok in seps)   # masked = -9999 floor
        lines += [f"Logprobs at the first {len(seps)} item separators: ']' {'IS' if offered else 'is NOT'} offered "
                  f"({'probabilities look pre-mask' if offered else 'probabilities look post-mask'}; check raw.jsonl E13 by hand)."]
    if m.get("backend") == "vllm":
        lines += ["", rendered_prompt(snd, payload(ASK), out_dir)]
    fails = [r["test"] for r in results if r["verdict"] not in ("PASS",)]
    lines += ["", f"Not PASS: {', '.join(fails) or 'none'}. Read raw.jsonl before deciding anything."]
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwrote {out_dir}")


if __name__ == "__main__":
    main()
