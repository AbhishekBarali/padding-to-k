#!/usr/bin/env python3
"""matcher.py: the item matcher for outcome 2, "invented" (PLAN/RUN-PLAN.md section 5.1). VERSION v0.

PRELIMINARY. Built and tuned only on dev-set outputs (the 312 reserve documents, arm "dev"); it refuses
any other run. Thresholds were fitted on provisional labels that are NOT the authors'
(analysis/dev/matcher_labels_dev.jsonl; the authors' labels replace them in v1), so every number it produces is
"preliminary, provisional labels".
It is deterministic code: no model of any kind is called.

For one output entry it returns one label:

  placeholder         common.is_placeholder() says so (passed through unchanged)
  repeat              common.is_duplicate() against the earlier substantive entries (passed through)
  true_item           matches an answer-list item not claimed by an earlier entry (gold index or indices;
                      several indices = one entry that merges several true items)
  split_of_true       matches an answer-list item an earlier entry already claimed: a piece of a split
                      item, or the same item again in other words
  in_text_wrong_type  real document text (allowing light rewording) that is not an item of the asked kind
  plausible_invented  in neither the answer list nor the document. Two notes ride along: "prompt_echo"
                      (copied from the prompt or schema, not made up) and "possible_note" (reads like a
                      model note that the placeholder rules missed, e.g. "Unknown Person 3")

Not decided in v0: missed_gold (a true item the answer list missed: needs a person, RUN-PLAN 5.4) and
beyond_excerpt (needs the wider source). Both currently land in in_text_wrong_type or
plausible_invented; see REPORT.md for how often that matters.

How each set is matched (5.1):
  names (wiki_people)   accent-folded, punctuation-free forms; exact, token-contained, or squashed
                        (spaces removed: "Anne Westfal l" = "Anne Westfall") match against each gold item,
                        then the same test against the sentence
  quotes (emails, job_posts, job_posts_knowledge, novel_quotes, receipts, clinical, reviews)
                        strip "please", "could you" and similar, edge punctuation, quote marks and any
                        broken-JSON tail ("]} ..."); find the tightest windows of the document holding the
                        entry's content words (fuzzy substring search; close spellings count; generic words
                        a model adds, such as "provide", "ensure", "development", do not), keep the window
                        whose word order fits the entry best; accept a gold item when it overlaps the gold
                        span by at least half of the shorter of the two (merges and splits allowed);
                        otherwise a reworded match against the gold text itself; otherwise
                        in_text_wrong_type when enough of the entry is found in one window
  meetings              answer items are annotators' summaries, never verbatim: lexical similarity
                        (mean of TF-IDF cosine and IDF-weighted recall of the item's job words; roles
                        normalised: PM / Project Manager / a speaker's "I" -> one token) against each gold
                        item and its evidence lines, assigned for the whole output at once (best pairs
                        first), then TF-IDF cosine against transcript windows. The similarity is a class
                        (LexicalSimilarity) so a sentence-embedding similarity can replace it later without
                        touching the rules

    python analysis/matcher.py fit  [--labels analysis/dev/matcher_labels_dev.jsonl]
    python analysis/matcher.py eval [--split heldout|test|audit|fit|all]   agreement with the labels
    python analysis/matcher.py run [runs/<dev run> ...] [--out analysis/dev]
                                   label every dev entry (matcher_entries_dev.csv) + matcher_report.md
With no runs given, every runs/*_dev folder is used.
"""
import argparse
import csv
import itertools
import json
import math
import os
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))
import common  # noqa: E402  (parse_output, field_of, is_placeholder, is_duplicate, normalise, loaders)

MATCHER_VERSION = "v0-dev-preliminary"
LABELS = ("true_item", "split_of_true", "in_text_wrong_type", "plausible_invented", "placeholder", "repeat")
NOT_DECIDED_V0 = ("missed_gold", "beyond_excerpt")
FAMILY = {"wiki_people": "name", "meetings": "summary"}           # every other set: "quote"

# Thresholds, frozen for v0 from `fit` on the fit half of the provisional dev labels.
#   win    the smallest search window, in words (the window is 1.5 x the entry's length + 4 words)
#   loc    share of the entry's content words found in one document window for it to count as located
#   para   share of words shared with a gold item's text (of the shorter) for a reworded true item
#   gold   meetings: similarity to a gold item (or w_ev x its evidence lines) for a true item
#   text   meetings: similarity to a transcript window for in_text_wrong_type
DEFAULT_THRESHOLDS = {"loc": 0.6, "para": 0.6, "win": 6, "gold": 0.35, "text": 0.3, "w_ev": 0.8}
THRESHOLDS = {
    "emails": {"loc": 0.5, "para": 0.6, "win": 6},
    "job_posts": {"loc": 0.6, "para": 0.6, "win": 6},
    "job_posts_knowledge": {"loc": 0.6, "para": 0.6, "win": 6},
    "novel_quotes": {"loc": 0.6, "para": 0.6, "win": 6},
    "receipts": {"loc": 0.6, "para": 0.6, "win": 6},
    "clinical": {"loc": 0.7, "para": 0.6, "win": 6},
    "reviews": {"loc": 0.6, "para": 0.6, "win": 6},   # never tuned: the review text is not on this machine
    "meetings": {"gold": 0.2, "text": 0.1, "w_ev": 0.8},
    "wiki_people": {},                                 # exact / contained match: nothing to fit
}
OVERLAP = 0.5   # fixed by the plan: overlap of at least half of the shorter span

