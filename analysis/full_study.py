#!/usr/bin/env python3
"""full_study.py: every registered test and estimate of the full study (protocol-stage2.md sections 5 and 6).

    python analysis/full_study.py all --runs-dir <folder of fs_* run folders>     score, then tables
    python analysis/full_study.py score --runs-dir <...> [--jobs 3]                per-output tables only
    python analysis/full_study.py tables [--boot 10000]                             from the scored tables

Inputs: the run folders (manifest.json, planned.jsonl, raw*.jsonl, as harness/run.py writes them), scored by
analysis/full_study_score.py with the frozen parser, placeholder rules and v0 matcher into
analysis/full/scored/. Outputs, all in analysis/full/:
  RESULTS.md        every number, in markdown tables, with where it comes from
  REPORT.md         the headline numbers on the 8 main models and what could not be done as written
  tex/*.tex         LaTeX tabulars the paper can \\input (booktabs; \\cnd{} for condition names)
  runs.md           which run folders were found, what kind each is, and the missing-output counts

Runs are recognised by name: fs_<model>_full (the study), _full-repeat (repeat check), _full-reask1 (re-ask
arm), _dev (reserve documents; not part of any test), fs_<model>_think-filters_s<seed> and
fs_bedrock-kimi-k3-think_* (thinking side test). A run kind that is absent is reported as absent; the thinking
tables appear once those folders are copied in. Transport failures and unanswered requests are MISSING and
are left out of every pair (never counted as an output); unreadable outputs are counted (0 entries).

Units. Length change: substantive entries under one condition minus under the other, same model, document
and k. Over-count: share of outputs with more substantive entries than true items, shown in points
(100 x share). Every interval: 95% percentile interval from --boot draws over document groups resampled
within set (the same scheme as harness/score_counts.py's Boot, seed 20261014), with the two-sided bootstrap
p-value 2 x min(share of draws <= 0, share >= 0) where a test is registered.
"""
import argparse
import json
import math
import re
import sys
import warnings
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))
sys.path.insert(0, str(ROOT / "analysis"))
import common  # noqa: E402

OUT = ROOT / "analysis" / "full"
CACHE = OUT / "scored"
SEED = 20261014
SETS = ["meetings", "emails", "receipts", "job_posts", "clinical", "reviews", "job_posts_knowledge",
        "wiki_people", "novel_quotes"]
SET_NAME = {"meetings": "meetings", "emails": "emails", "receipts": "receipts", "job_posts": "job-ad skills",
            "clinical": "clinical", "reviews": "reviews", "job_posts_knowledge": "job-ad knowledge",
            "wiki_people": "Wikipedia people", "novel_quotes": "novel quotes"}
CONDS = ["none", "prose_up_to_k", "prose_exactly_k", "max_k_shown", "min_k_shown", "min_k_shown_fewer_ok",
         "min_k_enforced", "min_k_escape"]
PROMPT_SIDE = CONDS[:6]
NAME = {"qwen3.5-0.8b": "Qwen3.5-0.8B", "qwen3.5-2b": "Qwen3.5-2B", "qwen3.5-9b": "Qwen3.5-9B",
        "qwen3.5-27b": "Qwen3.5-27B", "gemma-4-31b": "Gemma 4 31B", "olmo-3.1-32b": "Olmo 3.1 32B",
        "ministral-3-14b": "Ministral 3 14B", "gpt-oss-20b": "gpt-oss-20b",
        "together-deepseek-v4.1-flash": "DeepSeek V4.1 Flash (Together)",
        "together-qwen3.5-9b": "Qwen3.5-9B (Together)", "bedrock-kimi-k3": "Kimi K3 (Bedrock)",
        "bedrock-deepseek-v3.2": "DeepSeek V3.2 (Bedrock)", "bedrock-qwen3-235b": "Qwen3-235B (Bedrock)",
        "bedrock-mistral-large-3": "Mistral Large 3 (Bedrock)", "bedrock-ministral-3-14b": "Ministral 3 14B (Bedrock)",
        "bedrock-gpt-oss-20b": "gpt-oss-20b (Bedrock)", "bedrock-gpt-oss-120b": "gpt-oss-120b (Bedrock)"}
PAIRS = [("together-qwen3.5-9b", "qwen3.5-9b"), ("bedrock-ministral-3-14b", "ministral-3-14b"),
         ("bedrock-gpt-oss-20b", "gpt-oss-20b")]
SORTS = ["padded", "says_short", "honest_short", "unreadable"]


# ---------------------------------------------------------------------------------------------------------
# configuration
def lineup():
    import yaml
    cfg = yaml.safe_load((ROOT / "configs" / "models.yaml").read_text(encoding="utf-8"))
    fs = cfg["full_study"]
    main = list(fs["gpu"]["main"])
    hosted = list(fs["together"]["models"]) + list(fs["bedrock"]["models"])
    family = {m: cfg["models"][m].get("family", m) for m in main}
    think_pairs = [(p["think"], p["partner"]) for p in fs["gpu"]["thinking_pairs"]]
    think_pairs.append((fs["bedrock"]["kimi_k3_thinking"]["key"], "bedrock-kimi-k3"))
    return main, hosted, family, think_pairs


def run_kind(run_id):
    if re.search(r"_full$", run_id):
        return "full"
    if run_id.endswith("_full-repeat"):
        return "repeat"
    if run_id.endswith("_full-reask1"):
        return "reask"
    if run_id.endswith("_dev"):
        return "dev"
    if re.search(r"_think-filters_s\d+$", run_id) or "-think_" in run_id:
        return "think"
    return "other"


# ---------------------------------------------------------------------------------------------------------
# bootstrap: score_counts.Boot generalised to several sums per group (same draws for the same input)
class Bootstrap:
    def __init__(self, boot=10000, seed=SEED):
        self.boot, self.seed = boot, seed

    def stat(self, per_group, strata, fn):
        """per_group: {group: vector of sums}; strata: {group: set}; fn maps summed vectors (last axis) to the
        statistic. Returns (estimate, low, high, two-sided p, number of groups)."""
        groups = list(per_group)
        if not groups:
            return None
        M = np.array([np.asarray(per_group[g], float) for g in groups])
        est = float(fn(M.sum(axis=0)))
        by_set = defaultdict(list)
        for i, g in enumerate(groups):
            by_set[strata[g]].append(i)
        rng = np.random.default_rng(self.seed)
        tot = np.zeros((self.boot, M.shape[1]))
        for idx in by_set.values():
            idx = np.array(idx)
            pick = idx[rng.integers(0, len(idx), (self.boot, len(idx)))]
            for j in range(M.shape[1]):
                tot[:, j] += M[pick, j].sum(axis=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            draws = np.asarray(fn(tot), float)
        draws = np.sort(draws[np.isfinite(draws)])
        if not len(draws):
            return None
        lo, hi = float(draws[int(0.025 * len(draws))]), float(draws[int(0.975 * len(draws)) - 1])
        p = float(min(1.0, 2 * min((draws <= 0).mean(), (draws >= 0).mean())))
        return {"est": est, "lo": lo, "hi": hi, "p": p, "groups": len(groups)}

    def mean(self, frame, col="diff"):
        """Mean of `col` over rows (pairs), resampling document groups within set."""
        if frame is None or not len(frame):
            return None
        g = frame.groupby("group", sort=True, observed=True).agg(s=(col, "sum"), c=(col, "size"), set=("set", "first"))
        res = self.stat({k: (r.s, r.c) for k, r in g.iterrows()}, g["set"].to_dict(),
                        lambda v: v[..., 0] / np.maximum(v[..., 1], 1))
        if res:
            res["pairs"] = int(len(frame))
        return res

    def diff_of_means(self, fa, fb, col="diff"):
        """mean(fa) - mean(fb), both resampled together by group."""
        if fa is None or fb is None or not len(fa) or not len(fb):
            return None
        ga = fa.groupby("group", observed=True).agg(s=(col, "sum"), c=(col, "size"), set=("set", "first"))
        gb = fb.groupby("group", observed=True).agg(s=(col, "sum"), c=(col, "size"), set=("set", "first"))
        groups = sorted(set(ga.index) | set(gb.index))
        strata = {**ga["set"].to_dict(), **gb["set"].to_dict()}
        per = {g: (ga.s.get(g, 0.0), ga.c.get(g, 0), gb.s.get(g, 0.0), gb.c.get(g, 0)) for g in groups}
        res = self.stat(per, strata, lambda v: v[..., 0] / np.maximum(v[..., 1], 1) - v[..., 2] / np.maximum(v[..., 3], 1))
        if res:
            res["pairs"] = int(len(fa) + len(fb))
        return res

    def model_weighted(self, frame, weights, col="diff"):
        """sum_m weights[m] x mean of model m (family-weighted estimate)."""
        models = list(weights)
        frame = frame[frame.model_key.isin(models)]
        if not len(frame):
            return None
        per, strata = defaultdict(lambda: np.zeros(2 * len(models))), {}
        for (g, m), sub in frame.groupby(["group", "model_key"], observed=True):
            j = models.index(m)
            per[g][2 * j] += sub[col].sum()
            per[g][2 * j + 1] += len(sub)
            strata[g] = sub["set"].iloc[0]
        w = np.array([weights[m] for m in models])

        def fn(v):
            means = v[..., 0::2] / np.maximum(v[..., 1::2], 1)
            return (means * w).sum(axis=-1)
        res = self.stat(dict(sorted(per.items())), strata, fn)
        if res:
            res["pairs"] = int(len(frame))
        return res


def holm(ps):
    """Holm step-down adjusted p-values, in the input order."""
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [None] * len(ps), 0.0
    for rank, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - rank) * ps[i]))
        adj[i] = run
    return adj


