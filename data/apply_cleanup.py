"""Apply the cleanup decisions (cleanup/decisions.jsonl) to the selected documents.

build.py selects documents exactly as before, then calls apply() here. Nothing in the source loaders
changes, and no document text is ever touched: a decision can only keep a document, change its answer
list, drop it, or leave it for the human check. Every change keeps the annotators' original list next to
the new one (gold_items_original, n_original) and every new item is marked origin="cleanup".

A decision is tied to the exact text and annotator list it was made on (text_sha256, gold_sha256). If a
rebuild produces a different text or list for that document, the build stops instead of applying the
decision to something nobody checked.

Review documents (not redistributable) are stored by character position plus a hash, never by text, so
this file and its outputs can be committed.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DECISIONS = HERE / "cleanup" / "decisions.jsonl"
STATUSES = ("ok", "fixed", "dropped", "needs_human")


def sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def gold_sha(gold) -> str:
    return sha(json.dumps([g["text"] for g in gold], ensure_ascii=False))


def load_decisions(path: Path = DECISIONS):
    out = {}
    if not path.exists():
        return out
    for ln, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        d = json.loads(line)
        if d["status"] not in STATUSES:
            raise ValueError(f"{path.name} line {ln}: bad status {d['status']!r}")
        key = (d["set"], d["source_id"])
        if key in out:
            raise ValueError(f"{path.name} line {ln}: second decision for {key}")
        out[key] = d
    return out


def _span(text, s, e, want_sha=None, want_text=None, what=""):
    got = text[s:e]
    if want_text is not None and got != want_text:
        raise ValueError(f"{what}: text[{s}:{e}] is {got!r}, decision says {want_text!r}")
    if want_sha is not None and sha(got) != want_sha:
        raise ValueError(f"{what}: text[{s}:{e}] does not match the stored hash")
    return got


def _item(doc, it, what):
    """Turn a stored item into a gold item for this document."""
    text = doc["text"]
    # meeting items, and quotations interrupted by a speech tag (the PDNC convention: the parts joined by a
    # space, each part an evidence span), carry evidence spans instead of one span
    if doc["item_type"] == "vague_theme" or "evidence" in it:
        ev = [{"text": _span(text, x["start"], x["end"], x.get("sha256"), x.get("text"), what),
               "start": x["start"], "end": x["end"]} for x in it["evidence"]]
        return {"text": it["text"], "start": None, "end": None, "evidence": ev, "origin": "cleanup"}
    t = _span(text, it["start"], it["end"], it.get("sha256"), it.get("text"), what)
    return {"text": t, "start": it["start"], "end": it["end"], "evidence": None, "origin": "cleanup"}


def new_gold(doc, dec):
    """The answer list after a decision's changes, in annotator order then additions."""
    old = doc["gold_items"]
    keep = {i: [dict(g, origin="annotator")] for i, g in enumerate(old, 1)}
    adds = []
    for c in dec.get("changes", []):
        what = f"{doc['doc_id']} {c['op']}"
        if c["op"] == "remove":
            keep.pop(c["index"])
        elif c["op"] == "replace":
            keep[c["index"]] = [dict(_item(doc, it, what), replaces=c["index"]) for it in c["with"]]
        elif c["op"] == "add":
            adds.append(_item(doc, c["item"], what))
        else:
            raise ValueError(f"{what}: unknown op")
    gold = [g for i in sorted(keep) for g in keep[i]] + adds
    seen = set()
    for g in gold:
        k = g["text"].strip().lower()
        if k in seen:
            raise ValueError(f"{doc['doc_id']}: duplicate item after cleanup: {g['text']!r}")
        seen.add(k)
    return gold


def _order(seed, doc_id):
    return sha(f"{seed}|{doc_id}")


