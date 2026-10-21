#!/usr/bin/env python3
"""without_08b.py (post hoc): the headline numbers on the seven GPU models other than Qwen3.5-0.8B.

Qwen3.5-0.8B writes 36.6% unreadable outputs, which the frozen rules score as 0 entries. This reruns the
main contrast (C2, length and over-count) and the over-count shares under no count, a shown minimum and an
enforced minimum without it, with the registered bootstrap (10,000 draws over document groups within set).

    python analysis/posthoc/without_08b.py [--scored <folder of *.outputs.csv.gz>] [--boot 10000]

Writes analysis/posthoc/out/without_08b.md.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
import full_study as fs  # noqa: E402

DROP = "qwen3.5-0.8b"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scored", default=str(fs.CACHE))
    ap.add_argument("--boot", type=int, default=10000)
    a = ap.parse_args()

    df, _ = fs.load_scored(a.scored)
    df = fs.add_doc_fields(df, fs.doc_table())
    main_models = [m for m in fs.NAME if not m.startswith(("together-", "bedrock-"))]
    df = df[(df["kind"] == "full") & (df["arm"] == "main") & df["model_key"].isin(main_models)]
    boot = fs.Bootstrap(a.boot)

    lines = ["# Post hoc: headline numbers without Qwen3.5-0.8B", "",
             "Documents with n < k, k = 3 and 5; 95%% intervals from %d draws over document groups within set." % a.boot, "",
             "| models | C2 length (entries) | C2 over-count (points) | over-count %, none | min_k_shown | min_k_enforced |",
             "|---|---|---|---|---|---|"]
    for label, f in (("8 GPU models (registered)", df), ("7 GPU models, without Qwen3.5-0.8B", df[df.model_key != DROP])):
        f = f.copy()
        f["model_key"] = f["model_key"].cat.remove_unused_categories()
        c2 = boot.mean(fs.contrast_pairs(f, "C2"))
        c2o = boot.mean(fs.contrast_pairs(f, "C2", outcome="over_count"))
        lt = f[f["ok"] & (f["n"] < f["k"]) & f["k"].isin((3, 5))]
        share = {c: 100 * lt.loc[lt.condition == c, "over_count"].mean() for c in ("none", "min_k_shown", "min_k_enforced")}
        lines.append("| %s | %+.2f [%+.2f, %+.2f] | %+.1f [%+.1f, %+.1f] | %.1f | %.1f | %.1f |" % (
            label, c2["est"], c2["lo"], c2["hi"], 100 * c2o["est"], 100 * c2o["lo"], 100 * c2o["hi"],
            share["none"], share["min_k_shown"], share["min_k_enforced"]))
    out = ROOT / "analysis" / "posthoc" / "out" / "without_08b.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
