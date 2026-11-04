#!/usr/bin/env python3
"""esco_downstream.py: job-ad skills linked to ESCO (OSF addendum 1, section 3.2; exploratory).

    python analysis/downstream/esco/esco_downstream.py --runs <run folder> [<run folder> ...] [--boot 10000]

    # the registered set: the 8 main models and the hosted references, plus the addendum-1 closed models
    python analysis/downstream/esco/esco_downstream.py \\
        --runs ../fs-runs/fs_*_full ../wt-closed/runs/a1_*

Inputs
- run folders as harness/run.py writes them (manifest.json, planned.jsonl, raw*.jsonl). Each run's matcher
  labels come from the frozen scorer (analysis/full_study_score.py): a scored table in one of --scored
  (default: analysis/full/scored/ and this folder's cache/scored/) is reused when its source hash matches the
  run folder; otherwise the run is scored into cache/scored/ with the same code.
- entry text: the run's raw records parsed with harness/common.py exactly as full_study_score.py does
  (latest record per request id; parse_output on the request's field). The entry index of each parsed item
  is checked against the scored table (same number of entries, same word count, same placeholder and repeat
  calls); a mismatch stops the script.
- ESCO v1.2.1 skills pillar (fetch_esco.py) and the linker (esco_linker.py).

Cells: the two SkillSpan sets (job_posts = job-ad skills, job_posts_knowledge = job-ad knowledge), documents
with n < k at k = 3 and 5, ok outputs only. Substantive entries = entries the matcher labels neither
placeholder nor repeat (the same entries harness/common.count_items counts as substantive). Each condition is
paired with `none` per (model, document, k), as in analysis/full_study.py: the `none` answer is reused at k = 3
and 5, and the 5 wordings of a prose condition are averaged first (each wording weighs 1/m when m wordings
answered).

Measures, per output (an output is one model's answer for one ad), with the true items of that ad linked by
the same linker:
  false concepts per ad   distinct concepts linked from substantive entries that no true item of the ad links to
  ad has a false concept  1 if that count is at least 1
  precision, recall       sum of concepts shared with the true items' concepts / sum of output concepts (or
                          of true-item concepts), over all pairs (ratio of sums)
  top-20                  the 20 concepts linked from the most outputs (wordings weighted as above), compared
                          with the 20 concepts linked from the most of the same ads' true items; reported:
                          how many of the first are not among the second. Ties broken by concept URI.
Intervals: 95% percentile intervals from --boot draws over document groups resampled within set, seed
20261014: the same draws as analysis/full_study.py's Bootstrap (checked by the tests). p: two-sided
bootstrap p-value of a difference, 2 x min(share of draws <= 0, share >= 0).

Outputs (this folder): RESULTS.md, results.json, tex/tab_esco_main.tex, tex/tab_esco_models.tex,
links_true_items.csv (every true item and its link). Cache (not committed): cache/entry_links.csv.gz (every
substantive entry and its link; read by hand_check.py), cache/scored/, embeddings.
"""
import argparse
import csv
import gzip
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(ROOT / "harness"))
sys.path.insert(0, str(ROOT / "analysis"))
sys.path.insert(0, str(HERE))
import common  # noqa: E402
import esco_linker as el  # noqa: E402

SEED = 20261014
SETS = ["job_posts", "job_posts_knowledge"]
SET_NAME = {"job_posts": "job-ad skills", "job_posts_knowledge": "job-ad knowledge", "pooled": "both sets"}
KS = (3, 5)
SUBSTANTIVE = ("true_item", "split_of_true", "in_text_wrong_type", "plausible_invented")
CONDS = ["prose_up_to_k", "prose_exactly_k", "max_k_shown", "min_k_shown", "min_k_shown_fewer_ok",
         "min_k_enforced", "min_k_escape"]
TOPN = 20
SCALE = 60          # wording weights are 1/m, m in 1..5: counts x 60 are whole numbers (exact tie-breaking)
CACHE = HERE / "cache"
SCORED_DEFAULT = [ROOT / "analysis" / "full" / "scored", CACHE / "scored"]


