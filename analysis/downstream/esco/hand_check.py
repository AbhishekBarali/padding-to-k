#!/usr/bin/env python3
"""hand_check.py: the authors' hand check of the ESCO linker (OSF addendum 1, section 3.2).

    python analysis/downstream/esco/hand_check.py draw        draw the 50 links (seed 20261013) -> hand_check_ids.csv
    python analysis/downstream/esco/hand_check.py excel       hand_check_A.xlsx and hand_check_B.xlsx (identical)
    python analysis/downstream/esco/hand_check.py read hand_check_A.xlsx hand_check_B.xlsx
                                                              accuracy per author, agreement -> HAND_CHECK.md

What is drawn (needs esco_downstream.py to have run: links_true_items.csv and cache/entry_links.csv.gz):
- 25 links from true items: every true item of a job-ad document in the cells (n < 5) whose link reaches the
  registered cutoff (cosine >= 0.5);
- 25 links from model entries that are not true items: substantive entries of the 8 main models in the cells
  whose matcher label is neither true_item nor split_of_true and whose link reaches 0.5. An entry text that
  occurs in several outputs for the same ad is one link (each distinct link is drawn with equal chance).
Both lists are sorted (document, text) before drawing; numpy default_rng(20261013) picks 25 of each without
replacement. The drawn ids are committed, so the draw is fixed; `draw` refuses to overwrite them.

The two Excel files hold one row per link in one shuffled order (same seed), so the origin is not shown: a neutral row id (map in hand_check_rows.csv), what the ad was asked for, the job-ad text, the entry, the linked ESCO concept (preferred label),
the label it matched, the concept's ESCO description, "Correct link?" (Yes/No list) and notes.
"""
import argparse
import csv
import gzip
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
sys.path.insert(0, str(ROOT / "harness"))
sys.path.insert(0, str(HERE))
SEED = 20261013
PER_ORIGIN = 25
CUTOFF = 0.5
IDS = HERE / "hand_check_ids.csv"
ROWS = HERE / "hand_check_rows.csv"   # neutral Excel row id -> link id
NOT_TRUE = ("in_text_wrong_type", "plausible_invented")
ASKED = {"job_posts": "skills", "job_posts_knowledge": "tools, technologies and fields of knowledge"}
FIELDS = ["link_id", "origin", "doc_id", "set", "text", "concept_uri", "matched_label", "cosine", "source"]


def main_models():
    import yaml
    return yaml.safe_load((ROOT / "configs" / "models.yaml").read_text(encoding="utf-8"))["full_study"]["gpu"]["main"]


