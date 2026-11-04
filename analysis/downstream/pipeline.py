#!/usr/bin/env python3
"""pipeline.py: decisions a pipeline makes from the list (addendum 1, section 3.1; exploratory).

    python analysis/downstream/pipeline.py [--scored DIR ...] [--runs RUN_ID ...] [--boot 10000]

Reads the per-output tables the frozen scorer wrote (analysis/full_study_score.py, `<run_id>.outputs.csv.gz`)
from every --scored folder (default analysis/full/scored) and writes, in analysis/downstream/pipeline/:
  RESULTS.md                 every number, with where it comes from
  per_model.csv              every scope (the 8 main models pooled, each model on its own) x set x condition
  headline.json              the pooled numbers of the 8 main models (read by analysis/tests/test_pipeline.py)
  tex/tab_pipeline.tex       the three measures per condition, 8 main models pooled (booktabs)
  tex/tab_pipeline_vs_none.tex   the same as changes against `none`

Runs used: the main study runs only, fs_<model>_full, and the closed-model runs of addendum 1,
a1_<model>_addendum1 and a1_<model>_addendum1-enforced (one model, two folders). Repeat, re-ask, thinking and
dev runs are never read. --runs keeps only the named run ids. The 8 main GPU models (configs/models.yaml,
full_study.gpu.main) are pooled; every other model is reported on its own and never pooled.

The three measures (documents with no true item have n = 0; n is the frozen answer list's count):
  1. false alarm        k = 1, n = 0: share of outputs with at least one substantive entry
  2. collection count   k = 3 and 5, n < k: total substantive entries / total true items in the cell (1.00 correct)
  3. wrong rows         k = 3 and 5, n < k: share of substantive entries that are not true items, i.e. entries the
                        matcher labels in_text_wrong_type or plausible_invented (true_item and split_of_true count
                        as true); 1 - entry precision

Selection, MISSING handling and bootstrap are those of analysis/full_study.py: only ok outputs (transport
failures and unanswered requests are left out; unreadable outputs count, with 0 entries); a level is the ratio of
sums over a condition's ok outputs in the cell; a change against `none` is taken over (model, document, k) units
that have an ok output under both conditions, a prose condition's wordings averaged first (full_study.paired);
every interval is the 95% percentile interval of full_study.Bootstrap (document groups resampled within set,
seed 20261014), the ratio of sums recomputed in every draw.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
import full_study as fs  # noqa: E402

OUT = ROOT / "analysis" / "downstream" / "pipeline"
SCORED = ROOT / "analysis" / "full" / "scored"
REGISTERED = ROOT / "analysis" / "full" / "RESULTS.md"
RUN_ID = re.compile(r"^(fs_.+_full|a1_.+_addendum1(-enforced)?)$")
NAME = {**fs.NAME, "bedrock-grok-4.3": "Grok 4.3 (Bedrock)", "azure-gpt-6-sol": "GPT-6 Sol (Azure)",
        "azure-gpt-6-luna": "GPT-6 Luna (Azure)"}
COLS = ["run_id", "model_key", "arm", "request_id", "doc_id", "group", "set", "condition", "k", "n", "wording_id",
        "status", "n_substantive", "n_true", "n_split", "n_wrong_type", "n_invented"]
MAIN_POOL = "main_pooled"

# key, label, k values, cell (full_study.cell_mask), numerator column, denominator column, display scale, digits
MEASURES = [
    ("false_alarm", "False alarm (share of empty-document outputs with an entry)", (1,), "lt_n0", "has_entry", "one", 100, 1),
    ("collection", "Collection count (substantive entries / true items)", (3, 5), "lt", "n_substantive", "n", 1, 2),
    ("wrong_rows", "Wrong rows (share of substantive entries that are not true items)", (3, 5), "lt", "n_wrong",
     "n_substantive", 100, 1),
]


# ---------------------------------------------------------------------------------------------------------
# loading
def find_runs(dirs, only=None):
    """{run_id: path of its outputs table}; the first folder holding a run id wins."""
    found = {}
    for d in dirs:
        for p in sorted(Path(d).glob("*.outputs.csv.gz")):
            rid = p.name[: -len(".outputs.csv.gz")]
            if RUN_ID.match(rid) and (not only or rid in only) and rid not in found:
                found[rid] = p
    if only:
        absent = sorted(set(only) - set(found))
        if absent:
            raise SystemExit(f"run ids not found in {', '.join(map(str, dirs))}: {', '.join(absent)}")
    return found


def load(runs):
    frames = []
    for rid, p in sorted(runs.items()):
        f = pd.read_csv(p, usecols=COLS, dtype={c: str for c in ("run_id", "model_key", "arm", "request_id", "doc_id",
                                                                 "group", "set", "condition", "wording_id", "status")},
                        keep_default_na=False, na_values=[""])
        frames.append(f[f["arm"].fillna("main") == "main"])
    df = pd.concat(frames, ignore_index=True)
    return prepare(df)


def prepare(df):
    df = df.copy()
    df["ok"] = df["status"] == "ok"
    for c in ("k", "n", "n_substantive", "n_true", "n_split", "n_wrong_type", "n_invented"):
        df[c] = pd.to_numeric(df[c], errors="coerce").astype(float)
    ok = df[df["ok"]]
    labelled = ok["n_true"] + ok["n_split"] + ok["n_wrong_type"] + ok["n_invented"]
    bad = int((labelled != ok["n_substantive"]).sum())
    if bad:
        raise SystemExit(f"{bad} ok outputs whose matcher labels do not add up to their substantive entries")
    df["has_entry"] = (df["n_substantive"] >= 1).astype(float)      # as full_study.add_doc_fields
    df["one"] = 1.0
    df["n_wrong"] = df["n_wrong_type"] + df["n_invented"]
    return df


# ---------------------------------------------------------------------------------------------------------
# estimates
def _cell(f, ks, cell, conds):
    sel = f[f["ok"] & f["condition"].isin(conds) & f["k"].isin(ks)]
    return sel[fs.cell_mask(sel, cell, "n")]


def _boot(B, g, cols, fn):
    if not len(g):
        return None
    per = {str(k): tuple(float(r[c]) for c in cols) for k, r in g.sort_index().iterrows()}
    strata = {str(k): v for k, v in g["set"].items()}
    with np.errstate(divide="ignore", invalid="ignore"):
        return B.stat(per, strata, fn)


def level(f, B, cond, ks, cell, num, den):
    """Ratio of sums over the condition's ok outputs in the cell."""
    sel = _cell(f, ks, cell, [cond])
    if not len(sel) or sel[den].sum() == 0:
        return None
    g = sel.groupby("group", sort=True).agg(a=(num, "sum"), b=(den, "sum"), set=("set", "first"))
    r = _boot(B, g, ["a", "b"], lambda v: v[..., 0] / v[..., 1])
    if r:
        r.update(outputs=int(len(sel)), num=float(sel[num].sum()), den=float(sel[den].sum()))
    return r


