#!/usr/bin/env python3
"""full_study_score.py: score every output of the full-study runs, one table per run (no output text).

    python analysis/full_study_score.py --runs-dir <folder holding the fs_* run folders> [--jobs 3]

Used by analysis/full_study.py (`score` step); it can also run on its own. For every run folder it writes
  <cache>/<run_id>.outputs.csv.gz   one row per covered request id (the `none` answer is reused at k = 1, 3, 5)
  <cache>/<run_id>.entries.csv.gz   one row per list entry of every ok output, with the matcher's label
  <cache>/<run_id>.source.json      sha256 of the run's record files, so a changed run is rescored

What is scored, and with what (all frozen at tag prereg-v2.1, none of it changed here):
- parsing, placeholders, repeats and substantive entries: harness/common.py (parse_output, count_items), the
  same calls harness/score_counts.py makes, so every count equals score_counts' per-output table
  (analysis/tests/test_full_study_score.py checks it row by row);
- entry labels: analysis/matcher.py (v0, thresholds unchanged), applied the way the pilot's matcher numbers
  were made (match_output with the request's prompt text). Its DocIndex is built once per document here,
  which changes no result (the index depends only on the document);
- only records with status "ok" are outputs. A transport failure or a request never answered is MISSING
  (status column), never an output, and is left out of every pair.

Extra per-output fields the protocol asks for (section 5.2), computed from the same parse:
  n_subst_bound   substantive entries, with every entry of 8 words or fewer that holds "no", "none", "not",
                  "only", "other", "additional" or "found" taken as a note (the placeholder bound)
  matched_gold    true items some entry matches (matcher labels true_item and split_of_true)
  left_out        n - matched_gold (true items no entry matches)
  outside_note    the text outside the JSON holds a note saying fewer items exist: common.is_placeholder()
                  applied to each sentence of it (sentences split at . ! ? newlines and colons)
  sort            on documents with n < k: padded | says_short | honest_short | unreadable (C3)
  shortfall_phrase  the thinking text names a shortfall (phrase search, unchecked by hand; C16)
"""
import argparse
import csv
import gzip
import hashlib
import json
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))
sys.path.insert(0, str(ROOT / "analysis"))
import common  # noqa: E402
import matcher  # noqa: E402

SCORE_VERSION = "fs-2"
OUT_COLS = ["run_id", "model_key", "arm", "request_id", "source_request_id", "doc_id", "group", "set", "split",
            "condition", "k", "n", "wording_id", "enforce_schema", "request_seed", "status", "finish_reason",
            "parse_rung", "list_source", "text_outside_json", "valid", "n_items", "n_substantive",
            "n_placeholder", "n_escape", "n_duplicate", "n_subst_bound", "over_count", "excess", "exact_k",
            "fewer_than_k", "more_than_k", "exact_n", "truncated", "reasoning_chars", "matched_gold", "left_out",
            "n_true", "n_split", "n_wrong_type", "n_invented", "n_invented_note", "outside_note", "sort",
            "shortfall_phrase", "content_sha1"]
ENT_COLS = ["run_id", "model_key", "arm", "request_id", "entry_index", "doc_id", "set", "condition", "k", "n",
            "label", "gold", "note", "n_words"]
BOUND_WORDS = re.compile(r"\b(no|none|not|only|other|additional|found)\b", re.I)
# C16: a thinking trace that notices the shortfall. A phrase search, named as unchecked by hand.
SHORTFALL = re.compile(
    r"\b(only (has |have |contains |lists |mentions |gives |names )?(one|two|three|four|1|2|3|4)\b|fewer than|less than (the )?(required|requested|asked)|not enough|"
    r"(there (is|are) )?no (more|other|further|additional)\b|can'?t find (more|enough|any more)|"
    r"(doesn'?t|does not) (contain|have|mention) (enough|that many|\d+|any)|"
    r"(need|have) to (make up|invent|pad|fill)|pad(ding)? (the|it|with)|placeholder)", re.I)
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+|:\s+")


# ---------------------------------------------------------------------------------------------
_DOC_INDEX = {}
_ORIG_DOC_INDEX = matcher.DocIndex


def _cached_doc_index(doc):
    """matcher.DocIndex, built once per document (it reads only the document's text and gold items, so the
    key is those, not just the id)."""
    key = (doc["doc_id"], hash(doc["text"]), json.dumps(doc.get("gold_items"), sort_keys=True))
    if key not in _DOC_INDEX:
        _DOC_INDEX[key] = _ORIG_DOC_INDEX(doc)
    return _DOC_INDEX[key]


class cached_doc_index:
    """Use the cached DocIndex inside a `with` block only, so importing this module changes nothing."""

    def __enter__(self):
        matcher.DocIndex = _cached_doc_index

    def __exit__(self, *exc):
        matcher.DocIndex = _ORIG_DOC_INDEX


