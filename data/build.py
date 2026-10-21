#!/usr/bin/env python3
"""Rebuild every file in data/ from the pinned original datasets.

    python build.py                 download (once, into $PADK_CACHE or ~/.cache/pad-to-k) and rebuild
    python build.py check           integrity checks on the built files
    python build.py kappa A.csv B.csv   agreement between two filled-in copies of verify_sheet.csv

Everything here is deterministic: same pinned sources + same SEED = byte-identical outputs.
Gold items are copied from the original annotators by the loaders in sources/; this file
selects documents, writes the prompts/schemas for each test condition, and derives the correct
answer for each condition from the gold list (handbook Part 3.3). The only changes to an annotator
list come from the reviewed decisions in cleanup/decisions.jsonl (see apply_cleanup.py), applied
after selection, with the original list kept next to every change.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import json
import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from sources import _common  # noqa: E402
import apply_cleanup  # noqa: E402

SEED = 20261013
K_VALUES = [1, 3, 5]
PILOT_K = [3, 5]
PILOT_CONDITIONS = ["min_k_shown", "max_k_shown"]
ESCAPE_VALUE = "N/A"
MAIN_N = [0, 1, 2, 3]
ARM_N = [4, 5, 6]          # k < n arm
# candidates per cell, over-sampled by about half so checkers can drop bad ones without a rebuild
PILOT_PER_CELL = 15        # final target 10
FULL_PER_CELL = 23         # final target 15 (pilot candidates count towards it for pilot sets)
ARM_PER_CELL = 5           # final target about 3 per n, about 10 per set
RESERVE_PER_CELL = 8       # replacements, no requests generated until promoted
# Final numbers per cell (README section 4), applied after the cleanup and the authors' check (13 Oct
# 2026): pilot 10 per n in the pilot sets, 15 per n for n = 0-3 (pilot counts towards it), 10 per set in
# the k < n arm. Over-full cells keep the documents whose lengths best match the rest of their set; the
# others stay as checked spares. Set FINAL_TARGETS = None to keep every candidate instead.
FINAL_TARGETS = {"pilot": 10, "full": 15, "arm_per_set": 10}
# Second batch of spares (13 Oct 2026). The cleanup pass (cleanup/) dropped so many documents in these
# cells that the first spares could not refill them. These are picked after every other cell, from
# groups nothing else uses, so the first selection stays exactly as it was. Same rules, same seed.
EXTRA_SPARES = {
    "emails": {3: 45, 4: 12, 5: 2},
    "job_posts": {1: 20, 2: 30, 3: 25, 5: 8, 6: 8},
    "job_posts_knowledge": {1: 15, 3: 20},
    "reviews": {1: 25, 2: 50, 3: 70, 6: 6},
}

# ---------------------------------------------------------------------------------------------
# What each list asks for. `field` is the JSON key; `one`/`many` are used in prompts; `describe`
# goes into the schema and follows the original annotation guideline as closely as possible. Five of them
# also state, in a few words, the counting rule (cleanup/COUNTING_RULES.md) that decided most of the
# disagreements in the first blind check (DECISIONS.md, 15 Oct): M4/M6/M8, E4, J2, K1/K2 and C1.
LISTS = {
    "action_items": dict(field="action_items", one="action item", many="action items",
                         describe="Next steps that a meeting participant will take after this meeting, "
                                  "one per job. One short sentence each. Not decisions, and not "
                                  "instructions they will receive."),
    "requests": dict(field="requests", one="request", many="requests",
                     describe="Things the sender asks the recipient to do or to provide, one per thing "
                              "asked. Copy each request as written in the email."),
    "line_items": dict(field="line_items", one="item", many="items",
                       describe="Names of the items purchased on this receipt, one entry per item, "
                                "copied as printed."),
    "skills": dict(field="skills", one="skill", many="skills",
                   describe="Skills, abilities and duties the job ad mentions, copied as written. Not "
                            "tools, technologies, fields of knowledge, languages or certificates."),
    "knowledge": dict(field="knowledge", one="tool, technology or field of knowledge",
                      many="tools, technologies and fields of knowledge",
                      describe="Tools, technologies, fields of knowledge, languages and certificates the "
                               "job ad mentions, copied as written. Not abilities or duties."),
    "medications": dict(field="medications", one="medication", many="medications",
                        describe="Medications or drugs, by name or by class, mentioned as given to or "
                                 "taken by the patient, copied as written."),
    "features": dict(field="features", one="feature", many="features",
                     describe="Features or aspects of the product or service that the reviewer gives "
                              "an opinion on, copied as written."),
    "people": dict(field="people", one="person", many="people",
                   describe="Names of people mentioned in the text, copied as written."),
    "quotations": dict(field="quotations", one="quotation", many="quotations",
                       describe="Direct speech quoted in the text, copied word for word."),
}


def _no_flag(*prefixes):
    def f(u):
        return any(fl.startswith(p) for fl in u["flags"] for p in prefixes)
    return f


# Each set = one list type from one source. role: pilot (pilot + full), main, itemtype.
# exclude: units never used. prefer: sort key, lower is better. balance: round-robin key.
SETS = [
    dict(set_id="meetings", prefix="mtg", source="ami", list_type="action_items", role="pilot",
         n_main=MAIN_N, n_arm=ARM_N, promote_to_pilot={2: ["full"]},
         exclude=_no_flag("n0_suspect"),
         prefer=lambda u: (("maybe_missing_item:assignment_talk" in u["flags"]),
                           ("short_margin" in u["flags"])),
         balance=lambda u: u["meta"].get("series_letter", "")),
    dict(set_id="emails", prefix="eml", source="mailex", list_type="requests", role="pilot",
         n_main=MAIN_N, n_arm=ARM_N, promote_to_pilot={2: ["full", "reserve"]},
         exclude=_no_flag("maybe_missing_item:request_cue", "outside_preferred_30_400_words",
                          "text_from_tokens"),
         prefer=lambda u: (("request_cue_outside_gold" in u["flags"]),
                           ("item_span_rule_fallback" in u["flags"]),
                           ("subject_has_request_cue" in u["flags"])),
         balance=None, length_target=65),
    dict(set_id="receipts", prefix="rcp", source="cord", list_type="line_items", role="main",
         n_main=[1, 2, 3], n_arm=ARM_N,
         exclude=_no_flag("void_menu_present", "gold_word_order_from_layout"),
         prefer=lambda u: (("has_sub_items" in u["flags"]), ("gold_dedup" in u["flags"])),
         balance=None),
    dict(set_id="job_posts", prefix="job", source="skillspan", list_type="skills", role="main",
         n_main=MAIN_N, n_arm=ARM_N,
         exclude=_no_flag("gold_contains_placeholder", "gold_is_placeholder"),
         prefer=lambda u: (("single_annotator" in u["flags"]),
                           (u["n"] == 0 and not any(f.startswith("n0_other_type_spans_in_window")
                                                    for f in u["flags"]))),
         balance=None),
    dict(set_id="clinical", prefix="med", source="maccrobat", list_type="medications", role="main",
         n_main=MAIN_N, n_arm=ARM_N,
         exclude=_no_flag("item_also_negated_or_hedged_in_window"),
         prefer=lambda u: (any(f.startswith("generic_item") for f in u["flags"]),
                           ("negated_mentions_present" in u["flags"])),
         balance=None, length_target=85),
    dict(set_id="reviews", prefix="rev", source="roast", list_type="features", role="main",
         n_main=[1, 2, 3], n_arm=ARM_N,
         exclude=_no_flag("n0_weak", "mojibake_present", "maybe_dropped_initial_chars", "nested_gold_items"),
         prefer=lambda u: (any(f.startswith("maybe_missing_item") for f in u["flags"]),
                           ("implicit_target_opinions_present" in u["flags"])),
         balance=lambda u: u["meta"].get("domain", "")),
    # item-type comparison inside one genre: same job-ad windows, named things vs skill phrases
    dict(set_id="job_posts_knowledge", prefix="jbk", source="skillspan", list_type="knowledge",
         role="itemtype", n_main=MAIN_N, n_arm=[],
         exclude=_no_flag("gold_contains_placeholder", "gold_is_placeholder"),
         prefer=lambda u: (("single_annotator" in u["flags"]),),
         balance=None),
    # item-type comparison across two more genres (short Wikipedia sentences, novel paragraphs)
    dict(set_id="wiki_people", prefix="ppl", source="fewnerd", list_type="people",
         role="itemtype", n_main=MAIN_N, n_arm=[],
         exclude=lambda u: (_no_flag("names_share_token", "same_person_multiple_forms",
                                     "io_span_has_separator")(u)
                            or not 15 <= u["meta"]["words"] <= 45),
         prefer=lambda u: (("pronoun_person_reference_present" in u["flags"]),),
         balance=None),
    dict(set_id="novel_quotes", prefix="quo", source="pdnc", list_type="quotations",
         role="itemtype", n_main=MAIN_N, n_arm=[],
         # texts still in copyright outside the US are left out of a public release
         exclude=lambda u: (_no_flag("text_copyright_outside_us_until", "speech_verb_no_quote_marks")(u)
                            or not 60 <= u["meta"]["words"] <= 160),
         prefer=lambda u: (any(f.startswith("interrupted_quote") for f in u["flags"]),),
         balance=lambda u: u["meta"].get("novel", ""), length_target=95),
]

# Conditions, in the order of handbook Part 3.3.
CONDITIONS = ["none", "prose_up_to_k", "prose_exactly_k", "max_k_shown",
              "min_k_shown", "min_k_enforced", "min_k_escape"]
PROSE = {"prose_up_to_k": "up_to_k", "prose_exactly_k": "exactly_k", "min_k_escape": "escape"}


# ---------------------------------------------------------------------------------------------
def load_set_units(set_cfg, cache, unit_cache):
    name = set_cfg["source"]
    if name not in unit_cache:
        mod = importlib.import_module(f"sources.{name}")
        _common.check_source(mod.SOURCE)
        mod.fetch(cache)
        units = []
        for u in mod.units(cache):
            _common.check_unit(u)
            units.append(u)
        units.sort(key=lambda u: u["source_id"])
        unit_cache[name] = (mod.SOURCE, units)
    source, units = unit_cache[name]
    return source, [u for u in units if u["list_type"] == set_cfg["list_type"]]


def pick(cands, count, rng, prefer, balance, used_groups, length_target=None):
    pool = [u for u in cands if u["group"] not in used_groups]
    order = list(range(len(pool)))
    rng.shuffle(order)
    rank = {id(pool[i]): r for r, i in enumerate(order)}
    # optional length matching: prefer documents near one common length for every n, in 20-word steps
    near = (lambda u: abs(_common.words(u["text"]) - length_target) // 20) if length_target else (lambda u: 0)
    pool.sort(key=lambda u: (prefer(u), near(u), rank[id(u)]))
    if balance:
        buckets = defaultdict(list)
        for u in pool:
            buckets[balance(u)].append(u)
        keys = sorted(buckets)
        pool = []
        while any(buckets[k] for k in keys):
            for k in keys:
                if buckets[k]:
                    pool.append(buckets[k].pop(0))
    chosen, seen = [], set()
    for u in pool:
        if len(chosen) == count:
            break
        if u["group"] in seen:
            continue
        chosen.append(u)
        seen.add(u["group"])
    used_groups.update(seen)
    return chosen


def select(set_cfg, units):
    """Return [(split, unit)] for one set. One unit per original group (meeting, posting, report)."""
    rng = random.Random(f"{SEED}-{set_cfg['set_id']}")
    eligible, seen_text = [], set()
    for u in units:                      # units are sorted by source_id, so the first copy wins
        if set_cfg["exclude"](u) or u["text"] in seen_text:
            continue
        seen_text.add(u["text"])
        eligible.append(u)
    by_n = defaultdict(list)
    for u in eligible:
        by_n[u["n"]].append(u)
    cells = []
    for n in set_cfg["n_main"]:
        if set_cfg["role"] == "pilot" and n in (0, 1, 2):
            cells += [(n, "pilot", PILOT_PER_CELL), (n, "full", FULL_PER_CELL - PILOT_PER_CELL)]
        else:
            cells.append((n, "full", FULL_PER_CELL))
        cells.append((n, "reserve", RESERVE_PER_CELL))
    for n in set_cfg["n_arm"]:
        cells.append((n, "full", ARM_PER_CELL))
    # scarcest n first, so plentiful cells cannot use up the groups a scarce cell needs
    avail = {n: len({u["group"] for u in by_n[n]}) for n in by_n}
    split_rank = {"pilot": 0, "full": 1, "reserve": 2}
    cells.sort(key=lambda c: (c[0] in set_cfg["n_arm"], avail.get(c[0], 0), c[0], split_rank[c[1]]))
    used, out, shortfall = set(), [], []
    for n, split, count in cells:
        got = pick(by_n[n], count, rng, set_cfg["prefer"], set_cfg["balance"], used,
                   set_cfg.get("length_target"))
        out += [(split, u) for u in got]
        if len(got) < count:
            shortfall.append({"n": n, "split": split, "wanted": count, "got": len(got)})
    # extra pilot candidates where the AI pre-check found the most problems (n = 2), moved over
    # after sampling so the rest of the selection stays exactly as it was
    promote = set_cfg.get("promote_to_pilot", {})
    out = [("pilot" if split in promote.get(u["n"], []) else split, u) for split, u in out]
    for n, count in sorted(EXTRA_SPARES.get(set_cfg["set_id"], {}).items()):
        got = pick(by_n[n], count, rng, set_cfg["prefer"], set_cfg["balance"], used,
                   set_cfg.get("length_target"))
        out += [("reserve", dict(u, spare_batch=2)) for u in got]
        if len(got) < count:
            shortfall.append({"n": n, "split": "spare_batch_2", "wanted": count, "got": len(got)})
    return out, shortfall, len(units) - len(eligible)


# ---------------------------------------------------------------------------------------------
def schema_for(list_type, condition, k):
    spec = LISTS[list_type]
    items = {"type": "string"}
    arr = {"type": "array", "description": spec["describe"], "items": items}
    if condition == "max_k_shown":
        arr["maxItems"] = k
    elif condition in ("min_k_shown", "min_k_enforced"):
        arr["minItems"] = k
    elif condition == "min_k_escape":
        arr["minItems"] = k
        items["description"] = f"If the information is not available, use {ESCAPE_VALUE}."
    return {"type": "object", "properties": {spec["field"]: arr},
            "required": [spec["field"]], "additionalProperties": False}


def fill(template, list_type, k):
    spec = LISTS[list_type]
    return (template.replace("{k}", str(k))
            .replace("{list_name}", spec["one"] if k == 1 else spec["many"])
            .replace("{list_name_plural}", spec["many"])
            .replace("{escape}", ESCAPE_VALUE))


def load_wordings():
    """Study wordings, taken from the real-world collection in wordings.yaml.

    Only change made to a real template: "this page" -> "this document" (our inputs are not web pages).
    The no-count base follows the most common real family ("List all the ...", e.g. row 5108801).
    The escape condition uses escape_4 ("use N/A"), which also works when minItems forces k entries.
    The schema block is LangChain's JSON format instructions as ScrapeGraphAI sent them in 2025.
    """
    cats = yaml.safe_load((HERE / "wordings.yaml").read_text())["categories"]
    adapt = lambda t: t.replace("this page", "this document")
    out = {
        "no_count": [("all_1", "List all the {list_name_plural}.")],
        "up_to_k": [(t["id"], adapt(t["template"])) for t in cats["up_to_k"]["templates"]],
        "exactly_k": [(t["id"], adapt(t["template"])) for t in cats["exactly_k"]["templates"]],
        "escape": [(t["id"], t["template"]) for t in cats["escape"]["templates"] if t["id"] == "escape_4"],
    }
    lc = next(t for t in cats["schema_in_prompt"]["templates"] if t["id"] == "langchain_json_2025")["text"]
    body = lc.split('"""', 1)[1].rsplit('"""', 1)[0].replace("{{", "{").replace("}}", "}")
    out["schema_in_prompt"] = [("langchain_json_2025", body)]
    li = next(t for t in cats["schema_in_prompt"]["templates"] if t["id"] == "llamaindex_pydantic")["text"]
    out["schema_blocks_extra"] = [("llamaindex_pydantic", li.split('"""', 1)[1].rsplit('"""', 1)[0].strip())]
    return out


# Robustness arms, pilot documents only, never part of the main grid (requests_robustness.jsonl):
#   block_llamaindex  the same prompts with LlamaIndex's schema block, which has no 2-item example list
#                     (the LangChain block shows {"foo": ["bar", "baz"]}, a possible length anchor)
#   base_neutral      the same prompts with a base sentence without "all" (constructed, not from the
#                     real-world collection), because "List all the ..." may push toward completeness
ROBUSTNESS_ARMS = {
    "block_llamaindex": {"schema_block_id": "llamaindex_pydantic", "base": ("all_1", "List all the {list_name_plural}.")},
    "base_neutral": {"schema_block_id": "langchain_json_2025",
                     "base": ("neutral_1", "Extract the {list_name_plural} from this document.")},
}
ROBUSTNESS_CONDITIONS = ["none", "max_k_shown", "min_k_shown", "min_k_enforced"]


# Dev requests on the reserve documents (clean, checked, never in the study): model outputs on these are
# what the item matcher's thresholds are fitted on, so the matcher is tuned without looking at study
# outputs (requests_dev.jsonl). A reserve document promoted later keeps these ids (they end in |dev).
DEV_CONDITIONS = ["none", "max_k_shown", "min_k_shown", "min_k_enforced"]


def dev_requests(doc, wordings):
    wid, wtext = wordings["no_count"][0]
    block = wordings["schema_in_prompt"][0][0]
    return [{"request_id": f"{doc['doc_id']}|{cond}|k{k}|{wid}|dev", "doc_id": doc["doc_id"],
             "split": doc["split"], "set": doc["set"], "condition": cond, "k": k, "n": doc["n"],
             "wording_id": wid, "instruction": fill(wtext, doc["list_type"], k),
             "schema_id": schema_id(doc["list_type"], cond, k), "schema_block_id": block,
             "enforce_schema": cond == "min_k_enforced", "in_pilot_run": False, "arm": "dev"}
            for cond in DEV_CONDITIONS for k in K_VALUES]


def robustness_requests(doc):
    rows = []
    for arm, spec in ROBUSTNESS_ARMS.items():
        wid, wtext = spec["base"]
        for cond in ROBUSTNESS_CONDITIONS:
            for k in K_VALUES:
                rows.append({
                    "request_id": f"{doc['doc_id']}|{cond}|k{k}|{wid}|{arm}", "doc_id": doc["doc_id"],
                    "split": doc["split"], "set": doc["set"], "condition": cond, "k": k, "n": doc["n"],
                    "wording_id": wid, "instruction": fill(wtext, doc["list_type"], k),
                    "schema_id": schema_id(doc["list_type"], cond, k), "schema_block_id": spec["schema_block_id"],
                    "enforce_schema": cond == "min_k_enforced", "in_pilot_run": False, "arm": arm,
                })
    return rows


USER_MESSAGE = 'INSTRUCTION\n\nSCHEMA_BLOCK\n\nDocument:\n"""\nDOCUMENT\n"""'


def schema_id(list_type, cond, k):
    return f"{list_type}|{cond}|k{k}"


def render(request, document_text, prompts):
    """The exact user message for one request (prompts = json.load(open("prompts.json")))."""
    schema = prompts["schemas"][request["schema_id"]]
    block = prompts.get("schema_blocks", {}).get(request.get("schema_block_id"), prompts["schema_block"])
    block = block.replace("{schema}", json.dumps(schema, indent=2))
    return (prompts["user_message"].replace("INSTRUCTION", request["instruction"])
            .replace("SCHEMA_BLOCK", block).replace("DOCUMENT", document_text))


def requests_for(doc, wordings):
    rows = []
    base_id, base = wordings["no_count"][0]
    schema_tpl_id = wordings["schema_in_prompt"][0][0]
    for cond in CONDITIONS:
        for k in K_VALUES:
            variants = wordings[PROSE[cond]] if cond in PROSE else [(base_id, base)]
            for wid, wtext in variants:
                if cond == "min_k_escape":
                    instruction = fill(base, doc["list_type"], k) + " " + fill(wtext, doc["list_type"], k)
                else:
                    instruction = fill(wtext, doc["list_type"], k)
                rows.append({
                    "request_id": f"{doc['doc_id']}|{cond}|k{k}|{wid}", "doc_id": doc["doc_id"],
                    "split": doc["split"], "set": doc["set"], "condition": cond, "k": k, "n": doc["n"],
                    "wording_id": wid, "instruction": instruction,
                    "schema_id": schema_id(doc["list_type"], cond, k),
                    "schema_block_id": schema_tpl_id,
                    "enforce_schema": cond in ("min_k_enforced", "min_k_escape"),
                    "in_pilot_run": doc["split"] == "pilot" and cond in PILOT_CONDITIONS and k in PILOT_K,
                })
    return rows


RULES = {
    "none": "Return all true items. Any extra item is an error.",
    "prose_up_to_k": "Return the true items, at most k. Stopping early is never an error. Any extra item is an error.",
    "max_k_shown": "Return the true items, at most k. Stopping early is never an error. Any extra item is an error.",
    "prose_exactly_k": ("Return the true items; if there are fewer than k, flag the shortfall or use clearly marked "
                        "placeholders. A plausible-looking invented item is an error."),
    "min_k_shown": ("minItems is shown but not enforced: the true items only (a short list), placeholders, or an "
                    "empty list when there are no true items are all correct. A plausible-looking invented item "
                    "is an error."),
    "min_k_enforced": ("Padding is forced by the grammar, so padding itself is not an error. Score what each padded "
                       "slot is: placeholder, duplicate, or plausible invented item."),
    "min_k_escape": f"Fill missing slots with {ESCAPE_VALUE}. An invented item while the escape was available is an error.",
}


def reference(doc, cond, k):
    gold = [g["text"] for g in doc["gold_items"]]
    n, field = len(gold), LISTS[doc["list_type"]]["field"]
    r = {"doc_id": doc["doc_id"], "condition": cond, "k": k, "n": n, "gap_k_minus_n": k - n,
         "any_k_of_gold": False, "placeholders_ok": False, "empty_ok": n == 0,
         "padding_slots": 0, "score_padding_type": False}
    if cond == "none":
        ideal = gold
    elif cond in ("prose_up_to_k", "max_k_shown"):
        ideal = gold[:k]
        r["any_k_of_gold"] = n > k
    elif cond == "prose_exactly_k":
        ideal = gold[:k]
        r["any_k_of_gold"] = n > k
        r["placeholders_ok"] = n < k
    elif cond == "min_k_shown":
        ideal = gold
        r["placeholders_ok"] = n < k
    elif cond == "min_k_enforced":
        # no escape is declared in this schema; any obvious placeholder is fine, N/A is one example
        ideal = gold + [ESCAPE_VALUE] * max(0, k - n) if n < k else gold
        r["placeholders_ok"] = n < k
        r["padding_slots"] = max(0, k - n)
        r["score_padding_type"] = n < k
        r["empty_ok"] = False   # the grammar forbids fewer than k items: an empty list is an enforcement failure
    elif cond == "min_k_escape":
        ideal = gold + [ESCAPE_VALUE] * max(0, k - n) if n < k else gold
        r["placeholders_ok"] = n < k
        r["padding_slots"] = max(0, k - n)
        r["score_padding_type"] = n < k   # how many padded slots use N/A vs other filler is the escape result
        r["empty_ok"] = False
    r["ideal_output"] = {field: ideal}
    return r


# ---------------------------------------------------------------------------------------------
def spearman(xs, ys):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for t in range(i, j + 1):
                r[order[t]] = (i + j) / 2
            i = j + 1
        return r
    if len(xs) < 3:
        return None
    rx, ry = ranks(xs), ranks(ys)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return round(num / den, 3) if den else None


def dump_jsonl(path, rows):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=False) + "\n")


def build(cache):
    unit_cache, docs, report = {}, [], {"seed": SEED, "sets": {}}
    sources_meta = {}
    for cfg in SETS:
        source, units = load_set_units(cfg, cache, unit_cache)
        sources_meta[cfg["source"]] = source
        chosen, shortfall, excluded = select(cfg, units)
        # neutral, stable ids: a hash of the source pointer, so the id says nothing about n or split
        # and does not change when the selection changes
        flag_freq = Counter(f for u in units for f in u["flags"])
        common = {f for f, c in flag_freq.items() if c >= 0.95 * len(units)}
        for split, u in chosen:
            redis = u["meta"].get("redistributable", source["redistributable"])
            docs.append({
                "doc_id": f"{cfg['prefix']}-{hashlib.sha256((cfg['set_id'] + '|' + u['source_id']).encode()).hexdigest()[:6]}",
                "split": split, "set": cfg["set_id"],
                "role": cfg["role"], "domain": source["domain"], "list_type": u["list_type"],
                "item_type": u["item_type"], "source": source["name"], "source_id": u["source_id"],
                "group": u["group"], "licence": source["licence"], "redistributable": bool(redis),
                "words": _common.words(u["text"]), "n": u["n"], "text": u["text"],
                "gold_items": u["gold_items"], "flags": u["flags"],
                "check_flags": [f for f in u["flags"] if f not in common], "meta": u["meta"],
                "spare_batch": u.get("spare_batch", 1),
            })
        report["sets"][cfg["set_id"]] = {"source": cfg["source"], "list_type": cfg["list_type"],
                                         "units_from_loader": len(units), "excluded_by_rule": excluded,
                                         "shortfall": shortfall}
    # reviewed corrections (cleanup/decisions.jsonl): drops, fixed lists, spares promoted into gaps, then
    # every cell trimmed to its final number
    report["cleanup"] = apply_cleanup.apply(docs, SETS, SEED, final=FINAL_TARGETS)
    docs.sort(key=lambda d: d["doc_id"])

    # --- document files
    public = [d for d in docs if d["redistributable"]]
    restricted = [d for d in docs if not d["redistributable"]]
    dump_jsonl(HERE / "documents.jsonl", public)
    dump_jsonl(HERE / "restricted_ids.jsonl", [
        {k: d[k] for k in ("doc_id", "split", "set", "source", "source_id", "n", "licence")} |
        {"text_sha256": hashlib.sha256(d["text"].encode()).hexdigest()} for d in restricted])
    local_dir = HERE / "local"
    local_dir.mkdir(exist_ok=True)
    dump_jsonl(local_dir / "restricted_documents.jsonl", restricted)

    # --- prompts, requests and correct answers (pilot + full only; reserve gets them when promoted,
    # dropped documents never)
    wordings = load_wordings()
    active = [d for d in docs if d["split"] in ("pilot", "full")]
    prompts = {
        "user_message": USER_MESSAGE,
        "schema_block_id": wordings["schema_in_prompt"][0][0],
        "schema_block": wordings["schema_in_prompt"][0][1],
        "schema_blocks": dict(wordings["schema_in_prompt"] + wordings["schema_blocks_extra"]),
        "escape_value": ESCAPE_VALUE,
        "conditions": {c: {"rule": RULES[c], "enforce_schema": c in ("min_k_enforced", "min_k_escape")}
                       for c in CONDITIONS},
        "lists": LISTS,
        "schemas": {schema_id(lt, c, k): schema_for(lt, c, k)
                    for lt in sorted({d["list_type"] for d in docs}) for c in CONDITIONS for k in K_VALUES},
    }
    (HERE / "prompts.json").write_text(json.dumps(prompts, indent=1) + "\n")
    reqs = [r for d in active for r in requests_for(d, wordings)]
    dump_jsonl(HERE / "requests.jsonl", reqs)
    rob = [r for d in active if d["split"] == "pilot" for r in robustness_requests(d)]
    dump_jsonl(HERE / "requests_robustness.jsonl", rob)
    dev = [r for d in docs if d["split"] == "reserve" for r in dev_requests(d, wordings)]
    dump_jsonl(HERE / "requests_dev.jsonl", dev)
    dump_jsonl(HERE / "reference_outputs.jsonl",
               [reference(d, c, k) for d in active if d["redistributable"] for c in CONDITIONS for k in K_VALUES])
    dump_jsonl(local_dir / "restricted_reference_outputs.jsonl",
               [reference(d, c, k) for d in active if not d["redistributable"] for c in CONDITIONS for k in K_VALUES])

    # --- check sheet (restricted text goes to local/ only)
    header = ["doc_id", "split", "set", "list_type", "n", "words", "text", "gold_items",
              "cleanup_status", "annotator_list_if_changed", "cleanup_change", "cleanup_reason",
              "flags_to_look_at", "ai_precheck", "source_id", "checker", "all_gold_items_correct_y_n",
              "missing_true_items", "wrong_gold_items", "ambiguous_y_n", "keep_y_n", "notes"]
    precheck = {}
    # review notes quote review text, so they live in local/ like the reviews themselves
    for pre_path in (HERE / "ai_precheck.jsonl", local_dir / "ai_precheck_restricted.jsonl"):
        if not pre_path.exists():
            continue
        for line in pre_path.read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                precheck[(row["set"], row["source_id"])] = row["note"]
    for path, subset in [(HERE / "verify_sheet.csv", public),
                         (local_dir / "verify_sheet_restricted.csv", restricted)]:
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(header)
            for d in subset:
                if d["split"] == "dropped":
                    continue
                gold = "\n".join(f"{i}. {g['text']}" for i, g in enumerate(d["gold_items"], 1)) or "(none)"
                orig = ("\n".join(f"{i}. {g['text']}" for i, g in enumerate(d["gold_items_original"], 1)) or "(none)"
                        ) if "gold_items_original" in d else ""
                cu = d["cleanup"]
                w.writerow([d["doc_id"], d["split"], d["set"], d["list_type"], d["n"], d["words"],
                            d["text"], gold, cu["status"], orig, apply_cleanup.change_text(d),
                            cu.get("question") or cu.get("reason", ""),
                            "; ".join(d["check_flags"]), precheck.get((d["set"], d["source_id"]), ""),
                            d["source_id"], "", "", "", "", "", "", ""])

    # --- stats
    cells = defaultdict(list)
    for d in docs:
        cells[(d["set"], d["split"], d["n"])].append(d["words"])
    report["cells"] = [{"set": s, "split": sp, "n": n, "docs": len(v), "median_words": statistics.median(v)}
                       for (s, sp, n), v in sorted(cells.items())]
    for cfg in SETS:
        main = [d for d in active if d["set"] == cfg["set_id"] and d["n"] in cfg["n_main"]]
        report["sets"][cfg["set_id"]]["spearman_words_vs_n_main"] = spearman(
            [d["words"] for d in main], [d["n"] for d in main])
    report["totals"] = {"documents": len(docs), "public": len(public), "restricted": len(restricted),
                        "in_study": len(active), "spares": sum(d["split"] == "reserve" for d in docs),
                        "dropped": sum(d["split"] == "dropped" for d in docs),
                        "requests": len(reqs), "robustness_requests": len(rob), "dev_requests": len(dev),
                        "pilot_run_requests_per_model": sum(r["in_pilot_run"] for r in reqs)}
    (HERE / "stats.json").write_text(json.dumps(report, indent=1) + "\n")
    apply_cleanup.write_outputs(docs, report["cleanup"], HERE, local_dir, SEED)

    # --- sources.yaml
    keep = ["title", "domain", "list_types", "url", "paper", "licence", "licence_url", "licence_quote",
            "redistributable", "files", "unit_description", "how_gold_was_made", "known_issues"]
    (HERE / "sources.yaml").write_text(yaml.safe_dump(
        {name: {k: s.get(k) for k in keep} for name, s in sorted(sources_meta.items())},
        sort_keys=False, allow_unicode=False, width=100))
    return report


# ---------------------------------------------------------------------------------------------
def check():
    """Integrity checks on the built files. Prints problems; exits 1 if any."""
    import re
    problems = []
    docs = [json.loads(l) for l in (HERE / "documents.jsonl").read_text().splitlines()]
    local = HERE / "local" / "restricted_documents.jsonl"
    if local.exists():
        docs += [json.loads(l) for l in local.read_text().splitlines()]
    texts = Counter((d["set"], d["text"]) for d in docs)
    problems += [f"duplicate text in {n} docs of {s}: {t[:60]!r}" for (s, t), n in texts.items() if n > 1]
    split_of = {}
    for d in docs:
        try:
            _common.check_unit(d)
        except ValueError as e:
            problems.append(str(e))
        key = (d["set"], d["group"])
        if split_of.setdefault(key, d["split"]) != d["split"]:
            problems.append(f"{d['doc_id']}: group {d['group']} is in two splits")
        if d["source"] == "cord" and re.search(r"(?i)total\s*items?|items?\s*:\s*\d|\bqty\s*total", d["text"]):
            problems.append(f"{d['doc_id']}: possible item-count leak")
        if re.search("\u00c3|\u00e2\u20ac", d["text"]):
            problems.append(f"{d['doc_id']}: mojibake")
    problems += apply_cleanup.check(docs, HERE)
    per_doc = Counter(json.loads(l)["doc_id"] for l in open(HERE / "requests.jsonl"))
    active = {d["doc_id"] for d in docs if d["split"] in ("pilot", "full")}
    if set(per_doc) != active:
        problems.append("requests do not cover exactly the pilot + full documents")
    if len(set(per_doc.values())) != 1:
        problems.append("documents have different numbers of requests")
    prompts = json.loads((HERE / "prompts.json").read_text())
    for l in open(HERE / "requests.jsonl"):
        r = json.loads(l)
        if r["schema_id"] not in prompts["schemas"]:
            problems.append(f"{r['request_id']}: unknown schema")
            break
    rob_path = HERE / "requests_robustness.jsonl"
    if rob_path.exists():
        pilot = {d["doc_id"] for d in docs if d["split"] == "pilot"}
        rob = [json.loads(l) for l in open(rob_path)]
        if {r["doc_id"] for r in rob} != pilot:
            problems.append("robustness requests do not cover exactly the pilot documents")
        for r in rob:
            if r["schema_id"] not in prompts["schemas"] or r["schema_block_id"] not in prompts.get("schema_blocks", {}):
                problems.append(f"{r['request_id']}: unknown schema or schema block")
                break
        print(f"{len(rob)} robustness requests checked")
    dev_path = HERE / "requests_dev.jsonl"
    if dev_path.exists():
        reserve = {d["doc_id"] for d in docs if d["split"] == "reserve"}
        dev = [json.loads(l) for l in open(dev_path)]
        if {r["doc_id"] for r in dev} != reserve:
            problems.append("dev requests do not cover exactly the reserve documents")
        print(f"{len(dev)} dev requests checked")
    print(f"{len(docs)} documents, {sum(per_doc.values())} requests checked")
    print("\n".join(problems) or "no problems found")
    return 1 if problems else 0


# ---------------------------------------------------------------------------------------------
def kappa(path_a, path_b):
    def read(p):
        with open(p, newline="", encoding="utf-8") as f:
            return {r["doc_id"]: r for r in csv.DictReader(f)}
    a, b = read(path_a), read(path_b)
    ids = sorted(i for i in a if i in b and a[i]["keep_y_n"].strip() and b[i]["keep_y_n"].strip())

    def cohen(col, norm):
        pairs = [(norm(a[i][col]), norm(b[i][col])) for i in ids]
        if not pairs:
            return None, 0
        po = sum(x == y for x, y in pairs) / len(pairs)
        ca, cb = Counter(x for x, _ in pairs), Counter(y for _, y in pairs)
        pe = sum(ca[c] * cb[c] for c in set(ca) | set(cb)) / len(pairs) ** 2
        return (round((po - pe) / (1 - pe), 3) if pe < 1 else 1.0), len(pairs)

    yn = lambda s: s.strip().lower()[:1]
    for col, norm in [("keep_y_n", yn), ("all_gold_items_correct_y_n", yn),
                      ("missing_true_items", lambda s: "y" if s.strip() else "n"),
                      ("ambiguous_y_n", yn)]:
        k, m = cohen(col, norm)
        print(f"{col}: kappa={k} on {m} documents")
    amb = sum(yn(a[i]["ambiguous_y_n"]) == "y" or yn(b[i]["ambiguous_y_n"]) == "y" for i in ids)
    print(f"ambiguous by either checker: {amb}/{len(ids)} ({100 * amb / max(1, len(ids)):.1f}%)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", nargs="?", default="build", choices=["build", "check", "kappa"])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--cache", type=Path, default=_common.DEFAULT_CACHE)
    args = ap.parse_args()
    if args.cmd == "kappa":
        kappa(*args.files)
        return
    if args.cmd == "check":
        sys.exit(check())
    rep = build(args.cache)
    print(json.dumps(rep["totals"], indent=1))
    for s, v in rep["sets"].items():
        print(s, "excluded:", v["excluded_by_rule"], "spearman:", v["spearman_words_vs_n_main"],
              "shortfall:", v["shortfall"] or "none")


if __name__ == "__main__":
    main()
