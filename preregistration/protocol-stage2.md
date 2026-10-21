# Preregistration protocol, stage 2: padding lists to a required count

Stage 2 of the registration, written after the pilot and before any full-run request is sent. It
replaces nothing from stage 1; it brings it up to date. Stage 1 is `preregistration/protocol.md`, frozen
on 15 Oct 2026 at git tag `prereg-v1` together with `preregistration/manifest.sha256` (SHA-256 of every
file under `data/`, `configs/`, `harness/` and `preregistration/`). This file is meant to be read on its
own: every rule that holds for the full study is written out here.

Every change from stage 1 is marked in the text as **[C1]**, **[C2]**, ... and listed in section 10,
"Changes after the pilot", with the reason and the stage-1 text it replaces. Text without a mark is
stage 1 unchanged. The reason for every choice is in `DECISIONS.md`.

- Registration: OSF Open-Ended Registration, filed before the first full-run request **[C19]**.
  This file is the document registered there; the registration date is the one OSF records.
- Authors: author A and author B.
- Repository state for this registration: tag `prereg-v2.1`, set when this file is uploaded, with
  `preregistration/manifest-stage2.sha256` (SHA-256 of every file under `data/`, `configs/`, `harness/`,
  `analysis/` and `preregistration/` at that tag). The model line-up, request files, prompts and
  scoring code at that tag are the registered ones.

## 1. Background and the gap

A JSON schema can ask for a list with at least k entries (`minItems: k`). When the document holds only
n < k true items, the model must either return a short list, flag the shortfall, or pad the list. This
study measures how often it pads, and with what.

- PhantomFill (arXiv 2607.20492, v2, 27 Jul 2026), word for word from the v2 abstract: "The fabrication
  hides exactly where hedging is impossible: in required enums and minimum-count arrays, fields where no
  disclaimer fits." Its inputs are synthetic and built so the asked-for fields cannot be answered, with
  answerable versions as controls (sections 1, 3.2 and 5). It compares free text, JSON asked for in the
  prompt and grammar-constrained JSON; it does not vary the true count against the asked-for count on
  real documents.
- arXiv 2607.01240 (v2): on 123 CoNLL-2014 passages the prompt states the true error count N, N+2 or
  max(1, N-2), in prose only. For four GPT and Claude models the reported count moves by 82-94% of the
  four-error gap, and a case shows GPT-4o inventing errors to reach N+2 (abstract, sections 3.2 and 4.7).
- arXiv 2407.06071 (v2): models asked for 25 facts where at most 10 exist, from memory; a list moves from
  correct facts to invented ones and then to repetitions (sections 3 and 6.1, appendix B.1).
- arXiv 2601.05201 (v2, ACL 2026): vision-language models told an image holds N+1 to N+5 objects
  increasingly go along with the prompt beyond four objects (section 3.2).
- StructHallu-Drift (ACL Anthology 2026.surgellm-1.22) leaves "cardinality hallucination" to future work.
- This study: real annotated documents with n = 0 to 6 true items, k = 1, 3, 5, the count stated in
  prose, in a schema shown in the prompt, or forced by the decoder, on open-weight models only **[C13]**.

**What the right answer is [C3].** The document sets the count. When it holds n < k true items, a correct
output lists the n true items and stops, or says the list is short (a clearly marked placeholder, "N/A"
where offered, or a note). Padding the list with entries that are not true items is the failure, whether
the padding is invented or real text of the wrong kind.

## 2. Research questions and predictions

The confirmatory claims are about the 8 main open-weight models run on the local GPU (section 3). Also
preregistered, to speak to models in general: the number of models whose own interval is above 0, the
estimate with the 5 families weighted equally, and leave-one-family-out. Per-model estimates are reported
first, the pooled estimate next to them **[C7]**.

| RQ | Prediction | Null | Status |
|---|---|---|---|
| RQ1 dose | Lists under minItems shown are longer at k = 5 than at k = 3 (same document, n at most 2) **[C1]** | No difference | confirmatory (contrast 1) |
| RQ2 channel | Lists under minItems shown are longer than with no count **[C1]** (the main measure) and than under maxItems shown; lists under prose "exactly k" are longer than under "up to k" | No difference | confirmatory (contrasts 2, 3, 4) |
| RQ2b escape | With N/A offered under an enforced minimum, fewer substantive entries fill the forced slots | No difference | confirmatory (contrast 5) |
| RQ2c fewer is fine **[C4]** | None stated. Lists under `min_k_shown_fewer_ok` longer than with no count means models pad even when told they may stop; no difference means the line removes the padding | No difference from no count | named test (section 6.3) |
| RQ2d enough items **[C5]** | On documents with at least k true items, a shown minimum changes list length much less than on documents with fewer | Same change as on n < k | named test (section 6.3) |
| RQ2e empty document, k = 1 **[C6]** | On documents with no true item, more outputs hold at least one substantive entry under a minimum of 1 than with no count | No difference | named test (section 6.3) |
| RQ3 k < n | Models drop true items when asked for fewer (position = rank by first appearance in the text) | | exploratory |
| RQ4 item type | Names vs quotes inside job ads (tools vs skills) | | exploratory |
| RQ5 mechanism | Probability of closing the list after the last true item, against n | | exploratory |
| RQ6 thinking | Thinking on vs off on the same weights | | exploratory |
| RQ7 confidence | Extra entries carry lower token probability than real ones (teacher-forced pass, no grammar); AUROC per model, next to a position-only baseline | AUROC 0.5 | exploratory |
| RQ8 hidden state | A linear probe reads "real" vs "extra" from the hidden state at the start of each entry better than a control task and a position-only baseline | No better than the baselines | exploratory |

