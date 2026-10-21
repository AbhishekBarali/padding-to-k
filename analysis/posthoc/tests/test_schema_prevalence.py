"""POST HOC: tests for the JSON Schema walker in schema_prevalence.py (hand-written schemas, no network)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import schema_prevalence as sp  # noqa: E402


def found(schema):
    return {path: a for path, _, a in sp.arrays_of(schema)}


def test_nested_keywords_are_walked():
    schema = {
        "type": "object",
        "properties": {
            "skills": {"type": "array", "minItems": 3, "items": {"type": "string"}},
            "box": {"anyOf": [{"type": "null"}, {"type": "array", "minItems": 2, "items": {"type": "number"}}]},
        },
        "$defs": {"people": {"type": "array", "minItems": 2, "items": {"$ref": "#/$defs/person"}},
                  "person": {"type": "object", "properties": {"name": {"type": "string"}}}},
        "definitions": {"tags": {"type": ["array", "null"], "minItems": 1}},
        "patternProperties": {"^x-": {"not": {"type": "array"}}},
        "additionalProperties": {"if": {"type": "array"}, "then": {"minItems": 2}, "else": {"type": "string"}},
        "dependentSchemas": {"a": {"properties": {"b": {"type": "array", "items": {"type": "integer"}}}}},
        "dependencies": {"c": ["d"]},
        "enum": [{"type": "array", "minItems": 9}],  # data, not a schema: never walked
    }
    arrs = found(schema)
    assert set(arrs) == {"/properties/skills", "/properties/box/anyOf/1", "/$defs/people", "/definitions/tags",
                         "/patternProperties/^x-/not", "/additionalProperties/if", "/additionalProperties/then",
                         "/dependentSchemas/a/properties/b"}
    assert arrs["/properties/skills"]["kind"] == "string" and arrs["/properties/skills"]["min"] == 3
    assert arrs["/properties/box/anyOf/1"]["group"] == "number"
    assert arrs["/$defs/people"]["kind"] == "object"  # item type through a local $ref
    assert arrs["/dependentSchemas/a/properties/b"]["kind"] == "number"


def test_fixed_and_tuple_are_not_open():
    schema = {"properties": {
        "rgb": {"type": "array", "minItems": 3, "maxItems": 3, "items": {"type": "integer"}},
        "pair": {"type": "array", "items": [{"type": "string"}, {"type": "number"}], "minItems": 2},
        "pair2020": {"type": "array", "prefixItems": [{"type": "string"}], "minItems": 2},
        "range": {"type": "array", "minItems": 2, "maxItems": 4, "items": {"type": "string"}},
    }}
    arrs = found(schema)
    assert arrs["/properties/rgb"]["shape"] == "fixed"
    assert arrs["/properties/pair"]["shape"] == "tuple"
    assert arrs["/properties/pair2020"]["shape"] == "tuple"
    assert arrs["/properties/range"]["shape"] == "open"
    # tuple members are still walked as subschemas
    assert "/properties/pair/items/0" not in arrs


def test_odd_values_and_cycles():
    a = {"type": "array", "minItems": "2", "items": True}
    b = {"type": "array", "minItems": 2.0, "items": {"enum": ["x", "y"]}}
    c = {"type": "array", "minItems": True, "items": {"properties": {}}}
    schema = {"properties": {"a": a, "b": b, "c": c, "weird": 5, "list": [1, 2]}, "anyOf": "nope"}
    schema["properties"]["self"] = schema  # a cycle must not loop
    arrs = found(schema)
    assert arrs["/properties/a"]["min"] is None and arrs["/properties/a"]["bad_min"]
    assert arrs["/properties/a"]["kind"] == "unspecified"
    assert arrs["/properties/b"]["min"] == 2 and arrs["/properties/b"]["kind"] == "string"
    assert arrs["/properties/c"]["min"] is None and arrs["/properties/c"]["kind"] == "object"
    assert len(arrs) == 3


def test_coordinates_and_non_standard_defs_via_ref():
    schema = {"properties": {"line": {"$ref": "#/defs/line"}},
              "defs": {"line": {"type": "array", "minItems": 2,
                                "items": {"type": "array", "minItems": 2, "items": {"type": "number"}}}}}
    arrs = found(schema)
    assert arrs["/defs/line"]["kind"] == "number_array" and arrs["/defs/line"]["group"] == "number"
    assert arrs["/defs/line/items"]["kind"] == "number"
    assert sp.raw_min2(schema)


def test_count_subset_flags():
    rows = [("1", '{"type": "array", "minItems": 2, "items": {"type": "string"}}'),
            ("2", '{"type": "object", "properties": {"v": {"type": "array", "minItems": 3, "maxItems": 3}}}'),
            ("3", '{"type": "object"}'),
            ("4", "{not json")]
    c, dist, excl, fails = sp.count_subset("t", rows, [])
    assert c["schemas"] == 4 and c["parse_fail"] == 1 and fails[0]["unique_id"] == "4"
    assert c["with_array"] == 2 and c["with_q2"] == 1 and c["with_q2_string_object"] == 1
    assert c["with_excl2_fixed"] == 1 and dist == {2: 1} and excl == {("fixed", 3): 1}
