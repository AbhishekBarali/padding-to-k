"""PDNC (Project Dialogism Novel Corpus) loader: direct-speech quotations in novel windows.

One unit = 1 to 3 consecutive paragraphs (40 to 300 words) from one chapter of one novel.
Gold = every PDNC-annotated quotation fully inside the window, copied verbatim from the novel
text at PDNC's own character offsets. Quote marks are NOT part of the gold text (PDNC's spans
exclude them, and we keep that convention everywhere).

Only windows in which every double-quote character is accounted for by a PDNC annotation are
yielded, so an n = 0 window contains no quote marks at all and every quoted span in an n > 0
window is gold.
"""
from __future__ import annotations

import csv
import ast
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

try:
    from . import _common
except ImportError:  # pragma: no cover
    import _common  # type: ignore

COMMIT = "e507a27b89a85c1e9710a897ad0b3f5a9ad73dc4"
RAW = f"https://raw.githubusercontent.com/Priya22/project-dialogism-novel-corpus/{COMMIT}/"

_SHA = {
    "data/AHandfulOfDust/novel_text.txt": "d93d1d7034fb98e38c1400c33caac7a7ff5c2111029de935fac8f5f7dbd960fc",
    "data/AHandfulOfDust/quotation_info.csv": "138c7f64cea186c5d73c473aa0f7a017b57736a94a89ec08be215ea8d809ab12",
    "data/APassageToIndia/novel_text.txt": "bc9c50093a6822f7c488224ce46c602981759e3b421b1de0cd698bcc8d54d2b2",
    "data/APassageToIndia/quotation_info.csv": "d96c944be6a6f08293f76480bded9f2449eb1537ba422422c6c43103dc1ce3cb",
    "data/ARoomWithAView/novel_text.txt": "a7f6e16555eda0e34c03659b797c573d637de90c7bbcd70f8592e74948ef419d",
    "data/ARoomWithAView/quotation_info.csv": "4fa67257c5afbe79c0c71691026fb163b43fc4ac67c133d1f25ffbcfa9ac0267",
    "data/AlicesAdventuresInWonderland/novel_text.txt": "3c07acdad93b3fffab80c1cd05f5a64787837a3a046dcffb82d9f23d25b72cf4",
    "data/AlicesAdventuresInWonderland/quotation_info.csv": "97c23c58701b4c71e62967c710d423a1abcd30afd6fe8b1e0a4bc693dae76cac",
    "data/AnneOfGreenGables/novel_text.txt": "caa7444ca060bba9566f3d9ed7ef8340cd5543b03f96c93c24f3691b0e8aeccd",
    "data/AnneOfGreenGables/quotation_info.csv": "0a81f83d10804d8e4a3a34d46d32cde863795d8a4d2cddb676ac16f16354060c",
    "data/DaisyMiller/novel_text.txt": "3475c47037aa1aa6b35e763b1049a2362ee7cbd286324b9f2a55baa0bece5dde",
    "data/DaisyMiller/quotation_info.csv": "a7336df3a00736f891ce0012001045ac130904fd7a560cd31240206b52720e0b",
    "data/Emma/novel_text.txt": "244f3afe05a7490c0fe0daddad0b93ab42f5639ac2fc24814b321c91dd143d1c",
    "data/Emma/quotation_info.csv": "2e6672f9e575b5ad83d335f9ef1f3f5ad1c755dfe1c95b4bdb733c57b3247455",
    "data/HardTimes/novel_text.txt": "86ec45c3bc09d6a08662f5f20d192a1b04de010ea8dc70e5366d3b60ea35e7e6",
    "data/HardTimes/quotation_info.csv": "a4eab13d70b2bfa704823f98aeed3ae188385fd5131e660ceab83185ca0274b7",
    "data/HowardsEnd/novel_text.txt": "fd5c4e2ac5bc8b0c62577c610b9d2f1768bce94245cad9174b4457b6609ddcd3",
    "data/HowardsEnd/quotation_info.csv": "4dcf0da1e22528bd35c4e4eab3d247fa4fbc3711ceda853338502cb61ad2e0b0",
    "data/MansfieldPark/novel_text.txt": "b6c3c9f73be5e54682dc8b77f31844e48f3972b8e1f80dd86bd2b62c5ff80d87",
    "data/MansfieldPark/quotation_info.csv": "3a7a3078031d14ab9cba8361ce873830bbce0ef296b581569287933dcd26feb5",
    "data/NightAndDay/novel_text.txt": "39028e9931692c4affebe2f4e43db1b4438c67ac1d452af0d2d55d1b93fe077d",
    "data/NightAndDay/quotation_info.csv": "390b41d807b9cc7c8023c791a63a0b44c5ec4c4de2127d410c85cf89b75edb80",
    "data/NorthangerAbbey/novel_text.txt": "b204181174e72d207e7a7d48db85faf1758a6e73b9abbf9f8f94ef29e28e13ee",
    "data/NorthangerAbbey/quotation_info.csv": "2939bb20a22e9e668a66bb77be3e9c06fb8c522a42798037d2e8febf07277ab4",
    "data/OliverTwist/novel_text.txt": "7042780c3068035978098513fe2d2fe467740af6b82a85fe1e6b36757dd84213",
    "data/OliverTwist/quotation_info.csv": "5d4bfbb67bfd90a7303e626786bea3d87c76e931e35917b837afc7d94ce52aba",
    "data/Persuasion/novel_text.txt": "b42c4b4735cadffec44ef7462405b1551388fd1be6c35487c23745763584cd26",
    "data/Persuasion/quotation_info.csv": "818959323968d05be920a1488c14bb133143655a801954abb49d192a8c70a53d",
    "data/PrideAndPrejudice/novel_text.txt": "03ef2a45e7d958ea400cd63e77499ba65e0aa4a06e35c434ca348a0e46789660",
    "data/PrideAndPrejudice/quotation_info.csv": "4eb8d235fc06dfb39c11eb5525fa21943d1a9f0e1d01af61f9329fa10512792b",
    "data/SenseAndSensibility/novel_text.txt": "504919bfd78b59cc995904769eb51e645be05c805718e445d0ec969366e0d5c5",
    "data/SenseAndSensibility/quotation_info.csv": "b9c9c6ae60f72c73e9c43acbda76adffc9a34c4de33a0e9ffcf8b394f9ebea4e",
    "data/TheAgeOfInnocence/novel_text.txt": "12be42dbe622193a4519cb0fd08fcda3b593ba3bf000c68849453977994cec60",
    "data/TheAgeOfInnocence/quotation_info.csv": "0fe87b0bbfeb9b2837a43245436d82be74758c86ac250cf3637ecc4e92f8b2e3",
    "data/TheAwakening/novel_text.txt": "70e6caa8b14d81c3675f774158abfe674e091b73dafc784ef33c13f08a3de603",
    "data/TheAwakening/quotation_info.csv": "d5b95f316a562b170be3de5b6ef13e8e216ba0bdbd307d5d0ba9ff721fae3f0c",
    "data/TheGambler/novel_text.txt": "e11d342dc4a88db12401910a8eed3c1e65eea2252cf7a8ddaca73b201abfbd92",
    "data/TheGambler/quotation_info.csv": "debeeebb3c553dfbfc73f28ce1b090bbb81f09fe8f3e64fc8e49d0e6a166d9ee",
    "data/TheInvisibleMan/novel_text.txt": "31581b513dfd3a1eea64cf5a8f509c7184038f21787397525ec989f7257f7d31",
    "data/TheInvisibleMan/quotation_info.csv": "8976e6c96a016e0bd3a846f1ace0a1ecb1b17280ead7023a09495e0a7ba4c0e5",
    "data/TheManWhoWasThursday/novel_text.txt": "9b3b46730e44838a4323e31d74e8eecea5d30414b33b747e39eb517caaf10a71",
    "data/TheManWhoWasThursday/quotation_info.csv": "b4505b6bdadda6c371b304532557b234099db44b079190e27c4fb4cc8f543611",
    "data/TheMysteriousAffairAtStyles/novel_text.txt": "e6b3744c27e5796d706ca7a3507258330a35d21e74e185fdbfe6dc48ea7acc72",
    "data/TheMysteriousAffairAtStyles/quotation_info.csv": "adce1455ddbb7baa2bf1f7a798a4e893aad6d5012a8407c4026305e6425f0abb",
    "data/ThePictureOfDorianGray/novel_text.txt": "1293f3b0b9b0088233049391be644421e8226cae54db1dec6c6c22760afe3e9d",
    "data/ThePictureOfDorianGray/quotation_info.csv": "db6d480b169114efe10ef1d3b7a87489a1221dce298d8d5da35ede6b375d0676",
    "data/TheSignOfTheFour/novel_text.txt": "f64ea9c167a8bda40b1d2c79516759b3c15c50d5f1808fe4a1a2bacd8188ea5f",
    "data/TheSignOfTheFour/quotation_info.csv": "673d2b10888ffb0bce565f3ba6ac37165d86395c7a2fd8bd51f4492c7bf01ed2",
    "data/TheSportOfTheGods/novel_text.txt": "12ab9c8e2c15500ca3d52b163d1f386b6da87c29467259930f6ab24a6b546073",
    "data/TheSportOfTheGods/quotation_info.csv": "8390ec2bfc453fd0c9895cff6e54c4db85924c711175f42b70d9ceb1bb918654",
    "data/TheSunAlsoRises/novel_text.txt": "4fd2e7b51fc866b9f5abfa11be3137c4954a005aeddc1858b8e7778426316923",
    "data/TheSunAlsoRises/quotation_info.csv": "4fad59f179406ff9b5685a2fb6a3bcbc91df21d0239377f01483feed33ea12e6",
    "data/WhereAngelsFearToTread/novel_text.txt": "4b85d0e79688594c7e3aa5da11424f4717d1b9cf35a6a243b2a2dcc92d719538",
    "data/WhereAngelsFearToTread/quotation_info.csv": "2ccfaa8240d67b686ddb24261631f58684d4d69f967cd15202af928068cf29b0",
    "data/WinnieThePooh/novel_text.txt": "bb942f9c4cb5727cd9ef01bffd4eea2b22185953ac90351209096f65e7a2f210",
    "data/WinnieThePooh/quotation_info.csv": "ce8a6318369b93b7d199695ccebbf61376abd711b64b90e2f6054570d23d8876",
    "ReadMe.md": "68d33b693ead891840b3814af2ffaac1def492d9bbf54ffa1e5bfe97668ef8bd",
    "PDNC-Novel-Index.csv": "1a0f38e68dc57ada0c1d4e7fe6049e2286ddc01b67ff4d68b7c9a6c637588f40",
}

