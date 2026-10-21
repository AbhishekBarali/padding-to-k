#!/usr/bin/env python3
"""POST HOC analyses 1, 2, 3 and 5 (not in the registered plan), and the assembled POSTHOC.md.

    python analysis/posthoc/build_entries.py --runs-dir <runs>    # once: entry text + grounding flags
    python analysis/posthoc/lenient_08b.py --runs-dir <runs>      # analysis 4
    python analysis/posthoc/posthoc.py [--boot 10000]             # analyses 1, 2, 3, 5 and POSTHOC.md

Scope, as the paper's pooled analyses (analysis/full_study.py): the fs_<model>_full runs, arm main, ok outputs;
"GPU" = the 8 main GPU models pooled, "hosted" = the 9 hosted models pooled (reference only). The `none`
answer is reused at k = 1, 3 and 5 (one request answers all three); exactly as full_study counts it, a `none`
entry counts once per k it answers, so filters on k and n < k treat it like every other condition.
Labels are matcher v0 (preliminary, as everywhere in the paper). Extra entry = substantive entry the matcher
does not match to a distinct true item: labels split_of_true, in_text_wrong_type, plausible_invented.
"""
import argparse
import csv
import hashlib
import json
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common_posthoc as cp  # noqa: E402
from common_posthoc import common, full_study as fs  # noqa: E402

KS = (3, 5)
COND_ORDER = fs.CONDS
SEED = fs.SEED
HUMAN = cp.ROOT / "analysis" / "human"


# ---------------------------------------------------------------------------------------------------------
def load_entries():
    runs, main, hosted = cp.main_runs()
    parts = []
    for r in runs:
        d = pd.read_pickle(cp.CACHE / f"{r}.entries.pkl")
        d["group_kind"] = "gpu" if d["model_key"].iloc[0] in main else "hosted"
        parts.append(d)
    e = pd.concat(parts, ignore_index=True)
    return e, main, hosted


def expand_none(e):
    """A `none` entry (planned at k = 1) also answers k = 3 and 5: one copy per k, as the outputs table has."""
    nn = e[e["condition"] == "none"]
    extra = [nn.assign(k=k) for k in KS]
    return pd.concat([e] + extra, ignore_index=True)


def load_outputs():
    runs, main, hosted = cp.main_runs()
    tmp = Path(tempfile.mkdtemp())
    for r in runs:
        for suf in (".outputs.csv.gz", ".source.json"):
            (tmp / f"{r}{suf}").symlink_to((cp.SCORED / f"{r}{suf}").resolve())
    df, _ = fs.load_scored(tmp)
    df = fs.add_doc_fields(df, fs.doc_table())
    df = df[(df["kind"] == "full") & (df["arm"] == "main") & df["ok"]].copy()
    df["group_kind"] = np.where(df["model_key"].isin(main), "gpu", "hosted")
    for c in ("n_true", "n_split", "n_wrong_type", "n_invented", "n_substantive", "matched_gold"):
        df[c] = df[c].fillna(0)
    df["n_extra"] = df["n_split"] + df["n_wrong_type"] + df["n_invented"]
    return df, main, hosted


def pct(a, b):
    return round(100.0 * a / b, 1) if b else None


# ---------------------------------------------------------------------------------------------------------
# checks that can fail
def checks(e, x, out, main):
    res = {}
    frame = json.loads((HUMAN / "matcher_frame.json").read_text())["frame_entries"]
    sub = e[e["label"].isin(cp.SUBST)]
    mine = {"true_or_split": int(sub["label"].isin(["true_item", "split_of_true"]).sum()),
            "in_text_wrong_type": int((sub["label"] == "in_text_wrong_type").sum()),
            "plausible_invented": int((sub["label"] == "plausible_invented").sum())}
    res["frame_counts"] = {"this_table": mine, "matcher_frame_json": {k: frame[k] for k in mine},
                           "equal": all(mine[k] == frame[k] for k in mine)}
    g = x[(x["group_kind"] == "gpu") & x["k"].isin(KS) & (x["n"] < x["k"]) & x["label"].isin(cp.EXTRA)]
    o = out[(out["group_kind"] == "gpu") & out["k"].isin(KS) & (out["n"] < out["k"]) & (out["valid"] == 1)]
    eq = {}
    for c in COND_ORDER:
        a = int((g["condition"] == c).sum())
        b = int(o.loc[o["condition"] == c, "n_extra"].sum())
        eq[c] = {"entries_table": a, "outputs_table": b, "equal": a == b}
    res["gpu_extras_n_lt_k_vs_outputs"] = eq
    for k, v in res.items():
        print("CHECK", k, json.dumps(v))
    return res