def apply(docs, sets_cfg, seed, checked_by_default="", final=None):
    """Apply decisions in place, then trim each cell to `final` (see trim()). Returns a report dict for
    stats.json."""
    decisions = load_decisions()
    cfg = {c["set_id"]: c for c in sets_cfg}
    # candidate count per cell before any change: the number promotion refills to
    target = Counter((d["set"], d["split"], d["n"]) for d in docs if d["split"] != "reserve")
    used = set()
    for d in docs:
        dec = decisions.get((d["set"], d["source_id"]))
        d["n_original"], d["split_original"] = d["n"], d["split"]
        if dec is None:
            d["cleanup"] = {"status": "unchecked"}
            continue
        used.add((d["set"], d["source_id"]))
        if dec["text_sha256"] != sha(d["text"]) or dec["gold_sha256"] != gold_sha(d["gold_items"]):
            raise ValueError(f"{d['doc_id']}: decision was made on a different text or annotator list; "
                             f"re-check it and update cleanup/decisions.jsonl")
        info = {k: dec[k] for k in ("status", "reason", "rules", "checked_by") if k in dec}
        if dec.get("question"):
            info["question"] = dec["question"]
        if dec.get("ruling"):
            info["ruling"] = dec["ruling"]     # an open question the authors settled
        if dec["status"] == "fixed":
            gold = new_gold(d, dec)
            d["gold_items_original"] = d["gold_items"]
            d["gold_items"], d["n"] = gold, len(gold)
            info["changes"] = dec["changes"]
        elif dec["status"] == "needs_human" and dec.get("changes"):
            info["proposed_changes"] = dec["changes"]
            info["proposed_gold"] = [g["text"] for g in new_gold(d, dec)]
        d["cleanup"] = info
        if dec["status"] == "dropped":
            d["split"] = "dropped"
            continue
        # a new n can move a document to another cell, or out of the study's range
        c = cfg[d["set"]]
        if d["n"] not in set(c["n_main"]) | set(c["n_arm"]):
            d["split"] = "dropped"
            d["cleanup"]["status"] = "dropped"
            d["cleanup"]["dropped_because"] = f"corrected n = {d['n']} is outside this set's range"
            continue
        if c["role"] == "pilot":
            if d["split"] == "pilot" and d["n"] not in (0, 1, 2):
                d["split"] = "full"
            elif d["split"] == "full" and d["n"] == 2:
                d["split"] = "pilot"      # as in the selection: every n = 2 document of a pilot set is pilot
    orphans = sorted(set(decisions) - used)
    if orphans:
        raise ValueError(f"{len(orphans)} decisions match no selected document, e.g. {orphans[0]}; "
                         f"the selection changed, re-check before building")

    # refill each cell to its candidate count from checked, clean spares with the same (new) n
    clean = lambda d: d["cleanup"]["status"] in ("ok", "fixed")
    have = Counter((d["set"], d["split"], d["n"]) for d in docs if clean(d) and d["split"] in ("pilot", "full"))
    spares = defaultdict(list)
    for d in docs:
        if d["split"] == "reserve" and clean(d):
            spares[(d["set"], d["n"])].append(d)
    for v in spares.values():
        v.sort(key=lambda d: _order(seed, d["doc_id"]))
    promoted = []
    for (s, split, n), want in sorted(target.items(), key=lambda kv: (kv[0][0], kv[0][1] != "pilot", kv[0][2])):
        while have[(s, split, n)] < want and spares[(s, n)]:
            d = spares[(s, n)].pop(0)
            d["split"] = split
            d["cleanup"]["promoted"] = f"reserve -> {split}, refilling {s} {split} n = {n}"
            have[(s, split, n)] += 1
            promoted.append(d["doc_id"])

    trimmed = trim(docs, sets_cfg, seed, final) if final else {}

    cells = []
    for s in [c["set_id"] for c in sets_cfg]:
        for n in sorted(set(cfg[s]["n_main"]) | set(cfg[s]["n_arm"])):
            row = {"set": s, "n": n}
            for split in ("pilot", "full", "reserve"):
                sub = [d for d in docs if d["set"] == s and d["split"] == split and d["n"] == n]
                row[split] = sum(clean(d) for d in sub)
                row[split + "_needs_human"] = sum(d["cleanup"]["status"] == "needs_human" for d in sub)
            row["candidates_before"] = target[(s, "pilot", n)] + target[(s, "full", n)]
            cells.append(row)
    by_set = {s: dict(Counter(d["cleanup"]["status"] for d in docs if d["set"] == s)) for s in cfg}
    moves = Counter((d["set"], d["n_original"], d["n"]) for d in docs
                    if d["cleanup"]["status"] == "fixed" and d["n"] != d["n_original"])
    return {"decisions": len(decisions), "status_by_set": by_set, "promoted": promoted,
            "n_moves": [{"set": s, "from": a, "to": b, "docs": k} for (s, a, b), k in sorted(moves.items())],
            "final_targets": final, "trimmed": trimmed, "cells_clean": cells}


