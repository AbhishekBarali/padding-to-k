"""CORD v2 receipts (naver-clova-ix/cord-v2) -> Pad to k units.

One unit = one receipt. Text = the receipt rebuilt from the annotators' OCR word boxes
(`valid_line`): words grouped into the annotated rows (`row_id`), rows sorted top to bottom by
mean y, words left to right by x, one receipt row per text line. Gold = every menu item name
(`menu.nm`, key words such as "Jenis BBM" excluded, exactly as in the published `gt_parse`).

fetch() does NOT download the 2.3 GB of parquet (most of it is images). It range-reads only the
`ground_truth` column of each pinned parquet file over HTTP and writes it to a small JSONL file
whose sha256 is pinned below. The remote file size is checked against the pinned LFS size.
"""
from __future__ import annotations

import io
import json
import os
import re
import statistics
import sys
import time
from collections import Counter, OrderedDict
from pathlib import Path

try:
    from . import _common
except ImportError:  # pragma: no cover - direct script use
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import _common  # type: ignore

REPO = "naver-clova-ix/cord-v2"
REVISION = "7f0115a4b758a71d6473b8d085751692da2fef98"
_BASE = f"https://huggingface.co/datasets/{REPO}/resolve/{REVISION}/"

# (parquet path in the repo, LFS sha256 of the full parquet, size in bytes, sha256 of our extract)
_PARQUETS = [
    ("data/test-00000-of-00001-9c204eb3f4e11791.parquet",
     "51c65f1788faff392abe2a0b55b023eb23e9be551c509138eaa3a832514224e7", 234202795, "2f1e51a42c47e01e34da1c23cbca9563aaad3804804b01c77eee921d6e4ea3be"),
    ("data/train-00000-of-00004-b4aaeceff1d90ecb.parquet",
     "da3994eee1bf9bd3c57f0d53a72c3a6812c8696c5ba26245987949ddf73483cc", 490224630, "ac5954d495f31eee173d9e96bfa65cd0fc8e59b0985ecd7d6d8641e81b644082"),
    ("data/train-00001-of-00004-7dbbe248962764c5.parquet",
     "cce4def16a0d6a6c75f80be712f7494c56c318a8829b712f5c62650155c9e58e", 441418432, "5636c59c804a33452cc46364e7ed84a3308a515077e1dfbe9aae96968cfc8139"),
    ("data/train-00002-of-00004-688fe1305a55e5cc.parquet",
     "591e2db8fe8b1d364b054f46e8c375b7f00e72578914ba46a573b6858162cab2", 443802181, "536ad2b1fc9d22f0a7ec64cc3066388b0f8b7e63c9a9c1b380b2e1cec84ffab4"),
    ("data/train-00003-of-00004-2d0cd200555ed7fd.parquet",
     "1ffd9de8d6fbcee7630fd4cdfedff05b9b7fabc0fae4fc17557c5fe7cf178748", 455555434, "9c1e5abe2b62106a633bb2884aa035044caf3a2c77e0e813b8382d36156960f5"),
    ("data/validation-00000-of-00001-cc3c5779fe22e8ca.parquet",
     "0d0f6dac11fdcc549de2746aa9f53136a3bc22a2a1aff2b0b847f7622ad60c15", 242080800, "e6050eec3a8d7fda68c350cd5d71636bfb03585fb6d205988f537024077e24a7"),
]

# Categories whose words print the number of items / total quantity on the receipt.
COUNT_LEAK_CATEGORIES = {"total.menuqty_cnt", "total.menutype_cnt"}
# SPEC rule 4 says 15 words minimum; CORD texts are tiny (218 n=1 receipts fall under it), so the
# floor can be lowered for a sensitivity run with PADK_CORD_MIN_WORDS (default stays 15).
MIN_WORDS = int(os.environ.get("PADK_CORD_MIN_WORDS", "15"))
MAX_WORDS, MAX_N = 900, 8