# ---------------------------------------------------------------------------------------------------------
# 1. source check
def rate_rows(d, by):
    rows = []
    for key, s in ([("all", d)] if by is None else d.groupby(by, observed=True, sort=False)):
        nn = len(s)
        rows.append({"key": key if by is None else (key if not isinstance(key, tuple) else "|".join(map(str, key))),
                     "entries": nn, "empty": int(s["empty"].sum()),
                     "exact_pass_pct": pct(int(s["exact"].sum()), nn),
                     "fuzzy90_pass_pct": pct(int(s["fuzzy"].astype(bool).sum()), nn),
                     "repo_core_pass_pct": pct(int(s["repo_core"].sum()), nn)})
    return rows


def source_check(x):
    res = {}
    scopes = {
        "gpu_n_lt_k_k35": x[(x["group_kind"] == "gpu") & x["k"].isin(KS) & (x["n"] < x["k"])],
        "gpu_all_docs_k35": x[(x["group_kind"] == "gpu") & x["k"].isin(KS)],
        "hosted_n_lt_k_k35": x[(x["group_kind"] == "hosted") & x["k"].isin(KS) & (x["n"] < x["k"])],
    }
    for sname, d in scopes.items():
        ex = d[d["label"].isin(cp.EXTRA)]
        tr = d[d["label"] == "true_item"]
        r = {"extra_pooled": rate_rows(ex, None)[0], "true_item_pooled": rate_rows(tr, None)[0],
             "extra_by_label": {row["key"]: row for row in rate_rows(ex, "label")},
             "extra_by_condition": {row["key"]: row for row in rate_rows(ex, "condition")},
             "invented_by_condition": {row["key"]: row for row in rate_rows(ex[ex["label"] == "plausible_invented"], "condition")},
             "true_by_condition": {row["key"]: row for row in rate_rows(tr, "condition")},
             "extra_by_set": {row["key"]: row for row in rate_rows(ex, "set")},
             "invented_by_set": {row["key"]: row for row in rate_rows(ex[ex["label"] == "plausible_invented"], "set")},
             "true_by_set": {row["key"]: row for row in rate_rows(tr, "set")}}
        # the copied-quote sets only (meetings ask for a one-sentence summary, wiki_people for names)
        q = ~d["set"].isin(["meetings", "wiki_people"])
        r["quote_sets_extra"] = rate_rows(ex[q.loc[ex.index]], None)[0]
        r["quote_sets_invented"] = rate_rows(ex[q.loc[ex.index] & (ex["label"] == "plausible_invented")], None)[0]
        r["quote_sets_true"] = rate_rows(tr[q.loc[tr.index]], None)[0]
        res[sname] = r
    rows = []
    for sname, r in res.items():
        for part in ("extra_by_condition", "invented_by_condition", "true_by_condition", "extra_by_label",
                     "extra_by_set", "invented_by_set", "true_by_set"):
            for k, v in r[part].items():
                rows.append({"scope": sname, "part": part, **v})
        for part in ("extra_pooled", "true_item_pooled", "quote_sets_extra", "quote_sets_invented", "quote_sets_true"):
            rows.append({"scope": sname, "part": part, **r[part]})
    pd.DataFrame(rows).to_csv(cp.OUT / "source_check.csv", index=False)
    return res


