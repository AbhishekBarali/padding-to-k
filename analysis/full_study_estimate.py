#!/usr/bin/env python3
"""full_study_estimate.py: projected hosted cost and GPU time of the full study, and a check of its spending caps.

    python analysis/full_study_estimate.py        writes analysis/full_study_estimate.md
    python analysis/full_study_estimate.py check  only checks the caps in configs/models.yaml (exit 1 if one fails)

Hosted cost: tokens per request measured on the cost test of 18 Oct (runs/costtest_2026-10-18_*: the same 50
pilot requests per Bedrock model, none and min_k_shown at k = 3 and 5), times the number of sends of each job in
configs/models.yaml (full_study), times each model's price there (Flex tier where it applies). Together:
tokens per request from its pilot runs (15 Oct). The re-ask arm: the share of min_k_shown replies shorter than k
in the cost test, times the 1,674 min_k_shown requests of a full run, at the cost per re-asked reply measured in
the cost test's -reask1 runs.

Caps: every hosted job's `max_usd` (the `go --max-usd` the queue sends) must be at least 1.5 times its projection,
and the caps of one provider, plus what that provider has already cost, must stay under its cap.

GPU time: requests per second measured on the pilot (15 Oct, one RTX PRO 6000, 32 workers) for the three
pilot models and the thinking arms; the five other models are scaled from the pilot models by their
single-request decoding speed in the engine test of 14 Oct (runs/enforce/), so their rows are estimates, and
a slow column halves every rate. Server start-up from runs/servers/*.json (seconds_to_healthy).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "harness"))
import run  # noqa: E402

# sends per job, from `run.py plan` (checked on 18 Oct)
SENDS_FULL_GPU = 25668          # --scope full, every condition (Together too)
SENDS_FULL_PROMPT_SIDE = 22320  # --scope full on a Bedrock model: the prompt-side conditions with min_k_shown_fewer_ok
SENDS_PILOT_PROMPT_SIDE = 2400  # --scope custom --splits pilot on a Bedrock model
SENDS_THINK_ALL_DOCS = 3906     # the thinking filters (--splits pilot full, 4 conditions, k = 3 and 5), per seed
SENDS_THINK_PILOT = 420         # the same filters on the pilot documents only, per seed (the pilot's thinking runs)
SENDS_DEV = 2184
SENDS_REPEAT = 300
MIN_K_SHOWN_FULL = 1674         # min_k_shown requests in a full run (the re-ask arm's pool)
CAP_FACTOR = 1.5
TOGETHER_PILOT = {"together-deepseek-v4.1-flash": (539, 67, "2026-10-15_together-deepseek-v4.1-flash_pilot"),
                  "together-qwen3.5-9b": (582, 60, "2026-10-15_together-qwen3.5-9b_pilot")}

# GPU requests per second at 32 workers. Measured: the pilot robustness runs (840 sends, the larger runs) and
# the thinking pilots (one seed of 420 each; the sessions of 15 Oct start 18 minutes apart for Qwen3.5-9B).
# Scaled: single-request tokens per second in the engine test relative to qwen3.5-9b (73) and gemma-4-31b
# (10); gpt-oss-20b also writes about 3.4 times the tokens (206 vs 60, Bedrock cost test).
GPU_RATE = {
    "qwen3.5-9b": (20.0, "measured: 2026-10-15_qwen3.5-9b_robustness, 840 in 0.7 min"),
    "gemma-4-31b": (3.4, "measured: 2026-10-15_gemma-4-31b_robustness, 840 in 4.1 min"),
    "ministral-3-14b": (6.1, "measured: 2026-10-15_ministral-3-14b_robustness, 840 in 2.3 min"),
    "qwen3.5-0.8b": (20.0, "scaled: taken as qwen3.5-9b (its own engine-test speed is 4x; the harness, not the GPU, is the limit there)"),
    "qwen3.5-2b": (20.0, "scaled: as qwen3.5-0.8b"),
    "qwen3.5-27b": (6.3, "scaled: 23 / 73 of qwen3.5-9b (engine test)"),
    "olmo-3.1-32b": (3.4, "scaled: same engine-test speed as gemma-4-31b (10 tokens/s)"),
    "gpt-oss-20b": (10.8, "scaled: 135 / 73 of qwen3.5-9b, times 60 / 206 for its longer replies"),
    "qwen3.5-9b-think": (0.387, "measured: 2026-10-15_qwen3.5-9b-think_pilot_s1, 420 in about 18 min"),
    "qwen3.5-9b-nothink": (17.5, "measured: 2026-10-15_qwen3.5-9b-nothink_pilot_s1, 420 in 0.4 min"),
    "qwen3.5-9b-think-pp0": (0.387, "taken as qwen3.5-9b-think (not measured; without the penalty it may think longer)"),
    "qwen3.5-9b-nothink-pp0": (17.5, "taken as qwen3.5-9b-nothink"),
    "gemma-4-31b-think": (0.0775, "measured: 2026-10-15_gemma-4-31b-think_pilot_s1, 420 in 90.3 min"),
    "gemma-4-31b-sampled": (3.0, "measured: 2026-10-15_gemma-4-31b-sampled_pilot_s1, 420 in 2.4 min"),
}
STARTUP_S = {"qwen3.5-0.8b": 176, "qwen3.5-2b": 176, "qwen3.5-9b": 236, "qwen3.5-27b": 351, "gemma-4-31b": 347,
             "olmo-3.1-32b": 371, "ministral-3-14b": 226, "gpt-oss-20b": 201, "qwen3.5-9b-think": 236,
             "qwen3.5-9b-nothink": 171, "qwen3.5-9b-think-pp0": 236, "qwen3.5-9b-nothink-pp0": 171,
             "gemma-4-31b-think": 301, "gemma-4-31b-sampled": 347}


def lineup():
    return run.yaml.safe_load((ROOT / "configs" / "models.yaml").read_text())["full_study"]


def costtest():
    """Per Bedrock model key: tokens and USD per request in the cost test, and the re-ask arm's numbers."""
    rows, prompts = {}, run.common.load_prompts()
    for d in sorted((ROOT / "runs").glob("costtest_2026-10-18_*")):
        man = json.loads((d / "manifest.json").read_text())
        key, price = man["model_key"], man["model"]["price"]
        recs = [r for r in run.run_records(d) if r["status"] == "ok"]
        usd = run.run_cost(d, price)[0]
        if d.name.endswith("-reask1"):
            rows.setdefault(key, {})["reask_per"] = usd / len(recs)
            continue
        shown = [r for r in recs if r["condition"] == "min_k_shown"]
        short = 0
        for r in shown:
            items = run.common.parse_output(r["content"], prompts["lists"][r["schema_id"].split("|")[0]]["field"])["items"]
            short += items is not None and len(items) < r["k"]
        rows.setdefault(key, {}).update({
            "n": len(recs), "price": price, "test_usd": usd, "per": usd / len(recs),
            "in": sum(r["usage"]["prompt_tokens"] for r in recs) / len(recs),
            "out": sum(r["usage"]["completion_tokens"] for r in recs) / len(recs),
            "reasoning": sum(((r["usage"].get("completion_tokens_details") or {}).get("reasoning_tokens") or 0)
                             for r in recs) / len(recs),
            "short_share": short / len(shown) if shown else 0.0})
    return rows


