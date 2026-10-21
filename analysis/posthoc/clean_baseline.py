#!/usr/bin/env python3
"""POST HOC (not in the registered plan): over-count on the documents a model gets right with no count.

With no count at all, 34.5% of GPU outputs on n < k documents already list more than n substantive entries,
so the 55.4% under a shown minimum mixes padding the count causes with over-listing the model does anyway.
This keeps only the (GPU model, document) pairs whose no-count output was clean and asks how often the same
model on the same document over-counts under each count condition. Two clean definitions:
  (a) exact:        the no-count output has exactly n substantive entries;
  (b) not over:     the no-count output does not over-count (at most n substantive entries).
Counts are the cached frozen scores (analysis/full/scored/; unreadable outputs count as 0 entries); nothing
is re-scored.

Pairing is the paper's: one cell per (model, document, k), documents with n < k, k = 3 and 5, ok outputs only,
a prose condition's wordings averaged within the cell first (full_study.paired). The no-count answer is sent
once per document and covers every k, so a clean pair contributes one cell per k with n < k. Intervals: the
registered bootstrap (full_study.Bootstrap: 95% percentile, document groups resampled within set, seed
20261014), here over the cells' over-count share.

    python analysis/posthoc/clean_baseline.py [--scored <folder of *.outputs.csv.gz>] [--boot 10000]

Writes analysis/posthoc/out/clean_baseline.md, analysis/posthoc/out/clean_baseline.json and
paper/final/generated/app_clean_baseline_rows.tex.
"""
import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
import full_study as fs  # noqa: E402

DROP = "qwen3.5-0.8b"
BASE = "none"
CONDS = [c for c in fs.CONDS if c != BASE]                    # every count condition, paper order
TEX_CONDS = ["min_k_shown", "min_k_shown_fewer_ok", "min_k_enforced", "min_k_escape", "max_k_shown"]
SUBSETS = {"exact": "no-count output has exactly n substantive entries",
           "not_over": "no-count output does not over-count (at most n substantive entries)"}
KEYS = ["model_key", "doc_id", "k"]


def gpu_frame(df):
    main, _, _, _ = fs.lineup()
    f = df[(df["kind"] == "full") & (df["arm"] == "main") & df["model_key"].isin(main)].copy()
    f["model_key"] = f["model_key"].cat.remove_unused_categories()
    return f, [m for m in main if m in set(f["model_key"].unique())]


def cells(f):
    """One row per (model, document, k) on n < k, k = 3 and 5, ok outputs: the no-count output's substantive
    count and over-count, validity, and each condition's over-count share (wordings averaged)."""
    sel = f[f["ok"] & f["k"].isin((3, 5)) & (f["n"] < f["k"])]
    base = sel[sel["condition"] == BASE].groupby(KEYS, observed=True).agg(
        base_subst=("n_substantive", "mean"), base_over=("over_count", "mean"), base_valid=("valid", "mean"))
    over = sel[sel["condition"] != BASE].groupby(KEYS + ["condition"], observed=True)["over_count"].mean()
    over = over.unstack("condition")
    over = over[[c for c in CONDS if c in over.columns]]
    t = base.join(over, how="left").reset_index()
    info = sel.drop_duplicates("doc_id").set_index("doc_id")[["group", "set", "n"]]
    return t.join(info, on="doc_id")


def clean_mask(t, subset):
    if subset == "exact":
        return t["base_subst"] == t["n"]
    if subset == "not_over":
        return t["base_over"] == 0
    if subset == "all":
        return pd.Series(True, index=t.index)
    raise ValueError(subset)


def rate(boot, t, cond):
    """Over-count share (cells) under `cond` with its bootstrap interval; None when no cell has that condition."""
    sub = t.dropna(subset=[cond])
    if not len(sub):
        return None
    r = boot.mean(sub.assign(diff=sub[cond].astype(float)))
    return {"est": r["est"], "lo": r["lo"], "hi": r["hi"], "cells": r["pairs"], "groups": r["groups"]}


def summarise(boot, t, subset):
    s = t[clean_mask(t, subset)]
    out = {"model_doc_pairs": int(s[["model_key", "doc_id"]].drop_duplicates().shape[0]), "cells": int(len(s)),
           "unreadable_no_count": int((s["base_valid"] < 1).sum()), "over_count": {}}
    for c in [BASE] + CONDS:
        col = "base_over" if c == BASE else c
        if col in s:
            out["over_count"][c] = rate(boot, s, col)
    return out