# ---------------------------------------------------------------------------------------------
# Trimming to the final numbers. The cells are over-sampled so checkers could drop documents without a
# rebuild. Once the cleanup and the authors' check are done, each cell keeps its final number, chosen so
# that the lengths in every cell of a set follow the same spread: length should not give away n.
def _quantiles(values, m):
    """m evenly spaced points (the middles of m equal slices) of the distribution of values."""
    v = sorted(values)
    out = []
    for i in range(m):
        p = (i + 0.5) / m * (len(v) - 1)
        lo = math.floor(p)
        hi = min(lo + 1, len(v) - 1)
        out.append(v[lo] + (v[hi] - v[lo]) * (p - lo))
    return out


def _pick(items, targets, key):
    """Choose len(targets) of items so that, both sorted, each chosen item is as close to its target as
    possible (least total distance). Exact, by dynamic programming over the two sorted lists. `items` must
    already be in a fixed order (the seeded order), which also settles ties."""
    items = sorted(items, key=key)
    t = sorted(targets)
    k, m = len(items), len(t)
    if m >= k:
        return list(items)
    inf = float("inf")
    cost = [[0.0] + [inf] * m for _ in range(k + 1)]
    take = [[False] * (m + 1) for _ in range(k + 1)]
    for i in range(1, k + 1):
        x = key(items[i - 1])
        for j in range(1, min(i, m) + 1):
            use = cost[i - 1][j - 1] + abs(x - t[j - 1])
            if use <= cost[i - 1][j]:
                cost[i][j], take[i][j] = use, True
            else:
                cost[i][j] = cost[i - 1][j]
    out, i, j = [], k, m
    while j > 0:
        if take[i][j]:
            out.append(items[i - 1])
            j -= 1
        i -= 1
    return out


