#!/usr/bin/env python3
"""POST HOC: a lenient parser for Qwen3.5-0.8B, which often writes its answer list inside a copy of the JSON
schema. The locked parser (harness/common.py parse_output) never takes a schema-shaped object as the answer
(protocol 5.1); this script does not change it. It rescores the 0.8B full run with a parser that first runs the
locked ladder and, only when that finds no list, looks inside every JSON object of the reply for the asked-for
field:
  schema copy       {"properties": {"<field>": [ ... ]}}                      -> that list
  schema copy, items {"properties": {"<field>": {"type": "array", "items": [ ... ]}}} -> that list
  wrapper           any other nesting, {"answer": {"<field>": [ ... ]}}       -> that list
A pure schema echo ("items": {"type": "string"}, no list) and broken JSON stay unreadable.

    python analysis/posthoc/lenient_08b.py --runs-dir <folder of fs_* run folders> [--boot 10000]

Step 1 rescores the run with the repo's own scorer (analysis/full_study_score.py score_run: same counts, same
matcher v0) into analysis/posthoc/cache/lenient/, with only the parse call swapped. Step 2 checks that every
output the locked parser could read is unchanged, then compares strict and lenient: unreadable share,
the main contrasts (contrast 2, shown minimum vs no count: length change and over-count, with full_study's
bootstrap), and mean entries / over-count per condition. Results: analysis/posthoc/out/lenient_08b.json and .md.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_posthoc as cp  # noqa: E402
from common_posthoc import common, full_study as fs  # noqa: E402

import full_study_score as fss  # noqa: E402

MODEL = "qwen3.5-0.8b"
RUN = f"fs_{MODEL}_full"
LCACHE = cp.CACHE / "lenient"
_STRICT = common.parse_output


def _candidates(text):
    text = common.REASONING_BLOCK.sub("", (text or "").strip()).strip()
    out = []
    try:
        out.append(json.loads(text))
    except (json.JSONDecodeError, ValueError):
        for m in common.FENCE.finditer(text):
            try:
                out.append(json.loads(m.group(1).strip()))
            except (json.JSONDecodeError, ValueError):
                pass
        for a, b in common._balanced(text, "{", "}"):
            try:
                out.append(json.loads(text[a:b]))
            except (json.JSONDecodeError, ValueError):
                pass
    return out


def _find(obj, field, path=()):
    """Depth-first, in key order: (list, how) for the first value under key `field` that is a list, or a dict
    whose "items" is a list."""
    if isinstance(obj, dict):
        for key, v in obj.items():
            if key == field:
                if isinstance(v, list):
                    return v, "schema_copy" if "properties" in path else "wrapper"
                if isinstance(v, dict) and isinstance(v.get("items"), list):
                    return v["items"], "schema_copy_items"
            got = _find(v, field, path + (key,))
            if got:
                return got
    elif isinstance(obj, list):
        for v in obj:
            got = _find(v, field, path)
            if got:
                return got
    return None


def parse_lenient(content, field):
    out = _STRICT(content, field)
    if out["items"] is not None:
        return out
    for obj in _candidates(content):
        got = _find(obj, field)
        if got:
            arr, how = got
            items = []
            for x in arr:
                if isinstance(x, str):
                    items.append(x)
                elif isinstance(x, dict) and len(x) == 1 and isinstance(next(iter(x.values())), str):
                    items.append(next(iter(x.values())))
                else:
                    items.append("" if x is None else json.dumps(x, ensure_ascii=False))
            out = dict(out, parse_rung="lenient_" + how, list_source="lenient", items=items)
            return out
    return out


def rescore(runs_dir):
    LCACHE.mkdir(parents=True, exist_ok=True)
    common.parse_output = parse_lenient          # only in this process; the locked file is untouched
    try:
        return fss.score_run(Path(runs_dir) / RUN, LCACHE, force=True)
    finally:
        common.parse_output = _STRICT


def frames():
    docs = fs.doc_table()
    out = {}
    for tag, cache in (("strict", cp.SCORED), ("lenient", LCACHE)):
        df, _ = fs.load_scored(cache) if tag == "lenient" else _load_one(cache)
        df = fs.add_doc_fields(df, docs)
        out[tag] = df[(df["kind"] == "full") & (df["arm"] == "main") & (df["model_key"] == MODEL)]
    return out


def _load_one(cache):
    """full_study.load_scored on the strict cache, 0.8B full run only (via a temporary folder of links)."""
    import tempfile
    tmp = Path(tempfile.mkdtemp())
    for suf in (".outputs.csv.gz", ".source.json"):
        (tmp / f"{RUN}{suf}").symlink_to((Path(cache) / f"{RUN}{suf}").resolve())
    return fs.load_scored(tmp)


def r2(x):
    return None if x is None else {k: (round(v, 4) if isinstance(v, float) else v) for k, v in x.items()}


def analyse(boot):
    F = frames()
    s, l = F["strict"], F["lenient"]
    key = ["request_id"]
    a = s.set_index(key).sort_index()
    b = l.set_index(key).sort_index()
    assert list(a.index) == list(b.index), "strict and lenient tables cover different requests"
    was_ok = a["ok"] & (a["valid"] == 1)
    cols = ["n_items", "n_substantive", "over_count", "excess", "matched_gold", "n_true", "n_split",
            "n_wrong_type", "n_invented"]
    changed = int((a.loc[was_ok, cols].fillna(-9).values != b.loc[was_ok, cols].fillna(-9).values).any(axis=1).sum())
    B = fs.Bootstrap(boot)
    res = {"unchanged_check": {"outputs_readable_strict": int(was_ok.sum()), "changed_by_lenient": changed}}
    for tag, f in F.items():
        ok = f[f["ok"]]
        lt = ok[(ok["n"] < ok["k"]) & ok["k"].isin((3, 5))]
        r = {"ok_outputs": int(len(ok)), "unreadable": int((ok["valid"] == 0).sum()),
             "unreadable_pct": round(100 * float((ok["valid"] == 0).mean()), 2),
             "rungs": {str(k): int(v) for k, v in ok["parse_rung"].astype(str).value_counts().items()}}
        r["C2_length"] = r2(B.mean(fs.contrast_pairs(f, "C2")))
        r["C2_over_count"] = r2(B.mean(fs.contrast_pairs(f, "C2", "over_count")))
        r["C1_length"] = r2(B.mean(fs.contrast_pairs(f, "C1")))
        r["C3_length"] = r2(B.mean(fs.contrast_pairs(f, "C3")))
        r["fewer_ok_vs_none_length"] = r2(B.mean(fs.paired(f, "min_k_shown_fewer_ok", "none")))
        per = {}
        for c in fs.CONDS:
            sub = lt[lt["condition"] == c]
            if len(sub):
                per[c] = {"outputs": int(len(sub)), "mean_entries": round(float(sub["n_substantive"].mean()), 3),
                          "over_count_pct": round(100 * float(sub["over_count"].mean()), 1),
                          "unreadable_pct": round(100 * float(1 - sub["valid"].mean()), 1),
                          "mean_entries_readable": round(float(sub.loc[sub["valid"] == 1, "n_substantive"].mean()), 3)}
        r["per_condition_n_lt_k"] = per
        # the same contrast on outputs readable under BOTH parsers is the strict pairs; on lenient-readable only:
        rd = f[f["valid"] == 1]
        r["C2_length_readable_pairs"] = r2(B.mean(fs.contrast_pairs(rd, "C2")))
        r["C2_over_count_readable_pairs"] = r2(B.mean(fs.contrast_pairs(rd, "C2", "over_count")))
        res[tag] = r
    return res


def write(res):
    cp.OUT.mkdir(parents=True, exist_ok=True)
    (cp.OUT / "lenient_08b.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    f = lambda r, sc=1.0, nd=2: fs.fmt(r, sc, nd)  # noqa: E731
    L = ["# POST HOC: Qwen3.5-0.8B with a lenient parser", "",
         "Written by `analysis/posthoc/lenient_08b.py`. Strict = the locked parser (the paper's numbers); lenient = "
         "the same ladder, plus the answer list taken from inside a schema copy or a wrapper object.", "",
         f"- Outputs the locked parser reads: {res['unchanged_check']['outputs_readable_strict']}; of them changed by "
         f"the lenient parser: {res['unchanged_check']['changed_by_lenient']} (must be 0).", "",
         "| measure | strict | lenient |", "|---|---|---|"]
    s, l = res["strict"], res["lenient"]
    L.append(f"| unreadable outputs, all conditions and k | {s['unreadable']} of {s['ok_outputs']} ({s['unreadable_pct']}%) | "
             f"{l['unreadable']} of {l['ok_outputs']} ({l['unreadable_pct']}%) |")
    for k, lab, sc, nd in (("C2_length", "C2 shown minimum vs no count, length change (entries)", 1, 2),
                           ("C2_over_count", "C2 over-count (points)", 100, 1),
                           ("C2_length_readable_pairs", "C2 length, pairs readable on both sides", 1, 2),
                           ("C2_over_count_readable_pairs", "C2 over-count, pairs readable on both sides (points)", 100, 1),
                           ("C1_length", "C1 dose k=5 vs k=3 (entries)", 1, 2),
                           ("C3_length", "C3 shown minimum vs shown maximum (entries)", 1, 2),
                           ("fewer_ok_vs_none_length", "fewer-ok minimum vs no count (entries)", 1, 2)):
        L.append(f"| {lab} | {f(s[k], sc, nd)} (pairs {s[k]['pairs'] if s[k] else 0}) | "
                 f"{f(l[k], sc, nd)} (pairs {l[k]['pairs'] if l[k] else 0}) |")
    L += ["", "Per condition, documents with n < k, k = 3 and 5 (unreadable outputs count as 0 entries, as in the paper):", "",
          "| condition | outputs | mean entries strict | mean entries lenient | over-count % strict | over-count % lenient | unreadable % strict | unreadable % lenient |",
          "|---|---|---|---|---|---|---|---|"]
    for c in fs.CONDS:
        a, b = s["per_condition_n_lt_k"].get(c), l["per_condition_n_lt_k"].get(c)
        if a and b:
            L.append(f"| {c} | {a['outputs']} | {a['mean_entries']:.2f} | {b['mean_entries']:.2f} | {a['over_count_pct']} | "
                     f"{b['over_count_pct']} | {a['unreadable_pct']} | {b['unreadable_pct']} |")
    L += ["", "Lenient parse rungs (ok outputs): " + ", ".join(f"{k} {v}" for k, v in sorted(l["rungs"].items()))]
    (cp.OUT / "lenient_08b.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs-dir", required=True)
    ap.add_argument("--boot", type=int, default=10000)
    ap.add_argument("--skip-rescore", action="store_true")
    a = ap.parse_args()
    if not a.skip_rescore:
        print(rescore(a.runs_dir))
    write(analyse(a.boot))


if __name__ == "__main__":
    main()
