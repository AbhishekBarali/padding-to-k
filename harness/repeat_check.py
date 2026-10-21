#!/usr/bin/env python3
"""repeat_check.py: how often does the same prompt give a different answer?

    python harness/run.py plan --model qwen3.5-9b --repeat-of runs/<full run> --run-id <full run>-repeat
    python harness/run.py go runs/<full run>-repeat --base-url ... --server-info ...
    python harness/repeat_check.py runs/<full run> runs/<full run>-repeat

Compares every request present in both runs (same model): the share of identical outputs, and how
often the over-count verdict flips. Greedy decoding with batch-invariant mode should give 100%
identical; models that cannot use batch-invariant mode (Qwen3.5, Nemotron-H in vLLM v0.31.0) may
not. The flip rate goes into the paper's repeat-run table (data/results_template/table_repeat_runs.csv).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
from score_counts import latest_records  # noqa: E402


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    a_dir, b_dir = Path(sys.argv[1]), Path(sys.argv[2])
    ma = json.loads((a_dir / "manifest.json").read_text())
    mb = json.loads((b_dir / "manifest.json").read_text())
    if ma["model_key"] != mb["model_key"]:
        sys.exit("the two runs are of different models")
    a, b = latest_records(a_dir), latest_records(b_dir)
    prompts, docs = common.load_prompts(), common.load_documents()
    shared = sorted(i for i in a if i in b and a[i]["status"] == "ok" and b[i]["status"] == "ok")
    if not shared:
        sys.exit("no request has an ok output in both runs")
    same = flips = 0
    for i in shared:
        same += a[i].get("content") == b[i].get("content")
        field = prompts["lists"][a[i]["schema_id"].split("|")[0]]["field"]
        text, n = docs[a[i]["doc_id"]]["text"], a[i]["n"]

        def over(rec):
            items = common.parse_output(rec.get("content"), field)["items"]
            return items is not None and common.count_items(items, "N/A", text)["n_substantive"] > n
        flips += over(a[i]) != over(b[i])
    print(f"model {ma['model_key']}: {len(shared)} prompts in both runs; identical outputs "
          f"{same} ({100 * same / len(shared):.1f}%); over-count verdict flips {flips} "
          f"({100 * flips / len(shared):.2f}%)")
    print("CSV row for table_repeat_runs.csv:")
    print(f"{ma['model_key']},{ma['model'].get('backend')},{len(shared)},2,{same / len(shared):.4f},{flips},"
          f"batch_invariant={(ma['model'].get('env') or {}).get('VLLM_BATCH_INVARIANT', 'default')}")


if __name__ == "__main__":
    main()
