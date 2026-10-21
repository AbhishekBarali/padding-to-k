"""Shared pieces of the run harness: load the frozen data, render the exact prompt, parse outputs.

Everything a model sees comes from data/ (documents.jsonl, data/local/restricted_documents.jsonl for the
review set, requests.jsonl, prompts.json) through data/build.py's render(). Nothing here rewrites a
prompt. The parse and count rules below are the ones the scorer uses; change them only before the
preregistration is filed, and record the change in DECISIONS.md.
"""
import hashlib
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
sys.path.insert(0, str(DATA))
import build  # noqa: E402  (data/build.py: render() is the single source of the prompt text)

HARNESS_VERSION = "0.1.0"
DATA_FILES = ["documents.jsonl", "requests.jsonl", "requests_robustness.jsonl", "requests_dev.jsonl",
              "requests_fewer_ok.jsonl", "prompts.json", "reference_outputs.jsonl",
              "local/restricted_documents.jsonl", "local/restricted_reference_outputs.jsonl"]


def sha256_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def data_hashes():
    """sha256 of every data file a run depends on (missing restricted files are reported as missing)."""
    out = {}
    for name in DATA_FILES:
        p = DATA / name
        out[name] = sha256_file(p) if p.exists() else "MISSING"
    return out


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_documents():
    """All documents by id, including the review set rebuilt into data/local/ (never committed)."""
    docs = {d["doc_id"]: d for d in read_jsonl(DATA / "documents.jsonl")}
    local = DATA / "local" / "restricted_documents.jsonl"
    if local.exists():
        docs.update({d["doc_id"]: d for d in read_jsonl(local)})
    return docs


def load_requests():
    """All 25,110 main requests and the 1,674 of min_k_shown_fewer_ok (added 18 Oct, in the full scope), then
    the robustness-arm and dev (reserve-document) requests; those carry an `arm` field and are never part of
    the pilot or full scope. Review requests are in requests.jsonl too; only their document text is local."""
    rows = read_jsonl(DATA / "requests.jsonl")
    for extra in ("requests_fewer_ok.jsonl", "requests_robustness.jsonl", "requests_dev.jsonl"):
        if (DATA / extra).exists():
            rows += read_jsonl(DATA / extra)
    return rows


def load_prompts():
    return json.loads((DATA / "prompts.json").read_text(encoding="utf-8"))


def user_message(req, doc, prompts):
    """The exact user message (instruction + schema block + document), as data/build.py renders it."""
    return build.render(req, doc["text"], prompts)


def schema_of(req, prompts):
    return prompts["schemas"][req["schema_id"]]


def field_of(req, prompts):
    return prompts["lists"][req["schema_id"].split("|")[0]]["field"]


# ---------------------------------------------------------------------------------------------
# Parse ladder: the same for every condition. Each rung is recorded, so a reader can see how much
# of a result rests on lenient parsing. Rungs, in order:
#   strict           the whole text is JSON
#   fence            a ```json block``` (the first one that holds the asked-for list wins)
#   first_object / later_object   a balanced {...} in the text (same rule)
#   array_in_text    a balanced [...] in the text
#   truncated_salvage  the output was cut off inside the list: the complete strings before the cut
#   failed
# A dict that looks like a JSON schema (an echo of the prompt) is never taken as the answer.
FENCE = re.compile(r"```(?:json|JSON)?\s*\n?(.*?)```", re.S)
REASONING_BLOCK = re.compile(r"<(reasoning|think|thinking)>.*?</\1>", re.S | re.I)
UNCLOSED_REASONING = re.compile(r"^\s*<(reasoning|think|thinking)>", re.I)
JSON_STRING = re.compile(r'"((?:[^"\\]|\\.)*)"')


def _balanced(s, open_c, close_c):
    """Yield (start, end) of each balanced open_c...close_c span, left to right, respecting strings."""
    i = s.find(open_c)
    while i != -1:
        depth, in_str, esc, end = 0, False, False, None
        for j in range(i, len(s)):
            c = s[j]
            if in_str:
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    in_str = False
            elif c == '"':
                in_str = True
            elif c == open_c:
                depth += 1
            elif c == close_c:
                depth -= 1
                if depth == 0:
                    end = j + 1
                    break
        if end:
            yield i, end
            i = s.find(open_c, end)
        else:
            i = s.find(open_c, i + 1)


def _looks_like_schema(obj):
    return isinstance(obj, dict) and ("properties" in obj or "$schema" in obj
                                      or obj.get("type") in ("object", "array"))