# ---------------------------------------------------------------------------------------------------------
# loading
OUT_DTYPES = {"k": "int8", "n": "int8", "n_items": "float32", "n_substantive": "float32", "n_placeholder": "float32",
              "n_escape": "float32", "n_duplicate": "float32", "n_subst_bound": "float32", "excess": "float32",
              "matched_gold": "float32", "left_out": "float32", "n_true": "float32", "n_split": "float32",
              "n_wrong_type": "float32", "n_invented": "float32", "n_invented_note": "float32",
              "reasoning_chars": "float32"}
BOOLS = ["valid", "over_count", "exact_k", "fewer_than_k", "more_than_k", "exact_n", "truncated", "outside_note",
         "shortfall_phrase", "enforce_schema", "text_outside_json"]
CATS = ["run_id", "model_key", "arm", "doc_id", "group", "set", "split", "condition", "wording_id", "status",
        "finish_reason", "parse_rung", "sort"]


def doc_table():
    """Per study document: words, the annotators' count (n_src) and whether the cleanup changed the list."""
    import answer_key_vs_source as aks
    docs = common.load_documents()
    rows = []
    for doc_id, s, split, n_src, n_clean, status, _, _ in aks.study_documents():
        d = docs.get(doc_id, {})
        rows.append({"doc_id": doc_id, "n_src": int(n_src), "n_clean": int(n_clean),
                     "list_changed": status != "ok", "words": float(d.get("words") or 0)})
    overlay = ROOT / "analysis" / "gold_overlay.jsonl"
    delta = defaultdict(int)
    if overlay.exists():
        for r in common.read_jsonl(overlay):
            delta[r["doc_id"]] += -1 if r.get("op") == "remove" else 1
    t = pd.DataFrame(rows).set_index("doc_id")
    t["n_overlay"] = t["n_clean"] + pd.Series(delta, dtype=float).reindex(t.index).fillna(0).astype(int)
    t.attrs["overlay_rows"] = sum(abs(v) for v in delta.values())
    t.attrs["overlay_exists"] = overlay.exists()
    return t


def load_scored(cache=CACHE):
    frames, meta = [], []
    for p in sorted(Path(cache).glob("*.outputs.csv.gz")):
        rid = p.name[: -len(".outputs.csv.gz")]
        m = json.loads((Path(cache) / f"{rid}.source.json").read_text())
        meta.append(m)
        f = pd.read_csv(p, dtype={"wording_id": str, "source_request_id": str, "request_seed": str, "sort": str,
                                  "finish_reason": str, "parse_rung": str, **{c: str for c in BOOLS}},
                        keep_default_na=False, na_values=[""])
        for c in BOOLS:
            if c in f:
                f[c] = f[c].map({"True": True, "False": False, True: True, False: False})
        f["kind"] = run_kind(rid)
        frames.append(f)
    df = pd.concat(frames, ignore_index=True)
    for c, t in OUT_DTYPES.items():
        df[c] = pd.to_numeric(df[c], errors="coerce").astype(t)
    for c in CATS + ["kind"]:
        df[c] = df[c].astype("category")
    return df, meta


def add_doc_fields(df, docs):
    df = df.join(docs[["n_src", "list_changed", "words", "n_overlay"]], on="doc_id")
    df["ok"] = df["status"] == "ok"
    df["slot_fill"] = np.where(df["k"] > df["n"], df["excess"] / (df["k"] - df["n"]).clip(lower=1), np.nan)
    df["has_entry"] = (df["n_substantive"] >= 1).astype("float32")
    df["left_share"] = np.where(df["n"] > 0, df["left_out"] / df["n"].clip(lower=1), np.nan)
    df["over_bound"] = (df["valid"].fillna(False) & (df["n_subst_bound"] > df["n"])).astype("float32")
    df["over_src"] = (df["valid"].fillna(False) & (df["n_substantive"] > df["n_src"])).astype("float32")
    df["over_overlay"] = (df["valid"].fillna(False) & (df["n_substantive"] > df["n_overlay"])).astype("float32")
    for c in ("over_count", "exact_k", "fewer_than_k", "more_than_k", "exact_n", "valid", "truncated"):
        df[c] = df[c].astype("float32")
    return df


# ---------------------------------------------------------------------------------------------------------
# pairs
def cell_mask(f, cell, nfield):
    if cell == "lt":
        return f[nfield] < f["k"]
    if cell == "ge":
        return f[nfield] >= f["k"]
    if cell == "lt_n0":
        return (f[nfield] < f["k"]) & (f[nfield] == 0)
    if cell == "lt_n1":
        return (f[nfield] < f["k"]) & (f[nfield] >= 1)
    return pd.Series(True, index=f.index)


def paired(f, a, b, outcome="n_substantive", ks=(3, 5), cell="lt", nfield="n"):
    """a - b per (model, document, k); a condition's wordings are averaged first (prose conditions).
    Only ok outputs; a pair needs both sides."""
    sel = f[f["ok"] & f["condition"].isin([a, b]) & f["k"].isin(ks)]
    sel = sel[cell_mask(sel, cell, nfield)]
    if not len(sel):
        return None
    g = sel.groupby(["model_key", "doc_id", "k", "condition"], observed=True)[outcome].mean().unstack("condition")
    if a not in g or b not in g:
        return None
    g = g.dropna(subset=[a, b])
    out = pd.DataFrame({"diff": (g[a] - g[b]).astype(float)}).reset_index()
    info = sel.drop_duplicates("doc_id").set_index("doc_id")[["group", "set", "split", "n", "n_src", "words",
                                                                "list_changed"]]
    return out.join(info, on="doc_id")


def dose_pairs(f, outcome="n_substantive", max_n=2, nfield="n"):
    """Contrast 1: min_k_shown at k = 5 minus k = 3, same document, n at most 2."""
    sel = f[f["ok"] & (f["condition"] == "min_k_shown") & f["k"].isin((3, 5)) & (f[nfield] <= max_n)]
    if not len(sel):
        return None
    g = sel.groupby(["model_key", "doc_id", "k"], observed=True)[outcome].mean().unstack("k").dropna()
    if 3 not in g or 5 not in g:
        return None
    out = pd.DataFrame({"diff": (g[5] - g[3]).astype(float)}).reset_index()
    out["k"] = 5
    info = sel.drop_duplicates("doc_id").set_index("doc_id")[["group", "set", "split", "n", "n_src", "words",
                                                                "list_changed"]]
    return out.join(info, on="doc_id")


CONFIRMATORY = [
    ("C1", "Dose: min_k_shown, k = 5 vs k = 3 (n at most 2)", "dose", None),
    ("C2", "min_k_shown vs none (main measure)", "min_k_shown", "none"),
    ("C3", "min_k_shown vs max_k_shown", "min_k_shown", "max_k_shown"),
    ("C4", "prose_exactly_k vs prose_up_to_k (5 wordings averaged)", "prose_exactly_k", "prose_up_to_k"),
    ("C5", "min_k_escape vs min_k_enforced (substantive extra entries per padded slot)", "min_k_escape", "min_k_enforced"),
]


def contrast_pairs(f, cid, outcome=None, nfield="n", cell="lt"):
    _, _, a, b = next(c for c in CONFIRMATORY if c[0] == cid)
    if cid == "C1":
        return dose_pairs(f, outcome or "n_substantive", nfield=nfield)
    if cid == "C5":
        return paired(f, a, b, outcome or "slot_fill", cell=cell, nfield=nfield)
    return paired(f, a, b, outcome or "n_substantive", cell=cell, nfield=nfield)


