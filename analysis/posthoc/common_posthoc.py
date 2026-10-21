"""POST HOC (not in the registered plan): shared helpers for analysis/posthoc/*.py.

Nothing here changes the locked scorer: parsing is harness/common.py, labels are the cached matcher v0 labels
written by analysis/full_study_score.py into analysis/full/scored/ (checked against the run folders by
analysis/posthoc/check_cache.py).
"""
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "harness"), str(ROOT / "analysis")]
import common  # noqa: E402
import full_study  # noqa: E402

POSTHOC = ROOT / "analysis" / "posthoc"
OUT = POSTHOC / "out"
CACHE = POSTHOC / "cache"          # gitignored: holds entry text (restricted reviews included)
SCORED = ROOT / "analysis" / "full" / "scored"
EXTRA = ("split_of_true", "in_text_wrong_type", "plausible_invented")
SUBST = ("true_item",) + EXTRA
LABEL_NAME = {"true_item": "true item", "split_of_true": "true-but-split", "in_text_wrong_type": "wrong kind",
              "plausible_invented": "invented", "placeholder": "placeholder", "repeat": "repeat"}


def lineup():
    main, hosted, _, _ = full_study.lineup()
    return main, hosted


def main_runs():
    """The fs_<model>_full runs, GPU main models then hosted models (the same run folders full_study uses)."""
    main, hosted = lineup()
    return [f"fs_{m}_full" for m in main + hosted], main, hosted


_DASH = re.compile(r"[\u2010-\u2015\u2212]")
_WS = re.compile(r"\s+")
_EDGE = " \t\n\"'`.,;:!?*-\u2022\u00b7()[]"


def gnorm(s):
    """Normalisation for the grounding check a developer could deploy: Unicode NFKC, curly quotes and dashes
    made plain, lower case, whitespace collapsed, quotes / punctuation / bullets stripped from both ends."""
    s = unicodedata.normalize("NFKC", str(s))
    s = s.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    s = _DASH.sub("-", s)
    s = _WS.sub(" ", s.lower()).strip()
    return s.strip(_EDGE)


def restricted_sets():
    return {"reviews"}
