"""Few-NERD loader: people named in one Wikipedia sentence.

One unit = one Few-NERD sentence (supervised split, test set). Few-NERD ships sentences in a
shuffled order with no article or paragraph id, so consecutive sentences cannot be put back
into multi-sentence documents (checked: consecutive test sentences share an entity token no more
often than random pairs). Gold = the distinct person-* mention strings tagged by the annotators.
"""
from __future__ import annotations

import json
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path

try:
    from . import _common
except ImportError:  # pragma: no cover
    import _common  # type: ignore

REVISION = "205f3e9c9f3577ea2561d43f2f62dc249ab92d5b"
HF = f"https://huggingface.co/datasets/DFKI-SLT/few-nerd/resolve/{REVISION}/"

SOURCE = {
    "name": "fewnerd",
    "title": "Few-NERD",
    "domain": "wiki",
    "list_types": ["people"],
    "url": "https://github.com/thunlp/Few-NERD",
    "paper": "Ding, Xu, Chen, Wang, Han, Xie, Zheng and Liu (2021). Few-NERD: A Few-shot Named Entity "
             "Recognition Dataset. ACL-IJCNLP 2021, pages 3198-3213. https://aclanthology.org/2021.acl-long.248",
    "licence": "CC-BY-SA-4.0",
    "licence_url": "https://creativecommons.org/licenses/by-sa/4.0/",
    "licence_quote": "Few-NERD dataset is distributed under the CC BY-SA 4.0 license. The code is distributed "
                     "under the Apache 2.0 license.",
    "redistributable": True,
    "files": [{
        "url": HF + "supervised/test-00000-of-00001.parquet",
        "sha256": "b7ad746fcbeb68fcc235ba7142d7c3723ea2dc39930089e947284defecf300c6",
        "path": "supervised/test-00000-of-00001.parquet",
    }],
    "unit_description": "One English Wikipedia sentence from the Few-NERD supervised test set.",
    "how_gold_was_made": "70 trained annotators and 10 experts labelled every entity in Wikipedia paragraphs with "
                         "8 coarse and 66 fine types: \"Each paragraph is independently annotated by two well-trained "
                         "annotators. Then, an experienced expert goes over the paragraph for possible wrong or "
                         "omissive annotations, and make the final decision.\" Gold items here are the distinct "
                         "strings of the person-* spans in the sentence.",
    "known_issues": [
        "Sentences only: Few-NERD has no article or paragraph id and the sentences are shuffled, so no "
        "multi-sentence windows can be built. Each sentence is its own group, so two sentences from the same "
        "article may land in different splits.",
        "Few-NERD uses IO tags, so two person names written directly next to each other merge into one span; "
        "spans that contain a comma, 'and', '&' or ';' are flagged io_span_has_separator.",
        "Text is rebuilt from tokens: spaces are removed before closing punctuation and clitics and after "
        "opening brackets, and PTB quote tokens (`` and '') become a straight double quote (flags tokens_joined, "
        "ptb_quotes_to_ascii).",
        "Gold counts distinct strings: a repeated name counts once (flag gold_dedup); a short form and a long "
        "form of what may be the same person ('Smith', 'John Smith') are both kept and flagged "
        "same_person_multiple_forms.",
        "Name variants of one person that are not substrings of each other ('Jean de Cabannes', 'Jean de Cabanes') "
        "count as separate items; names sharing a word (also relatives such as 'John Smith', 'Mary Smith') are "
        "flagged names_share_token for the human check.",
        "Pronouns (he, she, his, her) are not entities. n = 0 sentences with such pronouns are flagged "
        "pronoun_person_reference_present: a model might list the pronoun's referent.",
        "Few-NERD has some annotation noise (reported sentence-level accuracy >= 95% per batch, Cohen's kappa 76.44%).",
        "Fictional characters, gods and groups follow Few-NERD's typing (gods are other-god, bands are "
        "organization-showorganization), so they are not gold people.",
    ],
}

COARSE_PERSON = 7          # fewnerd coarse tag id for "person"
FINE_NAMES = {50: "person-actor", 51: "person-artist/author", 52: "person-athlete", 53: "person-director",
              54: "person-other", 55: "person-politician", 56: "person-scholar", 57: "person-soldier"}
MIN_W, MAX_W = 15, 900

NO_SPACE_BEFORE = re.compile(r"^([,.;:!?)\]}%]+|'s|'S|n't|'re|'ve|'ll|'d|'m)$")
NO_SPACE_AFTER = {"(", "[", "{", "$"}
QUOTE_TOKS = {"``", "''", '"'}
PRONOUN = re.compile(r"\b(he|she|him|her|his|hers|himself|herself)\b", re.I)
SEPARATORS = {",", "and", "&", ";"}

STATS = Counter()


def fetch(cache: Path) -> Path:
    return _common.fetch_all(SOURCE, cache)


