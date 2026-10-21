"""SkillSpan (Zhang et al., NAACL 2022): windows of job-posting sentences with SKILL / KNOWLEDGE spans.

One unit = 4 to 10 consecutive sentences (rows) of ONE released job posting, 60 to 300 words,
with the annotators' SKILL spans (list_type "skills") or KNOWLEDGE spans (list_type "knowledge")
that fall inside the window. Every released posting was span-annotated end to end, so a window
with no span of a type is a certified n = 0 for that type.

Text is rebuilt from the released tokens (natural detokenised spacing, one row per line).
Gold spans are the annotators' BIO spans, mapped to character offsets in the rebuilt text.
"""
from __future__ import annotations

import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from itertools import groupby
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sources import _common  # noqa: E402

COMMIT = "2ccf3de5b5af7a5409b8dd814fb1315dd6e0ae1b"
RAW = f"https://raw.githubusercontent.com/kris927b/SkillSpan/{COMMIT}/data/json"
SPLITS = ("train", "dev", "test")
SHA = {
    "train": "5e884c3426087d14fc437d328eb72132082edbfe1e776292ae0e6e9b36c1e1f6",
    "dev": "3732937c6869fe191c749b4efe7ffd597ce84eea1192f09b7fe3bd1eb459e2b4",
    "test": "8438eda34939a5877b984ea5daf9e6ff39b2d5c7e3d73cca0499d3de3784d24a",
}

SOURCE = {
    "name": "skillspan",
    "title": "SkillSpan: Hard and Soft Skill Extraction from English Job Postings",
    "domain": "job_posts",
    "list_types": ["skills", "knowledge"],
    "url": "https://github.com/kris927b/SkillSpan",
    "paper": "Zhang, Jensen, Sonniks and Plank (2022). SkillSpan: Hard and Soft Skill Extraction from "
             "English Job Postings. NAACL 2022, ACL Anthology 2022.naacl-main.366, arXiv 2204.12811.",
    "licence": "CC-BY-4.0",
    "licence_url": "https://huggingface.co/datasets/jjzha/skillspan",
    "licence_quote": "HF dataset card (author Mike Zhang) front matter: \"license: cc-by-4.0\". "
                     "GitHub repo LICENSE: \"MIT License, Copyright (c) 2023 Mike Zhang\" "
                     "(https://github.com/kris927b/SkillSpan/blob/main/LICENSE). Paper Sec. 4: \"We release the "
                     "anonymized raw data and annotations of the parts with permissible licenses, i.e., HOUSE ... "
                     "and TECH\"; Appendix A: \"The job posting data in TECH is from Stackoverflow jobs, and is "
                     "licensed under the CC BY-SA license.\"",
    "redistributable": True,
    "files": [
        {"url": f"{RAW}/{s}.json", "sha256": SHA[s], "path": f"data/json/{s}.json"} for s in SPLITS
    ],
    "unit_description": "A window of 4 to 10 consecutive sentences (60 to 300 words) from one English job "
                        "posting (Danish labour agency HOUSE ads or StackOverflow TECH ads), one sentence per line.",
    "how_gold_was_made": "Domain-expert annotators marked every SKILL span (abilities to apply knowledge, "
                         "including soft skills/attitudes and the job's duties) and every KNOWLEDGE span (tools, "
                         "technologies, fields, certificates) in whole postings, following the paper's Appendix B "
                         "guidelines (ESCO definitions). Test postings were annotated by three annotators and "
                         "majority-voted (Fleiss kappa 0.70-0.75); train and dev postings by one annotator.",
    "known_issues": [
        "The 'skills' list is not 'requirements': annotators tag every skill the employee is expected to apply, "
        "so duties ('Provide your patients with a safe and effective course of treatment') count as items "
        "alongside stated requirements and soft skills. Prompts must ask for skills/competences mentioned, "
        "not 'requirements'.",
        "The 'knowledge' list covers tools, technologies, languages, fields and certificates (Python, AWS, "
        "English, gynaecology); guideline rule 13 also tags industries/fields, which are not always obvious "
        "named entities.",
        "By guideline, skills/knowledge in the posting title, in job/position names ('Experienced Java Engineer' "
        "is untagged) and in text that describes only the company are NOT tagged, so a model may list such "
        "mentions and be scored as padding. Windows containing the posting's first row carry "
        "flag title_untagged_by_guideline.",
        "Train and dev postings were single-annotated (flag single_annotator); missed spans there mean a true "
        "item can be absent from gold, including in n = 0 windows.",
        "The released text is de-identified with placeholders (<ORGANIZATION>, <LOCATION>, <NAME>, <CONTACT>, "
        "<ADDRESS>, <SALARY>, ...); some gold knowledge spans are or contain a placeholder (flags "
        "anonymised_placeholders, gold_contains_placeholder, gold_is_placeholder).",
        "The source tokenisation removed most commas ('Be good humoured loyal dedicated and flexible .'), and "
        "the sentence splitter sometimes breaks mid-sentence ('approx .' / '2,800 operations'); the rebuilt "
        "text keeps both as released.",
        "HOUSE text contains cp1252 characters stored as C1 control code points (\\x92 for an apostrophe, "
        "\\x95 for a bullet); the loader re-decodes them to the intended characters (flag "
        "cp1252_mojibake_repaired). Windows containing \\x1a (a lost character) are dropped.",
        "Some boilerplate sentences recur across postings of the same employer with different tags; windows "
        "with such a sentence carry flag boilerplate_tag_inconsistent.",
    ],
}