# ---------------------------------------------------------------------------------------------------------
# bootstrap: the draws of analysis/full_study.py's Bootstrap, as a weight matrix (group -> times drawn)
def draw_weights(groups, strata, boot=10000, seed=SEED):
    """W (boot x len(groups)): how often each group is drawn in each bootstrap draw. Same random numbers,
    in the same order, as full_study.Bootstrap.stat for the same group list and strata."""
    by_set = defaultdict(list)
    for i, g in enumerate(groups):
        by_set[strata[g]].append(i)
    rng = np.random.default_rng(seed)
    W = np.zeros((boot, len(groups)))
    rows = np.arange(boot)[:, None]
    for idx in by_set.values():
        idx = np.array(idx)
        pick = idx[rng.integers(0, len(idx), (boot, len(idx)))]
        np.add.at(W, (np.broadcast_to(rows, pick.shape), pick), 1)
    return W


_W = {}


def _weights(groups, sets, boot):
    key = (groups, sets, boot)
    if key not in _W:
        _W.clear()
        _W[key] = draw_weights(list(groups), dict(zip(groups, sets)), boot)
    return _W[key]


def summarise(est, draws, test=False):
    draws = np.asarray(draws, float)
    draws = np.sort(draws[np.isfinite(draws)])
    if not len(draws) or est is None or not np.isfinite(est):
        return None
    out = {"est": float(est), "lo": float(draws[int(0.025 * len(draws))]),
           "hi": float(draws[int(0.975 * len(draws)) - 1])}
    if test:
        out["p"] = float(min(1.0, 2 * min((draws <= 0).mean(), (draws >= 0).mean())))
    return out


# ---------------------------------------------------------------------------------------------------------
# runs: scored tables and entry text
def run_folders(paths):
    out = []
    for p in map(Path, paths):
        if (p / "manifest.json").exists() and (p / "planned.jsonl").exists():
            out.append(p)
        elif p.is_dir():
            out += sorted(q for q in p.iterdir() if (q / "manifest.json").exists() and (q / "planned.jsonl").exists())
    seen, uniq = set(), []
    for p in out:
        if p.resolve() not in seen:
            seen.add(p.resolve())
            uniq.append(p)
    return uniq


def scored_entries(run_dir, scored_dirs):
    """The frozen scorer's entry table for this run: reused if its source hash matches, else scored now."""
    import full_study_score as fss
    rid = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))["run_id"]
    src = fss.source_hash(run_dir)
    for d in scored_dirs:
        meta = Path(d) / f"{rid}.source.json"
        ent, outs = Path(d) / f"{rid}.entries.csv.gz", Path(d) / f"{rid}.outputs.csv.gz"
        if meta.exists() and ent.exists() and outs.exists() and json.loads(meta.read_text())["source"] == src:
            return ent, outs, "reused"
    (CACHE / "scored").mkdir(parents=True, exist_ok=True)
    fss.score_run(run_dir, CACHE / "scored")
    return CACHE / "scored" / f"{rid}.entries.csv.gz", CACHE / "scored" / f"{rid}.outputs.csv.gz", "scored"


