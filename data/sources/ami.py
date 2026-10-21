"""AMI Meeting Corpus: abstractive-summary ACTIONS and DECISIONS as gold lists.

One unit is a short window of a meeting transcript (speaker turns, verbatim words) cut around
a run of annotator-written ACTIONS (or DECISIONS) sentences, using the annotator's own links
from each summary sentence to the dialogue acts it summarises. n = 0 windows come only from
meetings whose annotator wrote NA under that section.

Recipe (per list): items sorted by first linked token. For every run of consecutive items,
window = [first linked token - margin, last linked token + margin], snapped outward to
dialogue-act boundaries. Keep it if it is <= 1200 word tokens, 15..900 rendered words, holds no
dialogue act linked to any OTHER item of that list, and the meeting has no unlinked item of
that list. margin = 150 tokens; if that window fails on length or on another item's link, the
loader retries with 100 and then 50 (recorded in meta.margin_tokens, flag short_margin).
"""
from __future__ import annotations

import collections
import glob
import json
import os
import re
import statistics
import sys
import zipfile
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sources import _common as C  # noqa: E402

ZIP_NAME = "ami_public_manual_1.6.2.zip"
ZIP_URL = "https://groups.inf.ed.ac.uk/ami/AMICorpusAnnotations/ami_public_manual_1.6.2.zip"
ZIP_SHA = "b56e5babb2496b8795deeeda7e71178d7fbc9963f94276cf2a3f4b56ebbc9f9d"

SOURCE = {
    "name": "ami",
    "title": "AMI Meeting Corpus (manual annotations 1.6.2 / release 1.7): abstractive summaries",
    "domain": "meeting_notes",
    "list_types": ["action_items", "decisions"],
    "url": "https://groups.inf.ed.ac.uk/ami/corpus/",
    "paper": "Carletta et al. 2005, The AMI Meeting Corpus: A Pre-Announcement, MLMI 2005 (LNCS 3869)",
    "licence": "CC-BY-4.0",
    "licence_url": "https://groups.inf.ed.ac.uk/ami/corpus/license.shtml",
    "licence_quote": ("The AMI corpus and its annotations are released under the Creative Commons "
                      "Attribution 4.0 International Public License agreement (CC BY 4.0)."),
    "redistributable": True,
    "files": [{"url": ZIP_URL, "sha256": ZIP_SHA, "path": ZIP_NAME}],
    "unit_description": ("A window of one AMI meeting transcript (one speaker turn per line, verbatim "
                         "words) cut around a known number of annotator-summarised action items or decisions."),
    "how_gold_was_made": (
        "One AMI annotator per meeting wrote an abstractive summary with ACTIONS and DECISIONS sections "
        "('Name the next steps that each member of the group will take until the next meeting'; "
        "'Name all decisions that were made during the meeting'), writing NA for an empty section, and "
        "then linked each summary sentence to the dialogue acts it summarises. No reliability figure was published."),
    "known_issues": [
        "One annotator per meeting and no published agreement; minor or implicit commitments can be missing.",
        "A gold sentence can bundle several assignees or decisions; n counts sentences, not tasks.",
        "Action links cluster in the wrap-up at the end of the meeting; meta.rel_position records window position.",
        "Meetings whose annotator wrote NA under ACTIONS are mostly final ('d') meetings of a series, so n=0 "
        "action windows over-represent end-of-project talk.",
        "Scenario meetings are a role-play (designing a TV remote), so items are templated ('X will work on Y').",
        "Overlapping speech is serialised by dialogue-act start time.",
    ],
}

NITE = "{http://nite.sourceforge.net/}"
NA_RE = re.compile(r"^\W*n/?a\W*$", re.I)
HREF = re.compile(r"([\w.\-]+)\.xml#id\(([^)]+)\)(?:\.\.id\(([^)]+)\))?")
ROLE_NAMES = {"PM": "Project Manager", "ME": "Marketing Expert", "UI": "User Interface",
              "ID": "Industrial Designer"}
CUE_RE = re.compile(r"\b(will|should|need to|going to|gonna|next meeting)\b", re.I)
# stricter, second-person assignment cue (a subset of CUE_RE hits); flag only, never gold
ASSIGN_RE = re.compile(r"\b(you(?:'re| are)? (?:gonna|going to|gotta)|you'll|you will|you need to|you should|"
                       r"you have to|you've got to|your job)\b", re.I)
ASSIGNEE_RE = re.compile(r"project manager|marketing|user interface|interface designer|industrial designer|"
                         r"\bteam\b|\beveryone\b|\ball\b|\beach\b|\bgroup\b", re.I)
