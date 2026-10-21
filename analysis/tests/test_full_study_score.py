"""Tests for analysis/full_study_score.py. Run: python analysis/tests/test_full_study_score.py (or pytest).

The run-record test needs one full-study run folder; it uses $PADK_FS_RUNS (default: fs-runs/ next to the repo) and
is skipped when no run folder is there.
"""
import gzip
import csv
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import full_study_score as fss  # noqa: E402

sys.path.insert(0, str(HERE.parent.parent / "harness"))
import common  # noqa: E402
import score_counts  # noqa: E402

FS_RUNS = Path(os.environ.get("PADK_FS_RUNS", str(HERE.parent.parent.parent / "fs-runs")))
DOC = {"doc_id": "t-1", "text": "Please send the report. Also call Anna about the budget.", "set": "emails"}


def test_outside_note_reads_sentences_outside_the_json():
    reply = 'Here is the list.\n```json\n{"requests": ["send the report"]}\n```\nNote: only one request in this email.'
    assert fss.outside_text(reply).startswith("Here is the list.")
    assert "send the report" not in fss.outside_text(reply)
    assert fss.outside_note(reply, DOC["text"], "N/A")              # "only one request ..." after the colon
    assert not fss.outside_note('{"requests": ["send the report"]}', DOC["text"], "N/A")
    assert not fss.outside_note('Sure! {"requests": []}', DOC["text"], "N/A")


def test_outside_note_ignores_document_text():
    # a sentence copied from the document is document text, never a note (common.is_placeholder's guard)
    doc = {"text": "Only one more day until the launch."}
    assert not fss.outside_note('{"quotes": []}\nOnly one more day until the launch.', doc["text"], "N/A")


def test_placeholder_bound_counts_short_entries_with_the_words():
    assert fss.bound_count(["No other requests found", "Send the report"]) == 1
    assert fss.bound_count(["Do not forget to send the full quarterly report to the whole team today"]) == 0
    assert fss.bound_count(["Nothing else"]) == 0      # none of the seven words


def test_shortfall_phrase():
    assert fss.SHORTFALL.search("The email only has two requests, but three are needed.")
    assert fss.SHORTFALL.search("there are fewer than 3 items")
    assert not fss.SHORTFALL.search("I list the three requests in order.")


def _one_run():
    if not FS_RUNS.exists():
        return None
    for name in ("fs_qwen3.5-9b_full-repeat", "fs_gemma-4-31b_full-repeat"):
        if (FS_RUNS / name / "manifest.json").exists():
            return FS_RUNS / name
    return None


def test_counts_equal_score_counts_row_by_row():
    run = _one_run()
    if run is None:
        print("skip: no run folder")
        return
    with tempfile.TemporaryDirectory() as tmp:
        fss.score_run(run, tmp, force=True)
        mine = {r["request_id"]: r for r in csv.DictReader(gzip.open(Path(tmp) / f"{run.name}.outputs.csv.gz", "rt"))}
    prompts, docs = common.load_prompts(), common.load_documents()
    req = {r["request_id"]: r for r in common.load_requests()}
    theirs = score_counts.expand(str(run), prompts, docs, req)
    assert len(theirs) == len(mine)
    keys = ["status", "parse_rung", "valid", "n_items", "n_substantive", "n_placeholder", "n_escape", "n_duplicate",
            "over_count", "excess", "exact_k", "fewer_than_k", "more_than_k", "truncated", "condition", "k", "n"]
    for t in theirs:
        m = mine[t["request_id"]]
        for key in keys:
            if key in t:
                assert str(t[key]) == m[key], (t["request_id"], key, t[key], m[key])
        if m["status"] == "ok":
            n = int(m["n"])
            assert int(m["left_out"]) == n - int(m["matched_gold"]) and 0 <= int(m["matched_gold"]) <= n
            if int(m["k"]) > n:
                assert m["sort"] in ("padded", "says_short", "honest_short", "unreadable")
                assert (m["sort"] == "padded") == (m["over_count"] == "True")
                assert (m["sort"] == "unreadable") == (m["valid"] == "False")
            else:
                assert m["sort"] == ""


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