SOURCE = {
    "name": "cord",
    "title": "CORD: A Consolidated Receipt Dataset for Post-OCR Parsing (v2)",
    "domain": "receipts",
    "list_types": ["line_items"],
    "url": "https://huggingface.co/datasets/naver-clova-ix/cord-v2",
    "paper": ("Park, Shin, Lee, Lee, Surh, Seo, Lee. CORD: A Consolidated Receipt Dataset for "
              "Post-OCR Parsing. Document Intelligence Workshop at NeurIPS 2019. "
              "OpenReview SJl3z659UH."),
    "licence": "CC-BY-4.0",
    "licence_url": "https://github.com/clovaai/cord/blob/master/LICENSE-CC-BY",
    "licence_quote": ("This work is licensed under a Creative Commons Attribution 4.0 "
                      "International License."),
    "redistributable": True,
    "files": [],  # filled below
    "unit_description": ("One Indonesian shop or restaurant receipt, rebuilt as plain text from the "
                         "annotated OCR words (menu, subtotal and total area only)."),
    "how_gold_was_made": ("Clova AI annotators drew word boxes on each receipt photo, typed the "
                          "text, and labelled every word with a class (menu.nm, menu.cnt, "
                          "menu.price, total.total_price ...), grouping the words of one purchased "
                          "item with a shared group id. Gold here is the menu.nm text of each item "
                          "group, i.e. the item names in the published gt_parse.menu list."),
    "known_issues": [
        "Store name, address and payment details were removed by the dataset authors for legal "
        "reasons, so texts are only the item / total block and are short.",
        "Sub-items (toppings, modifiers, set contents; menu.sub.nm) are printed as their own "
        "lines but are not gold items; units carrying them are flagged has_sub_items.",
        "Text is OCR-like (abbreviations, typos such as CHIKEN, split words) because it is the "
        "annotators' transcription of a photo.",
        "Reading order comes from the annotated rows; a visual line annotated as two rows becomes "
        "two text lines.",
        "Printed item-count / total-quantity fields (total.menuqty_cnt, total.menutype_cnt) were "
        "removed from the text (flag count_leak_stripped); a few unlabelled count-like strings "
        "may remain (flag possible_count_leak_unlabelled).",
        "Discounted, free (price 0) and voided lines stay in the text; free items are still gold "
        "because annotators labelled them menu.nm.",
    ],
}


def _extract_name(pq_path: str) -> str:
    return "gt/" + Path(pq_path).stem + ".ground_truth.jsonl"


SOURCE["files"] = [
    {
        "url": _BASE + p,
        "sha256": ext_sha,
        "path": _extract_name(p),
        "parquet_lfs_sha256": lfs,
        "parquet_size": size,
        "note": "range-read of the ground_truth column only; sha256 is of the extracted JSONL",
    }
    for p, lfs, size, ext_sha in _PARQUETS
]


# --------------------------------------------------------------------------- fetch

class _HttpRangeFile(io.RawIOBase):
    """Minimal seekable read-only file over HTTP range requests (enough for pyarrow)."""

    def __init__(self, url: str):
        import requests

        self._rq = requests
        self.url = url
        self.pos = 0
        h = self._get(url, "bytes=0-0")
        self.size = int(h.headers["Content-Range"].split("/")[1])
        self.final = h.url  # signed CDN URL after redirect

    def _get(self, url, rng, tries=4):
        for i in range(tries):
            try:
                r = self._rq.get(url, headers={"Range": rng, "User-Agent": "pad-to-k-data-build/1.0"},
                                 timeout=120, allow_redirects=True)
                if r.status_code == 206:
                    return r
                raise RuntimeError(f"HTTP {r.status_code} for range {rng}")
            except Exception:
                if i == tries - 1:
                    raise
                time.sleep(2 * (i + 1))
                if url is not self.url and hasattr(self, "final"):
                    url = self.url  # signed URL may have expired: resolve again

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=0):
        self.pos = off if whence == 0 else (self.pos + off if whence == 1 else self.size + off)
        return self.pos

    def read(self, k=-1):
        if k is None or k < 0:
            k = self.size - self.pos
        if k == 0 or self.pos >= self.size:
            return b""
        end = min(self.size, self.pos + k) - 1
        d = self._get(self.final, f"bytes={self.pos}-{end}").content
        self.pos += len(d)
        return d

    def readinto(self, b):
        d = self.read(len(b))
        b[: len(d)] = d
        return len(d)


