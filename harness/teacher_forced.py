#!/usr/bin/env python3
"""teacher_forced.py: read a finished run's outputs back through the model, without the grammar.

    python harness/teacher_forced.py score    --source runs/<run_id> --server-info runs/servers/<file>.json
    python harness/teacher_forced.py hf-check --scores runs/<tf_run_id> [--n 200]

`score` feeds each output of a local vLLM run back to the same model in one pass: the prompt the model
saw, then the tokens of what it wrote. No grammar, no sampling. It reads two things:

  * at each list boundary (just after "[" and after each complete entry): how likely the model was to
    close the list there rather than go on (the mechanism figure, RUN-PLAN 5.7, RQ5);
  * for each entry: the log probability of its own tokens (RQ7: are extra entries written with lower
    confidence than real ones?).

It writes a new run folder, runs/tf_<source run id>_<utc>/ (manifest.json, scores.jsonl, summary.json),
with numbers and character/token offsets only, never output or document text, so review-set outputs are
scored too. The source run folder is only read. A resumed pass appends; read the last line per request
id. `hf-check` recomputes a sample of the same numbers in HF Transformers (RUN-PLAN 5.7: about 200 cases)
and writes runs/<tf_run_id>_hfcheck/.

Both run inside the pinned vLLM image, which has the tokenizer and model libraries. The server needs the
token-scoring route and room for the candidate ids:

    python harness/serve.py up qwen3.5-9b --hf-home /home/ubuntu/hf --extra=--enable-scale-out --extra=--max-logprobs=1024
    docker run --rm --network host --user "$(id -u):$(id -g)" -v "$PWD":/repo -w /repo -v /home/ubuntu/hf:/hf \\
        -e HF_HOME=/hf -e HF_HUB_OFFLINE=1 -e HOME=/tmp --entrypoint python3 <image digest> \\
        harness/teacher_forced.py score --source runs/<run_id> --server-info runs/servers/<file>.json
    python harness/serve.py down qwen3.5-9b

hf-check needs the GPU to itself (stop the server first) and the same docker command with --gpus all.

Reading a boundary. The anchor is the "[" of the list or an entry's closing quote; the first character
after it that is not white space decides: "]" closes the list, "," goes on (after "[", '"' starts an
entry). The first reading is at the token that holds the character right after the anchor. With R, the
part of that token up to the anchor (empty when the token starts after it; '."' when the tokenizer joined
the end of an entry to its quote), every vocabulary token that starts with R is sorted by what follows R:
close (white space, then "]"), go on ("," or '"'), open (only white space, so the choice comes later).
The rest (other text, or another split of the same text) is p_other. When white space came first, as in
pretty-printed JSON, a reading is also taken at every later token up to the one that holds the deciding
character (read on the whole token, since the white space is optional), and they combine from the last
one back: p_close = p_close(this) + p_open(this) x p_close(next), and the same for p_cont. The
ids go to vLLM as prompt_logprob_token_ids (v0.31.0, model runner V2), so every probability is exact,
not cut off at a top-k list. When the go-on set is too large to send (a '"' that starts an entry can
begin thousands of tokens), p_cont and p_other are left empty; p_close stays exact.

Which tokens are read back. run.py asks vLLM for the generated token ids (return_token_ids) and keeps them
in each record; those exact ids are scored (token_source "generated"). Runs made before that (the 14 Oct
dev sets) kept only the text, which is tokenized again (token_source "retokenized"); token_count_match says
whether that gives as many tokens as the model generated (usage.completion_tokens, less the end token when
it stopped by itself). Under the grammar it often does not: the model writes "{" and '"' as two tokens
where the tokenizer joins them. prompt_tokens_match (and prompt_ids_match, when the run kept a hash of the
prompt ids) checks the prompt the same way.
"""
import argparse
import base64
import bisect
import datetime as dt
import hashlib
import io
import json
import math
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

TF_VERSION = "0.1.0"
WS = " \t\n\r"
AFTER = {  # what may follow R, by boundary kind and class
    "start": {"close": re.compile(r"\s*\]"), "cont": re.compile(r'\s*"')},
    "entry": {"close": re.compile(r"\s*\]"), "cont": re.compile(r"\s*,")},
}
OPEN = re.compile(r"\s*\Z")
CLASSES = ("close", "cont", "open")
MAX_CONT_IDS = 256        # a larger go-on set is not sent (see the docstring); close and open always are
ALIGN_TOL = 1e-3          # nats: one token's log probability, read through both vLLM outputs, must agree


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="milliseconds")


# ---------------------------------------------------------------------------------------------------------
# Where the list and its entries sit in the model's own text

