"""Shared helpers for the source loaders in data/sources/.

Every loader module exposes:
    SOURCE: dict             metadata (see REQUIRED_SOURCE_KEYS)
    fetch(cache: Path)       download the pinned raw files into cache/<SOURCE["name"]>/
    units(cache: Path)       yield every candidate unit (see check_unit for the shape)

Loaders only copy what the original annotators wrote. Nothing here creates or edits gold items.
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import tempfile
import urllib.request
from pathlib import Path

DEFAULT_CACHE = Path(os.environ.get("PADK_CACHE", Path.home() / ".cache" / "pad-to-k"))

ITEM_TYPES = {"exact_quote", "named_entity", "vague_theme"}

REQUIRED_SOURCE_KEYS = {
    "name",              # short id, same as the module name
    "title",             # dataset name as its authors call it
    "domain",            # meeting_notes | emails | receipts | job_posts | product_reviews | clinical | wiki | fiction
    "list_types",        # list of list_type values this loader yields
    "url",               # dataset home page
    "paper",             # citation string (authors, year, venue, arXiv/ACL id)
    "licence",           # SPDX-style id, e.g. CC-BY-4.0
    "licence_url",
    "licence_quote",     # the exact sentence from the licence page or file
    "redistributable",   # True if the document text may ship in this repo
    "files",             # [{"url", "sha256", "path"}]  path is relative to cache/<name>/
    "unit_description",  # one plain sentence: what one document is
    "how_gold_was_made", # 2-3 plain sentences: who wrote the item lists and under which guideline
    "known_issues",      # list of plain sentences
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_file(url: str, dest: Path, sha256: str | None = None) -> Path:
    """Download url to dest once, then verify the pinned sha256 (if given)."""
    dest = Path(dest)
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "pad-to-k-data-build/1.0"})
        with urllib.request.urlopen(req, timeout=300) as r, tempfile.NamedTemporaryFile(
            dir=dest.parent, delete=False
        ) as tmp:
            shutil.copyfileobj(r, tmp)
            tmp_path = Path(tmp.name)
        tmp_path.replace(dest)
    if sha256:
        got = sha256_file(dest)
        if got != sha256:
            raise RuntimeError(f"sha256 mismatch for {dest}: expected {sha256}, got {got}")
    return dest


def fetch_all(source: dict, cache: Path) -> Path:
    """Fetch every file listed in source['files'] into cache/<name>/ and return that dir."""
    root = Path(cache) / source["name"]
    for f in source["files"]:
        fetch_file(f["url"], root / f["path"], f.get("sha256"))
    return root


def words(text: str) -> int:
    return len(re.findall(r"\S+", text))


def check_source(source: dict) -> None:
    missing = REQUIRED_SOURCE_KEYS - set(source)
    if missing:
        raise ValueError(f"SOURCE missing keys: {sorted(missing)}")


def check_unit(u: dict) -> None:
    """Raise ValueError if a unit breaks the shared contract."""
    for key in ("source_id", "group", "text", "n", "gold_items", "list_type", "item_type", "flags", "meta"):
        if key not in u:
            raise ValueError(f"{u.get('source_id')}: missing {key}")
    if u["item_type"] not in ITEM_TYPES:
        raise ValueError(f"{u['source_id']}: bad item_type {u['item_type']}")
    if not isinstance(u["text"], str) or not u["text"].strip():
        raise ValueError(f"{u['source_id']}: empty text")
    if u["n"] != len(u["gold_items"]):
        raise ValueError(f"{u['source_id']}: n={u['n']} but {len(u['gold_items'])} gold items")
    seen = set()
    for g in u["gold_items"]:
        t = g.get("text", "")
        if not t.strip():
            raise ValueError(f"{u['source_id']}: empty gold item")
        key = t.strip().lower()
        if key in seen:
            raise ValueError(f"{u['source_id']}: duplicate gold item {t!r}")
        seen.add(key)
        s, e = g.get("start"), g.get("end")
        if s is not None:
            if u["text"][s:e] != t:
                raise ValueError(f"{u['source_id']}: span mismatch {u['text'][s:e]!r} != {t!r}")
        else:
            ev = g.get("evidence") or []
            for x in ev:
                if u["text"][x["start"]:x["end"]] != x["text"]:
                    raise ValueError(f"{u['source_id']}: evidence span mismatch for {t!r}")
            if not ev and "no_evidence_span" not in u["flags"]:
                raise ValueError(f"{u['source_id']}: abstractive item {t!r} has no evidence and no flag")
    if not isinstance(u["flags"], list):
        raise ValueError(f"{u['source_id']}: flags must be a list")