def outputs_of_run(run_dir, scored_dirs, ctx):
    """One dict per covered request id in the cells (job-ad sets, n < k, k = 3 and 5) with an ok output:
    model, document, condition, k, wording and the substantive entries (index, text, matcher label)."""
    import full_study_score as fss
    man = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    rid, model = man["run_id"], man["model_key"]
    ent_path, out_path, how = scored_entries(run_dir, scored_dirs)
    ents = pd.read_csv(ent_path, dtype={"request_id": str}, keep_default_na=False)
    ents = ents[ents["set"].isin(SETS)]
    lab = defaultdict(dict)
    for r in ents.itertuples(index=False):
        lab[r.request_id][int(r.entry_index)] = (r.label, int(r.n_words))
    outs = pd.read_csv(out_path, dtype={"request_id": str}, keep_default_na=False, low_memory=False)
    outs = outs[outs["set"].isin(SETS) & (outs["status"] == "ok")]
    n_subst = dict(zip(outs["request_id"], pd.to_numeric(outs["n_substantive"], errors="coerce")))
    recs = fss.latest_records(run_dir)
    rows, checked = [], 0
    for p in common.read_jsonl(run_dir / "planned.jsonl"):
        src_rid = p.get("source_request_id") or ""
        base = ctx.req[src_rid or p["request_id"]]
        if base["set"] not in SETS:
            continue
        rec = recs.get(p["request_id"])
        if rec is None or rec["status"] != "ok":
            continue
        doc = ctx.docs[base["doc_id"]]
        parsed = common.parse_output(rec.get("content"), common.field_of(base, ctx.prompts))
        items = parsed["items"] or []
        got = lab.get(p["request_id"], {})
        if len(got) != len(items) or any(got[i][1] != len(str(items[i]).split()) for i in range(len(items))):
            raise SystemExit(f"{rid} {p['request_id']}: parsed entries do not line up with the scored table")
        earlier = []
        for i, it in enumerate(items):          # placeholder / repeat calls must agree with the label
            ph = common.is_placeholder(it, ctx.esc, doc["text"])
            rp = (not ph) and common.is_duplicate(it, earlier)
            if not ph and not rp:
                earlier.append(it)
            want = "placeholder" if ph else "repeat" if rp else None
            if (want or "substantive") != (got[i][0] if got[i][0] in ("placeholder", "repeat") else "substantive"):
                raise SystemExit(f"{rid} {p['request_id']} entry {i}: placeholder/repeat call differs from the label")
        subst = [(i, str(items[i]).strip(), got[i][0]) for i in range(len(items)) if got[i][0] in SUBSTANTIVE]
        if p["request_id"] in n_subst and n_subst[p["request_id"]] != len(subst):
            raise SystemExit(f"{rid} {p['request_id']}: substantive count differs from the scored table")
        checked += len(items)
        arm = p.get("arm") or base.get("arm") or "main"
        if arm != "main":
            continue
        for cid in [p["request_id"], *p.get("also_answers", [])]:
            q = ctx.req[cid]
            if q["k"] not in KS or not q["n"] < q["k"]:
                continue
            rows.append({"run_id": rid, "model_key": model, "request_id": p["request_id"], "covered_id": cid,
                         "doc_id": q["doc_id"], "group": doc.get("group") or q["doc_id"], "set": q["set"],
                         "split": doc["split"], "condition": q["condition"], "k": q["k"], "n": q["n"],
                         "wording_id": q["wording_id"], "entries": subst})
    return rows, {"run_id": rid, "model_key": model, "table": how, "entries_checked": checked,
                  "outputs_in_cells": len(rows)}


# ---------------------------------------------------------------------------------------------------------
# linking
def link_all(rows, docs, linker):
    """Link every true item of the job-ad documents and every substantive entry. Returns
    (true_links: doc_id -> [(gold index, text, concept, label idx, score)], entry link per text)."""
    gold = {}
    for d in docs.values():
        if d.get("set") in SETS and d.get("split") in ("pilot", "full"):
            gold[d["doc_id"]] = [(j, g["text"].strip()) for j, g in enumerate(d.get("gold_items") or [])]
    texts = sorted({t for v in gold.values() for _, t in v} | {t for r in rows for _, t, _ in r["entries"]})
    ci, li, sc = linker.best(texts)
    best = {t: (int(c), int(l), float(s)) for t, c, l, s in zip(texts, ci, li, sc)}
    true_links = {d: [(j, t, *best[t]) for j, t in v] for d, v in gold.items()}
    return true_links, best


def concept_sets(rows, true_links, best, cutoff):
    """Per row: output concept set (substantive entries linked at the cutoff); per doc: true concept set."""
    true_c = {d: {c for _, _, c, _, s in v if el.link_scores([s], cutoff)[0]} for d, v in true_links.items()}
    out_c = [{best[t][0] for _, t, _ in r["entries"] if el.link_scores([best[t][2]], cutoff)[0]} for r in rows]
    return out_c, true_c


# ---------------------------------------------------------------------------------------------------------
# measures
def output_measures(out_set, true_set):
    """The per-output quantities: false concepts, has a false concept, shared, output concepts, true concepts."""
    false = len(out_set - true_set)
    return {"false": false, "any": float(false >= 1), "tp": len(out_set & true_set), "pred": len(out_set),
            "true": len(true_set)}