def trim(docs, sets_cfg, seed, final):
    """Trim every cell to `final` = {"pilot": per n, "full": per n incl. pilot, "arm_per_set": total}.

    - Pilot sets, pilot documents: keep `pilot` per n (only from documents that were already pilot,
      because those are the ones the authors checked in full).
    - Every set, n in n_main: keep `full` per n in pilot + full. In pilot sets the kept pilot documents
      count towards it and the rest is chosen from full documents and the pilot ones not kept.
    - The k < n arm: keep `arm_per_set` in all, spread as evenly over n as the documents allow.
    Cells already at or below their number keep everything (they are reported as short elsewhere).
    A trimmed document stays clean and checked: it becomes a spare (split "reserve") and records where it
    came from in cleanup.trimmed / cleanup.trimmed_from, so setting `final` to None brings it back."""
    cfg = {c["set_id"]: c for c in sets_cfg}
    clean = lambda d: d["cleanup"]["status"] in ("ok", "fixed")
    val = lambda d: math.log(d["words"] + 1)
    before = {d["doc_id"]: d["split"] for d in docs}
    ordered = sorted(docs, key=lambda d: _order(seed, d["doc_id"]))
    for s, c in cfg.items():
        inset = [d for d in ordered if d["set"] == s and clean(d)]
        active = lambda d: d["split"] in ("pilot", "full")
        if c["role"] == "pilot":
            pil = [d for d in inset if d["split"] == "pilot"]
            ref = [val(d) for d in pil]
            for n in sorted({d["n"] for d in pil}):
                cell = [d for d in pil if d["n"] == n]
                keep = {d["doc_id"] for d in _pick(cell, _quantiles(ref, final["pilot"]), val)}
                for d in cell:
                    if d["doc_id"] not in keep:
                        d["split"] = "full"         # still a candidate for the full study below
        ref = [val(d) for d in inset if active(d) and d["n"] in c["n_main"]]
        for n in c["n_main"]:
            cell = [d for d in inset if active(d) and d["n"] == n]
            fixed = [d for d in cell if d["split"] == "pilot"]
            free = [d for d in cell if d["split"] == "full"]
            if len(cell) <= final["full"]:
                continue
            targets = _quantiles(ref, final["full"])
            if fixed:   # the slots the kept pilot documents already fill, the rest go to the free ones
                slots = list(range(len(targets)))
                taken = set(_pick(slots, [val(d) for d in fixed], key=lambda i: targets[i]))
                targets = [targets[i] for i in slots if i not in taken]
            keep = {d["doc_id"] for d in _pick(free, targets, val)}
            for d in free:
                if d["doc_id"] not in keep:
                    d["split"] = "reserve"
        arm = {n: [d for d in inset if active(d) and d["n"] == n] for n in c["n_arm"]}
        if sum(map(len, arm.values())) > final["arm_per_set"]:
            share = {n: 0 for n in arm}
            for _ in range(final["arm_per_set"]):
                n = min((n for n in sorted(arm) if share[n] < len(arm[n])), key=lambda n: (share[n], n))
                share[n] += 1
            ref = [val(d) for v in arm.values() for d in v]
            for n, cell in arm.items():
                keep = {d["doc_id"] for d in _pick(cell, _quantiles(ref, share[n]), val)}
                for d in cell:
                    if d["doc_id"] not in keep:
                        d["split"] = "reserve"
    out = Counter()
    for d in docs:
        if d["split"] != before[d["doc_id"]]:
            d["cleanup"]["trimmed_from"] = before[d["doc_id"]]
            d["cleanup"]["trimmed"] = (f"{before[d['doc_id']]} -> {d['split']}: over the final number for "
                                       f"{d['set']} n = {d['n']}; the kept documents match the set's lengths best")
            out[f"{d['set']} {before[d['doc_id']]} -> {d['split']}"] += 1
    return dict(sorted(out.items()))


# ---------------------------------------------------------------------------------------------
def _list(gold):
    return "\n".join(f"{i}. {g['text']}" for i, g in enumerate(gold, 1)) or "(none)"


def change_text(d, show_text=True):
    """One plain line per change, e.g. 'removed 1: "..."' or 'added: "..."'."""
    info = d["cleanup"]
    ch = info.get("changes") or info.get("proposed_changes") or []
    orig = d["gold_items_original"] if "gold_items_original" in d else d["gold_items"]
    q = (lambda t: f' "{t}"') if show_text else (lambda t: "")
    out = []
    for c in ch:
        if c["op"] == "remove":
            out.append(f"removed {c['index']}:" + q(orig[c["index"] - 1]["text"]))
        elif c["op"] == "replace":
            parts = [_render_item(d, it, show_text) for it in c["with"]]
            out.append(f"{'split' if len(parts) > 1 else 'replaced'} {c['index']}:" + q(orig[c["index"] - 1]["text"])
                       + " -> " + " | ".join(parts))
        else:
            out.append("added: " + _render_item(d, c["item"], show_text))
    return "; ".join(out)


def _render_item(d, it, show_text):
    if "evidence" in it:
        return f'"{it["text"]}"'
    if not show_text:
        return f"chars {it['start']}-{it['end']}"
    return f'"{d["text"][it["start"]:it["end"]]}"'


