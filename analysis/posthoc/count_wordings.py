#!/usr/bin/env python3
"""POST HOC (not in the registered plan): how often do real extraction prompts carry a count wording?

Data: ScrapeGraphAI-100k (Brach et al. 2026, arXiv:2602.15189), Hugging Face dataset scrapegraphai/scrapegraphai-100k,
pinned to one dataset commit (REVISION below), licence Apache-2.0. The release is one 793 MB parquet file; only the
columns id, prompt, schema and schema_hash are read (HTTP range reads through huggingface_hub's HfFileSystem) and
kept in analysis/posthoc/cache/scrapegraphai100k/<revision>/ (gitignored). Later runs read that copy.

A prompt carries a count wording when one of the patterns in PATTERNS below matches it and the words after the
number pass the checks in accept(). The patterns and checks were written after a rough look at the prompts
(a few loose regexes and their most common contexts) and before the final count. Every change made after
looking at matches is listed in RULE_CHANGES, with the counts before and after.

Patterns (each needs a number k right after the anchor words; k is a whole number in digits, or a number word
from NUMBER_WORDS; case is ignored):
  top        "top k", "top-k"
  up_to      "up to k"
  at_least   "at least k", "a minimum of k", "minimum of k", "no fewer than k", "no less than k", "not less than k"
  at_most    "at most k", "no more than k", "not more than k", "a maximum of k", "maximum of k", "max k",
             "maximum k", "limit(ed) to k"
  exactly    "exactly k"
  first_k    "first k", "last k", "latest k", "next k", "most recent k", "newest k"   (an extra type; not in the ask)
  bare       a request verb, optional "me"/"us", optional "the"/"only"/"just", then k  ("list 5 products")

Checks on the words after k (accept()); a candidate that fails one is not a count wording and is tallied by reason:
  percent    k is followed by "%", "percent" or "per cent"                         ("top 10%")
  decimal    k is followed by ".d" or ",d" (a decimal, not a thousands group)       ("at least 1,5 meter")
  range      k is followed by "-", "to", "or", "and" or "/" and a second number     ("3-5 items", "3 to 5")
  glued      k is glued to letters                                                   ("5MB", "3rd")
  unit       a unit word (UNITS) comes before the noun head                          ("up to 5 MB", "at least 18 years")
  of         the first word after k is "of"                                          ("exactly one of these values")
  no_head    no noun head within the next four words. A noun head is a plural word (ending in "s", not "ss", "us",
             "ous", "is", and not in NOT_PLURAL; or an irregular plural in IRREGULAR_PLURAL), reached before any
             word in STOP_WORDS. When k = 1 a singular head is allowed: the first word after k that is not a STOP
             word. Exception: "top k" with nothing after k (punctuation or end of text) counts, because
             "return the top 3." names a list cut. (Version 1 also excepted "first k"; see RULE_CHANGES.)
The k of an accepted match is k itself ("top three" gives 3).

    python -m venv .venv && .venv/Scripts/python -m pip install huggingface_hub pyarrow
    .venv/Scripts/python analysis/posthoc/count_wordings.py

Outputs: analysis/posthoc/out/count_wordings.md and .json. Unit of the main count: one row (one extraction event);
the same counts over distinct prompt texts are given too, because the release repeats prompts across rows.
The schema column is checked with the walker of schema_prevalence.py for minItems, for comparison.
"""
import argparse
import hashlib
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from schema_prevalence import arrays_of  # noqa: E402  same walker and array classes as the JSONSchemaBench count

DATASET = "scrapegraphai/scrapegraphai-100k"
REVISION = "0f8d168f2a64632a3ec860059919059273314e66"  # dataset commit of 2026-07-27 (v1.0, 93,695 rows)
LICENCE = "Apache-2.0"
FILE = "data/train.parquet"
COLUMNS = ["id", "prompt", "schema", "schema_hash"]
CACHE = HERE / "cache" / "scrapegraphai100k" / REVISION
LOCAL = CACHE / "prompt_schema.parquet"
META = CACHE / "meta.json"
OUT = HERE / "out"
SEED = 20261101          # for the 20 random matches and the examples
N_RANDOM = 20
N_EXAMPLES = 5

# ---------------------------------------------------------------- rules (written before the final count)

NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
                "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
                "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30,
                "forty": 40, "fifty": 50, "hundred": 100}