def hosted_jobs(fs, models, ct):
    """Every hosted job of the queue: (provider, label, model key, sends, projected USD, max_usd)."""
    jobs = []
    for key, c in fs["together"]["models"].items():
        tin, tout, _ = TOGETHER_PILOT[key]
        p = models[key]["price"]
        per = (tin * p["in"] + tout * p["out"]) / 1e6
        jobs.append(("together", "full", key, SENDS_FULL_GPU, per * SENDS_FULL_GPU, c["max_usd"]))
        jobs.append(("together", "repeat", key, SENDS_REPEAT, per * SENDS_REPEAT, c["repeat_max_usd"]))
    for key, c in fs["bedrock"]["models"].items():
        per = ct[key]["per"]
        jobs.append(("bedrock", "full", key, SENDS_FULL_PROMPT_SIDE, per * SENDS_FULL_PROMPT_SIDE, c["max_usd"]))
        jobs.append(("bedrock", "repeat", key, SENDS_REPEAT, per * SENDS_REPEAT, c["repeat_max_usd"]))
    kt = fs["bedrock"]["kimi_k3_thinking"]
    sends = SENDS_PILOT_PROMPT_SIDE if kt["documents"] == "pilot" else SENDS_FULL_PROMPT_SIDE
    jobs.append(("bedrock", f"thinking on, {kt['documents']} documents", kt["key"], sends,
                 ct[kt["key"]]["per"] * sends, kt["max_usd"]))
    for key, cap in fs["bedrock"]["retry_arm"].items():
        n = round(ct[key]["short_share"] * MIN_K_SHOWN_FULL)
        jobs.append(("bedrock", "re-ask arm", key, n, n * ct[key]["reask_per"], cap))
    return jobs


