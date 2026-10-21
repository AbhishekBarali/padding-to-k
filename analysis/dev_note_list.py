#!/usr/bin/env python3
"""dev_note_list.py: possible shortfall notes in the dev-set outputs, listed for the authors (RUN-PLAN 5.1).

    python analysis/dev_note_list.py runs/<dev run> [runs/<dev run> ...] [--out analysis/dev/note_candidates.md]

Lists every output entry not copied from its document that is short (at most --max-words words, default 4) or contains "no", "none",
"not", "only", "other", "additional" or "found", across all conditions, with how often it appears and
whether the current placeholder rules (harness/common.py, is_placeholder) already treat it as a note.
The authors read the entries the rules count as items and add any missed note to the placeholder rules
before the freeze. Dev outputs only (reserve documents, never in the study). Outputs on the review set
(raw_restricted.jsonl) quote review text, so they never go into the file: --show-restricted prints them.
"""
import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))
import common  # noqa: E402

KEYWORDS = re.compile(r"\b(no|none|not|only|other|additional|found)\b", re.I)


def entries(run_dir, restricted, docs, prompts):
    path = Path(run_dir) / ("raw_restricted.jsonl" if restricted else "raw.jsonl")
    if not path.exists():
        return
    for r in common.read_jsonl(path):
        if r.get("status") != "ok":
            continue
        items = common.parse_output(r.get("content"), common.field_of(r, prompts))["items"] or []
        for it in items:
            if isinstance(it, str):
                yield r, it, docs[r["doc_id"]]["text"]


def collect(runs, restricted, docs, prompts, max_words):
    rows, total = defaultdict(lambda: {"times": 0, "note": 0, "in_doc": 0, "cond": Counter(),
                                       "sets": Counter(), "models": set(), "text": None}), 0
    for run in runs:
        for r, it, text in entries(run, restricted, docs, prompts):
            total += 1
            if len(common.core(it).split()) > max_words and not KEYWORDS.search(it):
                continue
            row = rows[common.normalise(it)]
            row["text"] = row["text"] or it.strip()
            row["times"] += 1
            row["note"] += common.is_placeholder(it, doc_text=text)
            row["in_doc"] += common.in_document(it, text)
            row["cond"][r["condition"]] += 1
            row["sets"][r["set"]] += 1
            row["models"].add(r["model_key"])
    return rows, total


def cell(s, n=110):
    s = s.replace("|", "/").replace("\n", " ")
    return s if len(s) <= n else s[:n - 3] + "..."


def table(rows, keys):
    out = ["| entry | times | rules say note | copied from the document | conditions | sets | models |",
           "|---|---|---|---|---|---|---|"]
    for k in keys:
        r = rows[k]
        out.append(f"| {cell(r['text'])} | {r['times']} | {r['note']} | {r['in_doc']} | "
                   f"{', '.join(f'{c} {v}' for c, v in r['cond'].most_common())} | "
                   f"{', '.join(f'{c} {v}' for c, v in r['sets'].most_common())} | {', '.join(sorted(r['models']))} |")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--out", default=str(ROOT / "analysis" / "dev" / "note_candidates.md"))
    ap.add_argument("--max-words", type=int, default=4)
    ap.add_argument("--show-restricted", action="store_true", help="print review-set entries to the screen only")
    args = ap.parse_args()
    docs, prompts = common.load_documents(), common.load_prompts()
    if args.show_restricted:
        rows, total = collect(args.runs, True, docs, prompts, args.max_words)
        print("\n".join(table(rows, sorted(rows, key=lambda k: (-(rows[k]["times"] - rows[k]["note"]), k)))))
        return
    rows, total = collect(args.runs, False, docs, prompts, args.max_words)
    copied = [k for k in rows if rows[k]["in_doc"] == rows[k]["times"]]      # never a note, by rule
    items = sorted((k for k in rows if rows[k]["note"] < rows[k]["times"] and k not in set(copied)),
                   key=lambda k: (-rows[k]["times"], k))
    worded = [k for k in items if KEYWORDS.search(rows[k]["text"])]
    short = [k for k in items if not KEYWORDS.search(rows[k]["text"])]
    notes = sorted((k for k in rows if rows[k]["note"] == rows[k]["times"]), key=lambda k: (-rows[k]["times"], k))
    runs = [json.loads((Path(r) / "manifest.json").read_text())["run_id"] for r in args.runs]
    lines = ["# Possible shortfall notes in the dev-set outputs", "",
             f"Runs: {', '.join(runs)}. Entries parsed: {total} (review set left out: it stays local).",
             f"Listed: entries of at most {args.max_words} words, or with no / none / not / only / other / "
             "additional / found; same text after normalising counted together.", "",
             f"Left out: {len(copied)} distinct entries copied word for word from their document "
             f"({sum(rows[k]['times'] for k in copied)} times), since the rules never treat copied text as a note.", "",
             f"## Not in the document, counted as items by the current rules: {len(items)} distinct entries", "",
             "Read these. Any that is a note about a shortfall rather than an item of the asked kind should be "
             "added to the placeholder rules (harness/common.py) before the freeze. \"rules say note\" counts the "
             "times the rules already treat it as a note (an entry copied from the document never is).", "",
             f"### With no / none / not / only / other / additional / found: {len(worded)} (read these first)", "",
             *table(rows, worded), "",
             f"### Short, without those words: {len(short)}", "", *table(rows, short), "",
             f"## Already treated as notes: {len(notes)} distinct entries", "", *table(rows, notes), ""]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out}: {len(items)} entries counted as items, {len(notes)} already notes, from {total} entries")


if __name__ == "__main__":
    main()
