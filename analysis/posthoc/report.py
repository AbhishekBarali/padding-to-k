"""POST HOC: assemble analysis/posthoc/out/POSTHOC.md from the numbers posthoc.py and lenient_08b.py wrote.

Every number in POSTHOC.md is formatted here from analysis/posthoc/out/posthoc_results.json and
lenient_08b.json; none is typed by hand.
"""
import json

import common_posthoc as cp
from common_posthoc import full_study as fs

PY = ("uv run --no-project --offline --python 3.12 --with pandas==3.0.6 --with numpy==2.5.4 --with scipy==1.18.1 "
      "--with statsmodels==0.15.0 --with patsy==1.0.3 --with rapidfuzz==3.14.6 --with pyyaml python")


def table(head, rows):
    return ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(map(str, r)) + " |" for r in rows]


def rate(r):
    return [r["entries"], r["exact_pass_pct"], r["fuzzy90_pass_pct"], r["repo_core_pass_pct"]]


def ci3(v, nd=3):
    return f"{v[0]:.{nd}f}" if not isinstance(v, list) else f"{v[0]:.1f} [{v[1]:.1f}, {v[2]:.1f}]"


def write(res):
    L = []
    lj = json.loads((cp.OUT / "lenient_08b.json").read_text())
    s_c2 = fs.fmt(lj["strict"]["C2_length"])
    sec2 = (cp.ROOT / "analysis" / "full" / "RESULTS.md").read_text(encoding="utf-8").split("\n## 2.")[1].split("\n## ")[0]
    row = next(r for r in sec2.split("\n") if r.startswith("| Qwen3.5-0.8B |"))
    paper_c2 = row.split("|")[3].strip()
    print("CHECK 0.8B C2 strict", s_c2, "RESULTS.md", paper_c2, "equal", s_c2 == paper_c2)
    sc, pv, pr, ck = res["source_check"], res["prevalence"], res["prf"], res["checks"]
    g = sc["gpu_n_lt_k_k35"]
    L += ["# POST HOC analyses (not in the registered plan)", "",
          "Every result in this file is POST HOC: none of these analyses is in `preregistration/protocol-stage2.md`. "
          "Nothing in `preregistration/manifest-stage2.sha256` was changed; the locked parser, placeholder rules and "
          "matcher v0 are used as they are (the lenient parser of section 4 is a separate function in "
          "`analysis/posthoc/lenient_08b.py`). Every matcher-based number is matcher v0 and preliminary, as in the paper.", "",
          "## Scope and inputs", "",
          "- Runs: the `fs_<model>_full` runs, arm `main`, ok outputs (as `analysis/full_study.py`). **GPU** = the 8 main "
          "GPU models pooled (" + ", ".join(fs.NAME[m] for m in cp.lineup()[0]) + "); **hosted** = the 9 hosted models "
          "pooled (reference only, as in the paper).",
          "- Labels: the cached matcher v0 labels in `analysis/full/scored/*.entries.csv.gz` (written by "
          "`analysis/full_study_score.py`); `analysis/posthoc/check_cache.py` confirms every cached table matches its run "
          "folder (same source hash the scorer uses). Entry text: re-parsed from the run records with the locked "
          "`common.parse_output` (`analysis/posthoc/build_entries.py`; it stops if parse and cache disagree on any "
          "output's entry count).",
          "- Extra entry: a substantive entry the matcher does not match to a distinct true item (labels true-but-split, "
          "wrong kind, invented), the paper's definition (`full_study.py` section 6b).",
          "- `none` is asked once and its answer reused at k = 1, 3 and 5; as in `full_study.py`, a `none` entry counts "
          "once per k it answers.", "",
          "Checks that could fail:", "",
          f"- GPU extra entries per condition (n < k, k = 3 and 5) from the entry table equal the per-output sums the "
          f"paper's table uses, for every condition: "
          + ", ".join(f"{c} {v['entries_table']}" for c, v in ck["gpu_extras_n_lt_k_vs_outputs"].items())
          + f" (all equal: {all(v['equal'] for v in ck['gpu_extras_n_lt_k_vs_outputs'].values())}).",
          f"- The 400-entry check frame (`analysis/human/matcher_frame.json`) against this table: wrong kind "
          f"{ck['frame_counts']['this_table']['in_text_wrong_type']} vs {ck['frame_counts']['matcher_frame_json']['in_text_wrong_type']}, "
          f"invented {ck['frame_counts']['this_table']['plausible_invented']} vs {ck['frame_counts']['matcher_frame_json']['plausible_invented']}, "
          f"true or split {ck['frame_counts']['this_table']['true_or_split']} vs {ck['frame_counts']['matcher_frame_json']['true_or_split']}. "
          "The true-or-split difference is all in novel quotes: three GPU runs (0.8B, 2B, gpt-oss-20b) got resent records "
          "on 19 Oct, after the frame was drawn on 18 Oct.",
          f"- Lenient parser: of the {lj['unchanged_check']['outputs_readable_strict']} 0.8B outputs the locked parser "
          f"reads, {lj['unchanged_check']['changed_by_lenient']} change under the lenient one; the strict 0.8B contrast 2 "
          f"of section 4 ({s_c2}) against RESULTS.md section 2 ({paper_c2}): equal {s_c2 == paper_c2}.", "",
          "Reproduce (from the repository root; `data/local` must hold the restricted review documents):", "",
          "```", f"{PY} analysis/posthoc/check_cache.py <runs-dir>",
          f"{PY} analysis/posthoc/build_entries.py --runs-dir <runs-dir> --jobs 3",
          f"{PY} analysis/posthoc/lenient_08b.py --runs-dir <runs-dir> --boot 10000",
          f"{PY} analysis/posthoc/posthoc.py --boot 10000", "```", "",
          "`<runs-dir>` is the folder of `fs_*` run folders. `build_entries.py` writes `analysis/posthoc/cache/` "
          "(gitignored: it holds entry text, review text included). Outputs: `analysis/posthoc/out/`.", ""]

    # ---- 1
    hdr = ["", "entries", "exact substring %", "fuzzy (partial_ratio >= 90) %", "repo's own in_document %"]
    L += ["## 1. Source check: would a deployable grounding check catch the extra entries?", "",
          "Each entry against its own source document. **exact**: the entry, normalised (Unicode NFKC, curly quotes "
          "and dashes made plain, lower case, whitespace collapsed, quotes and punctuation stripped from both ends; "
          "`common_posthoc.gnorm`), is a substring of the normalised document. **fuzzy**: exact, or rapidfuzz "
          "`fuzz.partial_ratio(entry, document) >= 90` on the same normalised strings. **in_document**: the repo's "
          "own `common.in_document` (punctuation removed, at least 4 characters), for reference. No entry is empty "
          f"after normalising ({g['extra_pooled']['empty']} empty extra entries). Pass = the check would let the "
          "entry through.", "",
          "GPU, documents with n < k, k = 3 and 5:", ""]
    rows = [["extra entries, all", *rate(g["extra_pooled"])]]
    rows += [[f"extra: {cp.LABEL_NAME[l]}", *rate(g["extra_by_label"][l])] for l in cp.EXTRA]
    rows += [["true-item entries (reference)", *rate(g["true_item_pooled"])]]
    rows += [["extra entries, the 7 copied-text sets", *rate(g["quote_sets_extra"])],
             ["invented entries, the 7 copied-text sets", *rate(g["quote_sets_invented"])],
             ["true-item entries, the 7 copied-text sets", *rate(g["quote_sets_true"])]]
    L += table(hdr, rows)
    L += ["", "The 7 copied-text sets leave out meetings (the item is a one-sentence summary, so no item is a copy) and "
          "Wikipedia people (names). By condition (GPU, n < k, k = 3 and 5):", ""]
    rows = []
    for c in fs.CONDS:
        a, b, t = g["extra_by_condition"][c], g["invented_by_condition"][c], g["true_by_condition"][c]
        rows.append([c, a["entries"], a["exact_pass_pct"], a["fuzzy90_pass_pct"], b["entries"], b["exact_pass_pct"],
                     b["fuzzy90_pass_pct"], t["exact_pass_pct"], t["fuzzy90_pass_pct"]])
    L += table(["condition", "extra entries", "exact %", "fuzzy %", "invented entries", "invented exact %",
                "invented fuzzy %", "true items exact %", "true items fuzzy %"], rows)
    L += ["", "By set (GPU, n < k, k = 3 and 5):", ""]
    rows = []
    for s in fs.SETS:
        a, b, t = g["extra_by_set"][s], g["invented_by_set"][s], g["true_by_set"][s]
        rows.append([fs.SET_NAME[s], a["entries"], a["exact_pass_pct"], a["fuzzy90_pass_pct"], b["entries"],
                     b["exact_pass_pct"], t["exact_pass_pct"], t["fuzzy90_pass_pct"]])
    L += table(["set", "extra entries", "exact %", "fuzzy %", "invented entries", "invented exact %",
                "true items exact %", "true items fuzzy %"], rows)
    for nm, title in (("gpu_all_docs_k35", "GPU, all documents (any n), k = 3 and 5"),
                      ("hosted_n_lt_k_k35", "Hosted, n < k, k = 3 and 5")):
        r = sc[nm]
        L += ["", f"{title}:", ""]
        L += table(hdr, [["extra entries", *rate(r["extra_pooled"])],
                         *[[f"extra: {cp.LABEL_NAME[l]}", *rate(r["extra_by_label"][l])] for l in cp.EXTRA],
                         ["true-item entries", *rate(r["true_item_pooled"])]])
    h = res["source_check_human"]
    L += ["", "The matcher calls an entry invented largely because it is not found in the text, so the invented rows "
          "above are close to circular. The 400 entries the authors labelled give a check that does not lean on the "
          f"matcher ({h['found_in_table']} of {h['checked_entries']} found in the entry table), by the authors' settled label:", ""]
    L += table(hdr, [[k, *rate(v)] for k, v in h["by_authors_label"].items()])
    L += ["", f"**Result.** About half the extra entries pass: {g['extra_pooled']['exact_pass_pct']}% exact and "
          f"{g['extra_pooled']['fuzzy90_pass_pct']}% fuzzy (GPU, n < k), against {g['true_item_pooled']['exact_pass_pct']}% and "
          f"{g['true_item_pooled']['fuzzy90_pass_pct']}% of true-item entries. Wrong-kind entries pass at "
          f"{g['extra_by_label']['in_text_wrong_type']['exact_pass_pct']}% / {g['extra_by_label']['in_text_wrong_type']['fuzzy90_pass_pct']}%; "
          f"invented entries almost never do ({g['extra_by_label']['plausible_invented']['exact_pass_pct']}% / "
          f"{g['extra_by_label']['plausible_invented']['fuzzy90_pass_pct']}%), and none of the "
          f"{h['by_authors_label']['plausible_invented']['entries']} entries the authors call invented passes either check. "
          f"Under the shown minimum {g['extra_by_condition']['min_k_shown']['exact_pass_pct']}% of extra entries pass exact. "
          "So a grounding check removes the invented padding and keeps most of the wrong-kind padding; on the copied-text "
          f"sets it passes {g['quote_sets_extra']['exact_pass_pct']}% of extra entries.", ""]

    # ---- 2
    a = pv["gpu_min_k_shown_n_lt_k_k35"]
    cor = pv["corrected_gpu_min_k_shown_n_lt_k_k35"]
    cs = pv["check_sample"]
    L += ["## 2. Prevalence: what the extra entries are under the shown minimum", "",
          "Share of extra entries by matcher v0 label, documents with n < k, k = 3 and 5, condition `min_k_shown`:", ""]
    rows = []
    for nm, title in (("gpu_min_k_shown_n_lt_k_k35", "GPU (8 main models)"), ("gpu_none_n_lt_k_k35", "GPU, `none` (for comparison)"),
                      ("hosted_min_k_shown_n_lt_k_k35", "hosted (9 models)"), ("all17_min_k_shown_n_lt_k_k35", "all 17 models")):
        v = pv[nm]
        rows.append([title, v["extra_entries"], v["share_of_extras_pct"]["true-but-split"], v["share_of_extras_pct"]["wrong kind"],
                     v["share_of_extras_pct"]["invented"], v["invented_not_echo_or_note_pct_of_extras"],
                     v["invented_share_of_substantive_pct"]])
    L += table(["pool", "extra entries", "true-but-split %", "wrong kind %", "invented %",
                "invented, not prompt echo or note %", "invented % of all substantive entries"], rows)
    L += ["", "Corrected with the authors' labels: each matcher label's extra entries are spread over the authors' "
          "categories in the proportions the settled 400-entry check gives for that matcher label (authors' "
          "missed_gold counted as a true item, 2 unsure rows dropped; the matcher's true-but-split label has only "
          f"{sum(cs['confusion_rows_matcher_label']['split_of_true'].values())} checked rows). 95% interval: "
          "10,000 resamples of the checked rows within each matcher label (seed 20261014). The proportions come from the "
          "whole check frame, not from this cell: only "
          f"{pv['check_rows_in_gpu_min_k_shown_n_lt_k']['rows']} checked rows are GPU `min_k_shown` with n < k.", ""]
    rows = [[k, ci3(v)] for k, v in cor.items() if k != "matcher_extras"]
    L += table(["GPU `min_k_shown`, n < k, k = 3 and 5 (" + str(cor["matcher_extras"]) + " matcher extra entries)",
                "share [95% CI]"], rows)
    L += ["", "Checked rows by matcher label and authors' label: " + "; ".join(
        f"matcher {m}: " + ", ".join(f"{k} {n}" for k, n in sorted(v.items())) for m, v in cs["confusion_rows_matcher_label"].items()) + ".", "",
          f"**Settled.** Both numbers are right; they have different denominators. The ~7% is the invented share of "
          f"*all substantive entries* (true items included) over the whole check frame: all 17 models, all conditions, "
          f"all k and n ({pv['frame_invented_share_of_substantive_pct']}% from this table; the paper's 7.0% matcher / 7.3% "
          f"corrected). The ~30% is the invented share of the *extra entries* on documents with n < k under the shown "
          f"minimum, GPU models: {a['share_of_extras_pct']['invented']}% by the matcher "
          f"({a['invented_not_echo_or_note_pct_of_extras']}% without prompt echoes and possible notes, the paper's 29.5%), "
          f"{ci3(cor['invented % of matcher extras'])}% after correcting with the authors' labels. So the reviewer's "
          f"~30% is the matcher's figure for the padding itself; the corrected figure is about a quarter; the 7% must not "
          f"be read as the invented share of the padding. The share depends on the models: hosted models' extras are "
          f"{pv['hosted_min_k_shown_n_lt_k_k35']['share_of_extras_pct']['invented']}% invented, all 17 pooled "
          f"{pv['all17_min_k_shown_n_lt_k_k35']['share_of_extras_pct']['invented']}%.", "",
          f"**Was the 400-entry sample stratified?** Yes, by matcher label: {cs['drawn_per_stratum']['true_or_split']} "
          f"true-or-split, {cs['drawn_per_stratum']['in_text_wrong_type']} wrong kind, {cs['drawn_per_stratum']['plausible_invented']} "
          "invented (the protocol's 80 per label, with the two labels v0 never assigns given to the other three), and "
          "within a label as equally as possible over the 9 sets, at most one entry per output, from every substantive "
          "entry of the 17 full runs (`analysis/full_study_sheets.py`, `draw_matcher_labels`). The sample's own label "
          "shares are therefore not prevalences; the paper's 7.3% weights each stratum by its frame size.", ""]

    # ---- 3
    L += ["## 3. Precision, recall and F1 per condition", "",
          "Entry level, matcher v0, k = 3 and 5, ok outputs (unreadable outputs count as 0 entries, so they lower recall "
          "and leave precision alone). Precision = true-item entries / substantive entries (a split piece, a wrong-kind "
          "or an invented entry is not a correct entry; `precision, split ok` also counts true-but-split pieces as "
          "correct). Recall = true items some entry matches (true-item and split labels) / true items, on documents "
          "with n >= 1. F1 from the pooled P and R. Pooled = summed over outputs. 95% intervals: full_study's "
          "bootstrap, 10,000 draws over document groups within set, seed 20261014.", ""]
    for scope, title in (("pooled_gpu", "GPU, all documents"), ("pooled_gpu_n_lt_k", "GPU, documents with n < k")):
        rows = []
        for c in fs.CONDS:
            v = pr[scope][c]
            rows.append([c, v["outputs"], v["substantive"], f"{v['precision']:.3f} [{v['precision_ci'][0]:.3f}, {v['precision_ci'][1]:.3f}]",
                         f"{v['precision_split_ok']:.3f}", f"{v['recall']:.3f} [{v['recall_ci'][0]:.3f}, {v['recall_ci'][1]:.3f}]",
                         f"{v['f1']:.3f} [{v['f1_ci'][0]:.3f}, {v['f1_ci'][1]:.3f}]", f"{v['mean_extra']:.2f}"])
        L += [f"{title}:", ""] + table(["condition", "outputs", "substantive entries", "precision", "precision, split ok",
                                         "recall", "F1", "extra entries per output"], rows) + [""]
    rows = [[c, f"{v['precision']:.3f}", f"{v['recall']:.3f}", f"{v['f1']:.3f}", f"{v['mean_extra']:.2f}"]
            for c, v in pr["pooled_hosted"].items()]
    L += ["Hosted, all documents (reference; `min_k_enforced` / `min_k_escape` only on the hosted models that ran them):", ""]
    L += table(["condition", "precision", "recall", "F1", "extra entries per output"], rows) + [""]
    main, hosted = cp.lineup()
    rows = []
    for m in main + hosted:
        pm = pr["per_model"].get(m, {})
        cells = []
        for c in ("none", "min_k_shown", "min_k_shown_fewer_ok", "min_k_enforced"):
            v = pm.get(c)
            cells.append(f"{v['precision']:.2f} / {v['recall']:.2f} / {v['f1']:.2f}" if v else "--")
        rows.append([fs.NAME.get(m, m), *cells])
    L += ["Per model, all documents, precision / recall / F1 (every condition in `out/prf.csv`):", ""]
    L += table(["model", "none", "min_k_shown", "min_k_shown_fewer_ok", "min_k_enforced"], rows)
    n0, ms, en = pr["pooled_gpu"]["none"], pr["pooled_gpu"]["min_k_shown"], pr["pooled_gpu"]["min_k_enforced"]
    L += ["", f"**Result.** A shown minimum costs precision and buys no recall: GPU pooled, all documents, precision "
          f"{ms['precision']:.3f} vs {n0['precision']:.3f} with no count, recall {ms['recall']:.3f} vs {n0['recall']:.3f}, "
          f"F1 {ms['f1']:.3f} vs {n0['f1']:.3f}. An enforced minimum raises recall to {en['recall']:.3f} at precision "
          f"{en['precision']:.3f} (F1 {en['f1']:.3f}).", "",
          "Padding vs missed true items per (model, condition): `out/padding_vs_missed.csv` (all 17 models; x = mean "
          "extra entries per output, y = 100 x (1 - recall), k = 3 and 5, all documents; also the n < k padding and P, R, "
          "F1). `out/fig_padding_vs_missed.tex` plots the 8 GPU models (one mark per model and condition, condition by "
          "mark, `\\footnotesize` labels): `\\input{.../fig_padding_vs_missed.tex}` inside a `figure`; it uses "
          "pgfplots and the paper's `\\cnd` macro.", ""]

    # ---- 4
    s, l = lj["strict"], lj["lenient"]
    L += ["## 4. Qwen3.5-0.8B with a lenient parser", "",
          "The locked parser never takes a schema-shaped object as the answer, and 0.8B often writes its list inside a "
          "copy of the schema (`{\"type\": \"object\", \"properties\": {\"requests\": [ ... ]}}`). The lenient parser "
          "(`lenient_08b.py`, `parse_lenient`) runs the locked ladder first; only when it finds no list it searches every "
          "JSON object of the reply for the asked-for field and takes its list (directly, or the `items` list of a schema "
          "copy). A schema echo with no list in it, and broken JSON (missing commas, unescaped quotes), stay "
          "unreadable. The 0.8B run is then rescored with the repo's own scorer (`full_study_score.score_run`, parse "
          "call swapped in-process only) and analysed with `full_study.py`'s own pairing and bootstrap.", ""]
    L += (cp.OUT / "lenient_08b.md").read_text(encoding="utf-8").split("\n")[4:]
    L += [f"**Result.** The lenient parser cuts 0.8B's unreadable share from {s['unreadable_pct']}% to "
          f"{l['unreadable_pct']}%. The registered contrast 2 (unreadable = 0 entries) barely moves on length "
          f"({fs.fmt(s['C2_length'])} strict, {fs.fmt(l['C2_length'])} lenient), because the shown minimum still holds "
          f"more pure schema echoes ({l['per_condition_n_lt_k']['min_k_shown']['unreadable_pct']}% unreadable vs "
          f"{l['per_condition_n_lt_k']['none']['unreadable_pct']}% under `none`). On over-count it moves from "
          f"{fs.fmt(s['C2_over_count'], 100, 1)} to {fs.fmt(l['C2_over_count'], 100, 1)} points. On the pairs readable on "
          f"both sides the sign is positive under both parsers: locked parser {fs.fmt(s['C2_length_readable_pairs'])} "
          f"entries and {fs.fmt(s['C2_over_count_readable_pairs'], 100, 1)} points ({s['C2_length_readable_pairs']['pairs']} "
          f"pairs); lenient {fs.fmt(l['C2_length_readable_pairs'])} entries and "
          f"{fs.fmt(l['C2_over_count_readable_pairs'], 100, 1)} points ({l['C2_length_readable_pairs']['pairs']} pairs). "
          "So the negative registered estimate for 0.8B comes from unreadable outputs counted as empty lists, not from "
          "shorter lists. With the lenient parser 0.8B shows the over-count effect but no clear length change; it pads "
          f"under every condition ({l['per_condition_n_lt_k']['none']['over_count_pct']}% over-count with no count). "
          "Readable-pairs numbers condition on readability, which the condition itself changes, so they are "
          "descriptive only.", ""]

    # ---- 5
    ex = (cp.OUT / "examples.md").read_text(encoding="utf-8")
    para = (cp.POSTHOC / "reviews_paraphrase.md").read_text(encoding="utf-8").strip()
    ex = ex.replace("REVIEWS_PARAPHRASE", para)
    L += ["## 5. Examples: padding under the shown minimum", "",
          "One real output per answer-list set: GPU main models, condition `min_k_shown`, k = 3 or 5, a document with "
          "1 <= n < k, an over-count output (more substantive entries than true items), at most 6 entries of at most 200 "
          "characters, at least one extra entry; among those, the output with the smallest sha256 of run id and request "
          "id (no hand picking). Labels are matcher v0 and can be wrong: in the emails example the matcher pairs the "
          "first entry with a true item and calls the near-verbatim second entry a split; the count of extra entries "
          "(entries minus true items) is right either way. Entries and true items are verbatim; the review is "
          "paraphrased (restricted text).", "", ex]
    (cp.OUT / "POSTHOC.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("wrote", cp.OUT / "POSTHOC.md")