def pair_units(f, a, b, ks, cell, num, den):
    """(model, document, k) units with an ok output under both a and b; a condition's wordings averaged first
    (the units and the averaging of full_study.paired)."""
    sel = _cell(f, ks, cell, [a, b])
    if not len(sel):
        return None
    g = sel.groupby(["model_key", "doc_id", "k", "condition"])[[num, den]].mean().unstack("condition")
    if (num, a) not in g or (num, b) not in g:
        return None
    g = g.dropna(subset=[(num, a), (num, b)])
    out = pd.DataFrame({"na": g[(num, a)], "da": g[(den, a)], "nb": g[(num, b)], "db": g[(den, b)]}).reset_index()
    info = sel.drop_duplicates("doc_id").set_index("doc_id")[["group", "set"]]
    return out.join(info, on="doc_id")


def change(f, B, a, b, ks, cell, num, den):
    """ratio(a) - ratio(b) over the paired units, both ratios recomputed in every draw."""
    u = pair_units(f, a, b, ks, cell, num, den)
    if u is None or not len(u) or u["da"].sum() == 0 or u["db"].sum() == 0:
        return None
    g = u.groupby("group", sort=True).agg(na=("na", "sum"), da=("da", "sum"), nb=("nb", "sum"), db=("db", "sum"),
                                         set=("set", "first"))
    r = _boot(B, g, ["na", "da", "nb", "db"], lambda v: v[..., 0] / v[..., 1] - v[..., 2] / v[..., 3])
    if r:
        r["pairs"] = int(len(u))
    return r