STOP = set("""a an the and or but if then so of to in on at by for with from as is are was were be been being
this that these those it its it's i me my we our you your he him his she her they them their there here
will would shall should can could may might must do does did done have has had not no yes please kindly
any some all each every other such than too very just also only about into over under up down out off
again more most own same let lets us what which who whom whose when where why how am s t m d ll re ve""".split())
# Words a model adds when it turns document text into an item ("Provide the requested information",
# "Ensure someone attends the call", "portfolio development"): they say what to do with the text, not
# what the text is, so they do not count against finding the entry in the document.
GENERIC_WORDS = """provide provided provides ensure confirm confirms review reviews send check verify clarify update
discuss determine consider finalize finalise document documents coordinate follow assign make sure need needs needed
require required regarding related respond reply share give get help assist information info details detail
specific appropriate relevant necessary possible potential further additional new next steps step development
process handle task tasks action actions request requests item items""".split()
EDGE_PHRASES = re.compile(
    r"^(?:(?:please|kindly|could you(?: please)?|can you(?: please)?|would you(?: please)?|will you|"
    r"i would appreciate (?:it )?if you|i'd appreciate (?:it )?if you|i would like you to|"
    r"we need you to|i need you to)\b[\s,:]*)+", re.I)
JSON_TAIL = re.compile(r"""["']?\s*\]\s*\}.*$""", re.S)             # a model that broke out of the list
QUOTE_CHARS = "\"'\u2018\u2019\u201c\u201d`\u00ab\u00bb"
WORD = re.compile(r"[^\W_]+", re.U)


# ---------------------------------------------------------------------------------------------
# Text helpers
def fold(s):
    """Accent-folded lower case (models write "Peri" for "Peri" with an accent)."""
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def stem(t):
    """Very light stemming, the same on both sides: plural s, -ing, -ed, British -is- spellings."""
    t = t.replace("isation", "ization").replace("ise", "ize") if len(t) > 6 else t
    for suf in ("ing", "ed", "es", "s"):
        if len(t) > len(suf) + 3 and t.endswith(suf):
            return t[: -len(suf)]
    return t


def tokens_with_spans(text):
    """[(stemmed token, start, end)] over the raw text, so gold character spans map onto tokens."""
    return [(stem(fold(m.group())), m.start(), m.end()) for m in WORD.finditer(text)]


def toks(text):
    return [t for t, _, _ in tokens_with_spans(text)]


GENERIC = {stem(fold(w)) for w in GENERIC_WORDS}


def content(tokens, generic=False):
    """Content words; with generic=True also without the GENERIC words (used to find an entry in the
    document, never to compare it with a gold item)."""
    c = [t for t in tokens if t not in STOP and not (generic and t in GENERIC)]
    return c if c else [t for t in tokens if t not in STOP] or list(tokens)


def squash(text):
    return "".join(toks(text))


def clean_entry(entry, set_name):
    """Strip what is never part of an item: a broken-JSON tail, request openers, quote marks, edge
    punctuation. For novel quotes, quote marks and apostrophes are dropped (the source lost them)."""
    s = JSON_TAIL.sub("", entry).strip()
    s = s.strip(QUOTE_CHARS + " \t\n.,;:!?-*")
    s = EDGE_PHRASES.sub("", s)
    if set_name == "novel_quotes":
        s = re.sub("[" + re.escape(QUOTE_CHARS) + "]", " ", s)
    return s.strip(QUOTE_CHARS + " \t\n.,;:!?-*") or entry.strip()


