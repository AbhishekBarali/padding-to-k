"""Tests for analysis/downstream/esco/ (ESCO linking, addendum 1 section 3.2).
Run: python analysis/tests/test_esco_downstream.py (or pytest). Needs numpy and pandas; the linker model is
never loaded (embeddings are made up here)."""
import json
import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "downstream" / "esco"))
sys.path.insert(0, str(HERE.parent.parent / "harness"))
import esco_downstream as ed  # noqa: E402
import esco_linker as el  # noqa: E402
import full_study as fs  # noqa: E402

CONCEPTS = [{"uri": "u:a", "type": "skill/competence", "label": "python", "alt": ["python programming"], "description": ""},
            {"uri": "u:b", "type": "knowledge", "label": "statistics", "alt": ["python"], "description": ""},
            {"uri": "u:c", "type": "skill/competence", "label": "teamwork", "alt": [], "description": ""}]


class FakeEmbedder:
    """Fixed unit vectors per text: lets the tests set every cosine exactly."""

    def __init__(self, table):
        self.table = table

    def embed(self, texts, progress=False):
        return np.array([self.table[t.strip()] for t in texts], dtype=np.float32)


def unit(*v):
    v = np.array(v, dtype=float)
    return v / np.linalg.norm(v)


def make_linker():
    table = {"python": unit(1, 0, 0), "python programming": unit(1, 0.1, 0), "statistics": unit(0, 1, 0),
             "teamwork": unit(0, 0, 1),
             "write python code": unit(1, 0.05, 0),                  # ~1.0 to python
             "data skills": unit(0.6, 0.8, 0),                       # 0.8 to statistics, 0.6 to python
             "be friendly": unit(0.55, 0, 0.835)}                    # ~0.835 to teamwork
    return el.Linker(CONCEPTS, FakeEmbedder(table))


def test_cutoff_logic():
    s = [0.49, 0.5, 0.69, 0.7, 0.95]
    assert list(el.link_scores(s, 0.5)) == [False, True, True, True, True]          # at least the cutoff
    assert list(el.link_scores(s, 0.7)) == [False, False, False, True, True]
    assert list(el.link_scores(s, None)) == [True] * 5                              # no cutoff: always linked
    assert el.CUTOFFS == {"0.5": 0.5, "none": None, "0.7": 0.7}


def test_label_table_and_ties():
    texts, owner = el.label_table(CONCEPTS)
    assert texts == ["python", "python programming", "statistics", "python", "teamwork"]
    assert list(owner) == [0, 0, 1, 1, 2]
    L = make_linker()
    ci, li, sc = L.best(["python"])
    assert ci[0] == 0 and li[0] == 0 and abs(sc[0] - 1) < 1e-6      # "python" is a label of a and b: a wins (URI order)
    ci, li, sc = L.best(["data skills", "be friendly"])
    assert list(ci) == [1, 2]
    assert abs(sc[0] - 0.8) < 1e-5 and abs(sc[1] - 0.835) < 1e-3


def test_false_concept_count_tiny_example():
    L = make_linker()
    gold = {"d1": [(0, "python")]}                                  # the ad's one true item links to a
    rows = [{"doc_id": "d1", "entries": [(0, "write python code", "true_item"), (1, "data skills", "in_text_wrong_type"),
                                         (2, "be friendly", "plausible_invented")]}]
    texts = sorted({t for _, t in gold["d1"]} | {t for _, t, _ in rows[0]["entries"]})
    ci, li, sc = L.best(texts)
    best = {t: (int(c), int(l), float(s)) for t, c, l, s in zip(texts, ci, li, sc)}
    true_links = {"d1": [(j, t, *best[t]) for j, t in gold["d1"]]}
    out_c, true_c = ed.concept_sets(rows, true_links, best, 0.5)
    assert out_c[0] == {0, 1, 2} and true_c["d1"] == {0}
    m = ed.output_measures(out_c[0], true_c["d1"])
    assert m == {"false": 2, "any": 1.0, "tp": 1, "pred": 3, "true": 1}
    out_c, _ = ed.concept_sets(rows, true_links, best, 0.82)       # "data skills" (0.8) drops out; friendly stays
    assert out_c[0] == {0, 2}
    out_c, _ = ed.concept_sets(rows, true_links, best, 0.9)
    assert ed.output_measures(out_c[0], true_c["d1"])["false"] == 0
    assert ed.output_measures(set(), set()) == {"false": 0, "any": 0.0, "tp": 0, "pred": 0, "true": 0}


def test_same_concept_twice_counts_once():
    assert ed.output_measures({5, 5, 7}, {7})["false"] == 1


def test_weights_match_full_study_bootstrap():
    rng = np.random.default_rng(1)
    groups = [f"g{i}" for i in range(13)]
    strata = {g: ("job_posts" if i % 3 else "job_posts_knowledge") for i, g in enumerate(groups)}
    M = rng.random((13, 2))
    ref = fs.Bootstrap(boot=500).stat({g: M[i] for i, g in enumerate(groups)}, strata, lambda v: v[..., 0] / v[..., 1])
    W = ed.draw_weights(groups, strata, boot=500)
    assert W.shape == (500, 13) and (W.sum(axis=1) == 13).all()
    mine = ed.summarise(M[:, 0].sum() / M[:, 1].sum(), (W @ M)[:, 0] / (W @ M)[:, 1])
    assert abs(mine["lo"] - ref["lo"]) < 1e-12 and abs(mine["hi"] - ref["hi"]) < 1e-12


