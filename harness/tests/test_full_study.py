"""Tests for the full-study additions of 18 Oct: the min_k_shown_fewer_ok requests, the spending stop, the
gpt-oss reasoning block, and the retry arm's correction message. Run: python3 harness/tests/test_full_study.py
"""
import json
import sys
import threading
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import common  # noqa: E402
import retry_arm  # noqa: E402
import run  # noqa: E402

sys.path.insert(0, str(common.DATA))
import build_fewer_ok  # noqa: E402


def test_fewer_ok_requests_match_min_k_shown():
    on_disk = common.read_jsonl(common.DATA / "requests_fewer_ok.jsonl")
    assert on_disk == build_fewer_ok.requests()            # the file is what the script builds
    shown = {(r["doc_id"], r["k"]): r for r in common.read_jsonl(common.DATA / "requests.jsonl")
             if r["condition"] == "min_k_shown"}
    assert len(on_disk) == len(shown) == 1674
    for r in on_disk:
        s = shown[(r["doc_id"], r["k"])]
        assert r["condition"] == "min_k_shown_fewer_ok" and not r["enforce_schema"]
        assert r["schema_id"] == s["schema_id"] and r["schema_block_id"] == s["schema_block_id"]
        assert r["instruction"] == s["instruction"] + f" If the document contains fewer than {r['k']}, list all available ones."
    assert len({r["request_id"] for r in on_disk}) == len(on_disk)


def test_fewer_ok_requests_are_in_the_full_scope_only():
    rows = [r for r in common.load_requests() if r["condition"] == "min_k_shown_fewer_ok"]
    assert len(rows) == 1674 and all(not r.get("arm") for r in rows)
    assert "min_k_shown_fewer_ok" not in run.PILOT_CONDITIONS


def test_gpt_oss_reasoning_block_is_dropped():
    content = ('<reasoning>We need extract names. Maybe {"people": ["Draft"]} first.</reasoning>'
               '{\n  "people": [\n    "Anna",\n    "Bob"\n  ]\n}')
    p = common.parse_output(content, "people")
    assert p["items"] == ["Anna", "Bob"] and p["parse_rung"] == "strict" and p["reasoning_in_content"]


def test_cut_off_inside_reasoning_is_no_answer():
    p = common.parse_output('<reasoning>Draft: {"people": ["Anna", "Bob"]} then check the', "people")
    assert p["items"] is None and p["parse_rung"] == "failed" and p["reasoning_in_content"]


def test_cost_of_a_reply():
    price = {"in": 1.65, "out": 8.25}
    assert abs(run.cost_usd({"prompt_tokens": 1_000_000, "completion_tokens": 100_000}, price) - 2.475) < 1e-9
    assert run.cost_usd(None, price) is None and run.cost_usd({"prompt_tokens": 5}, None) is None


def test_spending_stop_counts_requests_in_flight():
    s = types.SimpleNamespace(lock=threading.Lock(), max_usd=1.0, spent=0.0, n_costed=0, in_flight=0,
                              budget_stop=None)
    assert run.Sender._admit(s) and s.in_flight == 1          # nothing spent yet: send
    s.in_flight, s.spent, s.n_costed = 0, 0.8, 8              # mean 0.1 USD per reply
    assert run.Sender._admit(s) and run.Sender._admit(s)      # 0.8 + 0.1 and 0.8 + 0.2 in flight
    assert not run.Sender._admit(s) and "spending stop" in s.budget_stop   # 0.8 + 2 x 0.1 reaches 1.0
    s2 = types.SimpleNamespace(lock=threading.Lock(), max_usd=None, spent=99.0, n_costed=1, in_flight=0,
                               budget_stop=None)
    assert run.Sender._admit(s2)                              # no cap: always send


def test_retry_message_is_pydantic_and_instructor_text():
    # strings produced by pydantic 2.12.3 for `list[str] = Field(min_length=k)`, then Instructor's reask_md_json
    assert retry_arm.reask_message("requests", ["Send the file"], 3) == (
        "Correct your JSON ONLY RESPONSE, based on the following errors:\n"
        "1 validation error for Requests\nrequests\n"
        "  List should have at least 3 items after validation, not 1 [type=too_short, "
        "input_value=['Send the file'], input_type=list]\n"
        "    For further information visit https://errors.pydantic.dev/2.12/v/too_short")
    assert "for Requests\nrequests\n  List should have at least 3 items after validation, not 0 " \
           "[type=too_short, input_value=[], input_type=list]" in retry_arm.validation_error("requests", [], 3)
    long = retry_arm.validation_error("action_items", ["a" * 47], 5)
    assert "for ActionItems\naction_items\n" in long
    assert "input_value=['aaaaaaaaaaaaaaaaaaaaaaa...aaaaaaaaaaaaaaaaaaaaaa']" in long
    assert "input_value=['" + "a" * 46 + "']" in retry_arm.validation_error("action_items", ["a" * 46], 5)