# ---------------------------------------------------------------------------------------------
# Quote-like sets: fuzzy substring search with the overlap-with-answer-span rule
class DocIndex:
    """Token positions of one document and the token spans of its gold items."""

    def __init__(self, doc):
        self.text = doc["text"]
        self.tws = tokens_with_spans(self.text)
        self.tokens = [t for t, _, _ in self.tws]
        self.pos = defaultdict(list)
        for i, t in enumerate(self.tokens):
            self.pos[t].append(i)
        self.gold = []
        for g in doc.get("gold_items") or []:
            span = None
            if g.get("start") is not None and g.get("end") is not None:
                idx = [i for i, (_, a, b) in enumerate(self.tws) if a < g["end"] and b > g["start"]]
                span = (idx[0], idx[-1] + 1) if idx else None
            if span is None:                       # no offsets: find the gold text itself
                span = self.locate(toks(g["text"]))[1]
            self.gold.append({"span": span, "tokens": toks(g["text"])})

    def positions(self, tok):
        """Where a word occurs; a word the document lacks also matches a close spelling of one it has
        ("organizational" / "organisational", "intubation" / "intubated", "referr" / "refer")."""
        hit = self.pos.get(tok)
        if hit is not None or len(tok) < 5:
            return hit or ()
        cache = self.__dict__.setdefault("_near", {})
        if tok not in cache:
            out = []
            for t, ps in self.pos.items():
                if len(t) < 5 or t[:3] != tok[:3]:
                    continue
                pre = len(os.path.commonprefix([t, tok]))
                if pre >= max(5, 0.75 * min(len(t), len(tok))) or SequenceMatcher(None, t, tok).ratio() >= 0.85:
                    out.extend(ps)
            cache[tok] = sorted(out)
        return cache[tok]

    def locate(self, etoks, min_width=6):
        """Fuzzy substring search: the smallest stretches of the document that hold the most distinct
        content words of the entry, within a window about 1.5 times the entry's length.
        Returns (coverage, best span, [spans with that coverage]); spans are token [start, end)."""
        want = list(dict.fromkeys(content(etoks, generic=True)))
        if not want:
            return 0.0, None, []
        events = sorted((p, w) for w in want for p in self.positions(w))
        if not events:
            return 0.0, None, []
        width = max(min_width, int(1.5 * len(etoks)) + 4)
        best, spans = 0, []
        j, cnt = 0, Counter()
        for i in range(len(events)):               # two pointers over (position, word) events
            cnt[events[i][1]] += 1
            while events[i][0] - events[j][0] >= width or cnt[events[j][1]] > 1:
                cnt[events[j][1]] -= 1             # drop words that are too far away or held twice
                if not cnt[events[j][1]]:
                    del cnt[events[j][1]]
                j += 1
            have = len(cnt)
            span = (events[j][0], events[i][0] + 1)
            if have > best:
                best, spans = have, [span]
            elif have == best and span not in spans and len(spans) < 50:
                spans.append(span)
        # keep only the tightest stretches: a looser one holding the same words is not a match site
        short = min(b - a for a, b in spans)
        spans = [(a, b) for a, b in spans if b - a <= max(1.25 * short, short + 1)]
        return best / len(want), spans[0], spans


def _overlap(a, b):
    if a is None or b is None:
        return 0.0
    inter = max(0, min(a[1], b[1]) - max(a[0], b[0]))
    return inter / max(1, min(a[1] - a[0], b[1] - b[0]))


def _containment(a, b):
    sa, sb = set(content(a)), set(content(b))
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / min(len(sa), len(sb))


def match_quote(idx, entry_clean, claimed, th):
    etoks = toks(entry_clean)
    if not etoks:
        return "plausible_invented", None, 0.0, "empty after cleaning"
    cov, _, spans = idx.locate(etoks, th["win"])
    if cov >= th["loc"]:
        # match sites: the stretches whose words follow the entry's order most closely (a window that
        # straddles two neighbouring items must not turn one item into a merge, and a looser site must not
        # beat a tighter one that lies outside every gold span)
        def order(sp):
            return SequenceMatcher(None, idx.tokens[sp[0]:sp[1]], etoks, autojunk=False).ratio()
        top = max(order(sp) for sp in spans)
        spans = [sp for sp in spans if order(sp) >= top - 0.05]
        # then rank candidate golds: unclaimed first, then how much of the gold the site covers
        hits = {}
        for sp in spans:
            for gi, g in enumerate(idx.gold):
                if _overlap(sp, g["span"]) >= OVERLAP:
                    inter = max(0, min(sp[1], g["span"][1]) - max(sp[0], g["span"][0]))
                    frac = inter / max(1, g["span"][1] - g["span"][0])
                    hits.setdefault(sp, {})[gi] = frac
        if hits:
            def rank(item):
                sp, gs = item
                return (sum(1 for gi in gs if gi not in claimed), max(gs.values()), -(sp[1] - sp[0]))
            sp, gs = max(hits.items(), key=rank)
            free = sorted(gi for gi in gs if gi not in claimed)
            if free:
                return "true_item", free, cov, "span overlap"
            return "split_of_true", sorted(gs), cov, "span overlap, gold already claimed"
    # reworded match against the gold text itself
    best_gi, best = None, 0.0
    for gi, g in enumerate(idx.gold):
        c = _containment(etoks, g["tokens"])
        if c > best or (c == best and best_gi in claimed and gi not in claimed):
            best_gi, best = gi, c
    if best_gi is not None and best >= th["para"]:
        if best_gi not in claimed:
            return "true_item", [best_gi], best, "reworded gold"
        return "split_of_true", [best_gi], best, "reworded gold, already claimed"
    if cov >= th["loc"]:
        return "in_text_wrong_type", None, cov, "in document, no gold overlap"
    return "plausible_invented", None, cov, "not found in document"


# ---------------------------------------------------------------------------------------------
# Names (wiki_people)
def match_name(doc_text, gold_texts, entry_clean, claimed):
    e = toks(entry_clean)
    es = "".join(e)
    if not es:
        return "plausible_invented", None, 0.0, "empty after cleaning"
    hits = []
    for gi, g in enumerate(gold_texts):
        gt = toks(g)
        gs = "".join(gt)
        if es == gs or (set(gt) <= set(e)) or (set(e) <= set(gt) and len(es) >= 3) \
                or (min(len(es), len(gs)) >= 5 and (gs in es or es in gs)):
            hits.append(gi)
    if hits:
        free = [gi for gi in hits if gi not in claimed]
        if free:
            return "true_item", free, 1.0, "name match"
        return "split_of_true", hits, 1.0, "name match, already claimed"
    dt = toks(doc_text)
    n = len(e)
    if any(dt[i:i + n] == e for i in range(len(dt) - n + 1)) or (len(es) >= 4 and es in "".join(dt)):
        return "in_text_wrong_type", None, 1.0, "in sentence, not a gold person"
    return "plausible_invented", None, 0.0, "not in sentence"