def _string_end(s, i):
    """Index of the quote that closes the JSON string opened at s[i], or None if the text ends first."""
    j, n = i + 1, len(s)
    while j < n:
        c = s[j]
        if c == "\\":
            j += 2
            continue
        if c == '"':
            return j
        j += 1
    return None


def list_layout(content, field):
    """Character layout of the asked-for list as the model wrote it.

    entries: (open quote, close quote) of each complete string entry, in order.
    boundaries: (after, anchor, d, decision): after is -1 for the boundary just after "[", else the entry
    index; anchor is the "[" or the entry's closing quote; d is the deciding character; decision is
    "close" or "cont". stop: closed | cut_off | no_list | non_string_entry | trailing_comma | malformed.
    An entry the text ends in, or ends right after, is not complete; the parse ladder does not count it
    either.
    """
    out = {"open": None, "entries": [], "boundaries": [], "stop": "no_list"}
    m = re.search(r'"' + re.escape(field) + r'"\s*:\s*\[', content or "")
    if not m:
        return out
    n = len(content)

    def skip(j):
        while j < n and content[j] in WS:
            j += 1
        return j

    out["open"] = m.end() - 1
    i = skip(m.end())
    if i >= n:
        out["stop"] = "cut_off"
        return out
    if content[i] == "]":
        out["boundaries"].append((-1, out["open"], i, "close"))
        out["stop"] = "closed"
        return out
    if content[i] != '"':
        out["stop"] = "non_string_entry"
        return out
    out["boundaries"].append((-1, out["open"], i, "cont"))
    while True:
        j = _string_end(content, i)
        d = skip(j + 1) if j is not None else n
        if d >= n:
            out["stop"] = "cut_off"
            return out
        if content[d] not in ",]":
            out["stop"] = "malformed"
            return out
        k = len(out["entries"])
        out["entries"].append((i, j))
        if content[d] == "]":
            out["boundaries"].append((k, j, d, "close"))
            out["stop"] = "closed"
            return out
        out["boundaries"].append((k, j, d, "cont"))
        i = skip(d + 1)
        if i >= n:
            out["stop"] = "cut_off"
            return out
        if content[i] != '"':
            out["stop"] = "trailing_comma" if content[i] == "]" else "non_string_entry"
            return out


def entry_texts(content, layout):
    """The entries' decoded text, or None when one does not decode (it then cannot match the parse)."""
    try:
        return [json.loads(content[a:b + 1]) for a, b in layout["entries"]]
    except (json.JSONDecodeError, ValueError):
        return None


def token_at(starts, ends, d):
    """Index of the token whose character span holds position d, or None."""
    t = bisect.bisect_right(starts, d) - 1
    for _ in range(4):                     # zero-width or overlapping spans (multi-byte characters)
        if t < 0 or starts[t] > d:
            return None
        if d < ends[t]:
            return t
        t -= 1
    return None


# ---------------------------------------------------------------------------------------------------------
# The vocabulary, read as text

def decode_pieces(tok):
    """Each vocabulary token's text as it reads after other text, so a SentencePiece word-start mark stays
    a space. Special tokens keep their names, so they never look like white space."""
    probe = tok.encode("a", add_special_tokens=False)
    kw = {"skip_special_tokens": False, "clean_up_tokenization_spaces": False}
    size = len(tok)
    if len(probe) != 1:
        return tok.batch_decode([[v] for v in range(size)], **kw)
    base = tok.decode(probe, **kw)
    joined = tok.batch_decode([probe + [v] for v in range(size)], **kw)
    alone, pieces = None, []
    for v, s in enumerate(joined):
        if s.startswith(base):
            pieces.append(s[len(base):])
        else:
            alone = alone or tok.batch_decode([[x] for x in range(size)], **kw)
            pieces.append(alone[v])
    return pieces


def piece_offsets(ids, pieces, content):
    """Character spans from the decoded pieces, when they spell the content exactly; else None."""
    spans, s = [], 0
    for v in ids:
        p = pieces[v]
        if content[s:s + len(p)] != p:
            return None
        spans.append((s, s + len(p)))
        s += len(p)
    return spans if s == len(content) else None


def offsets_by_decoding(tok, ids, content):
    """Character spans by decoding growing prefixes: tokens that share one character (a multi-byte
    character split into bytes) share its span. None unless the ids decode to the content."""
    kw = {"skip_special_tokens": False, "clean_up_tokenization_spaces": False}
    spans, prev, pending, text = [], 0, [], ""
    for i in range(len(ids)):
        text = tok.decode(ids[:i + 1], **kw)
        if text.endswith("\ufffd"):
            pending.append(i)
            continue
        spans.extend((prev, len(text)) for _ in pending + [i])
        pending, prev = [], len(text)
    return spans if not pending and text == content else None


