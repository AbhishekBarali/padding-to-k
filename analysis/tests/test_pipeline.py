"""Tests for analysis/downstream/pipeline.py on small hand-made tables, plus the cross-check of its committed
results against the registered empty-document test. Run: python analysis/tests/test_pipeline.py (or pytest)."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "downstream"))
import full_study as fs  # noqa: E402
import pipeline as pl  # noqa: E402


def _row(model, doc, group, s, cond, k, n, subst, true=0, split=0, wrong=0, inv=0, status="ok", wording="all_1"):
    return {"run_id": f"fs_{model}_full", "model_key": model, "arm": "main", "request_id": f"{doc}|{cond}|k{k}|{wording}",
            "doc_id": doc, "group": group, "set": s, "condition": cond, "k": k, "n": n, "wording_id": wording,
            "status": status, "n_substantive": subst, "n_true": true, "n_split": split, "n_wrong_type": wrong,
            "n_invented": inv}


def _table():
    """Two models; empty documents e1-e3 at k = 1; documents d1 (n = 0), d2 (n = 1), d3 (n = 2) at k = 3."""
    rows = []
    for m in ("m1", "m2"):
        # empty documents, k = 1: entries under none / min_k_shown
        for doc, g, s, a, b in (("e1", "g1", "emails", 0, 1), ("e2", "g2", "emails", 1, 1), ("e3", "g3", "clinical", 0, 2)):
            rows.append(_row(m, doc, g, s, "none", 1, 0, a, inv=a))
            rows.append(_row(m, doc, g, s, "min_k_shown", 1, 0, b, wrong=b))
        # n < k at k = 3
        rows.append(_row(m, "d1", "g4", "emails", "none", 3, 0, 0))
        rows.append(_row(m, "d1", "g4", "emails", "min_k_shown", 3, 0, 3, inv=3))
        rows.append(_row(m, "d2", "g5", "emails", "none", 3, 1, 1, true=1))
        rows.append(_row(m, "d2", "g5", "emails", "min_k_shown", 3, 1, 3, true=1, split=1, wrong=1))
        rows.append(_row(m, "d3", "g6", "clinical", "none", 3, 2, 2, true=2))
        rows.append(_row(m, "d3", "g6", "clinical", "min_k_shown", 3, 2, 3, true=2, inv=1))
    return pl.prepare(pd.DataFrame(rows))


def _B(boot=500):
    return fs.Bootstrap(boot, fs.SEED)


def test_false_alarm_level_and_change():
    f = _table()
    lv = pl.level(f, _B(), "none", (1,), "lt_n0", "has_entry", "one")
    assert lv["est"] == 2 / 6 and lv["outputs"] == 6
    lv = pl.level(f, _B(), "min_k_shown", (1,), "lt_n0", "has_entry", "one")
    assert lv["est"] == 1.0
    ch = pl.change(f, _B(), "min_k_shown", "none", (1,), "lt_n0", "has_entry", "one")
    assert abs(ch["est"] - 4 / 6) < 1e-12 and ch["pairs"] == 6


def test_false_alarm_change_is_the_registered_empty_document_test():
    """Same pairs, same draws: identical to full_study's paired has_entry test on the empty documents."""
    rng = np.random.default_rng(3)
    rows = []
    for i in range(40):
        g, s = f"g{i:02d}", ("emails" if i < 15 else "clinical")
        for m in ("m1", "m2", "m3"):
            for c in ("none", "min_k_shown", "prose_up_to_k"):
                for w in (("up_to_1", "up_to_2") if c == "prose_up_to_k" else ("all_1",)):
                    v = int(rng.integers(0, 3))
                    rows.append(_row(m, f"e{i}", g, s, c, 1, 0, v, inv=v, status="ok" if rng.random() > 0.05 else "error",
                                     wording=w))
    f = pl.prepare(pd.DataFrame(rows))
    g = f.copy()
    g["has_entry"] = (g["n_substantive"] >= 1).astype("float32")
    for c in ("min_k_shown", "prose_up_to_k"):
        ref = fs.Bootstrap(2000).mean(fs.paired(g.assign(n_src=g["n"], words=1.0, list_changed=False, split="full"),
                                                c, "none", "has_entry", ks=(1,), cell="lt_n0"))
        mine = pl.change(f, fs.Bootstrap(2000), c, "none", (1,), "lt_n0", "has_entry", "one")
        for k in ("est", "lo", "hi", "p"):
            assert abs(ref[k] - mine[k]) < 1e-9, (c, k, ref[k], mine[k])
        e0 = g[g["ok"] & (g["k"] == 1) & (g["n"] == 0)]
        lv = pl.level(f, fs.Bootstrap(2000), c, (1,), "lt_n0", "has_entry", "one")
        assert abs(lv["est"] - e0[e0["condition"] == c]["has_entry"].mean()) < 1e-12   # full_study's empty_rate


