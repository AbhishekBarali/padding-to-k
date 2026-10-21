# Pad to k: the test data

Built 13 Oct 2026 for the H+I study (see `../PLAN/index.html` and `../GUIDE-H+I-research-handbook.md`).

## Summary

- **What this is.** Real documents (meetings, emails, receipts, job ads, medical case reports, product
  reviews, plus Wikipedia sentences and novel passages) where we know exactly how many true items each one
  contains: 0, 1, 2 or 3 for the main test, 4 to 6 for the "asked for fewer than exist" test. Each document
  comes with the ready-made test prompts for all 7 conditions at k = 1, 3, 5, and the correct answer for
  each condition.
- **Where the true items come from.** From the people who built each original dataset (their annotators),
  then checked by a cleanup pass under written counting rules (`cleanup/`, section 7). The cleanup fixed
  lists that were clearly wrong, dropped documents with no single right count, and keeps the annotators'
  list next to every change. No document text was changed, except removing text that would give away the
  count.
- **Size.** 1,446 documents checked (1,110 first candidates plus a second batch of 336 spares). Final, after
  the cleanup, the authors' check and trimming to the final numbers: 558 in the study (60 pilot, 498 full),
  311 clean spares, 577 dropped. 25,110 prompts per model (23,994 sends: the no-count prompt is the
  same at every k); the pilot sends 420 per model (`../PLAN/RUN-PLAN.md` section 5.2).
- **Status (13 Oct 2026).** Both authors went through the cleanup review and agreed with every decision. They
  settled the 3 open questions and confirmed the counting rules (`cleanup/README.md`). Every cell is now
  trimmed to its final number (section 4). Next: the blind check without the answer lists
  (`blind_check.py`, section 7), then freeze the data (hash and git tag). How the models are run:
  `../PLAN/RUN-PLAN.md`.
- **One thing to know.** Real answer lists are not perfect: the cleanup changed or dropped about half of
  all documents (`cleanup/REPORT.md`). Two cells are short of the target: emails n = 3 (11 of 15) and
  job_posts_knowledge n = 3 (12 of 15), plus the emails 4-6 arm (5 of about 10). Scoring labels:
  section 8.

## 1. What the data is for

The study asks: when a prompt or JSON schema asks for k items and the document only has n < k, does the
model invent the rest? To score that, every document needs a trustworthy answer list. The plan was to write
documents and answer lists by hand. Instead, these come from published datasets in which human annotators
already marked every item. That saves the writing, and it answers the reviewer question "does this happen
on real text?" with the main result instead of a side check.

## 2. Where the documents come from

