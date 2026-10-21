"""MailEx (Srivastava et al., EMNLP 2023): one Enron email, gold = its annotated request events.

Unit: one email (one "turn" of a MailEx thread). Text = "Subject: <subject>" line (when the raw thread
has one) + the email body, cut from the raw thread file to exactly the tokens the annotators labelled.
Gold item per Request_* event instance = the contiguous text from the first to the last token of
(trigger span + the instance's head argument), see HEAD_ROLES. Only annotator spans are used.
"""
from __future__ import annotations

import ast
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path
from statistics import median

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sources import _common  # noqa: E402

DRIVE_ID = "1a336g4-wlEwsVbXLPB9wPQnBDRE933mb"

SOURCE = {
    "name": "mailex",
    "title": "MailEx: Email Event and Argument Extraction",
    "domain": "emails",
    "list_types": ["requests"],
    "url": "https://github.com/salokr/Email-Event-Extraction",
    "paper": "Saurabh Srivastava, Gaurav Singh, Shou Matsumoto, Ali Raz, Paulo Costa, Joshua Poore, Ziyu Yao. "
             "MailEx: Email Event and Argument Extraction. EMNLP 2023. ACL Anthology 2023.emnlp-main.801, arXiv 2305.13469.",
    "licence": "CC-BY-SA-4.0",
    "licence_url": "https://creativecommons.org/licenses/by-sa/4.0/legalcode",
    "licence_quote": "The dataset is distributed under the [CC BY-SA 4.0 license](https://creativecommons.org/licenses/by-sa/4.0/legalcode).",
    "redistributable": True,
    "files": [
        {
            # Google Drive file linked from the repo README (repo HEAD 57507a458ce157378300d982914d7528448a381d, 2024-09-06).
            "url": f"https://drive.google.com/uc?export=download&id={DRIVE_ID}",
            "sha256": "dda3ce5da5ffc3452dd9e5a58cd69e19e68bd655eafe1deec48e87204f6c37b4",
            "path": "mailex.zip",
        }
    ],
    "unit_description": "One Enron business email (one message of a MailEx thread): its subject line and body.",
    "how_gold_was_made": (
        "Two native English-speaking Computer Science students annotated every email of 1,500 Enron threads with "
        "event triggers and argument spans (10 event types), seeing the earlier thread messages as context; "
        "instances where the two annotators disagreed on type or had no trigger overlap were deleted. "
        "Gold items here are the Request_* event instances (Request_Action, Request_Data, Request_Meeting, "
        "Request_Action_Data, Request_Meeting_Data), one item per instance, text = trigger span joined with the "
        "instance's head argument span."
    ),
    "known_issues": [
        "Disputed annotations were deleted by the authors, so an email with gold n=0 (or n=k) can still contain a real, unlabelled request; such n=0 emails are flagged maybe_missing_item:request_cue.",
        "Gold item text is a span we cut from the annotators' trigger and head-argument spans; it is extractive but its exact boundaries are our rule, so scoring should be fuzzy.",
        "Annotators read the whole thread; some requests only read as requests with that context (e.g. a bare follow-up question).",
        "The subject line is shown to the model but was never annotated.",
        "Request_Action_Data and some Request_Data instances are questions or offers ('Would you like me to forward ...?'), which a reader may not call a request.",
        "Enron emails are real people's private correspondence (names, phone numbers); the underlying CMU Enron corpus states no licence.",
    ],
}