def outside_text(content):
    """The reply with any reasoning block, fenced blocks and balanced {...} / [...] spans removed."""
    if not content:
        return ""
    text = common.REASONING_BLOCK.sub("", content.strip())
    text = common.FENCE.sub(" ", text)
    for o, c in (("{", "}"), ("[", "]")):
        spans = list(common._balanced(text, o, c))
        for a, b in reversed(spans):
            text = text[:a] + " " + text[b:]
    return text.strip()


def outside_note(content, doc_text, esc):
    """A sentence outside the JSON that the note rules of common.py read as 'nothing here / fewer exist'."""
    rest = outside_text(content)
    if not rest:
        return False
    for seg in SENT_SPLIT.split(rest):
        seg = seg.strip(" *_#>-\t")
        if len(common.core(seg)) >= 2 and common.is_placeholder(seg, esc, doc_text):
            return True
    return False


def bound_count(substantive):
    return sum(1 for s in substantive if len(s.split()) <= 8 and BOUND_WORDS.search(s))


def latest_records(run_dir):
    """The last record per request id (resends replace earlier failures), raw then raw_restricted."""
    recs = {}
    for name in ("raw.jsonl", "raw_restricted.jsonl"):
        p = Path(run_dir) / name
        if p.exists():
            with open(p, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        r = json.loads(line)
                        recs[r["request_id"]] = r
    return recs


def source_hash(run_dir):
    h = hashlib.sha256(SCORE_VERSION.encode())
    for name in ("manifest.json", "planned.jsonl", "raw.jsonl", "raw_restricted.jsonl"):
        p = Path(run_dir) / name
        h.update(name.encode())
        if p.exists():
            h.update(common.sha256_file(p).encode())
    return h.hexdigest()


class Context:
    def __init__(self):
        self.prompts = common.load_prompts()
        self.docs = common.load_documents()
        self.req = {r["request_id"]: r for r in common.load_requests()}
        self.esc = self.prompts.get("escape_value", "N/A")
        self._ptext = {}

    def prompt_text(self, q):
        key = (q["schema_id"], q.get("instruction"), q.get("schema_block_id"))
        if key not in self._ptext:
            self._ptext[key] = matcher.prompt_text_of(q, self.prompts)
        return self._ptext[key]


def score_output(ctx, q, doc, rec):
    """All per-output fields and the entry labels of one ok record."""
    field = common.field_of(q, ctx.prompts)
    parsed = common.parse_output(rec.get("content"), field)
    valid = parsed["items"] is not None
    items = parsed["items"] or []
    c = common.count_items(items, ctx.esc, doc["text"])
    m, n, k = c["n_substantive"], q["n"], q["k"]
    labels = matcher.match_output(doc, items, ctx.esc, ctx.prompt_text(q)) if items else []
    matched = set()
    cnt = {"true_item": 0, "split_of_true": 0, "in_text_wrong_type": 0, "plausible_invented": 0}
    inv_note = 0
    for x in labels:
        if x["label"] in ("true_item", "split_of_true"):
            matched.update(x["gold"] or [])
        if x["label"] in cnt:
            cnt[x["label"]] += 1
        if x["label"] == "plausible_invented" and x["note"] in ("prompt_echo", "possible_note"):
            inv_note += 1
    onote = outside_note(rec.get("content"), doc["text"], ctx.esc)
    over = valid and m > n
    if not valid:
        sort = "unreadable"
    elif over:
        sort = "padded"
    elif c["n_placeholder"] or onote:
        sort = "says_short"
    else:
        sort = "honest_short"
    reasoning = rec.get("reasoning_content") or ""
    row = {
        "finish_reason": rec.get("finish_reason"), "parse_rung": parsed["parse_rung"],
        "list_source": parsed["list_source"], "text_outside_json": parsed["text_outside_json"],
        "valid": valid, "n_items": c["n_items"], "n_substantive": m, "n_placeholder": c["n_placeholder"],
        "n_escape": c["n_escape"], "n_duplicate": c["n_duplicate"],
        "n_subst_bound": m - bound_count(c["substantive"]),
        "over_count": over, "excess": max(0, m - n) if valid else 0,
        "exact_k": valid and c["n_items"] == k, "fewer_than_k": valid and c["n_items"] < k,
        "more_than_k": valid and c["n_items"] > k, "exact_n": valid and m == n,
        "truncated": rec.get("finish_reason") == "length", "reasoning_chars": len(reasoning),
        "matched_gold": len(matched), "left_out": n - len(matched),
        "n_true": cnt["true_item"], "n_split": cnt["split_of_true"], "n_wrong_type": cnt["in_text_wrong_type"],
        "n_invented": cnt["plausible_invented"], "n_invented_note": inv_note, "outside_note": onote,
        "sort": sort if n < k else "",
        "shortfall_phrase": bool(reasoning and SHORTFALL.search(reasoning)),
        "content_sha1": hashlib.sha1((rec.get("content") or "").encode("utf-8")).hexdigest()[:12],
    }
    ents = [{"entry_index": i, "label": x["label"], "gold": "+".join(map(str, x["gold"] or [])),
             "note": x["note"] if x["note"] in ("prompt_echo", "possible_note") else "",
             "n_words": len(str(items[i]).split())} for i, x in enumerate(labels)]
    return row, ents


def score_run(run_dir, cache_dir, force=False):
    run_dir, cache_dir = Path(run_dir), Path(cache_dir)
    man = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    rid = man["run_id"]
    src = source_hash(run_dir)
    meta = cache_dir / f"{rid}.source.json"
    if not force and meta.exists() and json.loads(meta.read_text())["source"] == src:
        return rid, "cached"
    with cached_doc_index():
        return _score_run(run_dir, cache_dir, man, rid, src, meta)


def _score_run(run_dir, cache_dir, man, rid, src, meta):
    ctx = Context()
    planned = common.read_jsonl(run_dir / "planned.jsonl")
    recs = latest_records(run_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    n_out = n_ent = 0
    tmp_o, tmp_e = cache_dir / f"{rid}.outputs.csv.gz.tmp", cache_dir / f"{rid}.entries.csv.gz.tmp"
    with gzip.open(tmp_o, "wt", newline="", encoding="utf-8") as fo, \
            gzip.open(tmp_e, "wt", newline="", encoding="utf-8") as fe:
        wo, we = csv.DictWriter(fo, OUT_COLS), csv.DictWriter(fe, ENT_COLS)
        wo.writeheader()
        we.writeheader()
        for p in planned:
            rec = recs.get(p["request_id"])
            src_rid = p.get("source_request_id") or ""
            base_q = ctx.req[src_rid or p["request_id"]]
            doc = ctx.docs[base_q["doc_id"]]
            ok = rec is not None and rec["status"] == "ok"
            scored, ents = score_output(ctx, base_q, doc, rec) if ok else ({}, [])
            arm = p.get("arm") or base_q.get("arm") or "main"
            covered = [p["request_id"], *p.get("also_answers", [])]
            for i, cid in enumerate(covered):
                q = base_q if i == 0 else ctx.req[cid]
                row = {"run_id": rid, "model_key": man["model_key"], "arm": arm, "request_id": cid,
                       "source_request_id": src_rid, "doc_id": q["doc_id"], "group": doc.get("group") or q["doc_id"],
                       "set": q["set"], "split": doc["split"], "condition": q["condition"], "k": q["k"],
                       "n": q["n"], "wording_id": q["wording_id"], "enforce_schema": q["enforce_schema"],
                       "request_seed": man.get("request_seed") or "",
                       "status": rec["status"] if rec else "missing"}
                if ok:
                    s = dict(scored)
                    if i:                      # the `none` answer reused at another k: k-dependent fields again
                        k, n, m = q["k"], q["n"], s["n_substantive"]
                        s.update(exact_k=s["valid"] and s["n_items"] == k, fewer_than_k=s["valid"] and s["n_items"] < k,
                                 more_than_k=s["valid"] and s["n_items"] > k)
                        if not s["valid"]:
                            s["sort"] = "unreadable" if n < k else ""
                        elif s["over_count"]:
                            s["sort"] = "padded" if n < k else ""
                        else:
                            s["sort"] = ("says_short" if (s["n_placeholder"] or s["outside_note"]) else "honest_short") \
                                if n < k else ""
                    row.update(s)
                wo.writerow(row)
                n_out += 1
            for e in ents:
                we.writerow({"run_id": rid, "model_key": man["model_key"], "arm": arm, "request_id": p["request_id"],
                             "doc_id": base_q["doc_id"], "set": base_q["set"], "condition": base_q["condition"],
                             "k": base_q["k"], "n": base_q["n"], **e})
                n_ent += 1
    tmp_o.replace(cache_dir / f"{rid}.outputs.csv.gz")
    tmp_e.replace(cache_dir / f"{rid}.entries.csv.gz")
    meta.write_text(json.dumps({"run_id": rid, "model_key": man["model_key"], "source": src,
                                "score_version": SCORE_VERSION, "matcher": matcher.MATCHER_VERSION,
                                "rows": n_out, "entries": n_ent}, indent=1), encoding="utf-8")
    return rid, f"scored {n_out} rows, {n_ent} entries"


def run_folders(runs_dir):
    return sorted(p for p in Path(runs_dir).iterdir() if p.is_dir() and (p / "manifest.json").exists()
                  and (p / "planned.jsonl").exists())


def score_all(runs_dir, cache_dir, jobs=3, force=False, only=None):
    dirs = [d for d in run_folders(runs_dir) if not only or d.name in only]
    if jobs <= 1:
        return [score_run(d, cache_dir, force) for d in dirs]
    with ProcessPoolExecutor(max_workers=jobs) as ex:
        return list(ex.map(score_run, dirs, [cache_dir] * len(dirs), [force] * len(dirs)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs-dir", required=True)
    ap.add_argument("--cache", default=str(ROOT / "analysis" / "full" / "scored"))
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--only", nargs="*")
    args = ap.parse_args()
    for rid, what in score_all(args.runs_dir, args.cache, args.jobs, args.force, args.only):
        print(f"{rid}: {what}")


if __name__ == "__main__":
    main()