def cell_frame(rows, out_c, true_c):
    """One row per (model, doc, k, condition): wording-averaged measures, plus the concept weights."""
    recs = []
    for r, oc in zip(rows, out_c):
        m = output_measures(oc, true_c.get(r["doc_id"], set()))
        recs.append({"model_key": r["model_key"], "doc_id": r["doc_id"], "group": r["group"], "set": r["set"],
                     "k": r["k"], "condition": r["condition"], "concepts": frozenset(oc), **m})
    f = pd.DataFrame(recs)
    key = ["model_key", "doc_id", "k", "condition"]
    agg = f.groupby(key, sort=True).agg(group=("group", "first"), set=("set", "first"), false=("false", "mean"),
                                        any=("any", "mean"), tp=("tp", "mean"), pred=("pred", "mean"),
                                        true=("true", "first"), m=("false", "size"))
    weights = defaultdict(lambda: defaultdict(float))
    for kk, sub in f.groupby(key, sort=False):
        w = weights[kk]
        for cs in sub["concepts"]:
            for c in cs:
                w[c] += 1.0 / len(sub)
    agg = agg.reset_index()
    agg["weights"] = [dict(weights[tuple(x)]) for x in agg[key].itertuples(index=False, name=None)]
    return agg


def pair(frame, a, b="none"):
    """Rows of condition a joined with condition b on (model, doc, k); both sides needed."""
    A = frame[frame["condition"] == a].set_index(["model_key", "doc_id", "k"])
    B = frame[frame["condition"] == b].set_index(["model_key", "doc_id", "k"])
    j = A.join(B, how="inner", lsuffix="_a", rsuffix="_b")
    return j.reset_index()


def top_mask(counts, n=TOPN):
    """Boolean mask of the n concepts with the highest counts (ties: lower column index, i.e. URI order,
    first; zero counts never selected). counts: (..., C) array of counts x SCALE (whole numbers)."""
    C = counts.shape[-1]
    score = np.rint(counts) * C + (C - 1 - np.arange(C))
    k = min(n, C)
    idx = np.argpartition(-score, k - 1, axis=-1)[..., :k]
    mask = np.zeros(counts.shape, dtype=bool)
    np.put_along_axis(mask, idx, True, axis=-1)
    return mask & (counts > 0)


def not_in_true_top(out_counts, true_counts, n=TOPN):
    return (top_mask(out_counts, n) & ~top_mask(true_counts, n)).sum(axis=-1)


def measure_pairs(pr, boot, true_sets, top=True):
    """All measures on a paired frame (condition a vs none), with bootstrap intervals."""
    if pr is None or not len(pr):
        return None
    g = pr.groupby("group_a", sort=True)
    groups = list(g.groups)
    strata = g["set_a"].first().to_dict()
    cols = ["false_a", "false_b", "any_a", "any_b", "tp_a", "pred_a", "tp_b", "pred_b", "true_a"]
    S = g[cols].sum()
    S["n"] = g.size()
    M = S.loc[groups, cols + ["n"]].to_numpy(float)
    W = _weights(tuple(groups), tuple(strata[g] for g in groups), boot)
    T = W @ M
    e = M.sum(axis=0)
    ix = {c: i for i, c in enumerate(cols + ["n"])}

    def stats(v):
        with np.errstate(divide="ignore", invalid="ignore"):
            fa, fb = v[..., ix["false_a"]] / v[..., ix["n"]], v[..., ix["false_b"]] / v[..., ix["n"]]
            aa, ab = v[..., ix["any_a"]] / v[..., ix["n"]], v[..., ix["any_b"]] / v[..., ix["n"]]
            pa, pb = v[..., ix["tp_a"]] / v[..., ix["pred_a"]], v[..., ix["tp_b"]] / v[..., ix["pred_b"]]
            ra, rb = v[..., ix["tp_a"]] / v[..., ix["true_a"]], v[..., ix["tp_b"]] / v[..., ix["true_a"]]
        return {"false": (fa, fb), "any": (aa, ab), "precision": (pa, pb), "recall": (ra, rb)}

    est, dr = stats(e), stats(T)
    res = {"pairs": int(len(pr)), "groups": len(groups), "docs": int(pr["doc_id"].nunique()),
           "models": int(pr["model_key"].nunique())}
    for name in est:
        a, b = est[name]
        da, db = dr[name]
        res[name] = {"cond": summarise(a, da), "none": summarise(b, db), "diff": summarise(a - b, da - db, test=True)}
    if top:
        res["top20"] = top20(pr, groups, W, true_sets)
    return res


