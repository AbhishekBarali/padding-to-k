"""POST HOC: tests for the lenient parser and the grounding normalisation."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common_posthoc as cp  # noqa: E402
import lenient_08b as lp  # noqa: E402

SCHEMA_COPY = '```json\n{"type": "object", "properties": {"requests": ["Send the file", "Call Bob"]}, "required": ["requests"]}\n```'
SCHEMA_ITEMS = '{"type": "object", "properties": {"skills": {"type": "array", "items": ["Python", "SQL"], "minItems": 3}}}'
SCHEMA_ECHO = '{"type": "object", "properties": {"skills": {"type": "array", "items": {"type": "string"}}}}'
WRAPPER = '{"answer": {"requests": ["A", "B"]}}'
PLAIN = '{"requests": ["only one"]}'


def test_locked_parser_refuses_schema_copy():
    assert cp.common.parse_output(SCHEMA_COPY, "requests")["items"] is None


def test_schema_copy():
    out = lp.parse_lenient(SCHEMA_COPY, "requests")
    assert out["items"] == ["Send the file", "Call Bob"] and out["parse_rung"] == "lenient_schema_copy"


def test_schema_copy_items():
    out = lp.parse_lenient(SCHEMA_ITEMS, "skills")
    assert out["items"] == ["Python", "SQL"] and out["parse_rung"] == "lenient_schema_copy_items"


def test_pure_echo_stays_unreadable():
    assert lp.parse_lenient(SCHEMA_ECHO, "skills")["items"] is None


def test_wrapper():
    assert lp.parse_lenient(WRAPPER, "requests")["items"] == ["A", "B"]


def test_readable_output_unchanged():
    assert lp.parse_lenient(PLAIN, "requests") == cp.common.parse_output(PLAIN, "requests")


def test_gnorm():
    assert cp.gnorm("  \u201cSend the File.\u201d ") == "send the file"
    assert cp.gnorm("a \u2013 b\n c") == "a - b c"
    assert cp.gnorm("...") == ""