# ---------------------------------------------------------------------------------------------------------
# mixed models (next to the primary bootstrap test)
def mixed_lmm(pairs):
    """Linear mixed model of the paired difference ~ n + model + set + words + (1 | document); covariates
    centred and factors sum-coded, so the intercept is the average difference. Drops words, then set, if the
    fit fails or does not converge. Returns (estimate, low, high, p, formula) or None."""
    import statsmodels.formula.api as smf
    if pairs is None or len(pairs) < 20:
        return None
    d = pairs.copy()
    d["model_key"], d["set"] = d["model_key"].astype(str), d["set"].astype(str)
    d["n_c"] = d["n"] - d["n"].mean()
    d["words_c"] = (d["words"] - d["words"].mean()) / 100.0
    terms = ["n_c", "C(model_key, Sum)", "C(set, Sum)", "words_c"]
    for drop in (None, "words_c", "C(set, Sum)"):
        if drop:
            terms = [t for t in terms if t != drop]
        use = [t for t in terms if not (t.startswith("C(model_key") and d["model_key"].nunique() < 2)
               and not (t.startswith("C(set") and d["set"].nunique() < 2)]
        formula = "diff ~ " + " + ".join(use)
        for method in ("lbfgs", "powell", "cg"):        # optimisers in turn, then the smaller model
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    fit = smf.mixedlm(formula, d, groups=d["doc_id"].astype(str)).fit(reml=True, method=method)
                if not fit.converged:
                    continue
                b, se = fit.params["Intercept"], fit.bse["Intercept"]
                return {"est": float(b), "lo": float(b - 1.96 * se), "hi": float(b + 1.96 * se),
                        "p": float(fit.pvalues["Intercept"]),
                        "formula": formula + f" + (1 | document), REML, optimiser {method}"}
            except Exception:  # noqa: BLE001  (a singular fit: next optimiser)
                continue
    return None


def mixed_poisson(f, models):
    """Contrast 5: Poisson mixed model of the substantive extra entries per output, escape vs enforced, with
    n, model, set, words and log(padded slots) as fixed effects and a random intercept per document.
    Variational-Bayes fit (statsmodels PoissonBayesMixedGLM); returns the rate ratio for escape."""
    from statsmodels.genmod.bayes_mixed_glm import PoissonBayesMixedGLM
    sel = f[f["ok"] & f["condition"].isin(["min_k_escape", "min_k_enforced"]) & f["k"].isin((3, 5))
            & (f["n"] < f["k"]) & f["model_key"].isin(models)].copy()
    if len(sel) < 50:
        return None
    sel["escape"] = (sel["condition"] == "min_k_escape").astype(float)
    sel["n_c"] = sel["n"] - sel["n"].mean()
    sel["words_c"] = (sel["words"] - sel["words"].mean()) / 100.0
    sel["log_slots"] = np.log((sel["k"] - sel["n"]).astype(float))
    sel["y"] = sel["excess"].astype(float)
    sel["doc"] = sel["doc_id"].astype(str)
    sel["model_key"], sel["set"] = sel["model_key"].astype(str), sel["set"].astype(str)
    for model in ("escape + n_c + C(model_key, Sum) + C(set, Sum) + words_c + log_slots",
                  "escape + n_c + C(model_key, Sum) + C(set, Sum) + log_slots",
                  "escape + n_c + C(model_key, Sum) + log_slots"):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                m = PoissonBayesMixedGLM.from_formula("y ~ " + model, {"doc": "0 + C(doc)"}, sel)
                fit = m.fit_vb()
            names = list(m.exog_names)
            i = names.index("escape")
            b, sd = fit.fe_mean[i], fit.fe_sd[i]
            if not np.isfinite(b) or not np.isfinite(sd):
                continue
            return {"est": float(math.exp(b)), "lo": float(math.exp(b - 1.96 * sd)), "hi": float(math.exp(b + 1.96 * sd)),
                    "formula": "y ~ " + model + " + (1 | document), Poisson, variational Bayes"}
        except Exception:  # noqa: BLE001
            continue
    return None


# ---------------------------------------------------------------------------------------------------------
# formatting
def fmt(r, scale=1.0, nd=2, sign=True):
    if not r:
        return "--"
    s = "+" if sign else ""
    return f"{scale * r['est']:{s}.{nd}f} [{scale * r['lo']:{s}.{nd}f}, {scale * r['hi']:{s}.{nd}f}]"


def fmt_p(p):
    if p is None:
        return "--"
    return "< 0.0001" if p < 1e-4 else f"{p:.4f}"


def pts(r):
    return fmt(r, 100, 1)


def tex_escape(s):
    s = str(s).replace("_", "\\_").replace("%", "\\%").replace("&", "\\&")
    return s.replace(">=", "$\\geq$").replace("<", "$<$")


def cnd(c):
    return "\\cnd{" + c.replace("_", "\\_") + "}"


def md_table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join(str(x) for x in r) + " |" for r in rows]
    return out


def tex_table(cols, head, rows):
    out = ["\\begin{tabular}{" + cols + "}", "  \\toprule", "  " + " & ".join(head) + " \\\\", "  \\midrule"]
    for r in rows:
        if r == "MIDRULE":
            out.append("  \\midrule")
        else:
            out.append("  " + " & ".join(str(x) for x in r) + " \\\\")
    out += ["  \\bottomrule", "\\end{tabular}"]
    return "\n".join(out) + "\n"


def tex_ci(r, scale=1.0, nd=2):
    if not r:
        return "--"
    return (f"${scale * r['est']:+.{nd}f}$ [${scale * r['lo']:+.{nd}f}$, ${scale * r['hi']:+.{nd}f}$]"
            .replace("+-", "-"))


