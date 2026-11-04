#!/usr/bin/env python3
"""closed_models.py: the closed models of OSF addendum 1, section 1 (preregistration/addendum-1.md), and the
fewer-is-fine re-ask of section 2. Exploratory; each model on its own, never pooled with the GPU results.

    python analysis/full_study_score.py --runs-dir runs --cache analysis/addendum1/scored --only <a1_* runs>
    python analysis/closed_models.py [--boot 10000]

Inputs: the scored tables of the a1_* runs (analysis/addendum1/scored) and, for the comparison row and the
re-ask, the full-study scored tables (analysis/full/scored). Every measure is the registered one, computed with
the helpers of analysis/full_study.py (same pairs, same cells, same group bootstrap). The closed models ran
wording 1 of each prose condition only, so their contrast 4 is on wording 1; the comparison row restricts the 8
main models to the same wording.

Writes analysis/addendum1/RESULTS.md and analysis/addendum1/tex/*.tex.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "harness"))
import full_study as fs  # noqa: E402

ROOT = fs.ROOT
OUT = ROOT / "analysis" / "addendum1"
CACHE = OUT / "scored"
CLOSED = {"bedrock-grok-4.3": "Grok 4.3", "azure-gpt-6-sol": "GPT-6 Sol", "azure-gpt-6-luna": "GPT-6 Luna"}
REASK = ["bedrock-kimi-k3", "bedrock-ministral-3-14b"]


def run_role(rid):
    if rid.startswith("a1_") and rid.endswith("-repeat"):
        return "repeat"
    if rid.startswith("a1_"):
        return "full"          # the main run and its -enforced companion are one model's study
    if rid.endswith("_full-reask1-fewer-ok"):
        return "reask_fewer_ok"
    return None


def load(cache):
    df, meta = fs.load_scored(cache)
    df["kind"] = df["run_id"].astype(str).map(run_role).astype("category")
    return df, meta


def restrict_wording1(f):
    prose = f["condition"].astype(str).str.startswith("prose_")
    return f[~prose | f["wording_id"].astype(str).str.endswith("_1")]


def summary_rows(B, frames):
    """frames: [(label, frame)]; one row of registered measures per frame."""
    rows, trows = [], []
    for label, f in frames:
        c = {cid: B.mean(fs.contrast_pairs(f, cid)) for cid in ("C1", "C2", "C3", "C4")}
        c5 = B.mean(fs.contrast_pairs(f, "C5")) if (f["condition"] == "min_k_escape").any() else None
        fewer = B.mean(fs.paired(f, "min_k_shown_fewer_ok", "none"))
        over = {cond: B.mean(fs.paired(f, cond, "none", outcome="over_count")) for cond in ("min_k_shown",)}
        ok = f[f["ok"]]
        unread = 100 * (1 - ok["valid"].mean()) if len(ok) else float("nan")
        rows.append([label, *[fs.fmt(c[x]) for x in ("C1", "C2", "C3", "C4")], fs.fmt(c5) if c5 else "--",
                     fs.fmt(fewer), fs.pts(over["min_k_shown"]) if over["min_k_shown"] else "--",
                     f"{unread:.1f}", int((~f["ok"]).sum())])
        wrong, inv, _ = kinds_of_extra(f)
        trows.append([fs.tex_escape(label), fs.tex_ci(c["C2"]),
                      fs.tex_ci(over["min_k_shown"], 100, 1) if over["min_k_shown"] else "--",
                      fs.tex_ci(fewer), f"{wrong:.1f}", f"{inv:.1f}"])
    return rows, trows


def by_condition(f, cond_list):
    """Over-count (n < k, k = 3 and 5) and the empty-document rate (n = 0, k = 1) per condition, ok outputs."""
    ok = f[f["ok"]]
    lt = ok[ok["k"].isin((3, 5)) & (ok["n"] < ok["k"])]
    e = ok[(ok["k"] == 1) & (ok["n"] == 0)]
    out = []
    for c in cond_list:
        a, b = lt[lt["condition"] == c], e[e["condition"] == c]
        out.append((c, 100 * a["over_count"].mean() if len(a) else np.nan, len(a),
                    100 * b["has_entry"].mean() if len(b) else np.nan, len(b)))
    return out


def sorting(f):
    ok = f[f["ok"] & f["k"].isin((3, 5)) & (f["n"] < f["k"]) & (f["condition"] == "min_k_shown")]
    return {s: 100 * (ok["sort"] == s).mean() for s in fs.SORTS} if len(ok) else {}


def kinds_of_extra(f):
    """What the extra entries are under min_k_shown (n < k, k = 3 and 5), as analysis/full_study.py section 6b
    computes it: extra = split + wrong kind + invented, readable ok outputs; shares of the extra entries."""
    ok = f[f["ok"] & f["valid"].astype(bool) & f["k"].isin((3, 5)) & (f["n"] < f["k"]) & (f["condition"] == "min_k_shown")]
    extra = float((ok["n_split"] + ok["n_wrong_type"] + ok["n_invented"]).sum())
    if not extra:
        return np.nan, np.nan, 0
    inv = float((ok["n_invented"] - ok["n_invented_note"]).sum())
    return 100 * float(ok["n_wrong_type"].sum()) / extra, 100 * inv / extra, int(extra)


def content_filtered(run_dirs):
    n = 0
    for d in run_dirs:
        for name in ("raw.jsonl", "raw_restricted.jsonl"):
            p = Path(d) / name
            if p.exists():
                for line in open(p, encoding="utf-8"):
                    r = json.loads(line)
                    if r["status"] == "http_400" and "content_filter" in json.dumps(r.get("error_body") or {}):
                        n += 1
    return n


def repeat_rows(df, full):
    rows = []
    for m in CLOSED:
        rep = df[(df["kind"] == "repeat") & (df["model_key"] == m) & df["ok"]]
        base = full[(full["model_key"] == m) & full["ok"]]
        j = rep.merge(base, on="request_id", suffixes=("_r", "_b"))
        if not len(j):
            continue
        rows.append([CLOSED[m], len(j), f"{100 * (j['content_sha1_r'] == j['content_sha1_b']).mean():.1f}",
                     f"{100 * (j['over_count_r'] != j['over_count_b']).mean():.2f}"])
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--boot", type=int, default=10000)
    ap.add_argument("--main-cache", default=str(fs.CACHE))
    args = ap.parse_args()
    B = fs.Bootstrap(args.boot)
    docs = fs.doc_table()

    df, meta = load(CACHE)
    df = fs.add_doc_fields(df, docs)
    full = df[df["kind"] == "full"]

    main_df, _ = fs.load_scored(args.main_cache)
    main_df = fs.add_doc_fields(main_df, docs)
    main_lineup = fs.lineup()[0]
    gpu = main_df[(main_df["kind"] == "full") & (main_df["arm"] == "main") & main_df["model_key"].isin(main_lineup)]
    gpu_w1 = restrict_wording1(gpu)

    md = ["# Closed models (OSF addendum 1, exploratory)", "",
          "Registered at https://osf.io/45mfb before any request was sent. Each model on its own; never pooled.",
          "Length change in substantive entries (documents with n < k, k = 3 and 5) with 95% group-bootstrap",
          f"intervals ({args.boot} draws, seed {fs.SEED}). C1 dose, C2 min_k_shown vs none (main measure), C3 vs",
          "max_k_shown, C4 exactly vs up to (wording 1), C5 escape vs enforced (only where the API enforces",
          "minItems). The last row is the 8 main GPU models pooled on the same cells and wording, for reference.", ""]

    frames = [(CLOSED[m], full[full["model_key"] == m]) for m in CLOSED if (full["model_key"] == m).any()]
    frames.append(("8 GPU models (pooled, wording 1)", gpu_w1))
    rows, trows = summary_rows(B, frames)
    md += fs.md_table(["model", "C1", "C2", "C3", "C4", "C5", "fewer_ok vs none", "C2 over-count (points)",
                       "unreadable %", "missing"], rows)
    OUT.joinpath("tex").mkdir(parents=True, exist_ok=True)
    (OUT / "tex" / "tab_closed.tex").write_text(fs.tex_table(
        "lrrrrr", ["Model", "C2 (entries)", "C2 over-count (pts)", "Fewer-ok vs none", "Extra: text (\\%)",
                   "Extra: invented (\\%)"], trows), encoding="utf-8")

    cond_tex = {}
    for label, f in frames:
        cond_tex[label] = {c: (a, b) for c, a, _, b, _ in by_condition(f, fs.CONDS)}
    trows_c = []
    for c in fs.CONDS:
        cells = []
        for label, _ in frames:
            a, b = cond_tex[label].get(c, (np.nan, np.nan))
            cells += ["--" if np.isnan(a) else f"{a:.1f}", "--" if np.isnan(b) else f"{b:.1f}"]
        trows_c.append([fs.cnd(c), *cells])
    head_c = ["Condition"] + [x for label, _ in frames for x in (f"{fs.tex_escape(label.split(' (')[0])}: over", "empty")]
    (OUT / "tex" / "tab_closed_cond.tex").write_text(fs.tex_table("l" + "rr" * len(frames), head_c, trows_c), encoding="utf-8")

    md += ["", "## Per condition: over-count (n < k, k = 3 and 5) and empty documents (n = 0, k = 1)", ""]
    for label, f in frames:
        conds = [c for c in fs.CONDS if c in set(f["condition"].astype(str))]
        md += [f"### {label}", ""]
        md += fs.md_table(["condition", "over-count %", "outputs", "empty docs with an entry %", "outputs"],
                          [[c, f"{a:.1f}", na, f"{b:.1f}", nb] for c, a, na, b, nb in by_condition(f, conds)])
        md.append("")

    md += ["## Sorting of min_k_shown outputs (n < k, k = 3 and 5), and what fills the extra slots", ""]
    srows = []
    for label, f in frames:
        s = sorting(f)
        w, i, tot = kinds_of_extra(f)
        srows.append([label, *[f"{s.get(x, float('nan')):.1f}" for x in fs.SORTS], f"{w:.1f}", f"{i:.1f}", tot])
    md += fs.md_table(["model", *fs.SORTS, "extra: real text, wrong kind %", "extra: invented %", "extra entries"], srows)

    md += ["", "## Requests refused by a provider's content filter (a result, not an output)", ""]
    md += fs.md_table(["model", "refused"],
                      [[CLOSED[m], content_filtered(sorted(ROOT.glob(f"runs/a1_{m}_addendum1*")))] for m in CLOSED])

    rr = repeat_rows(df, full)
    if rr:
        (OUT / "tex" / "tab_closed_repeat.tex").write_text(fs.tex_table(
            "lrrr", ["Model", "Pairs", "Identical \\%", "Over-count flips \\%"], rr), encoding="utf-8")
        md += ["", "## Repeat check (300 prompts sent twice)", ""]
        md += fs.md_table(["model", "pairs", "identical %", "over-count flips %"], rr)

    # section 2: the re-ask with and without the fewer-is-fine line, same replies sent back
    reask_new = df[df["kind"] == "reask_fewer_ok"]
    if len(reask_new):
        reask_old = main_df[(main_df["kind"] == "reask") & main_df["model_key"].isin(REASK)]
        md += ["", "## Re-ask with \"fewer is fine\" (addendum section 2)", "",
               "Over-count among the re-asked outputs: the registered re-ask against the same replies sent back with "
               "the fewer-is-fine line added. Only request ids answered in both runs.", ""]
        rows = []
        base_full = main_df[(main_df["kind"] == "full") & (main_df["arm"] == "main") & main_df["ok"]]
        for m in REASK:
            a = reask_old[(reask_old["model_key"] == m) & reask_old["ok"]]
            b = reask_new[(reask_new["model_key"] == m) & reask_new["ok"]]
            base = base_full[base_full["model_key"] == m]
            j = (a.merge(b, on="source_request_id", suffixes=("_old", "_new"))
                  .merge(base, left_on="source_request_id", right_on="request_id"))
            lt = j[j["n"] < j["k"]]
            if not len(lt):
                continue
            rows.append([fs.NAME.get(m, m), len(lt), f"{100 * lt['over_count'].mean():.1f}",
                         f"{100 * lt['over_count_old'].mean():.1f}", f"{100 * lt['over_count_new'].mean():.1f}",
                         f"{(lt['n_substantive_new'] - lt['n_substantive_old']).mean():+.2f}",
                         " / ".join(f"{100 * lt['sort_new'].astype(str).eq(x).mean():.0f}" for x in fs.SORTS)])
        (OUT / "tex" / "tab_reask_fewer.tex").write_text(fs.tex_table(
            "lrrrrrl", ["Model", "Re-asked, $n < k$", "Before \\%", "Re-ask \\%", "+ fewer is fine \\%",
                        "Entries, difference", "Sorting after"], [[fs.tex_escape(r[0]), *r[1:]] for r in rows]),
            encoding="utf-8")
        md += fs.md_table(["model", "re-asked with n < k (answered in both)", "over-count before %",
                           "after the registered re-ask %", "after the re-ask + fewer is fine %",
                           "entries, fewer-is-fine minus registered", "sorting after fewer-is-fine (" + " / ".join(fs.SORTS) + ")"], rows)

    (OUT / "RESULTS.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
