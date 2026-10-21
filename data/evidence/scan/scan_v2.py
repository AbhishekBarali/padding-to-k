#!/usr/bin/env python3
"""Per-subset prevalence scan (copy-derived from
schema-fab-HI-2026-10-10/prevalence_scan.py; the original is imported, not edited).

Two modes per subset:
  * "orig"   -- exactly the original walk() (it also descends into the VALUES of
                examples/default/enum/const, so data that happens to look like a
                schema node is counted; kept for comparability with the 2026-10-10 run).
  * "strict" -- same counters, but never descends into examples/default/enum/const/
                example values, and additionally counts the OpenAPI-style singular
                `example` keyword (metadata_example_concrete_looking).

Schema-level unit: one record (one file / one dataset row / one tool) = one schema.
Also exports samples (JSONL) of minItems>=1 array fields and examples/default fields.

Usage:
  scan_v2.py --name NAME --records-jsonl FILE   (each line {"subset":..,"source":..,"schema":{..}})
  scan_v2.py --name NAME --dir DIR [--subset-depth 1]
"""
import argparse, hashlib, importlib.util, json, sys
from collections import Counter, defaultdict
from pathlib import Path

ORIG = str(Path(__file__).resolve().parent / "prevalence_scan.py")
spec = importlib.util.spec_from_file_location("orig", ORIG)
orig = importlib.util.module_from_spec(spec); spec.loader.exec_module(orig)

import re
EG = re.compile(r"\b(?:e\.g\.|for example|examples?:)", re.I)
DATA_KEYS = {"examples", "default", "enum", "const", "example"}
SCHEMA_METRICS = ("array_nodes_minitems_ge_1", "array_nodes_exact_length",
                  "required_properties_declared_array", "metadata_examples_concrete_looking",
                  "metadata_default_concrete_looking", "metadata_description_concrete_looking",
                  "metadata_example_concrete_looking", "array_nodes_minitems_ge_1_no_maxitems",
                  "array_nodes_minitems_ge_2", "metadata_description_eg_marker")


def walk_strict(node, counts, seen, path, sink):
    if isinstance(node, dict):
        if id(node) in seen:
            return
        seen.add(id(node))
        counts["schema_nodes"] += 1
        if orig.looks_array(node):
            counts["array_nodes"] += 1
            mn, mx = node.get("minItems"), node.get("maxItems")
            if isinstance(mn, int) and not isinstance(mn, bool) and mn >= 1:
                counts["array_nodes_minitems_ge_1"] += 1
                if mn >= 2:
                    counts["array_nodes_minitems_ge_2"] += 1
                if "maxItems" not in node:
                    counts["array_nodes_minitems_ge_1_no_maxitems"] += 1
                sink["minitems"].append((path, node))
            if isinstance(mn, int) and isinstance(mx, int) and mn == mx:
                counts["array_nodes_exact_length"] += 1
        for key in ("examples", "default", "description", "example"):
            k2 = "examples" if key == "example" else key
            if key in node and orig.metadata_is_concrete(k2, node.get(key)):
                counts["metadata_%s_concrete_looking" % key] += 1
                if key != "description":
                    sink["meta"].append((path, key, node))
        d = node.get("description")
        if isinstance(d, str) and EG.search(d):
            counts["metadata_description_eg_marker"] += 1
        props = node.get("properties")
        req = set(node.get("required", [])) if isinstance(node.get("required"), list) else set()
        if isinstance(props, dict):
            for name, child in props.items():
                if name in req and orig.looks_array(child):
                    counts["required_properties_declared_array"] += 1
                walk_strict(child, counts, seen, path + "/properties/" + str(name), sink)
        for key, child in node.items():
            if key == "properties" or key in DATA_KEYS:
                continue
            walk_strict(child, counts, seen, path + "/" + str(key), sink)
    elif isinstance(node, list):
        for i, child in enumerate(node):
            walk_strict(child, counts, seen, path + "/" + str(i), sink)


def scan(records):
    """records: iterable of (subset, source, schema_or_record). Returns per-subset dict."""
    out = defaultdict(lambda: {"orig": Counter(), "strict": Counter()})
    samples = {"minitems": [], "meta": []}
    for subset, source, rec in records:
        schema = orig.extract_schema(rec)
        groups = [subset, "__ALL__"]
        if subset.startswith("Github_"):
            groups.insert(1, "Github_ALL_TIERS")
        for grp in groups:
            if schema is None:
                out[grp]["orig"]["records_without_recognized_schema"] += 1
                out[grp]["strict"]["records_without_recognized_schema"] += 1
        if schema is None:
            continue
        # orig
        c = Counter(); orig.walk(schema, c, set())
        # strict
        s = Counter(); sink = {"minitems": [], "meta": []}
        walk_strict(schema, s, set(), "#", sink)
        for grp in groups:
            for mode, cc in (("orig", c), ("strict", s)):
                tgt = out[grp][mode]
                tgt["schemas_scanned"] += 1
                tgt.update(cc)
                for m in SCHEMA_METRICS:
                    if cc.get(m):
                        tgt["schemas_with_" + m] += 1
        for p, n in sink["minitems"]:
            samples["minitems"].append({"subset": subset, "source": source, "pointer": p, "node": n})
        for p, k, n in sink["meta"]:
            samples["meta"].append({"subset": subset, "source": source, "pointer": p, "keyword": k, "node": n})
    res = {g: {m: dict(sorted(v.items())) for m, v in d.items()} for g, d in sorted(out.items())}
    return res, samples


def dir_records(root, depth):
    root = Path(root)
    for f in sorted(root.rglob("*")):
        if not f.is_file() or f.suffix.lower() not in (".json", ".jsonl", ".gz"):
            continue
        rel = f.relative_to(root)
        subset = "/".join(rel.parts[:depth]) if len(rel.parts) > depth else "(root)"
        try:
            recs = orig.records_from_bytes(f.read_bytes(), str(f))
        except Exception as exc:  # noqa
            print("skip", f, exc, file=sys.stderr); continue
        for i, r in enumerate(recs):
            yield subset, str(rel) + ("" if len(recs) == 1 else "#%d" % i), r


def jsonl_records(path):
    with open(path) as fh:
        for line in fh:
            if line.strip():
                d = json.loads(line)
                yield d["subset"], d["source"], d["schema"]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--dir"); ap.add_argument("--subset-depth", type=int, default=1)
    ap.add_argument("--records-jsonl")
    ap.add_argument("--outdir", default="results")
    a = ap.parse_args()
    recs = dir_records(a.dir, a.subset_depth) if a.dir else jsonl_records(a.records_jsonl)
    res, samples = scan(recs)
    outdir = Path(a.outdir); outdir.mkdir(parents=True, exist_ok=True)
    o = outdir / ("%s_per_subset.json" % a.name)
    o.write_text(json.dumps({"input": a.dir or a.records_jsonl, "results": res}, indent=1, sort_keys=True) + "\n")
    with open(outdir / ("%s_samples_minitems.jsonl" % a.name), "w") as fh:
        for s in samples["minitems"]:
            fh.write(json.dumps(s, sort_keys=True) + "\n")
    with open(outdir / ("%s_samples_meta.jsonl" % a.name), "w") as fh:
        for s in samples["meta"]:
            fh.write(json.dumps(s, sort_keys=True) + "\n")
    print(o, hashlib.sha256(o.read_bytes()).hexdigest())