CHANGE_COLS = ["doc_id", "set", "status", "split_before", "split_after", "n_before", "n_after", "change",
               "reason", "rules", "question", "authors_ruling", "promoted", "trimmed"]


def _change_row(d, show_text):
    i = d["cleanup"]
    return [d["doc_id"], d["set"], i["status"], d["split_original"], d["split"], d["n_original"], d["n"],
            change_text(d, show_text), i.get("dropped_because") or i.get("reason", ""), " ".join(i.get("rules", [])),
            i.get("question", ""), i.get("ruling", ""), i.get("promoted", ""), i.get("trimmed", "")]


REVIEW_COLS = ["order", "doc_id", "why_in_sheet", "set", "split", "status", "n_before", "n_after", "text",
               "annotator_list", "current_list", "change", "reason", "question", "authors_ruling",
               "reviewer", "agree_y_n", "keep_y_n", "right_list_if_not", "notes"]


def review_queue(docs, seed):
    """Pilot documents, every open question, and a fixed-seed sample of fixes and drops."""
    rows, seen = [], set()

    def add(d, why):
        if d["doc_id"] not in seen:
            seen.add(d["doc_id"])
            rows.append((why, d))
    by = sorted(docs, key=lambda d: (d["set"], _order(seed, d["doc_id"])))
    # the queue is the one the authors checked: pilot as it stood before trimming, and the open questions
    # stay open questions after the authors settled them
    pilot = lambda d: "pilot" in (d["split"], d.get("split_original"), d["cleanup"].get("trimmed_from"))
    opened = lambda d: d["cleanup"]["status"] == "needs_human" or "ruling" in d["cleanup"]
    settled = lambda d: ", settled" if "ruling" in d["cleanup"] else ""
    for d in by:
        if pilot(d) and opened(d):
            add(d, "pilot, open question" + settled(d))
    for d in by:
        if pilot(d):
            st = d["cleanup"]["status"]
            moved = d["split"] not in ("pilot", "dropped")
            add(d, "pilot" + (f", {st}" if st in ("fixed", "dropped") else "") + (f", moved to {d['split']}" if moved else ""))
    for d in by:
        if opened(d):
            add(d, "open question" + settled(d))
    for status, share, least in (("fixed", 0.2, 4), ("dropped", 0.05, 2)):
        for s in sorted({d["set"] for d in docs}):
            pool = [d for d in by if d["set"] == s and d["cleanup"]["status"] == status and d["doc_id"] not in seen]
            for d in pool[:max(least, round(share * len(pool)))]:
                add(d, f"sample of {status}")
    return rows


def write_outputs(docs, report, here, local_dir, seed):
    out_dir = here / "cleanup"
    out_dir.mkdir(exist_ok=True)
    changed = [d for d in docs if d["cleanup"]["status"] in ("fixed", "dropped", "needs_human")
               or d["cleanup"].get("promoted") or d["cleanup"].get("trimmed")]
    for path, subset, show in [(out_dir / "changes.csv", [d for d in changed if d["redistributable"]], True),
                               (out_dir / "changes_reviews_no_text.csv",
                                [d for d in changed if not d["redistributable"]], False),
                               (local_dir / "changes_reviews.csv", [d for d in changed if not d["redistributable"]], True)]:
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(CHANGE_COLS)
            for d in subset:
                w.writerow(_change_row(d, show))
    queue = review_queue(docs, seed)
    for path, keep in [(out_dir / "review_sheet.csv", True), (local_dir / "review_sheet_reviews.csv", False)]:
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(REVIEW_COLS)
            k = 0
            for why, d in queue:
                if d["redistributable"] != keep:
                    continue
                k += 1
                i = d["cleanup"]
                w.writerow([k, d["doc_id"], why, d["set"], d["split"], i["status"], d["n_original"], d["n"],
                            d["text"], _list(d["gold_items_original"] if "gold_items_original" in d else d["gold_items"]),
                            _list(d["gold_items"]), change_text(d), i.get("dropped_because") or i.get("reason", ""),
                            i.get("question", ""), i.get("ruling", ""), "", "", "", "", ""])
    _write_review_md(queue, out_dir, local_dir)
    _write_report(docs, report, out_dir, queue)