def _list_in(obj, field):
    if isinstance(obj, dict) and isinstance(obj.get(field), list):
        return obj[field], "field"
    if isinstance(obj, list):
        return obj, "bare_list"
    if isinstance(obj, dict) and not _looks_like_schema(obj):
        lists = [v for v in obj.values() if isinstance(v, list)]
        if len(lists) == 1:
            return lists[0], "single_other_key"
    return None, None


def _closes_list(rest):
    """True when the list whose "[" comes just before `rest` is closed in it; brackets inside strings do
    not count (a model blocked by minItems may write "]}" inside an entry and go on)."""
    depth, in_str, esc = 0, False, False
    for c in rest:
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c in "[{":
            depth += 1
        elif c in "]}":
            if depth == 0:
                return True
            depth -= 1
    return False


def _salvage(text, field):
    """The list was cut off (max_tokens): keep the complete strings written before the cut."""
    m = re.search(r'"' + re.escape(field) + r'"\s*:\s*\[', text)
    if not m:
        return None
    rest = text[m.end():]
    if _closes_list(rest):                 # the list was closed: not a truncation
        return None
    items, pos = [], 0
    while True:
        sm = JSON_STRING.search(rest, pos)
        if not sm:
            break
        after = rest[sm.end():].lstrip()
        if not after.startswith((",", "]")):
            break                                  # the last string was cut in the middle
        try:
            items.append(json.loads('"' + sm.group(1) + '"'))
        except (json.JSONDecodeError, ValueError):
            break
        pos = sm.end()
    return items or None                   # cut before the first entry was complete: no list to read


def parse_output(content, field):
    """Parse a model's text into a list of items.

    Returns dict: parse_rung, list_source (field | bare_list | single_other_key | salvage | none),
    items (list or None), text_outside_json (bool), non_string_items (count), reasoning_in_content.
    """
    out = {"parse_rung": "failed", "list_source": "none", "items": None,
           "text_outside_json": False, "non_string_items": 0, "reasoning_in_content": False, "n_answer_lists": 0}
    if content is None:
        return out
    text = content.strip()
    if REASONING_BLOCK.search(text) or UNCLOSED_REASONING.match(text):
        out["reasoning_in_content"] = True
        text = REASONING_BLOCK.sub("", text).strip()
        if UNCLOSED_REASONING.match(text):
            # the reply was cut off inside its reasoning (gpt-oss on Bedrock writes <reasoning>...</reasoning>
            # before the answer): the answer never came, and a list drafted inside the reasoning is not it
            return out
    cands = []                                     # (obj, span or None, rung)
    try:
        cands.append((json.loads(text), None, "strict"))
    except (json.JSONDecodeError, ValueError):
        for m in FENCE.finditer(text):
            try:
                cands.append((json.loads(m.group(1).strip()), m.span(), "fence"))
            except (json.JSONDecodeError, ValueError):
                pass
        for i, (a, b) in enumerate(_balanced(text, "{", "}")):
            try:
                cands.append((json.loads(text[a:b]), (a, b), "first_object" if i == 0 else "later_object"))
            except (json.JSONDecodeError, ValueError):
                pass
        if not cands:
            for a, b in _balanced(text, "[", "]"):
                try:
                    cands.append((json.loads(text[a:b]), (a, b), "array_in_text"))
                    break
                except (json.JSONDecodeError, ValueError):
                    pass
    # how many DIFFERENT lists under the asked-for field the text holds (a first try, then a "corrected" one):
    # the first is the answer; the count lets the report show how much rests on that choice
    out["n_answer_lists"] = len({json.dumps(o[field]) for o, _, _ in cands if _list_in(o, field)[1] == "field"})
    chosen = next(((o, sp, r) for o, sp, r in cands if _list_in(o, field)[1] == "field"), None)
    if chosen is None:
        chosen = next(((o, sp, r) for o, sp, r in cands if _list_in(o, field)[0] is not None), None)
    if chosen is None:
        if cands:                                  # JSON, but no list in it
            out["parse_rung"] = cands[0][2]
            return out
        salvaged = _salvage(text, field)
        if salvaged is not None:
            out.update(parse_rung="truncated_salvage", list_source="salvage", items=salvaged)
        return out
    obj, span, rung = chosen
    out["parse_rung"] = rung
    if span:
        out["text_outside_json"] = bool((text[:span[0]] + text[span[1]:]).strip())
    arr, out["list_source"] = _list_in(obj, field)
    items = []
    for x in arr:
        if isinstance(x, str):
            items.append(x)
        else:
            out["non_string_items"] += 1
            if isinstance(x, dict) and len(x) == 1 and isinstance(next(iter(x.values())), str):
                items.append(next(iter(x.values())))      # {"text": "..."}: the value is the item
            else:
                items.append("" if x is None else json.dumps(x, ensure_ascii=False))
    out["items"] = items
    return out