def check_caps(fs, jobs, ct):
    """Problems with the caps, as text lines (empty when all hold)."""
    bad = [f"{prov} {label} {key}: max_usd {cap} is under {CAP_FACTOR} x the projected {usd:.2f} USD"
           for prov, label, key, _, usd, cap in jobs if cap < CAP_FACTOR * usd]
    spent = {"together": fs["together"]["spent_usd"], "bedrock": fs["bedrock"]["spent_usd"]}
    measured = sum(run.run_cost(d, json.loads((d / "manifest.json").read_text())["model"]["price"])[0]
                   for d in (ROOT / "runs").glob("costtest_2026-10-18_*"))
    if spent["bedrock"] < measured - 0.005:
        bad.append(f"bedrock: spent_usd {spent['bedrock']} is less than the cost test's {measured:.2f} USD")
    for prov in ("together", "bedrock"):
        caps = sum(j[5] for j in jobs if j[0] == prov)
        if caps + spent[prov] > fs[prov]["cap_usd"]:
            bad.append(f"{prov}: caps {caps:.2f} + spent {spent[prov]:.2f} USD pass the {fs[prov]['cap_usd']} USD cap")
    return bad


def gpu_jobs(fs):
    jobs = []
    for m in fs["gpu"]["main"]:
        jobs.append(("full grid + repeat check", m, SENDS_FULL_GPU + SENDS_REPEAT))
    for m in fs["gpu"]["dev_set"]:
        jobs.append(("dev set", m, SENDS_DEV))
    for pair in fs["gpu"]["thinking_pairs"]:
        n = len(pair["request_seeds"])
        docs = pair.get("documents", "all")
        sends = SENDS_THINK_PILOT if docs == "pilot" else SENDS_THINK_ALL_DOCS
        for key in (pair["think"], pair["partner"]):
            jobs.append((f"thinking pair, {docs} documents, {n} seed{'s' if n > 1 else ''}", key, sends * n))
    return jobs