def _write_review_md(queue, out_dir, local_dir):
    """The same queue as readable pages: one per part, so each renders on GitHub."""
    parts = defaultdict(list)
    for why, d in queue:
        if not d["redistributable"]:
            parts["local"].append((why, d))
        elif why.startswith("pilot"):
            parts[f"pilot_{d['set']}"].append((why, d))
        else:
            parts["other"].append((why, d))
    for name, rows in parts.items():
        path = (local_dir / "review_reviews.md") if name == "local" else (out_dir / f"review_{name}.md")
        lines = [f"# Review queue: {name.replace('_', ' ')} ({len(rows)} documents)\n\n",
                 "Same rows and order as `review_sheet.csv`; write your answers there. Items added or split by the "
                 "cleanup are marked **(cleanup)**.\n"]
        for why, d in rows:
            i = d["cleanup"]
            lines.append(f"\n---\n\n### {d['doc_id']} ({d['set']}, {d['split']}, n {d['n_original']} -> {d['n']}) "
                         f"- {why}\n")
            why_text = i.get("dropped_because") or i.get("reason", "")
            if i["status"] == "needs_human" and why_text:
                why_text = "Proposed: " + why_text
            lines.append(f"**Status:** {i['status']}" + (f". {why_text}" if why_text else "") + "\n")
            if i.get("question"):
                lines.append(f"\n**Question for you:** {i['question']}\n")
            if i.get("ruling"):
                lines.append(f"\n**Authors' ruling:** {i['ruling']}\n")
            if i.get("trimmed"):
                lines.append(f"\n**Trimmed:** {i['trimmed']}\n")
            lines.append("\n```text\n" + d["text"] + "\n```\n")
            orig = d.get("gold_items_original")
            if orig is not None:
                lines.append("\nAnnotator list:\n\n" + "\n".join(f"{k}. {g['text']}" for k, g in enumerate(orig, 1))
                             + ("\n" if orig else "(none)\n"))
                lines.append("\nList now:\n\n" + "\n".join(
                    f"{k}. {g['text']}" + (" **(cleanup)**" if g.get("origin") == "cleanup" else "")
                    for k, g in enumerate(d["gold_items"], 1)) + ("\n" if d["gold_items"] else "(none)\n"))
            else:
                lines.append("\nList:\n\n" + ("\n".join(f"{k}. {g['text']}" for k, g in enumerate(d["gold_items"], 1))
                                              or "(none)") + "\n")
                if i.get("proposed_gold") is not None:
                    lines.append("\nProposed instead:\n\n" + ("\n".join(f"{k}. {t}" for k, t in
                                                                     enumerate(i["proposed_gold"], 1)) or "(none)") + "\n")
        path.write_text("".join(lines), encoding="utf-8")