def top20(pr, groups, W, true_sets):
    """How many of the 20 concepts linked most often are not among the true items' top 20 (cond and none)."""
    concepts = sorted({c for col in ("weights_a", "weights_b") for w in pr[col] for c in w}
                      | {c for d in pr["doc_id"].unique() for c in true_sets[d]})
    pos = {c: i for i, c in enumerate(concepts)}
    gi = {g: i for i, g in enumerate(groups)}
    C, G = len(concepts), len(groups)
    if not C:
        return None
    A, B, T = np.zeros((G, C)), np.zeros((G, C)), np.zeros((G, C))
    for r in pr.itertuples(index=False):
        i = gi[r.group_a]
        for c, w in r.weights_a.items():
            A[i, pos[c]] += w * SCALE
        for c, w in r.weights_b.items():
            B[i, pos[c]] += w * SCALE
        for c in true_sets[r.doc_id]:
            T[i, pos[c]] += SCALE
    res = {}
    est = {"cond": not_in_true_top(A.sum(0), T.sum(0)), "none": not_in_true_top(B.sum(0), T.sum(0))}
    draws = {"cond": [], "none": []}
    for a in range(0, len(W), 500):
        w = W[a:a + 500]
        tt = w @ T
        draws["cond"].append(not_in_true_top(w @ A, tt))
        draws["none"].append(not_in_true_top(w @ B, tt))
    dc, dn = np.concatenate(draws["cond"]), np.concatenate(draws["none"])
    res["cond"] = summarise(float(est["cond"]), dc)
    res["none"] = summarise(float(est["none"]), dn)
    res["diff"] = summarise(float(est["cond"] - est["none"]), dc - dn, test=True)
    order = np.lexsort((np.arange(C), -np.rint(A.sum(0))))[:TOPN]
    res["cond_top"] = [concepts[i] for i in order if A.sum(0)[i] > 0]
    order = np.lexsort((np.arange(C), -np.rint(T.sum(0))))[:TOPN]
    res["true_top"] = [concepts[i] for i in order if T.sum(0)[i] > 0]
    return res


# ---------------------------------------------------------------------------------------------------------
# reporting
def f2(r, nd=2, scale=1.0, sign=False):
    if not r:
        return "--"
    s = "+" if sign else ""
    return f"{scale * r['est']:{s}.{nd}f} [{scale * r['lo']:{s}.{nd}f}, {scale * r['hi']:{s}.{nd}f}]"


def fp(p):
    return "--" if p is None else ("< 0.0001" if p < 1e-4 else f"{p:.4f}")


def tex_ci(r, nd=2, scale=1.0, sign=False):
    if not r:
        return "--"
    s = "+" if sign else ""
    return (f"${scale * r['est']:{s}.{nd}f}$ [${scale * r['lo']:{s}.{nd}f}$, ${scale * r['hi']:{s}.{nd}f}$]"
            .replace("+-", "-"))


def md_table(head, rows):
    return ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + \
           ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]


def tex_table(cols, head, rows):
    out = ["\\begin{tabular}{" + cols + "}", "  \\toprule", "  " + " & ".join(head) + " \\\\", "  \\midrule"]
    for r in rows:
        out.append("  \\midrule" if r == "MIDRULE" else "  " + " & ".join(str(x) for x in r) + " \\\\")
    return "\n".join(out + ["  \\bottomrule", "\\end{tabular}"]) + "\n"


def cnd(c):
    return "\\cnd{" + c.replace("_", "\\_") + "}"


def tex_escape(s):
    return str(s).replace("_", "\\_").replace("%", "\\%").replace("&", "\\&")


def main_lineup():
    import yaml
    cfg = yaml.safe_load((ROOT / "configs" / "models.yaml").read_text(encoding="utf-8"))
    return list(cfg["full_study"]["gpu"]["main"])