NUM = r"(?P<num>\d{1,3}(?:,\d{3})+(?![.,]?\d)|\d+|" + "|".join(NUMBER_WORDS) + r")\b"

VERBS = ("list", "extract", "get", "return", "give", "find", "scrape", "show", "provide", "collect", "fetch",
         "retrieve", "pull", "grab", "select", "pick", "identify", "name", "choose", "output", "generate",
         "suggest", "recommend", "gather", "include")

PATTERNS = {
    "top": r"\btop[\s-]+" + NUM,
    "up_to": r"\bup\s+to\s+" + NUM,
    "at_least": r"\b(?:at\s+least|a\s+minimum\s+of|minimum\s+of|no\s+fewer\s+than|no\s+less\s+than|not\s+less\s+than)\s+"
                + NUM,
    "at_most": r"\b(?:at\s+most|no\s+more\s+than|not\s+more\s+than|a\s+maximum\s+of|maximum\s+of|max(?:imum)?\.?"
               r"|limit(?:ed)?\s+to)\s+" + NUM,
    "exactly": r"\bexactly\s+" + NUM,
    "first_k": r"\b(?:first|last|latest|next|most\s+recent|newest)\s+" + NUM,
    "bare": r"\b(?:" + "|".join(VERBS) + r")(?:\s+(?:me|us))?(?:\s+(?:the|only|just))?\s+" + NUM,
}
TYPES = list(PATTERNS)
ASKED = ["top", "up_to", "at_least", "at_most", "exactly", "bare"]   # the types named in the ask
COMPILED = {t: re.compile(p, re.IGNORECASE) for t, p in PATTERNS.items()}

UNITS = {
    "character", "characters", "char", "chars", "word", "words", "token", "tokens", "sentence", "sentences",
    "line", "lines", "paragraph", "paragraphs", "letter", "letters", "digit", "digits", "decimal", "decimals",
    "byte", "bytes", "kb", "mb", "gb", "tb", "pixel", "pixels", "px",
    "second", "seconds", "sec", "secs", "minute", "minutes", "min", "mins", "hour", "hours", "hr", "hrs",
    "day", "days", "week", "weeks", "month", "months", "year", "years", "yr", "yrs", "decade", "decades",
    "time", "times", "percent", "meter", "meters", "metre", "metres", "m", "km", "cm", "mm", "mile", "miles",
    "inch", "inches", "foot", "feet", "ft", "kg", "kgs", "g", "gram", "grams", "lb", "lbs", "pound", "pounds",
    "dollar", "dollars", "usd", "eur", "euro", "euros", "star", "stars",
}
STOP_WORDS = {
    "the", "a", "an", "of", "in", "from", "with", "for", "that", "and", "or", "to", "on", "at", "by", "per",
    "each", "which", "who", "is", "are", "be", "was", "were", "as", "if", "it", "its", "this", "these", "those",
    "than", "then", "you", "your", "i", "we", "they", "not", "no", "only", "but", "so", "into", "about", "over",
    "under", "within", "between", "after", "before", "where", "when", "what", "how", "should", "must", "can",
    "will", "would", "may", "do", "does", "has", "have", "had",
}
NOT_PLURAL = {"this", "its", "his", "has", "was", "is", "us", "as", "yes", "does", "always", "plus", "less",
              "news", "series", "species", "status", "analysis", "basis", "thesis", "bus", "gas", "christmas",
              "vs", "perhaps", "whereas", "towards", "afterwards", "sometimes", "besides", "unless", "ones"}
IRREGULAR_PLURAL = {"people", "children", "men", "women", "data", "criteria", "media", "staff", "alumni", "feet"}
WORD = re.compile(r"[a-z][a-z'’-]*|\d+")

RULES_VERSION = 2  # 1 = commit 3342830; raise it with every entry in RULE_CHANGES

# Rule changes made after looking at matches: (date, change, counts before, counts after). Empty = none.
RULE_CHANGES = [
    ("2026-11-01",
     "first_k no longer counts with nothing after k; only top k does. Found in the first run's matches: "
     "'move forward to the next one.' The first rules are at commit 3342830 (rules sha256 fbe8ef7d58c1).",
     "rows: any 633 (0.68%), asked types 517 (0.55%), first_k 116, k=1 139, k=3 181, k=5 136",
     "rows: any 606 (0.65%), asked types 517 (0.55%), first_k 89, k=1 112, k=3 181, k=5 136 (other types unchanged)"),
]


