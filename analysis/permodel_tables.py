#!/usr/bin/env python3
"""permodel_tables.py: per-model versions of the pilot paper's Tables tab:conditions and tab:forced.

    python3 analysis/permodel_tables.py --runs-dir runs --entries <v0 matcher entries.csv for the pilot runs>

By default it writes next to the main tables (paper/pilot/generated) and checks against them there.

Rates and intervals come from analysis/pilot_tables.py (its Pilot class: the same run parsing, the same
documents-with-n-<-k selection and the same group bootstrap), so every cell traces to the run folders.
The forced-slot shares count the v0 matcher's labels in entries.csv, after checking that every labelled
output has exactly as many entries as the run record parsed by pilot_tables.py.

Writes:
  permodel_conditions.tex       tabular of Table tab:permodel-conditions
  permodel_forced.tex           tabular of Table tab:permodel-forced
  permodel_check.txt            the pooling check: per-model numbers against the main tables
"""
import argparse
import csv
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--repo", default=str(ROOT),
                help="clone that holds analysis/pilot_tables.py (default: the clone this script sits in, under analysis/)")
ap.add_argument("--runs-dir", default=str(ROOT / "runs"))
ap.add_argument("--day", default="2026-10-15")
ap.add_argument("--entries", required=True, help="v0 matcher labels, one row per list entry")
ap.add_argument("--main-generated", default=str(ROOT / "paper" / "pilot" / "generated"),
                help="the main tables' generated/ folder, for the pooling check")
ap.add_argument("--out", default=str(ROOT / "paper" / "pilot" / "generated"))
ap.add_argument("--boot", type=int, default=10000)
ap.add_argument("--seed", type=int, default=20261014)
args = ap.parse_args()

sys.path.insert(0, str(Path(args.repo) / "analysis"))
import pilot_tables as pt  # noqa: E402  (also puts harness/ on the path)

KS = (3, 5)
FORCED_CONDS = ["min_k_enforced", "min_k_shown"]
# Table tab:forced rows -> matcher (label, note) classes; None = not judged by the v0 matcher
FORCED_ROWS = [
    ("split or restated true item", lambda lab, note: lab == "split_of_true"),
    ("real text, wrong kind", lambda lab, note: lab == "in_text_wrong_type"),
    ("true item missed by the list", None),
    ("in the wider source", None),
    ("invented", lambda lab, note: lab == "plausible_invented" and note not in ("prompt_echo", "possible_note")),
    ("invented: prompt echo or a missed note",
     lambda lab, note: lab == "plausible_invented" and note in ("prompt_echo", "possible_note")),
    ("placeholder", lambda lab, note: lab == "placeholder"),
    ("repeat", lambda lab, note: lab == "repeat"),
]
# the pooled min_k_enforced column as printed in Table tab:forced (sections/results.tex)
MAIN_FORCED = {"split or restated true item": "12.9", "real text, wrong kind": "76.2", "invented": "4.0",
               "invented: prompt echo or a missed note": "0.3", "placeholder": "4.4", "repeat": "2.2",
               "extra entries": "1,193"}


def thousands(x):
    return f"{x:,}"


P = pt.Pilot(args.runs_dir, args.day, args.boot, args.seed)
out = Path(args.out)
out.mkdir(parents=True, exist_ok=True)
rows = {m: P.rows(f"{m}_pilot") for m in pt.MAIN}
models = [m for m in pt.MAIN if rows[m]]
check = [f"# Pooling check ({args.day} pilot runs, {args.boot} bootstrap draws, seed {args.seed})", ""]
ok_all = True


def verdict(ok):
    global ok_all
    ok_all &= ok
    return "OK" if ok else "MISMATCH"


# ---------------------------------------------------------------------------------------------------------
# 1. conditions, per model: over-count [CI], exactly k (%), mean excess [CI]; documents with n < k
cond = {}
tex = ["  \\begin{tabular}{lrrrrrr}", "    \\toprule",
       "     & \\multicolumn{3}{c}{$k = 3$} & \\multicolumn{3}{c}{$k = 5$} \\\\",
       "    \\cmidrule(lr){2-4} \\cmidrule(lr){5-7}",
       "    Condition & Over-count & Exactly $k$ & Excess & Over-count & Exactly $k$ & Excess \\\\"]