def model_name(m):
    import full_study as fs
    extra = {"azure-gpt-6-sol": "GPT-6 Sol (Azure)", "azure-gpt-6-luna": "GPT-6 Luna (Azure)",
             "bedrock-grok-4.3": "Grok 4.3 (Bedrock)"}
    return fs.NAME.get(m, extra.get(m, m))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs", nargs="+", required=True, help="run folders (or folders holding run folders)")
    ap.add_argument("--scored", nargs="*", default=[str(p) for p in SCORED_DEFAULT])
    ap.add_argument("--boot", type=int, default=10000)
    ap.add_argument("--out", default=str(HERE))
    a = ap.parse_args()
    t0 = time.time()
    out = Path(a.out)
    import full_study_score as fss
    ctx = fss.Context()
    folders = [p for p in run_folders(a.runs) if re.search(r"_full$|_addendum1(-enforced)?$", p.name)]
    rows, runs = [], []
    for p in folders:
        r, info = outputs_of_run(p, a.scored, ctx)
        rows += r
        runs.append(info)
        print(f"{info['run_id']}: {info['outputs_in_cells']} outputs in the cells, {info['entries_checked']} "
              f"entries checked against the scored table ({info['table']})", flush=True)
    concepts = el.load_concepts()
    meta = json.loads((HERE / "ESCO.json").read_text(encoding="utf-8"))
    linker = el.Linker(concepts, el.Embedder())
    true_links, best = link_all(rows, ctx.docs, linker)
    write_links(out, rows, true_links, best, concepts, linker)
    main_models = main_lineup()
    present = sorted({r["model_key"] for r in rows})
    others = [m for m in present if m not in main_models]
    # registered: the 8 main models pooled, and each other model alone; each main model alone is added
    # (not in the registration) so the pooled number can be read
    scopes = [("main", "8 main models pooled", [m for m in main_models if m in present])] + \
             [(m, model_name(m) + " (main model alone; not registered)", [m]) for m in main_models if m in present] + \
             [(m, model_name(m), [m]) for m in others]
    results = {"esco": meta, "linker": {"model": el.MODEL, "revision": el.REVISION, "cutoff": el.CUTOFF,
                                        "sensitivity": list(el.SENSITIVITY)},
               "runs": runs, "boot": a.boot, "seed": SEED, "cells": {}}
    for cname, cut in el.CUTOFFS.items():
        out_c, true_c = concept_sets(rows, true_links, best, cut)
        frame = cell_frame(rows, out_c, true_c)
        results["cells"][cname] = {}
        for sid, sname, models in scopes:
            fm = frame[frame["model_key"].isin(models)]
            for setname in (["pooled", *SETS] if cname == "0.5" else ["pooled"]):
                fs_ = fm if setname == "pooled" else fm[fm["set"] == setname]
                for c in CONDS:
                    if not (fs_["condition"] == c).any():
                        continue
                    res = measure_pairs(pair(fs_, c), a.boot, true_c)
                    if res:
                        if res.get("top20"):          # concept indices -> URIs (kept for min_k_shown only)
                            for key in ("cond_top", "true_top"):
                                if c == "min_k_shown":
                                    res["top20"][key] = [concepts[i]["uri"] for i in res["top20"][key]]
                                else:
                                    del res["top20"][key]
                        results["cells"][cname].setdefault(sid, {}).setdefault(setname, {})[c] = res
            print(f"cutoff {cname}: {sname} done ({time.time() - t0:.0f}s)", flush=True)
        results["cells"][cname]["_linked_share"] = linked_share(rows, true_links, best, cut, main_models)
    results["scopes"] = [[s, n, m] for s, n, m in scopes]
    (out / "results.json").write_text(json.dumps(results, indent=1), encoding="utf-8")
    write_results(out, results, concepts, scopes)
    print(f"done in {time.time() - t0:.0f}s")


def linked_share(rows, true_links, best, cut, main_models):
    t = [s for v in true_links.values() for *_, s in v]
    e = [best[x][2] for r in rows if r["model_key"] in main_models for _, x, _ in r["entries"]]
    return {"true_items": len(t), "true_items_linked": int(el.link_scores(t, cut).sum()) if t else 0,
            "main_entries": len(e), "main_entries_linked": int(el.link_scores(e, cut).sum()) if e else 0}


