#!/usr/bin/env python3
"""Check that every file the registered plan froze is unchanged.

preregistration/manifest-stage2.sha256 holds the SHA-256 of every file under data/, configs/,
harness/, analysis/ and preregistration/ at the moment the plan was registered (git tag prereg-v2.1);
the same manifest is on OSF. Run from the repository root:

    python tools/check_frozen.py

Exits 0 when every listed file is present and matches, 1 otherwise. A file whose only difference is
CRLF line endings (a Git checkout with core.autocrlf on Windows) is reported as EOL-ONLY with a hint;
it still counts as a mismatch, because the registered hash is of the exact bytes.

A registered file changed after registration (for OSF addendum 1) passes only when
preregistration/changed-after-registration.json declares it: its registered original, kept under
preregistration/registered-files/, must match the manifest, and the live file must match the
declared current hash. Any other difference still fails.
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "preregistration" / "manifest-stage2.sha256"
DECLARED = "preregistration/changed-after-registration.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def lf_sha256(path: Path) -> str:
    """Hash of the file with CRLF line endings turned into LF."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def status(path: Path, digest: str) -> str:
    if not path.is_file():
        return "MISSING"
    if sha256(path) == digest:
        return "OK"
    return "EOL-ONLY" if lf_sha256(path) == digest else "CHANGED"


def main(root: Path = ROOT, manifest: Path = MANIFEST) -> int:
    found = {"CHANGED": [], "EOL-ONLY": [], "MISSING": []}
    ok, total, declared_ok = 0, 0, []
    declaration = root / DECLARED
    declared = {}
    if declaration.is_file():
        declared = {row["path"]: row for row in json.loads(declaration.read_text(encoding="utf-8"))["files"]}
    registered = set()
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        digest, rel = line.split(None, 1)
        rel = rel.strip()
        registered.add(rel)
        total += 1
        row = declared.get(rel)
        if row is None:
            result = status(root / rel, digest)
            if result == "OK":
                ok += 1
            else:
                found[result].append(rel)
            continue
        # Declared: the stored original carries the registered hash, the live file the declared one.
        original = status(root / row["registered_copy"], digest)
        live = status(root / rel, row["current_sha256"])
        if row["registered_sha256"] != digest:
            found["CHANGED"].append(f"{rel} (declared with a registered hash the manifest does not have)")
        elif original != "OK":
            found[original].append(f"{row['registered_copy']} (registered original of {rel})")
        elif live != "OK":
            found[live].append(rel if live == "MISSING" else f"{rel} (not the declared current version)")
        else:
            declared_ok.append(rel)
    for rel in sorted(set(declared) - registered):
        found["CHANGED"].append(f"{rel} (declared in {DECLARED}, but not a registered file)")
    for rel in declared_ok:
        print(f"DECLARED {rel}: changed after registration (declared); "
              f"its registered original {declared[rel]['registered_copy']} matches")
    for kind in ("CHANGED", "EOL-ONLY", "MISSING"):
        for rel in found[kind]:
            print(f"{kind:<8} {rel}")
    summary = f"{ok} of {total} registered files match {manifest.relative_to(root)}"
    if declared_ok:
        summary += f"; {len(declared_ok)} changed after registration (declared), checked through their originals"
    print(summary)
    if found["EOL-ONLY"]:
        print(f"{len(found['EOL-ONLY'])} files differ only in line endings. The repository's .gitattributes turns "
              "conversion off; to refresh a checkout made before it, delete those files and run "
              "`git checkout -- .`")
    return 1 if any(found.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