def source_check_human(e):
    """The grounding check on the 400 entries the authors labelled, by the authors' settled label (a check that
    does not lean on the matcher's own definition of invented)."""
    key = pd.read_csv(HUMAN / "matcher_labels_key.csv", dtype=str)
    st = pd.read_csv(HUMAN / "matcher_labels_settled.csv", dtype=str, encoding="utf-8-sig")
    key = key.merge(st[["item_id", "label"]].rename(columns={"label": "authors"}), on="item_id")
    key["entry_index"] = key["entry_index"].astype(int)
    m = key.merge(e[["run_id", "request_id", "entry_index", "exact", "fuzzy", "repo_core", "empty"]],
                  on=["run_id", "request_id", "entry_index"], how="left")
    found = int(m["exact"].notna().sum())
    m = m[m["exact"].notna()]
    rows = {row["key"]: row for row in rate_rows(m, "authors")}
    rows["all"] = rate_rows(m, None)[0]
    return {"checked_entries": int(len(key)), "found_in_table": found, "by_authors_label": rows}


# ---------------------------------------------------------------------------------------------------------
# 2. prevalence, matcher and corrected with the authors' labels
def prevalence(e, x, boot):
    res = {}
    cells = {
        "gpu_min_k_shown_n_lt_k_k35": x[(x["group_kind"] == "gpu") & (x["condition"] == "min_k_shown")
                                        & x["k"].isin(KS) & (x["n"] < x["k"])],
        "gpu_none_n_lt_k_k35": x[(x["group_kind"] == "gpu") & (x["condition"] == "none")
                                 & x["k"].isin(KS) & (x["n"] < x["k"])],
        "hosted_min_k_shown_n_lt_k_k35": x[(x["group_kind"] == "hosted") & (x["condition"] == "min_k_shown")
                                           & x["k"].isin(KS) & (x["n"] < x["k"])],
        "all17_min_k_shown_n_lt_k_k35": x[(x["condition"] == "min_k_shown") & x["k"].isin(KS) & (x["n"] < x["k"])],
    }
    for name, d in cells.items():
        ex = d[d["label"].isin(cp.EXTRA)]
        cnt = Counter(ex["label"])
        tot = sum(cnt.values())
        subst = int(d["label"].isin(cp.SUBST).sum())
        res[name] = {"extra_entries": tot, "substantive_entries": subst,
                     "share_of_extras_pct": {cp.LABEL_NAME[l]: pct(cnt[l], tot) for l in cp.EXTRA},
                     "invented_not_echo_or_note_pct_of_extras": pct(int(((ex["label"] == "plausible_invented")
                                                                         & ~ex["note"].isin(["prompt_echo", "possible_note"])).sum()), tot),
                     "invented_share_of_substantive_pct": pct(cnt["plausible_invented"], subst)}
    # the paper's 7%: the whole check frame (unexpanded entries, all 17 models, all conditions, k, n)
    sub = e[e["label"].isin(cp.SUBST)]
    res["frame_invented_share_of_substantive_pct"] = pct(int((sub["label"] == "plausible_invented").sum()), len(sub))
    # corrected composition: P(authors' label | matcher label) from the settled 400-entry check
    key = {r["item_id"]: r for r in csv.DictReader(open(HUMAN / "matcher_labels_key.csv", encoding="utf-8"))}
    settled = {r["item_id"]: r["label"].strip() for r in
               csv.DictReader(open(HUMAN / "matcher_labels_settled.csv", encoding="utf-8-sig"))}
    mapping = {"true_item": "true item", "missed_gold": "true item", "split_of_true": "true-but-split",
               "in_text_wrong_type": "wrong kind", "plausible_invented": "invented"}
    checked = defaultdict(list)        # matcher label -> list of authors' categories
    for i, lab in settled.items():
        if lab == "unsure" or i not in key:
            continue
        checked[key[i]["matcher_label"]].append(mapping[lab])
    cats = ["true item", "true-but-split", "wrong kind", "invented"]
    res["check_sample"] = {
        "drawn_per_stratum": json.loads((HUMAN / "matcher_frame.json").read_text())["allocated"],
        "confusion_rows_matcher_label": {m: dict(Counter(v)) for m, v in checked.items()},
        "stratified": "yes: 400 places split equally over the matcher labels present (134 true-or-split, 133 wrong "
                      "kind, 133 invented; v0 assigns no missed_gold / beyond_excerpt), and within a label equally "
                      "over the 9 sets; the frame is every substantive entry of the 17 full runs, all conditions"}
    rng = np.random.default_rng(SEED)
    for name in ("gpu_min_k_shown_n_lt_k_k35", "gpu_none_n_lt_k_k35"):
        d = cells[name]
        ex = d[d["label"].isin(cp.EXTRA)]
        cnt = Counter(ex["label"])
        # split_of_true has only 10 checked rows: its row is used as is (stated in POSTHOC.md)

        def comp(conf):
            tot = np.zeros(len(cats))
            for m in cp.EXTRA:
                v = np.array([conf[m].count(c) for c in cats], float)
                tot += cnt[m] * v / max(1, v.sum())
            return tot
        est = comp(checked)
        draws = []
        for _ in range(boot):
            rs = {m: list(rng.choice(checked[m], len(checked[m]), replace=True)) for m in cp.EXTRA}
            draws.append(comp(rs))
        draws = np.array(draws)
        tot_all = est.sum()
        still_extra = est[1:].sum()
        out = {"matcher_extras": int(round(tot_all))}
        for j, c in enumerate(cats):
            sh = draws[:, j] / draws.sum(axis=1)
            out[f"{c} % of matcher extras"] = [round(100 * est[j] / tot_all, 1),
                                               round(100 * float(np.quantile(sh, 0.025)), 1),
                                               round(100 * float(np.quantile(sh, 0.975)), 1)]
        inv = draws[:, 3] / draws[:, 1:].sum(axis=1)
        out["invented % of corrected extras (true items removed)"] = [
            round(100 * est[3] / still_extra, 1), round(100 * float(np.quantile(inv, 0.025)), 1),
            round(100 * float(np.quantile(inv, 0.975)), 1)]
        res[f"corrected_{name}"] = out
    # the check rows that come from this very cell
    cell_rows = [(key[i]["matcher_label"], settled[i]) for i in settled if i in key
                 and key[i]["condition"] == "min_k_shown" and int(key[i]["n"]) < int(key[i]["k"])
                 and key[i]["model_key"] in set(x.loc[x["group_kind"] == "gpu", "model_key"].unique())]
    res["check_rows_in_gpu_min_k_shown_n_lt_k"] = {"rows": len(cell_rows),
                                                   "pairs": {f"{a}->{b}": c for (a, b), c in Counter(cell_rows).items()}}
    pd.DataFrame([{"cell": k, **{kk: (json.dumps(vv) if isinstance(vv, (dict, list)) else vv) for kk, vv in v.items()}}
                  for k, v in res.items() if isinstance(v, dict)]).to_csv(cp.OUT / "prevalence.csv", index=False)
    return res


