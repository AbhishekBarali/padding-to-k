#!/usr/bin/env python3
"""Bounded prevalence scan for JSON Schema corpora.

Usage examples:
  python3 prevalence_scan.py --input schemas.jsonl --output prevalence_results.json
  python3 prevalence_scan.py --input schemas.json --max-schemas 5000
  python3 prevalence_scan.py --directory checkout/data --output prevalence_results.json
  python3 prevalence_scan.py --url https://example.org/schemas.jsonl.gz --cache-dir /tmp/schema-prevalence

Input may be JSON, JSONL, a directory recursively containing those files, or
gzip-compressed JSON/JSONL. A JSON object can be a schema, a list of schemas,
or a dataset record containing one schema in a common field (schema, json_schema,
parameters, input_schema). The script intentionally uses only Python's standard
library. It never executes or resolves references.

Definitions:
* minItems>=1: an object-valued schema node with integer minItems >= 1.
* exact-length: object-valued node with integer minItems == maxItems.
* required array: a required property whose local declared schema (or its direct
  items under allOf/anyOf/oneOf) has type array. This is conservative.
* concrete-looking metadata: examples, default, or description values that appear
  to provide a concrete example rather than generic documentation. examples and
  default count if non-empty. description counts only with a quoted literal,
  a number/date/URL/email-like token, an all-caps hyphenated identifier, or
  explicit markers such as "e.g." / "for example" / "example:".

All output is a scoping estimate, not a claim about a corpus unless the precise
input, commit/revision, command and source license are recorded by the rerunner.
"""
import argparse
import gzip
import hashlib
import io
import json
import re
import sys
import urllib.request
from collections import Counter
from pathlib import Path

SCHEMA_FIELDS = ("schema", "json_schema", "input_schema", "parameters")
DESC_SAMPLE = re.compile(
    r"(?:\b(?:e\.g\.|for example|example:)\b|['\"][^'\"]{1,80}['\"]|"
    r"\bhttps?://\S+|\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b|"
    r"\b\d{4}-\d\d-\d\d\b|\b[A-Z]{2,}-\d{2,}\b|\b\d+(?:\.\d+)?\b)",
    re.I,
)


def open_input(source, cache_dir):
    """Return bytes and source provenance; download only if --url is used."""
    if source.startswith(("http://", "https://")):
        cache_dir.mkdir(parents=True, exist_ok=True)
        name = hashlib.sha256(source.encode()).hexdigest()[:16] + ".download"
        cached = cache_dir / name
        if not cached.exists():
            print("Downloading", source, file=sys.stderr)
            with urllib.request.urlopen(source, timeout=60) as response:
                data = response.read()
            cached.write_bytes(data)
        return cached.read_bytes(), source
    path = Path(source)
    return path.read_bytes(), str(path.resolve())


def records_from_bytes(data, source_name):
    if source_name.endswith(".gz") or data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    text = data.decode("utf-8")
    stripped = text.lstrip()
    if stripped.startswith("[") or stripped.startswith("{"):
        value = json.loads(text)
        return value if isinstance(value, list) else [value]
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def load_records(source, cache_dir):
    """Load a local file, URL, or recursively scanned local directory."""
    path = Path(source)
    if path.is_dir():
        records = []
        for candidate in sorted(path.rglob("*")):
            if candidate.is_file() and candidate.suffix.lower() in (".json", ".jsonl", ".gz"):
                try:
                    records.extend(records_from_bytes(candidate.read_bytes(), str(candidate)))
                except (UnicodeDecodeError, json.JSONDecodeError, OSError, gzip.BadGzipFile) as exc:
                    print("Skipping", candidate, ":", exc, file=sys.stderr)
        return records, str(path.resolve())
    raw, provenance = open_input(source, cache_dir)
    return records_from_bytes(raw, provenance), provenance