def main():
    _, models = run.load_models()
    fs = lineup()
    ct = costtest()
    jobs = hosted_jobs(fs, models, ct)
    bad = check_caps(fs, jobs, ct)
    if sys.argv[1:] == ["check"]:
        print("\n".join(bad) or "caps ok")
        sys.exit(1 if bad else 0)

    out = ["# Full study: projected hosted cost and GPU time", "",
           "Written by `python analysis/full_study_estimate.py`. Every number below comes from the cost test of",
           "18 Oct (`runs/costtest_2026-10-18_*`), the pilot runs of 15 Oct (branch `pilot-runs`) and the prices in",
           "`configs/models.yaml` (read from aws.amazon.com/bedrock/pricing and docs.together.ai on 18 Oct). The",
           "queue that runs it all is `harness/full_study_queue.py`.", ""]

    # ---- Bedrock per-model table (cost test)
    bed = fs["bedrock"]
    out += ["## Bedrock (credits, cap 300 USD; a model is dropped only if the total passes 280 USD)", "",
            f"Full run per model: {SENDS_FULL_PROMPT_SIDE:,} sends (the five prompt-side conditions and "
            f"min_k_shown_fewer_ok on all 558 documents) plus the {SENDS_REPEAT}-prompt repeat check. Flex tier on every "
            "model (one request each on 18 Oct came back with `service_tier: flex`, and so did all 50 of each cost "
            "test); DeepSeek v3.2 is counted at the Standard price because the pricing page lists no Flex price for it. "
            "gpt-oss reports no reasoning count: its reasoning is the <reasoning> block at the start of the content, "
            "billed in its completion tokens.", "",
            "| Model | Test replies | Prompt tokens / request | Completion tokens / request | of which reasoning | "
            "Price in / out (USD per M) | Tier | Projected USD | --max-usd (full + repeat) |", "|---|---|---|---|---|---|---|---|---|"]
    proj = {(j[0], j[1], j[2]): j for j in jobs}
    total = 0.0
    for key, c in bed["models"].items():
        r = ct[key]
        usd = proj[("bedrock", "full", key)][4] + proj[("bedrock", "repeat", key)][4]
        total += usd
        out.append(f"| {key} | {r['n']} | {r['in']:.0f} | {r['out']:.0f} | {r['reasoning']:.0f} | {r['price']['in']} / "
                   f"{r['price']['out']} | {r['price'].get('tier')} | {usd:.2f} | {c['max_usd']} + {c['repeat_max_usd']} |")
    kt = bed["kimi_k3_thinking"]
    r = ct[kt["key"]]
    think_all = r["per"] * (SENDS_FULL_PROMPT_SIDE + SENDS_REPEAT)
    think_pilot = r["per"] * SENDS_PILOT_PROMPT_SIDE
    think = think_pilot if kt["documents"] == "pilot" else think_all
    out.append(f"| {kt['key']} ({kt['documents']} documents) | {r['n']} | {r['in']:.0f} | {r['out']:.0f} | "
               f"{r['reasoning']:.0f} | {r['price']['in']} / {r['price']['out']} | {r['price'].get('tier')} | "
               f"{think:.2f} | {kt['max_usd']} |")
    reask = [j for j in jobs if j[1] == "re-ask arm"]
    for prov, label, key, n, usd, cap in reask:
        out.append(f"| {key}, re-ask arm (about {n} replies) | {ct[key]['n']} | | | | | flex | {usd:.2f} | {cap} |")
    reask_usd = sum(j[4] for j in reask)
    grand = total + think + reask_usd
    caps = sum(j[5] for j in jobs if j[0] == "bedrock")
    out += ["", f"Seven models, full run and repeat check: **{total:.2f} USD**. Kimi K3 with thinking on would cost "
            f"{think_all:.2f} USD on every prompt-side request ({total + think_all + reask_usd:.2f} USD in all, past "
            f"{bed['drop_above_usd']}), so it runs on the pilot documents: {think_pilot:.2f} USD. With the re-ask arm "
            f"({reask_usd:.2f} USD): **Bedrock total {grand:.2f} USD** of the {bed['cap_usd']} USD cap, plus "
            f"{bed['spent_usd']} USD already spent on the cost test. No model is dropped.", "",
            f"Caps: each job stops at about twice its projection; the caps add up to {caps:.2f} USD, so with the "
            f"{bed['spent_usd']} USD spent even every job running to its cap stays under {bed['cap_usd']} USD. The test "
            "used only none and min_k_shown; the five prose wordings ask for the same lists, so their replies should be "
            f"of the same length, and a {CAP_FACTOR}x margin on every row would still keep the total at "
            f"{CAP_FACTOR * grand:.0f} USD.", ""]

    # ---- Together
    tg = fs["together"]
    out += [f"## Together (cash, {tg['cap_usd']} USD in total, {tg['spent_usd']} USD spent by the pilot)", "",
            f"Full run per model: {SENDS_FULL_GPU:,} sends (every condition, min_k_enforced and min_k_escape included: "
            "both models force the count in the 14 Oct engine test) plus the repeat check.", "",
            "| Model | Prompt / completion tokens per request (pilot) | Price in / out | Projected USD | --max-usd (full + repeat) |",
            "|---|---|---|---|---|"]
    tg_total = 0.0
    for key, c in tg["models"].items():
        tin, tout, src = TOGETHER_PILOT[key]
        p = models[key]["price"]
        usd = proj[("together", "full", key)][4] + proj[("together", "repeat", key)][4]
        tg_total += usd
        out.append(f"| {key} | {tin} / {tout} (`{src}`) | {p['in']} / {p['out']} | {usd:.2f} | "
                   f"{c['max_usd']} + {c['repeat_max_usd']} |")
    tg_caps = sum(j[5] for j in jobs if j[0] == "together")
    out += ["", f"Together total {tg_total:.2f} USD; with the pilot's {tg['spent_usd']} USD, **{tg_total + tg['spent_usd']:.2f} "
            f"USD of {tg['cap_usd']}**. Caps add up to {tg_caps:.2f} USD ({tg_caps + tg['spent_usd']:.2f} with the pilot).", ""]

    # ---- GPU
    out += ["## GPU queue (one RTX PRO 6000)", "",
            "| Job | Model | Sends | Requests / s | Hours | Hours if half as fast | Rate from |", "|---|---|---|---|---|---|---|"]
    hours = 0.0
    servers = set()
    for what, key, sends in gpu_jobs(fs):
        rate, src = GPU_RATE[key]
        h = sends / rate / 3600
        hours += h
        servers.add(key)
        out.append(f"| {what} | {key} | {sends:,} | {rate:g} | {h:.2f} | {2 * h:.2f} | {src} |")
    # one server per model, plus a second start for each main model's repeat check (on a new server, as in the pilot)
    starts = sorted(servers) + list(fs["gpu"]["main"])
    start = sum(STARTUP_S[k] for k in starts) / 3600
    extra = 1.0   # the re-ask arm on three models (a few hundred sends each), restarts
    gem = SENDS_THINK_ALL_DOCS / GPU_RATE["gemma-4-31b-think"][0] / 3600
    qth = 3 * SENDS_THINK_ALL_DOCS / GPU_RATE["qwen3.5-9b-think"][0] / 3600
    out += ["", f"Generation {hours:.1f} h (slow column {2 * hours:.1f} h), server start-ups {start:.1f} h "
            f"({len(starts)} starts at their measured seconds_to_healthy), and about {extra:.0f} h for the re-ask arm "
            "and restarts. The teacher-forced pass is not in the queue (it runs with the mechanism figure).", "",
            f"**GPU total: about {hours + start + extra:.0f} hours ({2 * hours + start + extra:.0f} if every rate is half "
            f"as fast).** The thinking-on arms are most of it: Gemma 4 31B thinking {gem:.1f} h, Qwen3.5-9B thinking "
            f"{qth:.1f} h for its three seeds. Its presence-penalty-0 rerun runs on the pilot documents only, so it adds "
            "about 1 h, but it may think longer without the penalty, so that row is the least certain.", ""]
    if bad:
        out += ["## Cap problems", ""] + [f"- {b}" for b in bad] + [""]
    (ROOT / "analysis" / "full_study_estimate.md").write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out))


if __name__ == "__main__":
    main()