def write_links(out, rows, true_links, best, concepts, linker):
    with open(out / "links_true_items.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["doc_id", "gold_index", "text", "concept_uri", "concept_label", "matched_label", "cosine"])
        for d in sorted(true_links):
            for j, t, c, l, s in true_links[d]:
                w.writerow([d, j, t, concepts[c]["uri"], concepts[c]["label"], linker.label_texts[l], f"{s:.4f}"])
    CACHE.mkdir(exist_ok=True)
    with gzip.open(CACHE / "entry_links.csv.gz", "wt", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["run_id", "model_key", "request_id", "entry_index", "doc_id", "set", "condition", "k", "n",
                    "label", "text", "concept_uri", "concept_label", "matched_label", "cosine"])
        seen = set()
        for r in rows:
            if (r["run_id"], r["request_id"]) in seen:      # a `none` answer covers several k: write it once
                continue
            seen.add((r["run_id"], r["request_id"]))
            for i, t, lab in r["entries"]:
                c, l, s = best[t]
                w.writerow([r["run_id"], r["model_key"], r["request_id"], i, r["doc_id"], r["set"], r["condition"],
                            r["k"], r["n"], lab, t, concepts[c]["uri"], concepts[c]["label"], linker.label_texts[l],
                            f"{s:.4f}"])


def write_results(out, R, concepts, scopes):
    label = {c["uri"]: c["label"] for c in concepts}
    meta, L = R["esco"], R["linker"]
    md = ["# Job-ad skills linked to ESCO (OSF addendum 1, section 3.2; exploratory)", "",
          "Written by `python analysis/downstream/esco/esco_downstream.py` (see its docstring for every "
          "definition). Every number below comes from that script; nothing is typed in by hand.", "",
          f"- ESCO {meta['version']} (English, skills pillar: {meta['concepts']} concepts, "
          f"{meta['labels_preferred_plus_alternative']} preferred + alternative labels), package "
          f"\"{meta['package']}\" from ec.europa.eu/esco/download (Last-Modified {meta['last_modified']}), fetched "
          f"{meta['fetched_utc']}; zip sha256 `{meta['zip_sha256']}` (`ESCO.json`, `fetch_esco.py`).",
          f"- Linker: `{L['model']}` at revision `{L['revision']}`; an entry links to the concept of its most "
          f"similar label if the cosine is at least {L['cutoff']}; sensitivity: no cutoff, 0.7.",
          "- Cells: job-ad skills and job-ad knowledge, documents with n < k at k = 3 and 5, ok outputs; each "
          "condition paired with `none` per (model, document, k), prose wordings averaged.",
          f"- Intervals: 95% percentile, {R['boot']} bootstrap draws over document groups within set, seed "
          f"{R['seed']}; p = two-sided bootstrap p-value of the difference.", "",
          "## Runs read", ""]
    md += md_table(["run", "model", "outputs in the cells", "entries checked", "matcher labels"],
                   [[r["run_id"], r["model_key"], r["outputs_in_cells"], r["entries_checked"], r["table"]]
                    for r in R["runs"]])
    md += ["", "Entries checked: every parsed entry of every ok job-ad output lined up with the frozen scorer's "
           "entry table (same count, same word count, same placeholder and repeat calls).", "",
           "## How much gets linked", ""]
    rows = []
    for cname in el.CUTOFFS:
        s = R["cells"][cname]["_linked_share"]
        rows.append([cname, f"{s['true_items_linked']} / {s['true_items']}",
                     f"{s['main_entries_linked']} / {s['main_entries']}"])
    md += md_table(["cutoff", "true items linked", "substantive entries linked (8 main models, cells)"], rows)
    measures = [("false", "False ESCO concepts per ad", 2, 1.0), ("any", "Ads with at least one false concept (%)", 1, 100.0),
                ("precision", "ESCO precision (%)", 1, 100.0), ("recall", "ESCO recall (%)", 1, 100.0),
                ("top20", "Top-20 concepts not in the true items' top 20", 0, 1.0)]
    h = R["cells"]["0.5"].get("main", {}).get("pooled", {}).get("min_k_shown")
    if h:
        md += ["", "## Headline (8 main models pooled, both sets, cutoff 0.5)", "",
               f"- False ESCO concepts per ad: {f2(h['false']['none'])} under `none`, {f2(h['false']['cond'])} under "
               f"`min_k_shown`; difference {f2(h['false']['diff'], sign=True)} (p {fp(h['false']['diff']['p'])}; "
               f"{h['pairs']} pairs, {h['docs']} ads, {h['groups']} document groups).",
               f"- Ads with at least one false concept: {f2(h['any']['none'], 1, 100)}% vs {f2(h['any']['cond'], 1, 100)}%.",
               f"- ESCO precision: {f2(h['precision']['none'], 1, 100)}% vs {f2(h['precision']['cond'], 1, 100)}%; "
               f"recall {f2(h['recall']['none'], 1, 100)}% vs {f2(h['recall']['cond'], 1, 100)}%."]
        if h.get("top20"):
            md.append("- Of the 20 concepts linked most often, not among the true items' top 20: "
                      f"{h['top20']['none']['est']:.0f} under `none`, {h['top20']['cond']['est']:.0f} under `min_k_shown`.")
    sec = 0
    for cname in el.CUTOFFS:
        for sid, sname, models in scopes:
            if sid not in R["cells"][cname]:
                continue
            for setname, conds in R["cells"][cname][sid].items():
                sec += 1
                md += ["", f"## {sec}. {sname}, {SET_NAME[setname]}, cutoff {cname}", ""]
                body = []
                for c, res in conds.items():
                    for key, mname, nd, sc in measures:
                        x = res.get(key)
                        if not x:
                            body.append([f"`{c}`", res["pairs"], mname, "--", "--", "--", "--"])
                            continue
                        body.append([f"`{c}`", res["pairs"], mname, f2(x["none"], nd, sc), f2(x["cond"], nd, sc),
                                     f2(x["diff"], nd, sc, True), fp(x["diff"]["p"] if x["diff"] else None)])
                md += md_table(["condition", "pairs", "measure", "none", "condition", "difference", "p"], body)
                if setname == "pooled" and cname == "0.5" and "min_k_shown" in conds and conds["min_k_shown"].get("top20"):
                    t = conds["min_k_shown"]["top20"]
                    md += ["", "Top 20 concepts of the `min_k_shown` outputs: " + "; ".join(label[u] for u in t["cond_top"]),
                           "", "Top 20 concepts of the true items of the same ads: " +
                           "; ".join(label[u] for u in t["true_top"])]
    md += ["", "## Notes", "",
           "- Second linker: the SkillSpan authors' follow-up on linking to ESCO (Zhang, van der Goot and Plank, "
           "Findings of EACL 2024, github.com/jjzha/el_esco) fine-tunes BLINK and GENRE and releases training code and "
           "data, but no trained linker and no recommendation of one to use; so no second linker is added.",
           "- Hand check of the linker: `hand_check.py` (50 links, seed 20261013); its result is written to "
           "`HAND_CHECK.md` once both files are filled."]
    (out / "RESULTS.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    write_tex(out, R, scopes)


def write_tex(out, R, scopes):
    (out / "tex").mkdir(exist_ok=True)
    main = R["cells"]["0.5"].get("main", {}).get("pooled", {})
    rows = []
    for c, res in main.items():
        rows.append([cnd(c), tex_ci(res["false"]["none"]), tex_ci(res["false"]["cond"]),
                     tex_ci(res["false"]["diff"], sign=True), tex_ci(res["any"]["diff"], 1, 100, True),
                     tex_ci(res["precision"]["diff"], 1, 100, True), tex_ci(res["recall"]["diff"], 1, 100, True),
                     f"{res['top20']['none']['est']:.0f} / {res['top20']['cond']['est']:.0f}" if res.get("top20") else "--"])
    (out / "tex" / "tab_esco_main.tex").write_text(tex_table(
        "lrrrrrrr", ["Condition", "False/ad (none)", "False/ad", "Change", "Ads with a false (pts)",
                     "Precision (pts)", "Recall (pts)", "Top-20 off"], rows), encoding="ascii", errors="replace")
    rows = []
    mains = [s for s, n, _ in scopes if n.endswith("(main model alone; not registered)")]
    last_main = mains[-1] if mains else None
    for sid, sname, _ in scopes:
        res = R["cells"]["0.5"].get(sid, {}).get("pooled", {}).get("min_k_shown")
        if not res:
            continue
        rows.append([tex_escape(sname if sid == "main" else model_name(sid)), res["pairs"], tex_ci(res["false"]["none"]), tex_ci(res["false"]["cond"]),
                     tex_ci(res["false"]["diff"], sign=True), tex_ci(res["precision"]["diff"], 1, 100, True)])
        if sid == "main" or sid == last_main:
            rows.append("MIDRULE")
    (out / "tex" / "tab_esco_models.tex").write_text(tex_table(
        "lrrrrr", ["Model", "Pairs", "False/ad (none)", "False/ad (\\cnd{min\\_k\\_shown})", "Change",
                   "Precision (pts)"], rows), encoding="ascii", errors="replace")


if __name__ == "__main__":
    main()
