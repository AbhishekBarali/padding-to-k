#!/usr/bin/env python3
"""pilot_tables.py: the pilot paper's result tables and figure data, computed from the run records.

    python analysis/pilot_tables.py --runs-dir runs --day 2026-10-15 --out paper/pilot/generated

Reuses harness/score_counts.py (the same parsing, placeholder rules and group bootstrap), so every
number in the paper's results traces back to a run folder. Writes one LaTeX fragment per table
(\\input by the paper) and summary.md with every number in plain text. Runs that are missing are
skipped and listed, so the script can be rerun as the pilot queue fills in.
"""
import argparse
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "harness"))
import common  # noqa: E402
from score_counts import Boot, expand  # noqa: E402

MAIN = ["qwen3.5-9b", "ministral-3-14b", "gemma-4-31b"]
HOSTED = ["together-qwen3.5-9b", "together-deepseek-v4.1-flash", "together-kimi-k3", "together-glm-5.3-think"]
NAME = {"qwen3.5-9b": "Qwen3.5-9B", "ministral-3-14b": "Ministral 3 14B", "gemma-4-31b": "Gemma 4 31B",
        "together-qwen3.5-9b": "Qwen3.5-9B (same weights)", "together-deepseek-v4.1-flash": "DeepSeek V4.1 Flash",
        "together-kimi-k3": "Kimi K3", "together-glm-5.3-think": "GLM-5.3, thinking on"}
CONDS = ["none", "max_k_shown", "min_k_shown", "min_k_enforced"]
CND = {c: "\\cnd{" + c.replace("_", "\\_") + "}" for c in CONDS}


def pct(x):
    return f"{100 * x:.1f}"


def ci_txt(t, scale=100, nd=1):
    """(est, lo, hi) -> '34.4 [28.1, 40.8]'."""
    if t is None:
        return "--"
    e, lo, hi = t[:3]
    return f"{scale * e:.{nd}f} [{scale * lo:.{nd}f}, {scale * hi:.{nd}f}]"


