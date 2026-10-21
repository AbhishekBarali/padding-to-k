"""BC3 email corpus (Ulrich, Murray & Carenini 2008): one W3C mailing-list email, gold = its Request sentences.

Unit: one email of a BC3 thread. Text = "Subject: <subject>" line + the email's own sentences
(quoted lines, which start with '>', are removed: annotators never labelled one of them as a request).
Gold item = a whole sentence that at least 2 of the thread's 3 annotators labelled Request ("req").
"""
from __future__ import annotations

import html
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sources import _common  # noqa: E402

WAYBACK = ("https://web.archive.org/web/20171223010448id_/https://www.cs.ubc.ca/cs-research/lci/"
           "research-groups/natural-language-processing/bc3-with-subj.zip")

SOURCE = {
    "name": "bc3",
    "title": "BC3: British Columbia Conversation Corpus (email part)",
    "domain": "emails",
    "list_types": ["requests"],
    "url": "https://web.archive.org/web/20210414031606/https://www.cs.ubc.ca/cs-research/lci/research-groups/natural-language-processing/bc3.html",
    "paper": "Jan Ulrich, Gabriel Murray, Giuseppe Carenini. A Publicly Available Annotated Corpus for Supervised Email "
             "Summarization. AAAI-08 EMAIL Workshop, Chicago, 2008. https://www.cs.ubc.ca/~carenini/PAPERS/ulrich-aaai08.pdf",
    "licence": "CC-BY-SA-3.0",
    "licence_url": "http://creativecommons.org/licenses/by-sa/3.0/",
    "licence_quote": "The BC3 Corpus is licensed under a Creative Commons Attribution-Share Alike 3.0 Unported License.",
    "redistributable": True,
    "files": [
        {
            # Official UBC file, live page now gone; Internet Archive capture 2017-12-23 (raw bytes via id_).
            "url": WAYBACK,
            "sha256": "ef4ce49a6daaa5a85aa4e2673efbd333671c7a5c832a29597d62f2b0844484a8",
            "path": "bc3-with-subj.zip",
        }
    ],
    "unit_description": "One email from a W3C mailing-list thread: its subject line and its own (non-quoted) sentences.",
    "how_gold_was_made": (
        "Each of the 40 threads was read in full by 3 annotators (UBC students) who, after writing summaries, "
        "labelled sentences with speech acts; the paper defines 'a Request asks the recipient to perform an activity'. "
        "Gold items here are the sentences that at least 2 of the 3 annotators labelled Request (majority vote)."
    ),
    "known_issues": [
        "Items are whole manually segmented sentences, so an item can carry extra words around the request.",
        "Majority vote drops requests seen by only one annotator; those emails carry maybe_missing_item:single_annotator_request (n=0) or single_annotator_request_present (n>0).",
        "Quoted lines ('>') were removed from the text; no quoted line was ever labelled Request by any annotator.",
        "Mailing-list emails contain signatures, URLs and list footers; the corpus double-escaped HTML entities, which are unescaped once here.",
        "Small set: 40 threads, 261 emails; it is a high-agreement check set, not a main grid source.",
        "The official page is gone; the file and licence were read from the Internet Archive copy of the official UBC page.",
    ],
}

MIN_WORDS, MAX_WORDS = 15, 900
PREF_MIN, PREF_MAX = 30, 400


def fetch(cache: Path) -> Path:
    root = _common.fetch_all(SOURCE, cache)
    if not (root / "corpus.xml").exists() or not (root / "annotation.xml").exists():
        with zipfile.ZipFile(root / "bc3-with-subj.zip") as z:
            for m in ("corpus.xml", "annotation.xml"):
                z.extract(m, root)
    return root


def _votes(ann_root):
    """votes[(listno, sent_id)] = Counter(tag -> number of annotators); annotators[listno] = descs."""
    votes = defaultdict(Counter)
    annotators = defaultdict(list)
    for th in ann_root.findall("thread"):
        ln = th.findtext("listno").strip()
        for a in th.findall("annotation"):
            annotators[ln].append((a.findtext("desc") or "").strip())
            lab = a.find("labels")
            seen = {(el.attrib["id"].strip(), el.tag) for el in (lab if lab is not None else [])}
            for sid, tag in seen:
                votes[(ln, sid)][tag] += 1
    return votes, annotators


def _clean(s: str) -> str:
    s = html.unescape(s or "")
    s = s.replace("\r", "").replace("\t", " ").replace("\xa0", " ")
    return re.sub(r"[ ]{2,}", " ", s)


