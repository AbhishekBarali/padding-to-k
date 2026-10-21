#!/usr/bin/env python3
"""full_study_queue.py: the full study as one ordered queue of jobs, built from `full_study` in configs/models.yaml.

    python harness/full_study_queue.py list [--section gpu|together|bedrock]     print every job and its commands
    python harness/full_study_queue.py run --section bedrock [--from N] [--only N]  run the jobs of one section in order

Sections are independent and can run side by side: `gpu` on the GPU machine, `together` and `bedrock` from
any machine with the key in the environment (TOGETHER_API_KEY; AWS_BEARER_TOKEN_BEDROCK, e.g.
`set -a; . ~/.config/padk/bedrock.env; set +a`). Every run id is fixed (fs_<model>_<what>), so `run` can be
started again after a stop: `plan` is skipped for a run that already has its planned.jsonl, and `go` sends only
what has no result yet.

Hosted jobs carry their `go --max-usd` from models.yaml (analysis/full_study_estimate.py check verifies that
every cap is at least 1.5 times its projection and that the caps of one provider stay under its cap). A run that
reaches its cap stops sending (exit code 3); the queue then stops and says so, and the run can be continued with a
higher cap by hand.

GPU: one server per model (harness/serve.py up / down), the full grid, the re-ask arm where listed and the dev set
on that server; then the repeat check on a newly started server, as in the pilot. Thinking pairs send each request
seed as its own run, with a 3,600-second client timeout. If a GPU job stops half-way, `python harness/serve.py down
<model>` before running it again (its first step starts the server).
"""
import argparse
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
RUN, SERVE, RETRY = "harness/run.py", "harness/serve.py", "harness/retry_arm.py"
LOCAL = "http://127.0.0.1:8000/v1"
SERVER_INFO = "@server"       # replaced at run time by the newest runs/servers/<model>-*.json


def lineup():
    return yaml.safe_load((ROOT / "configs" / "models.yaml").read_text())["full_study"]


def plan(model, run_id, *filters):
    return ["plan", run_id, [PY, RUN, "plan", "--model", model, "--run-id", run_id, *filters]]


def go(run_id, *opts):
    return ["go", run_id, [PY, RUN, "go", f"runs/{run_id}", *opts]]


def gpu_jobs(fs):
    g, jobs = fs["gpu"], []
    w = ["--workers", str(g["workers"])]
    up = ["--hf-home", g["hf_home"]]
    local = ["--base-url", LOCAL, "--server-info", SERVER_INFO] + w
    for m in g["main"]:
        full = f"fs_{m}_full"
        steps = [["serve", m, [PY, SERVE, "up", m, *up]], plan(m, full, "--scope", "full"), go(full, *local)]
        if m in g["retry_arm"]:
            steps += [["retry", f"{full}-reask1", [PY, RETRY, "plan", f"runs/{full}"]], go(f"{full}-reask1", *local)]
        if m in g["dev_set"]:
            steps += [plan(m, f"fs_{m}_dev", "--scope", "dev"), go(f"fs_{m}_dev", *local)]
        steps += [["down", m, [PY, SERVE, "down", m]], ["serve", m, [PY, SERVE, "up", m, *up]],
                  plan(m, f"{full}-repeat", "--repeat-of", f"runs/{full}"), go(f"{full}-repeat", *local),
                  ["down", m, [PY, SERVE, "down", m]]]
        jobs.append(("gpu", f"{m}: full grid{', re-ask arm' if m in g['retry_arm'] else ''}"
                            f"{', dev set' if m in g['dev_set'] else ''}, repeat check on a new server", steps))
    for m in g["dev_set"]:
        if m not in g["main"]:
            jobs.append(("gpu", f"{m}: dev set", [["serve", m, [PY, SERVE, "up", m, *up]], plan(m, f"fs_{m}_dev", "--scope", "dev"),
                                                  go(f"fs_{m}_dev", *local), ["down", m, [PY, SERVE, "down", m]]]))
    think = local + ["--timeout", str(g["thinking_timeout"])]
    for pair in g["thinking_pairs"]:
        docs = pair.get("documents", "all")
        filters = list(g["thinking_filters"])
        if docs == "pilot":     # the pilot documents only: --splits pilot instead of --splits pilot full
            i = filters.index("--splits")
            filters[i + 1:i + 3] = ["pilot"]
        for m in (pair["think"], pair["partner"]):
            steps = [["serve", m, [PY, SERVE, "up", m, *up]]]
            for s in pair["request_seeds"]:
                rid = f"fs_{m}_think-filters_s{s}"
                steps += [plan(m, rid, *filters, "--request-seed", str(s)), go(rid, *think)]
            steps.append(["down", m, [PY, SERVE, "down", m]])
            jobs.append(("gpu", f"{m}: thinking pair, {docs} documents, seeds {pair['request_seeds']}", steps))
    return jobs