def _join(tokens):
    """Join tokens into text. Returns (text, [(start, end) per token], used_ptb_quotes)."""
    toks = [str(t) for t in tokens]
    nq = sum(t in QUOTE_TOKS for t in toks)
    paired = nq % 2 == 0
    out, offs, pos = [], [], 0
    glue_next = False
    q_open = False
    used_quotes = False
    for k, tok in enumerate(toks):
        render = tok
        no_before = bool(NO_SPACE_BEFORE.match(tok))
        no_after = tok in NO_SPACE_AFTER
        if tok in QUOTE_TOKS:
            render = '"'
            used_quotes = used_quotes or tok != '"'
            if paired:
                if not q_open:
                    no_after, no_before = True, False
                else:
                    no_before, no_after = True, False
                q_open = not q_open
        if k > 0 and not (no_before or glue_next):
            out.append(" ")
            pos += 1
        offs.append((pos, pos + len(render)))
        out.append(render)
        pos += len(render)
        glue_next = no_after
    return "".join(out), offs, used_quotes


def _units(cache: Path):
    import pyarrow.parquet as pq

    root = Path(cache) / SOURCE["name"]
    tbl = pq.read_table(root / SOURCE["files"][0]["path"]).to_pydict()
    for sid, tokens, coarse, fine in zip(tbl["id"], tbl["tokens"], tbl["ner_tags"], tbl["fine_ner_tags"]):
        text, offs, used_quotes = _join(tokens)
        nw = _common.words(text)
        if nw < MIN_W or nw > MAX_W:
            STATS["drop_length"] += 1
            continue
        # IO spans of the person type
        spans, k = [], 0
        while k < len(coarse):
            if coarse[k] == COARSE_PERSON:
                j = k
                while j + 1 < len(coarse) and coarse[j + 1] == COARSE_PERSON:
                    j += 1
                spans.append((k, j))
                k = j + 1
            else:
                k += 1
        gold, seen, fine_types, flags = [], set(), [], ["tokens_joined"]
        dedup = sep = 0
        for a, b in spans:
            s, e = offs[a][0], offs[b][1]
            t = text[s:e]
            if any(str(tokens[x]) in SEPARATORS for x in range(a, b + 1)):
                sep += 1
            key = t.strip().lower()
            if key in seen:
                dedup += 1
                continue
            seen.add(key)
            gold.append({"text": t, "start": s, "end": e, "evidence": None})
            fine_types.append(sorted({FINE_NAMES.get(int(fine[x]), str(fine[x])) for x in range(a, b + 1)}))
        n = len(gold)
        if n > 8:
            STATS["drop_n_over_8"] += 1
            continue
        if used_quotes:
            flags.append("ptb_quotes_to_ascii")
        if n == 0:
            flags.append("n0_certified_by:fewnerd_full_entity_annotation_no_person_span")
            if PRONOUN.search(text):
                flags.append("pronoun_person_reference_present")
        if dedup:
            flags.append("gold_dedup")
        if sep:
            flags.append("io_span_has_separator")
        names = [g["text"].lower() for g in gold]
        multi = [x for x in names for y in names
                 if x != y and re.search(r"(?<!\w)" + re.escape(x) + r"(?!\w)", y)]
        if multi:
            flags.append("same_person_multiple_forms")
        toks = [set(w for w in re.findall(r"\w+", x) if len(w) >= 3 and w not in {"the", "von", "van", "del", "der"})
                for x in names]
        if any(toks[i] & toks[j] for i in range(len(toks)) for j in range(i + 1, len(toks))):
            flags.append("names_share_token")
        other_types = sorted({int(c) for c in coarse} - {0, COARSE_PERSON})
        yield {
            "source_id": f"fewnerd:supervised/test:{sid}:tokens0-{len(tokens)}",
            "group": f"fewnerd:test:{sid}",
            "text": text,
            "n": n,
            "gold_items": gold,
            "list_type": "people",
            "item_type": "named_entity",
            "flags": flags,
            "meta": {
                "split": "supervised/test",
                "revision": REVISION,
                "fine_types": fine_types,
                "n_person_spans_before_dedup": len(spans),
                "other_coarse_types_present": other_types,
                "words": nw,
            },
        }


def units(cache: Path):
    for u in _units(cache):
        _common.check_unit(u)
        yield u


def _summary(us):
    hist, wds, flags = Counter(), defaultdict(list), Counter()
    for u in us:
        hist[u["n"]] += 1
        wds[u["n"]].append(u["meta"]["words"])
        for f in u["flags"]:
            flags[f] += 1
    print("n histogram:")
    for n in sorted(hist):
        print(f"  n={n}: {hist[n]} units, median words {statistics.median(wds[n])}")
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
        print(json.dumps(rng.choice([u for u in us if u["n"] == n]), ensure_ascii=False, indent=1))