# ---------------------------------------------------------------------------------------------
# Placeholders and duplicates. A placeholder is a whole item, in the model's own words, that says
# "nothing here" ("N/A", "No further requests", "Only one request in this email"). It never counts as
# an item. Two guards: an item that appears word for word in the document is document text, never a
# placeholder (a novel quote "Only one more day"); and anonymisation tokens copied from the job ads
# (<ORGANIZATION>) are document text too. The lexicon is matched on a "core" form of the item: lower
# case, punctuation removed, spaces collapsed.
LIST_NOUNS = (r"(line items?|items?|requests?|action items?|(follow up )?actions?|tasks?|instructions?|skills?|"
              r"knowledge|tools?|"
              r"technolog(y|ies)|requirements?|medications?|medicines?|drugs?|features?|aspects?|"
              r"persons?|people|names?|quotes?|quotations?|entr(y|ies)|lines?)")
_WHERE = (r"( (in|on|from) (the|this)( (provided|given|attached|above|original|supplied))? (document|text|email|"
          r"e mail|message|meeting|transcript|receipt|ad|"
          r"job ad|posting|report|case|case report|review|passage|sentence|excerpt|article|page|"
          r"biography|book|novel|chapter|list|notes|invoice))?")
_VERB = (r"( (found|available|mentioned|listed|identified|present|given|provided|specified|stated|assigned|"
         r"requested|asked|named|quoted|purchased|used|needed|noted|documented|reported|recorded))")
_TAIL = r"( [a-z0-9/]+){0,10}"
PLACEHOLDER_PATTERNS = [
    r"", r"n ?/? ?a", r"n a", r"none", r"null", r"nil", r"nothing", r"empty", r"blank", r"missing",
    r"unknown", r"unspecified", r"undefined", r"tbd", r"tba", r"placeholder", r"no data", r"no information",
    r"no", r"not",
    r"minitems|maxitems|string|description|type|error",          # schema words salvaged out of a broken output
    r"(none|nothing) (else|more|further)" + _TAIL,
    r"not (available|applicable|found|specified|provided|mentioned|given|stated|listed|identified|present|"
    r"known|relevant)" + _TAIL,
    r"(none|nothing) (found|available|mentioned|listed|identified|given|provided|specified|stated|applicable|"
    r"documented|noted|reported|recorded)" + _WHERE + _TAIL,
    r"(there (is|are|was|were) )?no (more|further|other|additional|remaining|extra|second|third|fourth|fifth|"
    r"other relevant)" + _TAIL,
    r"(there (is|are|was|were) )?no " + LIST_NOUNS + _TAIL,
    r"(there (is|are|was|were) )?no( [a-z]+){1,4}" + _VERB + _WHERE,
    r"there (is|are|was|were) (no|nothing)" + _TAIL,
    r"the [a-z]+( [a-z]+)? (contains|has|mentions|lists|includes|makes|gives|names) no" + _TAIL,
    r"(the |this )?(email|e mail|message|document|text|sender|author|speaker|team|reviewer|writer|patient|"
    r"meeting|transcript|ad|job ad|posting|report|case|review|passage|article|receipt|recipient|it|he|she|"
    r"they) (does|did|do) not (ask|mention|contain|list|include|request|name|have|specify|state|give|provide|"
    r"say|describe|quote|reference|refer to|discuss|indicate)" + _TAIL,
    r"(the |this )?(document|text|passage|excerpt|chapter|page|email|message|transcript|article) "
    r"(consists|is composed|is made up) (only|entirely|solely|purely) of" + _TAIL,
    r"(unable to|could not|cannot|can not|couldn t|did not|was not able to) (find|identify|locate|extract|see|"
    r"detect)" + _TAIL,
    r"only (one|two|three|four|five|six|single|\d+)" + _TAIL,
    r"(insufficient|not enough) (information|evidence|data)" + _TAIL,
    LIST_NOUNS + r"( (\d+|one|two|three|four|five))?( (none|n ?/? ?a|empty|placeholder|not found|missing|"
    r"unknown|not available|not applicable|not specified|tbd))?",
    LIST_NOUNS + r"( ?\d+| (one|two|three|four|five))",
    r"(unknown|unnamed|unidentified) " + LIST_NOUNS + r"( ?\d+| (one|two|three|four|five))",
    r"(additional|extra|another|other|more) " + LIST_NOUNS + r"( (\d+|needed|required))?",
    LIST_NOUNS + _VERB + r" (false|no|none|0)",                # "medications_mentioned: false"
    r"(reason|note|status) (none|nothing|n ?/? ?a|not (found|mentioned|available|applicable))( [a-z0-9/]+){0,4}",
]
PLACEHOLDER_RE = re.compile(r"^(?:" + "|".join(f"(?:{p})" for p in PLACEHOLDER_PATTERNS) + r")$")
ANON_TOKEN = re.compile(r"^<[A-Z_]+>$")
BRACKETED = re.compile(r"^\s*(\[[^\]]*\]|\([^)]*\)|<[^<>]*>|\{[^{}]*\})\s*$")
NUMBERED = re.compile(r"^\s*#\s*\d+\s*$")
# A model blocked by minItems may close the list inside an entry and go on in prose ('X]} is not valid
# because...'), or put a note in brackets after the entry ('X {Note: only 2 items...}'). Only the part
# before that is judged; an entry that starts by closing a bracket (']} ```...', '). Since the schema...')
# is spill from a broken output and never an item.
SPILL_START = re.compile(r"^\s*[)\]}:]")
SPILL_CUT = re.compile(r"""['"]?\s*\]\s*\}|[({]\s*\**\s*note\b|\*+\s*note\b""", re.I)
SCHEMA_TALK = re.compile(r"\b(minitems|maxitems|schema (requires|requirements?))\b")   # talk about the count rule