# Novels whose text may NOT be public domain in the US: excluded from units().
EXCLUDED_NOVELS = {
    "AHandfulOfDust": "us_copyright: first published 1934 (US term runs to end of 2029); PDNC took the text from gutenberg.ca, which relies on Canadian law",
}

# Public domain in the US (published 1930 or earlier), but the author died less than 70 years
# before 2026, so the text may still be in copyright in life+70 countries (UK, EU).
NON_US_COPYRIGHT_UNTIL = {
    "APassageToIndia": 2041,          # E. M. Forster d. 1970
    "ARoomWithAView": 2041,
    "HowardsEnd": 2041,
    "WhereAngelsFearToTread": 2041,
    "TheMysteriousAffairAtStyles": 2047,  # Agatha Christie d. 1976
    "TheSunAlsoRises": 2032,          # Ernest Hemingway d. 1961
    "WinnieThePooh": 2027,            # A. A. Milne d. 1956 (PD from 1 Jan 2027)
}

NOVELS = sorted({p.split("/")[1] for p in _SHA if p.startswith("data/")})

SOURCE = {
    "name": "pdnc",
    "title": "Project Dialogism Novel Corpus (PDNC)",
    "domain": "fiction",
    "list_types": ["quotations"],
    "url": "https://github.com/Priya22/project-dialogism-novel-corpus",
    "paper": "Vishnubhotla, Hammond and Hirst (2022). The Project Dialogism Novel Corpus: A Dataset for "
             "Quotation Attribution in Literary Texts. LREC 2022, pages 5838-5848. "
             "https://aclanthology.org/2022.lrec-1.628/",
    "licence": "CC-BY-4.0",
    "licence_url": "https://creativecommons.org/licenses/by/4.0/",
    "licence_quote": "PDNC is free to use under the CC-BY 4.0 License.",
    "redistributable": True,
    "files": [{"url": RAW + p, "sha256": s, "path": p} for p, s in _SHA.items()],
    "unit_description": "One to three consecutive paragraphs (40 to 300 words) from one chapter of a "
                        "public-domain English novel.",
    "how_gold_was_made": "University-level literature students annotated every quotation in each full "
                         "novel; each novel was annotated by two annotators who then resolved all "
                         "disagreements in up to three consensus rounds (paper section 4.2). Quotations "
                         "were pre-identified with GutenTag and checked by the annotators. Gold items here "
                         "are those quotation spans copied verbatim at PDNC's own character offsets.",
    "known_issues": [
        "An interrupted quotation (\"A,\" said X, \"B.\") is ONE PDNC quotation with two sub-spans; it is "
        "one gold item whose text is the sub-spans joined by a space, with each sub-span as an evidence span "
        "(flag interrupted_quote). meta.n_subquote_spans gives the count if fragments are scored separately.",
        "Speech reported without quote marks (free indirect speech) is not annotated as a quotation and is not "
        "detected; a model may list it.",
        "PDNC's novel_text.txt files contain no characters above ASCII: em dashes, curly apostrophes and ligatures "
        "were dropped or turned into spaces by PDNC, so some words read oddly ('I m going', 'antenn ', 'Hastings it's'). "
        "Units copy this text verbatim because PDNC's offsets index it.",
        "n = 0 windows that contain a speech verb (said, asked ...) are flagged speech_verb_no_quote_marks; in the "
        "ones read these were indirect speech, which is correctly not a quotation.",
        "n = 0 windows are longer (median 113 words) than n = 1-3 windows (82-84 words): narration paragraphs are long.",
        "Quote marks are excluded from gold text, matching PDNC's spans.",
        "Windows containing any double-quote character not covered by a PDNC annotation are dropped, so scare "
        "quotes, quoted titles, letters and missed quotations never appear; this removes a slice of real text.",
        "Some texts keep Project Gutenberg underscore italics (_word_); kept verbatim (flag gutenberg_underscore_italics).",
        "Identical quotations in one window (for example two characters saying \"No.\") are merged (flag gold_dedup), "
        "so n counts distinct quote strings.",
        "A Handful of Dust (1934) is excluded because its text is not public domain in the US.",
        "Seven novels are US public domain but may still be in copyright in life+70 countries "
        "(flag text_copyright_outside_us_until:<year>).",
    ],
}