# ---------------------------------------------------------------------------------------------------------
# 3. precision / recall / F1
def prf(sub):
    st, ns = float(sub["n_true"].sum()), float(sub["n_substantive"].sum())
    sp = float((sub["n_true"] + sub["n_split"]).sum())
    pos = sub[sub["n"] >= 1]
    mg, nn = float(pos["matched_gold"].sum()), float(pos["n"].sum())
    p = st / ns if ns else float("nan")
    r = mg / nn if nn else float("nan")
    f1 = 2 * p * r / (p + r) if p + r else float("nan")
    return {"outputs": int(len(sub)), "substantive": int(ns), "precision": p, "precision_split_ok": sp / ns if ns else float("nan"),
            "recall": r, "f1": f1, "mean_extra": float(sub["n_extra"].mean()), "missed_pct": 100 * (1 - r),
            "unreadable_pct": 100 * float(1 - sub["valid"].mean())}


def prf_ci(sub, B):
    """Bootstrap intervals (document groups resampled within set) for pooled P, R, F1."""
    g = sub.assign(pos_mg=np.where(sub["n"] >= 1, sub["matched_gold"], 0), pos_n=np.where(sub["n"] >= 1, sub["n"], 0))
    a = g.groupby("group", observed=True).agg(t=("n_true", "sum"), s=("n_substantive", "sum"), m=("pos_mg", "sum"),
                                              n=("pos_n", "sum"), set=("set", "first"))
    per = {k: (r.t, r.s, r.m, r.n) for k, r in a.iterrows()}
    strata = a["set"].to_dict()
    P = lambda v: v[..., 0] / np.maximum(v[..., 1], 1)  # noqa: E731
    R = lambda v: v[..., 2] / np.maximum(v[..., 3], 1)  # noqa: E731
    F = lambda v: 2 * P(v) * R(v) / np.maximum(P(v) + R(v), 1e-12)  # noqa: E731
    return {nm: B.stat(per, strata, fn) for nm, fn in (("precision", P), ("recall", R), ("f1", F))}


