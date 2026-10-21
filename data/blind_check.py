#!/usr/bin/env python3
"""blind_check.py: the blind agreement check on the answer lists, with no answer list in sight.

    python blind_check.py make [--fresh 40] [--out blind/]
    python blind_check.py round2 [--sets meetings,emails,job_posts,job_posts_knowledge,clinical] [--per-set 5]
    python blind_check.py agree blind/blind_sheet_A.csv blind/blind_sheet_B.csv [--out blind/]

Why this exists: verify_sheet.csv shows the answer list, the cleanup change and the AI notes, so filling
it in is a review, not a blind check. Here each checker reads only the document and the definition of
what to list, and writes down the items they find. Agreement is then computed on the COUNT (n), which is
the number the study depends on, plus the unclear rate.

make   writes blind/blind_sheet.csv (one row per document, shuffled, no answer list, no n, no split) and
       blind/blind_key.csv (doc_id -> part, kept apart so the checker never needs to open it).
       Documents: every pilot document ("seen": both authors reviewed them with the lists in view), plus
       --fresh documents from the full split that appear in NO review sheet or page (cleanup/review_*,
       local/review_*), spread over the sets and over n. Ten fresh review documents go to a local-only
       sheet, local/blind_sheet_reviews.csv (review text may not be committed); check it the same way
       and run `agree` on it with --key local/blind_key_reviews.csv.
agree  reads two filled-in copies (each checker works alone on their own copy) and prints:
       count agreement of each checker with the answer list, and of the checkers with each other
       (exact share, Cohen's kappa on n as a category, quadratic-weighted kappa, Gwet's AC1), the
       share of documents either checker marked unclear, all of it for pilot and fresh separately.
       Rule 3 of the pilot (RUN-PLAN 5.2), printed as PASS or FAIL: on the fresh documents each checker
       agrees with the answer list's count on at least 85% of documents, the two checkers' AC1 is at
       least 0.80, and at most 10% of pilot documents are marked unclear by either checker.
       It also writes blind/adjudicate.csv: every document where a checker's count differs from the
       answer list or a checker marked it unclear, now WITH the answer list, for the two of you to settle.
       Put every settled change into cleanup/decisions.jsonl and rebuild (see cleanup/README.md).

How to fill in a sheet: copy blind_sheet.csv to blind_sheet_A.csv (or _B), put your name in `checker`,
and for each row write every item you would list in `items_found`, one per line, then the count in
`n_found` (0 if there are none), `y` in `unclear_y_n` if two careful readers could count differently,
and anything worth saying in `notes`. Use the rules in cleanup/COUNTING_RULES.md. Do not look at
documents.jsonl, verify_sheet.csv, model outputs or the other checker's sheet while you work.
"""
import argparse
import csv
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
SEED = 20261014
SHEET_COLS = ["row", "doc_id", "set", "list_asked", "definition", "text",
              "checker", "items_found", "n_found", "unclear_y_n", "notes"]


def load_docs():
    docs = [json.loads(line) for line in (HERE / "documents.jsonl").read_text(encoding="utf-8").splitlines()]
    local = HERE / "local" / "restricted_documents.jsonl"
    if local.exists():
        docs += [json.loads(line) for line in local.read_text(encoding="utf-8").splitlines() if line.strip()]
    return docs


def already_reviewed():
    """Every document id that appears in a cleanup review sheet or page (shown with its answer list)."""
    ids = set()
    paths = list((HERE / "cleanup").glob("review_*")) + list((HERE / "local").glob("review_*"))
    for path in paths:
        ids |= set(re.findall(r"\b[a-z]{3}-[0-9a-f]{6}\b", path.read_text(encoding="utf-8", errors="replace")))
    return ids