for i, m in enumerate(models):
    tex.append("    \\midrule")
    tex.append(f"    \\multicolumn{{7}}{{l}}{{\\textit{{{pt.NAME[m]}}}}} \\\\")
    for c in pt.CONDS:
        cells = []
        for k in KS:
            sel = (lambda r, c=c, k=k: r["condition"] == c and r["k"] == k and r["n"] < k)
            t = P.rate(rows[m], sel)
            ek = P.rate(rows[m], sel, "exact_k")
            ex = P.rate(rows[m], sel, "excess")
            cond[(m, c, k)] = (t, ek, ex)
            cells += [pt.ci_txt(t), pt.pct(ek[0]) if ek else "--", pt.ci_txt(ex, 1, 2)]
        tex.append(f"    {pt.CND[c]} & " + " & ".join(cells) + " \\\\")
tex += ["    \\bottomrule", "  \\end{tabular}"]
(out / "permodel_conditions.tex").write_text("\n".join(tex) + "\n", encoding="ascii")

# check 1a: every per-model over-count cell is the cell of the main Table tab:conditions
main_body = (Path(args.main_generated) / "conditions_body.tex").read_text(encoding="ascii")
main_cells = {}
for line in main_body.splitlines():
    name = re.search(r"\\cnd\{(.*?)\}", line).group(1).replace("\\_", "_")
    cells = [x.strip() for x in line.split("&")[1:]]
    cells[-1] = cells[-1].rstrip("\\").strip()
    for j, m in enumerate(models):
        for h, k in enumerate(KS):
            main_cells[(m, name, k)] = cells[2 * j + h]
same = sum(pt.ci_txt(cond[key][0]) == main_cells[key] for key in cond)
check += ["## Table tab:conditions", "",
          f"- over-count cells equal to the main table ({args.main_generated}/conditions_body.tex): "
          f"{same} of {len(cond)} -> {verdict(same == len(cond) == len(main_cells))}"]
ns = sorted({cond[key][0][3] for key in cond})
check.append(f"- outputs per cell: {ns} (caption of tab:conditions: 60) -> {verdict(ns == [60])}")
# check 1b: pooled over the three models, per-model counts add up to the pooled-row rate
for c in pt.CONDS:
    for k in KS:
        hits = sum(round(cond[(m, c, k)][0][0] * cond[(m, c, k)][0][3]) for m in models)
        tot = sum(cond[(m, c, k)][0][3] for m in models)
        pooled_rows = [r for m in models for r in rows[m]]
        pooled = P.rate(pooled_rows, lambda r: r["condition"] == c and r["k"] == k and r["n"] < k)
        check.append(f"- {c} k={k}: per-model over-count {'+'.join(str(round(cond[(m, c, k)][0][0] * cond[(m, c, k)][0][3])) for m in models)}"
                     f" = {hits}/{tot} = {pt.pct(hits / tot)}; pooled rows {pt.pct(pooled[0])} (n = {pooled[3]})"
                     f" -> {verdict(abs(hits / tot - pooled[0]) < 1e-12 and tot == pooled[3])}")
# check 1c: the exactly-k ranges quoted in the caption of tab:conditions
for c, quoted in (("min_k_shown", "55 to 78"), ("min_k_enforced", "82 to 97")):
    vals = [100 * cond[(m, c, k)][1][0] for m in models for k in KS]
    got = f"{min(vals):.0f} to {max(vals):.0f}"
    check.append(f"- exactly k under {c}: {min(vals):.1f} to {max(vals):.1f}, rounded {got}; caption says {quoted}"
                 f" -> {verdict(got == quoted)}")
check.append("")

# ---------------------------------------------------------------------------------------------------------
# 2. forced slots, per model: shares of the matcher's extra entries (documents with n < k)
run_items = {}
for m in models:
    for r in rows[m]:
        if r["condition"] in FORCED_CONDS and r["n"] < r["k"] and r["valid"]:
            run_items[(m, r["request_id"])] = r["n_items"]
entries = list(csv.DictReader(open(args.entries, encoding="utf-8")))
per_req = Counter((e["model_key"], e["request_id"]) for e in entries
                  if e["condition"] in FORCED_CONDS and int(e["n"]) < int(e["k"]))
agree = sum(per_req[key] == run_items.get(key) for key in per_req)
covered = sum(1 for key, n in run_items.items() if n and key in per_req)
nonempty = sum(1 for n in run_items.values() if n)
check += ["## Table tab:forced", "",
          f"- matcher outputs whose entry count equals the run record's parsed list (n_items): {agree} of {len(per_req)}"
          f" -> {verdict(agree == len(per_req))}",
          f"- readable non-empty run outputs ({', '.join(FORCED_CONDS)}, n < k) that the matcher labelled: "
          f"{covered} of {nonempty} -> {verdict(covered == nonempty)}"]