# ---------------------------------------------------------------------------------------------
# Meetings: lexical similarity, written so an embedding similarity can replace it
ROLE_PATTERNS = [
    (re.compile(r"\b(project manager|the manager|pm)\b", re.I), " rolepm "),
    (re.compile(r"\b(industrial de[si]+gner|i_d_|id)\b", re.I), " roleid "),
    (re.compile(r"\b(user interface designer|user interface(?! (design|concept|prototype)\b)|interface designer|ui( designer)?|u_i_)\b",
                re.I), " roleui "),
    (re.compile(r"\b(marketing (expert|manager|person|executive)|marketing)\b", re.I), " roleme "),
]
SPEAKER = re.compile(r"^(Project Manager|Industrial Designer|User Interface|Marketing Expert):\s*(.*)$")
FIRST_PERSON = re.compile(r"\b(i'll|i will|i'm|i am|i)\b", re.I)
ROLE_OF = {"Project Manager": "rolepm", "Industrial Designer": "roleid", "User Interface": "roleui",
           "Marketing Expert": "roleme"}


def norm_roles(text):
    for pat, rep in ROLE_PATTERNS:
        text = pat.sub(rep, text)
    return text


def meeting_lines(text):
    """Transcript turns with the speaker's "I" replaced by the speaker's role token."""
    out = []
    for line in text.splitlines():
        m = SPEAKER.match(line.strip())
        if m:
            out.append(FIRST_PERSON.sub(" " + ROLE_OF[m.group(1)] + " ", m.group(2)))
        elif line.strip():
            out.append(line.strip())
    return out


class LexicalSimilarity:
    """TF-IDF cosine over role-normalised, stopword-free, lightly stemmed words. IDF comes from the
    transcript lines of the reserve meetings only. Replace with an object that has the same
    `sim(a, b)` method (for example sentence-embedding cosine) to upgrade the matcher."""

    def __init__(self, corpus_lines):
        df = Counter()
        for line in corpus_lines:
            df.update(set(self.terms(line)))
        self.n = max(1, len(corpus_lines))
        self.idf = {t: math.log((1 + self.n) / (1 + c)) + 1 for t, c in df.items()}
        self.default_idf = math.log(1 + self.n) + 1
        self._cache = {}

    @staticmethod
    def terms(text):
        return [t for t in toks(norm_roles(text)) if t not in STOP and len(t) > 1]

    def vec(self, text):
        v = self._cache.get(text)
        if v is None:
            tf = Counter(self.terms(text))
            v = {t: (1 + math.log(c)) * self.idf.get(t, self.default_idf) for t, c in tf.items()}
            norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
            v = {t: x / norm for t, x in v.items()}
            self._cache[text] = v
        return v

    def sim(self, a, b):
        va, vb = self.vec(a), self.vec(b)
        if len(va) > len(vb):
            va, vb = vb, va
        return sum(x * vb.get(t, 0.0) for t, x in va.items())

    def recall(self, entry, ref):
        """IDF-weighted share of the reference's job words (roles left out) that the entry contains:
        does the entry's job cover the answer item's job."""
        e = set(self.terms(entry))
        r = {t for t in self.terms(ref) if not t.startswith("role")}
        tot = sum(self.idf.get(t, self.default_idf) for t in r)
        return sum(self.idf.get(t, self.default_idf) for t in r if t in e) / tot if tot else 0.0


_SIM = None


def meeting_similarity():
    """One shared similarity, IDF fitted on the reserve (dev) meeting transcripts only."""
    global _SIM
    if _SIM is None:
        docs = common.load_documents()
        lines = [ln for d in docs.values() if d["set"] == "meetings" and d["split"] == "reserve"
                 for ln in meeting_lines(d["text"])]
        _SIM = LexicalSimilarity(lines)
    return _SIM


def meeting_gold_scores(doc, entry_clean, th, sim):
    """Similarity of one entry to each gold item: mean of TF-IDF cosine and job-word recall against the
    annotator's sentence, or w_ev x cosine against the item's evidence lines, whichever is higher."""
    out = []
    for g in doc.get("gold_items") or []:
        s_text = 0.5 * (sim.sim(entry_clean, g["text"]) + sim.recall(entry_clean, g["text"]))
        ev = " ".join(e["text"] for e in g.get("evidence") or [])
        s_ev = sim.sim(entry_clean, ev) if ev else 0.0
        out.append(max(s_text, th["w_ev"] * s_ev))
    return out


