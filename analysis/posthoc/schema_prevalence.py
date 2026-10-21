#!/usr/bin/env python3
"""POST HOC (not in the registered plan): how often do real-world JSON Schemas put "minItems" >= 2 on a list?

Data: JSONSchemaBench (Geng et al. 2025, arXiv:2501.10868), Hugging Face dataset epfl-dlab/JSONSchemaBench,
pinned to one dataset commit (REVISION below), licence MIT. The script downloads the ten named subsets (train,
val and test splits of each; 30 parquet files) into analysis/posthoc/cache/jsonschemabench/<revision>/ (gitignored)
and reads them from there on later runs. The sha256 of every file is written to the JSON output.

For every schema it walks all subschemas (properties, items, prefixItems, additionalItems, contains,
additionalProperties, patternProperties, propertyNames, unevaluated*, anyOf/oneOf/allOf, not, if/then/else,
$defs/definitions, dependentSchemas and schema-valued dependencies). Values of enum, const, default and examples
are data, not schemas, and are not walked. A node is an array schema when its "type" is or includes "array", or
when it has no "type" but has an array keyword (items, prefixItems, minItems, maxItems, additionalItems, contains).

Each array schema is one of:
  tuple        "items" given as a list, or "prefixItems" present (positions, not a list of things)
  fixed        minItems == maxItems (a fixed-length vector)
  open         everything else; only these count as "qualifying" when minItems >= 2
Qualifying arrays are split by item type: string or object items (lists of things) against number or integer
items, or arrays of them (vectors, ranges, coordinates), with everything else as "other" (other arrays,
booleans, mixed, unspecified).
The item type follows local "$ref"s ("#/...") and infers a missing "type" from keywords.

    uv run --no-project --python 3.12 --with pyarrow==26.0.0 python analysis/posthoc/schema_prevalence.py

Outputs: analysis/posthoc/out/schema_prevalence.json and .md, and
paper/final/generated/app_schema_prevalence_rows.tex.
"""
import argparse
import hashlib
import json
import sys
import urllib.request
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATASET = "epfl-dlab/JSONSchemaBench"
REVISION = "5bd0f4640badc6f3f02df796421d21cb0ca0b141"  # dataset commit of 2025-03-31
LICENCE = "MIT"
SUBSETS = ["Github_trivial", "Github_easy", "Github_medium", "Github_hard", "Github_ultra",
           "Glaiveai2K", "JsonSchemaStore", "Kubernetes", "Snowplow", "WashingtonPost"]
SPLITS = ["train", "val", "test"]
CACHE = HERE / "cache" / "jsonschemabench" / REVISION
OUT = HERE / "out"
TEX = ROOT / "paper" / "final" / "generated" / "app_schema_prevalence_rows.tex"

# keyword -> how its value holds subschemas
SINGLE = ("items", "additionalItems", "contains", "additionalProperties", "propertyNames", "not",
          "if", "then", "else", "unevaluatedItems", "unevaluatedProperties")
LISTS = ("anyOf", "oneOf", "allOf", "prefixItems")
MAPS = ("properties", "patternProperties", "$defs", "definitions", "dependentSchemas")
ARRAY_KEYS = ("items", "prefixItems", "minItems", "maxItems", "additionalItems", "contains")


# ---------------------------------------------------------------- walker

def _types(node):
    t = node.get("type")
    if isinstance(t, str):
        return {t}
    if isinstance(t, list):
        return {x for x in t if isinstance(x, str)}
    return set()


def is_array_schema(node):
    if not isinstance(node, dict):
        return False
    if "type" in node:
        return "array" in _types(node)
    return any(k in node for k in ARRAY_KEYS)


def as_int(v):
    """minItems/maxItems as an int, or None when absent or not a whole number."""
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    if isinstance(v, float) and v.is_integer():
        return int(v)
    return None