class Pilot:
    def __init__(self, runs_dir, day, boot, seed):
        self.runs_dir, self.day = Path(runs_dir), day
        self.prompts, self.docs = common.load_prompts(), common.load_documents()
        self.req = {r["request_id"]: r for r in common.load_requests()}
        self.boot = Boot(boot, seed)
        self.missing = []

    def rows(self, run_id):
        d = self.runs_dir / f"{self.day}_{run_id}"
        if not d.exists():
            self.missing.append(run_id)
            return []
        return [r for r in expand(str(d), self.prompts, self.docs, self.req) if r["status"] == "ok"]

    def strata(self, rows):
        return {r["group"]: r["set"] for r in rows}

    def ci(self, per_group, rows):
        return self.boot.ci({g: (sum(v), len(v)) for g, v in per_group.items()}, self.strata(rows))

    def rate(self, rows, pred, outcome="over_count"):
        per_group = defaultdict(list)
        for r in rows:
            if pred(r):
                per_group[r["group"]].append(float(r[outcome]))
        return (*self.ci(per_group, rows), sum(map(len, per_group.values()))) if per_group else None

    def contrast(self, rows, a, b, ks=(3, 5), outcome="over_count", keep=lambda r: True):
        """Paired a - b per (document, model, k, arm); documents with n < k."""
        val = defaultdict(dict)
        for r in rows:
            if r["n"] < r["k"] and r["k"] in ks and r["condition"] in (a, b) and keep(r):
                val[(r["doc_id"], r["model_key"], r["k"], r["arm"])][r["condition"]] = (float(r[outcome]), r["group"])
        per_group = defaultdict(list)
        for v in val.values():
            if a in v and b in v:
                per_group[v[a][1]].append(v[a][0] - v[b][0])
        return (*self.ci(per_group, rows), sum(map(len, per_group.values()))) if per_group else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs-dir", default=str(common.ROOT / "runs"))
    ap.add_argument("--day", default="2026-10-15")
    ap.add_argument("--out", default=str(common.ROOT / "paper" / "pilot" / "generated"))
    ap.add_argument("--boot", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=20261014)
    args = ap.parse_args()
    P = Pilot(args.runs_dir, args.day, args.boot, args.seed)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    lines = [f"# Pilot paper numbers ({args.day} runs, {args.boot} bootstrap draws over document groups)", ""]
    main_rows = {m: P.rows(f"{m}_pilot") for m in MAIN}
    pooled = [r for m in MAIN for r in main_rows[m]]
    ran = [m for m in MAIN if main_rows[m]]

    # 1. stop rules, pooled and per model
    rules = {}
    for name, (a, b) in {"rule1": ("min_k_shown", "none"), "rule2": ("min_k_shown", "max_k_shown")}.items():
        rules[name] = {"pooled": P.contrast(pooled, a, b), **{m: P.contrast(main_rows[m], a, b) for m in ran}}
    rule1_no_n0_emails = P.contrast(pooled, "min_k_shown", "none", keep=lambda r: not (r["set"] == "emails" and r["n"] == 0))
    lines += ["## Stop rules (points, pooled over " + ", ".join(ran) + ")"]
    for name, res in rules.items():
        lines += [f"- {name}: " + "; ".join(f"{k} {ci_txt(v)} (pairs {v[3]})" for k, v in res.items() if v)]
    lines += [f"- rule1 without the n = 0 emails: {ci_txt(rule1_no_n0_emails)}", ""]

    def decision(c):
        if c is None:
            return "--"
        return "stop" if c[2] < 0.10 else ("go" if c[1] > 0 else "caution rule")

    (out / "stoprules_rows.tex").write_text(
        f"    1. \\cnd{{min\\_k\\_shown}} $-$ \\cnd{{none}} & stop: upper $< 10$ pts; go: lower $> 0$ & "
        f"{ci_txt(rules['rule1']['pooled'])} & {decision(rules['rule1']['pooled'])} \\\\\n"
        f"    2. \\cnd{{min\\_k\\_shown}} $-$ \\cnd{{max\\_k\\_shown}} & as rule 1 & "
        f"{ci_txt(rules['rule2']['pooled'])} & {decision(rules['rule2']['pooled'])} \\\\\n", encoding="utf-8")

    # 2. conditions: over-count and exactly-k per model, condition and k (documents with n < k)
    lines += ["## Over-count % [95% CI] and exactly k entries %, documents with n < k"]
    body = []
    for c in CONDS:
        cells = []
        for m in ran:
            for k in (3, 5):
                t = P.rate(main_rows[m], lambda r: r["condition"] == c and r["k"] == k and r["n"] < k)
                ek = P.rate(main_rows[m], lambda r: r["condition"] == c and r["k"] == k and r["n"] < k, "exact_k")
                cells.append(ci_txt(t))
                lines.append(f"- {m} {c} k={k}: over-count {ci_txt(t)}; exactly k {pct(ek[0]) if ek else '--'}%"
                             f" (n = {t[3] if t else 0})")
        body.append(f"    {CND[c]} & " + " & ".join(cells) + " \\\\")
    (out / "conditions_body.tex").write_text("\n".join(body) + "\n", encoding="utf-8")
    (out / "conditions_head.tex").write_text(
        "    Condition & " + " & ".join(f"\\multicolumn{{2}}{{c}}{{{NAME[m]}}}" for m in ran) + " \\\\\n"
        "     & " + " & ".join("$k = 3$ & $k = 5$" for _ in ran) + " \\\\\n", encoding="utf-8")
    lines.append("")

    # 3. dose: mean excess against k - n in min_k_shown, per model (pgfplots coordinates)
    lines += ["## Dose: mean excess (entries) in min_k_shown against k - n"]
    plots = []
    for m in ran:
        coords = []
        for gap in (1, 2, 3, 4, 5):
            t = P.rate(main_rows[m], lambda r: r["condition"] == "min_k_shown" and r["k"] - r["n"] == gap, "excess")
            if t:
                coords.append(f"({gap},{t[0]:.3f}) += (0,{t[2] - t[0]:.3f}) -= (0,{t[0] - t[1]:.3f})")
                lines.append(f"- {m} k-n={gap}: {t[0]:.2f} [{t[1]:.2f}, {t[2]:.2f}] (n = {t[3]})")
        plots.append(f"      \\addplot+[error bars/.cd, y dir=both, y explicit] coordinates {{{' '.join(coords)}}};\n"
                     f"      \\addlegendentry{{{NAME[m]}}}")
    (out / "dose_plots.tex").write_text("\n".join(plots) + "\n", encoding="utf-8")
    # contrast 1 (dose), the same document at k = 5 against k = 3, n <= 2, outcome excess
    val = defaultdict(dict)
    for r in pooled:
        if r["condition"] == "min_k_shown" and r["n"] <= 2 and r["k"] in (3, 5):
            val[(r["doc_id"], r["model_key"])][r["k"]] = (float(r["excess"]), r["group"])
    per_group = defaultdict(list)
    for v in val.values():
        if 3 in v and 5 in v:
            per_group[v[5][1]].append(v[5][0] - v[3][0])
    dose_pooled = (*P.ci(per_group, pooled), sum(map(len, per_group.values()))) if per_group else None
    lines += [f"- contrast 1 (excess, k = 5 minus k = 3, same document, n <= 2), pooled: "
              f"{ci_txt(dose_pooled, 1, 2)} (pairs {dose_pooled[3] if dose_pooled else 0})", ""]

    # 4. the forced condition: what fills the slots the grammar forces (score_counts' shares)
    lines += ["## min_k_enforced, documents with n < k: share of padded slots"]
    forced_rows = []
    for m in ran:
        sub = [r for r in main_rows[m] if r["condition"] == "min_k_enforced" and r["n"] < r["k"] and r["valid"]]
        slots = sum(max(0, r["n_items"] - r["n"]) for r in sub)
        ph = sum(r["n_placeholder"] for r in sub)
        du = sum(r["n_duplicate"] for r in sub)
        ex = sum(r["excess"] for r in sub)
        cut = sum(1 for r in main_rows[m] if r["condition"] == "min_k_enforced" and r["truncated"])
        if slots:
            lines.append(f"- {m}: {slots} padded slots; substantive extra {ex / slots:.2f}, placeholder {ph / slots:.2f}, "
                         f"repeat {du / slots:.2f}; outputs cut at the token cap: {cut}")
            forced_rows.append(f"    {NAME[m]} & {pct(ex / slots)} & {pct(ph / slots)} & {pct(du / slots)} & {cut} \\\\")
    (out / "forced_rows.tex").write_text("\n".join(forced_rows) + "\n", encoding="utf-8")
    lines.append("")

    # 5. per model, local and hosted: rules 1 and 2, unreadable share
    lines += ["## Per model: rule 1, rule 2 (points), unreadable %"]
    model_rows = []
    for m in ran + HOSTED:
        rows = main_rows[m] if m in main_rows else P.rows(f"{m}_pilot")
        if not rows:
            continue
        r1, r2 = P.contrast(rows, "min_k_shown", "none"), P.contrast(rows, "min_k_shown", "max_k_shown")
        unread = sum(1 for r in rows if not r["valid"]) / len(rows)
        lines.append(f"- {m}: rule1 {ci_txt(r1)}; rule2 {ci_txt(r2)}; unreadable {pct(unread)}% of {len(rows)}")
        model_rows.append((m, f"    {NAME[m]} & {ci_txt(r1)} & {ci_txt(r2)} & {pct(unread)} \\\\"))
    (out / "models_local.tex").write_text("\n".join(t for m, t in model_rows if m in MAIN) + "\n", encoding="utf-8")
    (out / "models_hosted.tex").write_text("\n".join(t for m, t in model_rows if m in HOSTED) + "\n", encoding="utf-8")
    lines.append("")

    # 6. exploratory: robustness arms, sampling, thinking
    lines += ["## Exploratory"]
    expl = []
    rob = {m: P.rows(f"{m}_robustness") for m in ran}
    for arm in ("block_llamaindex", "base_neutral"):
        rr = [r for m in ran for r in rob[m] if r["arm"] == arm]
        if rr:
            r1 = P.contrast(rr, "min_k_shown", "none")
            r2 = P.contrast(rr, "min_k_shown", "max_k_shown")
            lines.append(f"- robustness {arm}: rule1 {ci_txt(r1)} (main {ci_txt(rules['rule1']['pooled'])}); "
                         f"rule2 {ci_txt(r2)} (main {ci_txt(rules['rule2']['pooled'])})")
            expl.append(f"    Arm \\texttt{{{arm.replace('_', chr(92) + '_')}}}: rule 1, rule 2 & {ci_txt(r1)}; {ci_txt(r2)} \\\\")
    for base, label in (("qwen3.5-9b", "Qwen3.5-9B"), ("gemma-4-31b", "Gemma 4 31B")):
        seeds = [P.rows(f"{base}-sampled_pilot_s{s}") for s in (1, 2, 3)]
        got = [s for s in seeds if s]
        if got:
            r1s = [P.contrast(s, "min_k_shown", "none") for s in got]
            lines.append(f"- {base} sampled, rule1 per seed: " + "; ".join(ci_txt(t) for t in r1s)
                         + f" (greedy {ci_txt(rules['rule1'].get(base))})")
            expl.append(f"    {label}, sampled ({len(got)} seeds): rule 1 & " + "; ".join(ci_txt(t) for t in r1s) + " \\\\")
    for base, label, n_seeds in (("qwen3.5-9b", "Qwen3.5-9B", 3), ("gemma-4-31b", "Gemma 4 31B", 1)):
        think = [P.rows(f"{base}-think_pilot_s{s}") for s in range(1, n_seeds + 1)]
        off = ([P.rows(f"{base}-nothink_pilot_s{s}") for s in range(1, n_seeds + 1)] if base == "qwen3.5-9b"
               else [P.rows(f"{base}-sampled_pilot_s1")])
        for s, (t_rows, o_rows) in enumerate(zip(think, off), 1):
            if t_rows and o_rows:
                ton = P.rate(t_rows, lambda r: r["condition"] == "min_k_shown" and r["n"] < r["k"])
                tof = P.rate(o_rows, lambda r: r["condition"] == "min_k_shown" and r["n"] < r["k"])
                r1on, r1off = P.contrast(t_rows, "min_k_shown", "none"), P.contrast(o_rows, "min_k_shown", "none")
                lines.append(f"- {base} thinking seed {s}: min_k_shown over-count on {ci_txt(ton)} vs off {ci_txt(tof)}; "
                             f"rule1 on {ci_txt(r1on)} vs off {ci_txt(r1off)}")
                expl.append(f"    {label}, thinking on / off (seed {s}): \\cnd{{min\\_k\\_shown}} over-count "
                            f"& {ci_txt(ton)} / {ci_txt(tof)} \\\\")
    (out / "exploratory_rows.tex").write_text("\n".join(expl) + "\n", encoding="utf-8")
    lines += ["", "Missing runs (skipped): " + (", ".join(P.missing) or "none")]
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