def assign_meeting(doc, cleans, th, sim):
    """Labels for all substantive entries of one meetings output at once. Pairs (entry, gold) are taken
    best score first, each entry and each gold once: so a weak early paraphrase cannot take a gold item
    from a closer later one. Entries left over that still pass the gold cut-off are split_of_true."""
    scores = [meeting_gold_scores(doc, c, th, sim) for c in cleans]
    pairs = sorted(((s, ei, gi) for ei, row in enumerate(scores) for gi, s in enumerate(row) if s >= th["gold"]),
                   key=lambda x: (-x[0], x[1], x[2]))
    got, used = {}, set()
    for s, ei, gi in pairs:
        if ei not in got and gi not in used:
            got[ei] = (gi, s)
            used.add(gi)
    lines = meeting_lines(doc["text"])
    windows = lines + [" ".join(lines[i:i + 3]) for i in range(max(0, len(lines) - 2))]
    res = []
    for ei, c in enumerate(cleans):
        if ei in got:
            res.append(("true_item", [got[ei][0]], got[ei][1], "similar to gold"))
            continue
        best_g = max(range(len(scores[ei])), key=lambda gi: scores[ei][gi], default=None)
        if best_g is not None and scores[ei][best_g] >= th["gold"]:
            res.append(("split_of_true", [best_g], scores[ei][best_g], "similar to gold, gold taken by another entry"))
            continue
        best = max((sim.sim(c, w) for w in windows), default=0.0)
        if best >= th["text"]:
            res.append(("in_text_wrong_type", None, best, "similar to transcript"))
        else:
            res.append(("plausible_invented", None, best, "not similar to gold or transcript"))
    return res


# ---------------------------------------------------------------------------------------------
# Public API
def thresholds_for(set_name, override=None):
    th = dict(DEFAULT_THRESHOLDS)
    th.update(THRESHOLDS.get(set_name, {}))
    if override:
        th.update(override)
    return th


META = re.compile(r"(^\W*\]|\b(the|this) (provided )?(document|text|email|passage|receipt|sentence|transcript|"
                  r"schema|excerpt|report|ad)\b|\bjson\b|\bminitems\b|\bschema\b|\bplaceholder\b|"
                  r"\bunknown (person|item|medication|drug|request|skill)\b|\bno (direct )?(speech|quotations?|dialogue)\b)",
                  re.I)


def _in_prompt(entry, prompt_text):
    if not prompt_text:
        return False
    c = common.core(entry)
    return len(c) >= 3 and f" {c} " in f" {common.core(prompt_text)} "


def match_output(doc, entries, escape_value="N/A", prompt_text=None, override=None, sim=None):
    """Label every entry of one output list, in order. Returns a list of dicts:
    {label, gold (list of gold indices or None), score, note}."""
    set_name = doc["set"]
    fam = FAMILY.get(set_name, "quote")
    th = thresholds_for(set_name, override)
    idx = DocIndex(doc) if fam == "quote" else None
    if fam == "summary" and sim is None:
        sim = meeting_similarity()
    claimed, subst, out, pending = set(), [], [], []
    for entry in entries:
        entry = entry if isinstance(entry, str) else json.dumps(entry)
        if common.is_placeholder(entry, escape_value, doc["text"]):
            out.append({"label": "placeholder", "gold": None, "score": None, "note": "common.is_placeholder"})
            continue
        if common.is_duplicate(entry, subst):
            out.append({"label": "repeat", "gold": None, "score": None, "note": "common.is_duplicate"})
            continue
        subst.append(entry)
        clean = clean_entry(entry, set_name)
        if fam == "summary":                     # decided below, for the whole output at once
            out.append(None)
            pending.append((len(out) - 1, entry, clean))
            continue
        if fam == "quote":
            lab, gold, score, note = match_quote(idx, clean, claimed, th)
        else:
            lab, gold, score, note = match_name(doc["text"], [g["text"] for g in doc["gold_items"]], clean, claimed)
        if lab == "true_item":
            claimed.update(gold)
        out.append(_finish(lab, gold, score, note, entry, clean, prompt_text))
    if pending:
        for (pos, entry, clean), res in zip(pending, assign_meeting(doc, [c for _, _, c in pending], th, sim)):
            out[pos] = _finish(*res, entry, clean, prompt_text)
    return out


def _finish(lab, gold, score, note, entry, clean, prompt_text):
    if lab == "plausible_invented" and _in_prompt(clean, prompt_text):
        note = "prompt_echo"
    elif lab == "plausible_invented" and META.search(entry):
        note = "possible_note"                 # reads like a model note the placeholder rules missed
    return {"label": lab, "gold": gold, "score": None if score is None else round(score, 3), "note": note}


def label_entry(doc, entry, earlier=(), escape_value="N/A", prompt_text=None):
    """The label of one entry, given the entries before it in the same output (which decide whether a
    gold item is already claimed and whether the entry repeats). Returns the dict match_output gives.
    For meetings the scorer labels a whole output at once (match_output), so an entry can also lose a
    gold item to a LATER, closer entry; this helper only sees the earlier ones."""
    return match_output(doc, [*earlier, entry], escape_value, prompt_text)[-1]


