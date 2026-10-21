# Preregistration protocol, stage 1

Frozen 15 Oct 2026 at git tag `prereg-v1` (AbhishekBarali/pad-to-k), before the pilot ran, together with
`preregistration/manifest.sha256` (SHA-256 of every file under data/, configs/, harness/ and this folder).
Registered on OSF before the full runs; stage 2 (what changed after the pilot, and why) follows then.
Drafted from `PLAN/templates/PREREG-OUTLINE.md`; DECISIONS.md holds the reason for every choice.

## 1. Background and the gap

- PhantomFill (arXiv 2607.20492, v2, 27 Jul 2026), word for word from the v2 abstract: "The fabrication
  hides exactly where hedging is impossible: in required enums and minimum-count arrays, fields where no
  disclaimer fits."
- PhantomFill's inputs are synthetic and built so the asked-for fields cannot be answered, with answerable
  versions as controls (sections 1, 3.2 and 5). It compares free text, JSON asked for in the prompt and
  grammar-constrained JSON; it does not vary the true count against the asked-for count on real documents.
- arXiv 2607.01240 (v2): on 123 CoNLL-2014 passages the prompt states the true error count N, N+2 or
  max(1, N-2), in prose only. For four GPT and Claude models the reported count moves by 82-94% of the
  four-error gap, and a case shows GPT-4o inventing errors to reach N+2 (abstract, sections 3.2 and 4.7).
- arXiv 2407.06071 (v2): models asked for 25 facts where at most 10 exist, from memory; a list moves from
  correct facts to invented ones and then to repetitions (sections 3 and 6.1, appendix B.1).
- arXiv 2601.05201 (v2, ACL 2026): vision-language models told an image holds N+1 to N+5 objects
  increasingly go along with the prompt beyond four objects (section 3.2).
- StructHallu-Drift (ACL Anthology 2026.surgellm-1.22) leaves "cardinality hallucination" to future
  work (check the quote in the paper when you file).
- This study: real annotated documents with n = 0 to 6 true items, k = 1, 3, 5, the count stated in
  prose, in a schema shown in the prompt, or forced by the decoder.

## 2. Research questions and predictions

| RQ | Prediction | Null | Confirmatory? |
|---|---|---|---|
| RQ1 dose | Excess entries in minItems-shown rise from k = 3 to k = 5 (same document, n at most 2) | No rise | yes (contrast 1) |
| RQ2 channel | minItems shown gives more over-count than no count and than maxItems shown; prose "exactly k" more than "up to k" | No difference | yes (contrasts 2, 3, 4) |
| RQ2b escape | With N/A offered, fewer substantive entries fill the forced slots | No difference | yes (contrast 5) |
| RQ3 k < n | Models drop true items when asked for fewer (position = rank by first appearance in the text) | | no |
| RQ4 item type | Names vs quotes inside job ads (tools vs skills) | | no |
| RQ5 mechanism | Probability of closing the list after the last true item, against n | | no |
| RQ6 thinking | Thinking on vs off on the same weights | | no |
| RQ7 confidence | Extra entries carry lower token probability than real ones (teacher-forced pass, no grammar); AUROC per model, next to a position-only baseline | AUROC 0.5 | no |
| RQ8 hidden state | A linear probe reads "real" vs "extra" from the hidden state at the start of each entry better than a control task and a position-only baseline | No better than the baselines | no |

The confirmatory claims are about the 8 main models. Also preregistered, to speak to models in general:
the number of models whose own interval is above 0, the estimate with the 5 families weighted equally,
and leave-one-family-out.

### RQ7 and RQ8 in detail (exploratory; draft text for the registration)

Both are exploratory, labelled so before any result is seen, reported with 95% intervals and no test of
significance. Neither changes the main runs: both read outputs the main runs already produced.

**Entries.** Outputs in min_k_enforced and min_k_shown for documents with n < k, k = 3 and 5. Each entry that
is neither a placeholder nor a repeat gets a label from the matcher: "real" (a true item, a split of one, or a
true item the answer list missed) or "extra" (real text of the wrong kind, text from beyond the excerpt, or
found nowhere). In the pilot paper the labels come from the preliminary matcher, fitted on dev outputs only,
so the pilot numbers are preliminary. A matcher-free check: the sets whose items are names, where an exact
match decides the label.

**RQ7, confidence of extra entries.** The teacher-forced pass of the mechanism figure: each model's own
output, unchanged, is fed back after the same prompt without the grammar (vLLM `prompt_logprobs`, the same
server settings), so the probabilities are the model's own, not the mask's. For each entry, the mean
log-probability of its content tokens (inside the quotes). Score: minus that mean. Outcome: the AUROC for
"extra" against "real", per model, with an interval from 10,000 bootstrap draws over document groups.
Secondary: the first content token's log-probability, and the lowest one in the entry. Prediction: AUROC
above 0.5. Null: 0.5. Baseline, reported next to every RQ7 AUROC: the entry's position in the list alone
(later entries are more often extra), and the gain of the mean log-probability over position within the same
documents (a logistic regression of extra on both, by document group); a probability signal that position
explains is reported as such.

