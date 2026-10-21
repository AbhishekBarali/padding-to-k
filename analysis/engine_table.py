#!/usr/bin/env python3
"""engine_table.py: the engine-test table of the pilot paper (Table 1), read from runs/enforce/.

    python3 analysis/engine_table.py [--out analysis/pilot]

One row per model and serving stack, from the engine test that decided it (RUNS below, with the reason for
each choice). Columns: minItems 3 and 5 met under the grammar (E02, E03); maxItems respected (E04 to E06, a
closed list); reasoning seen on the replies sent with a grammar and on those sent without one; and how many
of 5 repeats of a study request came back identical (E14 against E10a). Writes engine_tests.md (every row,
with the folder) and engine_tests.tex (the table body for the paper).
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENF = ROOT / "runs" / "enforce"

# (label, folder, in study?, note). The folder is the last test under the settings the study uses.
RUNS = [
    ("GPU", "Qwen3.5-0.8B", "qwen3.5-0.8b-20261014T144126Z", True, ""),
    ("GPU", "Qwen3.5-2B", "qwen3.5-2b-20261014T153302Z", True, "rerun after the parse-ladder fix"),
    ("GPU", "Qwen3.5-9B", "qwen3.5-9b-20261014T153000Z", True, "the xgrammar control of the llguidance test"),
    ("GPU", "Qwen3.5-27B", "qwen3.5-27b-20261014T145016Z", True, ""),
    ("GPU", "Gemma 4 31B", "gemma-4-31b-20261014T143023Z", True, "as configured, with the reasoning parser"),
    ("GPU", "Ministral 3 14B", "ministral-3-14b-20261014T141128Z", True, ""),
    ("GPU", "OLMo 3.1 32B", "olmo-3.1-32b-20261014T181319Z", True, "with the template copy, from models.yaml"),
    ("GPU", "gpt-oss-20b", "gpt-oss-20b-20261014T181628Z", True, "batch invariance off, from models.yaml"),
    ("GPU", "gpt-oss-120b", "gpt-oss-120b-20261014T162209Z", False, "out"),
    ("GPU", "Qwen3.5-9B, thinking", "qwen3.5-9b-think-20261014T190852Z", True, "card sampling, 81,920 tokens"),
    ("GPU", "Gemma 4 31B, thinking", "gemma-4-31b-think-20261014T191647Z", True, "card sampling, 81,920 tokens"),
    ("Together", "Qwen3.5-9B", "together-qwen3.5-9b-20261014T185700Z", True, "re-test under the tightened rules"),
    ("Together", "DeepSeek V4.1 Flash", "together-deepseek-v4.1-flash-20261014T173556Z", True, "forced comparison"),
    ("Together", "Kimi K3", "together-kimi-k3-20261014T134950Z", True, "prompt-side conditions only"),
    ("Together", "GLM-5.3, thinking", "together-glm-5.3-think-20261014T173600Z", True, "prompt-side conditions only"),
    ("Together", "GLM-5.3", "together-glm-5.3-20261014T134943Z", False, "out: thinking not reliably off"),
    ("Together", "DeepSeek V4 Pro", "together-deepseek-v4-pro-20261014T135156Z", False, "out"),
    ("Together", "DeepSeek V4 Pro, thinking", "together-deepseek-v4-pro-think-20261014T173602Z", False, "out"),
    ("Together", "Llama 3.3 70B", "together-llama-3.3-70b-20261014T135410Z", False, "fallback, not used"),
    ("Together", "Muse Glimmer 30B", "together-muse-glimmer-30b-20261014T173554Z", False, "out"),
    ("Together", "gpt-oss-120b", "together-gpt-oss-120b-20261014T173558Z", False, "out"),
    ("Together", "Qwen3.5-9B, thinking", "together-qwen3.5-9b-think-20261014T173604Z", False, "out"),
]
GRAMMAR_FREE = {"E12a", "E12b", "E16a"}     # sent without a response_format
SKIP = {"E07"}                              # an unsatisfiable schema the server should reject


def cell(rec):
    if rec is None:
        return "-"
    if str(rec.get("verdict", "")).startswith("HTTP"):
        return rec["verdict"]
    if rec.get("http_status") is None:
        return "timeout"                     # no reply within the client timeout (600 s): still generating
    return ("yes" if rec["verdict"] == "PASS" else "no") + f" ({rec.get('n_items')})"


def row(folder):
    recs = {}
    for line in (ENF / folder / "raw.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            recs[r["test"]] = r
    maxs = [recs.get(t) for t in ("E04", "E05", "E06")]
    if all(m is not None and m["verdict"] == "PASS" for m in maxs):
        mx = "yes"
    else:
        mx = "no: " + ", ".join(t + (" (timeout)" if m is not None and m.get("http_status") is None else "")
                                for t, m in zip(("E04", "E05", "E06"), maxs) if m is None or m["verdict"] != "PASS")
    with_g = [r for t, r in recs.items() if t not in GRAMMAR_FREE | SKIP and r.get("http_status") == 200]
    without_g = [r for t, r in recs.items() if t in GRAMMAR_FREE and r.get("http_status") == 200]
    reason = lambda rs: f"{sum(1 for r in rs if r.get('reasoning_content'))}/{len(rs)}"   # noqa: E731
    base = recs.get("E10a")
    reps = [recs.get(f"E14-{i}") for i in range(5)]
    same = sum(1 for r in reps if r is not None and base is not None and base.get("content") is not None
               and r.get("content") == base.get("content"))
    return {"ge3": cell(recs.get("E02")), "ge5": cell(recs.get("E03")), "max": mx,
            "reason_grammar": reason(with_g), "reason_free": reason(without_g), "rep": f"{same}/5"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "analysis" / "pilot"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    md = ["# Engine test, one row per model and stack (from runs/enforce/)", "",
          "minItems 3 / 5 met under the grammar (E02, E03; entries returned in brackets); maxItems respected (E04 to",
          "E06); reasoning seen on replies sent with a grammar / without one; identical repeats of a study request (E14).",
          "", "| stack | model | in study | >= 3 | >= 5 | max | reasoning, grammar | reasoning, none | repeats | folder | note |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    tex = ["% generated by analysis/engine_table.py from runs/enforce/; do not edit by hand"]
    for stack, label, folder, study, note in RUNS:
        r = row(folder)
        md.append(f"| {stack} | {label} | {'yes' if study else 'no'} | {r['ge3']} | {r['ge5']} | {r['max']} | "
                  f"{r['reason_grammar']} | {r['reason_free']} | {r['rep']} | `{folder}` | {note} |")
        if study:
            tex.append(f"{stack}: {label} & {r['ge3']} & {r['ge5']} & {r['max'].replace(': ', ' ')} & "
                       f"{r['reason_grammar']} & {r['rep']} \\\\")
    md += ["", "Not tested: Qwen3.5-397B, Gemma 4 31B and Nemotron 3 Ultra on Together answer HTTP 400 "
           "(not serverless; `runs/enforce/together-*-20261014T1354*Z`).", ""]
    (out / "engine_tests.md").write_text("\n".join(md), encoding="utf-8")
    (out / "engine_tests.tex").write_text("\n".join(tex) + "\n\\bottomrule\n", encoding="utf-8")
    print(f"wrote {out / 'engine_tests.md'} and engine_tests.tex ({len(RUNS)} rows)")


if __name__ == "__main__":
    main()