QUOTE = '"'
HEAD_RE = re.compile(
    r"^\s*((CHAPTER|Chapter|BOOK|Book|PART|Part|VOLUME|Volume)\b.*|[IVXLC]+\.?|\d+\.?)\s*$"
)
PARA_SEP = re.compile(r"\n[ \t]*\n")
WS = re.compile(r"\s+")
MIN_W, MAX_W = 40, 300
SPEECH_VERB = re.compile(r"\b(said|says|cried|replied|exclaimed|asked|answered)\b")


def fetch(cache: Path) -> Path:
    return _common.fetch_all(SOURCE, cache)


def _paragraphs(t: str):
    """(start, end) of each non-blank paragraph, trimmed of outer whitespace."""
    out, pos = [], 0
    for m in list(PARA_SEP.finditer(t)) + [None]:
        end = m.start() if m else len(t)
        s, e = pos, end
        while s < e and t[s].isspace():
            s += 1
        while e > s and t[e - 1].isspace():
            e -= 1
        if e > s:
            out.append((s, e))
        if m:
            pos = m.end()
    return out


def _is_heading(p: str) -> bool:
    first = p.strip().split("\n")[0]
    if QUOTE in p or len(p.split()) > 40:
        return False
    if HEAD_RE.match(first):
        return True
    # short all-caps line block (chapter titles printed on their own)
    letters = [c for c in p if c.isalpha()]
    return bool(len(p.split()) <= 12 and letters and not any(c.islower() for c in letters))


