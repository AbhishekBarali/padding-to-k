#!/usr/bin/env python3
"""Build the requests and answer lists of the condition min_k_shown_fewer_ok (added 18 Oct, after the pilot).

    python data/build_fewer_ok.py          writes data/requests_fewer_ok.jsonl and
                                           data/reference_outputs_fewer_ok.jsonl (and the restricted
                                           answer lists into data/local/ when the review set is there)
    python data/build_fewer_ok.py check    rebuilds in memory and compares with the files on disk

The condition is min_k_shown with one plain line added after the base instruction that allows a shorter
list. Everything else is the min_k_shown request of the same document and k: the same schema (minItems k,
shown, not enforced), the same schema block, the same document. So the pair min_k_shown vs
min_k_shown_fewer_ok differs only in that line.

The line is a real-world wording from data/wordings.yaml (categories.escape.real_examples, ScrapeGraphAI
row 4580890): "If the source text genuinely contains fewer than three identifiable distinct features,
list all available ones." Changes: "the source text" -> "the document" (as build.py turns "this page" into
"this document"), "three" -> k, and the words "genuinely" and "identifiable distinct features" left out.
The noun is left out the way escape_2 leaves it out (the base instruction names the list one sentence
earlier, and "fewer than 1 action items" is not English); "genuinely" is left out because it asks the
model to make sure first, which is the "try harder" reading the condition must avoid. escape_2 ("If there
are fewer than {k}, return as many as possible.") is not used for the same reason: "as many as possible"
can read as an instruction to find more.

Nothing frozen is rewritten: the rows are derived from the min_k_shown rows of data/requests.jsonl, and
the answer lists from build.reference() for min_k_shown, relabelled.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build  # noqa: E402

CONDITION = "min_k_shown_fewer_ok"
WORDING_ID = "fewer_1"
WORDING = "If the document contains fewer than {k}, list all available ones."
BASED_ON = [4580890]
OUT_REQUESTS = HERE / "requests_fewer_ok.jsonl"
OUT_REFERENCE = HERE / "reference_outputs_fewer_ok.jsonl"
OUT_REFERENCE_LOCAL = HERE / "local" / "restricted_reference_outputs_fewer_ok.jsonl"


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def requests():
    rows = []
    for r in read_jsonl(HERE / "requests.jsonl"):
        if r["condition"] != "min_k_shown":
            continue
        list_type = r["schema_id"].split("|")[0]
        row = dict(r)
        row.update({
            "request_id": f"{r['doc_id']}|{CONDITION}|k{r['k']}|{WORDING_ID}",
            "condition": CONDITION,
            "wording_id": WORDING_ID,
            "instruction": r["instruction"] + " " + build.fill(WORDING, list_type, r["k"]),
            "in_pilot_run": False,
        })
        rows.append(row)           # schema_id, schema_block_id and enforce_schema stay min_k_shown's
    return rows


def references(docs, ks):
    out = []
    for d in docs:
        if d["split"] not in ("pilot", "full"):
            continue
        for k in ks:
            r = build.reference(d, "min_k_shown", k)
            r["condition"] = CONDITION
            out.append(r)
    return out


def dumps(rows):
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)


def main():
    check = sys.argv[1:] == ["check"]
    reqs = requests()
    ks = sorted({r["k"] for r in reqs})
    files = {OUT_REQUESTS: dumps(reqs), OUT_REFERENCE: dumps(references(read_jsonl(HERE / "documents.jsonl"), ks))}
    local = HERE / "local" / "restricted_documents.jsonl"
    if local.exists():
        files[OUT_REFERENCE_LOCAL] = dumps(references(read_jsonl(local), ks))
    bad = 0
    for path, text in files.items():
        if check:
            same = path.exists() and path.read_text(encoding="utf-8") == text
            bad += not same
            print(f"{path.relative_to(HERE)}: {'same' if same else 'DIFFERENT'}")
        else:
            path.write_text(text, encoding="utf-8", newline="\n")
            print(f"wrote {path.relative_to(HERE)}: {text.count(chr(10))} rows")
    if not check:
        print(f"{len(reqs)} requests on {len({r['doc_id'] for r in reqs})} documents, k = {ks}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