def units(cache: Path, drops: Counter | None = None):
    root = Path(cache) / SOURCE["name"]
    drops = drops if drops is not None else Counter()
    corpus = ET.parse(root / "corpus.xml").getroot()
    votes, annotators = _votes(ET.parse(root / "annotation.xml").getroot())
    for th in corpus.findall("thread"):
        ln = th.findtext("listno").strip()
        n_ann = len(annotators[ln])
        if n_ann != 3:
            drops["thread_without_3_annotators"] += 1
            continue
        for di, doc in enumerate(th.findall("DOC")):
            flags = ["whitespace_normalised", "html_entities_unescaped"]
            subject = _clean(doc.findtext("Subject") or "").strip()
            sents = doc.find("Text").findall("Sent")
            prefix = f"Subject: {subject}\n\n" if subject else ""
            if subject:
                flags.append("subject_line_not_annotated")
            body, items, item_meta, minority, removed, seen = "", [], [], [], [], set()
            dedup = False
            for s in sents:
                sid = s.attrib["id"].strip()
                raw = _clean(s.text)
                st = raw.strip()
                v = votes[(ln, sid)]["req"]
                if not st:
                    continue
                if st.startswith(">") and v == 0:
                    removed.append(sid)
                    continue
                if body:
                    body += "\n" if body_end_nl else " "
                start = len(prefix) + len(body)
                body += st
                body_end_nl = raw.rstrip(" ").endswith("\n")
                if v >= 2:
                    key = st.lower()
                    if key in seen:
                        dedup = True
                        continue
                    seen.add(key)
                    items.append({"text": st, "start": start, "end": start + len(st), "evidence": None})
                    item_meta.append({"sent_id": sid, "req_votes": v, "of": n_ann})
                elif v == 1:
                    minority.append({"sent_id": sid, "text": st})
            if not body:
                drops["empty_email"] += 1
                continue
            body = re.sub(r"\n{3,}", "\n\n", body)
            text = prefix + body
            flags.append("quoted_history_removed" if removed else "quoted_history:none")
            if dedup:
                flags.append("gold_dedup")
            n = len(items)
            if n > 8:
                drops["n_gt_8"] += 1
                continue
            wc = _common.words(text)
            if wc < MIN_WORDS:
                drops["under_15_words"] += 1
                continue
            if wc > MAX_WORDS:
                drops["over_900_words"] += 1
                continue
            if not (PREF_MIN <= wc <= PREF_MAX):
                flags.append("outside_preferred_30_400_words")
            if n == 0:
                flags.append("n0_certified_by:bc3_3_annotators_labelled_whole_thread_no_majority_req")
                if minority:
                    flags.append("maybe_missing_item:single_annotator_request")
            elif minority:
                flags.append("single_annotator_request_present")
            if any(m["req_votes"] == 2 for m in item_meta):
                flags.append("item_agreement_2_of_3")
            ids = [s.attrib["id"].strip() for s in sents]
            u = {
                "source_id": f"bc3/corpus.xml#thread={ln}/doc={di}/sents={ids[0]}..{ids[-1]}",
                "group": f"bc3:{ln}",
                "text": text,
                "n": n,
                "gold_items": items,
                "list_type": "requests",
                "item_type": "exact_quote",
                "flags": flags,
                "meta": {
                    "thread": ln,
                    "thread_name": (th.findtext("name") or "").strip(),
                    "doc_index": di,
                    "sender": _clean(doc.findtext("From") or "").strip(),
                    "words": wc,
                    "items": item_meta,
                    "single_annotator_requests": minority,
                    "removed_quoted_sent_ids": removed,
                    "annotators": annotators[ln],
                },
            }
            _common.check_unit(u)
            yield u


if __name__ == "__main__":
    import time
    t0 = time.time()
    cache = _common.DEFAULT_CACHE
    _common.check_source(SOURCE)
    fetch(cache)
    drops = Counter()
    us = list(units(cache, drops))
    print(f"units: {len(us)}  runtime {time.time() - t0:.1f}s")
    hist = Counter(u["n"] for u in us)
    print("n histogram:", dict(sorted(hist.items())))
    for n in sorted(hist):
        print(f"  n={n}: units={hist[n]} median_words={median(u['meta']['words'] for u in us if u['n'] == n)}")
    fl = Counter(x.split(":")[0] if x.startswith("n0_") else x for u in us for x in u["flags"])
    print("flags:", dict(fl.most_common()))
    print("dropped:", dict(drops))
    agree = Counter(m["req_votes"] for u in us for m in u["meta"]["items"])
    print("item agreement (votes of 3):", dict(agree))
    for n in (0, 1, 2):
        ex = next(u for u in us if u["n"] == n and u["meta"]["words"] < 120)
        print(json.dumps(ex, indent=1)[:2500])