def populations():
    import common
    docs = common.load_documents()
    true_pop = []
    with open(HERE / "links_true_items.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d = docs[r["doc_id"]]
            if d["n"] < 5 and float(r["cosine"]) >= CUTOFF:
                true_pop.append({"origin": "true_item", "doc_id": r["doc_id"], "set": d["set"], "text": r["text"],
                                 "concept_uri": r["concept_uri"], "matched_label": r["matched_label"],
                                 "cosine": r["cosine"], "source": f"gold_index={r['gold_index']}"})
    mains = set(main_models())
    ent = {}
    with gzip.open(HERE / "cache" / "entry_links.csv.gz", "rt", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["model_key"] in mains and r["label"] in NOT_TRUE and float(r["cosine"]) >= CUTOFF:
                key = (r["doc_id"], r["text"])
                if key not in ent:
                    ent[key] = {"origin": "model_entry", "doc_id": r["doc_id"], "set": r["set"], "text": r["text"],
                                "concept_uri": r["concept_uri"], "matched_label": r["matched_label"],
                                "cosine": r["cosine"],
                                "source": f"{r['run_id']}|{r['request_id']}|entry={r['entry_index']}"}
    key = lambda x: (x["doc_id"], x["text"], x["source"])
    return sorted(true_pop, key=key), sorted(ent.values(), key=key)


def draw(force=False):
    if IDS.exists() and not force:
        sys.exit(f"{IDS.name} exists: the draw is fixed (use --force only to redo it on purpose)")
    rng = np.random.default_rng(SEED)
    true_pop, ent_pop = populations()
    picked = []
    for tag, pop in (("T", true_pop), ("E", ent_pop)):
        idx = sorted(rng.choice(len(pop), PER_ORIGIN, replace=False))
        for j, i in enumerate(idx, 1):
            picked.append({"link_id": f"{tag}{j:02d}", **pop[i]})
    with open(IDS, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(picked)
    print(f"drew {len(picked)} links from {len(true_pop)} true-item links and {len(ent_pop)} entry links -> {IDS.name}")
    meta = {"seed": SEED, "true_item_population": len(true_pop), "entry_population": len(ent_pop)}
    (HERE / "hand_check_draw.json").write_text(json.dumps(meta, indent=1) + "\n", encoding="utf-8")


def read_ids():
    with open(IDS, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def excel():
    import common
    import esco_linker as el
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font
    from openpyxl.worksheet.datavalidation import DataValidation
    docs = common.load_documents()
    concept = {c["uri"]: c for c in el.load_concepts()}
    rows = read_ids()
    order = np.random.default_rng(SEED).permutation(len(rows))
    with open(ROWS, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["row", "link_id"])
        for pos, i in enumerate(order):
            w.writerow([f"L{pos + 1:02d}", rows[i]["link_id"]])
    head = ["Link", "The ad was asked for", "Job ad", "Entry", "Linked ESCO concept", "Label it matched",
            "ESCO description", "Correct link?", "Notes"]
    widths = [8, 18, 70, 30, 28, 28, 50, 14, 30]
    for who in ("A", "B"):
        wb = Workbook()
        ws = wb.active
        ws.title = "Links"
        ws.append(head)
        for c in ws[1]:
            c.font = Font(bold=True)
        for pos, i in enumerate(order):
            r = rows[i]
            c = concept[r["concept_uri"]]
            # a neutral row id, so a reader cannot tell a true-item link from an entry link (map: ROWS)
            ws.append([f"L{pos + 1:02d}", ASKED[r["set"]], docs[r["doc_id"]]["text"], r["text"], c["label"],
                       r["matched_label"], c["description"], None, None])
        dv = DataValidation(type="list", formula1='"Yes,No"', allow_blank=True, showErrorMessage=True,
                            errorTitle="Yes or No", error="Choose Yes or No from the list.")
        ws.add_data_validation(dv)
        dv.add(f"H2:H{len(rows) + 1}")
        for j, w in enumerate(widths):
            ws.column_dimensions[chr(65 + j)].width = w
        for row in ws.iter_rows(min_row=1, max_row=len(rows) + 1):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
        ws.freeze_panes = "B2"
        path = HERE / f"hand_check_{who}.xlsx"
        wb.save(path)
        print(f"wrote {path.name} ({len(rows)} links)")


def answers(path):
    from openpyxl import load_workbook
    ws = load_workbook(path, read_only=True).active
    it = ws.iter_rows(values_only=True)
    head = list(next(it))
    li, ai, ni = head.index("Link"), head.index("Correct link?"), head.index("Notes")
    out = {}
    for row in it:
        if row[li]:
            v = (str(row[ai]).strip().lower() if row[ai] is not None else "")
            out[row[li]] = {"yes": True, "no": False}.get(v)
    return out


def kappa(a, b):
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return None if pe == 1 else (po - pe) / (1 - pe)


def wilson(k, n, z=1.959963984540054):
    """95% Wilson score interval for k successes in n trials, as fractions."""
    if n == 0:
        return None
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * (p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5 / den
    return mid - half, mid + half


def read(path_a, path_b):
    ids = {r["link_id"]: r for r in read_ids()}
    with open(ROWS, encoding="utf-8") as f:
        to_link = {r["row"]: r["link_id"] for r in csv.DictReader(f)}
    A = {to_link.get(k, k): v for k, v in answers(path_a).items()}
    B = {to_link.get(k, k): v for k, v in answers(path_b).items()}
    lines = ["# Hand check of the ESCO linker", "",
             f"Written by `python analysis/downstream/esco/hand_check.py read {Path(path_a).name} {Path(path_b).name}`. "
             f"{len(ids)} links drawn with seed {SEED} (`hand_check_ids.csv`): {PER_ORIGIN} from true items, "
             f"{PER_ORIGIN} from model entries that are not true items; cutoff {CUTOFF}.", "",
             "| who | links answered | correct | accuracy | 95% Wilson interval | true-item links | entry links |",
             "|---|---|---|---|---|---|---|"]
    for who, X in (("author A", A), ("author B", B)):
        got = {k: v for k, v in X.items() if k in ids and v is not None}
        acc = lambda o: [v for k, v in got.items() if ids[k]["origin"] == o]
        ti, en = acc("true_item"), acc("model_entry")
        ci = wilson(sum(got.values()), len(got))
        ci_txt = "n/a" if ci is None else f"{100 * ci[0]:.0f}% to {100 * ci[1]:.0f}%"
        lines.append(f"| {who} | {len(got)} / {len(ids)} | {sum(got.values())} | "
                     f"{100 * sum(got.values()) / max(1, len(got)):.0f}% | {ci_txt} | "
                     f"{sum(ti)} / {len(ti)} | {sum(en)} / {len(en)} |")
    both = [k for k in ids if A.get(k) is not None and B.get(k) is not None]
    if both:
        a, b = [A[k] for k in both], [B[k] for k in both]
        agree = sum(x == y for x, y in zip(a, b))
        kp = kappa(a, b)
        yes_both = sum(x and y for x, y in zip(a, b))
        lines += ["", f"- Answered by both: {len(both)}. Same answer: {agree} ({100 * agree / len(both):.0f}%); "
                  f"Cohen's kappa {'undefined' if kp is None else f'{kp:.2f}'}.",
                  f"- Correct according to both authors: {yes_both} of {len(both)} ({100 * yes_both / len(both):.0f}%)."]
        diff = [k for k in both if A[k] != B[k]]
        if diff:
            lines.append(f"- Answered differently: {', '.join(sorted(diff))}.")
    missing = [k for k in ids if A.get(k) is None or B.get(k) is None]
    if missing:
        lines.append(f"- Not answered by both yet: {len(missing)} links.")
    (HERE / "HAND_CHECK.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("draw")
    d.add_argument("--force", action="store_true")
    sub.add_parser("excel")
    r = sub.add_parser("read")
    r.add_argument("a")
    r.add_argument("b")
    x = ap.parse_args()
    if x.cmd == "draw":
        draw(x.force)
    elif x.cmd == "excel":
        excel()
    else:
        read(x.a, x.b)