def fetch(cache: Path) -> Path:
    """Range-read the ground_truth column of every pinned parquet into cache/cord/gt/*.jsonl."""
    import pyarrow.parquet as pq

    root = Path(cache) / SOURCE["name"]
    for f in SOURCE["files"]:
        dest = root / f["path"]
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            hf = _HttpRangeFile(f["url"])
            if f.get("parquet_size") and hf.size != f["parquet_size"]:
                raise RuntimeError(f"size mismatch for {f['url']}: {hf.size} != {f['parquet_size']}")
            table = pq.ParquetFile(hf).read(columns=["ground_truth"])
            tmp = dest.with_suffix(".part")
            with open(tmp, "w", encoding="utf-8") as out:
                for row, gt in enumerate(table.column("ground_truth").to_pylist()):
                    out.write(json.dumps({"row": row, "ground_truth": gt}, ensure_ascii=False) + "\n")
            tmp.replace(dest)
        if f.get("sha256"):
            got = _common.sha256_file(dest)
            if got != f["sha256"]:
                raise RuntimeError(f"sha256 mismatch for {dest}: expected {f['sha256']}, got {got}")
    return root


# --------------------------------------------------------------------------- text rebuild

_WS = re.compile(r"\s+")
# Count-like words that might survive outside the labelled count fields.
_COUNT_WORD = re.compile(r"(?i)(\bitems?\b|\bitem\(s\)|\bqty\b|\bquantity\b|\bjumlah\b|\bjml\b|\bitm\b|"
                         r"\bpcs\b|\bpurchased\b)")
_SMALL_INT = re.compile(r"(?<![\d.,])\d{1,2}(?:\.0+)?(?![\d,]|\.\d*[1-9])")


def _cx(q):
    return (q["x1"] + q["x2"] + q["x3"] + q["x4"]) / 4.0


def _cy(q):
    return (q["y1"] + q["y2"] + q["y3"] + q["y4"]) / 4.0


def _rebuild(gt: dict):
    """Return (text, word_pos, stripped, ws_fixed).

    word_pos maps (entry_idx, word_idx) -> (line_no, order_in_line, start, end).
    stripped lists the removed count-leak strings.
    """
    words = []
    stripped = []
    ws_fixed = False
    for ei, v in enumerate(gt["valid_line"]):
        if v["category"] in COUNT_LEAK_CATEGORIES:
            stripped.append(" ".join(_WS.sub(" ", w["text"]).strip() for w in v["words"]))
            continue
        for wi, w in enumerate(v["words"]):
            t = _WS.sub(" ", w["text"]).strip()
            if t != w["text"]:
                ws_fixed = True
            if not t:
                continue
            words.append((w["row_id"], _cx(w["quad"]), _cy(w["quad"]), t, ei, wi))
    rows = OrderedDict()
    for w in words:
        rows.setdefault(w[0], []).append(w)
    ordered = sorted(rows.items(), key=lambda kv: (statistics.fmean(x[2] for x in kv[1]), kv[0]))
    lines, pos, off = [], {}, 0
    for ln, (_, ws) in enumerate(ordered):
        ws.sort(key=lambda x: (x[1], x[2]))
        parts = []
        for k, w in enumerate(ws):
            if parts:
                off += 1
            pos[(w[4], w[5])] = (ln, k, off, off + len(w[3]))
            parts.append(w[3])
            off += len(w[3])
        lines.append(" ".join(parts))
        off += 1  # newline
    return "\n".join(lines), pos, stripped, ws_fixed