def k_value(s):
    s = s.lower()
    return NUMBER_WORDS[s] if s in NUMBER_WORDS else int(s.replace(",", ""))


def is_plural(w):
    if w in IRREGULAR_PLURAL:
        return True
    if w in NOT_PLURAL or len(w) < 4 or not w.endswith("s"):
        return False
    return not w.endswith(("ss", "us", "ous", "is"))


def accept(typ, text, m):
    """(True, head) for a count wording, else (False, reason). text is the lower-cased prompt, m the match."""
    k = k_value(m.group("num"))
    tail = text[m.end():m.end() + 80]
    if re.match(r"\s?(%|percent\b|per\s+cent\b)", tail):
        return False, "percent"
    if re.match(r"[.,]\d", tail):
        return False, "decimal"
    if re.match(r"\s*(-|–|—|to\b|or\b|and\b|/)\s*(\d+|" + "|".join(NUMBER_WORDS) + r")\b", tail):
        return False, "range"
    if re.match(r"[a-z]", tail):
        return False, "glued"
    # the words before the next sentence or clause mark (a hyphen inside a word is kept)
    clause = re.split(r"[.,;:!?()\[\]{}\"“”\n]|\s-\s", tail, maxsplit=1)[0]
    words = WORD.findall(clause)[:4]
    if not words:
        if typ == "top":   # first_k removed here on 2026-11-01, see RULE_CHANGES
            return True, ""
        return False, "no_head"
    if words[0] == "of":
        return False, "of"
    for i, w in enumerate(words):
        if w in UNITS:
            return False, "unit"
        if w in STOP_WORDS:
            break
        if is_plural(w):
            return True, w
        if k == 1 and i == 0 and not w.isdigit():
            return True, w
    return False, "no_head"


def find(prompt):
    """[(type, start, end, k, accepted, head_or_reason)] for every candidate in one prompt."""
    text = prompt.lower().replace("’", "'")
    out = []
    for typ, rx in COMPILED.items():
        for m in rx.finditer(text):
            ok, why = accept(typ, text, m)
            out.append((typ, m.start(), m.end(), k_value(m.group("num")), ok, why))
    return out


# ---------------------------------------------------------------- data