def _children(node, path):
    """(child, path) pairs of the subschemas directly under a schema node."""
    for k in SINGLE:
        if k in node:
            v = node[k]
            if k == "items" and isinstance(v, list):
                for i, x in enumerate(v):
                    yield x, path + ["items", str(i)]
            else:
                yield v, path + [k]
    for k in LISTS:
        v = node.get(k)
        if isinstance(v, list):
            for i, x in enumerate(v):
                yield x, path + [k, str(i)]
    for k in MAPS:
        v = node.get(k)
        if isinstance(v, dict):
            for name, x in v.items():
                yield x, path + [k, str(name)]
    dep = node.get("dependencies")
    if isinstance(dep, dict):
        for name, x in dep.items():
            if isinstance(x, dict):  # a list here is property names, not a schema
                yield x, path + ["dependencies", str(name)]


def walk(schema):
    """Yield (path, node) for every dict subschema, depth first, each object visited once (cycle-safe).
    A local "$ref" target is walked too (at the path of its pointer), so definitions kept under a
    non-standard key that the schema itself references (e.g. "#/defs/x") are reached."""
    seen = set()
    stack = [(schema, [])]
    while stack:
        node, path = stack.pop()
        if not isinstance(node, dict) or id(node) in seen:
            continue
        seen.add(id(node))
        yield path, node
        kids = list(_children(node, path))
        ref = node.get("$ref")
        if isinstance(ref, str):
            target = pointer(schema, ref)
            if isinstance(target, dict):
                kids.append((target, [p for p in ref[2:].split("/") if p]))
        stack.extend(reversed(kids))


def pointer(root, ref):
    """The value a local JSON pointer ('#', '#/a/b') names in root, or None (external or broken refs)."""
    if not isinstance(ref, str) or not ref.startswith("#"):
        return None
    target = root
    for part in ref[1:].split("/"):
        if not part:
            continue
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(target, dict) and part in target:
            target = target[part]
        elif isinstance(target, list) and part.isdigit() and int(part) < len(target):
            target = target[int(part)]
        else:
            return None
    return target


def resolve(node, root, hops=10):
    """Follow local '$ref' pointers from node; return the final target dict, or node itself."""
    while hops and isinstance(node, dict) and "$ref" in node:
        hops -= 1
        target = pointer(root, node["$ref"])
        if not isinstance(target, dict) or target is node:
            return node
        node = target
    return node


def _kind_of_value(v):
    if isinstance(v, bool):
        return "boolean"
    if isinstance(v, (int, float)):
        return "number"
    if isinstance(v, str):
        return "string"
    if isinstance(v, dict):
        return "object"
    if isinstance(v, list):
        return "array"
    return "other"


def item_kind(items, root, depth=0):
    """string / object / number / array / boolean / mixed / unspecified for an array's item schema."""
    if depth > 10 or not isinstance(items, dict):
        return "unspecified"
    items = resolve(items, root)
    if not isinstance(items, dict):
        return "unspecified"
    ts = _types(items) - {"null"}
    if ts:
        kinds = {"integer": "number"}.get
        ks = {kinds(t, t) for t in ts}
        if ks == {"array"}:
            return _nested(items, root, depth)
        return ks.pop() if len(ks) == 1 else "mixed"
    for key in ("enum", "const"):
        if key in items:
            vals = items[key] if key == "enum" and isinstance(items[key], list) else [items[key]]
            ks = {_kind_of_value(v) for v in vals if v is not None}
            if len(ks) == 1:
                return ks.pop()
            return "mixed" if ks else "unspecified"
    if any(k in items for k in ("properties", "required", "patternProperties", "additionalProperties")):
        return "object"
    if any(k in items for k in ("format", "pattern", "minLength", "maxLength")):
        return "string"
    if any(k in items for k in ("minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf")):
        return "number"
    if any(k in items for k in ARRAY_KEYS):
        return _nested(items, root, depth)
    for key in ("anyOf", "oneOf", "allOf"):
        if isinstance(items.get(key), list) and items[key]:
            ks = {item_kind(b, root, depth + 1) for b in items[key]} - {"unspecified"}
            if len(ks) == 1:
                return ks.pop()
            if ks:
                return "mixed"
    return "unspecified"