# Detokenisation: no space before these tokens, no space after the opening ones.
NO_SPACE_BEFORE = {".", ",", ";", ":", "!", "?", ")", "]", "}", "%", "\u2026", "\u201d"}
NO_SPACE_AFTER = {"(", "[", "{", "\u201c"}
C1 = re.compile(r"[\x80-\x9f]")
BAD_CTRL = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")
PLACEHOLDER = re.compile(r"<[A-Z_]+(?::[A-Z_]+)?>")
TRIM_CHARS = ".,;:!?*\u2022\u00b7-\u2013\u2014 "

MIN_ROWS, MAX_ROWS = 4, 10
MIN_WORDS, MAX_WORDS = 60, 300
MAX_N = 8
PER_GROUP_N = 3          # non-overlapping candidate windows kept per (posting, list_type, n)
MIN_DENSITY = 1.0        # spans per 100 tokens; below this a posting is treated as possibly partly annotated

LIST_TAGS = {"skills": ("tags_skill", "exact_quote"), "knowledge": ("tags_knowledge", "named_entity")}


def fetch(cache: Path) -> Path:
    return _common.fetch_all(SOURCE, cache)


def _repair(tok: str) -> tuple[str, bool]:
    """Re-decode cp1252 characters that were stored as C1 control code points."""
    if not C1.search(tok):
        return tok, False
    out = []
    for ch in tok:
        if "\x80" <= ch <= "\x9f":
            try:
                out.append(bytes([ord(ch)]).decode("cp1252"))
            except UnicodeDecodeError:
                out.append(ch)
        else:
            out.append(ch)
    return "".join(out), True


def _bio(tags: list[str]) -> list[tuple[int, int]]:
    """Token spans [i, j) from bare B/I/O tags; an I after O starts a new span."""
    spans, i = [], 0
    while i < len(tags):
        if tags[i] in ("B", "I"):
            j = i + 1
            while j < len(tags) and tags[j] == "I":
                j += 1
            spans.append((i, j))
            i = j
        else:
            i += 1
    return spans


DOT_PREFIX = re.compile(r"^(net|pdf)(\b|[-/])", re.I)  # ". NET", ". pdf" are one word split by the tokenizer


def _row_text(tokens: list[str]) -> tuple[str, list[tuple[int, int]]]:
    """Join tokens with natural spacing; return text and per-token char offsets."""
    parts, offs, pos, prev, glue_next = [], [], 0, None, False
    for i, t in enumerate(tokens):
        nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
        dot_word = t == "." and bool(DOT_PREFIX.match(nxt))
        if prev is None or glue_next or prev in NO_SPACE_AFTER:
            sep = ""
        elif dot_word:
            sep = " "
        else:
            sep = "" if t in NO_SPACE_BEFORE else " "
        glue_next = dot_word
        parts.append(sep)
        pos += len(sep)
        offs.append((pos, pos + len(t)))
        parts.append(t)
        pos += len(t)
        prev = t
    return "".join(parts), offs


def _trim(text: str, s: int, e: int) -> tuple[int, int]:
    """Strip boundary punctuation/bullets and unbalanced brackets/quotes from a gold span."""
    changed = True
    while changed and s < e:
        changed = False
        while s < e and text[s] in TRIM_CHARS:
            if text[s] == "." and s + 1 < e and text[s + 1].isalnum():
                break  # ".NET", ".pdf"
            s += 1
            changed = True
        while s < e and text[e - 1] in TRIM_CHARS:
            e -= 1
            changed = True
        for o, c in (("(", ")"), ("[", "]"), ("\u201c", "\u201d"), ("\u2018", "\u2019"), ('"', '"')):
            seg = text[s:e]
            if seg and seg[-1] == c and _unbalanced(seg, o, c, closing=True):
                e -= 1
                changed = True
                seg = text[s:e]
            if seg and seg[0] == o and _unbalanced(seg, o, c, closing=False):
                s += 1
                changed = True
    return s, e