def _head(raw):
    if SPILL_START.match(raw):
        return ""
    m = SPILL_CUT.search(raw)
    return raw[:m.start()].strip() if m else raw


def normalise(s):
    s = s.replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    s = re.sub(r"\s+", " ", s.strip().lower())
    return s.strip(" \"'.,;:!")


def core(s):
    """Lower case, punctuation gone (apostrophes too, so "doesn't" -> "doesn t"), spaces collapsed."""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9/ ]+", " ", normalise(s))).strip()


def in_document(item, doc_text):
    """True when the item is a stretch of the document (at least 4 characters after normalising)."""
    if not doc_text:
        return False
    c = core(item)
    return len(c) >= 4 and f" {c} " in f" {core(doc_text)} "


def is_placeholder(item, escape_value="N/A", doc_text=None):
    raw = item.strip()
    if raw.upper() == escape_value.upper():
        return True
    if ANON_TOKEN.match(raw) or in_document(raw, doc_text):
        return False
    head = _head(raw)
    if BRACKETED.match(head) or NUMBERED.match(head):
        return True
    c = core(head)
    return bool(PLACEHOLDER_RE.match(c) or SCHEMA_TALK.search(c))


def _tokens(s):
    return {t[:-1] if len(t) > 3 and t.endswith("s") else t for t in core(s).split()}


def is_duplicate(item, earlier):
    """A repeat of an earlier entry: the same text, or the same words (plural s ignored) with the same
    numbers. "Lisinopril 10 mg" and "Lisinopril 20 mg" are two items; "Send the files" repeats
    "Send the file". Repeats said in other words are left to the item matcher."""
    a, ta, da = normalise(item), _tokens(item), re.findall(r"\d+", item)
    for e in earlier:
        b = normalise(e)
        if a == b:
            return True
        if not a or not b or re.findall(r"\d+", e) != da:
            continue
        tb = _tokens(e)
        jac = len(ta & tb) / max(1, len(ta | tb))
        if jac >= 0.85 and SequenceMatcher(None, a, b).ratio() >= 0.85:
            return True
    return False


def count_items(items, escape_value="N/A", doc_text=None):
    """Split an output list into substantive items, placeholders and duplicates (string level).

    Pass the document text (doc_text) so that an item copied from the document is never taken for a
    placeholder. Repeats in other words are left to the item matcher.
    """
    subst, ph, dup, esc = [], 0, 0, 0
    for it in items:
        if is_placeholder(it, escape_value, doc_text):
            ph += 1
            esc += it.strip().upper() == escape_value.upper()
        elif is_duplicate(it, subst):
            dup += 1
        else:
            subst.append(it)
    return {"n_items": len(items), "n_substantive": len(subst), "n_placeholder": ph,
            "n_escape": esc, "n_duplicate": dup, "substantive": subst}
