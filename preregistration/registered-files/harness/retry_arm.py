#!/usr/bin/env python3
"""retry_arm.py: the Instructor-style retry arm. A min_k_shown reply whose list is shorter than k goes back to
the model once, with the validation error a retry library would send.

    python harness/retry_arm.py plan runs/<finished run>        writes runs/<that run>-reask1/ (nothing is sent)
    python harness/run.py go runs/<finished run>-reask1 ...      sends it like any other run

Which replies: status ok, condition min_k_shown, a list could be read (common.parse_output), and the list
has fewer than k entries (all entries, as a validator counts them, not only substantive ones). An unreadable
reply is not retried: a retry library would send a JSON error there, which is a different arm.

What is sent: the first request unchanged, then the model's own reply as the assistant turn, then the user
turn Instructor sends for its JSON modes, with the error pydantic raises for a list field with min_length k:

  Instructor (567-labs/instructor@035c77b7, instructor/v2/providers/openai/handlers.py, reask_md_json):
      "Correct your JSON ONLY RESPONSE, based on the following errors:\\n" + str(exception)
  pydantic 2.12, for `class Requests(BaseModel): requests: list[str] = Field(min_length=3)` and one entry:
      1 validation error for Requests
      requests
        List should have at least 3 items after validation, not 1 [type=too_short, input_value=['Send the file'], input_type=list]
          For further information visit https://errors.pydantic.dev/2.12/v/too_short

The model class is named after the field (requests -> Requests, line_items -> LineItems), as a user of the
library would name it. The retried replies are written with arm "reask1" and `retry_of` pointing at the first
reply, so they are scored as their own arm and never mixed with the first replies.
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common  # noqa: E402
import run  # noqa: E402

ARM = "reask1"
REASK = "Correct your JSON ONLY RESPONSE, based on the following errors:\n"
PYDANTIC_DOCS = "https://errors.pydantic.dev/2.12/v/too_short"


def _truncated_repr(value):
    """pydantic-core shows input_value as repr(), cut to its first 25 and last 24 characters past 50."""
    r = repr(value)
    return r if len(r) <= 50 else r[:25] + "..." + r[-24:]


def validation_error(field, items, k):
    model = "".join(part.capitalize() for part in field.split("_"))
    return (f"1 validation error for {model}\n{field}\n"
            f"  List should have at least {k} items after validation, not {len(items)} "
            f"[type=too_short, input_value={_truncated_repr(items)}, input_type=list]\n"
            f"    For further information visit {PYDANTIC_DOCS}")


def reask_message(field, items, k):
    return REASK + validation_error(field, items, k)


def plan(args):
    src = Path(args.run_dir)
    man = json.loads((src / "manifest.json").read_text(encoding="utf-8"))
    planned = {r["request_id"]: r for r in common.read_jsonl(src / "planned.jsonl")}
    prompts = common.load_prompts()
    picked, why = [], Counter()
    latest = {r["request_id"]: r for r in run.run_records(src)}
    for rid, rec in latest.items():
        if rec.get("arm") or rec["condition"] != "min_k_shown":
            continue
        if rec["status"] != "ok":
            why["not ok"] += 1
            continue
        field = prompts["lists"][rec["schema_id"].split("|")[0]]["field"]
        items = common.parse_output(rec.get("content"), field)["items"]
        if items is None:
            why["no list read"] += 1
            continue
        if len(items) >= rec["k"]:
            why["k or more entries"] += 1
            continue
        why["retried"] += 1
        row = dict(planned[rid])
        row.update({"request_id": f"{rid}|{ARM}", "source_request_id": rid, "also_answers": [], "arm": ARM,
                    "followup": {"run_id": man["run_id"], "assistant": rec["content"],
                                 "user": reask_message(field, items, rec["k"])}})
        picked.append(row)
    if not picked:
        raise SystemExit(f"nothing to retry in {src}: {dict(why)}")
    out = src.parent / f"{src.name}-{ARM}"
    if out.exists() and any(out.glob("raw*.jsonl")):
        raise SystemExit(f"{out} already has outputs")
    out.mkdir(exist_ok=True)
    picked.sort(key=lambda r: r["request_id"])
    with open(out / "planned.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for row in picked:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    new = dict(man)
    new.update({"run_id": out.name, "created_utc": run.now(), "scope": ARM, "retry_of_run": man["run_id"],
                "expected_outputs": len(picked), "expected_request_ids_covered": len(picked),
                "by_condition": dict(Counter(r["condition"] for r in picked)),
                "documents": len({r["doc_id"] for r in picked}),
                "restricted_outputs_expected": sum(r["restricted"] for r in picked),
                "git": run.git_state(), "selection": dict(why)})
    (out / "manifest.json").write_text(json.dumps(new, indent=1), encoding="utf-8")
    print(f"planned {out}: {len(picked)} replies to send back; {dict(why)}")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("run_dir")
    args = ap.parse_args()
    plan(args)


if __name__ == "__main__":
    main()