# ---------------------------------------------------------------------------------------------
# Dev outputs, labels, fitting, agreement
def dev_outputs(run_dirs):
    """(record, request, doc, items) for every ok output of the given DEV runs. Refuses any other run."""
    prompts, docs = common.load_prompts(), common.load_documents()
    reqs = {r["request_id"]: r for r in common.read_jsonl(common.DATA / "requests_dev.jsonl")}
    for rd in run_dirs:
        man = json.loads((Path(rd) / "manifest.json").read_text())
        recs = common.read_jsonl(Path(rd) / "raw.jsonl")       # raw_restricted.jsonl: review text, not here
        for r in recs:
            if r.get("arm") != "dev" or r["request_id"] not in reqs or docs[r["doc_id"]]["split"] != "reserve":
                raise SystemExit(f"{rd}: {r['request_id']} is not a dev request: the v0 matcher runs on "
                                 "dev outputs only")
            if r["status"] != "ok":
                continue
            req = reqs[r["request_id"]]
            parsed = common.parse_output(r.get("content"), common.field_of(req, prompts))
            yield man["model_key"], r, req, docs[r["doc_id"]], parsed["items"] or []


def prompt_text_of(req, prompts):
    return common.user_message(req, {"text": ""}, prompts)


def load_labels(path):
    return common.read_jsonl(path)


_OUT_CACHE = {}


def _wanted_outputs(labels, runs):
    """The labelled outputs, read once per set of runs."""
    key = tuple(runs)
    if key not in _OUT_CACHE:
        _OUT_CACHE[key] = {(m, r["request_id"]): (req, doc, items) for m, r, req, doc, items in dev_outputs(runs)}
    allout = _OUT_CACHE[key]
    want = defaultdict(set)
    for lab in labels:
        want[(lab["model_key"], lab["request_id"])].add(lab["entry_index"])
    return {k: (allout[k], idx) for k, idx in want.items()}


def _labelled_predictions(labels, runs, override_by_set=None):
    """Matcher label for every labelled entry: {(model, request_id, entry_index): prediction}."""
    prompts = common.load_prompts()
    pred = {}
    for (model, rid), ((req, doc, items), idx) in _wanted_outputs(labels, runs).items():
        ov = (override_by_set or {}).get(doc["set"])
        res = match_output(doc, items, prompts.get("escape_value", "N/A"), prompt_text_of(req, prompts), ov)
        for i in idx:
            pred[(model, rid, i)] = res[i]
    return pred


def agree(lab, p):
    """Agreement on the label; for true_item also on the gold item. An entry the labeller marked as a merge
    of several true items (gold_also) agrees when the matcher picks any of them."""
    if lab["label"] != p["label"]:
        return False
    if lab["label"] == "true_item":
        ok = {lab["gold_index"], *(lab.get("gold_also") or [])}
        return bool(ok & set(p["gold"] or []))
    return True


GRID = {
    "quote": [{"loc": a, "para": b, "win": c} for a, b, c in itertools.product(
        (0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0), (0.5, 0.6, 0.7, 0.8, 1.01), (6, 12))],
    "summary": [{"gold": a, "text": b, "w_ev": c} for a, b, c in itertools.product(
        (0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5), (0.1, 0.15, 0.2, 0.25, 0.3, 0.4), (0.0, 0.5, 0.8, 1.0))],
    "name": [{}],
}


def fit(labels, runs):
    """Grid search per set on the FIT half; ties go to the setting closest to the defaults."""
    fit_labels = [x for x in labels if x["split"] == "fit" and x["label"] in LABELS[:4]]
    by_set = defaultdict(list)
    for x in fit_labels:
        by_set[x["set"]].append(x)
    chosen = {}
    for s, labs in sorted(by_set.items()):
        fam = FAMILY.get(s, "quote")
        best = None
        for cand in GRID[fam]:
            pred = _labelled_predictions(labs, runs, {s: cand})
            acc = sum(agree(x, pred[(x["model_key"], x["request_id"], x["entry_index"])]) for x in labs)
            dist = sum(abs(cand[k] - DEFAULT_THRESHOLDS[k]) / (10.0 if k == "win" else 1.0) for k in cand)
            key = (acc, -dist)
            if best is None or key > best[0]:
                best = (key, cand)
        chosen[s] = {"thresholds": best[1], "fit_correct": best[0][0], "fit_n": len(labs)}
    return chosen


def evaluate(labels, runs, split="heldout"):
    labs = [x for x in labels if split == "all" or x["split"] == split]
    pred = _labelled_predictions(labs, runs)
    rows = defaultdict(lambda: [0, 0])
    conf = Counter()
    for x in labs:
        p = pred[(x["model_key"], x["request_id"], x["entry_index"])]
        ok = agree(x, p)
        for key in (x["set"], "ALL"):
            rows[key][0] += ok
            rows[key][1] += 1
        conf[(x["label"], p["label"])] += 1
    return rows, conf, pred


# ---------------------------------------------------------------------------------------------
# Running over all dev outputs, and the report
def run_all(runs, out_dir):
    prompts = common.load_prompts()
    esc = prompts.get("escape_value", "N/A")
    rows = []
    for model, r, req, doc, items in dev_outputs(runs):
        res = match_output(doc, items, esc, prompt_text_of(req, prompts))
        for i, x in enumerate(res):
            rows.append({"model_key": model, "request_id": r["request_id"], "entry_index": i, "doc_id": doc["doc_id"],
                         "set": doc["set"], "condition": req["condition"], "k": req["k"], "n": doc["n"],
                         "label": x["label"], "gold": "" if not x["gold"] else "+".join(map(str, x["gold"])),
                         "score": x["score"], "note": x["note"]})
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "matcher_entries_dev.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return rows


