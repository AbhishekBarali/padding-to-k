"""MACCROBAT2020 loader: windows of 3-8 sentences from PubMed Central case reports.

Two list types per window:
  symptoms     Sign_symptom entities the patient HAS (item_type exact_quote)
  medications  Medication entities the patient was given (item_type named_entity)

Gold is copied from the brat annotation shipped with the dataset. Mentions the annotators
marked as negated (POLARITY NEG / MAYBE_NEG), hedged (POLARITY UNCERTAIN / MAYBE_POS) or
belonging to another person (MODIFY-linked to a Subject entity, or inside a Family_history
span) are kept out of gold and listed in meta as distractors. Nothing here adds gold.
"""
from __future__ import annotations

import collections
import json
import re
import statistics
import sys
import zipfile
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sources import _common  # noqa: E402

ZIP_NAME = "MACCROBAT2020.zip"

SOURCE = {
    "name": "maccrobat",
    "title": "MACCROBAT2020",
    "domain": "clinical",
    "list_types": ["symptoms", "medications"],
    "url": "https://doi.org/10.6084/m9.figshare.9764942.v2",
    "paper": (
        "Caufield, J. Harry (2019). MACCROBAT. figshare. Dataset. "
        "https://doi.org/10.6084/m9.figshare.9764942.v2 ; annotation scheme described in "
        "Caufield J.H. et al. (2019), A comprehensive typing system for information extraction "
        "from clinical narratives, medRxiv 10.1101/19009118"
    ),
    "licence": "CC-BY-4.0",
    "licence_url": "https://creativecommons.org/licenses/by/4.0/",
    "licence_quote": (
        "figshare article 9764942 v2 licence field: \"CC BY 4.0\" "
        "(https://creativecommons.org/licenses/by/4.0/)"
    ),
    "redistributable": True,
    "files": [
        {
            # figshare file ids are immutable; this is the file of article 9764942 version 2
            # (md5 9d090f3e0719e77e7a33c38750548bb8 as reported by the figshare API).
            "url": "https://ndownloader.figshare.com/files/21489405",
            "sha256": "a2d34ccd1a605d9147fc7368293e61dcf2090357b26f7bce6c2b3d257204acc6",
            "path": ZIP_NAME,
        }
    ],
    "unit_description": (
        "A window of 3 to 8 consecutive sentences (40 to 300 words) from one published "
        "clinical case report, with either the patient's annotated signs/symptoms or the "
        "medications annotated in that window."
    ),
    "how_gold_was_made": (
        "The dataset author's team annotated all 200 case reports by hand in brat "
        "(\"All annotations were created manually\", figshare description) with a 24+ type "
        "clinical event scheme, including Sign_symptom and Medication entities and a POLARITY "
        "attribute for negated or uncertain events. The loader lists the Sign_symptom or "
        "Medication spans inside a window, minus negated, hedged and other-person mentions."
    ),
    "known_issues": [
        "Literature-style case reports, not chart notes; the text was cut down to the case details by the dataset author.",
        "Sign_symptom also covers findings and disease-like terms (mass, lesion, tumor, metastasis, recurrence) and some states (healthy, asymptomatic, recovered); flagged as non_symptom_item.",
        "Medication includes generic classes and procedures (chemotherapy, antibiotics, medication, sedation, general anesthesia); flagged as generic_item.",
        "Negation comes only from the annotators' POLARITY attribute; a negated mention they did not mark would still be gold.",
        "Inter-annotator agreement for MACCROBAT is not reported on the figshare page (not verified).",
        "Windows from one report overlap; the build must use group to keep one report in one split.",
    ],
}

# --- window shape (task spec) ---
MIN_SENT, MAX_SENT = 3, 8
MIN_WORDS, MAX_WORDS = 40, 300
MAX_N = 8
CAP_PER_GROUP_N = 4  # candidate windows kept per (report, list_type, n), least overlapping first

LIST_TYPES = {
    "symptoms": ("Sign_symptom", "exact_quote"),
    "medications": ("Medication", "named_entity"),
}
NEG_VALUES = {"NEG", "MAYBE_NEG"}
HEDGE_VALUES = {"UNCERTAIN", "MAYBE_POS"}