def exact_ids(gen, content, tok, pieces):
    """The run's generated ids that spell the content (the end token dropped), with character spans."""
    for ids in (gen, gen[:-1]):
        spans = piece_offsets(ids, pieces, content)
        if spans is not None:
            return list(ids), spans, "generated"
    for ids in (gen, gen[:-1]):
        spans = offsets_by_decoding(tok, ids, content)
        if spans is not None:
            return list(ids), spans, "generated_decoded"
    return None


class Vocab:
    """The boundary candidates (close / cont / open token ids) for a residual R, cached."""

    def __init__(self, pieces):
        self.pieces = pieces
        self.by_first = {}
        for v, s in enumerate(pieces):
            if s:
                self.by_first.setdefault(s[0], []).append(v)
        self._cache = {}

    def candidates(self, residual, kind):
        key = (residual, kind)
        if key not in self._cache:
            pool = self.by_first.get(residual[0], []) if residual else range(len(self.pieces))
            classes = {c: [] for c in CLASSES}
            for v in pool:
                s = self.pieces[v]
                if not s.startswith(residual):
                    continue
                rest = s[len(residual):]
                if AFTER[kind]["close"].match(rest):
                    classes["close"].append(v)
                elif AFTER[kind]["cont"].match(rest):
                    classes["cont"].append(v)
                elif OPEN.match(rest) and (residual or rest):
                    classes["open"].append(v)
            self._cache[key] = classes
        return self._cache[key]


# ---------------------------------------------------------------------------------------------------------
# One output: what to ask for, and what the answer means

def prepare(content, layout, prompt_ids, encode, vocab, max_ids=None):
    """Token ids to feed, the content tokens' character spans, and each boundary's reading rows.

    encode(text) -> (ids, [(start, end), ...], method). Row i of the scores predicts content token i.
    """
    ids, offsets, method = encode(content)
    starts, ends = [o[0] for o in offsets], [o[1] for o in offsets]
    bounds, want = [], set()
    for after, anchor, d, decision in layout["boundaries"]:
        kind = "start" if after == -1 else "entry"
        b = {"after": after, "anchor": anchor, "d": d, "decision": decision, "readings": []}
        r1, rd = token_at(starts, ends, anchor + 1), token_at(starts, ends, d)
        if r1 is not None and rd is not None:
            rows = [(r1, content[starts[r1]:anchor + 1] if starts[r1] <= anchor else "")]
            # every later row up to the deciding token: they hold only white space before d, which is optional,
            # so the classes are read on the whole token (a "]" with less white space closes the list too)
            rows += [(r, "") for r in range(r1 + 1, rd + 1)]
            for row, residual in rows:
                classes = dict(vocab.candidates(residual, kind))
                if len(classes["cont"]) > MAX_CONT_IDS:
                    classes["cont"] = None
                b["readings"].append({"row": row, "residual_len": len(residual), "classes": classes,
                                      "actual": ids[row]})
                want.add(ids[row])                 # the alignment check needs the token the model wrote
                for cls in CLASSES:
                    want.update(classes[cls] or [])
        bounds.append(b)
    if max_ids is not None and len(want) > max_ids:
        # Drop the go-on sets first, then give up: p_close must stay exact or not be reported at all.
        want = set()
        for b in bounds:
            for rd_ in b["readings"]:
                rd_["classes"]["cont"] = None
                want.update(rd_["classes"]["close"] + rd_["classes"]["open"] + [rd_["actual"]])
        if len(want) > max_ids:
            raise ValueError(f"{len(want)} candidate ids, the server allows {max_ids}")
    return {"P": len(prompt_ids), "C": len(ids), "full_ids": list(prompt_ids) + list(ids), "starts": starts,
            "ends": ends, "offsets": method, "layout": layout, "bounds": bounds, "ids": sorted(want)}


def _r(x, nd=6):
    return None if x is None else round(float(x), nd)


