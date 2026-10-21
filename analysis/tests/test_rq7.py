"""Tests for analysis/rq7.py's AUROC. Run: python3 analysis/tests/test_rq7.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import rq7  # noqa: E402


def test_auroc_extremes_and_ties():
    assert rq7.auroc([-3.0, -2.0], [-1.0, -0.5]) == 1.0      # every extra entry scores lower
    assert rq7.auroc([-0.1, 0.0], [-3.0, -2.0]) == 0.0       # every extra entry scores higher
    assert rq7.auroc([-1.0, -1.0], [-1.0]) == 0.5            # all tied
    assert rq7.auroc([-2.0, 0.0], [-1.0]) == 0.5             # one below, one above
    assert rq7.auroc([], [-1.0]) is None


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