# ---------------------------------------------------------------------------------------------------------
class Study:
    def __init__(self, df, meta, boot, docs):
        self.main, self.hosted, self.family, self.think_pairs = lineup()
        self.df, self.meta, self.B, self.docs = df, meta, Bootstrap(boot), docs
        self.full = df[(df["kind"] == "full") & (df["arm"] == "main")]
        self.gpu = self.full[self.full["model_key"].isin(self.main)]
        self.present_main = [m for m in self.main if m in set(self.gpu["model_key"].unique())]
        self.present_hosted = [m for m in self.hosted if m in set(self.full["model_key"].unique())]
        self.md, self.tex, self.head = [], {}, {}

    # ---- helpers
    def model_rows(self, model):
        return self.full[self.full["model_key"] == model]

    def sec(self, title, *lines):
        self.md += ["", f"## {title}", "", *lines]

    # ---- 0. runs
    def runs_section(self):
        rows = []
        for m in sorted(self.meta, key=lambda x: x["run_id"]):
            sub = self.df[self.df["run_id"] == m["run_id"]]
            rows.append([m["run_id"], run_kind(m["run_id"]), m["model_key"], len(sub), int(sub["ok"].sum()),
                         int((~sub["ok"]).sum())])
        lines = ["# Run folders scored", "",
                 "One row per run folder. Rows = covered request ids (the `none` answer covers k = 1, 3, 5). "
                 "Missing = transport failures and requests never answered: left out of every pair, never outputs.", ""]
        lines += md_table(["run", "kind", "model", "rows", "ok", "missing"], rows)
        missing_think = [p for p in self.think_pairs
                         if not any(run_kind(m["run_id"]) == "think" and m["model_key"] in p for m in self.meta)]
        lines += ["", "Thinking-pair runs not present yet: " +
                  (", ".join(f"{a} / {b}" for a, b in missing_think) or "none")]
        (OUT / "runs.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        self.head["missing_main"] = {m: int((~self.model_rows(m)["ok"]).sum()) for m in self.present_main}

    # ---- 1. confirmatory
    def confirmatory(self):
        f = self.gpu
        res, rows_md, rows_tex = {}, [], []
        for cid, label, a, b in CONFIRMATORY:
            pr = contrast_pairs(f, cid)
            r = self.B.mean(pr)
            r_np = self.B.mean(pr[pr["split"] != "pilot"]) if pr is not None else None
            mm = mixed_lmm(pr) if cid != "C5" else mixed_poisson(f, self.present_main)
            oc = None if cid == "C5" else self.B.mean(contrast_pairs(f, cid, "over_count"))
            res[cid] = {"r": r, "no_pilot": r_np, "mixed": mm, "over": oc, "pairs": pr}
        ps = [res[c]["r"]["p"] if res[c]["r"] else 1.0 for c, *_ in CONFIRMATORY]
        adj = holm(ps)
        for (cid, label, a, b), pa in zip(CONFIRMATORY, adj):
            x = res[cid]
            x["holm"] = pa
            unit = "rate ratio" if cid == "C5" else "entries"
            rows_md.append([cid, label, fmt(x["r"]), fmt_p(x["r"]["p"] if x["r"] else None), fmt_p(pa),
                            x["r"]["pairs"] if x["r"] else 0, x["r"]["groups"] if x["r"] else 0, fmt(x["no_pilot"]),
                            (fmt(x["mixed"]) if cid != "C5" else fmt(x["mixed"], sign=False)) + f" ({unit})",
                            pts(x["over"]) if x["over"] else "--"])
            rows_tex.append([cid.replace("C", ""), tex_escape(label), tex_ci(x["r"]), tex_escape(fmt_p(pa)), tex_ci(x["no_pilot"]),
                             tex_ci(x["mixed"]) if cid != "C5" else (f"{x['mixed']['est']:.2f} [{x['mixed']['lo']:.2f}, {x['mixed']['hi']:.2f}]"
                                                                     if x["mixed"] else "--"),
                             tex_ci(x["over"], 100, 1) if x["over"] else "--"])
        self.res_conf = res
        self.sec("1. Confirmatory contrasts (8 main models pooled, documents with n < k, k = 3 and 5; Holm across the five)",
                 "Primary test: the 95% bootstrap interval of the mean paired difference over documents and models, "
                 "and its two-sided bootstrap p-value (Holm-adjusted across the five). Contrasts 1 to 4: length change "
                 "in substantive entries. Contrast 5: substantive extra entries per padded slot (excess / (k - n) per "
                 "output). Next to it: the mixed model (contrasts 1-4: LMM of the paired difference, intercept = "
                 "average difference; contrast 5: Poisson mixed model, rate ratio for the escape), the same test "
                 "without the 60 pilot documents, and over-count (points) for contrasts 1 to 4.", "",
                 *md_table(["#", "contrast", "estimate [95% CI]", "p", "Holm p", "pairs", "groups", "without pilot docs",
                            "mixed model", "over-count (points)"], rows_md))
        for cid, *_ in CONFIRMATORY:
            if res[cid]["mixed"]:
                self.md.append(f"- {cid} mixed model: `{res[cid]['mixed']['formula']}`")
        self.tex["tab_confirmatory.tex"] = tex_table(
            "rlrrrrr", ["\\#", "Contrast", "Estimate [95\\% CI]", "Holm $p$", "Without pilot", "Mixed model",
                        "Over-count (pts)"], rows_tex)
        # n = 0 apart from n = 1 to 3
        rows = []
        for cid, label, a, b in CONFIRMATORY:
            pr = res[cid]["pairs"]
            if pr is None:
                continue
            rows.append([cid, fmt(self.B.mean(pr[pr["n"] == 0])), fmt(self.B.mean(pr[pr["n"] >= 1]))])
        self.sec("1a. Confirmatory contrasts, n = 0 apart from n >= 1 (section 6.1)",
                 *md_table(["#", "n = 0", "n = 1 to 4 (n < k)"], rows))
        self.head["confirmatory"] = {c: res[c]["r"] for c, *_ in CONFIRMATORY}
        self.head["confirmatory_holm"] = {c: res[c]["holm"] for c, *_ in CONFIRMATORY}
        self.head["c2_over"] = res["C2"]["over"]

    # ---- 2. per model, per set
    def per_model(self, models, title, texname, contrasts=("C1", "C2", "C3", "C4", "C5")):
        rows, trows = [], []
        for m in models:
            f = self.model_rows(m)
            cells = []
            for cid in contrasts:
                cells.append(self.B.mean(contrast_pairs(f, cid)))
            rows.append([NAME.get(m, m), *[fmt(c) for c in cells]])
            trows.append([tex_escape(NAME.get(m, m)), *[tex_ci(c) for c in cells]])
            if title.startswith("2."):
                self.head.setdefault("per_model_c2", {})[m] = cells[contrasts.index("C2")]
        if title.startswith("2."):
            pooled = [self.res_conf[c]["r"] for c in contrasts]
            rows.append(["8 models pooled", *[fmt(c) for c in pooled]])
            trows += ["MIDRULE", ["Pooled", *[tex_ci(c) for c in pooled]]]
        self.sec(title, *md_table(["model", *contrasts], rows))
        self.tex[texname] = tex_table("l" + "r" * len(contrasts), ["Model", *contrasts], trows)

    def per_set(self):
        rows, trows = [], []
        for s in SETS:
            f = self.gpu[self.gpu["set"] == s]
            cells = [self.B.mean(contrast_pairs(f, cid)) for cid, *_ in CONFIRMATORY]
            oc = self.B.mean(contrast_pairs(f, "C2", "over_count"))
            rows.append([SET_NAME[s], *[fmt(c) for c in cells], pts(oc)])
            trows.append([SET_NAME[s], *[tex_ci(c) for c in cells], tex_ci(oc, 100, 1)])
        self.sec("3. Per set (8 main models pooled)", "Same contrasts as section 1; the last column is contrast 2 on "
                 "over-count (points). Job-ad skills is the least certain answer list (protocol 4.1).", "",
                 *md_table(["set", "C1", "C2", "C3", "C4", "C5", "C2 over-count"], rows))
        self.tex["tab_per_set.tex"] = tex_table("lrrrrrr", ["Set", "C1", "C2", "C3", "C4", "C5", "C2 over-count"], trows)

    # ---- 3. named tests
    def named(self, models=None, tag="main"):
        f = self.gpu if models is None else self.full[self.full["model_key"].isin(models)]
        out = {}
        out["fewer_vs_none"] = self.B.mean(paired(f, "min_k_shown_fewer_ok", "none"))
        out["fewer_vs_shown"] = self.B.mean(paired(f, "min_k_shown_fewer_ok", "min_k_shown"))
        out["fewer_over_vs_none"] = self.B.mean(paired(f, "min_k_shown_fewer_ok", "none", "over_count"))
        out["max_vs_none"] = self.B.mean(paired(f, "max_k_shown", "none"))
        ge, lt = {}, {}
        for k in (1, 3, 5):
            ge[k] = paired(f, "min_k_shown", "none", ks=(k,), cell="ge")
            lt[k] = paired(f, "min_k_shown", "none", ks=(k,), cell="lt")
        ge_all = pd.concat([x for x in ge.values() if x is not None]) if any(x is not None for x in ge.values()) else None
        out["enough"] = self.B.mean(ge_all)
        out["enough_left"] = self.B.mean(paired(f, "min_k_shown", "none", "left_share", ks=(1, 3, 5), cell="ge"))
        out["enough_by_k"] = {k: (self.B.mean(ge[k]), self.B.mean(lt[k]), self.B.diff_of_means(lt[k], ge[k]))
                              for k in (1, 3, 5)}
        lt35 = pd.concat([x for x in (lt[3], lt[5]) if x is not None]) if lt[3] is not None or lt[5] is not None else None
        ge35 = pd.concat([x for x in (ge[3], ge[5]) if x is not None]) if ge[3] is not None or ge[5] is not None else None
        out["slot_part_35"] = self.B.diff_of_means(lt35, ge35)
        out["empty"] = {c: self.B.mean(paired(f, c, "none", "has_entry", ks=(1,), cell="lt_n0"))
                        for c in CONDS[1:]}
        e0 = f[f["ok"] & (f["k"] == 1) & (f["n"] == 0)]
        out["empty_rate"] = {c: float(e0[e0["condition"] == c]["has_entry"].mean()) if len(e0[e0["condition"] == c]) else None
                             for c in CONDS}
        return out

    def named_section(self):
        r = self.named()
        self.res_named = r
        rows = [["fewer is fine: min_k_shown_fewer_ok vs none (length)", fmt(r["fewer_vs_none"]), fmt_p(r["fewer_vs_none"]["p"] if r["fewer_vs_none"] else None)],
                ["fewer is fine: min_k_shown_fewer_ok vs min_k_shown (length)", fmt(r["fewer_vs_shown"]), fmt_p(r["fewer_vs_shown"]["p"] if r["fewer_vs_shown"] else None)],
                ["fewer is fine: min_k_shown_fewer_ok vs none (over-count, points)", pts(r["fewer_over_vs_none"]), "--"],
                ["maxItems: max_k_shown vs none (length)", fmt(r["max_vs_none"]), fmt_p(r["max_vs_none"]["p"] if r["max_vs_none"] else None)],
                ["enough items (n >= k, k = 1, 3, 5): min_k_shown vs none (length)", fmt(r["enough"]), fmt_p(r["enough"]["p"] if r["enough"] else None)],
                ["enough items: min_k_shown vs none (share of true items left out, points)", pts(r["enough_left"]), "--"],
                ["part of the effect from filling missing slots, k = 3 and 5: change on n < k minus on n >= k", fmt(r["slot_part_35"]), "--"]]
        for k, (g, l, d) in r["enough_by_k"].items():
            rows.append([f"enough items, k = {k}: n >= k {fmt(g)}; n < k {fmt(l)}; difference (n < k minus n >= k)", fmt(d), "--"])
        for c, x in r["empty"].items():
            rows.append([f"empty document, k = 1 (n = 0): {c} vs none, share with at least one entry (points)", pts(x),
                         fmt_p(x["p"] if x else None)])
        self.sec("4. Named tests (section 6.3; 8 main models pooled; outside the Holm family)",
                 "Shares with at least one substantive entry on the 105 empty documents at k = 1: " +
                 "; ".join(f"{c} {100 * v:.1f}%" for c, v in r["empty_rate"].items() if v is not None), "",
                 *md_table(["test", "estimate [95% CI]", "p (unadjusted)"], rows))
        def math_bounds(s):  # interval bounds in math mode, so LaTeX sets proper minus signs
            return re.sub(r"\[([+-]?[\d.]+), ([+-]?[\d.]+)\]", r"[$\1$, $\2$]", s)

        trows = [[math_bounds(tex_escape(x[0])), math_bounds(x[1])] for x in rows]
        self.tex["tab_named.tex"] = tex_table("lr", ["Named test", "Estimate [95\\% CI]"], trows)
        # per model
        prow = []
        for m in self.present_main:
            x = self.named([m])
            prow.append([NAME[m], fmt(x["fewer_vs_none"]), fmt(x["fewer_vs_shown"]), fmt(x["max_vs_none"]),
                         fmt(x["enough"]), fmt(x["slot_part_35"]), pts(x["empty"]["min_k_shown"])])
        self.sec("4a. Named tests per main model",
                 *md_table(["model", "fewer_ok vs none", "fewer_ok vs min_k_shown", "max vs none", "n >= k: shown vs none",
                            "slot-filling part (k 3, 5)", "empty k = 1: shown vs none (points)"], prow))
        self.head["named"] = r

    # ---- 4. secondary outcomes
    def outcomes(self, models, title_suffix=""):
        f = self.full[self.full["model_key"].isin(models) & self.full["ok"]]
        lt = f[(f["n"] < f["k"]) & f["k"].isin((3, 5))]
        rows = []
        for c in CONDS:
            sub = lt[lt["condition"] == c]
            if not len(sub):
                continue
            pos = f[(f["condition"] == c) & (f["n"] >= 1) & f["k"].isin((3, 5))]
            rows.append([c, len(sub), f"{100 * sub['over_count'].mean():.1f}", f"{100 * sub['over_bound'].mean():.1f}",
                         f"{sub['excess'].mean():.2f}", f"{100 * (1 - sub['valid'].mean()):.1f}",
                         f"{100 * sub['fewer_than_k'].mean():.1f}", f"{100 * sub['exact_k'].mean():.1f}",
                         f"{100 * sub['more_than_k'].mean():.1f}", f"{100 * sub['exact_n'].mean():.1f}",
                         f"{100 * pos['left_out'].sum() / max(1, pos['n'].sum()):.1f}"])
        return rows

    def outcomes_section(self):
        head = ["condition", "outputs (n < k)", "over-count %", "over-count %, placeholder bound", "excess",
                "unreadable %", "fewer than k %", "exactly k %", "more than k %", "exactly n %",
                "true items left out % (n >= 1)"]
        self.sec("5. Over-count, excess, length distribution and true items left out (8 main models pooled, k = 3 and 5)",
                 "Over-count, excess and the length distribution on documents with n < k; true items left out on "
                 "documents with n >= 1 (any n vs k), share of their true items no entry matches (matcher true-item "
                 "and split labels). Placeholder bound: every substantive entry of 8 words or fewer holding no, none, "
                 "not, only, other, additional or found taken as a note.", "",
                 *md_table(head, self.outcomes(self.present_main)))
        rows = []
        for m in self.present_main:
            for r in self.outcomes([m]):
                rows.append([NAME[m], *r])
        self.sec("5a. The same per main model", *md_table(["model", *head], rows))
        urows = []
        for m in self.present_main + self.present_hosted:
            f = self.model_rows(m)
            f = f[f["ok"]]
            bad = f[f["valid"] == 0]
            json_no_list = bad[bad["parse_rung"].astype(str) != "failed"]
            urows.append([NAME.get(m, m), len(f), len(bad), f"{100 * len(bad) / max(1, len(f)):.1f}", len(json_no_list),
                          int(bad["truncated"].sum())])
        self.sec("5b. Unreadable outputs, all conditions and k",
                 "JSON read but no answer list = the parse ladder found JSON but no list it may take as the answer; "
                 "almost always the answer written inside a copy of the schema, which the frozen rules never take "
                 "(protocol 5.1). Cut at the token limit = finish_reason length.", "",
                 *md_table(["model", "ok outputs", "unreadable", "unreadable %", "JSON read but no answer list",
                            "cut at the token limit"], urows))
        self.head["unreadable"] = {r[0]: r[3] for r in urows}
        trows = []
        for r in self.outcomes(self.present_main):
            trows.append([cnd(r[0]), r[2], r[3], r[4], r[5], r[7], r[10]])
        self.tex["tab_outcomes.tex"] = tex_table("lrrrrrr", ["Condition", "Over-count \\%", "Bound \\%", "Excess",
                                                             "Unreadable \\%", "Exactly $k$ \\%", "Left out \\%"], trows)

    def sorting_section(self, models, title, texname=None):
        f = self.full[self.full["model_key"].isin(models) & self.full["ok"]]
        f = f[(f["n"] < f["k"]) & f["k"].isin((3, 5))]
        rows, trows = [], []
        for c in CONDS:
            sub = f[f["condition"] == c]
            if not len(sub):
                continue
            share = sub["sort"].value_counts(normalize=True)
            vals = [f"{100 * share.get(s, 0.0):.1f}" for s in SORTS]
            rows.append([c, len(sub), *vals])
            trows.append([cnd(c), *vals])
        self.sec(title, "Each output on a document with n < k (k = 3 and 5) sorted as padded (more substantive "
                 "entries than n; wins over a note), says it is short (not padded; a placeholder, an N/A or a note "
                 "outside the list), honest short list, or unreadable. Shares in %.", "",
                 *md_table(["condition", "outputs", *SORTS], rows))
        if texname:
            self.tex[texname] = tex_table("lrrrr", ["Condition", "Padded", "Says short", "Honest short", "Unreadable"], trows)
        return rows

    def sorting_per_model(self):
        rows = []
        for m in self.present_main:
            f = self.model_rows(m)
            f = f[f["ok"] & (f["n"] < f["k"]) & f["k"].isin((3, 5))]
            for c in ("none", "min_k_shown", "min_k_shown_fewer_ok", "max_k_shown", "min_k_enforced"):
                sub = f[f["condition"] == c]
                if len(sub):
                    sh = sub["sort"].value_counts(normalize=True)
                    rows.append([NAME[m], c, *[f"{100 * sh.get(s, 0.0):.1f}" for s in SORTS]])
        self.sec("6a. Sorting per main model (selected conditions)", *md_table(["model", "condition", *SORTS], rows))

    def fills_section(self, models, title):
        f = self.full[self.full["model_key"].isin(models) & self.full["ok"] & self.full["valid"].astype(bool)]
        f = f[(f["n"] < f["k"]) & f["k"].isin((3, 5))]
        rows = []
        for c in ("none", "max_k_shown", "min_k_shown", "min_k_shown_fewer_ok", "min_k_enforced", "min_k_escape"):
            sub = f[f["condition"] == c]
            if not len(sub):
                continue
            extra = float((sub["n_split"] + sub["n_wrong_type"] + sub["n_invented"]).sum())
            ent = float(sub["n_items"].sum())
            rows.append([c, int(extra), *(f"{100 * float(sub[col].sum()) / max(1.0, extra):.1f}"
                                         for col in ("n_split", "n_wrong_type")),
                         f"{100 * float((sub['n_invented'] - sub['n_invented_note']).sum()) / max(1.0, extra):.1f}",
                         f"{100 * float(sub['n_invented_note'].sum()) / max(1.0, extra):.1f}",
                         f"{100 * float(sub['n_placeholder'].sum()) / max(1.0, ent):.1f}",
                         f"{100 * float(sub['n_duplicate'].sum()) / max(1.0, ent):.1f}"])
        self.sec(title, "Matcher v0 labels of the extra entries (substantive entries not matched to a distinct true "
                 "item) on documents with n < k, k = 3 and 5. These are the matcher's calls, not checked yet: an "
                 "invented share is stated in the paper only with the authors' matcher check (5.3 b, C11). The matcher "
                 "v0 does not decide missed_gold or beyond_excerpt (see REPORT.md). Placeholder and repeat shares are "
                 "of all list entries.", "",
                 *md_table(["condition", "extra entries", "split or restated true item %", "real text, wrong kind %",
                            "invented %", "invented: prompt echo or possible note %", "placeholder % of entries",
                            "repeat % of entries"], rows))
        return rows

    # ---- 5. answer-key variants
    def key_variants(self):
        f = self.gpu
        rows = []
        for cid, label, *_ in CONFIRMATORY[:4]:
            prim = self.res_conf[cid]["r"]
            src = self.B.mean(contrast_pairs(f, cid, nfield="n_src"))
            prs = self.res_conf[cid]["pairs"]
            kept = self.B.mean(prs[~prs["list_changed"].astype(bool)]) if prs is not None else None
            chg = self.B.mean(prs[prs["list_changed"].astype(bool)]) if prs is not None else None
            ov = self.B.mean(contrast_pairs(f, cid, nfield="n_overlay"))
            rows.append([cid, fmt(prim), fmt(src), fmt(kept), fmt(chg), fmt(ov)])
        cid = "C2"
        oc = [self.B.mean(paired(f, "min_k_shown", "none", o, nfield=nf)) for o, nf in
              (("over_count", "n"), ("over_src", "n_src"), ("over_overlay", "n_overlay"))]
        ov_note = ("no overlay file (analysis/gold_overlay.jsonl): the overlay column equals the frozen lists"
                   if not self.docs.attrs["overlay_exists"] else f"overlay rows applied: {self.docs.attrs['overlay_rows']}")
        self.sec("7. Answer-key variants (sections 4.2, 4.3): frozen lists, the annotators' counts, kept vs changed lists, overlay",
                 "Length change does not need a count; the annotators' counts change only which documents are in the "
                 "n < k cells. Kept / changed: whether the cleanup changed the document's answer list. " + ov_note + ".", "",
                 *md_table(["#", "frozen lists (primary)", "annotators' counts", "list kept", "list changed", "overlay"], rows),
                 "", f"- Contrast 2 on over-count (points): frozen {pts(oc[0])}; annotators' counts {pts(oc[1])}; overlay {pts(oc[2])}")
        self.head["c2_src"] = rows[1][2]

    # ---- 6. generality
    def generality(self):
        pr = self.res_conf["C2"]["pairs"]
        above = [m for m in self.present_main if (self.head["per_model_c2"].get(m) or {}).get("lo", -1) > 0]
        fams = sorted({self.family[m] for m in self.present_main})
        w = {}
        for fa in fams:
            ms = [m for m in self.present_main if self.family[m] == fa]
            for m in ms:
                w[m] = 1.0 / len(fams) / len(ms)
        fw = self.B.model_weighted(pr, w)
        lofo = {fa: self.B.mean(pr[pr["model_key"].map(self.family) != fa]) for fa in fams}
        self.sec("8. Generality summary (section 2; contrast 2)",
                 f"- models whose own interval is above 0: {len(above)} of {len(self.present_main)} ({', '.join(NAME[m] for m in above)})",
                 f"- the {len(fams)} families weighted equally ({', '.join(fams)}; within a family its models equally): {fmt(fw)}",
                 *[f"- leaving out {fa}: {fmt(v)}" for fa, v in lofo.items()])
        self.head["generality"] = {"above": len(above), "of": len(self.present_main), "family_weighted": fw, "lofo": lofo}

    # ---- 7. per wording
    def wordings(self):
        f = self.gpu[self.gpu["ok"]]
        rows = []
        for c in ("prose_up_to_k", "prose_exactly_k"):
            for w in sorted(f[f["condition"] == c]["wording_id"].dropna().unique()):
                one = f[(f["condition"] == "none") | ((f["condition"] == c) & (f["wording_id"] == w))]
                sub = one[(one["condition"] == c) & (one["n"] < one["k"]) & one["k"].isin((3, 5))]
                rows.append([c, w, fmt(self.B.mean(paired(one, c, "none"))), f"{100 * sub['over_count'].mean():.1f}"])
        self.sec("9. Per wording (prose conditions; length change against none and over-count %, n < k, k = 3 and 5)",
                 *md_table(["condition", "wording", "vs none (length)", "over-count %"], rows))

    # ---- 8. exploratory: RQ3, RQ4
    def rq3(self):
        docs = common.load_documents()
        rank = {}
        for d_id in self.gpu["doc_id"].unique():
            d = docs[d_id]
            pos = []
            for i, g in enumerate(d.get("gold_items") or []):
                p = g.get("start")
                if p is None and g.get("evidence"):
                    p = min((e.get("start") for e in g["evidence"] if e.get("start") is not None), default=None)
                if p is None:
                    j = d["text"].lower().find(g["text"].lower())
                    p = j if j >= 0 else 10 ** 9 + i
                pos.append((p, i))
            rank[d_id] = {i: r for r, (_, i) in enumerate(sorted(pos))}
        return rank

    def rq3_section(self):
        """Share of true items left out by their rank of first appearance, k < n (exploratory). Needs the
        matched gold indices, which are in the entries tables."""
        rank = self.rq3()
        hit = defaultdict(lambda: [0, 0])
        for m in self.present_main:
            run = f"fs_{m}_full"
            p = CACHE / f"{run}.entries.csv.gz"
            if not p.exists():
                continue
            e = pd.read_csv(p, usecols=["request_id", "doc_id", "condition", "k", "n", "label", "gold"],
                            dtype={"gold": str}, keep_default_na=False)
            e = e[(e["k"] < e["n"]) & e["label"].isin(["true_item", "split_of_true"])]
            got = defaultdict(set)
            for rid, g in zip(e["request_id"], e["gold"]):
                for x in str(g).split("+"):
                    if x != "":
                        got[rid].add(int(x))
            f = self.model_rows(m)
            f = f[f["ok"] & (f["k"] < f["n"]) & (f["condition"] != "none")]
            for rid, d_id, c, n in zip(f["request_id"], f["doc_id"], f["condition"], f["n"]):
                for gi in range(int(n)):
                    r = rank[d_id].get(gi, gi)
                    hit[(c, min(r, 5))][0] += gi not in got.get(rid, ())
                    hit[(c, min(r, 5))][1] += 1
        rows = []
        for c in CONDS[1:]:
            vals = [f"{100 * hit[(c, r)][0] / hit[(c, r)][1]:.1f}" if hit[(c, r)][1] else "--" for r in range(6)]
            if any(v != "--" for v in vals):
                rows.append([c, *vals])
        self.sec("10. RQ3 (exploratory): asked for fewer than exist (k < n), share of true items left out by position",
                 "Position = rank of the item's first appearance in the document (1 = first; 6 = sixth or later). "
                 "8 main models pooled; matcher v0 true-item and split labels.", "",
                 *md_table(["condition", "1st", "2nd", "3rd", "4th", "5th", "6th+"], rows))

    def rq4_section(self):
        rows = []
        for s in ("job_posts", "job_posts_knowledge"):
            f = self.gpu[self.gpu["set"] == s]
            rows.append([SET_NAME[s], fmt(self.B.mean(contrast_pairs(f, "C2"))),
                         pts(self.B.mean(contrast_pairs(f, "C2", "over_count")))])
        a = contrast_pairs(self.gpu[self.gpu["set"] == "job_posts"], "C2")
        b = contrast_pairs(self.gpu[self.gpu["set"] == "job_posts_knowledge"], "C2")
        self.sec("11. RQ4 (exploratory): item type inside job ads (skills, quoted, vs knowledge, named tools)",
                 *md_table(["set", "contrast 2 (length)", "contrast 2 (over-count, points)"], rows), "",
                 f"- skills minus knowledge, contrast 2 (length): {fmt(self.B.diff_of_means(a, b))}")

    # ---- 9. hosted, pairs
    def hosted_section(self):
        rows, trows = [], []
        for m in self.present_hosted:
            f = self.model_rows(m)
            cells = [self.B.mean(contrast_pairs(f, c)) for c in ("C1", "C2", "C3", "C4", "C5")]
            fewer = self.B.mean(paired(f, "min_k_shown_fewer_ok", "none"))
            unread = 100 * (1 - f[f["ok"]]["valid"].mean())
            rows.append([NAME.get(m, m), *[fmt(c) for c in cells], fmt(fewer), f"{unread:.1f}", int((~f["ok"]).sum())])
            trows.append([tex_escape(NAME.get(m, m)), *[tex_ci(c) for c in cells[:4]], tex_ci(fewer)])
        self.sec("12. Hosted models (dated reference, never pooled with the GPU results)",
                 "Bedrock runs the prompt-side conditions only, so contrast 5 is empty there.", "",
                 *md_table(["model", "C1", "C2", "C3", "C4", "C5", "fewer_ok vs none", "unreadable %", "missing"], rows))
        self.tex["tab_hosted.tex"] = tex_table("lrrrrr", ["Model", "C1", "C2", "C3", "C4", "Fewer-ok vs none"], trows)
        self.sorting_section(self.present_hosted, "12a. Sorting, hosted models pooled (reference only)")

    def pairs_section(self):
        rows = []
        for h, g in PAIRS:
            if h not in self.present_hosted or g not in self.present_main:
                continue
            fh, fg = self.model_rows(h), self.model_rows(g)
            a, b = contrast_pairs(fh, "C2"), contrast_pairs(fg, "C2")
            oa, ob = contrast_pairs(fh, "C2", "over_count"), contrast_pairs(fg, "C2", "over_count")
            # the same documents and k only
            key = ["doc_id", "k"]
            common_keys = a.merge(b, on=key)[key] if a is not None and b is not None else None
            if common_keys is not None:
                a, b = a.merge(common_keys, on=key), b.merge(common_keys, on=key)
                oa, ob = oa.merge(common_keys, on=key), ob.merge(common_keys, on=key)
            d = self.B.diff_of_means(a, b)
            do = self.B.diff_of_means(oa, ob)
            rows.append([f"{NAME[h]} vs {NAME[g]}", fmt(self.B.mean(a)), fmt(self.B.mean(b)), fmt(d), pts(do),
                         "yes" if do and abs(100 * do["est"]) < 10 else "no"])
        self.sec("13. Same-weights pairs (contrast 2 on the same documents and k)",
                 "The serving stack is said not to drive the result if the pair's main contrast differs by less than "
                 "10 points; points are over-count points (the contrast is also given in entries).", "",
                 *md_table(["pair", "hosted (length)", "GPU (length)", "difference (length)", "difference (over-count, points)",
                            "under 10 points"], rows))

    # ---- 10. repeat check, re-ask, thinking
    def repeat_section(self):
        rows = []
        for m in sorted({x["model_key"] for x in self.meta if run_kind(x["run_id"]) == "repeat"}):
            rep = self.df[(self.df["kind"] == "repeat") & (self.df["model_key"] == m) & self.df["ok"]]
            base = self.full[(self.full["model_key"] == m) & self.full["ok"]]
            j = rep.merge(base, on="request_id", suffixes=("_r", "_b"))
            if not len(j):
                continue
            same = (j["content_sha1_r"] == j["content_sha1_b"]).mean()
            flip = (j["over_count_r"] != j["over_count_b"]).mean()
            dlen = (j["n_substantive_r"] - j["n_substantive_b"]).abs().gt(0).mean()
            rows.append([NAME.get(m, m), len(j), f"{100 * same:.1f}", f"{100 * flip:.2f}", f"{100 * dlen:.1f}"])
        self.sec("14. Repeat check (300 prompts per model sent twice; the repeat on a newly started server)",
                 "Identical = the same reply text. Flip = the over-count verdict differs. Length differs = the number "
                 "of substantive entries differs. Request ids answered in both runs only.", "",
                 *md_table(["model", "prompts in both", "identical %", "over-count flips %", "length differs %"], rows))
        self.tex["tab_repeat.tex"] = tex_table("lrrrr", ["Model", "Prompts", "Identical \\%", "Flips \\%", "Length differs \\%"],
                                               [[tex_escape(r[0]), *r[1:]] for r in rows])

    def reask_section(self):
        rows = []
        for m in sorted({x["model_key"] for x in self.meta if run_kind(x["run_id"]) == "reask"}):
            re_ = self.df[(self.df["kind"] == "reask") & (self.df["model_key"] == m) & self.df["ok"]]
            base = self.full[(self.full["model_key"] == m) & self.full["ok"]]
            j = re_.merge(base, left_on="source_request_id", right_on="request_id", suffixes=("_r", "_b"))
            if not len(j):
                continue
            lt = j[j["n_b"] < j["k_b"]]
            rows.append([NAME.get(m, m), len(j), f"{100 * (j['n_items_r'] >= j['k_r']).mean():.1f}", len(lt),
                         f"{100 * lt['over_count_b'].mean():.1f}" if len(lt) else "--",
                         f"{100 * lt['over_count_r'].mean():.1f}" if len(lt) else "--",
                         f"{(lt['n_substantive_r'] - lt['n_substantive_b']).mean():+.2f}" if len(lt) else "--",
                         " / ".join(f"{100 * lt['sort_r'].astype(str).eq(s).mean():.0f}" for s in SORTS) if len(lt) else "--"])
        self.sec("15. Re-ask arm (exploratory): min_k_shown replies shorter than k sent back once with the validation error",
                 "Before = the first reply, after = the reply to the re-ask. Sorting after, on n < k: "
                 + " / ".join(SORTS) + " (%).", "",
                 *md_table(["model", "re-asked", "after: k or more entries %", "re-asked with n < k",
                            "over-count before %", "over-count after %", "length change", "sorting after"], rows))

    def thinking_section(self):
        th = self.df[(self.df["kind"] == "think") & self.df["ok"]]
        rows, phr = [], []
        if not len(th):
            self.sec("16. Thinking side test (exploratory)", "No thinking-pair run is in the runs folder yet; these "
                     "tables fill in when the fs_*_think-filters_s* (and fs_bedrock-kimi-k3-think_*) folders are copied in.")
            return
        for on, off in self.think_pairs:
            for seed in sorted(set(th[th["model_key"] == on]["request_seed"].dropna().astype(str)) | {""}):
                fon = th[(th["model_key"] == on) & (th["request_seed"].astype(str) == seed)] if seed else \
                    th[(th["model_key"] == on) & th["request_seed"].isna()]
                if not len(fon):
                    continue
                if off == "bedrock-kimi-k3":
                    foff = self.full[(self.full["model_key"] == off) & self.full["doc_id"].isin(set(fon["doc_id"]))]
                else:
                    foff = th[(th["model_key"] == off) & (th["request_seed"].astype(str) == seed)]
                a, b = paired(fon, "min_k_shown", "none"), paired(foff, "min_k_shown", "none")
                if a is not None and b is not None:
                    key = a.merge(b, on=["doc_id", "k"])[["doc_id", "k"]]
                    a, b = a.merge(key, on=["doc_id", "k"]), b.merge(key, on=["doc_id", "k"])
                ocon = fon[(fon["condition"] == "min_k_shown") & (fon["n"] < fon["k"]) & fon["k"].isin((3, 5))]["over_count"].mean()
                ocoff = foff[(foff["condition"] == "min_k_shown") & (foff["n"] < foff["k"]) & foff["k"].isin((3, 5))]["over_count"].mean()
                rows.append([on, off, seed or "-", fmt(self.B.mean(a)), fmt(self.B.mean(b)), fmt(self.B.diff_of_means(a, b)),
                             f"{100 * ocon:.1f}", f"{100 * ocoff:.1f}"])
                sub = fon[(fon["n"] < fon["k"]) & (fon["condition"] != "none")]
                if len(sub):
                    phr.append([on, seed or "-", len(sub), f"{100 * sub['shortfall_phrase'].astype(float).mean():.1f}",
                                f"{100 * sub[sub['over_count'] > 0]['shortfall_phrase'].astype(float).mean():.1f}"
                                if (sub["over_count"] > 0).any() else "--"])
        self.sec("16. Thinking side test (exploratory; sampled decoding, per request seed)",
                 *md_table(["thinking on", "partner (off)", "seed", "C2 on (length)", "C2 off (length)", "on minus off",
                            "min_k_shown over-count on %", "off %"], rows), "",
                 "Thinking text naming a shortfall (phrase search, NOT checked by hand; C16), outputs with n < k:", "",
                 *md_table(["model", "seed", "outputs", "trace names a shortfall %", "of padded outputs %"], phr))

    # ---- write
    def write(self):
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "tex").mkdir(exist_ok=True)
        hdr = ["# Full study: every registered test and estimate", "",
               "Written by `python analysis/full_study.py tables` from the scored run records in "
               "`analysis/full/scored/` (`analysis/full_study_score.py`); run folders in `runs.md`. "
               f"Bootstrap: {self.B.boot} draws over document groups within set, seed {SEED}. Length change in "
               "substantive entries; over-count in points. GPU results pool the 8 main models: "
               + ", ".join(NAME[m] for m in self.present_main) + "."]
        missing = [m for m in self.main if m not in self.present_main]
        if missing:
            hdr.append(f"\nMAIN MODELS WITHOUT A FULL RUN: {', '.join(missing)}")
        (OUT / "RESULTS.md").write_text("\n".join(hdr + self.md) + "\n", encoding="utf-8")
        for name, body in self.tex.items():
            (OUT / "tex" / name).write_text(body, encoding="ascii", errors="replace")
        (OUT / "headline.json").write_text(json.dumps(self.head, indent=1, default=lambda o: None), encoding="utf-8")

    def run_all(self):
        self.runs_section()
        self.confirmatory()
        self.per_model(self.present_main, "2. Per main model (each with its own interval; the pooled row is section 1)",
                       "tab_per_model.tex")
        self.per_set()
        self.named_section()
        self.outcomes_section()
        self.sorting_section(self.present_main, "6. Sorting every output (C3), 8 main models pooled", "tab_sorting.tex")
        self.sorting_per_model()
        self.fills_section(self.present_main, "6b. What the extra entries are (matcher v0, unchecked), 8 main models pooled")
        self.key_variants()
        self.generality()
        self.wordings()
        self.rq3_section()
        self.rq4_section()
        self.hosted_section()
        self.pairs_section()
        self.repeat_section()
        self.reask_section()
        self.thinking_section()
        self.md += ["", "## 17. Not computed from these runs", "",
                    "- RQ5 (closing probability), RQ7 (token confidence) and RQ8 (hidden-state probe) need the "
                    "teacher-forced and hidden-state passes (harness/teacher_forced.py, analysis/rq7.py); none was run "
                    "on the full-study outputs, so they are not in these tables.",
                    "- The robustness arms (block_llamaindex, base_neutral) ran on the pilot documents in the pilot "
                    "only; they are not part of the full-study runs.",
                    "- The dev runs (reserve documents) are scored (runs.md) but enter no test."]
        self.write()