def _nested(items, root, depth):
    """An array of arrays: 'number_array' when the inner items are numbers (coordinates, matrices), else 'array'."""
    inner = items.get("items")
    if isinstance(inner, list) and inner:  # a tuple of positions, e.g. [lon, lat]
        ks = {item_kind(x, root, depth + 1) for x in inner}
    else:
        ks = {item_kind(inner, root, depth + 1)}
    return "number_array" if ks and ks <= {"number", "number_array"} else "array"


def kind_group(kind):
    if kind in ("string", "object"):
        return "string_object"
    if kind in ("number", "number_array"):
        return "number"
    return "other"


def classify(node, root):
    """Classification of one array schema node."""
    mn, mx = as_int(node.get("minItems")), as_int(node.get("maxItems"))
    bad_min = "minItems" in node and mn is None
    if isinstance(node.get("items"), list) or "prefixItems" in node:
        shape = "tuple"
    elif mn is not None and mx is not None and mn == mx:
        shape = "fixed"
    else:
        shape = "open"
    kind = item_kind(node.get("items"), root) if shape != "tuple" else "tuple"
    return {"min": mn, "max": mx, "bad_min": bad_min, "shape": shape, "kind": kind, "group": kind_group(kind)}


def raw_min2(obj):
    """True when any object anywhere in the parsed JSON has an integer minItems >= 2 (no keyword rules)."""
    stack, seen = [obj], set()
    while stack:
        o = stack.pop()
        if id(o) in seen:
            continue
        seen.add(id(o))
        if isinstance(o, dict):
            m = as_int(o.get("minItems"))
            if m is not None and m >= 2:
                return True
            stack.extend(o.values())
        elif isinstance(o, list):
            stack.extend(o)
    return False


def arrays_of(schema):
    """[(path, node, classification)] for every array schema in a parsed schema."""
    out = []
    for path, node in walk(schema):
        if is_array_schema(node):
            out.append(("/" + "/".join(path), node, classify(node, schema)))
    return out


# ---------------------------------------------------------------- data

def fetch(force=False):
    """Download (or reuse) the pinned parquet files; return {subset: [(unique_id, json_schema_text)]}, file hashes."""
    import pyarrow.parquet as pq

    rows, hashes = {}, {}
    for sub in SUBSETS:
        rows[sub] = []
        for split in SPLITS:
            rel = f"{sub}/{split}-00000-of-00001.parquet"
            dest = CACHE / rel
            if force or not dest.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                url = f"https://huggingface.co/datasets/{DATASET}/resolve/{REVISION}/{rel}"
                tmp = dest.with_suffix(".part")
                with urllib.request.urlopen(url, timeout=120) as r, open(tmp, "wb") as f:
                    f.write(r.read())
                tmp.replace(dest)
            hashes[rel] = hashlib.sha256(dest.read_bytes()).hexdigest()
            t = pq.read_table(dest, columns=["unique_id", "json_schema"]).to_pylist()
            rows[sub].extend((r["unique_id"], r["json_schema"]) for r in t)
    return rows, hashes


# ---------------------------------------------------------------- counting

def _new():
    return Counter()