def pressure(row):
    """n < k for the counted conditions; the no-count condition has no k (reported as '-')."""
    if row["condition"] == "none":
        return "-"
    return "n<k" if row["n"] < row["k"] else "n>=k"


SPLIT_TITLE = {"heldout": "held-out half of the development labels (documents not used to fit thresholds; the "
                          "rules were written while these labels were visible)",
               "test": "fresh test labels (documents never seen before; drawn and labelled after the matcher "
                       "was frozen, then one bug fix: see REPORT.md)"}


def audit_section(labels, runs, rows):
    """Precision audit: random matcher plausible_invented (and in_text_wrong_type) calls on n < k documents,
    labelled with the matcher's call in view. Gives the share of the matcher's invented calls the
    labeller agrees with, per set, and a rough corrected invented share of the extras."""
    labs = [x for x in labels if x["split"] == "audit"]
    if not labs:
        return []
    pred = _labelled_predictions(labs, runs)
    per = defaultdict(Counter)
    for x in labs:
        p = pred[(x["model_key"], x["request_id"], x["entry_index"])]
        per[(x["stratum"], x["set"])][x["label"]] += 1
        per[(x["stratum"], x["set"])]["_still"] += p["label"] == (
            "plausible_invented" if x["stratum"] == "matcher_said_invented" else "in_text_wrong_type")
    ext = defaultdict(Counter)
    for r in rows:
        if pressure(r) == "n<k" and r["label"] in ("split_of_true", "in_text_wrong_type", "plausible_invented"):
            ext[r["set"]]["extras"] += 1
            if r["label"] == "plausible_invented":
                ext[r["set"]]["inv"] += 1
                ext[r["set"]]["inv_plain"] += r["note"] not in ("prompt_echo", "possible_note")
    L = ["## Precision audit of the invented calls", "",
         "Random entries the matcher called plausible_invented (no note, no prompt echo) or in_text_wrong_type,",
         "on documents with n < k, labelled WITH the matcher's call in view (not blind).", "",
         "| set | invented calls checked | label: invented | label: wrong type | label: split | label: note | "
         "wrong-type calls checked | label: not invented | extras | matcher invented (plain) | rough corrected |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    tot_corr, tot_ext = 0.0, 0
    for s_ in sorted({k[1] for k in per} | set(ext)):
        a = per.get(("matcher_said_invented", s_), Counter())
        b = per.get(("matcher_said_wrong_type", s_), Counter())
        na, nb = sum(v for k, v in a.items() if not k.startswith("_")), sum(v for k, v in b.items() if not k.startswith("_"))
        prec = a["plausible_invented"] / na if na else None
        e = ext[s_]
        corr = e["inv_plain"] * prec if prec is not None else None
        if corr is not None:
            tot_corr += corr
        tot_ext += e["extras"]
        L.append(f"| {s_} | {na} | {a['plausible_invented']} | {a['in_text_wrong_type']} | {a['split_of_true']} | "
                 f"{a['placeholder']} | {nb} | {nb - b['plausible_invented']} | {e['extras']} | {e['inv_plain']} | "
                 + (f"{corr:.0f} ({100 * corr / max(1, e['extras']):.0f}%)" if corr is not None else "-") + " |")
    L += ["", "rough corrected = matcher invented calls (plain) x the share of checked calls the label agreed with, per",
          "set; sets with no plain invented calls to check show '-'. The audit is small (3 to 8 calls per set), so",
          "read these as an order of magnitude, not an estimate with known error. Prompt echoes and possible notes",
          "are not in it.", ""]
    return L


def report(rows, evals, audit_lines=()):
    """evals: {split: (agreement rows, confusion)}."""
    sub = ("split_of_true", "in_text_wrong_type", "plausible_invented")
    L = ["# Matcher v0 on the dev outputs (PRELIMINARY)", "",
         f"Matcher `{MATCHER_VERSION}` (analysis/matcher.py); dev outputs only (the 312 reserve documents, arm",
         "`dev`; 3 models). The review set is not included: its text is licensed and is not on this machine",
         "(raw_restricted.jsonl, data/local/), so 293 documents are scored.",
         "**The labels used to fit and check the matcher are provisional and NOT the authors' (the authors'",
         "labels replace them in v1).** Every number here is preliminary. No document or output text is reproduced.", ""]
    for split, (ev, conf) in evals.items():
        L += [f"## Agreement with the provisional labels: {SPLIT_TITLE[split]}", "",
              "Agreement = same label, and for true_item the same gold item.", "",
              "| set | agree | n | share |", "|---|---|---|---|"]
        for s in sorted(ev, key=lambda k: (k == "ALL", k)):
            a, n = ev[s]
            L.append(f"| {s} | {a} | {n} | {a / n:.2f} |")
        L += ["", "Confusion (rows: provisional label, columns: matcher label):", "",
              "| label \\ matcher | " + " | ".join(LABELS[:5]) + " |", "|---" * 6 + "|"]
        for a_ in LABELS[:5]:
            if any(conf[(a_, b_)] for b_ in LABELS):
                L.append(f"| {a_} | " + " | ".join(str(conf[(a_, b_)]) for b_ in LABELS[:5]) + " |")
        called = sum(conf[(a_, "plausible_invented")] for a_ in LABELS)
        right = conf[("plausible_invented", "plausible_invented")]
        truth = sum(conf[("plausible_invented", b_)] for b_ in LABELS)
        L += ["", f"plausible_invented: the matcher said it {called} times, the label agreed {right} times; "
                  f"the label said it {truth} times.", ""]
    L += ["Thresholds: analysis/matcher.py THRESHOLDS, chosen by grid search per set on the fit half; see REPORT.md.",
          ""]
    L += list(audit_lines)
    L += ["## Label distribution per model x condition x (n < k)", "",
          "Entries of every ok output (shares of the row). `none` asks for no count, and its one answer serves",
          "k = 1, 3, 5, so it is counted once and shown with '-'.", "",
          "| model | condition | n vs k | entries | " + " | ".join(LABELS) + " |", "|---" * (4 + len(LABELS)) + "|"]
    cell = defaultdict(Counter)
    for r in rows:
        cell[(r["model_key"], r["condition"], pressure(r))][r["label"]] += 1
    for key in sorted(cell):
        c = cell[key]
        tot = sum(c.values())
        L.append(f"| {key[0]} | {key[1]} | {key[2]} | {tot} | " +
                 " | ".join(f"{c[l]} ({100 * c[l] / tot:.0f}%)" for l in LABELS) + " |")
    L += ["", "## Extra entries on documents with n < k", "",
          "Extra = a substantive entry (not a placeholder, not a repeat) that is not matched to a distinct true",
          "item: split_of_true + in_text_wrong_type + plausible_invented. Counted conditions only (`none` has no k).",
          "Of plausible_invented, `note?` reads like a model note the placeholder rules missed and `echo` was",
          "copied from the prompt or schema; both are in the count.", "",
          "| model | condition | extras | split_of_true | in_text_wrong_type | plausible_invented | note? | echo |",
          "|---|---|---|---|---|---|---|---|"]
    ext = defaultdict(Counter)
    for r in rows:
        if pressure(r) == "n<k" and r["label"] in sub:
            for key in ((r["model_key"], r["condition"]), (r["model_key"], "all"), ("all", r["condition"]),
                        ("all", "all")):
                ext[key][r["label"]] += 1
                ext[key]["echo"] += r["note"] == "prompt_echo"
                ext[key]["note"] += r["note"] == "possible_note"
    for key in sorted(ext, key=lambda k: (k[0] == "all", k[0], k[1] == "all", k[1])):
        c = ext[key]
        tot = sum(c[l] for l in sub)
        L.append(f"| {key[0]} | {key[1]} | {tot} | " + " | ".join(f"{c[l]} ({100 * c[l] / tot:.0f}%)" for l in sub)
                 + f" | {c['note']} | {c['echo']} |")
    L += ["", "Per set, all models and counted conditions pooled (n < k):", "",
          "| set | extras | split_of_true | in_text_wrong_type | plausible_invented | note? | echo |",
          "|---|---|---|---|---|---|---|"]
    ps = defaultdict(Counter)
    for r in rows:
        if pressure(r) == "n<k" and r["label"] in sub:
            ps[r["set"]][r["label"]] += 1
            ps[r["set"]]["echo"] += r["note"] == "prompt_echo"
            ps[r["set"]]["note"] += r["note"] == "possible_note"
    for s_ in sorted(ps):
        c = ps[s_]
        tot = sum(c[l] for l in sub)
        L.append(f"| {s_} | {tot} | " + " | ".join(f"{c[l]} ({100 * c[l] / tot:.0f}%)" for l in sub)
                 + f" | {c['note']} | {c['echo']} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["fit", "eval", "run"])
    ap.add_argument("runs", nargs="*")
    ap.add_argument("--labels", default=str(ROOT / "analysis" / "dev" / "matcher_labels_dev.jsonl"))
    ap.add_argument("--out", default=str(ROOT / "analysis" / "dev"))
    ap.add_argument("--split", default="heldout", choices=["fit", "heldout", "test", "audit", "all"],
                    help="which labels `eval` scores (test = drawn after the matcher was frozen)")
    args = ap.parse_args()
    runs = args.runs or sorted(str(p) for p in (ROOT / "runs").glob("*_dev") if (p / "raw.jsonl").exists())
    labels = load_labels(args.labels)
    if args.cmd == "fit":
        print(json.dumps(fit(labels, runs), indent=1))
    elif args.cmd == "eval":
        rows, conf, _ = evaluate(labels, runs, args.split)
        for s, (a, n) in sorted(rows.items()):
            print(f"{s:22s} {a:3d}/{n:3d} {a / n:.2f}")
        for (a, b), c in sorted(conf.items()):
            if a != b:
                print(f"  label {a:20s} matcher {b:20s} {c}")
    else:
        rows = run_all(runs, args.out)
        evals = {sp: evaluate(labels, runs, sp)[:2] for sp in ("heldout", "test")}
        audit = audit_section(labels, runs, rows)
        (Path(args.out) / "matcher_report.md").write_text(report(rows, evals, audit), encoding="utf-8")
        print(f"{len(rows)} entries labelled -> {args.out}/matcher_entries_dev.csv, matcher_report.md")


if __name__ == "__main__":
    main()