def estimates(f, B, scope, model_name, pool, sets):
    """One row per set scope x measure x condition."""
    rows = []
    conds = [c for c in fs.CONDS if c in set(f["condition"].unique())]
    for s in ["all", *sets]:
        fs_ = f if s == "all" else f[f["set"] == s]
        if not len(fs_):
            continue
        for key, _, ks, cell, num, den, scale, _ in MEASURES:
            for c in conds:
                lv = level(fs_, B, c, ks, cell, num, den)
                ch = None if c == "none" else change(fs_, B, c, "none", ks, cell, num, den)
                if lv is None and ch is None:
                    continue
                rows.append({"scope": scope, "model": model_name, "pool": pool, "set": s, "measure": key,
                             "condition": c, "scale": scale,
                             "level": lv["est"] if lv else None, "level_lo": lv["lo"] if lv else None,
                             "level_hi": lv["hi"] if lv else None, "outputs": lv["outputs"] if lv else 0,
                             "numerator": lv["num"] if lv else None, "denominator": lv["den"] if lv else None,
                             "groups": lv["groups"] if lv else 0,
                             "change_vs_none": ch["est"] if ch else None, "change_lo": ch["lo"] if ch else None,
                             "change_hi": ch["hi"] if ch else None, "change_p": ch["p"] if ch else None,
                             "pairs": ch["pairs"] if ch else 0})
    return rows


# ---------------------------------------------------------------------------------------------------------
# formatting
def _f(x, scale, nd, sign=False):
    return f"{scale * x:{'+' if sign else ''}.{nd}f}"


def cell_text(r, kind, scale, nd):
    """'est [lo, hi]' for kind 'level' or 'change', '--' if absent."""
    if r is None:
        return "--"
    est, lo, hi = (r["level"], r["level_lo"], r["level_hi"]) if kind == "level" else \
        (r["change_vs_none"], r["change_lo"], r["change_hi"])
    if est is None or pd.isna(est):
        return "--"
    sg = kind == "change"
    return f"{_f(est, scale, nd, sg)} [{_f(lo, scale, nd, sg)}, {_f(hi, scale, nd, sg)}]"


def tex_text(r, kind, scale, nd):
    s = cell_text(r, kind, scale, nd)
    if s == "--":
        return s
    return re.sub(r"([+-]?[\d.]+) \[([+-]?[\d.]+), ([+-]?[\d.]+)\]", r"$\1$ [$\2$, $\3$]", s).replace("$-", "$-")


def pick(rows, scope, s, measure, cond):
    for r in rows:
        if r["scope"] == scope and r["set"] == s and r["measure"] == measure and r["condition"] == cond:
            return r
    return None