def finish(prep, actual, class_lp):
    """Entry and boundary numbers from one pass.

    actual[i] = (log probability, rank) of content token i as written; class_lp(row, ids) -> log
    probabilities of those ids at that row.
    """
    starts, ends, C = prep["starts"], prep["ends"], prep["C"]
    entries = []
    for i, (a, b) in enumerate(prep["layout"]["entries"]):
        toks = [t for t in range(C) if starts[t] < b and ends[t] > a + 1]     # the text inside the quotes
        lps = [actual[t][0] for t in toks]
        entries.append({
            "i": i, "chars": [a, b], "toks": [toks[0], toks[-1]] if toks else None, "n_tokens": len(toks),
            "sum_lp": _r(sum(lps)) if lps else None, "mean_lp": _r(sum(lps) / len(lps)) if lps else None,
            "min_lp": _r(min(lps)) if lps else None, "first_lp": _r(lps[0]) if lps else None,
            "first_rank": actual[toks[0]][1] if toks else None,
            "rank1_share": _r(sum(actual[t][1] == 1 for t in toks) / len(toks), 4) if toks else None,
            "lps": [round(x, 3) for x in lps]})
    bounds, aligns = [], []
    for b in prep["bounds"]:
        out = {"after": b["after"], "decision": b["decision"], "anchor": b["anchor"], "char": b["d"]}
        if not b["readings"]:
            out["status"] = "unmapped"
            bounds.append(out)
            continue
        readings = []
        for rd in b["readings"]:
            row, classes = rd["row"], rd["classes"]
            p = {c: (None if classes[c] is None else
                     float(np.exp(np.asarray(class_lp(row, classes[c]), dtype=np.float64)).sum())
                     if classes[c] else 0.0) for c in CLASSES}
            act_lp, act_rank = actual[row]
            aligns.append(abs(float(np.asarray(class_lp(row, [rd["actual"]]))[0]) - act_lp))
            act_cls = next((c for c in CLASSES if classes[c] is not None and rd["actual"] in classes[c]),
                           "other" if classes["cont"] is not None else None)
            readings.append({"row": row, "residual_len": rd["residual_len"], "p_close": _r(p["close"]),
                             "p_cont": _r(p["cont"]), "p_open": _r(p["open"]),
                             "p_other": None if p["cont"] is None else _r(1.0 - p["close"] - p["cont"] - p["open"]),
                             "actual_lp": _r(act_lp), "actual_rank": act_rank, "actual_class": act_cls,
                             "n_candidates": {c: (None if v is None else len(v)) for c, v in classes.items()}})
        # fold back from the last reading: p = p(here) + p_open(here) x p(next reading)
        p_close, p_cont = readings[-1]["p_close"], readings[-1]["p_cont"]
        for r_ in reversed(readings[:-1]):
            p_close = r_["p_close"] + r_["p_open"] * p_close
            p_cont = None if p_cont is None or r_["p_cont"] is None else r_["p_cont"] + r_["p_open"] * p_cont
        out.update(status="ok", p_close=_r(p_close), p_cont=_r(p_cont), readings=readings)
        bounds.append(out)
    return {"entries": entries, "boundaries": bounds, "align_max": _r(max(aligns)) if aligns else None}


# ---------------------------------------------------------------------------------------------------------
# Talking to the server

def post(url, body, timeout, attempts=3):
    data = json.dumps(body).encode("utf-8")
    for attempt in range(1, attempts + 1):
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.loads(e.read().decode("utf-8", errors="replace"))
            except (json.JSONDecodeError, ValueError):
                return e.code, None
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if attempt == attempts:
                raise
            time.sleep(2 ** attempt)
    return None, None


def decode_npy(b64):
    return np.load(io.BytesIO(base64.b64decode(b64)), allow_pickle=False)


def _flag(command, name):
    """The last value given for a vLLM flag in a server command (the last one wins in vLLM too)."""
    val = None
    for i, a in enumerate(command):
        if a == name and i + 1 < len(command):
            val = command[i + 1]
        elif a.startswith(name + "="):
            val = a.split("=", 1)[1]
    return val


def git_head():
    """The commit checked out in the repo, read from .git (the vLLM image has no git)."""
    g = common.ROOT / ".git"
    try:
        head = (g / "HEAD").read_text().strip()
        if not head.startswith("ref: "):
            return head
        ref = head[5:]
        if (g / ref).exists():
            return (g / ref).read_text().strip()
        for line in (g / "packed-refs").read_text().splitlines():
            if line.endswith(" " + ref):
                return line.split()[0]
    except OSError:
        pass
    return "unavailable"


def keep_ids(request_id, restricted, permille):
    """A fixed sample of outputs keeps its token ids, for hf-check. Never the review set: its ids would be
    its text."""
    return (not restricted and
            int(hashlib.sha256(request_id.encode("utf-8")).hexdigest()[:8], 16) % 1000 < permille)


def source_records(src):
    recs = []
    for name, restricted in (("raw.jsonl", False), ("raw_restricted.jsonl", True)):
        p = src / name
        if p.exists():
            for r in common.read_jsonl(p):
                r["_restricted"] = restricted
                recs.append(r)
    return recs


def expected_completion_tokens(rec):
    """Tokens of the content alone: the end token is generated and counted, but not part of the text."""
    n = (rec.get("usage") or {}).get("completion_tokens")
    if n is None:
        return None
    return n - 1 if rec.get("finish_reason") == "stop" else n


def last_per_request(lines):
    out = {}
    for line in lines:
        out[line["request_id"]] = line
    return list(out.values())


