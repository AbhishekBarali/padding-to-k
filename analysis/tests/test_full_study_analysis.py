"""Tests for analysis/full_study.py on small made-up tables. Run: python analysis/tests/test_full_study_analysis.py (or pytest)."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import full_study as fs  # noqa: E402

sys.path.insert(0, str(HERE.parent.parent / "harness"))
from score_counts import Boot  # noqa: E402


def _rows():
    """Two models, three documents in two sets; n < k everywhere at k = 3."""
    rows = []
    docs = [("d1", "g1", "emails", 0), ("d2", "g2", "emails", 1), ("d3", "g3", "clinical", 2)]
    lengths = {"none": [0, 1, 2], "min_k_shown": [3, 3, 2], "max_k_shown": [0, 1, 1]}
    for m, extra in (("m1", 0), ("m2", 1)):
        for (d, g, s, n), i in zip(docs, range(3)):
            for c, ls in lengths.items():
                rows.append({"model_key": m, "doc_id": d, "group": g, "set": s, "split": "full", "n": n, "n_src": n,
                             "words": 100.0, "list_changed": False, "k": 3, "condition": c, "wording_id": "all_1",
                             "ok": True, "n_substantive": float(ls[i] + (extra if c == "min_k_shown" else 0)),
                             "excess": 0.0})
            for w, v in (("exactly_1", 3.0), ("exactly_2", 1.0)):
                rows.append({"model_key": m, "doc_id": d, "group": g, "set": s, "split": "full", "n": n, "n_src": n,
                             "words": 100.0, "list_changed": False, "k": 3, "condition": "prose_exactly_k",
                             "wording_id": w, "ok": True, "n_substantive": v, "excess": 0.0})
    return pd.DataFrame(rows)


def test_paired_differences_per_model_document_and_k():
    pr = fs.paired(_rows(), "min_k_shown", "none")
    got = {(r.model_key, r.doc_id): r.diff for r in pr.itertuples()}
    assert got == {("m1", "d1"): 3, ("m1", "d2"): 2, ("m1", "d3"): 0, ("m2", "d1"): 4, ("m2", "d2"): 3, ("m2", "d3"): 1}


def test_prose_wordings_are_averaged_before_the_difference():
    pr = fs.paired(_rows(), "prose_exactly_k", "none")
    assert sorted(pr["diff"].tolist()) == sorted([2.0 - 0, 2.0 - 1, 2.0 - 2] * 2)


def test_missing_outputs_leave_their_pair_out():
    f = _rows()
    f.loc[(f["doc_id"] == "d1") & (f["model_key"] == "m1") & (f["condition"] == "none"), "ok"] = False
    pr = fs.paired(f, "min_k_shown", "none")
    assert len(pr) == 5 and not ((pr["doc_id"] == "d1") & (pr["model_key"] == "m1")).any()


def test_cells_n_below_k_only():
    f = _rows()
    f.loc[f["doc_id"] == "d3", "n"] = 3          # now n = k: out of the n < k cell
    pr = fs.paired(f, "min_k_shown", "none")
    assert set(pr["doc_id"]) == {"d1", "d2"}
    ge = fs.paired(f, "min_k_shown", "none", cell="ge")
    assert set(ge["doc_id"]) == {"d3"}


def test_bootstrap_mean_equals_score_counts_boot():
    rng = np.random.default_rng(1)
    per_group, strata = {}, {}
    for i in range(30):
        g = f"g{i:02d}"
        vals = rng.integers(-2, 4, rng.integers(1, 5)).astype(float)
        per_group[g] = (vals.sum(), len(vals))
        strata[g] = "a" if i < 12 else "b"
    old = Boot(2000, 20261014).ci(per_group, strata)
    new = fs.Bootstrap(2000, 20261014).stat(per_group, strata, lambda v: v[..., 0] / np.maximum(v[..., 1], 1))
    assert abs(old[0] - new["est"]) < 1e-12 and abs(old[1] - new["lo"]) < 1e-12 and abs(old[2] - new["hi"]) < 1e-12


def test_bootstrap_p_value_two_sided():
    per_group = {f"g{i}": (1.0 + (i % 3), 1) for i in range(20)}
    strata = {g: "s" for g in per_group}
    r = fs.Bootstrap(1000).stat(per_group, strata, lambda v: v[..., 0] / np.maximum(v[..., 1], 1))
    assert r["p"] == 0.0 and r["lo"] > 0
    sym = {f"g{i}": ((-1.0) ** i, 1) for i in range(20)}
    r = fs.Bootstrap(1000).stat(sym, {g: "s" for g in sym}, lambda v: v[..., 0] / np.maximum(v[..., 1], 1))
    assert r["p"] > 0.5


def test_holm():
    adj = fs.holm([0.01, 0.04, 0.03, 0.2, 0.001])
    assert np.allclose(adj, [0.04, 0.09, 0.09, 0.2, 0.005])


def test_dose_pairs_same_document_k5_minus_k3():
    f = _rows()
    f5 = f[f["condition"] == "min_k_shown"].copy()
    f5["k"] = 5
    f5["n_substantive"] += 1
    pr = fs.dose_pairs(pd.concat([f, f5]))
    assert len(pr) == 6 and (pr["diff"] == 1).all()


def test_family_weighting():
    pr = fs.paired(_rows(), "min_k_shown", "none")      # m1 mean 5/3, m2 mean 8/3
    r = fs.Bootstrap(200).model_weighted(pr, {"m1": 0.5, "m2": 0.5})
    assert abs(r["est"] - (5 / 3 + 8 / 3) / 2) < 1e-12
    r = fs.Bootstrap(200).model_weighted(pr, {"m1": 1.0, "m2": 0.0})
    assert abs(r["est"] - 5 / 3) < 1e-12


def test_diff_of_means():
    pr = fs.paired(_rows(), "min_k_shown", "none")
    a, b = pr[pr["model_key"] == "m2"], pr[pr["model_key"] == "m1"]
    r = fs.Bootstrap(200).diff_of_means(a, b)
    assert abs(r["est"] - 1.0) < 1e-12


def test_run_kinds():
    assert fs.run_kind("fs_qwen3.5-9b_full") == "full"
    assert fs.run_kind("fs_qwen3.5-9b_full-repeat") == "repeat"
    assert fs.run_kind("fs_qwen3.5-9b_full-reask1") == "reask"
    assert fs.run_kind("fs_gpt-oss-20b_dev") == "dev"
    assert fs.run_kind("fs_qwen3.5-9b-think_think-filters_s2") == "think"
    assert fs.run_kind("fs_gemma-4-31b-sampled_think-filters_s1") == "think"
    assert fs.run_kind("fs_bedrock-kimi-k3-think_pilot") == "think"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    bad = 0
    for fn in fns:
        try:
            fn()
            print(f"ok   {fn.__name__}")
        except Exception as e:  # noqa: BLE001
            bad += 1
            print(f"FAIL {fn.__name__}: {type(e).__name__}: {e}")
    print(f"{len(fns) - bad}/{len(fns)} passed")
    sys.exit(1 if bad else 0)