def registered_empty_doc():
    """From analysis/full/RESULTS.md: the shares with at least one substantive entry on the empty documents at
    k = 1 (%, one decimal) and the empty-document tests against none (points, one decimal, with interval)."""
    text = REGISTERED.read_text(encoding="utf-8")
    m = re.search(r"Shares with at least one substantive entry on the \d+ empty documents at k = 1: (.*)", text)
    shares = {c: float(v) for c, v in re.findall(r"(\w+) ([\d.]+)%", m.group(1))} if m else {}
    tests = {c: tuple(float(x) for x in (e, lo, hi)) for c, e, lo, hi in re.findall(
        r"empty document, k = 1 \(n = 0\): (\w+) vs none, share with at least one entry \(points\) \| "
        r"([+-][\d.]+) \[([+-][\d.]+), ([+-][\d.]+)\]", text)}
    return shares, tests


def cross_check(rows):
    """Measure 1, 8 main models pooled, against the registered empty-document numbers. Returns (lines, ok)."""
    shares, tests = registered_empty_doc()
    lines, ok = [], True
    for c, v in shares.items():
        r = pick(rows, MAIN_POOL, "all", "false_alarm", c)
        mine = None if r is None else round(100 * r["level"], 1)
        same = mine == v
        ok &= same
        lines.append(f"| {c} | level | {v:.1f} | {'--' if mine is None else f'{mine:.1f}'} | {'yes' if same else 'NO'} |")
    for c, (e, lo, hi) in tests.items():
        r = pick(rows, MAIN_POOL, "all", "false_alarm", c)
        mine = None if r is None else tuple(round(100 * r[x], 1) for x in ("change_vs_none", "change_lo", "change_hi"))
        same = mine == (e, lo, hi)
        ok &= same
        lines.append(f"| {c} | vs none | {e:+.1f} [{lo:+.1f}, {hi:+.1f}] | "
                     f"{'--' if mine is None else '{:+.1f} [{:+.1f}, {:+.1f}]'.format(*mine)} | {'yes' if same else 'NO'} |")
    return lines, ok and bool(shares) and bool(tests)