def extract_schema(record):
    if not isinstance(record, dict):
        return None
    for field in SCHEMA_FIELDS:
        value = record.get(field)
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
    # Accept a top-level schema object itself.
    if any(k in record for k in ("type", "properties", "$schema", "items", "allOf", "anyOf", "oneOf")):
        return record
    return None


def looks_array(schema):
    if not isinstance(schema, dict):
        return False
    kind = schema.get("type")
    if kind == "array" or (isinstance(kind, list) and "array" in kind):
        return True
    return any(looks_array(x) for key in ("allOf", "anyOf", "oneOf") for x in schema.get(key, []) if isinstance(x, dict))


def metadata_is_concrete(key, value):
    if key in ("examples", "default"):
        return value not in (None, "", [], {})
    return isinstance(value, str) and bool(DESC_SAMPLE.search(value))


def walk(node, counts, seen):
    if isinstance(node, dict):
        ident = id(node)
        if ident in seen:
            return
        seen.add(ident)
        counts["schema_nodes"] += 1
        if looks_array(node):
            counts["array_nodes"] += 1
            mn, mx = node.get("minItems"), node.get("maxItems")
            if isinstance(mn, int) and mn >= 1:
                counts["array_nodes_minitems_ge_1"] += 1
            if isinstance(mn, int) and isinstance(mx, int) and mn == mx:
                counts["array_nodes_exact_length"] += 1
        for key in ("examples", "default", "description"):
            if metadata_is_concrete(key, node.get(key)):
                counts["metadata_%s_concrete_looking" % key] += 1
        props = node.get("properties")
        required = set(node.get("required", [])) if isinstance(node.get("required"), list) else set()
        if isinstance(props, dict):
            for name, child in props.items():
                if name in required and looks_array(child):
                    counts["required_properties_declared_array"] += 1
                walk(child, counts, seen)
        for key, child in node.items():
            if key == "properties":
                continue
            walk(child, counts, seen)
    elif isinstance(node, list):
        for child in node:
            walk(child, counts, seen)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", help="Local JSON/JSONL(/.gz) file")
    parser.add_argument("--directory", help="Local directory recursively containing JSON/JSONL files")
    parser.add_argument("--url", help="Remote JSON/JSONL(/.gz) URL")
    parser.add_argument("--output", default="prevalence_results.json")
    parser.add_argument("--cache-dir", default="/tmp/schema-prevalence")
    parser.add_argument("--max-schemas", type=int, default=10000)
    args = parser.parse_args()
    sources = [x for x in (args.input, args.directory, args.url) if x]
    if len(sources) != 1:
        parser.error("provide exactly one of --input, --directory, or --url")
    source = sources[0]
    records, provenance = load_records(source, Path(args.cache_dir))
    source_digest = None
    source_path = Path(source)
    if source_path.is_file():
        source_digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
    counts = Counter()
    schema_level_metrics = (
        "array_nodes_minitems_ge_1",
        "array_nodes_exact_length",
        "required_properties_declared_array",
        "metadata_examples_concrete_looking",
        "metadata_default_concrete_looking",
        "metadata_description_concrete_looking",
    )
    for record in records[:args.max_schemas]:
        schema = extract_schema(record)
        if schema is None:
            counts["records_without_recognized_schema"] += 1
            continue
        counts["schemas_scanned"] += 1
        before = {key: counts[key] for key in schema_level_metrics}
        walk(schema, counts, set())
        for key in schema_level_metrics:
            if counts[key] > before[key]:
                counts["schemas_with_" + key] += 1
    result = {
        "label": "scoping estimate computed by Kiro on 2026-10-10; the authors must re-run the script themselves before citing",
        "source": provenance,
        "source_sha256": source_digest,
        "input_records_seen": min(len(records), args.max_schemas),
        "max_schemas": args.max_schemas,
        "definitions": {
            "required_array": "required property whose local schema is array (including direct combinator branches)",
            "concrete_looking_metadata": "non-empty examples/default; description with a conservative sample-value pattern",
        },
        "counts": dict(sorted(counts.items())),
    }
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