def prf_section(out, main, hosted, boot):
    B = fs.Bootstrap(boot)
    o = out[out["k"].isin(KS)]
    res = {"pooled_gpu": {}, "pooled_gpu_n_lt_k": {}, "pooled_hosted": {}, "per_model": {}}
    rows = []
    for c in COND_ORDER:
        for scope, sub in (("pooled_gpu", o[(o["group_kind"] == "gpu")]),
                           ("pooled_gpu_n_lt_k", o[(o["group_kind"] == "gpu") & (o["n"] < o["k"])]),
                           ("pooled_hosted", o[(o["group_kind"] == "hosted")])):
            s = sub[sub["condition"] == c]
            r = prf(s)
            if scope != "pooled_hosted":
                ci = prf_ci(s, B)
                for nm in ("precision", "recall", "f1"):
                    r[nm + "_ci"] = [round(ci[nm]["lo"], 3), round(ci[nm]["hi"], 3)] if ci[nm] else None
            res[scope][c] = r
            rows.append({"scope": scope, "model": "pooled", "condition": c, **r})
        for m in main + hosted:
            s = o[(o["model_key"] == m) & (o["condition"] == c)]
            if len(s):
                r = prf(s)
                res["per_model"].setdefault(m, {})[c] = r
                rows.append({"scope": "gpu" if m in main else "hosted", "model": m, "condition": c, **r})
    t = pd.DataFrame(rows)
    t.to_csv(cp.OUT / "prf.csv", index=False, float_format="%.4f")
    # padding vs missed, per (model, condition)
    pts = []
    for m in main + hosted:
        for c in COND_ORDER:
            s = o[(o["model_key"] == m) & (o["condition"] == c)]
            lt = s[s["n"] < s["k"]]
            if not len(s):
                continue
            r = prf(s)
            pts.append({"model_key": m, "model": fs.NAME.get(m, m), "group": "gpu" if m in main else "hosted",
                        "condition": c, "outputs": r["outputs"], "mean_extra_entries": round(r["mean_extra"], 4),
                        "missed_true_items_pct": round(r["missed_pct"], 3), "recall": round(r["recall"], 4),
                        "precision": round(r["precision"], 4), "f1": round(r["f1"], 4),
                        "mean_extra_entries_n_lt_k": round(float(lt["n_extra"].mean()), 4) if len(lt) else None,
                        "unreadable_pct": round(r["unreadable_pct"], 2)})
    pd.DataFrame(pts).to_csv(cp.OUT / "padding_vs_missed.csv", index=False)
    write_scatter(pts)
    return res


MARK = {"none": ("black", "*"), "prose_up_to_k": ("gray", "o"), "prose_exactly_k": ("gray", "square*"),
        "max_k_shown": ("blue", "triangle"), "min_k_shown": ("red", "triangle*"),
        "min_k_shown_fewer_ok": ("orange", "diamond*"), "min_k_enforced": ("purple", "square"),
        "min_k_escape": ("teal", "diamond")}