# NA meetings whose wrap-up holds next-step talk of a kind other AMI annotators DO list under
# ACTIONS (role assignments, "I will write the minutes", "send me your presentation", "complete
# the final questionnaire"). Set from the loader author's own read of the final windows on
# 2026-10-13, NOT from the AMI annotation: it only adds a flag for the human check, gold is unchanged.
NA_SUSPECT = {
    "ES2007a": ("strong", "PM assigns each role its task in the wrap-up"),
    "IS1001b": ("strong", "PM will write a summary; asks members to email presentations"),
    "TS3005b": ("strong", "PM will write minutes; individual actions for the other roles"),
    "TS3012a": ("medium", "personal coach will give your assignments"),
    "ES2015b": ("medium", "we'll have to do more research; investigate financial implications"),
    "ES2015d": ("medium", "don't forget to complete final questionnaire and meeting summary"),
    "ES2016d": ("medium", "complete the final questionnaire; PM still has to do minutes"),
}
MARGINS = (150, 100, 50)
MAXTOK = 1200
MIN_WORDS, MAX_WORDS = 15, 900
MAX_N = 8
LISTS = (("actions", "action_items"), ("decisions", "decisions"))
NEEDED = ("abstractive/", "dialogueActs/", "words/", "corpusResources/meetings.xml", "LICENCE.txt")


# ----------------------------------------------------------------------------- fetch
def fetch(cache: Path) -> Path:
    root = C.fetch_all(SOURCE, cache)
    out = root / "manual"
    marker = out / ".extracted"
    if not marker.exists():
        with zipfile.ZipFile(root / ZIP_NAME) as z:
            for name in z.namelist():
                keep = name.startswith(NEEDED) or (name.startswith("extractive/") and name.endswith(".summlink.xml"))
                if keep and not name.endswith("/") and ".." not in name:
                    z.extract(name, out)
        marker.write_text("ok\n")
    return out


# ----------------------------------------------------------------------------- parsing
def _roles(root: Path) -> dict:
    import xml.etree.ElementTree as ET
    roles = {}
    for m in ET.parse(root / "corpusResources" / "meetings.xml").getroot().iter("meeting"):
        obs = m.get("observation")
        for s in m.iter("speaker"):
            if s.get("role"):
                roles[(obs, s.get("nxt_agent"))] = ROLE_NAMES.get(s.get("role"), s.get("role"))
    return roles


def _summary(root: Path, meeting: str):
    """-> {section: {"items": [(id, text)], "na": bool, "annotator": str}}"""
    import xml.etree.ElementTree as ET
    r = ET.parse(root / "abstractive" / f"{meeting}.abssumm.xml").getroot()
    out = {}
    for sec, _ in LISTS:
        el = r.find(sec)
        if el is None:
            out[sec] = None
            continue
        items, na = [], False
        if NA_RE.match((el.text or "").strip()):
            na = True
        for s in el.findall("sentence"):
            t = re.sub(r"\s+", " ", (s.text or "")).strip()
            if NA_RE.match(t):
                na = True
            elif t:
                items.append((s.get(NITE + "id"), t))
        ann = (el.get(NITE + "id") or "").split(".")[1] if el.get(NITE + "id") else None
        out[sec] = {"items": items, "na": na and not items, "annotator": ann}
    return out


def _links(root: Path, meeting: str) -> dict:
    import xml.etree.ElementTree as ET
    p = root / "extractive" / f"{meeting}.summlink.xml"
    links = collections.defaultdict(list)
    if not p.exists():
        return links
    for el in ET.parse(p).getroot():
        ext = ab = None
        for ptr in el:
            m = HREF.search(ptr.get("href", ""))
            if m:
                if ptr.get("role") == "extractive":
                    ext = m.group(2)
                else:
                    ab = m.group(2)
        if ext and ab:
            links[ab].append(ext)
    return links