### RQ7 and RQ8 in detail (exploratory, unchanged from stage 1)

Both are exploratory, labelled so before any result is seen, reported with 95% intervals and no test of
significance. Neither changes the main runs: both read outputs the main runs already produced.

**Entries.** Outputs in min_k_enforced and min_k_shown for documents with n < k, k = 3 and 5. Each entry
that is neither a placeholder nor a repeat gets a label from the matcher: "real" (a true item, a split of
one, or a true item the answer list missed) or "extra" (real text of the wrong kind, text from beyond the
excerpt, or found nowhere). A matcher-free check: the sets whose items are names, where an exact match
decides the label.

**RQ7, confidence of extra entries.** Each model's own output, unchanged, is fed back after the same
prompt without the grammar (vLLM `prompt_logprobs`, the same server settings), so the probabilities are
the model's own, not the mask's. For each entry, the mean log-probability of its content tokens (inside
the quotes). Score: minus that mean. Outcome: the AUROC for "extra" against "real", per model, with an
interval from 10,000 bootstrap draws over document groups. Secondary: the first content token's
log-probability, and the lowest one in the entry. Prediction: AUROC above 0.5. Null: 0.5. Baseline,
reported next to every RQ7 AUROC: the entry's position in the list alone, and the gain of the mean
log-probability over position within the same documents (a logistic regression of extra on both, by
document group); a probability signal that position explains is reported as such.

**RQ8, readable from the hidden state.** Hugging Face Transformers, BF16, the same model revision, and the
same prompt tokens as vLLM (checked equal). For each entry, the hidden state at the last token before its
first content token, at every layer. A logistic-regression probe (L2, strength chosen by cross-validation
inside the training folds) for "real" against "extra"; five folds split by document group; the layer is
chosen inside the training folds too. Outcome: test AUROC with a bootstrap interval over groups. Two
baselines: a control task in the sense of Hewitt and Liang (2019), the same probe on labels assigned at
random to each first content token type (a type always gets the same label; the share of "extra" kept);
and a position-only baseline, a logistic regression on the entry's index, k, and index divided by k.
Prediction: the probe beats both baselines. Qwen3.5-9B first; Gemma 4 31B if time allows. Worded as
"readable from the hidden state", never "the model knows".

## 3. Design

### 3.1 Documents

558 documents (`data/README.md`) from 9 sets drawn from 8 published datasets: meetings (AMI action
items), emails (MailEx requests), receipts (CORD items, Indonesian receipts), job-ad skills and job-ad
knowledge (both SkillSpan), clinical case reports (MACCROBAT medications), product reviews (ROAST
features; text not redistributable, rebuilt locally), Wikipedia people (Few-NERD) and novel quotations
(PDNC; the novel texts lost their non-ASCII characters). Cells: n = 0 to 3, 15 documents per set and n
(emails n = 3 has 11, job-ad knowledge n = 3 has 12; receipts and reviews have no n = 0), and a 4 to 6
group for k < n (emails has 5). 60 of them are the pilot documents (meetings and emails, n = 0 to 2, 10
per cell).

Answer lists come from the datasets' annotators, cleaned under `data/cleanup/COUNTING_RULES.md`, checked
by both authors, then blind-checked (section 4). How the cleanup pass was done: the counting rules (`data/cleanup/COUNTING_RULES.md`) were confirmed by
both authors on 13 Oct 2026, including the five calls that move the most documents. Under author A's
direction, an AI assistant, Claude Opus 5.5 (`claude-opus-5.5`), applied those rules to all 1,446
candidate answer lists. For each list it drafted a fix, a drop or no change, and it kept the annotators'
original next to every change (`data/cleanup/decisions.jsonl`, `data/cleanup/changes.csv`). Every case the
rules did not settle went to the authors. Author B checked every document's answer list by hand. Both authors went
through the review queue (every pilot document, the open questions and a sample of fixes and drops) and
settled the open questions. The final lists then passed a blind check in which both authors counted
fresh documents without seeing the lists (section 4). The matcher's 544 development labels
(`analysis/dev/matcher_labels_dev.jsonl`) were drafted by the same assistant, so in the full study the
matcher is checked only against labels made by the authors (section 5, C10). The full record is in
`AI-USE.md` **[C21]**.
That statement is also the reason no Claude model is in the study (section 3.3).

### 3.2 Conditions

All prompts are an instruction, then the JSON schema pasted the way LangChain's `JsonOutputParser` does it,
then the document. Exact text: `data/prompts.json`; every request: `data/requests.jsonl`.