def test_followup_turns_are_appended():
    s = types.SimpleNamespace()
    req = next(r for r in common.load_requests() if r["condition"] == "min_k_shown" and r["split"] == "pilot")
    docs, prompts = common.load_documents(), common.load_prompts()
    msg = common.user_message(req, docs[req["doc_id"]], prompts)
    s._req_index, s.docs, s.prompts, s.logprobs = {req["request_id"]: req}, docs, prompts, 0
    s.mcfg, s.req_defaults, s.manifest = {"api_model": "m", "backend": "bedrock", "send_seed": False}, \
        {"temperature": 0, "top_p": 1, "seed": 0, "max_tokens": 512}, {}
    row = {"request_id": req["request_id"] + "|reask1", "source_request_id": req["request_id"],
           "doc_id": req["doc_id"], "prompt_sha256": common.sha256_text(msg), "enforce_schema": False,
           "followup": {"assistant": '{"x": []}', "user": "Correct your JSON"}}
    b = run.Sender.body(s, row)
    assert [m["role"] for m in b["messages"]] == ["user", "assistant", "user"]
    assert b["messages"][0]["content"] == msg and b["messages"][2]["content"] == "Correct your JSON"


def test_full_study_lineup_keys_exist():
    import yaml
    cfg = yaml.safe_load((common.ROOT / "configs" / "models.yaml").read_text())
    fs, models = cfg["full_study"], cfg["models"]
    keys = fs["gpu"]["main"] + fs["gpu"]["dev_set"] + fs["gpu"]["retry_arm"]
    keys += list(fs["together"]["models"]) + list(fs["bedrock"]["models"]) + list(fs["bedrock"]["retry_arm"])
    keys += [p[x] for p in fs["gpu"]["thinking_pairs"] for x in ("think", "partner")]
    keys += [fs["bedrock"]["kimi_k3_thinking"]["key"]]
    assert all(k in models for k in keys), [k for k in keys if k not in models]
    for k in list(fs["bedrock"]["models"]) + list(fs["together"]["models"]) + [fs["bedrock"]["kimi_k3_thinking"]["key"]]:
        assert models[k].get("price"), k
    for k in list(fs["bedrock"]["models"]) + [fs["bedrock"]["kimi_k3_thinking"]["key"]]:
        assert models[k]["conditions"] == cfg["defaults"]["prompt_side_conditions"], k
        assert models[k]["extra_body"] == {"service_tier": "flex"}, k
    assert len(fs["gpu"]["main"]) == 8
    # the presence-penalty-0 pair differs from the thinking pair only in the penalty
    for a, b in (("qwen3.5-9b-think", "qwen3.5-9b-think-pp0"), ("qwen3.5-9b-nothink", "qwen3.5-9b-nothink-pp0")):
        x, y = dict(models[a]), dict(models[b])
        assert y["request"].pop("presence_penalty") == 0 and x["request"].pop("presence_penalty") == 1.5
        for d in (x, y):
            d.pop("why", None)
        assert x == y, (a, b)


def test_caps_hold():
    sys.path.insert(0, str(common.ROOT / "analysis"))
    import full_study_estimate as est
    _, models = run.load_models()
    fs, ct = est.lineup(), est.costtest()
    assert est.check_caps(fs, est.hosted_jobs(fs, models, ct), ct) == []


def test_queue_lists_every_job_once():
    import full_study_queue as q
    fs = q.lineup()
    jobs = q.all_jobs()
    gos = [what for _, _, _, steps in jobs for kind, what, _ in steps if kind == "go"]
    assert len(gos) == len(set(gos))
    for m in fs["gpu"]["main"]:
        assert {f"fs_{m}_full", f"fs_{m}_full-repeat"} <= set(gos), m
    for m in list(fs["together"]["models"]) + list(fs["bedrock"]["models"]):
        assert {f"fs_{m}_full", f"fs_{m}_full-repeat"} <= set(gos), m
    for p in fs["gpu"]["thinking_pairs"]:
        for m in (p["think"], p["partner"]):
            assert {f"fs_{m}_think-filters_s{s}" for s in p["request_seeds"]} <= set(gos), m
    # every hosted go carries a spending stop, and no local one does
    for _, section, _, steps in jobs:
        for kind, what, argv in steps:
            if kind == "go":
                assert ("--max-usd" in argv) == (section != "gpu"), what


if __name__ == "__main__":
    fns = [v for k, v in dict(globals()).items() if k.startswith("test_") and callable(v)]
    bad = 0
    for fn in fns:
        try:
            fn()
            print("ok  ", fn.__name__)
        except AssertionError as e:
            bad += 1
            print("FAIL", fn.__name__, e)
    print(f"{len(fns) - bad}/{len(fns)} passed")
    sys.exit(1 if bad else 0)
