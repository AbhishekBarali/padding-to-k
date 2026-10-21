"""POST HOC: tests for clean_baseline.py (pairing, clean definitions, rates) on a small synthetic table."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import clean_baseline as cb  # noqa: E402


def _row(model, doc, n, k, cond, subst, valid=True, wording=None, ok=True):
    return {"model_key": model, "doc_id": doc, "group": doc, "set": "emails", "n": n, "k": k, "condition": cond,
            "wording_id": wording, "n_substantive": float(subst), "over_count": float(valid and subst > n),
            "valid": float(valid), "ok": ok}


def _frame():
    rows = []
    # d1 (n = 1): no count exact -> clean (a) and (b); one row per k, since the no-count answer covers both k
    for k in (3, 5):
        rows.append(_row("m", "d1", 1, k, "none", 1))
        rows.append(_row("m", "d1", 1, k, "min_k_shown", k))                      # pads
        rows.append(_row("m", "d1", 1, k, "prose_up_to_k", 2, wording="w1"))     # over
        rows.append(_row("m", "d1", 1, k, "prose_up_to_k", 1, wording="w2"))     # not over -> cell share 0.5
    # d2 (n = 2): no count lists 1 -> clean (b) only; k = 3 and 5
    for k in (3, 5):
        rows.append(_row("m", "d2", 2, k, "none", 1))
        rows.append(_row("m", "d2", 2, k, "min_k_shown", 2))                      # does not pad
    # d3 (n = 0): no count over-counts -> in neither subset
    for k in (3, 5):
        rows.append(_row("m", "d3", 0, k, "none", 2))
        rows.append(_row("m", "d3", 0, k, "min_k_shown", k))
    # d4 (n = 4): only k = 5 has n < k; the k = 3 row must be dropped
    rows.append(_row("m", "d4", 4, 3, "none", 4))
    rows.append(_row("m", "d4", 4, 3, "min_k_shown", 5))
    rows.append(_row("m", "d4", 4, 5, "none", 4))
    rows.append(_row("m", "d4", 4, 5, "min_k_shown", 5))
    # a missing (not ok) output is left out
    rows.append(_row("m", "d2", 2, 5, "min_k_enforced", 3, ok=False))
    return pd.DataFrame(rows)


def test_cells_pairing():
    t = cb.cells(_frame())
    assert len(t) == 7                                      # d1, d2, d3 at k 3 and 5; d4 at k 5 only
    d1 = t[t.doc_id == "d1"].set_index("k")
    assert d1.loc[3, "prose_up_to_k"] == 0.5 and d1.loc[5, "min_k_shown"] == 1.0
    assert "min_k_enforced" not in t or t["min_k_enforced"].isna().all()


def test_clean_definitions():
    t = cb.cells(_frame())
    exact = set(t[cb.clean_mask(t, "exact")].doc_id)
    not_over = set(t[cb.clean_mask(t, "not_over")].doc_id)
    assert exact == {"d1", "d4"} and not_over == {"d1", "d2", "d4"}
    assert cb.clean_mask(t, "all").all()


def test_rates():
    t = cb.cells(_frame())
    boot = cb.fs.Bootstrap(200)
    s = cb.summarise(boot, t, "not_over")
    assert s["model_doc_pairs"] == 3 and s["cells"] == 5
    assert s["over_count"]["none"]["est"] == 0.0
    assert abs(s["over_count"]["min_k_shown"]["est"] - 3 / 5) < 1e-9   # d1 k3, d1 k5, d4 k5 pad; d2 does not
    a = cb.summarise(boot, t, "all")
    assert abs(a["over_count"]["none"]["est"] - 2 / 7) < 1e-9
    assert cb.pct(s["over_count"]["min_k_shown"]).startswith("60.0 [")