def hosted_jobs(fs, section):
    p, jobs = fs[section], []
    base = ["--api-key-env", p["api_key_env"], "--workers", str(p["workers"])]
    _, models = load_models()

    def url(m):     # a model's own base_url (run.py go uses it when --base-url is left out)
        return [] if models[m].get("base_url") else ["--base-url", p["base_url"]]

    for m, c in p["models"].items():
        full = f"fs_{m}_full"
        steps = [plan(m, full, "--scope", "full"), go(full, *url(m), *base, "--max-usd", str(c["max_usd"])),
                 plan(m, f"{full}-repeat", "--repeat-of", f"runs/{full}"),
                 go(f"{full}-repeat", *url(m), *base, "--max-usd", str(c["repeat_max_usd"]))]
        if section == "bedrock" and m in p.get("retry_arm", {}):
            steps += [["retry", f"{full}-reask1", [PY, RETRY, "plan", f"runs/{full}"]],
                      go(f"{full}-reask1", *url(m), *base, "--max-usd", str(p["retry_arm"][m]))]
        jobs.append((section, f"{m}: full run, repeat check" + (", re-ask arm" if "retry" in [s[0] for s in steps] else ""), steps))
    if section == "bedrock":
        kt = p["kimi_k3_thinking"]
        m = kt["key"]
        rid = f"fs_{m}_{kt['documents']}"
        scope = ["--scope", "custom", "--splits", "pilot"] if kt["documents"] == "pilot" else ["--scope", "full"]
        jobs.append((section, f"{m}: thinking on, {kt['documents']} documents",
                     [plan(m, rid, *scope), go(rid, *url(m), *base, "--timeout", "1800", "--max-usd", str(kt["max_usd"]))]))
    return jobs


def load_models():
    sys.path.insert(0, str(ROOT / "harness"))
    import run   # noqa: E402
    return run.load_models()


def all_jobs(section=None):
    fs = lineup()
    jobs = gpu_jobs(fs) + hosted_jobs(fs, "together") + hosted_jobs(fs, "bedrock")
    return [(i, *j) for i, j in enumerate(jobs, 1) if section in (None, j[0])]


def show(argv):
    return " ".join(a if a and " " not in a else repr(a) for a in argv).replace(f"{PY} ", "python ")


def newest_server_info(model):
    files = sorted((ROOT / "runs" / "servers").glob(f"{model}-*.json"), key=lambda p: p.stat().st_mtime)
    if not files:
        raise SystemExit(f"no server info for {model} in runs/servers/")
    return str(files[-1].relative_to(ROOT))


def run_jobs(args):
    jobs = all_jobs(args.section)
    for n, section, title, steps in jobs:
        if (args.only and n != args.only) or n < args.from_:
            continue
        print(f"\n=== job {n} [{section}] {title}", flush=True)
        model = None
        for kind, what, argv in steps:
            if kind == "serve":
                model = what
            if kind in ("plan", "retry") and (ROOT / "runs" / what / "planned.jsonl").exists():
                print(f"  {what}: already planned", flush=True)
                continue
            if kind == "go" and what.endswith("-reask1") and not args.dry_run \
                    and not (ROOT / "runs" / what / "planned.jsonl").exists():
                print(f"  {what}: nothing to re-ask", flush=True)
                continue
            if not args.dry_run:
                argv = [newest_server_info(model) if a == SERVER_INFO else a for a in argv]
            print(f"  $ {show(argv)}", flush=True)
            if args.dry_run:
                continue
            rc = subprocess.call(argv, cwd=ROOT)
            if kind == "retry" and rc != 0:
                print("  (nothing to re-ask, or already planned: going on)")
                continue
            if rc == 3:
                raise SystemExit(f"job {n}: {what} reached its --max-usd and stopped sending; the queue stops here. "
                                 f"Continue it by hand with a higher cap, then `run --section {section} --from {n}`.")
            if rc != 0:
                raise SystemExit(f"job {n}: `{show(argv)}` exited {rc}; the queue stops here "
                                 f"(fix it, then `run --section {section} --from {n}`)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    ls = sub.add_parser("list")
    ls.add_argument("--section", choices=["gpu", "together", "bedrock"])
    r = sub.add_parser("run")
    r.add_argument("--section", required=True, choices=["gpu", "together", "bedrock"])
    r.add_argument("--from", dest="from_", type=int, default=1, help="start at this job number")
    r.add_argument("--only", type=int, help="run only this job number")
    r.add_argument("--dry-run", action="store_true", help="print the commands, run nothing")
    args = ap.parse_args()
    if args.cmd == "list":
        for n, section, title, steps in all_jobs(args.section):
            print(f"{n:>3} [{section}] {title}")
            for _, _, argv in steps:
                print(f"      {show(argv)}")
    else:
        run_jobs(args)


if __name__ == "__main__":
    main()