def make_encoder(tok, pieces):
    lock = threading.Lock()

    def encode(text):
        with lock:
            try:
                enc = tok(text, add_special_tokens=False, return_offsets_mapping=True)
                ids, mapping = list(enc["input_ids"]), enc["offset_mapping"]
            except (ValueError, NotImplementedError):
                # MistralCommonBackend (Ministral 3) has no offset mapping: take the ids alone
                ids, mapping = list(tok.encode(text, add_special_tokens=False)), None
        spans = piece_offsets(ids, pieces, text)
        if spans is not None:
            return ids, spans, "pieces"
        if mapping is not None:
            return ids, [tuple(o) for o in mapping], "tokenizer"
        with lock:
            spans = offsets_by_decoding(tok, ids, text)
        if spans is None:
            raise ValueError("no character offsets: the tokenizer gives no offset mapping and its ids do not "
                             "decode back to the text")
        return ids, spans, "decoding"
    return encode


# ---------------------------------------------------------------------------------------------------------
# score

def score(args):
    from transformers import AutoTokenizer   # in the vLLM image; see the docstring

    src = Path(args.source).resolve()
    man = json.loads((src / "manifest.json").read_text(encoding="utf-8"))
    mcfg, model_key = man["model"], man["model_key"]
    if mcfg.get("backend") != "vllm":
        sys.exit("only runs on the local vLLM server can be read back")
    if mcfg.get("reasoning_effort"):
        sys.exit(f"{model_key} writes reasoning before its answer; reading it back is not supported yet")
    server = json.loads(Path(args.server_info).read_text(encoding="utf-8"))
    if server.get("model_key") != model_key:
        sys.exit(f"server info is for {server.get('model_key')}, the run is {model_key}")
    command = server.get("command") or []
    if "--enable-scale-out" not in command:
        sys.exit("start the server with --extra=--enable-scale-out (the token-scoring route)")
    max_ids = int(_flag(command, "--max-logprobs") or 20)
    if _flag(command, "--revision") != mcfg["revision"]:
        sys.exit(f"the scoring server runs revision {_flag(command, '--revision')}, the run used {mcfg['revision']}")
    run_digests = {(json.loads(l).get("server_info_file") or {}).get("image_digest")
                   for l in open(src / "sessions.jsonl", encoding="utf-8") if l.strip()} - {None}
    if run_digests and server.get("image_digest") not in run_digests:
        sys.exit(f"the scoring server image {server.get('image_digest')} is not the one the run used {sorted(run_digests)}")

    tok = AutoTokenizer.from_pretrained(mcfg["hf_repo"], revision=mcfg["revision"])
    t0 = time.time()
    pieces = decode_pieces(tok)
    vocab = Vocab(pieces)
    encode = make_encoder(tok, pieces)
    print(f"tokenizer {type(tok).__name__}: {len(pieces)} tokens read in {time.time() - t0:.0f}s")

    if args.out:
        out = Path(args.out).resolve()
    else:
        out = common.ROOT / "runs" / f"tf_{man['run_id']}_{dt.datetime.now(dt.timezone.utc):%Y%m%dT%H%MZ}"
    out.mkdir(parents=True, exist_ok=True)
    if not (out / "manifest.json").exists():
        (out / "manifest.json").write_text(json.dumps({
            "tf_run_id": out.name, "source_run_id": man["run_id"],
            "source_manifest_sha256": common.sha256_file(src / "manifest.json"),
            "model_key": model_key, "hf_repo": mcfg["hf_repo"], "revision": mcfg["revision"],
            "tokenizer_class": type(tok).__name__, "vocab_pieces": len(pieces),
            "vocab_pieces_sha256": common.sha256_text("\x00".join(pieces)),
            "server_info": str(Path(args.server_info)), "server_command": command, "max_logprobs": max_ids,
            "base_url": args.base_url, "tf_version": TF_VERSION, "harness_version": common.HARNESS_VERSION,
            "git_commit": git_head(), "keep_ids_permille": args.keep_ids_permille, "max_cont_ids": MAX_CONT_IDS,
            "code_sha256": {p: common.sha256_file(common.ROOT / p) for p in
                            ("harness/teacher_forced.py", "harness/common.py")},
            "classes": {k: {c: p.pattern for c, p in v.items()} | {"open": OPEN.pattern} for k, v in AFTER.items()},
            "utc": now()}, indent=1), encoding="utf-8")

    stored = json.loads((out / "manifest.json").read_text(encoding="utf-8")).get("code_sha256")
    if not stored or stored != {p: common.sha256_file(common.ROOT / p) for p in stored}:
        sys.exit(f"{out.name} was scored by other code (code_sha256 in its manifest); start a new tf run folder")
    done = set()
    if (out / "scores.jsonl").exists():
        done = {r["request_id"] for r in common.read_jsonl(out / "scores.jsonl") if r.get("status") == "ok"}
    recs = [r for r in source_records(src) if r.get("status") == "ok" and r["request_id"] not in done]
    recs.sort(key=lambda r: r["request_id"])
    if args.limit:
        recs = recs[:args.limit]
    reqs = {r["request_id"]: r for r in common.load_requests()}
    docs, prompts = common.load_documents(), common.load_prompts()
    base = args.base_url.rstrip("/")
    lock = threading.Lock()

    def one(rec):
        rid = rec["request_id"]
        line = {"request_id": rid, "restricted": rec["_restricted"], "condition": rec.get("condition"),
                "k": rec.get("k"), "n": rec.get("n"), "utc": now()}
        full = reqs.get(rid)
        if full is None:
            return {**line, "status": "skipped", "detail": "request not in the data files"}
        if rec.get("reasoning_content"):
            return {**line, "status": "skipped", "detail": "reasoning text in the output"}
        content, field = rec.get("content"), common.field_of(full, prompts)
        parsed = common.parse_output(content, field)
        if parsed["items"] is None:
            return {**line, "status": "skipped", "detail": "no list parsed"}
        lay = list_layout(content, field)
        if parsed["non_string_items"] or entry_texts(content, lay) != parsed["items"]:
            return {**line, "status": "skipped", "detail": f"layout differs from the parse ({lay['stop']})"}
        msg = common.user_message(full, docs[rec["doc_id"]], prompts)
        if common.sha256_text(msg) != rec["prompt_sha256"]:
            return {**line, "status": "skipped", "detail": "prompt changed since the run"}
        body = {"model": rec["api_model"], "messages": [{"role": "user", "content": msg}],
                "add_generation_prompt": True}
        tkw = (rec.get("request_params") or {}).get("chat_template_kwargs")
        if tkw:
            body["chat_template_kwargs"] = tkw
        st, resp = post(base + "/tokenize", body, args.timeout)
        if st != 200:
            return {**line, "status": "error", "detail": f"/tokenize HTTP {st}"}
        prompt_ids = resp["tokens"]
        enc = encode
        if rec.get("token_ids"):
            exact = exact_ids(rec["token_ids"], content, tok, pieces)
            if exact is None:
                return {**line, "status": "skipped", "detail": "generated ids do not spell the content"}
            enc = lambda text: exact  # noqa: E731
        prep = prepare(content, lay, prompt_ids, enc, vocab, max_ids)
        P, C = prep["P"], prep["C"]
        if C == 0:
            return {**line, "status": "skipped", "detail": "empty content"}
        st, resp = post(base + "/inference/v1/generate", {
            "model": rec["api_model"], "token_ids": prep["full_ids"],
            "sampling_params": {"max_tokens": 1, "temperature": 0.0, "prompt_logprobs": 0,
                                "prompt_logprob_token_ids": prep["ids"], "prompt_logprob_start": P - 1,
                                "detokenize": False}}, args.timeout)
        if st != 200:
            if not rec["_restricted"]:
                print(f"{rid}: generate HTTP {st}: {json.dumps(resp)[:300]}", file=sys.stderr)
            return {**line, "status": "error", "detail": f"generate HTTP {st}"}
        arr = decode_npy(resp["prompt_token_id_logprobs"])
        plp = resp.get("prompt_logprobs") or []
        if arr.shape != (C, len(prep["ids"])) or len(plp) != P + C:
            return {**line, "status": "error",
                    "detail": f"shapes: scores {list(arr.shape)}, prompt_logprobs {len(plp)}, "
                              f"want {C}x{len(prep['ids'])}, {P + C}"}
        actual = []
        for i in range(C):
            lp = (plp[P + i] or {}).get(str(prep["full_ids"][P + i]))
            actual.append((lp["logprob"], lp.get("rank")) if lp else (math.nan, None))
        col = {v: k for k, v in enumerate(prep["ids"])}
        res = finish(prep, actual, lambda row, ids: arr[row, [col[v] for v in ids]])
        expect = expected_completion_tokens(rec)
        stored = rec.get("prompt_token_ids_sha256")
        line.update(res, status="ok", n_prompt_tokens=P, n_content_tokens=C, offsets=prep["offsets"],
                    token_source="generated" if rec.get("token_ids") else "retokenized",
                    prompt_tokens_match=P == (rec.get("usage") or {}).get("prompt_tokens"),
                    prompt_ids_match=None if not stored else common.sha256_text(json.dumps(prompt_ids)) == stored,
                    completion_tokens=(rec.get("usage") or {}).get("completion_tokens"),
                    token_count_match=None if expect is None else C == expect,
                    finish_reason=rec.get("finish_reason"), list_stop=lay["stop"],
                    n_entries=len(lay["entries"]), n_ids_scored=len(prep["ids"]))
        if keep_ids(rid, rec["_restricted"], args.keep_ids_permille):
            line["ids"] = prep["full_ids"]
        return line

    f = open(out / "scores.jsonl", "a", encoding="utf-8", newline="\n")
    counts = Counter()

    def work(rec):
        try:
            line = one(rec)
        except Exception as e:  # noqa: BLE001  (one bad output must not stop the pass; it is recorded)
            line = {"request_id": rec["request_id"], "restricted": rec["_restricted"], "status": "error",
                    "detail": type(e).__name__}
            if not rec["_restricted"]:
                print(f"{rec['request_id']}: {type(e).__name__}: {e}", file=sys.stderr)
        with lock:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")
            f.flush()
            counts[line["status"]] += 1
            if sum(counts.values()) % 200 == 0:
                print(f"{sum(counts.values())}/{len(recs)} {dict(counts)}", flush=True)

    t0 = time.time()
    with ThreadPoolExecutor(args.workers) as ex:
        list(ex.map(work, recs))
    f.close()
    summary = summarise(last_per_request(common.read_jsonl(out / "scores.jsonl")))
    summary["seconds_this_session"] = round(time.time() - t0)
    (out / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))
    print(f"wrote {out}")


