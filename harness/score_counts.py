#!/usr/bin/env python3
"""score_counts.py: the over-count outcome, which needs no item matcher, and the pilot stop rules.

    python harness/score_counts.py runs/<run_a> [runs/<run_b> ...] [--out analysis/pilot] [--boot 10000]

For every output it counts SUBSTANTIVE items: list entries that are not a placeholder ("N/A", "none",
"No further requests", "Only one request in this email", ...; an entry copied from the document is
never a placeholder) and not a string-level repeat of an earlier entry. Then:

  over_count   the output has more substantive items than the document has true items (m > n)
  excess       m - n when positive (how many extra items)
  exact_k      the list has exactly k entries (did the model obey the count, true or not)

What over-count is and is not: it is "the list has more entries than the document has true items".
It also fires when a model splits one true item into two, repeats an item in other words, or lists
real text of the wrong kind; the item matcher tells those apart from invention. It is not a lower bound
on invented items. Placeholder notes the lexicon misses would inflate it, more where count pressure is
higher, which is why the plan audits short and negated items by hand (RUN-PLAN 5.1).

Outputs (in --out):
  per_output_counts.csv   one row per request id (the `none` answer is reused at k = 1, 3, 5); no text
  cells.csv               over-count rate and invalid rate per model x arm x condition x k on documents
                          with n < k, with a 95% interval from a bootstrap over document groups
  contrasts.md            the pilot stop rules (pooled and per model) and the dose contrast
Invalid outputs (no list could be read) count as NOT over-count; contrasts.md also gives the rules
with invalid outputs left out. Truncated lists are salvaged (the complete entries before the cut).
Bootstrap unit: the document's `group` (an original meeting, email folder, job ad, case report,
novel chapter), so the 16 job ads that appear in both job-ad sets are resampled together.
"""
import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402

try:
    import numpy as np
except ImportError:  # the pure-Python fallback is fine for the pilot, slow for the full study
    np = None

COLS = ["request_id", "run_id", "model_key", "arm", "doc_id", "group", "set", "condition", "k", "n",
        "gap_k_minus_n", "wording_id", "enforce_schema", "status", "finish_reason", "parse_rung", "list_source",
        "text_outside_json", "reasoning_in_content", "n_answer_lists", "valid", "n_items", "n_substantive", "n_placeholder",
        "n_escape", "n_duplicate", "over_count", "excess", "exact_k", "fewer_than_k", "more_than_k",
        "enforcement_violation", "cap_violation", "truncated", "reasoning_chars"]


def latest_records(run_dir):
    recs = {}
    for name in ("raw.jsonl", "raw_restricted.jsonl"):
        p = Path(run_dir) / name
        if p.exists():
            for r in common.read_jsonl(p):
                recs[r["request_id"]] = r
    return recs


def expand(run_dir, prompts, docs, req_index):
    """One row per covered request id, from the record of the request that was actually sent."""
    planned = common.read_jsonl(Path(run_dir) / "planned.jsonl")
    recs = latest_records(run_dir)
    man = json.loads((Path(run_dir) / "manifest.json").read_text())
    rows = []
    for p in planned:
        rec = recs.get(p["request_id"])
        for rid in [p["request_id"], *p["also_answers"]]:
            q = req_index[rid]
            d = docs[q["doc_id"]]
            row = {"request_id": rid, "run_id": man["run_id"], "model_key": man["model_key"],
                   "arm": q.get("arm") or "main", "doc_id": q["doc_id"], "group": d.get("group") or q["doc_id"],
                   "set": q["set"], "condition": q["condition"], "k": q["k"], "n": q["n"],
                   "gap_k_minus_n": q["k"] - q["n"], "wording_id": q["wording_id"],
                   "enforce_schema": q["enforce_schema"], "status": rec["status"] if rec else "missing"}
            if rec and rec["status"] == "ok":
                field = prompts["lists"][q["schema_id"].split("|")[0]]["field"]
                parsed = common.parse_output(rec.get("content"), field)
                valid = parsed["items"] is not None
                c = common.count_items(parsed["items"] or [], prompts.get("escape_value", "N/A"), d["text"])
                m, n, k = c["n_substantive"], q["n"], q["k"]
                row.update({
                    "finish_reason": rec.get("finish_reason"), "parse_rung": parsed["parse_rung"],
                    "list_source": parsed["list_source"], "text_outside_json": parsed["text_outside_json"],
                    "reasoning_in_content": parsed["reasoning_in_content"], "n_answer_lists": parsed["n_answer_lists"],
                    "valid": valid, "n_items": c["n_items"], "n_substantive": m, "n_placeholder": c["n_placeholder"],
                    "n_escape": c["n_escape"], "n_duplicate": c["n_duplicate"],
                    "over_count": valid and m > n, "excess": max(0, m - n) if valid else 0,
                    "exact_k": valid and c["n_items"] == k, "fewer_than_k": valid and c["n_items"] < k,
                    "more_than_k": valid and c["n_items"] > k,
                    "enforcement_violation": bool(q["enforce_schema"] and (not valid or c["n_items"] < k)),
                    "cap_violation": bool(q["condition"] in ("max_k_shown", "prose_up_to_k") and valid
                                          and c["n_items"] > k),
                    "truncated": rec.get("finish_reason") == "length",
                    "reasoning_chars": len(rec.get("reasoning_content") or ""),
                })
            rows.append(row)
    return rows