def _write_report(docs, report, out_dir, queue):
    L = ["# Cleanup report (generated by build.py; do not edit)\n",
         "\nWhat the cleanup pass decided, per set. `ok` = list was right; `fixed` = list changed; `dropped` = "
         "document removed from the study; `needs_human` = a judgment call left for you.\n",
         "\n| Set | checked | ok | fixed | dropped | needs_human | spares promoted |\n|---|---|---|---|---|---|---|\n"]
    prom = Counter(d["set"] for d in docs if d["cleanup"].get("promoted"))
    for s, c in report["status_by_set"].items():
        L.append(f"| {s} | {sum(v for k, v in c.items() if k != 'unchecked')} | {c.get('ok', 0)} | {c.get('fixed', 0)} | "
                 f"{c.get('dropped', 0)} | {c.get('needs_human', 0)} | {prom[s]} |\n")
    settled = [d for d in docs if "ruling" in d["cleanup"]]
    if settled:
        L.append(f"\nOpen questions settled by the authors: {len(settled)} ("
                 + ", ".join(f"{d['doc_id']} {d['cleanup']['status']}" for d in sorted(settled, key=lambda d: d["doc_id"]))
                 + "). Their rulings are in `decisions.jsonl` (`ruling`) and in the review sheet.\n")
    fin = report.get("final_targets")
    L.append("\n## Documents per cell\n\nClean = ok or fixed. The study's targets (data/README.md "
             "section 4): pilot 10 per n (meetings, emails, n = 0-2); full 15 per n for n = 0-3 (pilot counts "
             "towards it); about 3 per n and about 10 per set for n = 4-6 (the arm totals are in the next table). "
             "`short` marks a cell below target. "
             + ("Cells are trimmed to these numbers (`FINAL_TARGETS` in build.py); trimmed documents are counted "
                "in clean spares left.\n\n" if fin else "Cells are not trimmed yet (`FINAL_TARGETS` is off).\n\n")
             + "| Set | n | pilot clean | full clean | pilot + full clean | target | open questions | clean spares left | "
             "candidates before |\n|---|---|---|---|---|---|---|---|---|\n")
    for r in report["cells_clean"]:
        tgt = 15 if r["n"] <= 3 else 3
        if r["candidates_before"] == 0 and r["pilot"] + r["full"] + r["reserve"] == 0:
            continue
        tot = r["pilot"] + r["full"]
        pil = r["pilot"]
        short = []
        if tot < tgt and r["n"] <= 3:
            short.append("short")
        if r["set"] in ("meetings", "emails") and r["n"] <= 2 and pil < 10:
            short.append("pilot short")
        L.append(f"| {r['set']} | {r['n']} | {pil} | {r['full']} | {tot} | {tgt}{' (pilot 10)' if r['set'] in ('meetings', 'emails') and r['n'] <= 2 else ''} | "
                 f"{r['pilot_needs_human'] + r['full_needs_human']} | {r['reserve']} | {r['candidates_before']} "
                 f"{'**' + ', '.join(short) + '**' if short else ''}|\n")
    arm = defaultdict(lambda: [0, 0])
    for r in report["cells_clean"]:
        if r["n"] >= 4 and (r["candidates_before"] or r["pilot"] + r["full"]):
            arm[r["set"]][0] += r["pilot"] + r["full"]
            arm[r["set"]][1] += r["candidates_before"]
    L.append("\n### The 4-6 arm (asked for fewer than exist), per set\n\n| Set | clean documents n = 4-6 | target | "
             "candidates before |\n|---|---|---|---|\n")
    for s_, (have_, before) in arm.items():
        L.append(f"| {s_} | {have_} | about 10 | {before} {'**short**' if have_ < 10 else ''}|\n")
    if report.get("trimmed"):
        L.append("\n## Trimmed to the final numbers\n\nEach over-full cell kept the documents whose lengths best "
                 "match the spread of lengths across the whole set (`trim()` in apply_cleanup.py), so that length "
                 "says as little as possible about n. Pilot documents were kept only from documents that were already "
                 "pilot. Trimmed documents stay clean and checked, as spares.\n\n| Set | moved | documents |\n|---|---|---|\n")
        for k_, v_ in report["trimmed"].items():
            s_, mv = k_.split(" ", 1)
            L.append(f"| {s_} | {mv} | {v_} |\n")
    if report["n_moves"]:
        L.append("\n## Documents whose count changed\n\n| Set | n before | n after | documents |\n|---|---|---|---|\n")
        for m in report["n_moves"]:
            L.append(f"| {m['set']} | {m['from']} | {m['to']} | {m['docs']} |\n")
    items = Counter()
    for d in docs:
        for c in d["cleanup"].get("changes", []):
            items[(d["set"], "split" if c["op"] == "replace" and len(c["with"]) > 1 else c["op"])] += 1
    L.append("\n## Item changes in fixed documents\n\n| Set | removed | replaced (span fixed) | split | added |\n"
             "|---|---|---|---|---|\n")
    for s in report["status_by_set"]:
        L.append(f"| {s} | {items[(s, 'remove')]} | {items[(s, 'replace')]} | {items[(s, 'split')]} | {items[(s, 'add')]} |\n")
    rules = Counter(r for d in docs if d["cleanup"]["status"] in ("fixed", "dropped", "needs_human")
                    for r in d["cleanup"].get("rules", []))
    L.append("\n## Rules cited (COUNTING_RULES.md)\n\n" + ", ".join(f"{r}: {k}" for r, k in sorted(rules.items())) + "\n")
    # second opinion: how this pass compares with the first AI pre-check (committed notes only; the 8 notes
    # on reviews live in local/ and are left out so the report is the same on every clone)
    pre_path = out_dir.parent / "ai_precheck.jsonl"
    if pre_path.exists():
        by_key = {(d["set"], d["source_id"]): d for d in docs}
        t = Counter()
        for line in pre_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                d = by_key.get((r["set"], r["source_id"]))
                if d is not None:
                    t[(r["verdict"], d["cleanup"]["status"])] += 1
        cols = ["ok", "fixed", "dropped", "needs_human"]
        L.append("\n## Compared with the first AI pre-check\n\nRows: what the pre-check said (pilot documents and a 10% "
                 "sample; its notes were read only after this pass had decided). Columns: what this pass decided.\n\n"
                 "| Pre-check said | " + " | ".join(cols) + " |\n|---|" + "---|" * len(cols) + "\n")
        for v in ["ok", "missing_item", "wrong_item", "ambiguous"]:
            L.append(f"| {v} | " + " | ".join(str(t[(v, c)]) for c in cols) + " |\n")
    whys = Counter(w for w, _ in queue)
    L.append("\n## Review queue (review_sheet.csv)\n\n" + "\n".join(f"- {w}: {k}" for w, k in whys.items()) + "\n")
    (out_dir / "REPORT.md").write_text("".join(L), encoding="utf-8")