def summarise(lines):
    """Checks on the pass itself (never results): statuses, token matches, alignment, candidate coverage."""
    ok = [l for l in lines if l.get("status") == "ok"]
    bounds = [b for l in ok for b in l["boundaries"] if b.get("status") == "ok"]
    reads = [r for b in bounds for r in b["readings"]]
    aligns = [l["align_max"] for l in ok if l.get("align_max") is not None]
    others = [r["p_other"] for r in reads if r.get("p_other") is not None]
    return {
        "lines": len(lines), "status": dict(Counter(l.get("status") for l in lines)),
        "skip_reasons": dict(Counter(l.get("detail") for l in lines if l.get("status") != "ok")),
        "prompt_tokens_match": f"{sum(bool(l['prompt_tokens_match']) for l in ok)}/{len(ok)}",
        "token_count_match": f"{sum(bool(l['token_count_match']) for l in ok)}/{len(ok)}",
        "token_source": dict(Counter(l.get("token_source") for l in ok)),
        "prompt_ids_match": dict(Counter(str(l.get("prompt_ids_match")) for l in ok)),
        "offsets": dict(Counter(l.get("offsets") for l in ok)),
        "boundaries": len(bounds),
        "boundaries_unmapped": sum(1 for l in ok for b in l["boundaries"] if b.get("status") == "unmapped"),
        "two_readings": sum(1 for b in bounds if len(b["readings"]) >= 2),
        "actual_class_vs_decision": dict(Counter(f"{b['decision']}:{b['readings'][-1]['actual_class']}"
                                                 for b in bounds)),
        "p_cont_not_sent": sum(1 for b in bounds if b.get("p_cont") is None),
        "p_other_mean": round(sum(others) / len(others), 6) if others else None,
        "align_max": max(aligns) if aligns else None,
        "align_over_tolerance": sum(1 for a in aligns if a > ALIGN_TOL),
        "lines_with_ids": sum(1 for l in ok if l.get("ids")),
    }