def count_subset(sub, items, examples):
    c = _new()
    dist = Counter()        # minItems values on open arrays
    dist_excl = Counter()   # minItems values on fixed / tuple arrays
    fails = []
    for uid, text in items:
        c["schemas"] += 1
        try:
            schema = json.loads(text)
        except Exception as e:  # noqa: BLE001 - report, never crash
            c["parse_fail"] += 1
            fails.append({"unique_id": uid, "error": type(e).__name__})
            continue
        if not isinstance(schema, dict):
            c["parse_fail"] += 1
            fails.append({"unique_id": uid, "error": f"root is {type(schema).__name__}"})
            continue
        arrs = arrays_of(schema)
        flags = set()
        if raw_min2(schema):
            c["raw_min2_anywhere"] += 1
            if not any(a["min"] is not None and a["min"] >= 2 for _, _, a in arrs):
                c["raw_min2_not_reached"] += 1
        for path, node, a in arrs:
            c["arrays"] += 1
            c[f"arrays_{a['shape']}"] += 1
            if a["bad_min"]:
                c["arrays_bad_minItems"] += 1
            if a["min"] is None:
                continue
            if a["shape"] == "open":
                dist[a["min"]] += 1
                if a["min"] >= 1:
                    flags.add("q1")
                    flags.add(f"q1_{a['group']}")
                if a["min"] >= 2:
                    c["qual2_arrays"] += 1
                    c[f"qual2_arrays_{a['group']}"] += 1
                    c[f"qual2_kind_{a['kind']}"] += 1
                    flags.add("q2")
                    flags.add(f"q2_{a['group']}")
                    if len(examples) < 5000:
                        examples.append({"subset": sub, "unique_id": uid, "path": path, "minItems": a["min"],
                                         "maxItems": a["max"], "item_type": a["kind"],
                                         "description": str(node.get("description") or node.get("title") or "")[:90]})
                if a["min"] >= 3:
                    c["qual3_arrays"] += 1
                    flags.add("q3")
                    flags.add(f"q3_{a['group']}")
            else:
                dist_excl[(a["shape"], a["min"])] += 1
                if a["min"] >= 2:
                    flags.add(f"excl2_{a['shape']}")
        if arrs:
            c["with_array"] += 1
        for f in flags:
            c[f"with_{f}"] += 1
    return c, dist, dist_excl, fails


def pct(a, b):
    return round(100.0 * a / b, 1) if b else 0.0


def summarise(c):
    n = c["schemas"]
    q = c["with_q2"]
    return {
        "schemas": n, "parse_fail": c["parse_fail"],
        "pct_any_array": pct(c["with_array"], n),
        "pct_min1_open": pct(c["with_q1"], n),
        "pct_min1_open_string_object": pct(c["with_q1_string_object"], n),
        "pct_min2_open": pct(q, n), "pct_min3_open": pct(c["with_q3"], n),
        "pct_min2_open_string_object": pct(c["with_q2_string_object"], n),
        "pct_min2_open_number": pct(c["with_q2_number"], n),
        "pct_min2_open_other": pct(c["with_q2_other"], n),
        "of_which_string_object_pct": pct(c["with_q2_string_object"], q) if q else None,
        "pct_min2_fixed": pct(c["with_excl2_fixed"], n), "pct_min2_tuple": pct(c["with_excl2_tuple"], n),
        "counts": dict(sorted(c.items())),
    }


def pick_examples(examples, n=15):
    """Deterministic spread: the first string/object example of each subset, then numeric ones, then the rest."""
    chosen, seen = [], set()

    def take(pred):
        for sub in SUBSETS:
            for e in examples:
                if len(chosen) >= n:
                    return
                key = (e["path"], e["minItems"], e["item_type"])
                if e["subset"] == sub and pred(e) and e["unique_id"] not in seen and key not in seen:
                    chosen.append(e)
                    seen.update([e["unique_id"], key])
                    break

    take(lambda e: kind_group(e["item_type"]) == "string_object")
    take(lambda e: kind_group(e["item_type"]) == "number")
    take(lambda e: kind_group(e["item_type"]) == "string_object")
    take(lambda e: True)
    return chosen


def _of(s, blank):
    v = s["of_which_string_object_pct"]
    return blank if v is None else f"{v:.1f}"


def tex_escape(s):
    return s.replace("\\", "\\textbackslash{}").replace("_", "\\_").replace("&", "\\&").replace("%", "\\%")


def write_tex(per, overall):
    lines = ["% generated by analysis/posthoc/schema_prevalence.py from analysis/posthoc/out/schema_prevalence.json"
             " (POST HOC)"]

    def row(name, s):
        return (f"  {name} & {s['schemas']:,} & {s['pct_any_array']:.1f} & {s['pct_min1_open_string_object']:.1f}"
                f" & {s['pct_min2_open']:.1f} & {s['pct_min2_open_string_object']:.1f} \\\\")

    for sub in SUBSETS:
        lines.append(row(tex_escape(sub), per[sub]))
    lines.append("  \\midrule")
    lines.append(row("All", overall))
    TEX.write_text("\n".join(lines) + "\n")