def write_scatter(pts):
    L = ["% POST HOC: padding vs missed true items, 8 GPU main models x 8 conditions, k = 3 and 5, all documents.",
         "% Written by analysis/posthoc/posthoc.py from analysis/posthoc/out/padding_vs_missed.csv. Needs pgfplots.",
         "\\begin{tikzpicture}", "\\begin{axis}[", "  width=\\columnwidth, height=0.78\\columnwidth,",
         "  xlabel={Extra entries per output (mean)}, ylabel={True items missed (\\%)},",
         "  label style={font=\\footnotesize}, tick label style={font=\\footnotesize},",
         "  legend cell align=left, legend style={font=\\footnotesize, at={(0.5,1.02)}, anchor=south, draw=none, legend columns=2,",
         "               /tikz/every even column/.append style={column sep=4pt}},",
         "  xmin=0, ymin=0, grid=major, grid style={gray!20},", "]"]
    for c in COND_ORDER:
        col, mk = MARK[c]
        coords = " ".join(f"({p['mean_extra_entries']:.3f},{p['missed_true_items_pct']:.2f})"
                          for p in pts if p["group"] == "gpu" and p["condition"] == c)
        L.append(f"\\addplot[only marks, mark={mk}, mark size=1.8pt, color={col}] coordinates {{{coords}}};")
        L.append(f"\\addlegendentry{{\\cnd{{{c.replace('_', chr(92) + '_')}}}}}")
    L += ["\\end{axis}", "\\end{tikzpicture}"]
    (cp.OUT / "fig_padding_vs_missed.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------------------------------------
# 5. examples
def examples(e, out, main):
    docs = common.load_documents()
    o = out[(out["group_kind"] == "gpu") & (out["condition"] == "min_k_shown") & out["k"].isin(KS)
            & (out["n"] < out["k"]) & (out["n"] >= 1) & (out["over_count"] == 1)]
    ent = e[(e["group_kind"] == "gpu") & (e["condition"] == "min_k_shown")]
    by = {(r, q): g for (r, q), g in ent.groupby(["run_id", "request_id"], sort=False)}
    picked, md, restricted_txt = {}, [], []
    for s in fs.SETS:
        cand = []
        for r in o[o["set"] == s].itertuples():
            g = by.get((r.run_id, r.request_id))
            if g is None:
                continue
            g = g.sort_values("entry_index")
            if g["text"].str.len().max() > 200 or len(g) > 6 or not g["label"].isin(cp.EXTRA).any():
                continue
            hv = hashlib.sha256(f"{r.run_id}|{r.request_id}".encode()).hexdigest()
            cand.append((hv, r, g))
        if not cand:
            continue
        hv, r, g = min(cand, key=lambda t: t[0])
        doc = docs[r.doc_id]
        gold = [x["text"] for x in doc.get("gold_items") or []]
        info = {"set": s, "model": fs.NAME[r.model_key], "doc_id": r.doc_id, "k": int(r.k), "n": int(r.n),
                "entries": int(len(g)), "extra": int(g["label"].isin(cp.EXTRA).sum()),
                "labels": [cp.LABEL_NAME[l] for l in g["label"]], "candidates": len(cand)}
        picked[s] = info
        head = (f"### {fs.SET_NAME[s]}: {info['model']}, document `{r.doc_id}`, k = {r.k}, n = {r.n} "
                f"({info['entries']} entries, {info['extra']} extra)")
        if s in cp.restricted_sets():
            md += [head, "", "REVIEWS_PARAPHRASE", ""]
            restricted_txt += [head, "", "True items:", *[f"- {t}" for t in gold], "", "Entries:",
                               *[f"- [{cp.LABEL_NAME[l]}] {t}" for l, t in zip(g["label"], g["text"])], "",
                               "Document:", doc["text"], ""]
        else:
            md += [head, "", "True items:", *[f"- {t[:200]}" for t in gold], "", "The model's list (matcher v0 label):",
                   *[f"{i + 1}. {t} -- **{cp.LABEL_NAME[l]}**{' (extra)' if l in cp.EXTRA else ''}"
                     for i, (l, t) in enumerate(zip(g["label"], g["text"]))], ""]
    (cp.CACHE / "examples_reviews_TEXT.md").write_text("\n".join(restricted_txt), encoding="utf-8")
    return picked, md


# ---------------------------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--boot", type=int, default=10000)
    a = ap.parse_args()
    cp.OUT.mkdir(parents=True, exist_ok=True)
    e, main_m, hosted = load_entries()
    x = expand_none(e)
    out, _, _ = load_outputs()
    res = {"checks": checks(e, x, out, main_m)}
    res["source_check"] = source_check(x)
    res["source_check_human"] = source_check_human(e)
    res["prevalence"] = prevalence(e, x, a.boot)
    res["prf"] = prf_section(out, main_m, hosted, a.boot)
    picked, md = examples(e, out, main_m)
    res["examples"] = picked
    (cp.OUT / "posthoc_results.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
    (cp.OUT / "examples.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    import report
    report.write(res)


if __name__ == "__main__":
    main()