# Strings a human checker should look at (flags only, gold is never changed by these).
NON_SYMPTOM = {
    "healthy", "asymptomatic", "recovered", "symptoms", "symptom", "symptomatic", "well",
    "complications", "complication", "recurrence", "relief", "improved", "improvement",
}
GENERIC_MED = {
    "medication", "medications", "drug", "drugs", "chemotherapy", "antibiotics", "antibiotic",
    "steroids", "steroid", "sedation", "general anesthesia", "general anaesthesia", "therapy",
    "treatment", "diuretics", "corticosteroids", "corticosteroid", "anticoagulant",
    "anticoagulation", "analgesics", "immunosuppressants", "inotropic agents", "pressors",
}
NUM = r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)"
COUNT_LEAK = re.compile(
    rf"\b{NUM}\s+(?:[\w-]+\s+)?(?:symptoms?|signs?|complaints?|medications?|drugs?|"
    rf"agents?|medicines?|therapies)\b",
    re.I,
)
# Whitespace normalisation: newline (sentence separator) and exotic spaces -> " ";
# zero-width space removed (offsets are remapped).
SPACE_LIKE = {"\n": " ", "\u2009": " ", "\u2005": " ", "\u200a": " ", "\u00a0": " ", "\u2002": " ", "\u2003": " "}
REMOVE = {"\u200b", "\ufeff"}
# A POLARITY NEG on a Sign_symptom sometimes means the symptom went away ("ascites rapidly
# resolved"), i.e. the patient DID have it. Windows holding such a mention are dropped.
RESOLVED = re.compile(
    r"resol|disappear|subsid|ameliorat|abat|regress|relie|no longer|ceas|cleared|vanish|"
    r"improv|weaned|withdraw|recover",
    re.I,
)


def fetch(cache: Path) -> Path:
    return _common.fetch_all(SOURCE, cache)


def _parse_ann(ann: str):
    T, E, A, R = {}, {}, collections.defaultdict(list), []
    for line in ann.splitlines():
        if not line.strip():
            continue
        p = line.split("\t")
        if line[0] == "T":
            ty, rest = p[1].split(" ", 1)
            frags = [tuple(map(int, x.split())) for x in rest.split(";")]
            T[p[0]] = {"id": p[0], "type": ty, "frags": frags, "text": p[2] if len(p) > 2 else ""}
        elif line[0] == "E":
            ty, tid = p[1].split()[0].split(":")
            E[p[0]] = tid
        elif line[0] == "A":
            x = p[1].split()
            if len(x) >= 3:
                A[x[1]].append((x[0], x[2]))
        elif line[0] == "R":
            x = p[1].split()
            R.append((x[0], x[1].split(":", 1)[1], x[2].split(":", 1)[1]))
    # attributes and relations may name the event (E) or the trigger (T)
    attrs = collections.defaultdict(list)
    for k, v in A.items():
        attrs[E.get(k, k)].extend(v)
    rels = [(rt, E.get(a, a), E.get(b, b)) for rt, a, b in R]
    return T, attrs, rels


def _normalise(raw: str):
    """Return (text, map) where map[i] = index in text of raw char i (or of the next kept char)."""
    out, mp = [], []
    for ch in raw:
        mp.append(len(out))
        if ch in REMOVE:
            continue
        out.append(SPACE_LIKE.get(ch, ch))
    mp.append(len(out))
    return "".join(out), mp


def _norm_str(s: str) -> str:
    return "".join(SPACE_LIKE.get(c, c) for c in s if c not in REMOVE)


