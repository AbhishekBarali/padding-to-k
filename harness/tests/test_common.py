"""Tests for the parse and count rules. Run: python3 harness/tests/test_common.py (or pytest).

AUTHORS_CASES at the bottom is for the plan's "10 tricky test cases written by hand": add real-looking
outputs you expect to be hard, with the counts you decide are right, BEFORE the preregistration.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import common  # noqa: E402

F = "requests"


def parse(s):
    return common.parse_output(s, F)


def test_strict_json():
    p = parse('{"requests": ["Send the file", "Call Bob"]}')
    assert p["parse_rung"] == "strict" and p["items"] == ["Send the file", "Call Bob"]
    assert not p["text_outside_json"]


def test_fenced_json_with_prose():
    p = parse('Here you go:\n```json\n{"requests": ["Send the file"]}\n```\nOnly one request was found.')
    assert p["parse_rung"] == "fence" and p["items"] == ["Send the file"] and p["text_outside_json"]


def test_first_object_with_braces_in_strings():
    p = parse('Sure. {"requests": ["Use {curly} braces", "B"]} done')
    assert p["parse_rung"] == "first_object" and p["items"] == ["Use {curly} braces", "B"]


def test_failed_and_truncated():
    assert parse("No requests.")["items"] is None
    assert parse(None)["parse_rung"] == "failed"
    p = parse('{"requests": ["Send the file", "Call Bob", "Book the ro')      # cut off by max_tokens
    assert p["parse_rung"] == "truncated_salvage" and p["items"] == ["Send the file", "Call Bob"]
    assert parse('{"requests": ["Send the file", "Call')["items"] == ["Send the file"]
    assert parse('{"requests": ["Send the file (and the rest of this entry is cut off')["parse_rung"] == "failed"


def test_truncated_with_brackets_inside_strings():
    # Qwen3.5-2B under minItems 3 (engine test, 14 Oct): it tried to close the list inside an entry, the grammar
    # kept the list open, and the token cap cut it off. The "]}" inside the string is not a closed list.
    p = parse('{"requests": ["Send the file", "Discuss the offsite - follow-up action]}", "status", "notes", "act')
    assert p["parse_rung"] == "truncated_salvage", p
    assert p["items"] == ["Send the file", "Discuss the offsite - follow-up action]}", "status", "notes"], p
    assert parse('{"requests": ["Send the file", "Call Bob"]} and then prose that is cut')["items"] == ["Send the file", "Call Bob"]


def test_two_answer_lists_are_counted():
    p = parse('{"requests": ["Send the file"]}\nThe schema needs 3, so:\n{"requests": ["Send the file", "a", "b"]}')
    assert p["items"] == ["Send the file"] and p["n_answer_lists"] == 2, p
    assert parse('{"requests": ["Send the file"]}')["n_answer_lists"] == 1


def test_schema_echo_is_not_the_answer():
    p = parse('Schema: {"type":"object","properties":{"requests":{"type":"array"}},"required":["requests"]}\n'
              'Answer: {"requests":["a","b"]}')
    assert p["items"] == ["a", "b"] and p["parse_rung"] == "later_object"
    p = parse('```json\n{"type": "object", "required": ["requests"]}\n```\n```json\n{"requests": ["x"]}\n```')
    assert p["items"] == ["x"] and p["parse_rung"] == "fence"
    assert parse('{"type": "object", "required": ["requests"]}')["items"] is None


def test_braces_in_prose_and_reasoning_tags():
    assert parse('Use {curly} braces. {"requests": ["a"]}')["items"] == ["a"]
    p = parse('<think>maybe {"requests": ["wrong"]}</think>{"requests": ["right"]}')
    assert p["items"] == ["right"] and p["reasoning_in_content"]
    assert parse('Here: ["a", "b"]')["parse_rung"] == "array_in_text"


def test_bare_list_and_other_key():
    assert parse('["a", "b"]')["list_source"] == "bare_list"
    p = parse('{"items": ["a"]}')
    assert p["list_source"] == "single_other_key" and p["items"] == ["a"]
    assert parse('{"a": ["x"], "b": ["y"]}')["items"] is None


def test_non_string_items_kept():
    p = parse('{"requests": ["a", null, {"x": 1, "y": 2}, {"text": "b"}]}')
    assert p["items"] == ["a", "", '{"x": 1, "y": 2}', "b"] and p["non_string_items"] == 3


def test_placeholders():
    yes = ["N/A", "n/a", "NA", "None", "none.", "", "-", "...", "Not specified", "Not mentioned in the email",
           "No further requests", "No more action items found", "There are no other requests",
           "No additional medications mentioned", "Unknown", "[none]", "(not provided)", "Item 3",
           "request 2", "Insufficient information", "Only one request found", "nothing",
           # found by the plan review (13 Oct): model notes that flag a shortfall
           "(none)", "Nothing else", "No action item", "Item not found", "Request 2: none",
           "Only one request in this email", "Not applicable - only 1 request",
           "The email contains no other requests.", "The sender does not ask for anything else",
           "Unable to find additional requests", "[No third request]",
           # found by the code review (13 Oct)
           "(N/A)", "N.A.", "n.a.", "N / A", "(blank)", "Missing", "Unspecified", "Placeholder", "Line item 1",
           "Quote 2", "Knowledge 3", "Requirement 4", "#3", "Item three", "no more people mentioned in the article",
           "Additional item", "No third request"]
    no = ["Send the file by Friday", "<ORGANIZATION>", "NASA", "Nadia", "Notify the team", "None of the above options",
          "No smoking policy", "Unknown Pleasures album", "aspirin", "Call Bob", "Lisinopril 10 mg daily",
          "Only you can do it", "Missing invoices must be reported", "Requests for proposals",
          "Do not mention the lawsuit to MSN", "Please do not reply", "product"]
    for s in yes:
        assert common.is_placeholder(s), s
    for s in no:
        assert not common.is_placeholder(s), s


def test_placeholders_from_the_dev_list():
    # Found in the dev-set outputs (analysis/dev/note_candidates.md, 14 Oct): notes the rules missed
    yes = ["None mentioned in the provided document.", "no", "not", "None applicable", "none documented",
           "No prescription drugs noted.", "No follow-up actions are required based on the given text.",
           "No instructions or tasks are outlined for the recipient.", "Document does not reference medications.",
           "The document consists only of narrative description.",
           "none mentioned in the provided document (no medications listed) or implied by the clinical context.",
           "Unknown Person 2", "medication1", "medications_mentioned: false", "reason: none_in_text",
           "minItems", "description", "string", "type", "error", ": 5,",
           "Document contains only 1 item, but schema requires at least 5.",
           "Please provide at least five requests as per the schema requirements, but the provided document "
           "contains no explicit requests.",
           "in a vague context, I cannot fulfill the schema's `minItems: 3` requirement with the given information.",
           # spill: the model closed the list inside an entry and went on in prose
           "]} ``` For a valid instance, additional medications would need to be included. ```json {",
           "). Since the schema requires at least **3 medication entries**, and the document only mentions",
           "]. However, since the document does not contain a third quotation, I cannot fulfill the constraint.",
           "} ``` (This is not a valid JSON instance either, but highlights the issue.) ```json {",
           "):```json[ARGS]{",
           "none mentioned in the provided document (no medications listed)]}The provided document does not "
           "mention any medications given to or taken by the patient."]
    # real items from the same list that look like notes: they must stay items
    no = ["Ed will find out the additional cost of adding a display.", "TAX", "Why?", "Please provide more information",
          "Note that only the first 4 of 8 pages are planned for inclusion.",
          "There is no mention in either the Confirm or the GTC language regarding the primary term of the new "
          "keep whole GTCs.", "Proceed with the changes to TW's tariff (assuming no meeting is needed)",
          "Understand that there is no rhyme or reason to the generator",
          "Validate that the interface contains only necessary buttons.",
          "steroid injections (if applicable, though not explicitly mentioned)",
          "antidiabetic medications (general category, as specifics are not mentioned)]}**",
          "everolimus (10 mg daily)]} is not valid because it does not meet the `minItems: 3` requirement.",
          "Popcorn Salt (S) {Note: The document provided contains only 2 items, but the schema requires a "
          "minimum of 5. I am listing the available items.}",
          "Why did she have the section? (Note: This is a single request, but the schema requires at least 5 "
          "items. Since the document only contains 4 requests, this is incomplete.)",
          "Unknown Pleasures album", "Unnamed Road", "Item description sheet", "No smoking policy"]
    for s in yes:
        assert common.is_placeholder(s), s
    for s in no:
        assert not common.is_placeholder(s), s


def test_document_text_is_never_a_placeholder():
    doc = 'He said, "Only one more day," and left. The (TAKE AWAY) box. Nothing else was there.'
    for s in ["Only one more day", "(TAKE AWAY)", "Nothing else was there"]:
        assert not common.is_placeholder(s, doc_text=doc), s
    assert common.is_placeholder("N/A", doc_text="Fees: N/A")          # the escape value is always a placeholder
    assert common.is_placeholder("Only one request in this email", doc_text=doc)


def test_duplicates():
    assert common.is_duplicate("Send the file.", ["send the file"])
    assert common.is_duplicate("Send the files", ["Send the file"])
    assert not common.is_duplicate("Send the budget", ["Send the file"])
    assert not common.is_duplicate("Lisinopril 10 mg daily", ["Lisinopril 20 mg daily"])
    assert not common.is_duplicate("Send the Q3 report to finance", ["Send the Q4 report to finance"])


def test_count_items():
    c = common.count_items(["Send the file", "send the file.", "N/A", "Call Bob", "None"])
    assert (c["n_items"], c["n_substantive"], c["n_placeholder"], c["n_escape"], c["n_duplicate"]) == (5, 2, 2, 1, 1)


# Add the authors' own hard cases here: (raw model output, field, expected substantive count).
AUTHORS_CASES = []


def test_request_body_provider_fields():
    import run   # noqa: E402  (run.py sits next to common.py)
    rq = {"temperature": 0, "top_p": 1, "seed": 0, "max_tokens": 512}
    vllm = run.build_body({"hf_repo": "Qwen/Qwen3.5-9B", "backend": "vllm",
                           "chat_template_kwargs": {"enable_thinking": False}}, rq, "hi")
    assert vllm["max_completion_tokens"] == 512 and "max_tokens" not in vllm
    assert vllm["chat_template_kwargs"] == {"enable_thinking": False} and "reasoning" not in vllm
    assert vllm["return_token_ids"] is True
    think = run.build_body({"hf_repo": "Qwen/Qwen3.5-9B", "backend": "vllm",
                            "chat_template_kwargs": {"enable_thinking": True}}, rq, "hi")
    assert "return_token_ids" not in think
    tg = run.build_body({"api_model": "moonshotai/Kimi-K3", "backend": "together", "max_tokens_field": "max_tokens",
                         "chat_template_kwargs": {"enable_thinking": False},
                         "extra_body": {"reasoning": {"enabled": False}}}, rq, "hi")
    assert tg["max_tokens"] == 512 and "max_completion_tokens" not in tg
    assert tg["reasoning"] == {"enabled": False} and "chat_template_kwargs" not in tg
    assert tg["model"] == "moonshotai/Kimi-K3" and tg["seed"] == 0 and "return_token_ids" not in tg


def test_authors_cases():
    for raw, field, expected in AUTHORS_CASES:
        p = common.parse_output(raw, field)
        got = common.count_items(p["items"] or [])["n_substantive"]   # add doc_text=... if the case needs it
        assert got == expected, (raw, got, expected)


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