| Condition | What the model gets | Grammar |
|---|---|---|
| `none` | "List all the ..." and a schema with no count | no |
| `prose_up_to_k` | 5 real wordings, e.g. "Extract up to {k} ..." | no |
| `prose_exactly_k` | 5 real wordings, e.g. "Extract exactly {k} ...", "Return the top {k} ..." | no |
| `max_k_shown` | schema with `maxItems: k`, shown in the prompt | no |
| `min_k_shown` | schema with `minItems: k`, shown in the prompt | no |
| `min_k_shown_fewer_ok` **[C4]** | `min_k_shown` plus one line saying a shorter list is fine (wording and requests in `data/build_fewer_ok.py` and `data/requests_fewer_ok.jsonl`, 1,674 requests) | no |
| `min_k_enforced` | the `min_k_shown` schema, enforced by the decoder | yes |
| `min_k_escape` | `minItems: k` enforced, plus "If the information is not available, use N/A." | yes |

k = 1, 3, 5. All 5 wordings of each prose condition run, and all are reported. Each list's schema
carries a one-line definition of the item; for five sets it states the counting rule (since 15 Oct).
The "prompt-side" conditions are the six without a grammar.

Request counts per model, from `data/requests.jsonl` at stage 1 (the `none` prompt is the same at every
k and is counted once per k here): 25,110 requests in all; 9,900 on documents with at least k true items;
1,575 at k = 1 on the 105 documents with no true item **[C5, C6]**. The new condition adds its own rows
(1,674 if built at every k on every document, like `min_k_shown`); the request file at tag `prereg-v2.1`
is the registered count.

Robustness arms on the pilot documents: `block_llamaindex` (LlamaIndex's schema block) and
`base_neutral` ("Extract the ... from this document."). A change of more than 10 points in either pilot
rule contrast is reported as prompt sensitivity.

### 3.3 Models

Only open-weight models run. The title and every claim say "open-weight models" **[C13]**. No closed
model is run. Claude models are excluded for the reason given in the cleanup statement (section 3.1).
Models, engines, revisions, reasoning-parser choice and the reason for each: `configs/models.yaml` at tag
`prereg-v2.1`. The cost test (50 pilot requests per Bedrock model, 18 Oct) dropped no model; projected cost
and the cap on every hosted run are in `analysis/full_study_estimate.md` **[C14]**.

- **Local GPU, the main result (unchanged).** 8 main models: Qwen3.5 0.8B, 2B, 9B and 27B, Gemma 4 31B,
  Olmo 3.1 32B, Ministral 3 14B, gpt-oss-20b; every condition. One NVIDIA RTX PRO 6000; vLLM v0.31.0,
  image digest sha256:c1c9f6fd5c109ba7f0546a59f5b2f15fb87f64c77782e90a27b648b42a8e67c3, XGrammar 0.2.7.
  A forced condition counts only if the engine test shows the count is enforced there.
- **Together AI (dated reference, never pooled with the GPU results).** DeepSeek V4.1 Flash (thinking off)
  and Qwen3.5-9B (the same weights as the local model), every condition **[C14]**.
- **Amazon Bedrock (dated reference, never pooled).** Kimi K3 with thinking off, DeepSeek V3.2, Qwen3-235B,
  Mistral Large 3 and gpt-oss-120b, plus the same-weights pairs Ministral 3 14B and gpt-oss-20b; the
  prompt-side conditions only (Bedrock cannot enforce a minimum above 1) **[C14]**.
- **Kimi K3 with thinking on.** The prompt-side conditions on the pilot documents only: on every
  document it would cost about 338 USD on its own, past the budget **[C14]**.
- GLM-5.3 with thinking on ran in the pilot and is not in the full run **[C14]**.
- Same-weights pairs: the paper says the serving stack does not drive the result if the pair's main
  contrast differs by less than 10 points.

### 3.4 Decoding and side tests

- Greedy decoding (temperature 0, top_p 1, seed 0), thinking off, batch-invariant mode on except where
  vLLM v0.31.0 cannot run it on this GPU (Qwen3.5, Nemotron-H, gpt-oss). In the pilot, batch-invariant
  mode did not make outputs repeatable: on a newly started server 40% of Ministral 3 14B's and 11% of
  Gemma 4 31B's repeated replies differed in their text, while the over-count verdict flipped for 0.7% to
  1.0% of repeated GPU prompts. The repeat check is the reported measure **[C22]**.
- No system prompt is sent, but two chat templates add one of their own (Olmo 3.1 a default system prompt,
  gpt-oss a system message with the current date); the prompt each
  model really receives is saved by the engine test (`rendered_prompt.txt`). With free whitespace off,
  XGrammar still writes one space after ":" and "," **[C22]**.
- Thinking side test: two same-weights pairs run with each vendor's sampling, each pair differing only in
  the thinking switch: Qwen3.5-9B (temperature 1.0, top_p 0.95, top_k 20, presence penalty 1.5; 3
  request seeds) and Gemma 4 31B (temperature 1.0, top_p 0.95, top_k 64; one seed in the pilot). gpt-oss-20b cannot stop
  reasoning and runs at low effort throughout. Gemma 4 31B pair in the full run: all documents,
  one request seed, the same conditions as the Qwen3.5-9B pair, so a second family is tested on every set.
- Extra thinking run: Qwen3.5-9B thinking on and off with presence penalty 0, all else as above, on the
  60 pilot documents, because a presence penalty also acts on the thinking text and the pilot's thinking
  result came from those documents **[C15]**.
- Re-ask arm (exploratory): when a `min_k_shown` reply has fewer than k items, it is sent back once with
  the validation error, the way Instructor-style retry libraries do (`harness/retry_arm.py`). It runs on
  Qwen3.5-9B, Gemma 4 31B, Ministral 3 14B, Bedrock Kimi K3 and Bedrock Ministral 3 14B; the re-asks depend
  on the first replies, so their record is each `-reask1` run's planned file, not `data/requests.jsonl`
  **[C15]**.
- Repeat check: 300 prompts per model sent twice; identical share and over-count flip rate reported.

## 4. Data checks

### 4.1 Blind check [C8]

Each author alone counted documents without the answer lists (`data/blind_check.py`).

- Round 1 (15 Oct, the earlier definitions): 40 fresh, never-reviewed documents. Author A matched the
  answer list's count on 29 (72.5%), author B on 26 (65.0%), and they agreed with each other on 33 (AC1
  0.805). Rule 3 failed and stays reported as failed. Most disagreements were counting rules the one-line
  definition did not state, so five definitions were extended and the 18 disputed documents settled (one
  list fixed, one document dropped) before tag `prereg-v1`.
