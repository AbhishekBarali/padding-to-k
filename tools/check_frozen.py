#!/usr/bin/env python3
"""Check that every file the registered plan froze is unchanged.

preregistration/manifest-stage2.sha256 holds the SHA-256 of every file under data/, configs/,
harness/, analysis/ and preregistration/ at the moment the plan was registered (git tag prereg-v2.1);
the same manifest is on OSF. Run from the repository root:

    python tools/check_frozen.py

Exits 0 when every listed file is present and matches, 1 otherwise. A file whose only difference is
CRLF line endings (a Git checkout with core.autocrlf on Windows) is reported as EOL-ONLY with a hint;
it still counts as a mismatch, because the registered hash is of the exact bytes.
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


def lf_sha256(path: Path) -> str:
    """Hash of the file with CRLF line endings turned into LF."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main(root: Path = ROOT, manifest: Path = MANIFEST) -> int:
    ok, changed, eol_only, missing = 0, [], [], []
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        digest, rel = line.split(None, 1)
        rel = rel.strip()
        path = root / rel
        if not path.is_file():
            missing.append(rel)
        elif sha256(path) == digest:
            ok += 1
        elif lf_sha256(path) == digest:
            eol_only.append(rel)
        else:
            changed.append(rel)
    for rel in changed:
        print(f"CHANGED  {rel}")
    for rel in eol_only:
        print(f"EOL-ONLY {rel}")
    for rel in missing:
        print(f"MISSING  {rel}")
    total = ok + len(changed) + len(eol_only) + len(missing)
    print(f"{ok} of {total} registered files match {manifest.relative_to(root)}")
    if eol_only:
        print(f"{len(eol_only)} files differ only in line endings. The repository's .gitattributes turns "
              "conversion off; to refresh a checkout made before it, delete those files and run "
              "`git checkout -- .`")
    return 1 if changed or eol_only or missing else 0


if __name__ == "__main__":
    sys.exit(main())
