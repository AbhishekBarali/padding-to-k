"""ROAST (review-level ABSA) loader: one English review = one unit, gold = explicit aspect targets.

Gold items are the distinct explicit opinion targets (aspect terms) that the ROAST annotators
wrote into the quadruples [target, category, sentiment, opinion_phrase]. Target 'NULL' means the
annotators marked the target as implicit; those quads add no gold item. Nothing here creates gold.
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sources import _common  # noqa: E402

COMMIT = "9b4e1ba0ed2652c97a74bd3675bf35b16a3297d5"
RAW = f"https://raw.githubusercontent.com/RiTUAL-UH/ROAST-ABSA/{COMMIT}"
DOMAINS = ["amazon_ff", "coursera", "hotels", "phones_eng"]
SPLITS = ["train", "dev", "test"]

_SHA = {
    "LICENSE": "c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4",
    "amazon_ff/dev.txt": "cb05a05acaaa86112d6a17730db91567e244ac65a42e2858fdc6027ae0b3c433",
    "amazon_ff/test.txt": "b12eb3b05765ffd941bfe63fb8a94af65d2eaafe276404274db8c8c3418790a1",
    "amazon_ff/train.txt": "21d3c690882d7961ef7d1de1eb6e4a3758c03ef61df7af0df2f3f23efe27226b",
    "coursera/dev.txt": "830e59f021f097f9f4ae3d34442a8100ae16eb8ef1d05ca2c248541f0cccaaf6",
    "coursera/test.txt": "2c85feec81afd2faa2773699a47bbc7698b9663ff7703bab29531795233b9af8",
    "coursera/train.txt": "a0e53dab849c75ae9af70b1027f8d9eae975e2fab4c2e90b896eeb11a228e6cf",
    "hotels/dev.txt": "d16b1ab565acbdec6a0275edbcf80729d4f0f4150fdd7fb74c43328ad8201847",
    "hotels/test.txt": "72b1897c8a52cc96726a1f6e055192d5a527cfa0f5b8294cbbc122aebdc5cc40",
    "hotels/train.txt": "9aae0a6b337bfcf5c5f51eec55ec8f8116019ccc21d0d7561d53cfe1b8d46156",
    "phones_eng/dev.txt": "833989e831fa583d265be65a4ffa809b90e0fa6fea7e8dcf6b617ad8e354ff1b",
    "phones_eng/test.txt": "b9103d8dd026212c03ca28f02372fcf8e4f8629fc2c7db085c7088bdd1c020ef",
    "phones_eng/train.txt": "7aa8b0c0c67148e239b1af1c1a7b40fb48f61284bbb5d079acb3582c78c0e73d",
}

_FILES = [{"url": f"{RAW}/LICENSE", "sha256": _SHA["LICENSE"], "path": "LICENSE"}] + [
    {
        "url": f"{RAW}/ROAST_Data/English/{d}/quads/{s}.txt",
        "sha256": _SHA[f"{d}/{s}.txt"],
        "path": f"English/{d}/quads/{s}.txt",
    }
    for d in DOMAINS
    for s in SPLITS
]

# Where each domain's review text comes from, and why it is not redistributable (see REPORT.md 6).
SUB_SOURCES = {
    "amazon_ff": (
        "Amazon Fine Food Reviews (SNAP, McAuley & Leskovec 2013; Kaggle mirror snap/amazon-fine-food-reviews)",
        "SNAP page states no licence; Kaggle mirror labelled CC0 by an uploader who is not the rights holder; "
        "review text written by Amazon users",
    ),
    "coursera": (
        "Kaggle '100K Coursera's Course Reviews Dataset' (septa97), scraped from coursera.org",
        "Kaggle labels it ODbL + DbCL, but it was scraped and Coursera's terms forbid scraping "
        "without prior written consent; reviewers own the text",
    ),
    "hotels": (
        "TripAdvisor hotel reviews via Yin et al. 2017 (HKUST-KnowComp/DMSC) from Wang et al. 2010 (LARA)",
        "neither the DMSC repo nor the LARA data page states a licence (only a citation request)",
    ),
    "phones_eng": (
        "phone reviews the ROAST authors crawled from 'several Indian review websites' (sites not named)",
        "source sites and their terms are not named in the paper or repo",
    ),
}

SOURCE = {
    "name": "roast",
    "title": "ROAST: Review-level Opinion Aspect Sentiment Target (English domains)",
    "domain": "product_reviews",
    "list_types": ["features"],
    "url": "https://github.com/RiTUAL-UH/ROAST-ABSA",
    "paper": (
        "Chebolu, Dernoncourt, Lipka, Solorio (2024). ROAST: Review-level Opinion Aspect Sentiment "
        "Target Joint Detection for ABSA. arXiv:2405.20274"
    ),
    "licence": "Apache-2.0 (annotations); review text: third-party, terms unclear",
    "licence_url": f"https://github.com/RiTUAL-UH/ROAST-ABSA/blob/{COMMIT}/LICENSE",
    "licence_quote": (
        "Apache License Version 2.0, January 2004 (repo LICENSE). Paper: \"We have only used this "
        "data for research and academic purposes, ensuring that we respect the terms of use for each "
        "platform.\""
    ),
    "redistributable": False,
    "files": _FILES,
    "unit_description": (
        "One whole English customer review (food product, online course, hotel or phone), "
        "15 to 400 words, as tokenised in the ROAST quads files."
    ),
    "how_gold_was_made": (
        "Two Upwork annotators labelled every opinion in each full review as a quadruple (target, "
        "aspect category, sentiment, opinion phrase) in BRAT, following a guideline written for the task; "
        "implicit targets were written as NULL. Disagreements in a 50-review pilot were resolved jointly, "
        "10 of every 50 reviews were cross-checked, and quadruple-level agreement was about 78% F1. "
        "Gold items here are the distinct non-NULL targets, located in the text by exact match."
    ),
    "known_issues": [
        "Only targets of an expressed opinion are annotated; a feature mentioned neutrally (no opinion) is not a gold item.",
        "Text is pre-tokenised by the dataset (spaces around punctuation, \"don ' t\"); it is kept as is.",
        "n = 0 reviews almost always still hold opinions with an implicit target (the product or course as 'it'), so they are weak zeros (flag n0_weak).",
        "Amazon_FF targets are often normalised to the product name rather than the specific feature, so a feature the review praises may be folded into one product target.",
        "Some lines join several paragraphs with no space (\"cleanBreakfast\") and some hotel texts carry mojibake from mis-decoded quotes; both are flagged.",
        "A few amazon_ff lines appear to hold two concatenated reviews with only the first annotated; units whose last annotation ends long before the text does are flagged.",
        "Targets can be pronoun-like or generic words ('it' is not used, but 'product', 'course', 'hotel' are common gold items).",
        "638 review texts appear two or more times in the release (often in different splits) with separately made annotations; copies naming the same targets are kept once (flag duplicate_in_source_same_targets), copies that disagree are all dropped.",
        "Some texts lost the first letter of a sentence ('he hotel', 'his is'); flagged maybe_dropped_initial_chars, text left as is.",
    ],
}

_WORD_CHAR = r"[0-9A-Za-z_]"
_MOJIBAKE = re.compile(r"[\u3000-\u9fff\uff00-\uffef\u00a3\u00e2\u00c3]")
_JOINED = re.compile(r"[a-z]{2}[A-Z][a-z]{2}")
_PRONOUNS = {"it", "this", "that", "they", "them", "these", "those", "he", "she", "him", "her", "one"}
MIN_WORDS, MAX_WORDS, MAX_N = 15, 400, 8


def fetch(cache: Path) -> Path:
    return _common.fetch_all(SOURCE, cache)


def _find(text: str, target: str):
    """First whole-word occurrence of target in text: case-sensitive, then case-insensitive."""
    pat = r"(?<!" + _WORD_CHAR + r")" + re.escape(target) + r"(?!" + _WORD_CHAR + r")"
    m = re.search(pat, text) or re.search(pat, text, re.I)
    return (m.start(), m.end()) if m else None


def _norm_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def _annotated_end(text: str, quads) -> int:
    """Char offset where the last located opinion phrase or target occurrence ends (-1 if none)."""
    end = -1
    low = text.lower()
    for q in quads:
        for piece in (q[3], q[0]):
            if not piece or piece == "NULL":
                continue
            p = _norm_ws(piece).lower()
            k = low.rfind(p)
            if k >= 0:
                end = max(end, k + len(p))
    return end


def _iter_raw(root: Path):
    for d in DOMAINS:
        for s in SPLITS:
            rel = f"English/{d}/quads/{s}.txt"
            with open(root / rel, encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    yield d, s, rel, i, line.rstrip("\n")


DROPS: Counter = Counter()


def _parse(root: Path):
    """Parse every line; return records grouped by exact (whitespace-normalised) text."""
    by_text: dict[str, list] = defaultdict(list)
    for domain, split, rel, lineno, line in _iter_raw(root):
        if not line.strip():
            DROPS["blank_line"] += 1
            continue
        if "####" not in line:
            DROPS["no_separator"] += 1
            continue
        raw_text, ann = line.rsplit("####", 1)
        try:
            quads = ast.literal_eval(ann)
        except (ValueError, SyntaxError):
            DROPS["unparsable_annotation"] += 1
            continue
        if not isinstance(quads, list) or any(not isinstance(q, (list, tuple)) or len(q) != 4 for q in quads):
            DROPS["malformed_quad"] += 1
            continue
        by_text[_norm_ws(raw_text)].append((domain, split, rel, lineno, raw_text, quads))
    return by_text


def _target_set(quads) -> frozenset:
    return frozenset(_norm_ws(q[0]).lower() for q in quads if q[0] != "NULL")


_INITIAL_DROP = re.compile(r"(^|[.!?] )(he|his|hese|hey|hat|here|hose|f course) [a-z]")
_SENT_SPLIT = re.compile(r"(?<=[.!?]) ")


def units(cache: Path):
    root = Path(cache) / SOURCE["name"]
    DROPS.clear()
    for text, copies in _parse(root).items():
        dup_lines = []
        if len(copies) > 1:
            # Same review text annotated more than once (sometimes across splits). Keep one copy only
            # when every copy names the same targets; otherwise n is not settled, so drop them all.
            if len({_target_set(c[5]) for c in copies}) > 1:
                DROPS["duplicate_text_conflicting_targets"] += len(copies)
                continue
            DROPS["duplicate_text_same_targets_extra_copy"] += len(copies) - 1
            dup_lines = [f"{c[2]}:line{c[3]}" for c in copies[1:]]
        domain, split, rel, lineno, raw_text, quads = copies[0]

        flags = ["text_pretokenised", "gold_scope:opinion_targets_only"]
        if text != raw_text:
            flags.append("whitespace_normalised")
        if dup_lines:
            flags.append("duplicate_in_source_same_targets")
        nw = _common.words(text)
        if nw < MIN_WORDS:
            DROPS["too_short_<15_words"] += 1
            continue
        if nw > MAX_WORDS:
            DROPS["too_long_>400_words"] += 1
            continue
        key = text.lower()

        null_quads = [q for q in quads if q[0] == "NULL"]
        targets = []
        for q in quads:
            t = q[0]
            if t != "NULL" and t not in targets:
                targets.append(t)

        gold, by_lower, merged, bad = [], {}, False, None
        for t in targets:
            tn = _norm_ws(t)
            if not tn:
                bad = "empty_target"
                break
            span = _find(text, tn)
            if span is None:
                bad = "target_not_whole_word_in_text"
                break
            s, e = span
            lk = text[s:e].lower()
            if lk in by_lower:
                merged = True
                by_lower[lk]["raw"].append(t)
                continue
            item = {"text": text[s:e], "start": s, "end": e, "evidence": None, "raw": [t]}
            by_lower[lk] = item
            gold.append(item)
        if bad:
            DROPS[bad] += 1
            continue
        n = len(gold)
        if n > MAX_N:
            DROPS["n_above_8"] += 1
            continue
        if merged:
            flags.append("gold_dedup")

        if n == 0:
            if quads:
                flags.append("n0_certified_by:all_quads_null_target")
            else:
                flags.append("n0_certified_by:no_quads_annotated")
            flags.append("n0_weak")
        elif null_quads:
            flags.append("implicit_target_opinions_present")
        if any(g["text"].lower() in _PRONOUNS for g in gold):
            flags.append("pronoun_target")
        spans = sorted((g["start"], g["end"]) for g in gold)
        if any(b[0] < a[1] for a, b in zip(spans, spans[1:])):
            flags.append("nested_gold_items")
        lows = {g["text"].lower() for g in gold}
        if any(x + "s" in lows or x + "es" in lows for x in lows):
            flags.append("near_duplicate_gold:plural_variant")
        if _MOJIBAKE.search(text):
            flags.append("mojibake_present")
        if _JOINED.search(text):
            flags.append("maybe_lost_line_breaks")
        if _INITIAL_DROP.search(text):
            flags.append("maybe_dropped_initial_chars")
        sents = [s.strip().lower() for s in _SENT_SPLIT.split(text) if _common.words(s) >= 6]
        if len(sents) != len(set(sents)):
            flags.append("repeated_sentence")
        ann_end = _annotated_end(text, quads)
        tail_words = _common.words(text[ann_end:]) if ann_end >= 0 else nw
        if quads and tail_words > 40:
            flags.append("maybe_missing_item:unannotated_tail_>40_words")

        sub, why = SUB_SOURCES[domain]
        h = hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]
        u = {
            "source_id": f"roast:ROAST_Data/{rel}:line{lineno}:chars0-{len(text)}",
            "group": f"roast:{domain}:{h}",
            "text": text,
            "n": n,
            "gold_items": [{k: g[k] for k in ("text", "start", "end", "evidence")} for g in gold],
            "list_type": "features",
            "item_type": "exact_quote",
            "flags": flags,
            "meta": {
                "domain": domain,
                "split": split,
                "line": lineno,
                "words": nw,
                "raw_targets": {g["text"]: g["raw"] for g in gold},
                "quads": [list(q) for q in quads],
                "n_quads": len(quads),
                "n_null_target_quads": len(null_quads),
                "duplicate_copies": dup_lines,
                "sub_source": sub,
                "redistributable": False,
                "redistributable_why": why,
            },
        }
        _common.check_unit(u)
        yield u


def main() -> None:
    cache = _common.DEFAULT_CACHE
    fetch(cache)
    us = list(units(cache))
    hist = Counter(u["n"] for u in us)
    print("n histogram:", dict(sorted(hist.items())))
    byd = defaultdict(Counter)
    for u in us:
        byd[u["meta"]["domain"]][u["n"]] += 1
    for d in DOMAINS:
        print(f"  {d}:", dict(sorted(byd[d].items())))
    wl = defaultdict(list)
    for u in us:
        wl[u["n"]].append(u["meta"]["words"])
    print("median words per n:", {k: statistics.median(v) for k, v in sorted(wl.items())})
    fc = Counter(f for u in us for f in u["flags"])
    print("flags:", dict(fc.most_common()))
    print("dropped:", dict(DROPS))
    ex = [next(u for u in us if u["n"] == k) for k in (0, 1, 3)]
    for u in ex:
        v = dict(u)
        v["meta"] = {k: u["meta"][k] for k in ("domain", "split", "line", "words", "raw_targets")}
        print(json.dumps(v, ensure_ascii=False))


if __name__ == "__main__":
    main()