**RQ8, readable from the hidden state.** Hugging Face Transformers, BF16, the same model revision, and the
same prompt tokens as vLLM (checked equal). For each entry, the hidden state at the last token before its
first content token, the point where the model is about to write it, at every layer. A logistic-regression
probe (L2, strength chosen by cross-validation inside the training folds) for "real" against "extra"; five
folds split by document group; the layer is chosen inside the training folds too. Outcome: test AUROC with a
bootstrap interval over groups. Two baselines: a control task in the sense of Hewitt and Liang (2019), the
same probe on labels assigned at random to each first content token type (a type always gets the same label;
the share of "extra" kept), whose AUROC shows what the probe gets by memorising tokens; and a position-only
baseline, a logistic regression on the entry's index, k, and index divided by k. Prediction: the probe beats
both baselines. Qwen3.5-9B first; Gemma 4 31B if time allows. Worded as "readable from the hidden state",
never "the model knows".

## 3. Design

- Documents: 558 (`data/README.md`): 9 sets, n = 0 to 3 (15 per set and n; emails n = 3 has 11, job-ad
  tools n = 3 has 12) and a 4 to 6 group. Answer lists from the datasets' annotators, cleaned under
  `data/cleanup/COUNTING_RULES.md`, checked by both authors, plus the blind check (section 4).
- Conditions: none, prose_up_to_k, prose_exactly_k, max_k_shown, min_k_shown, min_k_enforced,
  min_k_escape (`data/prompts.json`). k = 1, 3, 5. All 5 wordings of each prose condition, all reported.
  Each list's schema carries a one-line definition (`data/prompts.json` lists); for five sets it states the
  counting rule since 15 Oct (DECISIONS.md).
- Robustness arms (pilot documents): `block_llamaindex`, `base_neutral`. A change of more than 10 points
  in either rule contrast is reported as prompt sensitivity.