def _segments(root: Path, meeting: str):
    """Time-ordered segments (dialogue acts, plus runs of words outside any act).

    Each segment: dict(da, spk, words=[(text, punc)], start). Only <w> tokens are kept, so
    vocalsound / gap / disfmarker events are dropped; word text (including um, uh and truncated
    words) is kept exactly as transcribed.
    """
    import xml.etree.ElementTree as ET
    segs = []
    stats = collections.Counter()
    for wf in sorted(glob.glob(str(root / "words" / f"{meeting}.*.words.xml"))):
        spk = os.path.basename(wf).split(".")[1]
        elems = list(ET.parse(wf).getroot())
        idx = {e.get(NITE + "id"): i for i, e in enumerate(elems)}
        covered = [None] * len(elems)
        daf = root / "dialogueActs" / f"{meeting}.{spk}.dialog-act.xml"
        das = []
        if daf.exists():
            for d in ET.parse(daf).getroot():
                if d.tag != "dact":
                    continue
                ids = []
                for ch in d:
                    if ch.tag != NITE + "child":
                        continue
                    m = HREF.search(ch.get("href", ""))
                    if not m or m.group(2) not in idx:
                        continue
                    a = idx[m.group(2)]
                    b = idx.get(m.group(3) or m.group(2), a)
                    ids.extend(range(a, b + 1))
                if ids:
                    das.append((d.get(NITE + "id"), sorted(set(ids))))
        for da_id, ids in das:
            for i in ids:
                covered[i] = da_id

        def mk(da_id, ids):
            ws, st = [], None
            for i in ids:
                e = elems[i]
                if e.tag != "w":
                    continue
                ws.append((e.text or "", e.get("punc") == "true"))
                if st is None and e.get("starttime") not in (None, ""):
                    st = float(e.get("starttime"))
            return ws, st

        for da_id, ids in das:
            ws, st = mk(da_id, ids)
            if ws:
                segs.append({"da": da_id, "spk": spk, "words": ws, "start": st, "first": ids[0]})
        run = []
        for i, e in enumerate(elems + [None]):
            if e is not None and covered[i] is None and e.tag == "w":
                run.append(i)
                continue
            if run:
                ws, st = mk(None, run)
                if ws:
                    segs.append({"da": None, "spk": spk, "words": ws, "start": st, "first": run[0]})
                    stats["uncovered_words"] += sum(1 for _, p in ws if not p)
                run = []
    # segments with no timed word inherit the previous segment time of the same speaker
    by_spk = collections.defaultdict(list)
    for s in segs:
        by_spk[s["spk"]].append(s)
    for lst in by_spk.values():
        lst.sort(key=lambda s: s["first"])
        last = 0.0
        for s in lst:
            if s["start"] is None:
                s["start"] = last
            last = s["start"]
    segs.sort(key=lambda s: (s["start"], s["spk"], s["first"]))
    tok = 0
    for s in segs:
        s["tok0"] = tok
        tok += sum(1 for _, p in s["words"] if not p)
        s["tok1"] = tok
    return segs, stats


def _seg_text(seg) -> str:
    out = []
    for t, p in seg["words"]:
        if p and out:
            out.append(t)
        else:
            out.append((" " if out else "") + t)
    return "".join(out)


def _render(segs, a, b, label):
    """Render segments [a, b] (inclusive). Returns text and {seg_index: (start, end)} char spans."""
    lines, spans, cur_spk, pos = [], {}, None, 0
    buf = ""
    for i in range(a, b + 1):
        s = segs[i]
        t = _seg_text(s)
        if s["spk"] != cur_spk:
            if cur_spk is not None:
                lines.append(buf)
                pos += len(buf) + 1
            buf = f"{label(s['spk'])}: "
            cur_spk = s["spk"]
            start = pos + len(buf)
            buf += t
        else:
            buf += " "
            start = pos + len(buf)
            buf += t
        spans[i] = (start, start + len(t))
    lines.append(buf)
    return "\n".join(lines), spans


# ----------------------------------------------------------------------------- units
def _snap(segs, lo_tok, hi_tok):
    """Smallest segment range covering word tokens [lo_tok, hi_tok)."""
    lo_tok, hi_tok = max(0, lo_tok), min(segs[-1]["tok1"], hi_tok)
    a = next(i for i, s in enumerate(segs) if s["tok1"] > lo_tok)
    b = max(i for i, s in enumerate(segs) if s["tok0"] < hi_tok)
    return a, b