def test_top_mask_ties_and_zeros():
    counts = np.array([5, 7, 7, 0, 1.0]) * ed.SCALE
    m = ed.top_mask(counts, 2)
    assert list(m) == [False, True, True, False, False]
    m = ed.top_mask(np.array([3, 3, 3.0]) * ed.SCALE, 2)            # tie: lower index (URI order) first
    assert list(m) == [True, True, False]
    m = ed.top_mask(np.array([0, 2, 0.0]) * ed.SCALE, 2)            # a zero count is never in a top list
    assert list(m) == [False, True, False]
    out = np.array([4, 4, 1, 0.0]) * ed.SCALE
    true = np.array([0, 4, 3, 1.0]) * ed.SCALE
    assert ed.not_in_true_top(out, true, 2) == 1                     # top of out {0,1}; of true {1,2}


def _frame():
    """Two models, two ads; `none` vs min_k_shown; prose with two wordings."""
    rows = []
    for m in ("m1", "m2"):
        for d, g, s in (("d1", "g1", "job_posts"), ("d2", "g2", "job_posts_knowledge")):
            rows.append({"model_key": m, "doc_id": d, "group": g, "set": s, "k": 3, "condition": "none",
                         "wording_id": "all_1", "entries": []})
            rows.append({"model_key": m, "doc_id": d, "group": g, "set": s, "k": 3, "condition": "min_k_shown",
                         "wording_id": "all_1", "entries": []})
            for w in ("exactly_1", "exactly_2"):
                rows.append({"model_key": m, "doc_id": d, "group": g, "set": s, "k": 3, "condition": "prose_exactly_k",
                             "wording_id": w, "entries": []})
    true_c = {"d1": {1}, "d2": set()}
    out_c = []
    for r in rows:
        if r["condition"] == "none":
            out_c.append({1} if r["doc_id"] == "d1" else set())
        elif r["condition"] == "min_k_shown":
            out_c.append({1, 2, 3} if r["doc_id"] == "d1" else {4})
        else:
            out_c.append({1, 2} if r["wording_id"] == "exactly_1" else {1})
    return rows, out_c, true_c


def test_pairs_and_measures():
    rows, out_c, true_c = _frame()
    f = ed.cell_frame(rows, out_c, true_c)
    pe = f[(f["condition"] == "prose_exactly_k") & (f["doc_id"] == "d1")].iloc[0]
    assert pe["false"] == 0.5 and pe["m"] == 2                      # wordings averaged: (1 + 0) / 2
    assert pe["weights"] == {1: 1.0, 2: 0.5}
    pr = ed.pair(f, "min_k_shown")
    assert len(pr) == 4
    res = ed.measure_pairs(pr, 200, true_c)
    assert res["false"]["none"]["est"] == 0 and res["false"]["cond"]["est"] == 1.5     # (2 + 1) per model / 2 ads
    assert res["false"]["diff"]["est"] == 1.5
    assert res["any"]["cond"]["est"] == 1.0 and res["any"]["none"]["est"] == 0.0
    assert abs(res["precision"]["cond"]["est"] - 2 / 8) < 1e-12     # shared 1+1 of 3+1+3+1 linked concepts
    assert res["precision"]["none"]["est"] == 1.0
    assert res["recall"]["cond"]["est"] == 1.0 and res["recall"]["none"]["est"] == 1.0
    t = res["top20"]
    assert t["none"]["est"] == 0 and t["cond"]["est"] == 3          # concepts 2, 3, 4 are not true items
    assert t["true_top"] == [1]                                      # concept indices (URIs in main())


def test_entry_text_lines_up_with_the_frozen_scorer():
    """A tiny run folder, scored by full_study_score.score_run; outputs_of_run must find the same entries
    the scorer labelled, keep only substantive ones, and expand `none` to k = 3 and 5 (n = 1 < k)."""
    import full_study_score as fss
    ctx = fss.Context()
    doc = "job-0ad70d"
    q_none, q_min = f"{doc}|none|k1|all_1", f"{doc}|min_k_shown|k3|all_1"
    assert q_none in ctx.req and q_min in ctx.req
    plan = [{"request_id": q_none, "also_answers": [f"{doc}|none|k3|all_1", f"{doc}|none|k5|all_1"], "arm": None},
            {"request_id": q_min, "also_answers": [], "arm": None}]
    replies = {q_none: '{"skills": ["Python", "Java"]}',
               q_min: '```json\n{"skills": ["Python", "N/A", "Python", "Leadership"]}\n```'}
    with tempfile.TemporaryDirectory() as tmp:
        run = Path(tmp) / "t_full"
        run.mkdir()
        (run / "manifest.json").write_text(json.dumps({"run_id": "t_full", "model_key": "m"}))
        (run / "planned.jsonl").write_text("".join(json.dumps(p) + "\n" for p in plan))
        (run / "raw.jsonl").write_text("".join(json.dumps({"request_id": r, "status": "ok", "content": c}) + "\n"
                                               for r, c in replies.items()))
        fss.score_run(run, Path(tmp) / "scored")
        rows, info = ed.outputs_of_run(run, [Path(tmp) / "scored"], ctx)
    assert info["table"] == "reused" and info["entries_checked"] == 6
    by = {(r["condition"], r["k"]): r for r in rows}
    assert set(by) == {("none", 3), ("none", 5), ("min_k_shown", 3)}
    assert [t for _, t, _ in by[("none", 3)]["entries"]] == ["Python", "Java"]
    assert [(i, t) for i, t, _ in by[("min_k_shown", 3)]["entries"]] == [(0, "Python"), (3, "Leadership")]


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