def _clean_span(t: str, s: int, e: int):
    while s < e and (t[s].isspace() or t[s] == QUOTE):
        s += 1
    while e > s and (t[e - 1].isspace() or t[e - 1] == QUOTE):
        e -= 1
    return (s, e) if e > s else None


def _normalise(t: str, paras):
    """Join paragraphs with a blank line, collapse whitespace inside a paragraph.
    Returns (text, map) where map[orig_index] = new index for every non-space original char."""
    pieces, mapping, n = [], {}, 0
    for k, (s, e) in enumerate(paras):
        if k:
            pieces.append("\n\n")
            n += 2
        prev_space = False
        for i in range(s, e):
            c = t[i]
            if c.isspace():
                if not prev_space:
                    pieces.append(" ")
                    n += 1
                prev_space = True
            else:
                mapping[i] = n
                pieces.append(c)
                n += 1
                prev_space = False
    return "".join(pieces), mapping


def _load_quotes(path: Path, t: str):
    quotes = []
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            spans = []
            for s, e in ast.literal_eval(row["quoteByteSpans"]):
                c = _clean_span(t, int(s), int(e))
                if c:
                    spans.append(c)
            if not spans:
                continue
            spans.sort()
            quotes.append({
                "id": row["quoteID"], "spans": spans, "lo": spans[0][0], "hi": spans[-1][1],
                "speaker": row.get("speaker"), "type": row.get("quoteType"),
            })
    quotes.sort(key=lambda q: q["lo"])
    return quotes


