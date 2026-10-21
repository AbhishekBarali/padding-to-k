#!/usr/bin/env python3
"""blind_rule3.py: pilot stop rule 3 as registered (preregistration/protocol.md, section 7, rule 3).

    python analysis/blind_rule3.py

Rule 3 is judged on 40 documents under the final definitions: round 1's 15 documents of the three sets
whose definitions did not change (novel quotes, receipts, Wikipedia people), plus round 2's 25. Each author
must match the answer list's count on at least 85% of them, and the authors' AC1 must be at least 0.80.
The share marked unclear by either author is reported, not tested (DECISIONS.md, 15 Oct).

Inputs: the frozen round-1 sheets in data/blind/ and the filled round-2 sheets in analysis/blind/ (kept
outside data/ so the frozen blank round-2 sheets stay as hashed in preregistration/manifest.sha256).
Writes analysis/blind/adjudicate_round2.csv: every round-2 document where a count differs from the
answer list or either author marked it unclear, with the answer list next to both counts.
"""
import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "data"))
from blind_check import cohen, gwet_ac1, load_docs  # noqa: E402

CHANGED = {"meetings", "emails", "job_posts", "job_posts_knowledge", "clinical"}
SHEETS = {
    1: (ROOT / "data/blind/blind_sheet_fresh_A.csv", ROOT / "data/blind/blind_sheet_fresh_B.csv"),
    2: (ROOT / "analysis/blind/blind_sheet_round2_A_filled.csv", ROOT / "analysis/blind/blind_sheet_round2_B_filled.csv"),
}


def read(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return {r["doc_id"]: r for r in csv.DictReader(f)}


def unclear(row):
    return row.get("unclear_y_n", "").strip().lower().startswith("y")


def main():
    docs = {d["doc_id"]: d for d in load_docs()}
    rows = []  # (round, doc_id, set, n_list, row_A, row_B)
    for rnd, (pa, pb) in SHEETS.items():
        a, b = read(pa), read(pb)
        if set(a) != set(b):
            raise SystemExit(f"round {rnd}: the two sheets hold different documents")
        for i in a:
            if rnd == 1 and a[i]["set"] in CHANGED:
                continue
            for r in (a[i], b[i]):
                if not r["n_found"].strip():
                    raise SystemExit(f"round {rnd}, {i}: n_found is empty")
            rows.append((rnd, i, a[i]["set"], docs[i]["n"], a[i], b[i]))

    nA = lambda r: int(r[4]["n_found"])
    nB = lambda r: int(r[5]["n_found"])
    N = len(rows)
    a_ok = sum(nA(r) == r[3] for r in rows)
    b_ok = sum(nB(r) == r[3] for r in rows)
    pairs = [(nA(r), nB(r)) for r in rows]
    ac1 = gwet_ac1(pairs)
    n_unclear = sum(unclear(r[4]) or unclear(r[5]) for r in rows)
    print(f"{N} documents ({sum(r[0] == 1 for r in rows)} from round 1, {sum(r[0] == 2 for r in rows)} from round 2)")
    print(f"A matches the answer list on {a_ok}/{N} ({100 * a_ok / N:.1f}%), B on {b_ok}/{N} ({100 * b_ok / N:.1f}%); need 85% each")
    print(f"A and B give the same count on {sum(x == y for x, y in pairs)}/{N}; AC1 {ac1} (need 0.80), kappa {cohen(pairs)}")
    print(f"marked unclear by either author: {n_unclear}/{N} ({100 * n_unclear / N:.1f}%), reported only")
    ok = min(a_ok, b_ok) / N >= 0.85 and (ac1 or 0) >= 0.80
    print(f"rule 3 -> {'PASS' if ok else 'FAIL'}")

    print("\nper set: documents, A matches, B matches, A = B")
    per = defaultdict(lambda: [0, 0, 0, 0])
    for r in rows:
        t = per[r[2]]
        t[0] += 1
        t[1] += nA(r) == r[3]
        t[2] += nB(r) == r[3]
        t[3] += nA(r) == nB(r)
    for s, t in sorted(per.items()):
        print(f"  {s:20s} {t[0]}  {t[1]}  {t[2]}  {t[3]}")

    cols = ["doc_id", "set", "n_answer_list", "answer_list", "n_A", "items_A", "unclear_A", "notes_A",
            "n_B", "items_B", "unclear_B", "notes_B"]
    todo = [r for r in rows if r[0] == 2 and (nA(r) != r[3] or nB(r) != r[3] or unclear(r[4]) or unclear(r[5]))]
    out = ROOT / "analysis/blind/adjudicate_round2.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for rnd, i, s, n, ra, rb in todo:
            w.writerow({"doc_id": i, "set": s, "n_answer_list": n,
                        "answer_list": "\n".join(g["text"] for g in docs[i]["gold_items"]),
                        "n_A": ra["n_found"], "items_A": ra["items_found"], "unclear_A": unclear(ra), "notes_A": ra["notes"],
                        "n_B": rb["n_found"], "items_B": rb["items_found"], "unclear_B": unclear(rb), "notes_B": rb["notes"]})
    print(f"\nwrote {out.relative_to(ROOT)}: {len(todo)} round-2 documents with a differing count or an unclear mark")


if __name__ == "__main__":
    main()
