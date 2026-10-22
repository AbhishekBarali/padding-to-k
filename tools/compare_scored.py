#!/usr/bin/env python3
"""Compare two folders of scored tables (*.outputs.csv.gz), row by row.

    python tools/compare_scored.py analysis/full/scored /tmp/rescored

Rows are matched on (run_id, request_id). The reviews set is reported on its own line, because its
replies are not in the public outputs zip, so a rescore from that zip shows them as missing.
Exits 0 when every row outside the reviews set is identical, 1 otherwise, and 2 on bad arguments
(wrong number, a folder that does not exist, or a first folder with no scored tables).
"""

import csv
import gzip
import sys
from pathlib import Path


def rows(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as f:
        return {(r["run_id"], r["request_id"]): r for r in csv.DictReader(f)}


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print(__doc__)
        return 2
    a_dir, b_dir = Path(argv[0]), Path(argv[1])
    for d in (a_dir, b_dir):
        if not d.is_dir():
            print(f"not a folder: {d}")
            return 2
    a_paths = sorted(a_dir.glob("*.outputs.csv.gz"))
    if not a_paths:
        # Without this, a wrong path compares nothing and reports success.
        print(f"no *.outputs.csv.gz tables in {a_dir}")
        return 2
    same = differ = reviews_differ = 0
    missing_runs = []
    for a_path in a_paths:
        b_path = b_dir / a_path.name
        if not b_path.is_file():
            missing_runs.append(a_path.name)
            continue
        a, b = rows(a_path), rows(b_path)
        for key, row in a.items():
            if b.get(key) == row:
                same += 1
            elif row.get("set") == "reviews":
                reviews_differ += 1
            else:
                differ += 1
                if differ <= 10:
                    print(f"differs: {a_path.name} {key[1]}")
        differ += sum(1 for key in b if key not in a)
    for name in missing_runs:
        print(f"not in {b_dir}: {name}")
    print(f"{same:,} rows identical, {differ:,} rows differ outside the reviews set, "
          f"{reviews_differ:,} reviews-set rows differ")
    return 1 if differ or missing_runs else 0


if __name__ == "__main__":
    sys.exit(main())