def fresh_sample(docs, total, rng, sets=None, restricted=False, exclude=frozenset()):
    """Spread `total` never-reviewed full-split documents over the sets, and over n inside each set."""
    seen = already_reviewed() | set(exclude)
    pool = defaultdict(lambda: defaultdict(list))
    for d in docs:
        if d["split"] != "full" or d["doc_id"] in seen or bool(d.get("redistributable", True)) == restricted:
            continue
        if sets is None or d["set"] in sets:
            pool[d["set"]][d["n"]].append(d)
    sets = sorted(pool)
    per_set = Counter({s: total // len(sets) for s in sets})
    for s in sets[: total - sum(per_set.values())]:
        per_set[s] += 1
    chosen = []
    for s in sets:
        by_n = {n: sorted(v, key=lambda d: d["doc_id"]) for n, v in sorted(pool[s].items())}
        for v in by_n.values():
            rng.shuffle(v)
        while per_set[s] > 0 and any(by_n.values()):
            for n in list(by_n):
                if per_set[s] > 0 and by_n[n]:
                    chosen.append(by_n[n].pop())
                    per_set[s] -= 1
    return chosen


def make(args):
    prompts = json.loads((HERE / "prompts.json").read_text(encoding="utf-8"))
    docs = load_docs()
    rng = random.Random(SEED)
    pilot = [d for d in docs if d["split"] == "pilot"]
    fresh = fresh_sample(docs, args.fresh, rng)
    rows = [(d, "pilot") for d in pilot] + [(d, "fresh") for d in fresh]
    rng.shuffle(rows)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    def write(sheet, key, rows):
        with open(sheet, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=SHEET_COLS)
            w.writeheader()
            for i, (d, _) in enumerate(rows, 1):
                lst = prompts["lists"][d["list_type"]]
                w.writerow({"row": i, "doc_id": d["doc_id"], "set": d["set"], "list_asked": lst["many"],
                            "definition": lst["describe"], "text": d["text"]})
        with open(key, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["doc_id", "part"])
            for d, part in sorted(rows, key=lambda r: r[0]["doc_id"]):
                w.writerow([d["doc_id"], part])

    write(out / "blind_sheet.csv", out / "blind_key.csv", rows)
    parts = Counter(p for _, p in rows)
    print(f"wrote {out / 'blind_sheet.csv'}: {len(rows)} documents ({parts['pilot']} pilot, {parts['fresh']} fresh)")
    print("fresh by set:", dict(Counter(d["set"] for d in fresh)))
    reviews = fresh_sample(docs, 10, rng, sets={"reviews"}, restricted=True)
    if reviews:
        local = HERE / "local"
        local.mkdir(exist_ok=True)
        write(local / "blind_sheet_reviews.csv", local / "blind_key_reviews.csv", [(d, "fresh") for d in reviews])
        print(f"wrote {local / 'blind_sheet_reviews.csv'}: {len(reviews)} review documents (local only, never commit)")


SEED_ROUND2 = 20261015
ROUND2_SETS = "meetings,emails,job_posts,job_posts_knowledge,clinical"


def round2(args):
    """Second round on the sets whose definitions were extended after the first (DECISIONS.md, 15 Oct).

    Fresh documents as in `make`, minus every document that appears in an earlier sheet or file in --out
    (the first round's sheets, the 100-row sheet, adjudicate.csv), so no checker has counted or seen one.
    Writes one sheet per checker with the checker's name filled in, and a key (doc_id -> part = fresh).
    """
    prompts = json.loads((HERE / "prompts.json").read_text(encoding="utf-8"))
    docs = load_docs()
    out = Path(args.out)
    shown = set()
    for path in out.glob("*.csv"):
        shown |= set(re.findall(r"\b[a-z]{3}-[0-9a-f]{6}\b", path.read_text(encoding="utf-8", errors="replace")))
    sets = set(args.sets.split(","))
    rng = random.Random(SEED_ROUND2)
    fresh = fresh_sample(docs, args.per_set * len(sets), rng, sets=sets, exclude=shown)
    rng.shuffle(fresh)
    for checker, suffix in (("Abhishek", "A"), ("B", "B")):
        with open(out / f"blind_sheet_round2_{suffix}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=SHEET_COLS)
            w.writeheader()
            for i, d in enumerate(fresh, 1):
                lst = prompts["lists"][d["list_type"]]
                w.writerow({"row": i, "doc_id": d["doc_id"], "set": d["set"], "list_asked": lst["many"],
                            "definition": lst["describe"], "text": d["text"], "checker": checker})
    with open(out / "blind_key_round2.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["doc_id", "part"])
        for d in sorted(fresh, key=lambda d: d["doc_id"]):
            w.writerow([d["doc_id"], "fresh"])
    print(f"wrote {out / 'blind_sheet_round2_A.csv'} and _B.csv: {len(fresh)} documents, "
          f"by set {dict(Counter(d['set'] for d in fresh))}, by n {dict(Counter(d['n'] for d in fresh))}; "
          f"{len(shown)} earlier documents left out")


# ---------------------------------------------------------------------------------------------
def cohen(pairs):
    if not pairs:
        return None
    po = sum(a == b for a, b in pairs) / len(pairs)
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[c] * cb[c] for c in set(ca) | set(cb)) / len(pairs) ** 2
    return round((po - pe) / (1 - pe), 3) if pe < 1 else 1.0


def weighted_kappa(pairs):
    """Quadratic-weighted kappa for integer counts: a 1-off disagreement costs less than a 3-off one."""
    if not pairs:
        return None
    cats = sorted({x for p in pairs for x in p})
    if len(cats) < 2:
        return 1.0
    lo, hi = cats[0], cats[-1]
    wt = lambda a, b: ((a - b) / (hi - lo)) ** 2
    obs = sum(wt(a, b) for a, b in pairs) / len(pairs)
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    m = len(pairs)
    exp = sum(ca[a] * cb[b] * wt(a, b) for a in ca for b in cb) / m ** 2
    return round(1 - obs / exp, 3) if exp else 1.0


def gwet_ac1(pairs):
    """Gwet's AC1: stable when almost every document gets the same answer (kappa is not)."""
    if not pairs:
        return None
    cats = sorted({x for p in pairs for x in p})
    q = len(cats)
    if q < 2:
        return 1.0
    po = sum(a == b for a, b in pairs) / len(pairs)
    pi = {c: (sum(a == c for a, _ in pairs) + sum(b == c for _, b in pairs)) / (2 * len(pairs)) for c in cats}
    pe = sum(p * (1 - p) for p in pi.values()) / (q - 1)
    return round((po - pe) / (1 - pe), 3) if pe < 1 else 1.0


def read_sheet(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = {r["doc_id"]: r for r in csv.DictReader(f)}
    filled = {}
    for i, r in rows.items():
        s = r.get("n_found", "").strip()
        if s:
            try:
                filled[i] = r | {"n": int(s), "unclear": r.get("unclear_y_n", "").strip().lower()[:1] == "y"}
            except ValueError:
                raise SystemExit(f"{path}: n_found for {i} is not a whole number: {s!r}")
    return filled


def agree(args):
    a, b = read_sheet(args.files[0]), read_sheet(args.files[1])
    docs = {d["doc_id"]: d for d in load_docs()}
    out = Path(args.out)
    key_path = Path(args.key) if args.key else out / "blind_key.csv"
    with open(key_path, newline="", encoding="utf-8") as f:
        key = {r["doc_id"]: r["part"] for r in csv.DictReader(f)}
    ids = sorted(i for i in a if i in b)
    if not ids:
        raise SystemExit("no document is filled in on both sheets")
    print(f"{len(ids)} documents filled in by both checkers "
          f"({a[ids[0]].get('checker') or 'A'} and {b[ids[0]].get('checker') or 'B'})")
    stats = {}
    for part in ["pilot", "fresh", "all"]:
        sel = [i for i in ids if part == "all" or key.get(i) == part]
        if not sel:
            continue
        gold = {i: docs[i]["n"] for i in sel}
        print(f"\n== {part}: {len(sel)} documents")
        for name, x, y in [("A vs answer list", {i: a[i]["n"] for i in sel}, gold),
                           ("B vs answer list", {i: b[i]["n"] for i in sel}, gold),
                           ("A vs B", {i: a[i]["n"] for i in sel}, {i: b[i]["n"] for i in sel})]:
            pairs = [(x[i], y[i]) for i in sel]
            exact = sum(p == q for p, q in pairs) / len(pairs)
            print(f"  {name:17s} same count {100 * exact:5.1f}%  kappa {cohen(pairs)}  "
                  f"weighted kappa {weighted_kappa(pairs)}  AC1 {gwet_ac1(pairs)}")
        unclear = sum(a[i]["unclear"] or b[i]["unclear"] for i in sel)
        print(f"  unclear by either checker: {unclear}/{len(sel)} ({100 * unclear / len(sel):.1f}%)")
        stats[part] = {"a_exact": sum(a[i]["n"] == gold[i] for i in sel) / len(sel),
                       "b_exact": sum(b[i]["n"] == gold[i] for i in sel) / len(sel),
                       "ac1": gwet_ac1([(a[i]["n"], b[i]["n"]) for i in sel]), "unclear": unclear / len(sel)}
    print("\nRule 3 (RUN-PLAN 5.2):")
    if "fresh" in stats:
        f = stats["fresh"]
        print(f"  fresh: A matches the list {100 * f['a_exact']:.0f}%, B {100 * f['b_exact']:.0f}% (need 85% each); "
              f"AC1 {f['ac1']} (need 0.80) -> {'PASS' if min(f['a_exact'], f['b_exact']) >= 0.85 and (f['ac1'] or 0) >= 0.80 else 'FAIL'}")
    if "pilot" in stats:
        print(f"  pilot: unclear {100 * stats['pilot']['unclear']:.0f}% (at most 10%) -> "
              f"{'PASS' if stats['pilot']['unclear'] <= 0.10 else 'FAIL'}")
    cols = ["doc_id", "part", "set", "n_answer_list", "answer_list", "n_A", "items_A", "unclear_A", "notes_A",
            "n_B", "items_B", "unclear_B", "notes_B", "decision", "new_list_if_changed"]
    todo = [i for i in ids if a[i]["n"] != docs[i]["n"] or b[i]["n"] != docs[i]["n"]
            or a[i]["unclear"] or b[i]["unclear"]]
    with open(out / "adjudicate.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for i in todo:
            d = docs[i]
            w.writerow({"doc_id": i, "part": key.get(i, ""), "set": d["set"], "n_answer_list": d["n"],
                        "answer_list": "\n".join(g["text"] for g in d["gold_items"]),
                        "n_A": a[i]["n"], "items_A": a[i].get("items_found", ""), "unclear_A": a[i]["unclear"],
                        "notes_A": a[i].get("notes", ""), "n_B": b[i]["n"], "items_B": b[i].get("items_found", ""),
                        "unclear_B": b[i]["unclear"], "notes_B": b[i].get("notes", "")})
    print(f"\nwrote {out / 'adjudicate.csv'}: {len(todo)} documents to settle together")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["make", "round2", "agree"])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--fresh", type=int, default=40, help="fresh full-split documents to add (default 40)")
    ap.add_argument("--sets", default=ROUND2_SETS, help="round2: the sets to draw from")
    ap.add_argument("--per-set", type=int, default=5, help="round2: documents per set (default 5)")
    ap.add_argument("--out", default=str(HERE / "blind"))
    ap.add_argument("--key", help="key file for agree (default: <out>/blind_key.csv)")
    args = ap.parse_args()
    if args.cmd == "make":
        make(args)
    elif args.cmd == "round2":
        round2(args)
    else:
        if len(args.files) != 2:
            ap.error("agree needs two filled-in sheets")
        agree(args)


if __name__ == "__main__":
    main()
