"""Tests for the item matcher v0. Run: python3 analysis/tests/test_matcher.py (or pytest).

Every document and output below is made up for the test; none is copied from the study or dev data.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import matcher  # noqa: E402


def span_doc(set_name, text, golds):
    """A document whose gold items carry character spans, as data/documents.jsonl stores them."""
    items = []
    for g in golds:
        a = text.index(g)
        items.append({"text": g, "start": a, "end": a + len(g)})
    return {"doc_id": "test", "set": set_name, "n": len(items), "text": text, "gold_items": items}


def labels(doc, entries, **kw):
    return [r["label"] for r in matcher.match_output(doc, entries, **kw)]


EMAIL = span_doc("emails",
                 "Subject: Budget\n\nHi Sam, could you send me the Q3 budget by Friday? The office will be closed "
                 "on Monday. Also, what time is the review meeting? Lunch will be provided. Let me know if you "
                 "have any questions.", ["send me the Q3 budget by Friday", "what time is the review meeting"])


def test_true_items_quotes_with_openers_and_rewording():
    res = matcher.match_output(EMAIL, ["Could you send me the Q3 budget by Friday?",
                                       "What time is the review meeting?"])
    assert [r["label"] for r in res] == ["true_item", "true_item"]
    assert res[0]["gold"] == [0] and res[1]["gold"] == [1]
    # a reworded request with the same words still lands on its gold span
    assert matcher.match_output(EMAIL, ["Please send the Q3 budget by Friday"])[0]["gold"] == [0]


def test_in_text_wrong_type_quotes():
    # real email text that is not a request, including an excluded sign-off
    assert labels(EMAIL, ["Lunch will be provided.", "Let me know if you have any questions",
                          "The office will be closed on Monday"]) == ["in_text_wrong_type"] * 3


def test_restated_with_a_generic_verb_is_still_in_text():
    # "Confirm that ..." adds a generic verb to a statement of the email: real text, not invented
    assert labels(EMAIL, ["Confirm that the office will be closed on Monday"]) == ["in_text_wrong_type"]


def test_plausible_invented_and_prompt_echo():
    res = matcher.match_output(EMAIL, ["Book a flight to Denver for the conference",
                                       "List all the requests."],
                               prompt_text="List all the requests.\nThe output should be formatted as JSON.")
    assert [r["label"] for r in res] == ["plausible_invented", "plausible_invented"]
    assert res[0]["note"] != "prompt_echo" and res[1]["note"] == "prompt_echo"


def test_possible_note_is_flagged_not_hidden():
    r = matcher.match_output(EMAIL, ["The email contains only two requests."])[0]
    assert r["label"] == "plausible_invented" and r["note"] == "possible_note"


def test_placeholder_and_repeat_pass_through():
    assert labels(EMAIL, ["send me the Q3 budget by Friday", "N/A", "No further requests",
                          "Send me the Q3 budget by Friday."]) == ["true_item", "placeholder", "placeholder", "repeat"]


def test_split_of_true_quotes():
    doc = span_doc("novel_quotes", 'He sat down. "Again, again, again! Stake again!" shouted the old lady.',
                   ["Again, again, again! Stake again!"])
    assert labels(doc, ["Again, again, again!", "Stake again!"]) == ["true_item", "split_of_true"]


def test_merge_claims_both_gold_items():
    doc = span_doc("job_posts_knowledge", "You know Python and SQL well.", ["Python", "SQL"])
    res = matcher.match_output(doc, ["Python and SQL", "SQL"])
    assert res[0]["label"] == "true_item" and res[0]["gold"] == [0, 1]
    assert res[1]["label"] == "split_of_true"


def test_neighbouring_items_are_not_merged():
    text = "What is the timeline for other protests to come in? What is the timeline for FERC to decide?"
    doc = span_doc("emails", text, ["What is the timeline for other protests to come in",
                                    "What is the timeline for FERC to decide"])
    res = matcher.match_output(doc, ["What is the timeline for other protests to come in?",
                                     "What is the timeline for FERC to decide?"])
    assert [(r["label"], r["gold"]) for r in res] == [("true_item", [0]), ("true_item", [1])]


def test_novel_quotes_ignore_quote_marks_and_apostrophes():
    doc = span_doc("novel_quotes", 'She said, "I m sure he s right," and left.', ["I m sure he s right,"])
    assert labels(doc, ['"I\'m sure he\'s right"']) == ["true_item"]


def test_receipts_lines():
    doc = span_doc("receipts", "1 Lemon Tea (L). 25.000\nSUBTOTAL 25.000\nTAX 2.500\nTOTAL 27.500",
                   ["Lemon Tea (L)."])
    assert labels(doc, ["1 Lemon Tea (L)", "TAX", "Chocolate Cake"]) == \
        ["true_item", "in_text_wrong_type", "plausible_invented"]


def test_clinical_spelling_variants_and_invented_drug():
    doc = span_doc("clinical", "She was given levofloxacin 500 mg daily iv and was intubated on day 3.",
                   ["levofloxacin"])
    assert labels(doc, ["levofloxacin 500 mg", "intubation", "warfarin"]) == \
        ["true_item", "in_text_wrong_type", "plausible_invented"]


def test_names_exact_contained_and_squashed():
    doc = span_doc("wiki_people", "In 1981, Freeman and Anne Westfal l left Epyx with Paul Reiche III.",
                   ["Freeman", "Anne Westfal l", "Paul Reiche III"])
    res = matcher.match_output(doc, ["Anne Westfall", "Reiche", "Freeman", "Epyx", "John Smith"])
    assert [(r["label"], r["gold"]) for r in res] == [
        ("true_item", [1]), ("true_item", [2]), ("true_item", [0]), ("in_text_wrong_type", None),
        ("plausible_invented", None)]


def test_name_accents_folded():
    doc = span_doc("wiki_people", "He attended lectures by Gabriel P\u00e9ri.", ["Gabriel P\u00e9ri"])
    assert labels(doc, ["Gabriel Peri"]) == ["true_item"]


MEETING = {
    "doc_id": "mtg-test", "set": "meetings", "n": 2,
    "text": ("Project Manager: The buttons should be rubber, I think.\n"
             "Industrial Designer: Yes, rubber buttons, and not too heavy.\n"
             "Project Manager: Next meeting in thirty minutes. I will put the minutes in the project folder.\n"
             "Project Manager: The Industrial Designer will do the components concept.\n"),
    "gold_items": [
        {"text": "The Project Manager will put the minutes in the project folder.", "start": None, "end": None,
         "evidence": [{"text": "I will put the minutes in the project folder."}]},
        {"text": "The Industrial Designer will work on the components concept.", "start": None, "end": None,
         "evidence": [{"text": "The Industrial Designer will do the components concept."}]},
    ],
}
SIM = matcher.LexicalSimilarity(matcher.meeting_lines(MEETING["text"]) + [
    "we need a remote", "the remote control should be simple", "next meeting", "buttons", "a budget"])


def test_meetings_labels():
    res = matcher.match_output(MEETING, [
        "ID will create the components concept.",                   # true item, role abbreviated
        "PM to put the minutes in the project folder.",             # true item
        "Industrial Designer will draft the components concept.",   # same gold again: split_of_true
        "Use rubber buttons that are not too heavy.",               # said in the meeting: wrong type
        "Negotiate a supplier discount with the factory in Taiwan.",  # not said anywhere: invented
    ], sim=SIM)
    assert [r["label"] for r in res] == ["true_item", "true_item", "split_of_true", "in_text_wrong_type",
                                         "plausible_invented"]
    assert res[0]["gold"] == [1] and res[1]["gold"] == [0]


def test_meetings_assignment_is_order_independent():
    # a weaker entry listed first must not take the gold item from a closer later one
    entries = ["The team will think about the concept.", "ID will create the components concept."]
    res = matcher.match_output(MEETING, entries, sim=SIM)
    assert res[1]["label"] == "true_item" and res[1]["gold"] == [1]


def test_label_entry_uses_earlier_entries():
    assert matcher.label_entry(EMAIL, "Send me the Q3 budget by Friday please",
                               earlier=["Could you send me the Q3 budget"])["label"] == "split_of_true"


def test_dev_only_guard(tmp=None):
    import json
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        Path(d, "manifest.json").write_text(json.dumps({"model_key": "x", "run_id": "x"}))
        Path(d, "raw.jsonl").write_text(json.dumps({"request_id": "eml-0|none|k1|all_1", "arm": None,
                                                    "doc_id": "eml-0", "status": "ok"}) + "\n")
        try:
            list(matcher.dev_outputs([d]))
        except SystemExit as e:
            assert "dev outputs only" in str(e)
        else:
            raise AssertionError("a non-dev run must be refused")


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok  ", name)
            except Exception as e:  # noqa: BLE001
                fails += 1
                print("FAIL", name, repr(e))
    print(f"{fails} failed")
    sys.exit(1 if fails else 0)