# ---------------------------------------------------------------------------------------------------------
def write(rows, runs, main_present, others, boot, sets):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tex").mkdir(exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / "per_model.csv", index=False, float_format="%.6g")
    md = ["# Decisions a pipeline makes from the list (addendum 1, section 3.1; exploratory)", "",
          "Written by `python analysis/downstream/pipeline.py` from the frozen scorer's per-output tables "
          "(`<run_id>.outputs.csv.gz`, analysis/full_study_score.py). Every number below and every per-set and "
          "per-model number is also in `per_model.csv` (one row per scope, set, measure and condition; `scale` is "
          "the factor applied for display). "
          f"Intervals: 95% percentile intervals from {boot} bootstrap draws over document groups resampled within "
          f"set, seed {fs.SEED} (analysis/full_study.py's Bootstrap), the ratio of sums recomputed in every draw.", "",
          "Measures (n = the frozen answer list's count of true items):", "",
          "1. **False alarm**: documents with no true item, k = 1: share of outputs with at least one substantive "
          "entry (%). Change against `none` in points.",
          "2. **Collection count**: documents with n < k, k = 3 and 5: total substantive entries / total true items "
          "in the cell (1.00 is correct). Change against `none` in the same units.",
          "3. **Wrong rows**: documents with n < k, k = 3 and 5: share of substantive entries the matcher labels "
          "`in_text_wrong_type` or `plausible_invented` (`true_item` and `split_of_true` count as true), i.e. "
          "1 - entry precision (%). Change against `none` in points.", "",
          "A level is a ratio of sums over all ok outputs of the condition in the cell (MISSING outputs left out, "
          "unreadable outputs counted with 0 entries). A change against `none` uses the (model, document, k) units "
          "with an ok output under both conditions, a prose condition's wordings averaged first, as in the "
          "registered paired tests.", "",
          f"Main models pooled ({len(main_present)}): " + ", ".join(NAME.get(m, m) for m in main_present) + ". "
          "Other models, each on its own, never pooled: " + (", ".join(NAME.get(m, m) for m in others) or "none") + ".",
          "", "Run tables read: " + ", ".join(f"`{r}`" for r in sorted(runs)) + ".", "",
          "Adding the closed-model runs of addendum 1: score them with the frozen scorer "
          "(`python analysis/full_study_score.py --runs-dir <folder with the a1_* runs> --cache <folder>`), then "
          "rerun this script with that folder added to `--scored`; models found are reported on their own."]
    # cross-check
    if len(main_present) == 8 and boot == 10000:
        lines, ok = cross_check(rows)
        md += ["", "## Cross-check against the registered empty-document test", "",
               "Measure 1 for the 8 main models pooled is the registered empty-document test of "
               "`analysis/full/RESULTS.md` section 4 (share with at least one substantive entry, and its change "
               "against `none`). Rounded as there:", "",
               "| condition | number | registered | here | same |", "|---|---|---|---|---|", *lines, "",
               f"All equal: {'yes' if ok else 'NO'}."]
        if not ok:
            print("WARNING: measure 1 differs from the registered empty-document test", file=sys.stderr)
    # section 1: main pooled, all sets
    head = ["condition"]
    for key, label, *_ in MEASURES:
        head += [f"{key}: level", f"{key}: vs none"]
    def scope_table(scope):
        out = []
        for c in fs.CONDS:
            cells, any_ = [c], False
            for key, _, _, _, _, _, scale, nd in MEASURES:
                r = pick(rows, scope, "all", key, c)
                any_ |= r is not None
                cells += [cell_text(r, "level", scale, nd), cell_text(r, "change", scale, nd) if c != "none" else ""]
            if any_:
                out.append(cells)
        return out
    md += ["", "## 1. The 8 main models pooled, all sets", "",
           "False alarm and wrong rows in % (changes in points); collection count as a ratio.", "",
           *fs.md_table(head, scope_table(MAIN_POOL))]
    cnt = [[c] + [str(int(pick(rows, MAIN_POOL, "all", key, c)["outputs"])) if pick(rows, MAIN_POOL, "all", key, c) else "--"
                  for key, *_ in MEASURES] +
           [f"{pick(rows, MAIN_POOL, 'all', 'collection', c)['numerator']:.0f} / "
            f"{pick(rows, MAIN_POOL, 'all', 'collection', c)['denominator']:.0f}"
            if pick(rows, MAIN_POOL, "all", "collection", c) else "--"]
           for c in fs.CONDS if pick(rows, MAIN_POOL, "all", "false_alarm", c) or pick(rows, MAIN_POOL, "all", "collection", c)]
    md += ["", "Outputs behind each level (prose conditions: all wordings) and the collection count's sums:", "",
           *fs.md_table(["condition", "false alarm outputs", "collection outputs", "wrong rows outputs",
                         "collection: entries / true items"], cnt)]
    # section 2: main pooled per set
    md += ["", "## 2. The 8 main models pooled, per set"]
    for key, label, _, _, _, _, scale, nd in MEASURES:
        conds = [c for c in fs.CONDS if pick(rows, MAIN_POOL, "all", key, c)]
        lv = [[fs.SET_NAME[s], *[cell_text(pick(rows, MAIN_POOL, s, key, c), "level", scale, nd) for c in conds]]
              for s in sets]
        ch = [[fs.SET_NAME[s], *[cell_text(pick(rows, MAIN_POOL, s, key, c), "change", scale, nd) for c in conds[1:]]]
              for s in sets]
        md += ["", f"### {label}: level", "", *fs.md_table(["set", *conds], lv),
               "", f"### {label}: change against none", "", *fs.md_table(["set", *conds[1:]], ch)]
    # section 3: each main model, section 4: each other model
    for title, models in (("3. Each main model on its own, all sets", main_present),
                          ("4. Every other model on its own (never pooled), all sets", others)):
        md += ["", f"## {title}"]
        if not models:
            md += ["", "None in the tables read."]
        for m in models:
            md += ["", f"### {NAME.get(m, m)}", "", *fs.md_table(head, scope_table(m))]
    md += ["", "## Notes", "",
           "- Wrong rows is computed on the n < k cells at k = 3 and 5 (the cells of measure 2). On the empty "
           "documents every substantive entry is a wrong row by definition, so measure 1 already covers them.",
           "- The matcher v0 does not give the labels `missed_gold` and `beyond_excerpt` (analysis/full/REPORT.md, "
           "note 2); such entries carry `in_text_wrong_type` or `plausible_invented` and count as wrong rows. The "
           "labels are the matcher's, frozen with the scorer; the frozen answer lists are used (no overlay).",
           "- The closed models of addendum 1 ran wording 1 of each prose condition only (addendum 1, section 1), "
           "so their prose rows are one wording, where the other models average five.",
           "- Per-set and per-model numbers for every scope are in `per_model.csv`."]
    (OUT / "RESULTS.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    # tex
    tl, tc = [], []
    for c in fs.CONDS:
        rs = [pick(rows, MAIN_POOL, "all", key, c) for key, *_ in MEASURES]
        if not any(rs):
            continue
        tl.append([fs.cnd(c), *[tex_text(r, "level", sc, nd) for r, (_, _, _, _, _, _, sc, nd) in zip(rs, MEASURES)]])
        if c != "none":
            tc.append([fs.cnd(c), *[tex_text(r, "change", sc, nd) for r, (_, _, _, _, _, _, sc, nd) in zip(rs, MEASURES)]])
    (OUT / "tex" / "tab_pipeline.tex").write_text(fs.tex_table(
        "lrrr", ["Condition", "False alarm \\%", "Collection count", "Wrong rows \\%"], tl), encoding="ascii")
    (OUT / "tex" / "tab_pipeline_vs_none.tex").write_text(fs.tex_table(
        "lrrr", ["Condition", "False alarm (pts)", "Collection count", "Wrong rows (pts)"], tc), encoding="ascii")
    head_json = {key: {c: {k: pick(rows, MAIN_POOL, "all", key, c).get(k) for k in
                           ("level", "level_lo", "level_hi", "change_vs_none", "change_lo", "change_hi", "outputs", "pairs")}
                       for c in fs.CONDS if pick(rows, MAIN_POOL, "all", key, c)}
                 for key, *_ in MEASURES}
    head_json["_meta"] = {"boot": boot, "seed": fs.SEED, "main_models": main_present, "other_models": others,
                          "runs": sorted(runs)}
    (OUT / "headline.json").write_text(json.dumps(head_json, indent=1), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scored", nargs="+", default=[str(SCORED)], help="folders of <run_id>.outputs.csv.gz tables")
    ap.add_argument("--runs", nargs="*", help="keep only these run ids")
    ap.add_argument("--boot", type=int, default=10000)
    args = ap.parse_args()
    runs = find_runs(args.scored, args.runs)
    if not runs:
        raise SystemExit("no fs_*_full or a1_*_addendum1 tables found")
    df = load(runs)
    main_models, hosted, _, _ = fs.lineup()
    present = set(df["model_key"].unique())
    main_present = [m for m in main_models if m in present]
    others = [m for m in hosted if m in present] + sorted(present - set(main_models) - set(hosted))
    sets = [s for s in fs.SETS if s in set(df["set"].unique())]
    B = fs.Bootstrap(args.boot)
    rows = []
    if main_present:
        rows += estimates(df[df["model_key"].isin(main_present)], B, MAIN_POOL, "8 main models pooled", "main", sets)
    for m in main_present + others:
        rows += estimates(df[df["model_key"] == m], B, m, NAME.get(m, m), "main" if m in main_present else "own", sets)
        print(f"{m}: done", flush=True)
    write(rows, runs, main_present, others, args.boot, sets)
    print(f"wrote {OUT}/RESULTS.md, per_model.csv, headline.json, tex/")


if __name__ == "__main__":
    main()