def pct(r):
    if not r:
        return "--"
    return f"{100 * r['est']:.1f} [{100 * r['lo']:.1f}, {100 * r['hi']:.1f}]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scored", default=str(fs.CACHE))
    ap.add_argument("--boot", type=int, default=10000)
    ap.add_argument("--out", default=str(ROOT / "analysis" / "posthoc" / "out"))
    ap.add_argument("--tex", default=str(ROOT / "paper" / "final" / "generated" / "app_clean_baseline_rows.tex"))
    a = ap.parse_args()

    df, _ = fs.load_scored(a.scored)
    df = fs.add_doc_fields(df, fs.doc_table())
    f, models = gpu_frame(df)
    boot = fs.Bootstrap(a.boot)
    t = cells(f)

    # sanity: the paper's unrestricted shares (plain output means, outcomes table) and the same on the cells
    lt = f[f["ok"] & (f["n"] < f["k"]) & f["k"].isin((3, 5))]
    plain = {c: float(lt.loc[lt["condition"] == c, "over_count"].mean()) for c in [BASE] + CONDS}

    pools = {"8 GPU models": t, "7 GPU models, without Qwen3.5-0.8B": t[t["model_key"] != DROP]}
    res = {"boot": a.boot, "seed": fs.SEED, "subsets": SUBSETS, "plain_output_share_all": plain, "pooled": {},
           "per_model": {}}
    for label, tt in pools.items():
        res["pooled"][label] = {s: summarise(boot, tt, s) for s in ("all", "exact", "not_over")}
    for m in models:
        tm = t[t["model_key"] == m]
        res["per_model"][fs.NAME.get(m, m)] = {s: summarise(boot, tm, s) for s in ("all", "exact", "not_over")}

    # markdown
    p8 = res["pooled"]["8 GPU models"]
    lines = ["# Post hoc: over-count where the model is clean with no count", "",
             "Pairs of (GPU model, document) whose no-count output was clean; documents with n < k, k = 3 and 5; "
             "one cell per (model, document, k), prose wordings averaged. Over-count %% with 95%% intervals from "
             "%d draws over document groups within set (seed %d). Clean (a): exactly n substantive entries with "
             "no count. Clean (b): at most n. Frozen scores: an unreadable output counts as 0 entries." % (a.boot, fs.SEED),
             "", "Sanity check (no clean filter, plain output share as in the paper): no count %.1f%%, "
             "min_k_shown %.1f%%." % (100 * plain[BASE], 100 * plain["min_k_shown"]), ""]
    for label in pools:
        r = res["pooled"][label]
        lines += [f"## {label}", "",
                  "| subset | (model, document) pairs | cells | unreadable no-count outputs |", "|---|---|---|---|"]
        for s, name in (("all", "all pairs"), ("exact", "(a) exactly n"), ("not_over", "(b) at most n")):
            lines.append(f"| {name} | {r[s]['model_doc_pairs']} | {r[s]['cells']} | {r[s]['unreadable_no_count']} |")
        lines += ["", "| condition | all pairs | (a) exactly n | (b) at most n |", "|---|---|---|---|"]
        for c in [BASE] + CONDS:
            lines.append(f"| {c} | " + " | ".join(pct(r[s]["over_count"].get(c)) for s in ("all", "exact", "not_over")) + " |")
        lines.append("")
    lines += ["## Per model: over-count % under min_k_shown", "",
              "| model | all pairs | (a) exactly n | (a) pairs | (b) at most n | (b) pairs |", "|---|---|---|---|---|---|"]
    for m, r in res["per_model"].items():
        lines.append(f"| {m} | {pct(r['all']['over_count'].get('min_k_shown'))} | "
                     f"{pct(r['exact']['over_count'].get('min_k_shown'))} | {r['exact']['model_doc_pairs']} | "
                     f"{pct(r['not_over']['over_count'].get('min_k_shown'))} | {r['not_over']['model_doc_pairs']} |")
    lines += ["", "## Per model: over-count % per condition, clean (b)", "",
              "| model | " + " | ".join(TEX_CONDS) + " |", "|" + "---|" * (len(TEX_CONDS) + 1)]
    for m, r in res["per_model"].items():
        lines.append(f"| {m} | " + " | ".join(pct(r["not_over"]["over_count"].get(c)) for c in TEX_CONDS) + " |")

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "clean_baseline.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out / "clean_baseline.json").write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")

    # LaTeX rows: condition; over-count % [95% CI] for (a) and (b), 8 GPU models pooled
    tex = ["% generated by analysis/posthoc/clean_baseline.py (POST HOC); 8 GPU models pooled, n < k, k = 3 and 5"]
    for c in TEX_CONDS:
        tex.append(f"  {fs.cnd(c)} & {pct(p8['exact']['over_count'].get(c))} & "
                   f"{pct(p8['not_over']['over_count'].get(c))} \\\\")
    Path(a.tex).parent.mkdir(parents=True, exist_ok=True)
    Path(a.tex).write_text("\n".join(tex) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