def fetch(force=False):
    """Return (rows, meta). Reads the four columns from the pinned remote file once, then the local copy."""
    import pyarrow.parquet as pq

    if force or not LOCAL.exists():
        from datetime import datetime, timezone

        from huggingface_hub import HfFileSystem

        fs = HfFileSystem()
        path = f"datasets/{DATASET}@{REVISION}/{FILE}"
        info = fs.info(path)
        with fs.open(path, "rb", block_size=8 * 1024 * 1024) as f:
            table = pq.ParquetFile(f).read(columns=COLUMNS)
        CACHE.mkdir(parents=True, exist_ok=True)
        tmp = LOCAL.with_suffix(".part")
        pq.write_table(table, tmp)
        tmp.replace(LOCAL)
        META.write_text(json.dumps({
            "dataset": DATASET, "revision": REVISION, "file": FILE, "remote_size": info.get("size"),
            "remote_lfs_sha256": (info.get("lfs") or {}).get("sha256"), "columns": COLUMNS,
            "downloaded_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}, indent=1) + "\n")
    meta = json.loads(META.read_text())
    meta["local_sha256"] = hashlib.sha256(LOCAL.read_bytes()).hexdigest()
    return pq.read_table(LOCAL, columns=COLUMNS).to_pylist(), meta


# ---------------------------------------------------------------- counting

def pct(a, b, d=2):
    return round(100.0 * a / b, d) if b else 0.0


def kbin(k):
    return str(k) if k in (1, 3, 5) else "other"


def context(prompt, start, end, n=15):
    """About n words around the match (the match in **bold**), whitespace collapsed."""
    before = re.sub(r"\s+", " ", prompt[:start]).split(" ")
    after = re.sub(r"\s+", " ", prompt[end:]).split(" ")
    nb = n // 2
    b = " ".join(before[-nb - 1:]).lstrip()
    a = " ".join(after[: n - nb + 1]).rstrip()
    mid = re.sub(r"\s+", " ", prompt[start:end])
    s = f"{b}**{mid}**{a}"
    return ("... " if len(before) > nb + 1 else "") + s + (" ..." if len(after) > n - nb + 1 else "")


def match_words(prompt, start, end, why):
    """The matched words plus the noun head, as written in the prompt."""
    s = re.sub(r"\s+", " ", prompt[start:end])
    if why:
        tail = prompt[end:end + 80]
        i = tail.lower().replace("’", "'").find(why)
        if i >= 0:
            s += re.sub(r"\s+", " ", tail[:i + len(why)])
    return s


def count(rows):
    n = len(rows)
    per_type_rows = Counter()
    any_rows = asked_rows = 0
    kdist = {t: Counter() for t in TYPES}
    kdist_all = Counter()
    k_rows = Counter()                 # rows with an accepted match of k in {1, 3, 5}
    excluded = {t: Counter() for t in TYPES}
    excl_examples = defaultdict(list)
    accepted = []                      # (prompt text, type, start, end, k, head) over distinct prompt texts
    numword = Counter()
    seen_text = set()
    uniq = {"prompts": 0, "any": 0, "asked": 0, **{t: 0 for t in TYPES}}
    for r in rows:
        p = r["prompt"] or ""
        cands = find(p)
        ok = [c for c in cands if c[4]]
        types = {c[0] for c in ok}
        for t in types:
            per_type_rows[t] += 1
        any_rows += bool(types)
        asked_rows += bool(types & set(ASKED))
        for t, s, e, k, _, head in ok:
            kdist[t][kbin(k)] += 1
            kdist_all[kbin(k)] += 1
        for kk in {kbin(c[3]) for c in ok}:
            k_rows[kk] += 1
        new = p not in seen_text
        if new:
            seen_text.add(p)
            uniq["prompts"] += 1
            uniq["any"] += bool(types)
            uniq["asked"] += bool(types & set(ASKED))
            for t in types:
                uniq[t] += 1
            for t, s, e, k, acc, why in cands:
                if acc:
                    accepted.append((p, t, s, e, k, why))
                    if not p[s:e].split()[-1].isdigit() and not p[s:e].split()[-1][0].isdigit():
                        numword[t] += 1
                else:
                    excluded[t][why] += 1
                    excl_examples[why].append((p, t, s, e))
    return {"rows": n, "per_type_rows": per_type_rows, "any_rows": any_rows, "asked_rows": asked_rows,
            "kdist": kdist, "kdist_all": kdist_all, "k_rows": k_rows, "excluded": excluded,
            "excl_examples": excl_examples, "accepted": accepted, "numword": numword, "uniq": uniq}


def schema_counts(rows):
    """minItems on open arrays in the schema column, per row and per distinct schema_hash."""
    def flags(text):
        try:
            s = json.loads(text)
        except Exception:  # noqa: BLE001
            return None
        if not isinstance(s, dict):
            return None
        f = set()
        for _, _, a in arrays_of(s):
            f.add("array")
            if a["shape"] != "open":
                continue
            if a["max"] is not None:
                f.add("max_any")
            if a["min"] is None:
                continue
            if a["min"] >= 1 and a["group"] == "string_object":
                f.add("min1_list")
            if a["min"] >= 2:
                f.add("min2")
                if a["group"] == "string_object":
                    f.add("min2_list")
            if a["min"] >= 3:
                f.add("min3")
        return f

    by_hash = {}
    row_c, hash_c = Counter(), Counter()
    for r in rows:
        h = r["schema_hash"] or hashlib.sha256((r["schema"] or "").encode()).hexdigest()
        if h not in by_hash:
            by_hash[h] = flags(r["schema"] or "")
            f = by_hash[h]
            hash_c["schemas"] += 1
            if f is None:
                hash_c["parse_fail"] += 1
            else:
                hash_c.update(f)
        f = by_hash[h]
        row_c["rows"] += 1
        if f is None:
            row_c["parse_fail"] += 1
        else:
            row_c.update(f)
    return row_c, hash_c


def random_matches(accepted, n=N_RANDOM, seed=SEED):
    """n accepted matches drawn at random (fixed seed) across all patterns, one per distinct (pattern, context)
    so near-identical prompts do not show the same window twice. Display only; the counts do not use it."""
    pool, seen = [], set()
    for a in sorted(accepted, key=lambda a: (a[0], a[2], a[1])):
        key = (a[1], context(a[0], a[2], a[3]))
        if key not in seen:
            seen.add(key)
            pool.append(a)
    return random.Random(seed).sample(pool, min(n, len(pool)))


def examples_by_type(accepted, n=N_EXAMPLES, seed=SEED):
    by = defaultdict(list)
    for a in sorted(accepted, key=lambda a: (a[0], a[2], a[1])):
        by[a[1]].append(a)
    rnd = random.Random(seed + 1)
    return {t: rnd.sample(by[t], min(n, len(by[t]))) for t in TYPES}


# ---------------------------------------------------------------- output

def md_cell(s):
    return s.replace("|", "\\|").replace("\n", " ")


def headline(res):
    o = res["overall"]
    return (f"HEADLINE rows={o['rows']} any={o['any_rows']} ({o['pct_any']:.2f}%) asked_types={o['asked_rows']} "
            f"({o['pct_asked']:.2f}%) " + " ".join(f"{t}={res['per_type'][t]['rows']}" for t in TYPES)
            + f" k1={o['k_rows']['1']} k3={o['k_rows']['3']} k5={o['k_rows']['5']} rules={res['rules_sha256'][:12]}")


def write_md(res, c, rnd, ex):
    o, m, sr, sh = res["overall"], res["meta"], res["schemas_rows"], res["schemas_unique"]
    L = ["# POST HOC: count wordings in real extraction prompts (ScrapeGraphAI-100k)", "",
         "POST HOC: not in the registered plan. Source: `analysis/posthoc/count_wordings.py`.", "",
         f"Data: `{DATASET}` at revision `{REVISION}` (licence {LICENCE}), file `{FILE}`, "
         f"{o['rows']:,} rows; columns read: {', '.join(COLUMNS)}. "
         f"Remote LFS sha256 `{m['remote_lfs_sha256']}`; columns fetched {m['downloaded_utc']}.", "",
         "Reproduce (from the repository root; reads four columns of the 793 MB file and keeps them as a 16 MB "
         "parquet in the gitignored `analysis/posthoc/cache/`):", "", "```",
         "python -m venv .venv", ".venv/Scripts/python -m pip install huggingface_hub pyarrow",
         ".venv/Scripts/python analysis/posthoc/count_wordings.py", "```", "",
         f"Headline line printed by the script: `{headline(res)}`", "",
         "## Summary", "",
         f"Of {o['rows']:,} extraction prompts, {o['any_rows']:,} ({o['pct_any']:.2f}%) carry a count wording of "
         f"any type below; {o['asked_rows']:,} ({o['pct_asked']:.2f}%) carry one of the six types named in the "
         f"ask (all but first_k). {o['k_rows']['3']:,} prompts ({pct(o['k_rows']['3'], o['rows'])}%) ask for k = 3 "
         f"and {o['k_rows']['5']:,} ({pct(o['k_rows']['5'], o['rows'])}%) for k = 5. "
         f"Over the {res['unique']['prompts']:,} distinct prompt texts the share is "
         f"{pct(res['unique']['any'], res['unique']['prompts']):.2f}%. "
         f"For comparison, {pct(sr.get('min2_list', 0), sr['rows'])}% of rows "
         f"({pct(sh.get('min2_list', 0), sh['schemas'])}% of the {sh['schemas']:,} distinct schemas) have a schema "
         f"with an open list of strings or objects with minItems >= 2 (JSONSchemaBench: 0.3%, "
         "`out/schema_prevalence.md`).", "",
         "The share is a count of pattern matches, not of judged count wordings: no person has yet checked the "
         "matches. Twenty random matches are listed below for that check. Only English wordings are counted.", "",
         "## Patterns (verbatim from the script)", "",
         "`NUM` (k in digits or a number word):", "", "```", NUM, "```", "",
         "| Pattern | Regex |", "|---|---|"]
    for t in TYPES:
        L.append(f"| {t} | `{md_cell(PATTERNS[t])}` |")
    L += ["", "A candidate is then kept or dropped by `accept()` (see the script's docstring): it is dropped when k "
          "is a percentage, a decimal, the start of a range, glued to letters, followed by a unit word, followed "
          "by \"of\", or has no noun head within four words (a plural, or any word when k = 1); bare \"top k\" and "
          "\"first k\" at a clause end are kept.", "",
          f"Unit words: {', '.join(sorted(UNITS))}.", "",
          f"Stop words (end the noun-head search): {', '.join(sorted(STOP_WORDS))}.", "",
          f"Request verbs (bare): {', '.join(VERBS)}.", "",
          f"Rules version {RULES_VERSION}; rules sha256 (RULES_VERSION, PATTERNS, UNITS, STOP_WORDS, NOT_PLURAL, IRREGULAR_PLURAL, VERBS, NUMBER_WORDS): "
          f"`{res['rules_sha256']}`.", "",
          "## Counts per pattern", "",
          "Rows: share of all rows with at least one kept match of the pattern. Distinct: the same over distinct "
          "prompt texts. k columns: kept matches in all rows, by k. Number words: kept matches in distinct "
          "prompts whose k is written as a word (\"top three\").", "",
          "| Pattern | Rows | % rows | Distinct prompts | % distinct | k=1 | k=3 | k=5 | other k | number words |",
          "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for t in TYPES:
        p = res["per_type"][t]
        kd = p["k"]
        L.append(f"| {t} | {p['rows']:,} | {p['pct_rows']:.2f} | {p['distinct']:,} | {p['pct_distinct']:.2f} | "
                 f"{kd.get('1', 0)} | {kd.get('3', 0)} | {kd.get('5', 0)} | {kd.get('other', 0)} | "
                 f"{p['number_words']} |")
    u = res["unique"]
    kd = o["k_matches"]
    L.append(f"| **any** | **{o['any_rows']:,}** | **{o['pct_any']:.2f}** | **{u['any']:,}** | "
             f"**{pct(u['any'], u['prompts'])}** | {kd.get('1', 0)} | {kd.get('3', 0)} | {kd.get('5', 0)} | "
             f"{kd.get('other', 0)} | |")
    L.append(f"| any of the six asked types | {o['asked_rows']:,} | {o['pct_asked']:.2f} | {u['asked']:,} | "
             f"{pct(u['asked'], u['prompts'])} | | | | | |")
    L += ["", f"A row can match several patterns, so the pattern rows add up to more than the any row. "
          f"Rows with a kept k = 1: {o['k_rows']['1']:,}; k = 3: {o['k_rows']['3']:,}; k = 5: {o['k_rows']['5']:,}; "
          f"other k: {o['k_rows']['other']:,}.", "",
          "## Dropped candidates (distinct prompts)", "",
          "Candidates the patterns found but `accept()` dropped, by reason. These are the nearby inputs: "
          "percentages, units, ranges and the like.", "",
          "| Pattern | " + " | ".join(REASONS) + " |", "|---|" + "---:|" * len(REASONS)]
    for t in TYPES:
        L.append(f"| {t} | " + " | ".join(str(c['excluded'][t].get(r, 0)) for r in REASONS) + " |")
    L += ["", "Two dropped examples per reason:", "", "| Reason | Pattern | Prompt around the match |", "|---|---|---|"]
    for r in REASONS:
        for p, t, s, e in res["excl_shown"].get(r, []):
            L.append(f"| {r} | {t} | {md_cell(context(p, s, e))} |")
    L += ["", f"## {N_RANDOM} random matches for the owner's check", "",
          f"Drawn with seed {SEED} across all patterns from the {res['n_random_pool']:,} kept matches with a distinct "
          f"pattern and context (of {len(c['accepted']):,} kept matches in distinct prompt texts; near-identical "
          "prompts share a context and are drawn once). Match: the anchor, k and the noun "
          "head as written. Context: about 15 words around the match "
          "(match in bold). Not judged here; the authors judge whether each is a top-k style count wording.", "",
          "| # | Pattern | k | Match | Context |", "|---:|---|---:|---|---|"]
    for i, (p, t, s, e, k, head) in enumerate(rnd, 1):
        L.append(f"| {i} | {t} | {k} | {md_cell(match_words(p, s, e, head))} | {md_cell(context(p, s, e))} |")
    L += ["", f"## {N_EXAMPLES} examples per pattern", "", "| Pattern | k | Context |", "|---|---:|---|"]
    for t in TYPES:
        for p, tt, s, e, k, head in ex[t]:
            L.append(f"| {t} | {k} | {md_cell(context(p, s, e))} |")
    L += ["", "## minItems in the dataset's schemas", "",
          "Same walker and array classes as `schema_prevalence.py` (open arrays: not fixed-length, not tuples).", "",
          "| Measure | Rows | % rows | Distinct schemas | % distinct |", "|---|---:|---:|---:|---:|"]
    for key, name in [("array", "any array"), ("min1_list", "open list of strings/objects, minItems >= 1"),
                      ("min2", "open array, minItems >= 2"), ("min2_list", "open list of strings/objects, minItems >= 2"),
                      ("min3", "open array, minItems >= 3"), ("max_any", "open array with a maxItems")]:
        L.append(f"| {name} | {sr.get(key, 0):,} | {pct(sr.get(key, 0), sr['rows'])} | {sh.get(key, 0):,} | "
                 f"{pct(sh.get(key, 0), sh['schemas'])} |")
    L += ["", f"Schemas that did not parse: {sr.get('parse_fail', 0):,} rows, {sh.get('parse_fail', 0):,} distinct.",
          "", "## Rule changes after looking at matches", ""]
    if RULE_CHANGES:
        L += ["| Date | Change | Before | After |", "|---|---|---|---|"]
        for d, ch, b, a in RULE_CHANGES:
            L.append(f"| {d} | {md_cell(ch)} | {md_cell(b)} | {md_cell(a)} |")
    else:
        L.append("None.")
    L += ["", "## Caveats", "",
          "- The rows are extraction events from opt-in telemetry of one library (ScrapeGraphAI), Q2-Q3 2025; "
          "the release keeps at most 5 rows per schema, and prompts repeat across rows "
          f"({u['prompts']:,} distinct texts in {o['rows']:,} rows).",
          "- English patterns only; prompts in other languages count as having no count wording.",
          "- A kept match is a pattern match. Some will be false positives (for example a count inside a field "
          "description); the random matches above are for a person to judge that.",
          "- A count in the prompt and a minItems in the schema are different things: the first is prose the model "
          "reads, the second is a keyword a decoder can enforce.", ""]
    (OUT / "count_wordings.md").write_text("\n".join(L), encoding="utf-8")


REASONS = ["percent", "decimal", "range", "glued", "unit", "of", "no_head"]


def rules_hash():
    blob = json.dumps([RULES_VERSION, PATTERNS, sorted(UNITS), sorted(STOP_WORDS), sorted(NOT_PLURAL), sorted(IRREGULAR_PLURAL),
                       VERBS, NUMBER_WORDS], sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--refresh", action="store_true", help="re-read the pinned remote file")
    args = ap.parse_args()
    rows, meta = fetch(args.refresh)
    c = count(rows)
    n = c["rows"]
    u = c["uniq"]
    per_type = {t: {"rows": c["per_type_rows"][t], "pct_rows": pct(c["per_type_rows"][t], n),
                    "distinct": u[t], "pct_distinct": pct(u[t], u["prompts"]),
                    "k": dict(c["kdist"][t]), "number_words": c["numword"][t]} for t in TYPES}
    overall = {"rows": n, "any_rows": c["any_rows"], "pct_any": pct(c["any_rows"], n),
               "asked_rows": c["asked_rows"], "pct_asked": pct(c["asked_rows"], n),
               "k_matches": dict(c["kdist_all"]), "k_rows": {b: c["k_rows"].get(b, 0) for b in ("1", "3", "5", "other")}}
    rnd = random_matches(c["accepted"])
    n_pool = len({(a[1], context(a[0], a[2], a[3])) for a in c["accepted"]})
    ex = examples_by_type(c["accepted"])
    rs = random.Random(SEED + 2)
    excl_shown = {r: rs.sample(c["excl_examples"][r], min(2, len(c["excl_examples"][r])))
                  for r in REASONS if c["excl_examples"][r]}
    sr, sh = schema_counts(rows)
    res = {"posthoc": True, "dataset": DATASET, "revision": REVISION, "licence": LICENCE, "meta": meta,
           "source": f"https://huggingface.co/datasets/{DATASET}/tree/{REVISION}",
           "patterns": PATTERNS, "num": NUM, "rules_sha256": rules_hash(), "rule_changes": RULE_CHANGES,
           "seed": SEED, "n_random_pool": n_pool, "overall": overall, "per_type": per_type, "unique": u,
           "excluded_distinct": {t: dict(c["excluded"][t]) for t in TYPES},
           "schemas_rows": dict(sr), "schemas_unique": dict(sh), "excl_shown": excl_shown,
           "random_matches": [{"pattern": t, "k": k, "match": match_words(p, s, e, h), "context": context(p, s, e)}
                              for p, t, s, e, k, h in rnd]}
    OUT.mkdir(parents=True, exist_ok=True)
    write_md(res, c, rnd, ex)
    res.pop("excl_shown")
    (OUT / "count_wordings.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(headline(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