def test_collection_count_is_a_ratio_of_sums():
    f = _table()
    assert pl.level(f, _B(), "none", (3, 5), "lt", "n_substantive", "n")["est"] == (0 + 1 + 2) * 2 / ((0 + 1 + 2) * 2)
    lv = pl.level(f, _B(), "min_k_shown", (3, 5), "lt", "n_substantive", "n")
    assert lv["est"] == 9 * 2 / 6 and lv["num"] == 18 and lv["den"] == 6
    ch = pl.change(f, _B(), "min_k_shown", "none", (3, 5), "lt", "n_substantive", "n")
    assert abs(ch["est"] - 2.0) < 1e-12
    assert ch["lo"] <= ch["est"] <= ch["hi"]


def test_wrong_rows_count_split_entries_as_true():
    f = _table()
    assert pl.level(f, _B(), "none", (3, 5), "lt", "n_wrong", "n_substantive")["est"] == 0.0
    # min_k_shown per model: 3 invented (d1), 1 wrong type (d2; the split entry is true), 1 invented (d3) of 9
    assert abs(pl.level(f, _B(), "min_k_shown", (3, 5), "lt", "n_wrong", "n_substantive")["est"] - 5 / 9) < 1e-12


def test_missing_outputs_are_left_out_and_wordings_averaged():
    f = _table()
    extra = pd.DataFrame([_row("m1", "d2", "g5", "emails", "prose_up_to_k", 3, 1, s, true=min(s, 1), inv=max(0, s - 1),
                               wording=w) for s, w in ((1, "up_to_1"), (3, "up_to_2"))]
                         + [_row("m1", "d3", "g6", "clinical", "prose_up_to_k", 3, 2, 0, status="error")])
    f = pl.prepare(pd.concat([f.drop(columns=["ok", "has_entry", "one", "n_wrong"]), extra], ignore_index=True))
    lv = pl.level(f, _B(), "prose_up_to_k", (3, 5), "lt", "n_substantive", "n")
    assert lv["outputs"] == 2 and lv["est"] == 4 / 2            # two ok outputs, the failure left out
    ch = pl.change(f, _B(), "prose_up_to_k", "none", (3, 5), "lt", "n_substantive", "n")
    assert ch["pairs"] == 1 and abs(ch["est"] - (2.0 / 1 - 1.0 / 1)) < 1e-12   # wordings averaged: 2 entries


def test_labels_must_add_up():
    bad = pd.DataFrame([_row("m1", "d1", "g1", "emails", "none", 3, 1, 2, true=1)])
    try:
        pl.prepare(bad)
    except SystemExit:
        return
    raise AssertionError("prepare accepted labels that do not add up")


def test_run_selection():
    for rid in ("fs_qwen3.5-9b_full", "fs_bedrock-kimi-k3_full", "a1_azure-gpt-6-sol_addendum1",
                "a1_bedrock-grok-4.3_addendum1-enforced"):
        assert pl.RUN_ID.match(rid), rid
    for rid in ("fs_qwen3.5-9b_full-repeat", "fs_gemma-4-31b_full-reask1", "fs_gpt-oss-20b_dev",
                "fs_gemma-4-31b-think_think-filters_s1", "fs_bedrock-kimi-k3-think_pilot", "costtest_x"):
        assert not pl.RUN_ID.match(rid), rid


def test_committed_false_alarm_equals_registered_empty_document_test():
    """Measure 1 for the 8 main models pooled (analysis/downstream/pipeline/headline.json) against the registered
    empty-document numbers of analysis/full/RESULTS.md, rounded as there."""
    head = json.loads((pl.OUT / "headline.json").read_text(encoding="utf-8"))
    assert len(head["_meta"]["main_models"]) == 8 and head["_meta"]["boot"] == 10000
    shares, tests = pl.registered_empty_doc()
    assert shares and tests
    fa = head["false_alarm"]
    for c, v in shares.items():
        assert round(100 * fa[c]["level"], 1) == v, (c, fa[c]["level"], v)
    for c, (e, lo, hi) in tests.items():
        got = tuple(round(100 * fa[c][k], 1) for k in ("change_vs_none", "change_lo", "change_hi"))
        assert got == (e, lo, hi), (c, got, (e, lo, hi))


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