SPLITS = ("train", "dev", "test")
REQUEST_TYPES = ("Request_Action", "Request_Data", "Request_Meeting", "Request_Action_Data", "Request_Meeting_Data")
# Head argument = the role that says WHAT is requested (first role found is used).
HEAD_ROLES = {
    "Request_Action": ("Action Description",),
    "Request_Action_Data": ("Action Description",),
    "Request_Data": ("Data idString", "Data Value", "Data Type"),
    "Request_Meeting": ("Meeting Agenda", "Meeting Name"),
    "Request_Meeting_Data": ("Meeting Agenda", "Meeting Name"),
}
MAX_ITEM_TOKENS = 40  # a trigger+head cover longer than this falls back to the head span alone
REQUEST_CUE = re.compile(r"(?i)\b(please|could you|can you|would you|let me know)\b|\?")
QUOTE_CUE = re.compile(r"(?im)(^>|\bwrote\s*:|\bwrites\b.*:|-{3,}\s*original message|^\s*from\s*:.*$\s*^\s*(to|sent)\s*:)")
SEP = re.compile(r"^-{29}[ \t]*$", re.M)
HEADER = re.compile(r"(?i)(from|to|cc|bcc|subject|date|sent)\s*:")
VARIANTS = {"``": ['"', "``", "''"], "''": ['"', "''", "``"], "-LRB-": ["("], "-RRB-": [")"]}
MIN_WORDS, MAX_WORDS = 15, 900
PREF_MIN, PREF_MAX = 30, 400


def fetch(cache: Path) -> Path:
    root = _common.fetch_all(SOURCE, cache)
    if not (root / "data" / "test").is_dir():
        with zipfile.ZipFile(root / "mailex.zip") as z:
            for m in z.namelist():
                if m.startswith("data/") and "__MACOSX" not in m:
                    z.extract(m, root)
    return root


def _flat(x):
    return [w for e in x for w in (_flat(e) if isinstance(e, list) else [e])]


def _segments(raw: str, nt: int | None = None):
    """Split a raw thread file into messages (newest first in the file). Tries a plain split on the
    29-dash separator first; if that does not give nt messages, glues parts that do not start with a
    header line back onto the previous part (a separator line inside a body)."""
    plain = [p for p in SEP.split(raw) if p.strip()]
    if nt is None or len(plain) == nt:
        return plain
    out = []
    for p in SEP.split(raw):
        if HEADER.match(p.lstrip()) or not out:
            out.append(p)
        elif p.strip():
            out[-1] += "-" * 29 + p
    return [p for p in out if p.strip()]


def _norm_ws(s: str) -> str:
    s = s.replace("\r\n", "\n").replace("\r", "\n").replace("\t", " ").replace("\xa0", " ")
    s = "\n".join(re.sub(r" {2,}", " ", ln).rstrip() for ln in s.split("\n"))
    return re.sub(r"\n{3,}", "\n\n", s)


def _parse(seg: str):
    s = seg.lstrip("\n")
    lines = s.split("\n")
    hdr, i = {}, 0
    while i < len(lines) and HEADER.match(lines[i]):
        k, v = lines[i].split(":", 1)
        hdr.setdefault(k.strip().upper(), v.strip())
        i += 1
    return hdr, s[sum(len(ln) + 1 for ln in lines[:i]):]


def _align(tokens, body):
    """Map each non-empty token to a (start, end) char span in body. None if it cannot be done
    without skipping non-space raw text (that text would be unannotated)."""
    pos, spans = 0, {}
    for i, tok in enumerate(tokens):
        if not tok:
            continue
        while pos < len(body) and body[pos].isspace():
            pos += 1
        hit = None
        for c in VARIANTS.get(tok, []) + [tok]:
            if body.startswith(c, pos):
                hit = (pos, pos + len(c))
                break
        if hit is None:
            return None
        spans[i] = hit
        pos = hit[1]
    return spans


def _role(label: str):
    # "Request_Action:B-Action Description" / "Request_Data:Context: I-Data idString"
    r = label.split(":", 1)[1].strip()
    if ":" in r:
        r = r.split(":", 1)[1].strip()
    bio, _, role = r.partition("-")
    return bio, role.strip()