def _unbalanced(seg: str, o: str, c: str, closing: bool) -> bool:
    if o == c:
        return seg.count(o) % 2 == 1
    return seg.count(c) > seg.count(o) if closing else seg.count(o) > seg.count(c)


def _postings(root: Path):
    for split in SPLITS:
        path = root / "data" / "json" / f"{split}.json"
        rows = []
        with open(path, encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                r = json.loads(line)
                r["_line"] = line_no
                rows.append(r)
        for (src, idx), grp in groupby(rows, key=lambda r: (r["source"], r["idx"])):
            yield split, src, idx, list(grp)


def _prepare(rows):
    """Per row: rebuilt text, token offsets, spans per list type, repair flag, bad-control flag."""
    out = []
    for r in rows:
        toks, rep = [], False
        for t in r["tokens"]:
            t2, ch = _repair(t)
            toks.append(t2)
            rep |= ch
        text, offs = _row_text(toks)
        spans = {}
        for lt, (key, _) in LIST_TAGS.items():
            spans[lt] = [(offs[i][0], offs[j - 1][1]) for i, j in _bio(r[key])]
        out.append({"text": text, "spans": spans, "repaired": rep, "bad": bool(BAD_CTRL.search(text)),
                    "line": r["_line"], "ntok": len(r["tokens"]), "raw": r})
    return out


def _header_like(t: str) -> bool:
    t = t.strip()
    return t.endswith(":") or (len(t.split()) <= 5 and not t.endswith((".", "!", "?", ";")))


def units(cache: Path, stats: dict | None = None):
    root = Path(cache) / SOURCE["name"]
    stats = stats if stats is not None else {}
    drops = stats.setdefault("dropped", Counter())
    posts = list(_postings(root))

    # Boilerplate sentences shared by >1 posting whose tags differ between copies.
    copies = defaultdict(set)
    for split, src, idx, rows in posts:
        for r in rows:
            if len(r["tokens"]) >= 6:
                copies[tuple(r["tokens"])].add((tuple(r["tags_skill"]), tuple(r["tags_knowledge"]), split, src, idx))
    inconsistent = {k for k, v in copies.items()
                    if len({(a, b) for a, b, *_ in v}) > 1 and len({tuple(x[2:]) for x in v}) > 1}

    for split, src, idx, rows in posts:
        group = f"skillspan:{split}:{src}:{idx}"
        ntok = sum(len(r["tokens"]) for r in rows)
        nspan = sum(len(_bio(r["tags_skill"])) + len(_bio(r["tags_knowledge"])) for r in rows)
        if 100 * nspan / ntok < MIN_DENSITY:
            drops["posting_low_annotation_density"] += 1
            continue
        prep = _prepare(rows)
        cands = defaultdict(list)  # (list_type, n) -> [(score, a, b, unit)]
        for a in range(len(prep)):
            for b in range(a + MIN_ROWS, min(a + MAX_ROWS, len(prep)) + 1):
                win = prep[a:b]
                text_rows = [w["text"] for w in win]
                text = "\n".join(text_rows)
                nw = _common.words(text)
                if nw > MAX_WORDS:
                    break
                if nw < MIN_WORDS:
                    continue
                if any(w["bad"] for w in win):
                    drops["window_has_control_char"] += 1
                    continue
                for lt, (_, item_type) in LIST_TAGS.items():
                    u = _build(text, text_rows, win, lt, item_type, split, src, idx, a, b, group, nw,
                               rows, inconsistent, drops)
                    if u is None:
                        continue
                    if u["n"] > MAX_N:
                        continue
                    score = (0 if a == 0 or _header_like(prep[a - 1]["text"]) or _header_like(prep[a]["text"]) else 1) \
                        + (1 if _header_like(prep[b - 1]["text"]) else 0) + abs(nw - 140) / 100
                    cands[(lt, u["n"])].append((score, a, b, u))
        for key in sorted(cands):
            taken = []
            for score, a, b, u in sorted(cands[key], key=lambda x: (x[0], x[1], x[2])):
                if len(taken) >= PER_GROUP_N:
                    break
                if any(not (b <= ta or a >= tb) for ta, tb in taken):
                    continue
                taken.append((a, b))
                _common.check_unit(u)
                yield u


def _build(text, text_rows, win, lt, item_type, split, src, idx, a, b, group, nw, rows, inconsistent, drops):
    flags = ["detokenised_from_tokens", "rows_joined_with_newline"]
    gold, seen, trimmed, dedup, punct_only = [], set(), False, False, False
    base = 0
    for w, rt in zip(win, text_rows):
        for s, e in w["spans"][lt]:
            s2, e2 = _trim(rt, s, e)
            if (s2, e2) != (s, e):
                trimmed = True
            if s2 >= e2:
                drops[f"gold_span_punct_only_removed:{lt}"] += 1
                punct_only = True
                continue
            item = rt[s2:e2]
            k = item.strip().lower()
            if k in seen:
                dedup = True
                continue
            seen.add(k)
            gold.append({"text": item, "start": base + s2, "end": base + e2, "evidence": None})
        base += len(rt) + 1
    n = len(gold)
    if n == 0:
        flags.append(f"n0_certified_by:posting_fully_span_annotated_no_{lt}_span_in_window")
    if trimmed:
        flags.append("span_punct_trimmed")
    if dedup:
        flags.append("gold_dedup")
    if punct_only:
        flags.append("annotated_punct_only_span_removed")
    if any(w["repaired"] for w in win):
        flags.append("cp1252_mojibake_repaired")
    ph = sorted(set(PLACEHOLDER.findall(text)))
    if ph:
        flags.append("anonymised_placeholders:" + ",".join(p.strip("<>") for p in ph))
    if any(PLACEHOLDER.search(g["text"]) for g in gold):
        flags.append("gold_contains_placeholder")
    if any(not PLACEHOLDER.sub("", g["text"]).strip() for g in gold):
        flags.append("gold_is_placeholder")
    if a == 0:
        flags.append("title_untagged_by_guideline")
    if split != "test":
        flags.append("single_annotator")
    if any(tuple(r["tokens"]) in inconsistent for r in rows[a:b]):
        flags.append("boilerplate_tag_inconsistent")
    other = "knowledge" if lt == "skills" else "skills"
    n_other = sum(len(w["spans"][other]) for w in win)
    if n == 0:
        # A window with spans of the other type shows the annotator was tagging this stretch; a window
        # with no spans at all is usually company/benefit text (correct by guideline 12.3) but could
        # also be a stretch the annotator skipped.
        flags.append(f"n0_other_type_spans_in_window:{n_other}" if n_other else "n0_no_spans_of_either_type")
    return {
        "source_id": f"skillspan/data/json/{split}.json#{src}-{idx}/rows{a}-{b - 1}/lines{win[0]['line']}-{win[-1]['line']}",
        "group": group,
        "text": text,
        "n": n,
        "gold_items": gold,
        "list_type": lt,
        "item_type": item_type,
        "flags": flags,
        "meta": {
            "split": split, "source": src, "posting_idx": idx, "row_start": a, "row_end": b - 1,
            "rows": b - a, "posting_rows": len(rows), "words": nw,
            "annotation": "three annotators, majority vote" if split == "test" else "single annotator",
            f"n_{other}_spans_in_window": n_other,
        },
    }


def _main():
    cache = _common.DEFAULT_CACHE
    _common.check_source(SOURCE)
    fetch(cache)
    stats = {}
    us = list(units(cache, stats))
    for lt in SOURCE["list_types"]:
        sel = [u for u in us if u["list_type"] == lt]
        hist = Counter(u["n"] for u in sel)
        print(f"== list_type={lt} units={len(sel)} groups={len({u['group'] for u in sel})}")
        print("n histogram:", {k: hist[k] for k in sorted(hist)})
        print("groups per n:", {k: len({u['group'] for u in sel if u['n'] == k}) for k in sorted(hist)})
        print("median words per n:", {k: statistics.median(u["meta"]["words"] for u in sel if u["n"] == k)
                                      for k in sorted(hist)})
    fl = Counter(f.split(":")[0] if f.startswith(("anonymised", "n0_other_type")) else f
                 for u in us for f in u["flags"])
    print("flags:", dict(sorted(fl.items())))
    print("dropped:", dict(stats.get("dropped", {})))
    picks = [next(u for u in us if u["n"] == 0 and u["list_type"] == "skills"),
             next(u for u in us if u["n"] == 2 and u["list_type"] == "knowledge"),
             next(u for u in us if u["n"] == 4 and u["list_type"] == "skills")]
    for u in picks:
        print(json.dumps(u, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    _main()