- Models, engines, versions, reasoning-parser choice and the reason for each: `configs/models.yaml` at tag `prereg-v1`. Engine: vLLM v0.31.0, image digest sha256:c1c9f6fd5c109ba7f0546a59f5b2f15fb87f64c77782e90a27b648b42a8e67c3, xgrammar 0.2.7. Bedrock models run only
  the five prompt-side conditions. Together AI models are a dated reference, never pooled with the GPU
  results: Qwen3.5-9B (same-weights pair) and DeepSeek V4.1 Flash with thinking off in every condition; Kimi
  K3 with thinking off and GLM-5.3 with thinking on in the prompt-side conditions only (the count is not
  enforced for Kimi K3 there, and under a grammar Together drops GLM-5.3's reasoning). A forced condition
  counts only if the engine test shows the count is enforced there. Same-weights pairs: the paper says the serving stack does not drive
  the result if the pair's rule-1 contrast differs by less than 10 points.
- Decoding: greedy (temperature 0, top_p 1, seed 0), thinking off, except the thinking side test: two
  same-weights pairs (Qwen3.5-9B, Gemma 4 31B) run with each vendor's sampling and 3 request seeds, each pair
  differing only in the thinking switch, with room to finish thinking; gpt-oss-20b cannot stop reasoning and
  runs at low effort throughout. Batch-invariant mode on, except the models vLLM
  v0.31.0 cannot run with it on this GPU (Qwen3.5, Nemotron-H, gpt-oss).
- Repeat check: 300 prompts per model sent twice; identical share and over-count flip rate reported.

## 4. Data checks

- Blind check (`data/blind_check.py`), each author alone, without the answer lists. Round 1 (15 Oct, the
  earlier list definitions): 40 fresh never-reviewed documents, 5 per set except reviews; A matched the
  answer list's count on 29, B on 26, and A and B agreed on 33 (AC1 0.805). Most disagreements were counting
  rules the one-line definition did not state, so five definitions were extended and the 18 disputed
  documents settled (one list fixed, one document dropped) before this registration (DECISIONS.md, 15 Oct).
  Round 2: 25 fresh documents of the five changed sets (`data/blind/blind_sheet_round2_*.csv`), counted
  before the full runs and reported in stage 2. The 60 pilot documents and the 10 local review documents
  are not in the blind check.
- 577 of 1,446 candidate documents were dropped before any run, each for a recorded reason, mostly that it
  had no single right count (trimmed documents are clean spares, not drops); reasons in `data/cleanup/REPORT.md`
  and `data/cleanup/decisions.jsonl`.
- Freeze: documents, requests, prompts and reference outputs are hashed (`PLAN/tools/manifest.py`) and
  tagged `prereg-v1`; no rebuild after that. Reserve documents are locked (none can enter the study).
- Later corrections of an answer list go only into `analysis/gold_overlay.jsonl` (document, item, reason
  from the document alone, who, date), made without knowing which model or condition produced the entry.
  Headline numbers are reported with the frozen lists (primary) and with the overlay.

## 5. Scoring

- Parse ladder (strict JSON, fenced block, first object holding the list, bare list, truncated salvage,
  failed), recorded per output. A copy of the schema is never taken as the answer.
- Placeholders and string-level repeats as in `harness/common.py` at tag `prereg-v1`. An entry copied
  from the document is never a placeholder.
- Primary outcome: over-count, more substantive entries than the document's n
  (`harness/score_counts.py`). Also excess (number of extra entries). Unreadable outputs count as no
  over-count; also reported with them left out, and the invalid rate per model and condition.
- Placeholder bound: over-count is also reported with every substantive entry of 8 words or fewer that
  contains "no", "none", "not", "only", "other", "additional" or "found" treated as a note, an upper bound on
  what missed notes could change. An entry that repeats the prompt's instruction or the schema's
  description is a substantive entry (it counts toward over-count) and is reported as its own kind, never
  as invented.
- Key secondary outcome: invented (`plausible_invented`): an entry that is not a true item or a split
  of one, not real text of the document (`in_text_wrong_type`, which includes extras the schema
  description allows but the counting rules exclude), not a true item the list missed, and not in the
  wider source (`beyond_excerpt`: an exact match of at least 3 content words, every one checked by hand;
  available for meetings, emails, job ads, case reports and novels only). Matcher: RUN-PLAN 5.1.
  Thresholds fitted only on dev-set outputs (`--scope dev`), frozen and tagged `scorer-v1` before
  scoring study outputs; validated on 200 study entries labelled by both authors, blind to model and
  condition.
- No LLM judge for the headline numbers.

## 6. Analysis

- Documents with n < k, k = 3 and 5, unless stated.
- Confirmatory contrasts (Holm across the five):
  1. min_k_shown, k = 5 vs k = 3, same document, n at most 2; outcome excess.
  2. min_k_shown vs none; over-count.
  3. min_k_shown vs max_k_shown; over-count.
  4. prose_exactly_k vs prose_up_to_k, averaged over the 5 wordings; over-count.
  5. min_k_escape vs min_k_enforced; outcome substantive extra entries per padded slot.
- Intervals: 10,000 bootstrap draws over document groups (original meeting, email folder, job ad, case
  report, novel chapter), within each set.
- Test: per contrast, a mixed logistic regression on the two conditions only: outcome ~ condition + n +
  model + set + words + (1 | document), the no-count answer entered once per document and model. If it
  does not converge: drop words, then set; then the bootstrap interval is the test. (For excess, a
  Poisson mixed model with the same terms.)
- Every confirmatory result also without the pilot documents (the go decision used them).
- n = 0 analysed apart from n = 1 to 3. Everything else is exploratory.

## 7. Pilot stop rules

On over-count, pilot documents, n < k, k = 3 and 5, pooled over the 3 pilot models that ran, 95%
bootstrap interval (10,000 draws over document groups).

1. minItems shown minus no count; 2. minItems shown minus maxItems shown. For each: STOP or rethink if
   the upper end is under 10 points (this takes precedence); GO if the lower end is above 0; otherwise go
   only if at least 2 of the 3 models are above 5 points and none is below 0.
3. Blind check: on 40 documents under the final definitions (round 1's 15 documents of the three sets whose
   definitions did not change, plus round 2's 25), each author matches the answer list's count on at least
   85% and the authors' AC1 is at least 0.80; the share marked unclear by either author is reported. Round 1
   under the earlier definitions failed (72.5% and 65.0%, AC1 0.805), which led to the changes in section 4.
   Rule 3 is judged when round 2 is in, before the full runs and before anyone reads the full grid.

Behaviour of rules 1 and 2 by simulation (`harness/stop_rule_sim.py`, floor 15%): no true effect -> stop
0.75, go 0.05; 5 points -> stop 0.25; 10 points -> go 0.82; 15 points -> go 0.98. Stage 2 reruns it with
the pilot's floor rate.

Outcomes: all clear = full study. 1 or 2 stops with clear documents = a short bounding paper, or backup
topic B. 3 fails = fix the lists and rerun the pilot (after this registration the fixes go into the
overlay of section 4, and the pilot is rescored with it). Rule 1 also reported without the n = 0 emails.

## 8. Exclusions and changes

No document is excluded after this registration except through the blind check, with the reason
recorded. Outputs are never excluded; unreadable ones are counted. Every change goes in DECISIONS.md and
in the stage-2 registration.
