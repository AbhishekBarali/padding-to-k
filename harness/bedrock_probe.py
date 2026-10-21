#!/usr/bin/env python3
"""bedrock_probe.py: settle the Bedrock questions the docs leave open, for one model, in ~15 calls.

    pip install -r harness/requirements.txt
    aws configure  (or export AWS_PROFILE=...; or export AWS_BEARER_TOKEN_BEDROCK=<Bedrock API key>)
    python harness/bedrock_probe.py qwen.qwen3-235b-a22b-2507-v1:0 --region us-east-1

What it checks (results in runs/bedrock-probe/<model>-<utc>.json and printed):
  1. minItems 1 (documented as supported) vs minItems 3 (documented: "only values 0 and 1"):
     expect a 400 ValidationException for 3. If 3 is accepted, count the items: 3 = enforced,
     1 = silently ignored. Either way, write it in DECISIONS.md.
  2. maxItems 2: not in AWS's lists at all. Rejected, ignored, or enforced?
  3. Does Bedrock add the schema to the prompt? Same prompt with and without outputConfig:
     compare usage.inputTokens.
  4. Repeat one prompt 5 times at temperature 0: how many distinct outputs?
  5. Is a `seed` accepted through additionalModelRequestFields? (Undocumented for open models.)
The study itself sends prompt-only conditions to Bedrock through the OpenAI-compatible endpoint
(harness/run.py with --base-url https://bedrock-runtime.<region>.amazonaws.com/openai/v1), so this
probe only answers questions; it produces no study data.
"""
import argparse
import datetime as dt
import json
import time
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

ROOT = Path(__file__).resolve().parent.parent
DOC = ("Report excerpt: The audit found one issue: the backup server had no offsite copy. "
       "No other issues were found.")
PROMPT = f"List the issues found in the document.\n\nDocument:\n{DOC}"


def schema(min_items=None, max_items=None):
    arr = {"type": "array", "items": {"type": "string"}}
    if min_items is not None:
        arr["minItems"] = min_items
    if max_items is not None:
        arr["maxItems"] = max_items
    return {"type": "object", "properties": {"issues": arr}, "required": ["issues"], "additionalProperties": False}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("model_id")
    ap.add_argument("--region", default="us-east-1")
    args = ap.parse_args()
    # long read timeout: the first use of a schema compiles a grammar, which "may take up to a few minutes"
    client = boto3.client("bedrock-runtime", region_name=args.region,
                          config=Config(read_timeout=600, retries={"max_attempts": 3}))
    results = []

    def converse(label, sch=None, extra=None):
        kw = dict(modelId=args.model_id, messages=[{"role": "user", "content": [{"text": PROMPT}]}],
                  inferenceConfig={"maxTokens": 512, "temperature": 0.0})
        if sch is not None:
            kw["outputConfig"] = {"textFormat": {"type": "json_schema", "structure": {
                "jsonSchema": {"schema": json.dumps(sch), "name": "issues"}}}}
        if extra:
            kw["additionalModelRequestFields"] = extra
        t0 = time.time()
        rec = {"label": label, "schema": sch, "extra": extra}
        try:
            r = client.converse(**kw)
            text = "".join(b.get("text", "") for b in r["output"]["message"]["content"])
            try:
                n = len(json.loads(text)["issues"])
            except (json.JSONDecodeError, KeyError, TypeError):
                n = None
            rec.update(ok=True, stop=r.get("stopReason"), usage=r.get("usage"), n_items=n, text=text,
                       seconds=round(time.time() - t0, 1),
                       has_reasoning=any("reasoningContent" in b for b in r["output"]["message"]["content"]))
        except ClientError as e:
            rec.update(ok=False, error_code=e.response["Error"]["Code"], error=e.response["Error"]["Message"])
        results.append(rec)
        shown = (f"stop={rec.get('stop')} in={(rec.get('usage') or {}).get('inputTokens')} items={rec.get('n_items')}"
                 if rec["ok"] else f"ERROR {rec['error_code']}: {rec['error'][:200]}")
        print(f"[{label}] {shown}")
        return rec

    print(f"model {args.model_id} region {args.region} boto3 {boto3.__version__}")
    base = converse("no schema")
    converse("schema, no count", schema())
    converse("minItems 1 (documented as supported)", schema(1))
    converse("minItems 3 (documented as NOT supported)", schema(3))
    converse("maxItems 2 (undocumented)", schema(None, 2))
    converse("seed in additionalModelRequestFields (undocumented)", None, {"seed": 0})
    reps = [converse(f"repeat {i}") for i in range(5)]
    distinct = len({r.get("text") for r in reps if r["ok"]})
    with_schema = next((r for r in results if r["label"] == "schema, no count"), None)
    summary = {
        "minItems_3": next(r for r in results if r["label"].startswith("minItems 3")),
        "schema_adds_input_tokens": ((with_schema or {}).get("usage") or {}).get("inputTokens", 0)
                                    - (base.get("usage") or {}).get("inputTokens", 0) if base["ok"] and with_schema and with_schema["ok"] else None,
        "distinct_outputs_in_5_repeats": distinct,
    }
    print(json.dumps({k: (v if k != "minItems_3" else {kk: v.get(kk) for kk in ("ok", "error_code", "n_items")})
                      for k, v in summary.items()}, indent=1))
    out = ROOT / "runs" / "bedrock-probe" / f"{args.model_id.replace(':', '_')}-{dt.datetime.now(dt.timezone.utc):%Y%m%dT%H%M%SZ}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"model_id": args.model_id, "region": args.region, "boto3": boto3.__version__,
                               "results": results, "summary": summary}, indent=1))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
