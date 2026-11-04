"""Tests for tools/check_frozen.py. Run: python -m pytest tools/tests"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check_frozen  # noqa: E402


def _setup(tmp_path: Path, files: dict[str, bytes]) -> Path:
    """Write the files and a manifest that registers their current bytes."""
    lines = ["# root: data"]
    for rel, data in files.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        lines.append(f"{hashlib.sha256(data).hexdigest()}  {rel}")
    manifest = tmp_path / "manifest.sha256"
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return manifest


def test_all_match(tmp_path, capsys):
    manifest = _setup(tmp_path, {"data/a.txt": b"one\ntwo\n", "data/b.bin": b"\x00\x01"})
    assert check_frozen.main(tmp_path, manifest) == 0
    assert "2 of 2 registered files match" in capsys.readouterr().out


def test_changed_file(tmp_path, capsys):
    manifest = _setup(tmp_path, {"data/a.txt": b"one\n"})
    (tmp_path / "data/a.txt").write_bytes(b"uno\n")
    assert check_frozen.main(tmp_path, manifest) == 1
    assert "CHANGED  data/a.txt" in capsys.readouterr().out


def test_missing_file(tmp_path, capsys):
    manifest = _setup(tmp_path, {"data/a.txt": b"one\n"})
    (tmp_path / "data/a.txt").unlink()
    assert check_frozen.main(tmp_path, manifest) == 1
    assert "MISSING  data/a.txt" in capsys.readouterr().out


def test_crlf_only_is_reported_and_fails(tmp_path, capsys):
    manifest = _setup(tmp_path, {"data/a.txt": b"one\ntwo\n"})
    (tmp_path / "data/a.txt").write_bytes(b"one\r\ntwo\r\n")
    assert check_frozen.main(tmp_path, manifest) == 1
    out = capsys.readouterr().out
    assert "EOL-ONLY data/a.txt" in out
    assert "CHANGED" not in out
    assert "differ only in line endings" in out


def test_registered_crlf_file_matches(tmp_path):
    # A file registered with CRLF (some CSVs in the repository are) must match as is.
    manifest = _setup(tmp_path, {"data/a.csv": b"x,y\r\n1,2\r\n"})
    assert check_frozen.main(tmp_path, manifest) == 0


def _declare(tmp_path: Path, rel: str, registered: bytes, current: bytes, original: bytes) -> None:
    """Declare rel as changed after registration and store `original` as its registered copy."""
    copy = f"preregistration/registered-files/{rel}"
    (tmp_path / copy).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / copy).write_bytes(original)
    row = {"path": rel, "registered_sha256": hashlib.sha256(registered).hexdigest(),
           "current_sha256": hashlib.sha256(current).hexdigest(), "reason": "test", "registered_copy": copy}
    (tmp_path / check_frozen.DECLARED).write_text(json.dumps({"files": [row]}), encoding="utf-8")


def test_declared_change_passes(tmp_path, capsys):
    manifest = _setup(tmp_path, {"data/a.txt": b"one\n", "data/b.txt": b"two\n"})
    (tmp_path / "data/a.txt").write_bytes(b"uno\n")
    _declare(tmp_path, "data/a.txt", b"one\n", b"uno\n", b"one\n")
    assert check_frozen.main(tmp_path, manifest) == 0
    out = capsys.readouterr().out
    assert "DECLARED data/a.txt: changed after registration (declared)" in out
    assert "1 of 2 registered files match" in out
    assert "CHANGED" not in out


def test_undeclared_change_fails(tmp_path, capsys):
    manifest = _setup(tmp_path, {"data/a.txt": b"one\n", "data/b.txt": b"two\n"})
    (tmp_path / "data/a.txt").write_bytes(b"uno\n")
    (tmp_path / "data/b.txt").write_bytes(b"dos\n")
    _declare(tmp_path, "data/a.txt", b"one\n", b"uno\n", b"one\n")
    assert check_frozen.main(tmp_path, manifest) == 1
    assert "CHANGED  data/b.txt" in capsys.readouterr().out


def test_declared_original_not_matching_manifest_fails(tmp_path, capsys):
    manifest = _setup(tmp_path, {"data/a.txt": b"one\n"})
    (tmp_path / "data/a.txt").write_bytes(b"uno\n")
    _declare(tmp_path, "data/a.txt", b"one\n", b"uno\n", b"not the original\n")
    assert check_frozen.main(tmp_path, manifest) == 1
    out = capsys.readouterr().out
    assert "CHANGED  preregistration/registered-files/data/a.txt (registered original of data/a.txt)" in out
    assert "DECLARED" not in out


def test_declared_file_not_at_declared_hash_fails(tmp_path, capsys):
    manifest = _setup(tmp_path, {"data/a.txt": b"one\n"})
    (tmp_path / "data/a.txt").write_bytes(b"tres\n")
    _declare(tmp_path, "data/a.txt", b"one\n", b"uno\n", b"one\n")
    assert check_frozen.main(tmp_path, manifest) == 1
    out = capsys.readouterr().out
    assert "CHANGED  data/a.txt (not the declared current version)" in out
    assert "DECLARED" not in out


def test_real_manifest_is_well_formed():
    # Every entry is "<64 hex digits>  <path under a frozen folder>", with no duplicates.
    frozen = ("analysis/", "configs/", "data/", "harness/", "preregistration/")
    seen = set()
    for line in check_frozen.MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        digest, rel = line.split(None, 1)
        assert len(digest) == 64 and all(c in "0123456789abcdef" for c in digest), line
        assert rel.startswith(frozen), line
        assert rel not in seen, line
        seen.add(rel)
    assert seen
