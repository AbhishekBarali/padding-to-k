#!/usr/bin/env python3
"""POST HOC: one row per list entry of every ok output of the main full runs, with its text and grounding.

    python analysis/posthoc/build_entries.py --runs-dir <folder of fs_* run folders> [--jobs 3]

For each fs_<model>_full run (8 GPU main models + the hosted models, arm main) it re-parses every ok record
with the frozen parser (common.parse_output, the same call full_study_score makes), takes each entry's
matcher label from the cached analysis/full/scored/<run>.entries.csv.gz (joined on request id and entry
index; the script stops if the parse and the cache disagree on the number of entries of any output), and
computes three grounding checks of the entry against its source document:
  exact     gnorm(entry) is a non-empty substring of gnorm(document)  (common_posthoc.gnorm)
  fuzzy     rapidfuzz.fuzz.partial_ratio(gnorm(entry), gnorm(document)) >= 90 (non-empty entry)
  repo_core common.in_document(entry, document): the repo's own "stretch of the document" test
            (punctuation removed, at least 4 characters)
Writes analysis/posthoc/cache/<run>.entries.pkl (gitignored: it holds entry text, review text included).
"""
import argparse
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_posthoc as cp  # noqa: E402
from common_posthoc import common  # noqa: E402

import full_study_score as fss  # noqa: E402


def build_run(args):
    run_dir, run_id = args
    from rapidfuzz import fuzz
    prompts, docs = common.load_prompts(), common.load_documents()
    req = {r["request_id"]: r for r in common.load_requests()}
    recs = fss.latest_records(run_dir)
    ent = pd.read_csv(cp.SCORED / f"{run_id}.entries.csv.gz", dtype={"gold": str, "note": str},
                      keep_default_na=False)
    ent = ent[ent["arm"] == "main"]
    by_req = {rid: g.sort_values("entry_index") for rid, g in ent.groupby("request_id", sort=False)}
    dnorm = {}
    rows = []
    for rid, g in by_req.items():
        rec = recs[rid]
        q = req[rid]
        doc = docs[q["doc_id"]]
        items = common.parse_output(rec.get("content"), common.field_of(q, prompts))["items"] or []
        if len(items) != len(g):
            raise SystemExit(f"{run_id} {rid}: parse gives {len(items)} entries, cache {len(g)}")
        if q["doc_id"] not in dnorm:
            dnorm[q["doc_id"]] = cp.gnorm(doc["text"])
        dn = dnorm[q["doc_id"]]
        for (_, e), text in zip(g.iterrows(), items):
            t = str(text)
            en = cp.gnorm(t)
            subst = e["label"] in cp.SUBST
            exact = bool(en) and en in dn
            fz = exact or (bool(en) and subst and fuzz.partial_ratio(en, dn, score_cutoff=90) >= 90)
            rows.append({"run_id": run_id, "model_key": e["model_key"], "request_id": rid,
                         "entry_index": int(e["entry_index"]), "doc_id": q["doc_id"], "set": q["set"],
                         "condition": q["condition"], "k": int(q["k"]), "n": int(q["n"]), "label": e["label"],
                         "gold": e["gold"], "note": e["note"], "text": t, "empty": not en,
                         "exact": exact, "fuzzy": bool(fz) if subst else None,
                         "repo_core": common.in_document(t, doc["text"])})
    df = pd.DataFrame(rows)
    cp.CACHE.mkdir(parents=True, exist_ok=True)
    df.to_pickle(cp.CACHE / f"{run_id}.entries.pkl")
    return run_id, len(df)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs-dir", required=True)
    ap.add_argument("--jobs", type=int, default=3)
    a = ap.parse_args()
    runs, _, _ = cp.main_runs()
    todo = [(str(Path(a.runs_dir) / r), r) for r in runs if not (cp.CACHE / f"{r}.entries.pkl").exists()]
    with ProcessPoolExecutor(max_workers=a.jobs) as ex:
        for rid, n in ex.map(build_run, todo):
            print(f"{rid}: {n} entries")


if __name__ == "__main__":
    main()