- Round 2 (filled 18 Oct): 25 fresh documents of the five changed sets. Rule 3 was judged as registered,
  on 40 documents under the final definitions (round 1's 15 of novel quotes, receipts and Wikipedia
  people, plus round 2's 25): author A matched on 35 (87.5%), author B on 38 (95.0%), A and B agreed on
  35 (AC1 0.851). Rule 3 passes. 15 of 40 were marked unclear by either author (reported, not tested).
  `python analysis/blind_rule3.py`.
- Per set (5 documents each; A matches, B matches, A = B): clinical 5, 5, 5; emails 5, 5, 5; job-ad
  knowledge 5, 5, 5; novel quotes, receipts and Wikipedia people 5, 5, 5 each; meetings 3, 5, 3; job-ad
  skills 2, 3, 2. Job-ad skills is the least certain answer list (whether a personal trait counts, and
  whether "precise and focused" is one item or two). Results are reported per set, and the paper names
  it as the weakest set. No answer list was changed after round 2.
- On round 2 alone (not the registered test) the authors matched 80% and 92%, AC1 0.762. Both authors had
  studied the counting rules by then, so the check measures agreement with the written rules, not with
  untrained readers.
- The 60 pilot documents and the review documents are not in the blind check. Both authors read the
  pilot documents with their lists during the cleanup review.

### 4.2 The answer lists against the source datasets' own counts [C9]

`python analysis/answer_key_vs_source.py` (output `analysis/answer_key/REPORT.md` and
`analysis/answer_key/differing_documents.csv`). On the 558 study documents, the cleaned count equals the
annotators' count on 423 (76%). Where they differ, it is by one item on 121 documents, two on 12, three
on 2.

| Set | documents | same count | cleaned higher | cleaned lower |
|---|---|---|---|---|
| meetings | 70 | 44 (63%) | 22 | 4 |
| emails | 61 | 39 (64%) | 4 | 18 |
| receipts | 55 | 55 (100%) | 0 | 0 |
| job-ad skills | 70 | 55 (79%) | 15 | 0 |
| clinical | 70 | 55 (79%) | 1 | 14 |
| reviews | 55 | 21 (38%) | 9 | 25 |
| job-ad knowledge | 57 | 46 (81%) | 5 | 6 |
| Wikipedia people | 60 | 49 (82%) | 3 | 8 |
| novel quotes | 60 | 59 (98%) | 0 | 1 |

On the pilot documents: meetings 21 of 30 the same (7 higher, 2 lower), emails 19 of 30 (1 higher, 10
lower). On the 15 blind-check documents where the two counts differ, author A's blind count matched the
cleaned count on 10 and the annotators' count on 1; author B's on 9 and 1. That says the cleaned lists
follow the written rules the authors also used; it does not say the rules are the only reasonable ones.

Because of this, every headline number is also reported with the annotators' original counts in place
of the cleaned ones (only where the measure needs a count), and split by documents whose list the cleanup
kept or changed.

### 4.3 Drops, freeze and corrections (unchanged)

- 577 of 1,446 candidate documents were dropped before any run, each for a recorded reason, mostly that
  it had no single right count; reasons in `data/cleanup/REPORT.md` and `data/cleanup/decisions.jsonl`.
- Documents, requests, prompts and reference outputs are hashed and tagged `prereg-v1`; no rebuild after
  that except the rows the new condition adds; those must leave every stage-1 request unchanged, which is
  checked by hash before tag `prereg-v2.1`. Reserve documents are locked.
- Later corrections of an answer list go only into `analysis/gold_overlay.jsonl` (document, item, reason
  from the document alone, who, date), made without knowing which model or condition produced the entry.
  Headline numbers are reported with the frozen lists (primary) and with the overlay.

## 5. Scoring

### 5.1 Reading an output (unchanged)

- Parse ladder: strict JSON, fenced block, first object holding the list, bare list, truncated salvage,
  failed; recorded per output. A copy of the schema is never taken as the answer. When an output holds
  two different lists under the field, the first is the answer.
- Placeholders and string-level repeats as in `harness/common.py` at tag `prereg-v1`. An entry copied from
  the document is never a placeholder. An entry that repeats the prompt's instruction or the schema's
  description is a substantive entry and is reported as its own kind, never as invented.
- Substantive entries: every entry that is neither a placeholder nor a repeat.

### 5.2 Outcomes

- **Main measure: list length change [C1].** For one document and one model, the number of substantive
  entries under a condition minus the number under the comparison condition (for the main contrast,
  `min_k_shown` against `none`). It needs no answer list: only the entries are counted. The answer list
  is used only to choose the cells (n < k).
- **Over-count (secondary, was primary) [C1].** More substantive entries than n (`harness/score_counts.py`).
  Also excess (number of entries beyond n). Reported for every condition, so the pilot's numbers stay
  comparable.
- **True items left out [C2].** Per output, the number of the document's true items no entry matches (the
  matcher's true-item and split labels); reported as the share of true items left out, per condition and
  model. Also the share of outputs with exactly n entries, and the length distribution (fewer than k,
  exactly k, more than k).
- **Sorting every output [C3].** On documents with n < k, each output is one of: padded (more substantive
  entries than n; this wins if the output also flags the shortfall); says it is short (not padded, and it
  holds a placeholder, an "N/A" or a note saying fewer items exist, by the note rules of
  `harness/common.py` applied to the list and to any text outside it, frozen with the scorer); an honest
  short list (not padded, no such mark); unreadable (the parse ladder failed, or the reply was cut off
  before a list). Unreadable outputs are their own category here; in over-count they still count as no
  over-count, with the rate reported per model and condition.
- **Placeholder bound (unchanged).** Over-count is also reported with every substantive entry of 8 words
  or fewer that contains "no", "none", "not", "only", "other", "additional" or "found" treated as a note.
- **Invented (key secondary).** Each entry beyond the true ones gets a matcher label: a true item or a
  split of one; real text of the document of the wrong kind (`in_text_wrong_type`); a true item the list
  missed (`missed_gold`); text from the wider source but not this excerpt (`beyond_excerpt`: an exact
  match of at least 3 content words, every one checked by hand; meetings, emails, job ads, case reports
  and novels only); or none of these (`plausible_invented`). Names match after normalising case and
  punctuation; quotes by fuzzy substring search against the document; meeting jobs by role-normalised
  similarity to each answer item and its transcript lines. Thresholds are fitted on development outputs
  only (reserve documents), frozen and tagged `scorer-v1` before study outputs are scored. The development
  runs of 14 Oct used the earlier definitions; that is reported. The matcher is validated as in 5.3.
- The pilot's "at most 4% invented" figure is not carried into the full study. An invented share is
  stated only with the matcher error rate from the authors' labels (5.3), and "at most" only if those
  labels support an upper bound **[C11]**.
- No LLM judge for the headline numbers.

### 5.3 Checks by the authors [C10, C12]

Three checks, all done before the results they check are read. Every draw uses seed 20261013 and is made
by a script committed before the draw; the drawn ids are committed before labelling starts.

**(a) Scoring check on 40 pilot outputs, before the full run.** 40 outputs drawn at random from the main
pilot runs (every pilot model, local and hosted, every pilot condition), plus every forced output cut at
the token limit and every unreadable output of those runs (3 and 4 in the local pilot). One author reads
each against `harness/score_counts.py`: parse rung, substantive entries, placeholders, repeats,
over-count. Every disagreement is listed with its cause. A scorer bug found here is fixed before
`scorer-v1`, logged in `DECISIONS.md`, and the pilot is rescored with the fix and reported both ways. The
record names which outputs were read.

**(b) Matcher labels on about 400 entries, after the full run.** The sample comes from the scored study
outputs, because seven of the nine sets are not in the pilot.

- Frame: every substantive entry of every study output, all models and conditions, `none` included, with
  its `scorer-v1` matcher label.
- Strata: the five matcher labels (true item or split, `in_text_wrong_type`, `missed_gold`,
  `beyond_excerpt`, `plausible_invented`). 80 entries per label, 400 in all. A label with fewer than 80
  entries in the frame gives all of them, and its unused places go in equal parts to the other labels.
  So the rare unmatched labels get as many examples as the common ones, not a share in proportion to
  their size.
- Within a label: at most one entry per output, spread as evenly over the nine sets as the label allows,
  then at random.
- What a labeller sees: the document, the list definition, the answer list and the one entry. Not the
  model, the condition, k, the other entries of the output, or the matcher's label.
- Both authors label every entry alone, with the matcher's labels plus "unsure", then settle the
  differences together; the settled label is the reference. Their agreement (exact share, kappa, AC1) is
  reported.
- Results: per label, the share of the matcher's calls the authors confirm (precision) and, weighting each
  stratum back to its size in the frame, the share of the authors' labels the matcher finds (recall),
  with 95% intervals from 10,000 bootstrap draws over document groups. The invented share is reported as
  the matcher gives it and corrected with these weights. Entries labelled `missed_gold` go to the overlay
  (4.3).

**(c) Hand recount on 10 documents, after scoring.** 10 study documents drawn at random from the n < k
cells, at most two per set. Each is paired with one main model in turn (two models get a second
document). For that document and model, one author counts the substantive entries by hand from the raw
outputs of `none`, `min_k_shown`, `max_k_shown` and `min_k_shown_fewer_ok` at k = 3 and 5 (7 outputs, 70
in all), and computes length change, over-count, true items left out and the sorting of 5.2. Every
number is compared with the scorer's per-output table; a difference is traced to its cause before any
headline is read.

## 6. Analysis

### 6.1 Scope and intervals

- Documents with n < k, k = 3 and 5, unless stated. n = 0 is analysed apart from n = 1 to 3 (the n = 0
  emails hold no request cues; the n = 0 meetings are mostly final meetings of a series).
- Intervals: 10,000 bootstrap draws over document groups (original meeting, email folder, job ad, case
  report, novel chapter), within each set.
- Every result is reported per model and per set. Every confirmatory result is also reported without
  the pilot documents (the go decision used them).

### 6.2 Confirmatory contrasts (Holm across the five)

1. Dose: `min_k_shown`, k = 5 against k = 3, same document, n at most 2. Outcome: length change **[C1]**
   (stage 1: excess).
2. `min_k_shown` against `none`. Outcome: length change, the main measure **[C1]** (stage 1:
   over-count).
3. `min_k_shown` against `max_k_shown`. Outcome: length change **[C1]**.
4. `prose_exactly_k` against `prose_up_to_k`, averaged over the 5 wordings. Outcome: length change
   **[C1]**.
5. Escape: `min_k_escape` against `min_k_enforced`. Outcome: substantive extra entries per padded slot
   (unchanged).

Test **[C7]**: for each contrast the one primary test is the 95% bootstrap interval of the mean paired
difference over documents and the 8 main models (document groups resampled within set), with a two-sided
bootstrap p-value for the Holm step. Next to it: the mixed model of stage 1 on the same pairs (a linear
mixed model of the paired difference for length, ~ n + model + set + words + (1 | document); for
contrast 5 a Poisson mixed model; if it does not converge, drop words, then set) and the per-model
estimates with their own intervals. Over-count is reported for contrasts 1 to 4 as in stage 1.

### 6.3 Named tests, reported whatever the result (outside the Holm family)

- **Fewer is fine [C4].** `min_k_shown_fewer_ok` against `none` (length change) and against
  `min_k_shown`, documents with n < k, k = 3 and 5. Also over-count and the sorting of 5.2.
- **Enough items [C5].** Documents with at least k true items (9,900 stage-1 requests per model).
  `min_k_shown` against `none`, length change and true items left out. The difference between this change
  and the change on n < k documents (same models, same k) is reported as the part of the effect that
  comes from filling missing slots.
- **Empty document, k = 1 [C6].** The 105 documents with no true item, k = 1 (1,575 stage-1 requests per
  model). Outcome: the share of outputs with at least one substantive entry, in every condition against
  `none`.
- **maxItems.** `max_k_shown` against `none`, length change with its interval. No equivalence margin is
  registered; the paper calls maxItems harmless only if the interval sits close to 0 and says how close.

### 6.4 Exploratory (everything else)

RQ3 to RQ8 (section 2); the robustness arms; the same-weights pairs; the hosted models (a dated
reference, never pooled with the GPU results); the thinking side test and its presence-penalty-0 rerun;
the re-ask arm; per-set and per-wording results; the generality summary of section 2.

Thinking text: whether a thinking trace notices the shortfall is reported only as a phrase search, named
as unchecked by hand **[C16]**.

### 6.5 Every test, in one list

| Test | Status | Section |
|---|---|---|
| Contrast 1, dose (min_k_shown k = 5 vs 3) | confirmatory | 6.2 |
| Contrast 2, min_k_shown vs none (main measure) | confirmatory | 6.2 |
| Contrast 3, min_k_shown vs max_k_shown | confirmatory | 6.2 |
| Contrast 4, prose exactly k vs up to k | confirmatory | 6.2 |
| Contrast 5, min_k_escape (N/A escape) vs min_k_enforced | confirmatory | 6.2 |
| min_k_shown_fewer_ok vs none and vs min_k_shown | named | 6.3 |
| n at least k documents | named | 6.3 |
| k = 1 on n = 0 documents | named | 6.3 |
| max_k_shown vs none | named | 6.3 |
| What fills enforced slots (min_k_enforced, min_k_escape) | exploratory | 5.2 |
| RQ3 k < n, RQ4 item type, RQ5 closing probability, RQ6 thinking, RQ7, RQ8 | exploratory | 2 |
| Robustness arms (block_llamaindex, base_neutral) | exploratory | 3.2 |
| Same-weights pairs (Together, Bedrock) | exploratory | 3.3 |
| Hosted models | exploratory | 3.3 |
| Thinking side test, presence penalty 0 rerun, Kimi K3 thinking on | exploratory | 3.4 |
| Re-ask arm | exploratory | 3.4 |
| Repeat check | reported | 3.4 |
| Placeholder bound | reported | 5.2 |
| Without the pilot documents; with the overlay; with the annotators' counts | reported | 4.2, 4.3, 6.1 |
| Generality summary (models above 0, family-weighted, leave-one-family-out) | reported | 2 |

## 7. Pilot stop rules (done)

On over-count, pilot documents, n < k, k = 3 and 5, pooled over the 3 local pilot models, 95% bootstrap
interval (10,000 draws over document groups). STOP or rethink if the upper end is under 10 points (this
takes precedence); GO if the lower end is above 0; otherwise go only if at least 2 of the 3 models are
above 5 points and none is below 0. Rule 3: on the 40 blind-check documents of 4.1, each author matches
the answer list's count on at least 85% and the authors' AC1 is at least 0.80.

| Rule | Result | Verdict |
|---|---|---|
| 1. minItems shown minus no count | +34.4 points [28.1, 40.8] (Qwen3.5-9B 30.0, Ministral 3 14B 13.3, Gemma 4 31B 60.0) | GO |
| 2. minItems shown minus maxItems shown | +34.2 points [28.3, 40.3] | GO |
| 3. blind check, round 1 (earlier definitions) | A 72.5%, B 65.0%, AC1 0.805 | failed |
| 3. blind check as registered (round 1's three unchanged sets + round 2) | A 87.5%, B 95.0%, AC1 0.851 | PASS |

The pilot ran on 15 Oct (15:37 to 19:35 UTC) before rule 3 was judged, as stage 1 allowed: rule 3 was to
be judged before the full runs and before anyone read the full grid. Result source: the pilot report on
branch `pilot-runs` and `analysis/blind_rule3.py`.

Stop-rule simulation rerun with the pilot's floor rates **[C18]** (`harness/stop_rule_sim.py --base`,
seed 20261014, 600 simulations; stop / go per true gap):

| Floor | 0 points | 5 points | 10 points | 15 points |
|---|---|---|---|---|
| 15% (stage 1) | 0.75 / 0.05 | 0.25 / 0.37 | 0.03 / 0.82 | 0.00 / 0.98 |
| 22% (Gemma 4 31B) | 0.71 / 0.06 | 0.22 / 0.35 | 0.03 / 0.78 | 0.00 / 0.97 |
| 43% (Qwen3.5-9B) | 0.68 / 0.04 | 0.22 / 0.26 | 0.04 / 0.67 | 0.00 / 0.95 |
| 78% (Ministral 3 14B) | 0.80 / 0.02 | 0.38 / 0.22 | 0.05 / 0.75 | 0.01 / 0.97 |

## 8. Limits named in advance [C17]

These are not tested and the paper names each one as a limit:

- Every list item is one copied string. Lists of records with several fields (task, owner, date), where
  padding would force invented field values, are not run.
- One grammar engine (XGrammar). A second engine (llguidance) was tried only in the engine test, where
  its outputs differed.
- The schema is always pasted in the prompt; a schema sent only through the API is not run.
- Thinking traces are not hand-checked.
- No closed model; the results speak to open-weight models.

## 9. Exclusions, changes and timeline

No document is excluded after this registration except through the overlay of 4.3, with the reason
recorded. Outputs are never excluded; unreadable ones are counted. Every change after this registration
goes in `DECISIONS.md` and in the paper's deviations table.

Timeline (UTC, from the repository's commit times; these are set by the authors' own machines and are not
independent proof, which is why the plan is registered on OSF before the full run) **[C19]**:

| When | What |
|---|---|
| 13 Oct 2026 | Data built, answer lists cleaned under written rules, checked by both authors |
| 15 Oct, 14:04 | Blind check round 1 result (rule 3 fails under the earlier definitions) |
| 15 Oct, 14:59 | Five definitions extended, two settled documents changed, data rebuilt, round-2 sheets made |
| 15 Oct, 15:35 | Stage 1 frozen at tag `prereg-v1` |
| 15 Oct, 15:37 to 19:35 | Pilot runs |
| 16 Oct | Pilot paper written from the pilot runs |
| 17 Oct | The authors' review of the pilot paper |
| 18 Oct, 03:20 | Blind check round 2 result (rule 3 passes) |
| 18 Oct | This stage-2 protocol written |
| OSF submission date | Registered on OSF; tag `prereg-v2.1` |

## 10. Changes after the pilot

| # | What changed | Why | Stage-1 text it replaces |
|---|---|---|---|
| C1 | The main measure is the length change on the same document: entries under a shown minimum minus entries with no count. Contrasts 1 to 4 use length; over-count becomes secondary | It needs no answer list, and the answer list is the study's weakest part; a yes/no over-count also hid that a stated number pulls lists toward k | Sec. 5: "Primary outcome: over-count"; sec. 6 contrasts 1 to 4 outcomes (excess, over-count) |
| C2 | True items left out, exact-n share and the length distribution are reported | A list that drops true items could look like success | New |
| C3 | The right answer is stated, and every output is sorted as padded, says it is short, honest short list, or unreadable | Answers "it just followed the instruction"; unreadable outputs need their own category | Sec. 5: "Unreadable outputs count as no over-count" (kept for over-count only) |
| C4 | New condition `min_k_shown_fewer_ok`, with a named test | Tests whether models pad even when told they may stop | Sec. 3 conditions list |
| C5 | Named test on documents with at least k true items (9,900 requests per model) | A control where the minimum asks for nothing missing; shows how much of the effect is slot filling | Sec. 6: "Documents with n < k ... unless stated" (no named result) |
| C6 | Named test at k = 1 on documents with no true item (1,575 requests per model) | The most common real minimum; already in the design but with no named result | Sec. 6 (no named result) |
| C7 | One primary test per contrast (bootstrap interval of the paired difference); the mixed model and per-model estimates next to it; per-model results first | The pilot's model effects differ widely (13, 30, 60 points); a model with model as a plain fixed effect fits them poorly | Sec. 6: "Test: per contrast, a mixed logistic regression ..." |
| C8 | Round 2 result written in; rule 3 passes as registered; round 1 stays reported as failed; results per set; job-ad skills named the least certain list | Round 2 was due in stage 2; pooling hides weak sets | Sec. 4: "Round 2 ... reported in stage 2"; sec. 7 rule 3 |
| C9 | Cleaned answer lists compared with the annotators' counts; headline numbers also with the annotators' counts and split by kept or changed lists | Shows how far the cleanup moved the key, in which direction, per set | New |
| C10 | Matcher validated on about 400 entries, stratified by matcher label, both authors, blind; precision and recall both ways | 200 random entries would hold too few invented ones to measure the matcher where it matters | Sec. 5: "validated on 200 study entries labelled by both authors" |
| C11 | The pilot's "at most 4% invented" is not carried over; an invented share is stated only with the authors' labels | That figure came from a check that can catch false alarms but not misses | New (pilot paper claim) |
| C12 | Scoring check on 40 pilot outputs plus every cut-off and unreadable one, and a 10-document hand recount, written into the protocol | Both were in the run plan but not in the registration | New |
| C13 | Open-weight models only; title and claims say so; no closed model; Claude excluded with a pointer to the cleanup statement | Every model tested is open-weight | Sec. 2: "The confirmatory claims are about the 8 main models" |
| C14 | Hosted line-up: Together runs DeepSeek V4.1 Flash and Qwen3.5-9B in every condition; Bedrock runs Kimi K3 (thinking off), DeepSeek V3.2, Qwen3-235B, Mistral Large 3, gpt-oss-120b and the pairs Ministral 3 14B and gpt-oss-20b on the prompt-side conditions; Kimi K3 thinking on, prompt-side conditions on the pilot documents (the cost test priced all documents at about 338 USD); GLM-5.3 thinking not in the full run | Decided by the authors after the pilot, with a Bedrock budget of 300 USD in credits; the cost test of 18 Oct dropped no model (Bedrock about 91 USD projected) | Sec. 3: "Together AI models are a dated reference ... Kimi K3 with thinking off and GLM-5.3 with thinking on in the prompt-side conditions only" |
| C15 | Qwen3.5-9B thinking pair rerun with presence penalty 0 on the pilot documents; an exploratory re-ask arm on five models | The penalty also acts on thinking text; validate-then-retry is how libraries enforce minimums | Sec. 3: thinking side test |
| C16 | The thinking-text shortfall check is reported as an unchecked phrase search | It was not hand-coded | New |
| C17 | Limits named in advance: multi-field records, a second grammar engine, schema sent only through the API, hand-checking thinking text | Not run; stated so readers do not assume them | New |
| C18 | Stop-rule simulation rerun with the pilot's floor rates | Promised in stage 1 | Sec. 7: "Stage 2 reruns it with the pilot's floor rate" |
| C19 | Registered on OSF before the full run, with a dated timeline; the git tag is named as not independent proof | A git tag set by the authors is not an outside timestamp | Header: "Registered on OSF before the full runs; stage 2 ... follows then" |
| C20 | n = 0 and per-set reporting given their reasons | The n = 0 cells differ in kind | Sec. 6: "n = 0 analysed apart" (kept) |
| C21 | How the cleanup pass was done is stated in the methods | It shaped every answer list | New |
| C22 | Setup facts corrected: batch invariance did not make outputs repeatable; two chat templates add a system prompt; XGrammar keeps a space after ":" and "," | The pilot and engine tests showed each | Sec. 3: "Batch-invariant mode on" |