def _doc_units(pmid: str, raw: str, ann: str, drops: collections.Counter):
    T, attrs, rels = _parse_ann(ann)
    # sentences = non-empty lines, with char offsets in raw
    sents, pos = [], 0
    for line in raw.split("\n"):
        if line.strip():
            sents.append((pos, pos + len(line)))
        pos += len(line) + 1

    other_subject = set()
    subj_ids = {k for k, t in T.items() if t["type"] == "Subject"}
    for rt, a, b in rels:
        if a in subj_ids:
            other_subject.add(b)
        if b in subj_ids:
            other_subject.add(a)
    dis_spans = [(t["frags"][0][0], t["frags"][-1][1], t["text"]) for k, t in T.items()
                 if t["type"] == "Disease_disorder"
                 and not any(v in NEG_VALUES | HEDGE_VALUES for a, v in attrs.get(k, []) if a == "POLARITY")]
    dis_spans += [(t["frags"][0][0], t["frags"][-1][1], "History:" + t["text"]) for t in T.values()
                  if t["type"] == "History"]
    fam_spans = [(t["frags"][0][0], t["frags"][-1][1], t["text"]) for t in T.values() if t["type"] == "Family_history"]

    ents = []  # one per Sign_symptom / Medication mention
    for k, t in T.items():
        if t["type"] not in ("Sign_symptom", "Medication"):
            continue
        s, e = t["frags"][0][0], t["frags"][-1][1]
        pol = [v for a, v in attrs.get(k, []) if a == "POLARITY"]
        role = "gold"
        if any(v in NEG_VALUES for v in pol):
            role = "negated"
        elif any(v in HEDGE_VALUES for v in pol):
            role = "hedged"
        elif k in other_subject or any(fs <= s and e <= fe for fs, fe, _ in fam_spans):
            role = "other_subject"
        resolved = False
        if role == "negated" and t["type"] == "Sign_symptom":
            ls = raw.rfind("\n", 0, s) + 1
            le = raw.find("\n", e)
            le = len(raw) if le < 0 else le
            resolved = bool(RESOLVED.search(raw[max(ls, s - 60):min(le, e + 60)]))
        ents.append({"id": k, "type": t["type"], "s": s, "e": e, "text": t["text"],
                     "disc": len(t["frags"]) > 1, "role": role, "pol": pol, "resolved": resolved,
                     "trend": [v for a, v in attrs.get(k, []) if a == "TREND"]})

    cands = collections.defaultdict(list)
    for i in range(len(sents)):
        for size in range(MIN_SENT, MAX_SENT + 1):
            if i + size > len(sents):
                break
            b, e = sents[i][0], sents[i + size - 1][1]
            raw_win = raw[b:e]
            text, mp = _normalise(raw_win)
            nw = _common.words(text)
            if nw < MIN_WORDS:
                drops["window_under_40_words"] += 1
                continue
            if nw > MAX_WORDS:
                drops["window_over_300_words"] += 1
                break  # larger windows from this start are longer still
            for lt, (bty, itype) in LIST_TYPES.items():
                inwin = [x for x in ents if x["type"] == bty and x["s"] < e and b < x["e"]]
                if any(not (b <= x["s"] and x["e"] <= e) for x in inwin):
                    drops[f"{lt}:item_crosses_window_edge"] += 1
                    continue
                bad = False
                mapped = []
                for x in inwin:
                    s2, e2 = mp[x["s"] - b], mp[x["e"] - b]
                    want = _norm_str(x["text"])
                    if text[s2:e2] != want:
                        bad = True
                        break
                    mapped.append(dict(x, s2=s2, e2=e2, t2=want))
                if bad:
                    drops[f"{lt}:discontinuous_or_mismatched_span"] += 1
                    continue
                mapped.sort(key=lambda x: (x["s2"], x["e2"]))
                if lt == "symptoms" and any(x["resolved"] for x in mapped):
                    drops["symptoms:negation_may_mean_resolved"] += 1
                    continue
                if lt == "medications" and any(x["role"] in ("negated", "hedged") for x in mapped):
                    # Medication NEG mostly marks a stopped drug the patient did take
                    drops["medications:non_positive_polarity_medication_in_window"] += 1
                    continue
                gold, seen, dedup = [], set(), False
                for x in mapped:
                    if x["role"] != "gold":
                        continue
                    key = x["t2"].strip().lower()
                    if key in seen:
                        dedup = True
                        continue
                    seen.add(key)
                    gold.append(x)
                n = len(gold)
                if n > MAX_N:
                    drops[f"{lt}:n_over_8"] += 1
                    continue
                cands[(lt, n)].append((i, size, b, e, text, nw, gold, mapped, dedup))

    for (lt, n), lst in cands.items():
        # least-overlapping selection: greedy by start, prefer windows disjoint from picked ones
        picked = []
        for c in sorted(lst, key=lambda c: (c[0], c[1])):
            if len(picked) >= CAP_PER_GROUP_N:
                break
            if all(c[0] >= p[0] + p[1] or p[0] >= c[0] + c[1] for p in picked):
                picked.append(c)
        for c in sorted(lst, key=lambda c: (c[1], c[0])):
            if len(picked) >= CAP_PER_GROUP_N:
                break
            if c not in picked:
                picked.append(c)
        drops[f"{lt}:not_selected_cap_{CAP_PER_GROUP_N}_per_report_per_n"] += len(lst) - len(picked)
        for c in picked:
            yield _make_unit(pmid, lt, n, c, fam_spans, dis_spans)