STATS = Counter()


def _novel_units(root: Path, folder: str, index_row: dict):
    t = (root / "data" / folder / "novel_text.txt").read_text(encoding="utf-8")
    quotes = _load_quotes(root / "data" / folder / "quotation_info.csv", t)
    covered = bytearray(len(t) + 1)
    for q in quotes:
        for s, e in q["spans"]:
            for i in range(max(0, s - 3), min(len(t), e + 3)):
                covered[i] = 1
    first, last = quotes[0]["lo"], quotes[-1]["hi"]
    paras = _paragraphs(t)
    # chapter index and per-paragraph status
    chap, info = 0, []
    for (s, e) in paras:
        p = t[s:e]
        head = _is_heading(p)
        if head:
            chap += 1
        in_stretch = e > first and s < last + 1
        unannot = any(t[i] == QUOTE and not covered[i] for i in range(s, e))
        info.append({"s": s, "e": e, "chap": chap, "head": head, "in": in_stretch, "unannot": unannot})
    # quotations touching each paragraph
    starts = [q["lo"] for q in quotes]
    import bisect

    copyright_until = NON_US_COPYRIGHT_UNTIL.get(folder)
    for i in range(len(paras)):
        for L in (1, 2, 3):
            j = i + L - 1
            if j >= len(paras):
                break
            win = info[i:j + 1]
            if any(w["head"] for w in win):
                STATS["drop_heading_in_window"] += 1
                break
            if not all(w["in"] for w in win):
                STATS["drop_outside_annotated_stretch"] += 1
                break
            if len({w["chap"] for w in win}) > 1:
                break
            if any(w["unannot"] for w in win):
                STATS["drop_unannotated_quote_mark"] += 1
                break  # longer windows from i also contain this paragraph
            ws, we = win[0]["s"], win[-1]["e"]
            # quotations overlapping the window
            k = bisect.bisect_left(starts, ws - 20000)
            inside, partial = [], False
            while k < len(quotes) and quotes[k]["lo"] < we:
                q = quotes[k]
                if q["hi"] > ws:
                    if q["lo"] >= ws and q["hi"] <= we:
                        inside.append(q)
                    else:
                        partial = True
                k += 1
            if partial:
                STATS["drop_partial_quote"] += 1
                continue
            text, mp = _normalise(t, [(w["s"], w["e"]) for w in win])
            nw = _common.words(text)
            if nw < MIN_W or nw > MAX_W:
                STATS["drop_length"] += 1
                continue
            flags = ["whitespace_normalised:hard_wraps_unwrapped"]
            gold, seen, dedup, interrupted, nsub = [], set(), 0, 0, 0
            qmeta = []
            multi_para = 0
            for q in inside:
                subs = []
                for s, e in q["spans"]:
                    a, b = mp[s], mp[e - 1] + 1
                    subs.append({"text": text[a:b], "start": a, "end": b})
                nsub += len(subs)
                if any("\n\n" in x["text"] for x in subs):
                    multi_para += 1
                if len(subs) == 1:
                    item = {"text": subs[0]["text"], "start": subs[0]["start"], "end": subs[0]["end"],
                            "evidence": None}
                else:
                    interrupted += 1
                    item = {"text": " ".join(x["text"] for x in subs), "start": None, "end": None,
                            "evidence": subs}
                key = item["text"].strip().lower()
                if key in seen:
                    dedup += 1
                    continue
                seen.add(key)
                gold.append(item)
                qmeta.append({"quote_id": q["id"], "speaker": q["speaker"], "quote_type": q["type"],
                              "n_subspans": len(subs)})
            n = len(gold)
            if n > 8:
                STATS["drop_n_over_8"] += 1
                continue
            if n == 0:
                flags.append("n0_certified_by:pdnc_full_novel_annotation_and_no_quote_marks_in_window")
                if SPEECH_VERB.search(text):
                    flags.append("speech_verb_no_quote_marks")
            else:
                flags.append("all_quote_marks_in_window_are_annotated")
            if interrupted:
                flags.append(f"interrupted_quote:{interrupted}")
            if multi_para:
                flags.append(f"quote_spans_paragraphs:{multi_para}")
            if dedup:
                flags.append("gold_dedup")
            if "_" in text:
                flags.append("gutenberg_underscore_italics")
            if copyright_until:
                flags.append(f"text_copyright_outside_us_until:{copyright_until}")
            yield {
                "source_id": f"pdnc:{folder}:chars{ws}-{we}:paras{i}-{j}",
                "group": f"pdnc:{folder}:ch{win[0]['chap']:03d}",
                "text": text,
                "n": n,
                "gold_items": gold,
                "list_type": "quotations",
                "item_type": "exact_quote",
                "flags": flags,
                "meta": {
                    "novel": folder,
                    "novel_title": index_row.get("Novel Title"),
                    "year_first_published": index_row.get("Year of First Publication"),
                    "text_source": index_row.get("Source"),
                    "commit": COMMIT,
                    "orig_char_range": [ws, we],
                    "n_paragraphs": L,
                    "words": nw,
                    "n_subquote_spans": nsub,
                    "quotes": qmeta,
                    "gold_excludes_quote_marks": True,
                },
            }