def _menu_items(gt: dict):
    """Item groups in valid_line order: list of dicts with nm entries and flags."""
    groups = OrderedDict()
    for ei, v in enumerate(gt["valid_line"]):
        c = v["category"]
        if not c.startswith("menu."):
            continue
        g = groups.setdefault(v["group_id"], {"nm": [], "sub": False, "cats": set()})
        g["cats"].add(c)
        if c == "menu.nm":
            g["nm"].append(ei)
        elif c.startswith("menu.sub."):
            g["sub"] = True
    return list(groups.values())


def _gt_parse_menu(gt: dict):
    m = gt["gt_parse"].get("menu", [])
    return [m] if isinstance(m, dict) else list(m)


def _norm(s: str) -> str:
    return _WS.sub(" ", s).strip()


def _receipts(cache: Path):
    root = Path(cache) / SOURCE["name"]
    for f in SOURCE["files"]:
        fname = Path(f["path"]).name
        with open(root / f["path"], encoding="utf-8") as fh:
            for line in fh:
                rec = json.loads(line)
                yield fname, rec["row"], json.loads(rec["ground_truth"])


def units(cache: Path, stats: Counter | None = None):
    """Yield one unit per usable receipt. `stats` (optional) collects drop reasons."""
    stats = stats if stats is not None else Counter()
    for fname, row, gt in _receipts(cache):
        stats["receipts_seen"] += 1
        meta_in = gt["meta"]
        split = meta_in["split"]
        image_id = meta_in["image_id"]
        sid = f"cord-v2@{REVISION[:7]}:{split}/image_id={image_id}"
        text, pos, stripped, ws_fixed = _rebuild(gt)
        groups = _menu_items(gt)
        published = _gt_parse_menu(gt)
        if len(groups) != len(published):
            stats["drop:menu_groups_disagree_with_gt_parse"] += 1
            continue
        if any(not g["nm"] for g in groups):
            stats["drop:item_without_name"] += 1
            continue
        if any(len(g["nm"]) > 1 for g in groups):
            stats["drop:item_name_in_several_pieces"] += 1
            continue
        flags = []
        gold, seen, dup_names = [], {}, 0
        bad = None
        for g in groups:
            v = gt["valid_line"][g["nm"][0]]
            idx = [(g["nm"][0], wi) for wi, w in enumerate(v["words"])
                   if not w["is_key"] and _norm(w["text"])]
            if not idx:
                bad = "drop:item_name_only_key_words"
                break
            name = " ".join(_norm(v["words"][wi]["text"]) for _, wi in idx)
            p = [pos[k] for k in idx]
            same_line = len({x[0] for x in p}) == 1
            orders = sorted(x[1] for x in p)
            contiguous = same_line and orders == list(range(orders[0], orders[0] + len(orders)))
            if contiguous:
                s, e = min(x[2] for x in p), max(x[3] for x in p)
                span_txt = text[s:e]
                if span_txt != name:  # word order in text differs from annotation order
                    name = span_txt
                    flags.append("gold_word_order_from_layout")
            else:
                # Name wrapped onto the next printed row (often with qty/price in between):
                # keep the annotators' name, point at each contiguous piece as evidence.
                p = sorted(p)
                runs, cur = [], [p[0]]
                for x in p[1:]:
                    if x[0] == cur[-1][0] and x[1] == cur[-1][1] + 1:
                        cur.append(x)
                    else:
                        runs.append(cur)
                        cur = [x]
                runs.append(cur)
                ev = [{"text": text[r[0][2]:r[-1][3]], "start": r[0][2], "end": r[-1][3]} for r in runs]
                name = " ".join(x["text"] for x in ev)
                s = e = None
                flags.append("gold_name_wrapped_lines")
            key = name.lower()
            if key in seen:
                dup_names += 1
                continue
            seen[key] = True
            if s is None:
                gold.append({"text": name, "start": None, "end": None, "evidence": ev})
            else:
                gold.append({"text": name, "start": s, "end": e, "evidence": None})
        if bad:
            stats[bad] += 1
            continue
        n = len(gold)
        nw = _common.words(text)
        if nw < MIN_WORDS:
            stats[f"drop:under_{MIN_WORDS}_words"] += 1
            stats[f"drop:under_{MIN_WORDS}_words:n={n}"] += 1
            continue
        if nw > MAX_WORDS:
            stats["drop:over_max_words"] += 1
            continue
        if n > MAX_N:
            stats[f"drop:n_over_{MAX_N}"] += 1
            continue
        if stripped:
            flags.append("count_leak_stripped")
        leftover = [ln for ln in text.split("\n") if _COUNT_WORD.search(ln)]
        # count words on lines that carry no menu field are the suspicious ones
        menu_lines = {pos[(ei, wi)][0] for ei, v in enumerate(gt["valid_line"])
                      if v["category"].startswith("menu.") for wi in range(len(v["words"]))
                      if (ei, wi) in pos}
        # off-menu line with a count word AND a bare small integer (a price like 127,000 is not a count)
        sus = [ln for i, ln in enumerate(text.split("\n"))
               if i not in menu_lines and _COUNT_WORD.search(ln) and _SMALL_INT.search(ln)]
        if sus:
            flags.append("possible_count_leak_unlabelled")
        if dup_names:
            flags.append("gold_dedup")
        if any(g["sub"] for g in groups):
            flags.append("has_sub_items")
        if "void_menu" in gt["gt_parse"]:
            flags.append("void_menu_present")
        if any(isinstance(x.get("price"), str) and re.fullmatch(r"[-0.,]*0", x["price"] or "") for x in published):
            flags.append("free_item_present")
        if ws_fixed:
            flags.append("ocr_word_whitespace_normalised")
        flags = sorted(set(flags))
        u = {
            "source_id": f"{sid} (file {fname}, row {row})",
            "group": f"cord-v2:{split}/{image_id}",
            "text": text,
            "n": n,
            "gold_items": gold,
            "list_type": "line_items",
            "item_type": "named_entity",
            "flags": flags,
            "meta": {
                "split": split,
                "image_id": image_id,
                "file": fname,
                "row": row,
                "revision": REVISION,
                "words": nw,
                "lines": text.count("\n") + 1,
                "name_lines_before_dedup": len(groups),
                "count_leak_removed": stripped,
                "count_like_lines_left": leftover,
                "count_like_lines_off_menu": sus,
                "gt_parse": gt["gt_parse"],
            },
        }
        _common.check_unit(u)
        stats["kept"] += 1
        stats[f"kept:n={n}"] += 1
        yield u