def _make_unit(pmid, lt, n, c, fam_spans, dis_spans):
    i, size, b, e, text, nw, gold, mapped, dedup = c
    bty, itype = LIST_TYPES[lt]
    flags = ["whitespace_normalised:sentence_newlines_to_spaces"]
    gold_items = [{"text": g["t2"], "start": g["s2"], "end": g["e2"], "evidence": None} for g in gold]

    def dl(role):
        return [{"text": x["t2"], "start": x["s2"], "end": x["e2"], "polarity": x["pol"]}
                for x in mapped if x["role"] == role]

    neg, hedged, other = dl("negated"), dl("hedged"), dl("other_subject")
    if n == 0:
        flags.append(f"n0_certified_by:full_report_brat_annotation_no_positive_{bty}_in_window")
    if neg:
        flags.append("negated_mentions_present")
    if hedged:
        flags.append("hedged_mentions_present")
    if other:
        flags.append("other_subject_mentions_present")
    fam = [t for fs, fe, t in fam_spans if b <= fs and fe <= e]
    if fam:
        flags.append("family_history_present")
    if lt == "symptoms" and any(b <= ds and de <= e and not t.startswith("History:") for ds, de, t in dis_spans):
        flags.append("disease_mentions_present")
    if lt == "symptoms" and any(b <= ds and de <= e and t.startswith("History:") for ds, de, t in dis_spans):
        flags.append("history_mentions_present")
    if dedup:
        flags.append("gold_dedup")
    low = [g["text"].lower() for g in gold_items]
    for x in low:
        for y in low:
            if y in (x + "s", x + "es"):
                flags.append(f"gold_near_duplicate:{x}|{y}")
    for g in gold_items:
        t = g["text"]
        if t.isupper() and 2 <= len(t) <= 6:
            for o in gold_items:
                ini = "".join(w[0] for w in re.findall(r"[A-Za-z]+", o["text"])).upper()
                if o is not g and ini == t:
                    flags.append(f"gold_abbreviation_pair:{t}={o['text'].lower()}")
    gl = {g["text"].lower() for g in gold_items}
    if any(x["text"].lower() in gl for x in neg + hedged + other):
        flags.append("item_also_negated_or_hedged_in_window")
    for g in gold_items:
        k = g["text"].lower()
        if lt == "symptoms" and k in NON_SYMPTOM:
            flags.append(f"non_symptom_item:{k}")
        if lt == "medications" and k in GENERIC_MED:
            flags.append(f"generic_item:{k}")
    for a in gold_items:
        for o in gold_items:
            if a is not o and a["start"] <= o["start"] and o["end"] <= a["end"]:
                flags.append("nested_gold_spans")
                break
        else:
            continue
        break
    for m in COUNT_LEAK.finditer(text):
        flags.append(f"possible_count_leak:{m.group(0).lower()}")
    raw_ids = [x["id"] for x in mapped]
    return {
        "source_id": f"maccrobat2020:{pmid}:sent{i}-{i + size - 1}:chars{b}-{e}:{lt}",
        "group": f"maccrobat2020:{pmid}",
        "text": text,
        "n": n,
        "gold_items": gold_items,
        "list_type": lt,
        "item_type": itype,
        "flags": flags,
        "meta": {
            "pmid": pmid,
            "brat_type": bty,
            "sentence_start": i,
            "sentence_count": size,
            "raw_char_range": [b, e],
            "words": nw,
            "gold_brat_ids": [g["id"] for g in gold],
            "gold_trend": {g["t2"]: g["trend"] for g in gold if g["trend"]},
            "negated_distractors": neg,
            "hedged_distractors": hedged,
            "other_subject_distractors": other,
            "family_history_spans": fam,
            "brat_ids_in_window": raw_ids,
            "release": "MACCROBAT2020 (figshare 9764942 v2, file 21489405)",
        },
    }


def units(cache: Path, drops: collections.Counter | None = None):
    drops = drops if drops is not None else collections.Counter()
    zpath = Path(cache) / SOURCE["name"] / ZIP_NAME
    with zipfile.ZipFile(zpath) as z:
        names = sorted(n for n in z.namelist() if n.endswith(".txt"))
        for name in names:
            pmid = Path(name).stem
            raw = z.read(name).decode("utf-8")
            ann = z.read(name[:-4] + ".ann").decode("utf-8")
            for u in _doc_units(pmid, raw, ann, drops):
                _common.check_unit(u)
                yield u


if __name__ == "__main__":
    import time

    t0 = time.time()
    _common.check_source(SOURCE)
    fetch(_common.DEFAULT_CACHE)
    drops = collections.Counter()
    us = list(units(_common.DEFAULT_CACHE, drops))
    for lt in SOURCE["list_types"]:
        sub = [u for u in us if u["list_type"] == lt]
        hist = collections.Counter(u["n"] for u in sub)
        print(f"== {lt}: {len(sub)} units, {len({u['group'] for u in sub})} reports")
        print("n histogram:", dict(sorted(hist.items())))
        print("median words per n:", {n: statistics.median(u["meta"]["words"] for u in sub if u["n"] == n) for n in sorted(hist)})
        print("reports per n:", {n: len({u["group"] for u in sub if u["n"] == n}) for n in sorted(hist)})
        fc = collections.Counter(f.split(":")[0] for u in sub for f in u["flags"])
        print("flags:", dict(fc.most_common()))
    print("drops/not selected:", dict(drops.most_common()))
    for u in (us[0], next(u for u in us if u["list_type"] == "symptoms" and u["n"] == 2),
              next(u for u in us if u["list_type"] == "medications" and u["n"] == 1)):
        print(json.dumps(u, ensure_ascii=True)[:3000])
    print(f"runtime {time.time() - t0:.1f}s")