| Set | One document is | List asked for | Item type | Source | Licence | In this repo? |
|---|---|---|---|---|---|---|
| meetings | a window of a meeting transcript (median 388 words) | action items | vague theme (annotator's summary sentence) | AMI Meeting Corpus, Carletta et al. 2005 | CC BY 4.0 | yes |
| emails | one Enron email (median 62 words) | requests | exact quote | MailEx, Srivastava et al. EMNLP 2023 | CC BY-SA 4.0 | yes |
| receipts | one receipt as plain text (median 20 words) | items purchased | name | CORD v2, Park et al. 2019 | CC BY 4.0 | yes |
| job_posts | 4-10 sentences of one job ad (median 107 words) | skills (includes duties) | exact quote | SkillSpan, Zhang et al. NAACL 2022 | CC BY 4.0 | yes |
| clinical | 3-8 sentences of a published case report (median 76 words) | medications | name | MACCROBAT2020, Caufield 2019 (PubMed Central) | CC BY 4.0 | yes |
| reviews | one product or service review (median 66 words) | features the reviewer comments on | exact quote | ROAST, Chebolu et al. 2024 | annotations Apache-2.0; review text unclear | **no**: rebuilt locally into `local/` |
| job_posts_knowledge | same kind of job-ad window | tools, technologies, fields | name | SkillSpan | CC BY 4.0 | yes |
| wiki_people | one Wikipedia sentence (median 23 words) | people | name | Few-NERD, Ding et al. ACL 2021 | CC BY-SA 4.0 | yes |
| novel_quotes | 1-3 paragraphs of a novel (median 92 words) | direct speech | exact quote | PDNC, Vishnubhotla et al. 2022 | CC BY 4.0 (novels public domain in the US) | yes |

`sources/bc3.py` loads BC3 (261 emails, 3 annotators each, CC BY-SA 3.0) as a backup email source; it is not
used in the sets above.

Full details per source (URL, pinned revision, sha256 of every file, the exact licence sentence, how the
answer lists were made, known issues) are in `sources.yaml`.

The first six sets are the six domains of the plan. The last three are for the item-type question (RQ4):
`job_posts` vs `job_posts_knowledge` compares quotes and names inside the same kind of text, and
`wiki_people` vs `novel_quotes` adds two more genres.

Licences: MailEx and Few-NERD are share-alike, so a released benchmark that contains their text must also be
CC BY-SA 4.0. Our own code and annotations can stay MIT / CC BY 4.0. Enron emails are real people's mail,
public since 2003; worth one line in the ethics statement.

## 3. How the data was collected

1. **Download.** Each loader in `sources/` downloads the original files from the dataset's own public URL at a
   pinned revision and checks their sha256.
2. **Cut documents.** Long originals (meetings, job ads, case reports, novels) are cut into windows that hold a
   known number of whole items, on sentence or speaker-turn boundaries.
3. **Copy the answer list.** The annotators' items are copied with their exact position in the text, so code
   can always find them. Meeting action items are the annotator's own summary sentences; each one carries
   the lines of the meeting it was linked to (`evidence`).
4. **Zero-item documents only when the annotation proves it.** For example: the AMI annotator wrote "NA" under
   action items, or the whole report was annotated and contains no medication. Receipts and reviews have no
   zero-item documents, because real ones barely exist.
5. **Remove count give-aways.** For example, 223 receipts print "TOTAL ITEMS 3"; that line was removed and
   flagged. No other text was changed except whitespace, re-joining tokens, and repairing broken characters
   (each change is recorded in the document's `flags`).
6. **Choose documents.** `build.py` picks documents with a fixed random seed (20261013): at most one document
   per original meeting, email thread, job ad, case report or novel chapter, cleaner documents first (no
   warning flags), and similar lengths across n where length would otherwise hint at the answer.
   Document ids (e.g. `eml-233b79`) are a hash of the source, so they say nothing about n.
7. **Clean the answer lists.** Every chosen document, spares included, was read against the written rules
   in `cleanup/COUNTING_RULES.md` and marked ok, fixed, dropped or left for you. `build.py` applies these
   decisions (`cleanup/decisions.jsonl`) after choosing, so a rebuild gives the same result. Spares refill
   the cells the drops emptied. Where they ran out, a second batch of spares was drawn after every other
   pick (`EXTRA_SPARES` in `build.py`, `spare_batch: 2`) and checked the same way.
8. **Trim to the final numbers.** After the authors' check, every over-full cell is trimmed to its final
   number, keeping the documents whose lengths best match the rest of their set (section 4).

## 4. Counts

Final numbers: clean documents (ok or fixed) in the study after the cleanup, the authors' check and trimming.
The full study uses the pilot documents too. Per-cell detail and the candidates each cell started with:
`cleanup/REPORT.md` (regenerated by every build).

| Set | checked | pilot n = 0/1/2 | pilot + full n = 0/1/2/3 | n = 4/5/6 | in study | clean spares | dropped |
|---|---|---|---|---|---|---|---|
| meetings | 109 | 10/10/10 | 15/15/15/15 | 6/3/1 | 70 | 22 | 17 |
| emails | 197 | 10/10/10 | 15/15/15/**11** | **5**/0/0 | 61 | 75 | 61 |
| receipts | 108 | - | -/15/15/15 | 4/3/3 | 55 | 48 | 5 |
| job_posts | 230 | - | 15/15/15/15 | 4/2/4 | 70 | 7 | 153 |
| clinical | 136 | - | 15/15/15/15 | 8/2/0 | 70 | 31 | 35 |
| reviews | 259 | - | -/15/15/15 | 4/3/3 | 55 | 19 | 185 |
| job_posts_knowledge | 159 | - | 15/15/15/**12** | - | 57 | 10 | 92 |
| wiki_people | 124 | - | 15/15/15/15 | - | 60 | 50 | 14 |
| novel_quotes | 124 | - | 15/15/15/15 | - | 60 | 49 | 15 |
| **all** | 1,446 | 60 | | | 558 | 311 | 577 |

- Targets: pilot 10 per n (meetings and emails, n = 0-2), 60 in all; full 15 per n for n = 0-3 (pilot counts
  towards it); 10 per set for n = 4-6, spread over n as evenly as the documents allow.
- **Trimming.** The cells were over-sampled so documents could be dropped without a rebuild. After the
  authors' check, `build.py` (`FINAL_TARGETS`) trims every over-full cell to its number. It keeps the
  documents whose lengths best match the spread of lengths across the whole set, so length says as little
  as possible about n. Pilot documents were kept only from documents that were already pilot (the ones the
  authors checked in full). Trimmed documents are clean, checked spares: `split: "reserve"`, with
  `cleanup.trimmed` saying where each came from. `FINAL_TARGETS = None` brings them all back.
- **Short:** emails n = 3 has 11 (needs 15) and job_posts_knowledge n = 3 has 12. Annotators often split one
  request or one tool into two, so true n = 3 documents are rarer than the labels said, and the second batch
  of spares held few. The emails 4-6 arm has 5 (10 wanted). job_posts n = 0, 2 and 3 and reviews n = 3 had
  exactly 15 and have no spares behind them. The bar was not lowered to fill these.
- Counts moved in both directions: meetings mostly up (the Project Manager's own jobs were missing), emails
  and reviews mostly down (one request counted twice, the product counted as its own feature). Several
  pilot meetings moved into the 4-6 arm.
- Does length give away n? Spearman correlation between words and n (n = 0-3, pilot + full), before and
  after trimming: meetings 0.10 -> 0.07, emails 0.31 -> 0.28, receipts 0.67 -> 0.54, job_posts -0.19 ->
  -0.21, clinical 0.09 -> 0.01, reviews 0.39 -> 0.22, job_posts_knowledge 0.05 -> 0.02, wiki_people 0.21 ->
  0.03, novel_quotes 0.04 -> 0.02 (`stats.json`). Pilot only: meetings 0.17 -> 0.07, emails 0.19 -> 0.09.
  Receipts stay high because a receipt with more items is longer; emails stay higher because the short n = 3
  cell could not be trimmed. Use document length as a covariate.

## 5. Files

| File | What it holds |
|---|---|
| `documents.jsonl` | one row per document: `doc_id`, `split` (pilot/full/reserve/dropped), `set`, `domain`, `list_type`, `item_type`, `source`, `source_id` (pointer back into the original data), `licence`, `words`, `n`, `text`, `gold_items` (text, start, end, evidence, `origin`: annotator or cleanup), `flags`, `meta`; after cleanup also `cleanup` (status, reason, rule, changes), `n_original`, `split_original`, `spare_batch`, and for fixed documents `gold_items_original` (the annotators' list) |
| `requests.jsonl` | one row per test prompt: `request_id`, `doc_id`, `condition`, `k`, `n`, `wording_id`, `instruction`, `schema_id`, `enforce_schema`, `in_pilot_run` |
| `requests_robustness.jsonl` | 1,440 extra prompts on the pilot documents, never part of the main grid: arm `block_llamaindex` (LlamaIndex's schema block, no 2-item example list) and arm `base_neutral` ("Extract the ... from this document.") |
| `requests_dev.jsonl` | 3,732 prompts on the 311 reserve documents (never in the study), for tuning the item matcher without looking at study outputs; the 14 Oct development runs used the 312 reserve documents of the time |
| `requests_fewer_ok.jsonl`, `reference_outputs_fewer_ok.jsonl` | Condition `min_k_shown_fewer_ok` (added 18 Oct, in the full scope): each min_k_shown prompt with one more line, "If the document contains fewer than {k}, list all available ones." (ScrapeGraphAI row 4580890 in `wordings.yaml`), 1,674 prompts and their answer lists; built by `build_fewer_ok.py` from the frozen files, which it leaves unchanged |
| `blind_check.py`, `blind/` | the blind check without answer lists (section 7): `blind_sheet.csv` to fill in, `blind_key.csv` (pilot or fresh) |
| `prompts.json` | the message template, the schema block, every JSON schema (by `schema_id`), the rule for each condition, the list definitions |
| `reference_outputs.jsonl` | the correct answer for each document x condition x k: `ideal_output` plus what is allowed (`any_k_of_gold`, `placeholders_ok`, `empty_ok`, `padding_slots`, `score_padding_type`) |
| `verify_sheet.csv` | the full check sheet (section 7), now with the cleanup status, change and reason per document; dropped documents left out |
| `cleanup/` | the cleanup: `README.md` (start here), `COUNTING_RULES.md`, `decisions.jsonl` (source of truth), and the generated `REPORT.md`, `changes.csv`, `review_sheet.csv` and `review_*.md` pages |
| `apply_cleanup.py` | applies `cleanup/decisions.jsonl` during the build and writes the cleanup outputs |
| `ai_precheck.jsonl` | the AI pre-check notes that fill the sheet's `ai_precheck` column |
| `restricted_ids.jsonl` | ids and text hashes of the review documents we cannot share; `build.py` rebuilds them into `local/` (not in git) |
| `wordings.yaml` | the real-world prompt wordings, with counts and sources (section 6) |
| `sources.yaml`, `stats.json` | source details; counts and length checks |
| `build.py`, `sources/`, `requirements.txt` | the code that rebuilds everything |
| `results_template/` | empty tables for the runs and the paper (section 8) |
| `evidence/` | schema prevalence numbers and real-world incidents for the introduction |

To get the exact text a model sees for one request:

```python
import json, build
prompts = json.load(open("prompts.json"))
docs = {d["doc_id"]: d for d in map(json.loads, open("documents.jsonl"))}
req = json.loads(next(open("requests.jsonl")))
print(build.render(req, docs[req["doc_id"]]["text"], prompts))
```

## 6. Test conditions and correct answers

Every prompt is: instruction, then the JSON schema pasted in the way LangChain's `JsonOutputParser` does it
(the library ScrapeGraphAI used for the real extraction calls in its dataset), then the document.

| Condition | What the model gets | Correct answer when n < k |
|---|---|---|
| `none` | "List all the ..." + schema without counts | the n true items; any extra is an error |
| `prose_up_to_k` | 5 real wordings, e.g. "Extract up to {k} ... from this document." | the n true items; stopping early is never an error |
| `prose_exactly_k` | 5 real wordings, e.g. "Extract exactly {k} ...", "Return the top {k} ..." | the n true items plus a flagged shortfall or clear placeholders; an invented item is an error |
| `max_k_shown` | schema with `maxItems: k`, shown in the prompt | the n true items |
| `min_k_shown` | schema with `minItems: k`, shown but not enforced | a short list, an empty list or placeholders; an invented item is an error |
| `min_k_enforced` | same schema, enforced by the engine (`enforce_schema: true`) | padding is forced: score what each padded slot is (placeholder, duplicate, invented) |
| `min_k_escape` | `minItems: k` enforced, plus "If the information is not available, use N/A." | the n true items plus N/A for the rest |

- The pilot run (`in_pilot_run: true`) is the plan's step 5: pilot documents, `min_k_shown` and `max_k_shown`,
  k = 3 and 5. That is 4 requests per document, 240 per model on the 60 pilot documents. The run plan
  (`../PLAN/RUN-PLAN.md` section 5.2) adds `none` (once per document) and `min_k_enforced` at k = 3 and 5:
  420 sends per model (`python harness/run.py plan --scope pilot`). The flag itself is unchanged.
- `render()` takes the schema block from `prompts.json` `schema_blocks` by the request's `schema_block_id`
  (main requests: `langchain_json_2025`, so their text is unchanged).
- Wordings: every instruction is copied from real prompts in ScrapeGraphAI-100k or from library docs; the only
  edit is "this page" -> "this document". `wordings.yaml` lists the real examples and row ids behind each one.
  All 5 wordings of each prose instruction are locked and reported (`../PLAN/RUN-PLAN.md`).

## 7. How to check the data (the two of you)

The cleanup pass (13 Oct 2026) checked every document against written counting rules, and both authors then
went through its review queue (`cleanup/README.md`: the open questions, every pilot document, and a sample of
fixes and drops) and agreed with every decision. Use the rules in `cleanup/COUNTING_RULES.md`; if you
overrule one later, change it there and in `cleanup/decisions.jsonl` for every document it touches, and
rebuild.

Still to do before the data is frozen: the blind check (at most 10% unclear). The review above is not
that check: it judged the cleanup's lists with the lists in view, and `verify_sheet.csv` shows them too.
The blind check uses a sheet with no answer lists:

1. `blind/blind_sheet.csv` holds 100 documents: the 60 pilot documents and 40 fresh ones from the full
   split (5 per set, spread over n; reviews left out because their text cannot be committed), shuffled,
   with no answer list and no count. Remake it with `python blind_check.py make`.
2. Each of you copies it (`blind_sheet_A.csv`, `blind_sheet_B.csv`) and works alone: the items you would
   list (one per line), the count, `y` if two careful readers could count differently, notes. Use
   `cleanup/COUNTING_RULES.md`. Do not open documents.jsonl, verify_sheet.csv or model outputs meanwhile.
3. `python blind_check.py agree blind/blind_sheet_A.csv blind/blind_sheet_B.csv`: count agreement with the
   answer lists and between you (exact share, kappa, weighted kappa, Gwet's AC1), unclear rate, for pilot
   and fresh documents apart, and `blind/adjudicate.csv` (the documents to settle, now with the lists).
4. Put settled changes into `cleanup/decisions.jsonl` and rebuild.
5. `python build.py kappa` (two copies of `verify_sheet.csv`) still works for a review-style check.

What the first AI pre-check found before the cleanup (an AI model read each pilot document and a 10% sample;
its notes are hints, not decisions). The cleanup readers did not see these notes; how the two compare is the
last table of `cleanup/REPORT.md`:

| Part | Read | ok | possible missing item | wrong item | ambiguous |
|---|---|---|---|---|---|
| pilot meetings | 51 | 35 | 7 | 0 | 9 |
| pilot emails | 53 | 33 | 4 | 5 | 11 |
| 10% sample of the full set | 80 | 53 | 16 | 3 | 8 |

- The 8 extra pilot emails with n = 2 were added after the pre-check and have no note yet.
- Almost all problems are at n = 2. At n = 0 the pre-check agreed with 28 of 30 pilot documents.
- Ambiguous counts are 18% (meetings) and 21% (emails) of pilot candidates on the AI's reading, above the
  plan's 10% limit. A shared grouping rule (below) should bring the human number down; if it does not, that is
  the plan's stop rule 3.
- Meetings: the main problem is how items are grouped. One annotator sentence sometimes covers three people's
  tasks, and the project manager's "I'll put the minutes in the folder" is sometimes counted and sometimes
  not. Agree on one grouping rule before you start.
- Emails: some gold items are statements, not requests ("we need to file this tomorrow"), and polite
  sign-offs ("let me know if you have questions") are a judgement call.
- Reviews are the weakest set: 4 of the 8 sampled miss an obvious feature. (The cleanup confirmed this: 185 of
  259 reviews were dropped.)

## 8. How results should be recorded and presented

`results_template/` has the empty tables, with the columns the paper needs:

| File | Fills |
|---|---|
| `raw_outputs.csv` | every response, never overwritten (plan step 6: model and engine versions, seed, raw text, errors) |
| `item_labels.csv` | one row per output item with its label and how it was matched |
| `per_output.csv` | one row per response: counts of each label, exact-k, invented yes/no |
| `table3_channels.csv` | Table 3: all conditions at matched k |
| `fig2_dose_response.csv` | Figure 2: invented-item rate against k - n |
| `table4_padding.csv` | Table 4: what the forced padding is |
| `table5_k_less_than_n.csv` | Table 5: which true items are dropped when k < n |
| `table6_item_type.csv` | Table 6: item type |

Model outputs are written by `../harness/run.py` as JSONL (`runs/<run_id>/raw.jsonl`; the review set in
`raw_restricted.jsonl`, never committed); `raw_outputs.csv` lists the same fields.

Two outcomes (`../PLAN/RUN-PLAN.md` section 5.1). Over-count, the main one, needs no matching: the output has
more substantive items (not placeholders, not repeats) than n (`../harness/score_counts.py`). Invented, the key
second one, comes from the item matcher: every item beyond the true ones is `true_item`, `in_text_wrong_type`
(real text of the document, but not an item of the asked kind), `missed_gold` (a true item the answer list
missed: fix the list and rescore), `beyond_excerpt` (not in this excerpt but in the full original source:
remembered, not invented), `plausible_invented` (in neither) or `ambiguous` (to a person). This replaces the
earlier single label `in_text_not_gold`.
Table 2 (design grid and counts) is section 4 above, after your drops.

## 9. Rebuild and verify

```
pip install -r requirements.txt
python build.py          # downloads about 300 MB once into ~/.cache/pad-to-k, rebuilds every file (about 1 minute)
python build.py check    # spans, duplicates, splits, count leaks, prompt coverage
```

Same pinned sources + same seed = byte-identical files (checked twice). After you freeze the data, hash it with
`../PLAN/tools/manifest.py` as the plan says.

## 10. Known issues

- AMI is one role-played scenario (a team designing a TV remote), one annotator per meeting, and its "no next
  steps" meetings are mostly final meetings. `meta.series_letter` records which meeting of the four it is.
- MailEx removed requests its annotators disputed, so some emails under-count; emails whose zero-request status
  looked doubtful were left out.
- SkillSpan's "skills" include job duties; text has anonymised placeholders like `<ORGANIZATION>`.
- MACCROBAT medication lists are clean in the sample; symptoms were not used (too often debatable).
- CORD: sub-items (e.g. "extra cheese") are not separate items; repeated lines count once.
- PDNC: the novel texts have non-ASCII characters removed, so some words read oddly ("I m going"); novels still
  in copyright outside the US were left out.
- Length still hints at n in receipts (0.54) and emails (0.28) after trimming (section 4): use it as a covariate.
- The cleanup is one AI model's reading under written rules, not a human label. Its biggest single calls
  (Project Manager jobs count, the product is not its own feature, advice is borderline) are listed in
  `cleanup/README.md` for you to confirm.
- Section I (copied schema examples and canaries) has no documents yet. It can reuse these documents; the
  canary design comes next.

## 11. Changes from the plan (for DECISIONS.md)

1. Main data is real annotated documents, not hand-written ones; your step 3 becomes "verify" instead of "write".
2. Pilot domains are meetings and emails (not invoices), because real receipts with zero items barely exist.
3. Receipts and reviews have no n = 0 cell.
4. "Vague theme" appears only through meetings; the item-type comparison is mainly quotes vs names.
5. New scoring label `in_text_not_gold`.
6. Prompt wordings are real-world ones, not invented ones.
7. Answer lists were cleaned under written counting rules (`cleanup/COUNTING_RULES.md`), with every change
   recorded next to the annotators' original (`cleanup/decisions.jsonl`, `cleanup/changes.csv`). The paper
   reports these counts (`cleanup/REPORT.md`).
8. A second batch of 336 spares was drawn for the cells the drops emptied (emails, job ads, reviews).

## 12. How the documents and answer lists were prepared

An AI agent (Kiro) found the datasets, wrote the loaders and `build.py`, chose the documents with a fixed seed,
collected the wordings and the evidence, and pre-checked documents. The pre-check notes are hints for the
human check, not labels.

The cleanup pass (13 Oct 2026) was also AI: Claude Opus 5.5 (`claude-opus-5.5`, through Kiro CLI), one lead
session and 14 reader sessions of the same model. It wrote the counting rules, checked all 1,446 documents,
and changed answer lists: it removed, split, merged and added items, and wrote the summary sentences of
added or split meeting action items (marked `origin: cleanup`). Every change keeps the annotators' original
next to it. These are proposals for the human check (`cleanup/README.md`).