def _item_tokens(etype, trig_idx, labels, ntok):
    """Return (first, last, rule) token indices of the item span, from annotator spans only."""
    by_role = {}
    for i, lab in enumerate(labels):
        if lab != "O":
            bio, role = _role(lab)
            by_role.setdefault(role, []).append(i)
    head = []
    head_role = None
    for r in HEAD_ROLES[etype]:
        if r in by_role:
            head, head_role = by_role[r], r
            break
    trig = [i for i in trig_idx if 0 <= i < ntok]
    pool = sorted(set(trig) | set(head))
    if not pool:
        return None
    a, b = pool[0], pool[-1]
    if not head:
        return a, b, "trigger_only"
    if b - a + 1 <= MAX_ITEM_TOKENS:
        return a, b, f"trigger+{head_role}"
    ha, hb = head[0], head[-1]
    if hb - ha + 1 <= MAX_ITEM_TOKENS:
        return ha, hb, f"{head_role}_only:cover_too_long"
    ta, tb = (min(trig), max(trig)) if trig else (ha, hb)
    return ta, tb, "trigger_only:cover_too_long"


def _thread_files(root: Path):
    for split in SPLITS:
        for f in sorted((root / "data" / split).glob("*.json")):
            yield split, f


def _raw_thread(root: Path, base: str):
    for name in (base + ".", base):
        p = root / "data" / "raw_threads" / name
        if p.exists():
            return p.read_text(encoding="utf-8", errors="replace")
    return None


def units(cache: Path, drops: Counter | None = None):
    root = Path(cache) / SOURCE["name"]
    drops = drops if drops is not None else Counter()
    for split, f in _thread_files(root):
        base = f.stem
        j = json.loads(f.read_text())
        nt = len(j["sentences"])
        raw = _raw_thread(root, base)
        segs = _segments(raw, nt)[::-1] if raw is not None else None
        seg_ok = segs is not None and len(segs) == nt
        for t in range(nt):
            toks = _flat(j["sentences"][t])
            nonempty = [i for i, w in enumerate(toks) if w]
            if not nonempty:
                drops["empty_turn"] += 1
                continue
            flags = ["whitespace_normalised", "quoted_history:none_in_turn"]
            hdr, body, spans = {}, None, None
            if seg_ok:
                hdr, body = _parse(segs[t])
                body = _norm_ws(body)
                spans = _align(toks, body)
            if spans is None:
                # fall back to the annotators' own tokens joined by spaces
                flags.append("text_from_tokens:" + ("raw_unaligned" if seg_ok else "raw_thread_missing_or_split_mismatch"))
                body, spans, pos = "", {}, 0
                for i in nonempty:
                    if body:
                        body += " "
                    spans[i] = (len(body), len(body) + len(toks[i]))
                    body += toks[i]
                b0 = 0
            else:
                b0 = spans[nonempty[0]][0]
                if body[spans[nonempty[-1]][1]:].strip() or body[:b0].strip():
                    flags.append("raw_text_outside_annotated_tokens_trimmed")
            body_txt = body[b0:spans[nonempty[-1]][1]]
            subject = hdr.get("SUBJECT", "")
            prefix = f"Subject: {subject}\n\n" if subject else ""
            if subject:
                flags.append("subject_line_not_annotated")
                if REQUEST_CUE.search(subject):
                    flags.append("subject_has_request_cue")
            text = prefix + body_txt
            off = len(prefix) - b0

            ev = j["events"].get(f"turn_{t}", {})
            items, item_meta, seen = [], [], set()
            dedup = False
            ntok = len(toks)
            for etype in REQUEST_TYPES:
                v = ev.get(etype)
                if not v:
                    continue
                for trig_s, labels in zip(v["triggers"], v["labels"]):
                    tr = ast.literal_eval(trig_s)
                    tidx = [int(x) for x in str(tr.get("indices", "")).split()]
                    res = _item_tokens(etype, tidx, labels, ntok)
                    if res is None:
                        drops["item_without_spans(unit_dropped)"] += 1
                        items = None
                        break
                    a, b, rule = res
                    while a <= b and not toks[a]:
                        a += 1
                    while b >= a and not toks[b]:
                        b -= 1
                    s, e = spans[a][0] + off, spans[b][1] + off
                    it = text[s:e]
                    key = it.strip().lower()
                    if key in seen:
                        dedup = True
                        continue
                    seen.add(key)
                    items.append({"text": it, "start": s, "end": e, "evidence": None})
                    item_meta.append({"event_type": etype, "trigger": tr.get("words"), "span_rule": rule,
                                      "token_range": [a, b + 1]})
                if items is None:
                    break
            if items is None:
                continue
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
            other_types = sorted(k for k in ev if k != "O" and k not in REQUEST_TYPES)
            if n == 0:
                flags.append("n0_certified_by:mailex_email_fully_annotated_no_request_event"
                             + ("_marked_O" if "O" in ev else ""))
                if REQUEST_CUE.search(body_txt) or REQUEST_CUE.search(subject):
                    flags.append("maybe_missing_item:request_cue")
            else:
                # cue sentences that no gold item touches (information for checkers; gold untouched)
                for m in re.finditer(r"[^.?!\n]+[.?!]*", text[len(prefix):]):
                    ms, me = m.start() + len(prefix), m.end() + len(prefix)
                    if REQUEST_CUE.search(m.group()) and not any(g["start"] < me and g["end"] > ms for g in items):
                        flags.append("request_cue_outside_gold")
                        break
            if any("only" in r["span_rule"] for r in item_meta):
                flags.append("item_span_rule_fallback")
            if QUOTE_CUE.search(body_txt):
                flags.append("forwarded_or_quoted_block_in_annotated_body")
            sender = hdr.get("FROM", "")
            u = {
                "source_id": f"mailex/data/{split}/{base}.json#turn_{t}:tokens[0:{ntok}]",
                "group": f"mailex:{base}",
                "text": text,
                "n": n,
                "gold_items": items,
                "list_type": "requests",
                "item_type": "exact_quote",
                "flags": flags,
                "meta": {
                    "split": split,
                    "thread": base,
                    "turn": t,
                    "turns_in_thread": nt,
                    "sender": sender,
                    "words": wc,
                    "items": item_meta,
                    "other_event_types": other_types,
                    "mailbox": base.split("_")[0],
                },
            }
            _common.check_unit(u)
            yield u