def write_md(res):
    o = res["overall"]
    L = ["# POST HOC: minItems >= 2 on lists in real-world JSON Schemas (JSONSchemaBench)", "",
         "POST HOC: not in the registered plan. Source: `analysis/posthoc/schema_prevalence.py`.", "",
         f"Data: `{DATASET}` at revision `{REVISION}` (licence {LICENCE}), ten subsets, train + val + test.", "",
         "Reproduce (from the repository root; downloads about 21 MB into the gitignored `analysis/posthoc/cache/`):",
         "", "```", "uv run --no-project --python 3.12 --with pyarrow==26.0.0 python analysis/posthoc/schema_prevalence.py",
         "```", "",
         "## Summary", "",
         f"Of {o['schemas']:,} schemas, {o['pct_any_array']:.1f}% contain at least one array. "
         f"{o['pct_min1_open']:.1f}% have an open array with minItems >= 1 "
         f"({o['pct_min1_open_string_object']:.1f}% one whose items are strings or objects). "
         f"{o['pct_min2_open']:.1f}% have an open (not fixed-length, not tuple) array with minItems >= 2, "
         f"and {o['pct_min3_open']:.1f}% one with minItems >= 3. "
         f"{o['pct_min2_open_string_object']:.1f}% of all schemas have such an array whose items are strings or "
         f"objects (a list of things), {o['of_which_string_object_pct']:.1f}% of the schemas with one; "
         f"{o['pct_min2_open_number']:.1f}% have one with number or integer items (vectors, ranges, coordinates). "
         f"({o['counts'].get('with_q2', 0)} schemas; {o['counts'].get('with_q2_string_object', 0)} with string or "
         f"object items.) "
         f"Fixed-length arrays (minItems == maxItems >= 2) occur in {o['pct_min2_fixed']:.1f}% of schemas and "
         f"tuple arrays with minItems >= 2 in {o['pct_min2_tuple']:.1f}%; neither is counted above. "
         f"{o['parse_fail']} schemas failed to parse.", "",
         "## Per subset (% of schemas)", "",
         "| Subset | Schemas | Parse fail | Any array | min>=2 open | min>=3 open | min>=2 str/obj | "
         "min>=2 num | of which str/obj | fixed min>=2 | tuple min>=2 |",
         "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for name, s in list(res["per_subset"].items()) + [("All", o)]:
        L.append(f"| {name} | {s['schemas']:,} | {s['parse_fail']} | {s['pct_any_array']:.1f} | "
                 f"{s['pct_min2_open']:.1f} | {s['pct_min3_open']:.1f} | {s['pct_min2_open_string_object']:.1f} | "
                 f"{s['pct_min2_open_number']:.1f} | {_of(s, '-')} | "
                 f"{s['pct_min2_fixed']:.1f} | {s['pct_min2_tuple']:.1f} |")
    oc = o["counts"]
    L += ["", "## Arrays (all subsets)", "",
          f"{oc.get('arrays', 0):,} array schemas: {oc.get('arrays_open', 0):,} open, {oc.get('arrays_fixed', 0):,} "
          f"fixed-length, {oc.get('arrays_tuple', 0):,} tuple. Open arrays with minItems >= 2: "
          f"{oc.get('qual2_arrays', 0):,} ({oc.get('qual2_arrays_string_object', 0):,} string/object items, "
          f"{oc.get('qual2_arrays_number', 0):,} number/integer, {oc.get('qual2_arrays_other', 0):,} other); "
          f"with minItems >= 3: {oc.get('qual3_arrays', 0):,}.", "",
          "minItems on open arrays: " + ", ".join(f"{k}: {v:,}" for k, v in res["minItems_open_distribution"].items()),
          "", "## Examples of qualifying arrays", "",
          "| Subset | Path | minItems | maxItems | Item type | Description |", "|---|---|---:|---:|---|---|"]
    for e in res["examples"]:
        d = e["description"].replace("|", "/").replace("\n", " ")
        L.append(f"| {e['subset']} | `{e['path']}` | {e['minItems']} | {e['maxItems'] if e['maxItems'] is not None else ''}"
                 f" | {e['item_type']} | {d} |")
    du = res["duplicates"]
    L += ["", "## Caveats", "",
          f"- Duplicates: {du['duplicate_texts']} schema texts occur more than once "
          f"({du['rows_in_duplicates']} rows; {du['cross_subset_texts']} of the texts across subsets). "
          f"Deduplicated by exact text, {du['unique_schemas']:,} schemas, of which "
          f"{du['dedup_pct_min2_open']:.1f}% have an open array with minItems >= 2 "
          f"({du['dedup_pct_min2_open_string_object']:.1f}% string/object).",
          f"- Walker coverage: {oc.get('raw_min2_anywhere', 0)} schemas have an integer minItems >= 2 on some "
          f"object anywhere in their JSON; the walker reaches one in all but {oc.get('raw_min2_not_reached', 0)} "
          "(those sit under non-schema keywords, or the minItems is on a node that is not an array schema).",
          "- Arrays under $defs/definitions are counted whether or not the schema references them.",
          "- Item types follow local $refs only; an external $ref counts as unspecified (\"other\").",
          "- The dataset dropped a few very long Github schemas on 2025-03-31 (see its card); this is the pinned "
          "revision after that change.", ""]
    (OUT / "schema_prevalence.md").write_text("\n".join(L))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--refresh", action="store_true", help="re-download the pinned files")
    args = ap.parse_args()
    rows, hashes = fetch(args.refresh)

    per, examples, tot = {}, [], _new()
    dist_all, excl_all, fails_all = Counter(), Counter(), []
    for sub in SUBSETS:
        c, dist, excl, fails = count_subset(sub, rows[sub], examples)
        per[sub] = summarise(c)
        tot.update(c)
        dist_all.update(dist)
        excl_all.update(excl)
        fails_all += [{"subset": sub, **f} for f in fails]
    overall = summarise(tot)

    # duplicates by exact schema text
    by_text = {}
    for sub in SUBSETS:
        for uid, text in rows[sub]:
            by_text.setdefault(text, []).append(sub)
    dup = {t: s for t, s in by_text.items() if len(s) > 1}
    uniq_items = [(str(i), t) for i, t in enumerate(by_text)]
    uc, _, _, _ = count_subset("unique", uniq_items, [])
    duplicates = {"unique_schemas": len(by_text), "duplicate_texts": len(dup),
                  "rows_in_duplicates": sum(len(s) for s in dup.values()),
                  "cross_subset_texts": sum(1 for s in dup.values() if len(set(s)) > 1),
                  "dedup_pct_min2_open": pct(uc["with_q2"], uc["schemas"]),
                  "dedup_pct_min2_open_string_object": pct(uc["with_q2_string_object"], uc["schemas"]),
                  "dedup_pct_min3_open": pct(uc["with_q3"], uc["schemas"])}

    res = {
        "posthoc": True,
        "dataset": DATASET, "revision": REVISION, "licence": LICENCE,
        "source": f"https://huggingface.co/datasets/{DATASET}/tree/{REVISION}",
        "subsets": SUBSETS, "splits": SPLITS, "file_sha256": hashes,
        "definitions": {
            "array schema": "type is/includes 'array', or no type and an array keyword",
            "tuple": "items is a list, or prefixItems present",
            "fixed": "minItems == maxItems",
            "qualifying": "open (not tuple, not fixed) array with integer minItems >= 2",
            "item groups": "string_object = string or object items; number = number or integer items, or arrays of them (coordinates); other = rest",
            "pct": "percent of schemas in the subset (parse failures stay in the denominator)",
            "of_which_string_object_pct": "percent of schemas with a qualifying array that have one with string/object items",
        },
        "overall": overall, "per_subset": per,
        "minItems_open_distribution": {str(k): v for k, v in sorted(dist_all.items())},
        "minItems_excluded_distribution": {f"{s}:{m}": v for (s, m), v in sorted(excl_all.items())},
        "duplicates": duplicates, "parse_failures": fails_all,
        "examples": pick_examples(examples),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "schema_prevalence.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n")
    write_md(res)
    write_tex(per, overall)
    print(json.dumps({k: overall[k] for k in overall if k != "counts"}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
