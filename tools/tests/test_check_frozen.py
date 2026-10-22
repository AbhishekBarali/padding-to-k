"""Tests for tools/check_frozen.py. Run: python -m pytest tools/tests"""
import hashlib
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