def _summary(us, drops):
    hist = Counter(u["n"] for u in us)
    print("n histogram:", dict(sorted(hist.items())))
    for n in sorted(hist):
        print(f"  n={n}: units={hist[n]} median_words={median(u['meta']['words'] for u in us if u['n'] == n)}")
    fl = Counter(x.split(":")[0] if x.startswith("n0_") else x for u in us for x in u["flags"])
    print("flags:", dict(fl.most_common()))
    print("dropped:", dict(drops))
    # pilot: clean = preferred length, n0 without request cue; spread over threads and senders
    bad = ("outside_preferred_30_400_words", "maybe_missing_item:request_cue")
    strict_bad = bad + ("request_cue_outside_gold", "item_span_rule_fallback", "subject_has_request_cue")
    for n in (0, 1, 2, 3):
        for name, b in (("clean", bad), ("strict", strict_bad)):
            c = [u for u in us if u["n"] == n and not any(x in b or x.startswith("text_from_tokens") for x in u["flags"])]
            print(f"  pilot n={n} {name}: units={len(c)} threads={len({u['group'] for u in c})} "
                  f"senders={len({u['meta']['sender'].lower() for u in c})} mailboxes={len({u['meta']['mailbox'] for u in c})}")


if __name__ == "__main__":
    import time
    t0 = time.time()
    cache = _common.DEFAULT_CACHE
    _common.check_source(SOURCE)
    fetch(cache)
    drops = Counter()
    us = list(units(cache, drops))
    print(f"units: {len(us)}  runtime {time.time() - t0:.1f}s")
    _summary(us, drops)
    for n in (0, 1, 2):
        ex = next(u for u in us if u["n"] == n and u["meta"]["words"] < 90 and len(u["flags"]) <= 4)
        print(json.dumps(ex, indent=1)[:2500])