# ---------------------------------------------------------------------------------------------------------
# hf-check

def hf_check(args):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tf = Path(args.scores).resolve()
    man = json.loads((tf / "manifest.json").read_text(encoding="utf-8"))
    src = common.ROOT / "runs" / man["source_run_id"]
    lines = [l for l in last_per_request(common.read_jsonl(tf / "scores.jsonl"))
             if l.get("status") == "ok" and l.get("ids")]
    lines.sort(key=lambda l: hashlib.sha256(l["request_id"].encode("utf-8")).hexdigest())
    lines = lines[:args.n]
    recs = {r["request_id"]: r for r in source_records(src)}
    reqs = {r["request_id"]: r for r in common.load_requests()}
    prompts = common.load_prompts()
    tok = AutoTokenizer.from_pretrained(man["hf_repo"], revision=man["revision"])
    pieces = decode_pieces(tok)
    if common.sha256_text("\x00".join(pieces)) != man["vocab_pieces_sha256"]:
        sys.exit("the tokenizer reads differently from the one the scores used")
    vocab = Vocab(pieces)
    from transformers import AutoConfig, AutoModelForImageTextToText
    arch = (AutoConfig.from_pretrained(man["hf_repo"], revision=man["revision"]).architectures or [""])[0]
    cls = AutoModelForImageTextToText if arch.endswith("ForConditionalGeneration") else AutoModelForCausalLM
    model, info = cls.from_pretrained(man["hf_repo"], revision=man["revision"], dtype=torch.bfloat16,
                                      device_map="cuda", output_loading_info=True)
    if info.get("missing_keys"):
        sys.exit(f"{arch}: {len(info['missing_keys'])} weights missing, e.g. {sorted(info['missing_keys'])[:3]}")
    model.eval()

    out = tf.parent / f"{tf.name}_hfcheck"
    out.mkdir(exist_ok=True)
    rows = []
    for l in lines:
        content = recs[l["request_id"]]["content"]
        lay = list_layout(content, common.field_of(reqs[l["request_id"]], prompts))
        P, ids = l["n_prompt_tokens"], l["ids"]
        exact = exact_ids(ids[P:], content, tok, pieces)
        if exact is None:
            rows.append({"request_id": l["request_id"], "status": "ids do not spell the content"})
            continue
        prep = prepare(content, lay, ids[:P], lambda text: exact, vocab)
        if prep["full_ids"] != ids:
            rows.append({"request_id": l["request_id"], "status": "ids differ"})
            continue
        with torch.no_grad():
            logits = model(input_ids=torch.tensor([ids], device="cuda")).logits[0, P - 1:len(ids) - 1].float()
            lp = torch.log_softmax(logits, dim=-1)                      # row i predicts content token i
            act = lp.gather(1, torch.tensor(ids[P:], device="cuda")[:, None])[:, 0]
            ranks = (lp > act[:, None]).sum(1) + 1
        hf = finish(prep, list(zip(act.tolist(), ranks.tolist())),
                    lambda row, vs: lp[row, vs].double().cpu().numpy())
        pairs = [(a, b) for a, b in zip(hf["boundaries"], l["boundaries"])
                 if a.get("status") == "ok" and b.get("status") == "ok"]
        d_close = [abs(a["p_close"] - b["p_close"]) for a, b in pairs]
        d_act = [abs(x["actual_lp"] - y["actual_lp"]) for a, b in pairs
                 for x, y in zip(a["readings"], b["readings"])]
        d_mean = [abs(a["mean_lp"] - b["mean_lp"]) for a, b in zip(hf["entries"], l["entries"])
                  if a.get("mean_lp") is not None and b.get("mean_lp") is not None]
        rows.append({"request_id": l["request_id"], "status": "ok", "n_tokens": len(ids),
                     "p_close_diff_max": _r(max(d_close)) if d_close else None,
                     "actual_lp_diff_max": _r(max(d_act)) if d_act else None,
                     "entry_mean_lp_diff_max": _r(max(d_mean)) if d_mean else None,
                     "boundaries": len(d_close), "entries": len(d_mean)})
    with open(out / "check.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    def spread(key):
        v = sorted(r[key] for r in rows if r.get(key) is not None)
        return None if not v else {"median": v[len(v) // 2], "p95": v[int(0.95 * (len(v) - 1))], "max": v[-1]}
    summary = {"tf_run_id": man["tf_run_id"], "model_key": man["model_key"], "checked": len(rows),
               "status": dict(Counter(r["status"] for r in rows)),
               "p_close_diff": spread("p_close_diff_max"), "actual_lp_diff": spread("actual_lp_diff_max"),
               "entry_mean_lp_diff": spread("entry_mean_lp_diff_max"),
               "p_close_diff_over_0.05": sum(1 for r in rows if (r.get("p_close_diff_max") or 0) > 0.05),
               "transformers": __import__("transformers").__version__, "torch": torch.__version__,
               "git_commit": git_head(), "utc": now()}
    (out / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(json.dumps(summary, indent=1))
    print(f"wrote {out}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("score")
    s.add_argument("--source", required=True, help="runs/<run_id> of a finished local vLLM run")
    s.add_argument("--server-info", required=True, help="runs/servers/<file>.json of the scoring server")
    s.add_argument("--base-url", default="http://127.0.0.1:8000")
    s.add_argument("--out", help="resume into this tf run folder")
    s.add_argument("--workers", type=int, default=8)
    s.add_argument("--timeout", type=int, default=300)
    s.add_argument("--limit", type=int, help="only the first N outputs (by request id), for a try-out")
    s.add_argument("--keep-ids-permille", type=int, default=100,
                   help="share of outputs (per thousand) that keep their token ids for hf-check")
    h = sub.add_parser("hf-check")
    h.add_argument("--scores", required=True, help="runs/<tf_run_id>")
    h.add_argument("--n", type=int, default=200)
    args = ap.parse_args()
    score(args) if args.cmd == "score" else hf_check(args)


if __name__ == "__main__":
    main()