def report(study):
    """REPORT.md: the headline numbers (from the same objects as RESULTS.md) and the protocol notes."""
    h = study.head
    c = h["confirmatory"]
    hp = h["confirmatory_holm"]
    lines = ["# Full study: headline numbers and protocol notes", "",
             "Generated by `python analysis/full_study.py tables`; every number below is also in `RESULTS.md`, "
             "which says how it was computed. 8 main open-weight models on the local GPU, documents with n < k, "
             f"k = 3 and 5, 95% intervals from {study.B.boot} bootstrap draws over document groups.", "",
             "## Headline numbers", ""]
    lab = {x[0]: x[1] for x in CONFIRMATORY}
    for cid in ("C2", "C1", "C3", "C4", "C5"):
        r = c[cid]
        lines.append(f"- {lab[cid]}: {fmt(r)}" + (" entries" if cid != "C5" else " extra entries per padded slot")
                     + f", Holm p {fmt_p(hp[cid])}" + (f", {r['pairs']} pairs" if r else ""))
    lines.append(f"- Contrast 2 on over-count: {pts(h['c2_over'])} points")
    lines.append("- Per model, contrast 2 (entries): " + "; ".join(f"{NAME[m]} {fmt(v)}" for m, v in h["per_model_c2"].items()))
    g = h["generality"]
    lines.append(f"- Models whose own interval is above 0: {g['above']} of {g['of']}; families weighted equally: "
                 f"{fmt(g['family_weighted'])}")
    n = h["named"]
    lines += [f"- Fewer is fine (min_k_shown_fewer_ok vs none): {fmt(n['fewer_vs_none'])}; vs min_k_shown "
              f"{fmt(n['fewer_vs_shown'])}",
              f"- maxItems shown vs none: {fmt(n['max_vs_none'])}",
              f"- Enough items (n >= k), min_k_shown vs none: {fmt(n['enough'])}; slot-filling part at k = 3 and 5 "
              f"(change on n < k minus on n >= k): {fmt(n['slot_part_35'])}",
              f"- Empty documents at k = 1, min_k_shown vs none, share with at least one entry: "
              f"{pts(n['empty']['min_k_shown'])} points",
              "- Missing outputs (transport failures that failed again when resent) in the main runs: "
              + (", ".join(f"{NAME[m]} {v}" for m, v in h["missing_main"].items() if v) or "none"),
              "- Unreadable outputs (all conditions and k), per main model: "
              + "; ".join(f"{NAME[m]} {h['unreadable'][NAME[m]]}%" for m in study.present_main) + ". Most of "
              "Qwen3.5-0.8B's are its answer written inside a copy of the schema, which the frozen parse rules "
              "never take as the answer (RESULTS.md 5b); they count as 0 entries, and more of them under min_k_shown than under none turn its contrast 2 "
              "negative."]
    lines += ["", "## What could not be implemented exactly as written", ""] + NOTES
    (OUT / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


NOTES = [
    "1. **The matcher was frozen with the registered plan.** Section 5.2 says the matcher is frozen and tagged "
    "`scorer-v1` before study outputs are scored. It was frozen with the registered plan instead (tag `prereg-v2.1`, "
    "`analysis/matcher.py` v0) and scores the study unchanged. Its accuracy is measured against the 400 entries both "
    "authors labelled independently (5.3 b; `analysis/human/RESULTS.md`).",
    "2. **`missed_gold` and `beyond_excerpt` are not decided by the matcher v0.** Those entries land in "
    "`in_text_wrong_type` or `plausible_invented`. The matcher-label sheet's strata for these two labels are empty, so, "
    "as section 5.3 b says for a label with fewer than 80 entries, their places go in equal parts to the other three "
    "labels (134, 133, 133). The labellers can still give either label; `beyond_excerpt` needs the wider source, which "
    "the sheet does not include.",
    "3. **Scoring check (5.3 a) done during the full run rather than before it.** The sheet is drawn from the pilot "
    "runs as 5.3 a says (65 replies: 40 random, 3 cut at the token limit, 22 unreadable). No scorer bug was found "
    "(`analysis/human/RESULTS.md`).",
    "4. **Contrast 5's per-output measure.** \"Substantive extra entries per padded slot\" is computed per output as "
    "excess / (k - n), the slots the grammar forces beyond the true items, so the paired difference is per document.",
    "5. **Contrast 5's Poisson mixed model is a variational-Bayes fit** (statsmodels `PoissonBayesMixedGLM`, random "
    "intercept per document, log(k - n) as a covariate), because no maximum-likelihood Poisson mixed model is available "
    "in the Python stack used here. It is reported next to the primary bootstrap test only, as a rate ratio with a "
    "posterior interval.",
    "6. **Mixed models report the intercept.** Covariates are centred and factors sum-coded so the intercept is the "
    "average paired difference; that intercept and its Wald interval are what the table shows.",
    "7. **\"Says it is short\" outside the list.** The note rules of `harness/common.py` are applied, unchanged, to each "
    "sentence of the text outside the JSON (split at . ! ?, new lines and colons). Notes those rules do not cover "
    "(\"there is only one request\") are not caught, so the says-short share is a lower bound.",
    "8. **n = 0 apart.** Section 6.1 says n = 0 is analysed apart from n = 1 to 3; the primary contrasts pool every "
    "n < k cell (as the pilot's stop rules did) and table 1a gives n = 0 and n >= 1 separately.",
    "9. **Same-weights pairs: \"10 points\".** The main measure is now in entries, while the 10-point rule was written for "
    "over-count; the pair table gives both and judges the rule on over-count points.",
    "10. **Overlay.** `analysis/gold_overlay.jsonl` does not exist yet, so the overlay variant equals the frozen lists. "
    "The code reads one row per corrected item and treats it as an added true item (`op: remove` subtracts one).",
    "11. **Human-check frame.** The 400-entry frame is every substantive entry of the full runs (8 GPU models and the "
    "hosted models, `none` included). The thinking-pair runs are not in it: they are still running, and the draw has to "
    "be fixed before labelling starts.",
    "12. **Not computed here**: RQ5, RQ7 and RQ8 need the teacher-forced and hidden-state passes, which were not run on "
    "the full-study outputs; the robustness arms ran only in the pilot.",
]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["score", "tables", "all"])
    ap.add_argument("--runs-dir")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--boot", type=int, default=10000)
    args = ap.parse_args()
    if args.cmd in ("score", "all"):
        if not args.runs_dir:
            raise SystemExit("--runs-dir is needed to score")
        import full_study_score
        for rid, what in full_study_score.score_all(args.runs_dir, CACHE, args.jobs):
            print(f"{rid}: {what}")
    if args.cmd in ("tables", "all"):
        docs = doc_table()
        df, meta = load_scored()
        df = add_doc_fields(df, docs)
        st = Study(df, meta, args.boot, docs)
        st.run_all()
        report(st)
        print(f"wrote {OUT}/RESULTS.md, REPORT.md, runs.md, tex/ ({len(st.tex)} tables)")


if __name__ == "__main__":
    main()
