#!/usr/bin/env python3
"""rq7.py: confidence of extra entries (RQ7, exploratory), PRELIMINARY preview on the dev set.

    python3 analysis/rq7.py --tf runs/tf_<model>_dev_<utc> [...] --labels analysis/dev/matcher_entries_dev.csv
        [--out analysis/dev] [--boot 2000]

Question: are list entries that are not true items written with lower token probability than true ones? If
so, probabilities alone could flag padding. For every scored entry it joins the teacher-forced pass (the
model's own output read back without the grammar: mean, minimum and first-token log probability of the
entry, `harness/teacher_forced.py`) with the matcher's label (`analysis/matcher.py run`). True = true_item;
extra = in_text_wrong_type or plausible_invented. split_of_true, placeholder and repeat are left out. The
AUROC says how often an extra entry has a LOWER score than a true one (0.5 = no signal); the 95% interval
comes from a bootstrap over document groups.

Dev outputs only, labels from the matcher v0 (fitted on provisional labels that are not the authors'), so
every number here is preliminary. The registered RQ7 runs on the pilot with the authors' labels.
"""
import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))
import common  # noqa: E402

TRUE = {"true_item"}
EXTRA = {"in_text_wrong_type", "plausible_invented"}
SCORES = ("mean_lp", "min_lp", "first_lp", "position")   # position: minus the entry index, the baseline


def auroc(extra, true):
    """P(score of an extra entry < score of a true entry), ties counted half (Mann-Whitney)."""
    if len(extra) == 0 or len(true) == 0:
        return None
    e = np.sort(np.asarray(extra, dtype=float))
    t = np.asarray(true, dtype=float)
    below = np.searchsorted(e, t, side="left")          # extra entries scoring lower than each true one
    tied = np.searchsorted(e, t, side="right") - below
    return float((below.sum() + 0.5 * tied.sum()) / (len(e) * len(t)))


def boot_ci(groups, score, n_boot, rng):
    """95% interval over document groups: groups maps group -> (extra scores, true scores)."""
    keys = list(groups)
    vals = []
    for _ in range(n_boot):
        pick = rng.choice(len(keys), len(keys), replace=True)
        e = np.concatenate([groups[keys[i]][0][score] for i in pick])
        t = np.concatenate([groups[keys[i]][1][score] for i in pick])
        a = auroc(e, t)
        if a is not None:
            vals.append(a)
    return (float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))) if vals else (None, None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tf", nargs="+", required=True, help="teacher-forced run folders (dev)")
    ap.add_argument("--labels", required=True, help="matcher_entries_dev.csv from analysis/matcher.py run")
    ap.add_argument("--out", default=str(ROOT / "analysis" / "dev"))
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=20261014)
    args = ap.parse_args()

    labels = {}
    for r in csv.DictReader(open(args.labels, encoding="utf-8")):
        labels[(r["model_key"], r["request_id"], int(r["entry_index"]))] = r
    docs = common.load_documents()
    rng = np.random.default_rng(args.seed)

    lines = ["# RQ7 preview: confidence of extra entries (dev set, PRELIMINARY)", "",
             "True = true_item; extra = in_text_wrong_type or plausible_invented (matcher v0 labels, fitted on",
             "provisional labels that are not the authors'). AUROC = how often an extra entry scores LOWER than a",
             f"true one (0.5 = no signal). 95% intervals from {args.boot} bootstrap draws over document groups. Dev outputs only.",
             "`position` is the baseline: the entry's place in the list alone (a later entry counts as lower).",
             "", "| model | score | true | extra | AUROC | 95% interval | wrong type only | invented only |",
             "|---|---|---|---|---|---|---|---|"]
    for tf_dir in args.tf:
        tf_dir = Path(tf_dir)
        man = json.loads((tf_dir / "manifest.json").read_text(encoding="utf-8"))
        model = man["model_key"]
        per_group = defaultdict(lambda: ([], [], [], []))   # extra, true, extra_wrong, extra_inv: rows of scores
        n_join = 0
        for rec in common.read_jsonl(tf_dir / "scores.jsonl"):
            if rec.get("status") != "ok" or rec.get("restricted"):
                continue
            rid = rec["request_id"]
            for e in rec.get("entries") or []:
                lab = labels.get((model, rid, e["i"]))
                if lab is None or lab["label"] not in TRUE | EXTRA:
                    continue
                n_join += 1
                d = docs.get(lab["doc_id"]) or {}
                g = d.get("group") or lab["doc_id"]
                row = [e.get(s) for s in SCORES[:-1]] + [-float(e["i"])]   # last: position baseline (later = lower)
                if any(v is None for v in row):
                    continue
                if lab["label"] in TRUE:
                    per_group[g][1].append(row)
                else:
                    per_group[g][0].append(row)
                    per_group[g][2 if lab["label"] == "in_text_wrong_type" else 3].append(row)
        groups = {g: tuple({s: np.array([r[j] for r in v], dtype=float) for j, s in enumerate(SCORES)}
                           for v in vals) for g, vals in per_group.items()}
        for s in SCORES:
            e = np.concatenate([groups[g][0][s] for g in groups]) if groups else np.array([])
            t = np.concatenate([groups[g][1][s] for g in groups]) if groups else np.array([])
            ew = np.concatenate([groups[g][2][s] for g in groups]) if groups else np.array([])
            ei = np.concatenate([groups[g][3][s] for g in groups]) if groups else np.array([])
            a = auroc(e, t)
            lo, hi = boot_ci({g: (groups[g][0], groups[g][1]) for g in groups}, s, args.boot, rng)
            aw, ai = auroc(ew, t), auroc(ei, t)
            fmt = lambda x: "-" if x is None else f"{x:.3f}"   # noqa: E731
            lines.append(f"| {model} | {s} | {len(t)} | {len(e)} | {fmt(a)} | {fmt(lo)} to {fmt(hi)} | "
                         f"{fmt(aw)} ({len(ew)}) | {fmt(ai)} ({len(ei)}) |")
        print(f"{model}: {n_join} labelled entries joined from {tf_dir.name}")
    lines += ["", "Inputs: " + ", ".join(Path(t).name for t in args.tf) + f"; labels {Path(args.labels).name}.", ""]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "rq7_dev.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out / 'rq7_dev.md'}")


if __name__ == "__main__":
    main()
