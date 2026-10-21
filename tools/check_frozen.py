#!/usr/bin/env python3
"""Check that every file the registered plan froze is unchanged.

preregistration/manifest-stage2.sha256 holds the SHA-256 of every file under data/, configs/,
harness/, analysis/ and preregistration/ at the moment the plan was registered (git tag prereg-v2.1);
the same manifest is on OSF. Run from the repository root:

    python tools/check_frozen.py

Exits 0 when every listed file is present and matches, 1 otherwise.
"""

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "preregistration" / "manifest-stage2.sha256"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    ok, changed, missing = 0, [], []
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        digest, rel = line.split(None, 1)
        path = ROOT / rel.strip()
        if not path.is_file():
            missing.append(rel.strip())
        elif sha256(path) != digest:
            changed.append(rel.strip())
        else:
            ok += 1
    for rel in changed:
        print(f"CHANGED  {rel}")
    for rel in missing:
        print(f"MISSING  {rel}")
    print(f"{ok} of {ok + len(changed) + len(missing)} registered files match {MANIFEST.relative_to(ROOT)}")
    return 1 if changed or missing else 0


if __name__ == "__main__":
    sys.exit(main())
