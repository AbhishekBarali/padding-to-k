#!/usr/bin/env python3
"""fewer_ok_recall.py (post hoc): an interval for the recall cost of the "fewer is fine" line.

The registered outcome "true items left out" (share of true items no entry matches, documents with n >= 1,
k = 3 and 5; analysis/full/RESULTS.md section 5) is reported per condition as a point estimate: 17.0% with no
count, 24.3% with "fewer is fine". This adds the paired difference with the registered bootstrap: for every
(model, document, k) answered under both conditions, the left-out share under min_k_shown_fewer_ok minus the
share under none, each a ratio of sums (true items left out over true items), with 10,000 draws over document
groups within set (analysis/full_study.py, Bootstrap). Labels are the cached matcher v0 labels; nothing in the
locked scorer changes.

    python analysis/posthoc/fewer_ok_recall.py [--scored <folder of *.outputs.csv.gz>] [--boot 10000]

Writes analysis/posthoc/out/fewer_ok_recall.md.
"""
import argparse
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
import full_study as fs  # noqa: E402

A, B = "min_k_shown_fewer_ok", "none"
DROP = "qwen3.5-0.8b"


def unpaired(f, cond):
    pos = f[f["ok"] & (f["condition"] == cond) & (f["n"] >= 1) & f["k"].isin((3, 5))]
    return 100 * pos["left_out"].sum() / max(1, pos["n"].sum())


def paired_diff(f, boot):
    sel = f[f["ok"] & f["condition"].isin([A, B]) & (f["n"] >= 1) & f["k"].isin((3, 5))]
    g = sel.groupby(["model_key", "doc_id", "k", "condition"], observed=True)[["left_out", "n"]].mean()
    g = g.unstack("condition").dropna()
    g.columns = [f"{v}|{c}" for v, c in g.columns]
    info = sel.drop_duplicates("doc_id").set_index("doc_id")[["group", "set"]]
    g = g.reset_index().join(info, on="doc_id")
    per_group, strata = defaultdict(lambda: np.zeros(4)), {}
    for row in g.to_dict("records"):
        per_group[row["group"]] += [row[f"left_out|{A}"], row[f"n|{A}"], row[f"left_out|{B}"], row[f"n|{B}"]]
        strata[row["group"]] = row["set"]
    res = boot.stat(dict(per_group), strata, lambda v: v[..., 0] / v[..., 1] - v[..., 2] / v[..., 3])
    res["pairs"] = len(g)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scored", default=str(fs.CACHE))
    ap.add_argument("--boot", type=int, default=10000)
    a = ap.parse_args()

    df, _ = fs.load_scored(a.scored)
    df = fs.add_doc_fields(df, fs.doc_table())
    main_models = [m for m in fs.NAME if not m.startswith(("together-", "bedrock-"))]
    df = df[(df["kind"] == "full") & (df["arm"] == "main") & df["model_key"].isin(main_models)]
    boot = fs.Bootstrap(a.boot)

    lines = ["# Post hoc: the recall cost of \"fewer is fine\", with an interval", "",
             "True items left out (%%), documents with n >= 1, k = 3 and 5, matcher v0 labels. Unpaired: every ok output "
             "of the condition, as in RESULTS.md section 5. Paired: (model, document, k) answered under both conditions; "
             "difference in points with a 95%% interval from %d draws over document groups within set." % a.boot, "",
             "| models | left out, none | left out, fewer is fine | paired difference (points) | pairs | groups |",
             "|---|---|---|---|---|---|"]
    for label, f in (("8 GPU models (registered)", df), ("7 GPU models, without Qwen3.5-0.8B", df[df.model_key != DROP])):
        f = f.copy()
        f["model_key"] = f["model_key"].cat.remove_unused_categories()
        d = paired_diff(f, boot)
        lines.append("| %s | %.1f | %.1f | %+.1f [%+.1f, %+.1f] | %d | %d |" % (
            label, unpaired(f, B), unpaired(f, A), 100 * d["est"], 100 * d["lo"], 100 * d["hi"], d["pairs"], d["groups"]))
    out = ROOT / "analysis" / "posthoc" / "out" / "fewer_ok_recall.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