class Boot:
    """Percentile 95% interval of a ratio of sums, resampling groups with replacement inside each set."""

    def __init__(self, boot, seed):
        self.boot, self.seed = boot, seed

    def ci(self, per_group, strata):
        """per_group: {group: (sum_of_values, n_values)}; strata: {group: set}."""
        groups = list(per_group)
        num = [per_group[g][0] for g in groups]
        den = [per_group[g][1] for g in groups]
        est = sum(num) / max(1, sum(den))
        by_set = defaultdict(list)
        for i, g in enumerate(groups):
            by_set[strata[g]].append(i)
        if np is not None:
            rng = np.random.default_rng(self.seed)
            num_a, den_a = np.array(num, float), np.array(den, float)
            tot_n, tot_d = np.zeros(self.boot), np.zeros(self.boot)
            for idx in by_set.values():
                idx = np.array(idx)
                pick = idx[rng.integers(0, len(idx), (self.boot, len(idx)))]
                tot_n += num_a[pick].sum(axis=1)
                tot_d += den_a[pick].sum(axis=1)
            draws = np.sort(tot_n / np.maximum(tot_d, 1))
            return est, float(draws[int(0.025 * self.boot)]), float(draws[int(0.975 * self.boot) - 1])
        import random
        rng = random.Random(self.seed)
        draws = []
        for _ in range(self.boot):
            n_ = d_ = 0.0
            for idx in by_set.values():
                for _ in idx:
                    i = rng.choice(idx)
                    n_ += num[i]
                    d_ += den[i]
            draws.append(n_ / max(1.0, d_))
        draws.sort()
        return est, draws[int(0.025 * self.boot)], draws[int(0.975 * self.boot) - 1]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--out", default=str(common.ROOT / "analysis" / "counts"))
    ap.add_argument("--boot", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=20261014)
    args = ap.parse_args()
    prompts = common.load_prompts()
    docs = common.load_documents()
    req_index = {r["request_id"]: r for r in common.load_requests()}
    rows, seen = [], {}
    for r in args.runs:
        for row in expand(r, prompts, docs, req_index):
            key = (row["model_key"], row["request_id"])
            if key in seen:                       # the same model answered the same request in two runs
                raise SystemExit(f"{key} appears in both {seen[key]} and {row['run_id']}: pass each "
                                 f"model's request only once (a repeat run belongs in repeat_check.py)")
            seen[key] = row["run_id"]
            rows.append(row)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "per_output_counts.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in COLS})
    boot = Boot(args.boot, args.seed)
    strata = {r["group"]: r["set"] for r in rows}
    ok = [r for r in rows if r["status"] == "ok"]
    status = Counter(r["status"] for r in rows)

    def agg(values_by_group):
        return {g: (sum(v), len(v)) for g, v in values_by_group.items()}

    # cells: model x arm x condition x k, documents under pressure (n < k)
    cell = defaultdict(lambda: defaultdict(list))
    inval = defaultdict(list)
    for r in ok:
        if r["n"] < r["k"]:
            key = (r["model_key"], r["arm"], r["condition"], r["k"])
            cell[key][r["group"]].append(float(r["over_count"]))
            inval[key].append(0.0 if r["valid"] else 1.0)
    with open(out / "cells.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model_key", "arm", "condition", "k", "n_groups", "n_outputs", "over_count_rate",
                    "ci_low", "ci_high", "invalid_rate"])
        for key, per_group in sorted(cell.items()):
            est, lo, hi = boot.ci(agg(per_group), strata)
            w.writerow([*key, len(per_group), sum(len(v) for v in per_group.values()), round(est, 4),
                        round(lo, 4), round(hi, 4), round(sum(inval[key]) / len(inval[key]), 4)])

    def contrast(a, b, model=None, drop_invalid=False, arm="main", ks=(3, 5), outcome="over_count", max_n=None):
        """Paired difference a - b per (document, model, k), averaged; documents with n < k."""
        val = defaultdict(dict)
        for r in ok:
            if r["n"] >= r["k"] or r["k"] not in ks or r["arm"] != arm or (model and r["model_key"] != model):
                continue
            if (drop_invalid and not r["valid"]) or (max_n is not None and r["n"] > max_n):
                continue
            if r["condition"] in (a, b):
                key = (r["doc_id"], r["model_key"], r["k"])
                if r["condition"] in val[key]:
                    raise SystemExit(f"two {r['condition']} outputs for {key}: one wording per condition expected")
                val[key][r["condition"]] = (float(r[outcome]), r["group"])
        per_group = defaultdict(list)
        for v in val.values():
            if a in v and b in v:
                per_group[v[a][1]].append(v[a][0] - v[b][0])
        if not per_group:
            return None
        est, lo, hi = boot.ci(agg(per_group), strata)
        return {"diff": est, "lo": lo, "hi": hi, "groups": len(per_group),
                "pairs": sum(len(v) for v in per_group.values())}

    def dose(model=None, outcome="over_count", arm="main"):
        """Within document: min_k_shown at k = 5 minus k = 3, documents with n <= 2 (under pressure at both)."""
        val = defaultdict(dict)
        for r in ok:
            if r["condition"] == "min_k_shown" and r["arm"] == arm and r["n"] <= 2 and r["k"] in (3, 5) \
                    and (not model or r["model_key"] == model):
                val[(r["doc_id"], r["model_key"])][r["k"]] = (float(r[outcome]), r["group"])
        per_group = defaultdict(list)
        for v in val.values():
            if 3 in v and 5 in v:
                per_group[v[5][1]].append(v[5][0] - v[3][0])
        if not per_group:
            return None
        est, lo, hi = boot.ci(agg(per_group), strata)
        return {"diff": est, "lo": lo, "hi": hi, "groups": len(per_group),
                "pairs": sum(len(v) for v in per_group.values())}

    def verdict(c, per_model):
        """Precedence: STOP wins. Then GO. Otherwise the caution rule decides."""
        if c is None:
            return "not computable (condition missing)"
        if c["hi"] < 0.10:
            return "STOP OR RETHINK: even the upper end is under 10 points"
        if c["lo"] > 0:
            return "GO: the lower end is above 0"
        ests = [m["diff"] for m in per_model if m]
        if len([e for e in ests if e > 0.05]) >= 2 and min(ests, default=0) >= 0:
            return "GO WITH CAUTION: at least 2 models above 5 points and none below 0"
        return "RETHINK: the caution rule is not met"

    models = sorted({r["model_key"] for r in ok})
    lines = ["# Count outcome: pilot report", "",
             f"Runs: {', '.join(Path(r).name for r in args.runs)}",
             f"Rows: {len(rows)} request ids; status {dict(status)}", "",
             "Over-count = more substantive entries than true items (m > n). Documents with n < k, k = 3 and 5.",
             f"Differences in rate points (0.10 = 10 points); 95% intervals from {args.boot} bootstrap draws over",
             "document groups, resampled within each set. Rules (RUN-PLAN 5.2): STOP if the upper end is under",
             "10 points (this wins); GO if the lower end is above 0; otherwise GO WITH CAUTION only if at least",
             "2 models are above 5 points and none is below 0.", ""]
    for a, b, label in [("min_k_shown", "none", "Rule 1: minItems shown vs no count (the floor)"),
                        ("min_k_shown", "max_k_shown", "Rule 2: minItems shown vs maxItems shown")]:
        per_model = {mk: contrast(a, b, mk) for mk in models}
        pooled = contrast(a, b, None)
        lines += [f"## {label}", "", "| models | difference | 95% interval | groups | pairs |", "|---|---|---|---|---|"]
        for mk, c in [("all (pooled)", pooled), *per_model.items()]:
            if c:
                lines.append(f"| {mk} | {c['diff']:+.3f} | {c['lo']:+.3f} to {c['hi']:+.3f} | {c['groups']} | {c['pairs']} |")
        lines += ["", f"Verdict: **{verdict(pooled, list(per_model.values()))}**"]
        c2 = contrast(a, b, None, drop_invalid=True)
        c3 = contrast(a, b, None, outcome="excess")
        if c2:
            lines.append(f"- invalid outputs left out: {c2['diff']:+.3f} ({c2['lo']:+.3f} to {c2['hi']:+.3f})")
        if c3:
            lines.append(f"- extra items per output (excess) instead of yes/no: {c3['diff']:+.3f} "
                         f"({c3['lo']:+.3f} to {c3['hi']:+.3f})")
        lines.append("")
    lines += ["## Dose: minItems shown at k = 5 minus k = 3, same document, n at most 2", ""]
    for outcome in ("over_count", "excess"):
        for mk in [None, *models]:
            c = dose(mk, outcome)
            if c:
                lines.append(f"- {outcome}, {mk or 'all (pooled)'}: {c['diff']:+.3f} ({c['lo']:+.3f} to {c['hi']:+.3f}), "
                             f"{c['pairs']} pairs")
    lines.append("")
    inv = Counter((r["model_key"], r["condition"]) for r in ok if not r["valid"])
    tot = Counter((r["model_key"], r["condition"]) for r in ok)
    lines += ["## Invalid outputs (no list could be read), by model and condition", ""]
    lines += [f"- {mk} / {cond}: {inv[(mk, cond)]} of {tot[(mk, cond)]}" for mk, cond in sorted(tot) if inv[(mk, cond)]] \
        or ["- none"]
    lines.append("")
    for arm in sorted({r["arm"] for r in ok} - {"main"}):
        title = ("Dev set: reserve documents, never in the study" if arm == "dev"
                 else f"Robustness arm: {arm} (same contrasts, pilot documents)")
        lines += [f"## {title}", ""]
        for a, b in [("min_k_shown", "none"), ("min_k_shown", "max_k_shown")]:
            c = contrast(a, b, None, arm=arm)
            if c:
                lines.append(f"- {a} vs {b}: {c['diff']:+.3f} ({c['lo']:+.3f} to {c['hi']:+.3f}), {c['groups']} groups")
        lines.append("")
    enf = [r for r in ok if r["condition"] in ("min_k_enforced", "min_k_escape") and r["n"] < r["k"] and r["valid"]
           and r["arm"] == "main"]
    if enf:
        lines += ["## What fills the forced slots (n < k)", "",
                  "| model | condition | outputs | substantive extra | placeholder | duplicate | enforcement violations |",
                  "|---|---|---|---|---|---|---|"]
        for mk in models:
            for cond in ("min_k_enforced", "min_k_escape"):
                sel = [r for r in enf if r["model_key"] == mk and r["condition"] == cond]
                if not sel:
                    continue
                slots = sum(max(0, r["n_items"] - r["n"]) for r in sel) or 1
                lines.append(f"| {mk} | {cond} | {len(sel)} | {sum(r['excess'] for r in sel) / slots:.2f} | "
                             f"{sum(r['n_placeholder'] for r in sel) / slots:.2f} | "
                             f"{sum(r['n_duplicate'] for r in sel) / slots:.2f} | "
                             f"{sum(r['enforcement_violation'] for r in sel)} |")
        lines += ["", "Shares of padded slots are rough: a slot that repeats a true item in other words counts as",
                  "substantive here. The item matcher and the hand check settle those."]
    (out / "contrasts.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwrote {out}/per_output_counts.csv, cells.csv, contrasts.md")


if __name__ == "__main__":
    main()