def _meeting_units(root: Path, meeting: str, roles: dict, drops: collections.Counter, n0_tokens: dict):
    summ = _summary(root, meeting)
    links = _links(root, meeting)
    segs, sstats = _segments(root, meeting)
    if not segs:
        drops["meeting_without_transcript"] += 1
        return
    total_tok = segs[-1]["tok1"]
    da_pos = {s["da"]: i for i, s in enumerate(segs) if s["da"]}
    scenario = (meeting[:2] in ("ES", "IS", "TS"))

    def label(spk):
        return roles.get((meeting, spk)) or f"Speaker {spk}"

    role_flag = "speaker_labels:role" if all((meeting, s["spk"]) in roles for s in segs) else "speaker_labels:generic"
    base_flags = [role_flag, "tokens_joined", "nonword_events_dropped", "overlap_serialised_by_da_start"]

    for sec, list_type in LISTS:
        info = summ.get(sec)
        if info is None:
            drops[f"{list_type}:section_missing"] += 1
            continue
        all_item_segs = {}
        for sid, _ in info["items"]:
            all_item_segs[sid] = sorted({da_pos[d] for d in links.get(sid, []) if d in da_pos})
        linked_segs_any = {i for v in all_item_segs.values() for i in v}

        def make_unit(a, b, run, margin, n0_flag=None):
            text, spans = _render(segs, a, b, label)
            nw = C.words(text)
            gold, seen, flags = [], {}, list(base_flags)
            for sid, t in run:
                key = t.lower()
                ev = [{"text": text[spans[i][0]:spans[i][1]], "start": spans[i][0], "end": spans[i][1]}
                      for i in all_item_segs[sid]]
                if key in seen:
                    g = gold[seen[key]]
                    g["evidence"] += [e for e in ev if e not in g["evidence"]]
                    if "gold_dedup" not in flags:
                        flags.append("gold_dedup")
                    continue
                seen[key] = len(gold)
                gold.append({"text": t, "start": None, "end": None, "evidence": ev})
            if n0_flag:
                flags.append(n0_flag)
                if list_type == "action_items" and meeting in NA_SUSPECT:
                    flags.append(f"n0_suspect:{NA_SUSPECT[meeting][0]}")
            if margin is not None and margin < MARGINS[0]:
                flags.append("short_margin")
            if any(len(set(m.group(0).lower() for m in ASSIGNEE_RE.finditer(g["text"]))) >= 2 for g in gold):
                flags.append("gold_bundles_assignees")
            run_segs = {i for sid, _ in run for i in all_item_segs[sid]}
            cue_segs = assign_segs = 0
            if list_type == "action_items":
                free = [_seg_text(segs[i]) for i in range(a, b + 1) if i not in run_segs]
                cue_segs = sum(1 for t in free if CUE_RE.search(t))
                assign_segs = sum(1 for t in free if ASSIGN_RE.search(t))
                if cue_segs:
                    flags.append("maybe_missing_item:task_talk")
                if assign_segs:
                    flags.append("maybe_missing_item:assignment_talk")
            lo, hi = segs[a]["tok0"], segs[b]["tok1"]
            u = {
                "source_id": f"ami:{meeting}:{sec}:tok{lo}-{hi}",
                "group": meeting,
                "text": text,
                "n": len(gold),
                "gold_items": gold,
                "list_type": list_type,
                "item_type": "vague_theme",
                "flags": flags,
                "meta": {
                    "meeting": meeting,
                    "series_letter": meeting[-1],
                    "scenario": scenario,
                    "annotator": info["annotator"],
                    "item_ids": [sid for sid, _ in run],
                    "meeting_items_in_list": len(info["items"]),
                    "tok_range": [lo, hi],
                    "seg_range": [a, b],
                    "tokens": hi - lo,
                    "meeting_tokens": total_tok,
                    "rel_position": round((lo + hi) / 2 / total_tok, 4),
                    "rel_start": round(lo / total_tok, 4),
                    "rel_end": round(hi / total_tok, 4),
                    "margin_tokens": margin,
                    "n0_suspect_note": (NA_SUSPECT[meeting][1] if n0_flag and list_type == "action_items"
                                        and meeting in NA_SUSPECT else None),
                    "words": nw,
                    "task_talk_unlinked_segments": cue_segs if list_type == "action_items" else None,
                    "assignment_talk_unlinked_segments": assign_segs if list_type == "action_items" else None,
                    "meeting_uncovered_words": sstats["uncovered_words"],
                    "files": [f"abstractive/{meeting}.abssumm.xml", f"extractive/{meeting}.summlink.xml",
                              f"dialogueActs/{meeting}.*.dialog-act.xml", f"words/{meeting}.*.words.xml"],
                },
            }
            return u, nw

        # ---- n = 0 from annotator-NA meetings
        if info["na"]:
            hi, k = total_tok, 0
            while hi > 0:
                T = n0_tokens[list_type][k % len(n0_tokens[list_type])]
                k += 1
                lo = max(0, hi - T)
                if hi - lo < T // 2:
                    drops[f"{list_type}:n0_tail_too_short"] += 1
                    break
                a, b = _snap(segs, lo, hi)
                if segs[b]["tok1"] > hi and b > a:
                    b -= 1  # keep non-overlapping with the window after it
                u, nw = make_unit(a, b, [], None, "n0_certified_by:meeting_NA")
                if MIN_WORDS <= nw <= MAX_WORDS:
                    yield u
                else:
                    drops[f"{list_type}:n0_bad_length"] += 1
                hi = segs[a]["tok0"]
            continue
        if not info["items"]:
            drops[f"{list_type}:section_empty_without_NA"] += 1
            continue
        if any(not v for v in all_item_segs.values()):
            drops[f"{list_type}:meeting_has_unlinked_item"] += 1
            continue
        items = sorted(info["items"], key=lambda it: all_item_segs[it[0]][0])
        for i in range(len(items)):
            for j in range(i, len(items)):
                run = items[i:j + 1]
                if len(run) > MAX_N:
                    drops[f"{list_type}:run_n_gt_8"] += 1
                    continue
                other = {x for it in items[:i] + items[j + 1:] for x in all_item_segs[it[0]]}
                own = [x for it in run for x in all_item_segs[it[0]]]
                first_tok, last_tok = segs[min(own)]["tok0"], segs[max(own)]["tok1"]
                done, why = False, "too_long"
                for margin in MARGINS:
                    a, b = _snap(segs, first_tok - margin, last_tok + margin)
                    if any(x in other for x in range(a, b + 1)):
                        why = "other_item_inside"
                        continue
                    if segs[b]["tok1"] - segs[a]["tok0"] > MAXTOK:
                        why = "too_long"
                        continue
                    u, nw = make_unit(a, b, run, margin)
                    if nw > MAX_WORDS:
                        why = "too_long"
                        continue
                    if nw < MIN_WORDS:
                        why = "too_short"
                        continue
                    yield u
                    done = True
                    break
                if not done:
                    drops[f"{list_type}:run_{why}"] += 1