counts = defaultdict(Counter)   # (condition, model or 'all') -> row label -> count
for e in entries:
    c, m = e["condition"], e["model_key"]
    if c not in FORCED_CONDS or m not in models or int(e["n"]) >= int(e["k"]) or e["label"] == "true_item":
        continue
    hit = [name for name, f in FORCED_ROWS if f and f(e["label"], e["note"])]
    assert len(hit) == 1, (e["label"], e["note"])
    for col in (m, "all"):
        counts[(c, col)][hit[0]] += 1
        counts[(c, col)]["extra entries"] += 1
cols = [(c, m) for c in FORCED_CONDS for m in models + ["all"]]
SHORT = {"qwen3.5-9b": "Qwen", "ministral-3-14b": "Ministral", "gemma-4-31b": "Gemma", "all": "All"}
tex = ["  \\begin{tabular}{l" + "r" * len(cols) + "}", "    \\toprule",
       "     & " + " & ".join(f"\\multicolumn{{{len(models) + 1}}}{{c}}{{{pt.CND[c]}}}" for c in FORCED_CONDS) + " \\\\",
       "    " + " ".join(f"\\cmidrule(lr){{{2 + j * (len(models) + 1)}-{1 + (j + 1) * (len(models) + 1)}}}"
                        for j in range(len(FORCED_CONDS))),
       "    What fills an extra entry & " + " & ".join(SHORT[m] for c, m in cols) + " \\\\", "    \\midrule"]
for name, f in FORCED_ROWS:
    if f is None:
        tex.append(f"    {name} & \\multicolumn{{{len(cols)}}}{{c}}{{not judged in v0}} \\\\")
        continue
    tex.append(f"    {name} & " + " & ".join(pt.pct(counts[col][name] / counts[col]['extra entries']) for col in cols)
               + " \\\\")
tex.append("    \\midrule")
tex.append("    extra entries & " + " & ".join(thousands(counts[col]["extra entries"]) for col in cols) + " \\\\")
tex += ["    \\bottomrule", "  \\end{tabular}"]
(out / "permodel_forced.tex").write_text("\n".join(tex) + "\n", encoding="ascii")

# check 2a: per-model counts add up to the pooled column; 2b: the pooled column is Table tab:forced
for c in FORCED_CONDS:
    for name in [n for n, f in FORCED_ROWS if f] + ["extra entries"]:
        parts = [counts[(c, m)][name] for m in models]
        check.append(f"- {c}, {name}: {'+'.join(map(str, parts))} = {sum(parts)}; pooled {counts[(c, 'all')][name]}"
                     f" -> {verdict(sum(parts) == counts[(c, 'all')][name])}")
check.append("- pooled min_k_enforced column against Table tab:forced (sections/results.tex):")
for name, quoted in MAIN_FORCED.items():
    tot = counts[("min_k_enforced", "all")]
    got = thousands(tot[name]) if name == "extra entries" else pt.pct(tot[name] / tot["extra entries"])
    check.append(f"  - {name}: {got}; table says {quoted} -> {verdict(got == quoted)}")
shown = counts[("min_k_shown", "all")]
for name, quoted in (("real text, wrong kind", "80"), ("invented", "3.5")):
    got = pt.pct(shown[name] / shown["extra entries"])
    rounded = f"{float(got):.0f}" if quoted == "80" else got
    check.append(f"- pooled min_k_shown {name}: {got}; Section sec:forced says {quoted}% -> {verdict(rounded == quoted)}")
gem = counts[("min_k_enforced", "gemma-4-31b")]
gem_ph = 100 * gem["placeholder"] / gem["extra entries"]
# Section sec:forced's "14% of its padded slots" uses pilot_tables.py's denominator (padded slots = parsed entries
# beyond n, generated/forced_rows.tex), not the matcher's extra entries; report both, informational only
sub = [r for r in rows["gemma-4-31b"] if r["condition"] == "min_k_enforced" and r["n"] < r["k"] and r["valid"]]
slots = sum(max(0, r["n_items"] - r["n"]) for r in sub)
ph = sum(r["n_placeholder"] for r in sub)
check.append(f"- (info) Gemma 4 31B placeholders under min_k_enforced: matcher {gem['placeholder']} of "
             f"{gem['extra entries']} extra entries = {gem_ph:.1f}%; pilot_tables.py {ph} of {slots} padded slots = "
             f"{100 * ph / slots:.1f}% (generated/forced_rows.tex). Section sec:forced's \"14%\" is the second.")

check += ["", "Missing runs (skipped): " + (", ".join(P.missing) or "none"),
          "ALL CHECKS PASS" if ok_all else "SOME CHECKS FAIL"]
(out / "permodel_check.txt").write_text("\n".join(check) + "\n", encoding="ascii")
print("\n".join(check))
sys.exit(0 if ok_all else 1)