# --------------------------------------------------------------------------- main

def main():
    _common.check_source(SOURCE)
    cache = _common.DEFAULT_CACHE
    t0 = time.time()
    fetch(cache)
    t1 = time.time()
    stats = Counter()
    us = list(units(cache, stats))
    t2 = time.time()
    hist = Counter(u["n"] for u in us)
    print(f"fetch {t1 - t0:.1f}s, units {t2 - t1:.1f}s, kept {len(us)}")
    print("n histogram:", dict(sorted(hist.items())))
    for n in sorted(hist):
        ws = [u["meta"]["words"] for u in us if u["n"] == n]
        print(f"  n={n}: units {len(ws)}, median words {statistics.median(ws)}")
    fl = Counter(f for u in us for f in u["flags"])
    print("flags:", dict(fl.most_common()))
    print("split:", dict(Counter(u["meta"]["split"] for u in us)))
    print("stats:", dict(sorted(stats.items())))
    shown = set()
    for want in (1, 2, 3):
        for u in us:
            if u["n"] == want and u["source_id"] not in shown:
                shown.add(u["source_id"])
                ex = {k: v for k, v in u.items() if k != "meta"}
                ex["meta"] = {k: v for k, v in u["meta"].items() if k != "gt_parse"}
                print(json.dumps(ex, ensure_ascii=False, indent=1))
                break


if __name__ == "__main__":
    main()