def units(cache: Path):
    root = Path(cache) / SOURCE["name"]
    with open(root / "PDNC-Novel-Index.csv", encoding="utf-8", newline="") as f:
        index = {r["Folder Name"]: r for r in csv.DictReader(f) if r.get("Folder Name")}
    for folder in NOVELS:
        if folder in EXCLUDED_NOVELS:
            STATS[f"novel_excluded:{folder}"] += 1
            continue
        for u in _novel_units(root, folder, index.get(folder, {})):
            _common.check_unit(u)
            yield u


def _summary(us):
    hist, wds, flags = Counter(), defaultdict(list), Counter()
    groups = defaultdict(set)
    for u in us:
        hist[u["n"]] += 1
        wds[u["n"]].append(u["meta"]["words"])
        groups[u["n"]].add(u["group"])
        for f in u["flags"]:
            flags[f.split(":")[0] if not f.startswith("n0_") else f] += 1
    print("n histogram (units / distinct groups):")
    for n in sorted(hist):
        print(f"  n={n}: {hist[n]} units, {len(groups[n])} groups, median words {statistics.median(wds[n])}")
    print("flags:", dict(flags))
    print("drops:", dict(STATS))


if __name__ == "__main__":
    _common.check_source(SOURCE)
    fetch(_common.DEFAULT_CACHE)
    us = list(units(_common.DEFAULT_CACHE))
    _summary(us)
    import random
    rng = random.Random(0)
    for n in (0, 1, 3):
        cand = [u for u in us if u["n"] == n]
        if cand:
            print(json.dumps(rng.choice(cand), ensure_ascii=False, indent=1)[:4000])
