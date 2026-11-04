# Padding to k: addendum 1 to the stage-2 registration

Registered study: https://osf.io/e4r9f (stage 2, 18 Oct 2026). This addendum is filed before any of the
numbers below exist: none of the new requests has been sent, and none of the new measures has been
computed on any output. Everything here is **exploratory**. It changes nothing in the registered study: its
models, requests, scoring, confirmatory tests and claims about open-weight models stay as registered.

## 1. Closed models (dated reference, never pooled)

**Models.** xAI Grok 4.3 on Amazon Bedrock (`xai.grok-4.3`, us-east-1, Flex tier); OpenAI GPT-6 Sol and
GPT-6 Luna on Microsoft Azure (Global Standard). Reasoning effort `none` on all three, the setting that
matches "thinking off" in the registered study. Temperature 0 and seed 0 where the API accepts them,
otherwise the API's default; up to 2,048 output tokens. The exact model id, API version, settings and dates
are recorded. A model we cannot run is reported as not run.

**Requests.** The prompt-side conditions (`none`, `prose_up_to_k`, `prose_exactly_k`, `max_k_shown`,
`min_k_shown`, `min_k_shown_fewer_ok`) on the documents with n < k at k = 3 and 5, and on the documents
with no true item at k = 1. For the two prose conditions, wording 1 only (`up_to_1`, "Extract up to {k}
...", and `exactly_1`, "Extract exactly {k} ..."). That is 5,604 requests per model, taken unchanged from
`data/requests.jsonl` and `data/requests_fewer_ok.jsonl`, plus the 300-prompt repeat check drawn as for the
other models (`harness/run.py plan --repeat-of`). As on 18 Oct, a 50-request cost test runs first; each
model's run stops at 25 USD.

**Enforced minimum (only if the API supports it).** Five development requests test whether a model's
structured-output mode enforces `minItems`. If every reply then has at least k entries, `min_k_enforced`
and `min_k_escape` also run on the same documents for that model. Otherwise they do not run, as for Bedrock.

**Scoring and reporting.** The frozen scorer (tag `scorer-v1`) and the registered measures: list length
change, over-count, the sorting of outputs, invented entries. Each model is reported on its own, next to the
hosted models and never pooled with the GPU results.

## 2. Re-ask with "fewer is fine"

On the two Bedrock re-ask runs (Kimi K3 with thinking off, Ministral 3 14B), every `min_k_shown` reply that
the registered re-ask arm sent back is sent back again in the same way, with one extra line at the end of the
re-ask message: "If the document contains fewer than {k}, list all available ones." (the
`min_k_shown_fewer_ok` line). Outcome: over-count among the re-asked outputs, against the registered re-ask.

## 3. What padding does downstream

### 3.1 Decisions a pipeline makes from the list

On the stored outputs of every model (the 8 main GPU models pooled, and every other model on its own), the
same cells as the registered analysis, per condition against `none`, pooled and per set, with 10,000
bootstrap draws over document groups within set:

1. **False alarm:** on the documents with no true item (k = 1), the share of outputs with at least one
   substantive entry, read as "this document has an item".
2. **Collection count:** on documents with n < k (k = 3 and 5), total substantive entries divided by total
   true items in the cell. 1.00 is correct.
3. **Wrong rows:** the share of substantive entries that are not true items (matcher labels), that is 1 minus
   entry precision.

### 3.2 Job-ad skills linked to ESCO

On the two SkillSpan sets (job-ad skills and job-ad knowledge):

- **ESCO:** the latest English ESCO classification (skills pillar, which holds both skills and knowledge
  concepts) from esco.ec.europa.eu, with its version recorded.
- **Linker:** every ESCO concept is represented by its preferred and alternative labels, embedded with
  `sentence-transformers/all-mpnet-base-v2`. An entry links to the concept of its most similar label if the
  cosine similarity is at least 0.5, and stays unlinked otherwise. The true items and the model entries go
  through the same linker. Sensitivity: no cutoff, and a cutoff of 0.7. If the SkillSpan authors recommend a
  different linker, it is added as a second linker and both are reported.
- **Hand check:** 50 links drawn with seed 20261013 (25 from true items, 25 from model entries that are not
  true items), each marked right or wrong by the authors. Reported as the linker's accuracy.
- **Measures**, per condition against `none`, 8 main models pooled and each other model on its own:
  1. false ESCO concepts per ad (concepts linked from the output that no true item of the same ad links to);
  2. ESCO-level precision and recall;
  3. the share of ads with at least one false concept;
  4. of the 20 concepts linked most often across all ads, how many are not in the true items' top 20.
