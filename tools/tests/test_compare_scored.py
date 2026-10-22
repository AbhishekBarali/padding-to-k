"""Tests for tools/compare_scored.py. Run: python -m pytest tools/tests"""
import csv
import gzip
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import compare_scored  # noqa: E402

FIELDS = ["run_id", "request_id", "set", "n_items"]


def _table(folder: Path, name: str, rows: list[dict]) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    with gzip.open(folder / f"{name}.outputs.csv.gz", "wt", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def _row(req: str, set_: str = "meetings", n: int = 3) -> dict:
    return {"run_id": "r1", "request_id": req, "set": set_, "n_items": n}


def test_identical(tmp_path, capsys):
    rows = [_row("q1"), _row("q2")]
    _table(tmp_path / "a", "run1", rows)
    _table(tmp_path / "b", "run1", rows)
    assert compare_scored.main([str(tmp_path / "a"), str(tmp_path / "b")]) == 0
    assert "2 rows identical, 0 rows differ" in capsys.readouterr().out


def test_differing_row(tmp_path, capsys):
    _table(tmp_path / "a", "run1", [_row("q1", n=3)])
    _table(tmp_path / "b", "run1", [_row("q1", n=4)])
    assert compare_scored.main([str(tmp_path / "a"), str(tmp_path / "b")]) == 1
    assert "differs: run1.outputs.csv.gz q1" in capsys.readouterr().out


def test_reviews_rows_do_not_fail(tmp_path, capsys):
    # Replies on the reviews set are not in the public zip, so they are counted apart.
    _table(tmp_path / "a", "run1", [_row("q1"), _row("q2", set_="reviews")])
    _table(tmp_path / "b", "run1", [_row("q1")])
    assert compare_scored.main([str(tmp_path / "a"), str(tmp_path / "b")]) == 0
    assert "1 reviews-set rows differ" in capsys.readouterr().out


def test_extra_row_in_second_folder_fails(tmp_path):
    _table(tmp_path / "a", "run1", [_row("q1")])
    _table(tmp_path / "b", "run1", [_row("q1"), _row("q9")])
    assert compare_scored.main([str(tmp_path / "a"), str(tmp_path / "b")]) == 1


def test_missing_run_fails(tmp_path, capsys):
    _table(tmp_path / "a", "run1", [_row("q1")])
    (tmp_path / "b").mkdir()
    assert compare_scored.main([str(tmp_path / "a"), str(tmp_path / "b")]) == 1
    assert "run1.outputs.csv.gz" in capsys.readouterr().out


def test_bad_arguments(tmp_path, capsys):
    (tmp_path / "empty").mkdir()
    assert compare_scored.main([]) == 2
    assert compare_scored.main([str(tmp_path / "nope"), str(tmp_path / "empty")]) == 2
    assert "not a folder" in capsys.readouterr().out
    assert compare_scored.main([str(tmp_path / "empty"), str(tmp_path / "empty")]) == 2
    assert "no *.outputs.csv.gz tables" in capsys.readouterr().out