# ---------------------------------------------------------------------------------------------
def check(docs, here):
    """Problems with the cleanup state of the built files (used by build.py check)."""
    problems = []
    for d in docs:
        st = d.get("cleanup", {}).get("status")
        if st is None:
            problems.append(f"{d['doc_id']}: no cleanup status (rebuild with build.py)")
            continue
        if st == "unchecked":
            problems.append(f"{d['doc_id']}: never checked by the cleanup pass")
        if (st == "dropped") != (d["split"] == "dropped"):
            problems.append(f"{d['doc_id']}: status {st} but split {d['split']}")
        if st == "fixed":
            if "gold_items_original" not in d:
                problems.append(f"{d['doc_id']}: fixed but the annotator list is missing")
            if not any(g.get("origin") == "cleanup" for g in d["gold_items"]) and len(d["gold_items"]) == len(
                    d["gold_items_original"]):
                problems.append(f"{d['doc_id']}: fixed but nothing changed")
        if d["n"] != len(d["gold_items"]):
            problems.append(f"{d['doc_id']}: n does not match the list")
    # review text must never reach a committed file
    restricted = [d for d in docs if not d["redistributable"]]
    committed = [p for p in (here / "cleanup").glob("*") if p.is_file()]
    committed += [here / f for f in ("documents.jsonl", "verify_sheet.csv", "reference_outputs.jsonl", "stats.json")]
    blobs = {p.name: p.read_text(encoding="utf-8") for p in committed if p.exists()}
    for d in restricted:
        t = d["text"]
        shingles = [t[i:i + 40] for i in range(0, max(1, len(t) - 40), 25)]
        for name, blob in blobs.items():
            if any(s in blob for s in shingles):
                problems.append(f"{d['doc_id']}: review text found in {name}")
                break
    return problems
