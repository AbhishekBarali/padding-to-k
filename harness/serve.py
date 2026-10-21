#!/usr/bin/env python3
"""serve.py: start (or print) the pinned vLLM server for one model, and record exactly how it ran.

    python harness/serve.py up qwen3.5-9b [--print] [--port 8000] [--hf-home /data/hf] [--image IMAGE]
                                        [--no-reasoning-parser] [--extra=--flag=value ...] [--env KEY=VALUE ...]
    python harness/serve.py down qwen3.5-9b

`up` builds the docker command from configs/models.yaml (defaults.serve_args + the model's serve_args;
a model value overrides a default with the same flag name), starts it detached, waits for /health,
and writes runs/servers/<model>-<utc>.json with the image digest, the full command, the env, the
GPU (nvidia-smi) and the vLLM version, so every run can point at the server that produced it
(run.py go --server-info <that file>). The port is bound to 127.0.0.1 only: the server has no API
key, so never publish it on a public interface.
"""
import argparse
import datetime as dt
import json
import shlex
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def merged_args(defaults, model, drop_reasoning):
    out = {}
    for a in defaults.get("serve_args", []) + model.get("serve_args", []):
        name = a.split("=", 1)[0]
        out[name] = a
    if drop_reasoning:
        out.pop("--reasoning-parser", None)
    return list(out.values())


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def up(args):
    cfg = yaml.safe_load((ROOT / "configs" / "models.yaml").read_text(encoding="utf-8"))
    d, m = cfg["defaults"], cfg["models"][args.model]
    if m.get("backend") != "vllm":
        sys.exit(f"{args.model} is not a local model")
    image = args.image or d["vllm_image"]
    name = f"padk-{args.model}".replace(".", "-")
    serve = ["--model", m["hf_repo"], "--revision", m["revision"], "--tokenizer-revision", m["revision"],
             *merged_args(d, m, args.no_reasoning_parser), *args.extra, "--host", "0.0.0.0", "--port", "8000"]
    env = {**d.get("env", {}), **(m.get("env") or {})}     # a model may override, e.g. batch invariance off
    for kv in args.env:
        k, _, v = kv.partition("=")
        env[k] = v
    cmd = ["docker", "run", "-d", "--name", name, "--gpus", "all", "--ipc=host",
           "-p", f"127.0.0.1:{args.port}:8000", "-v", f"{args.hf_home}:/root/.cache/huggingface",
           "-v", f"{ROOT / 'configs'}:/padk/configs:ro",      # chat templates kept in the repo (configs/chat_templates)
           "-e", "HF_TOKEN"]
    for k, v in env.items():
        cmd += ["-e", f"{k}={v}"]
    cmd += [image, *serve]
    print(" ".join(shlex.quote(c) for c in cmd))
    if args.print:
        return
    r = sh(cmd)
    if r.returncode:
        sys.exit(r.stderr)
    base = f"http://127.0.0.1:{args.port}"
    t0 = time.time()
    while time.time() - t0 < args.wait:
        running = sh(["docker", "inspect", "-f", "{{.State.Running}}", name]).stdout.strip()
        if running != "true":
            r = sh(["docker", "logs", "--tail", "200", name])
            print(r.stdout + r.stderr)
            sys.exit(f"container {name} stopped while starting (state: {running or 'gone'}); log above")
        try:
            with urllib.request.urlopen(base + "/health", timeout=5) as resp:
                if resp.status == 200:
                    break
        except Exception:  # noqa: BLE001  (still loading)
            pass
        time.sleep(5)
    else:
        print(sh(["docker", "logs", "--tail", "80", name]).stdout)
        sys.exit(f"server did not become healthy in {args.wait}s; see docker logs {name}")
    info = {"utc": dt.datetime.now(dt.timezone.utc).isoformat(), "model_key": args.model, "container": name,
            "image": image,
            "image_digest": sh(["docker", "inspect", "--format", "{{index .RepoDigests 0}}", image]).stdout.strip(),
            "command": cmd, "env": env, "seconds_to_healthy": round(time.time() - t0),
            "nvidia_smi": sh(["nvidia-smi", "--query-gpu=name,driver_version,memory.total,power.limit,ecc.mode.current",
                              "--format=csv,noheader"]).stdout.strip()}
    try:
        with urllib.request.urlopen(base + "/version", timeout=5) as resp:
            info["vllm_version"] = json.loads(resp.read().decode())
    except Exception as e:  # noqa: BLE001
        info["vllm_version"] = f"unavailable: {e}"
    info["pip_freeze_in_container"] = sh(["docker", "exec", name, "pip", "freeze"]).stdout.splitlines()
    out = ROOT / "runs" / "servers" / f"{args.model}-{info['utc'][:19].replace(':', '')}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(info, indent=1), encoding="utf-8")
    print(f"healthy after {info['seconds_to_healthy']}s; server info: {out}")


def down(args):
    name = f"padk-{args.model}".replace(".", "-")
    logs = ROOT / "runs" / "servers" / f"{name}-{dt.datetime.now(dt.timezone.utc):%Y%m%dT%H%M%S}.log"
    logs.parent.mkdir(parents=True, exist_ok=True)
    r = sh(["docker", "logs", name])
    logs.write_text(r.stdout + r.stderr, encoding="utf-8")
    print(sh(["docker", "rm", "-f", name]).stdout or f"removed {name}; log kept in {logs}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    u = sub.add_parser("up")
    u.add_argument("model")
    u.add_argument("--print", action="store_true", help="only print the docker command")
    u.add_argument("--port", type=int, default=8000)
    u.add_argument("--hf-home", default=str(Path.home() / ".cache" / "huggingface"))
    u.add_argument("--image")
    u.add_argument("--no-reasoning-parser", action="store_true")
    u.add_argument("--wait", type=int, default=1800)
    u.add_argument("--extra", action="append", default=[], help="extra vLLM flag, e.g. --extra=--enforce-eager")
    u.add_argument("--env", action="append", default=[], metavar="KEY=VALUE",
                   help="server environment for this start only, over models.yaml (to test a setting first)")
    dn = sub.add_parser("down")
    dn.add_argument("model")
    args = ap.parse_args()
    up(args) if args.cmd == "up" else down(args)


if __name__ == "__main__":
    main()