DROPS: collections.Counter = collections.Counter()


def units(cache: Path):
    root = fetch(cache)
    roles = _roles(root)
    meetings = sorted(os.path.basename(f).split(".")[0] for f in glob.glob(str(root / "abstractive" / "*.abssumm.xml")))
    DROPS.clear()
    n0_tokens = N0_TOKENS
    for m in meetings:
        for u in _meeting_units(root, m, roles, DROPS, n0_tokens):
            C.check_unit(u)
            yield u


# n=0 window sizes (word tokens), cycled per meeting from the END backwards so every NA meeting
# gives a wrap-up window. The cycle spans the 10th-90th percentile of the n>=1 windows of the
# same list (measured on this loader's own output, see REPORT.md), so length does not give n away.
N0_TOKENS = {"action_items": (250, 340, 300, 400, 280, 360),
             "decisions": (280, 420, 340, 520, 380, 460)}


# ----------------------------------------------------------------------------- main
def _summ(us):
    by = collections.defaultdict(list)
    for u in us:
        by[(u["list_type"], u["n"])].append(u)
    for (lt, n), lst in sorted(by.items()):
        mts = len({u["group"] for u in lst})
        late = sum(1 for u in lst if u["meta"]["rel_position"] >= 0.8)
        print(f"  {lt:13s} n={n}: units={len(lst):4d} meetings={mts:3d} "
              f"median_words={statistics.median(u['meta']['words'] for u in lst):6.1f} "
              f"median_tokens={statistics.median(u['meta']['tokens'] for u in lst):6.1f} "
              f"rel_pos>=0.8={late:3d} meetings_margin150={len({u['group'] for u in lst if u['meta']['margin_tokens'] in (None, 150)}):3d}")


if __name__ == "__main__":
    C.check_source(SOURCE)
    fetch(C.DEFAULT_CACHE)
    us = list(units(C.DEFAULT_CACHE))
    print("units:", len(us))
    print("n histogram:", dict(sorted(collections.Counter((u["list_type"], u["n"]) for u in us).items())))
    _summ(us)
    fl = collections.Counter()
    for u in us:
        for f in u["flags"]:
            fl[(u["list_type"], f)] += 1
    print("flags:")
    for k, v in sorted(fl.items()):
        print(f"  {k[0]:13s} {k[1]}: {v}")
    print("drops:", dict(sorted(DROPS.items())))
    picks = []
    for n in (0, 1, 2):
        picks.append(next(u for u in us if u["list_type"] == "action_items" and u["n"] == n))
    for u in picks:
        print(json.dumps(u, ensure_ascii=True))
