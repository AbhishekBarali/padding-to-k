# Evidence for the introduction and the schema-leak section

Collected 12-13 Oct 2026. Every number below was computed from pinned downloads; every quote was copied
from the page it links to (opened, not taken from a search snippet). Nothing here is a model result
produced by us.

## 1. How common count rules are in real schemas

Scripts and result files are in `scan/` (`prevalence_scan.py` is the original handbook script, unedited;
`scan_v2.py` imports it and adds per-subset and stricter counts; `table.py` prints the tables).

| Corpus | Schemas | minItems >= 1 | minItems >= 2 | Required array | default | examples |
|---|---|---|---|---|---|---|
| JSONSchemaBench, git 9a94995 (general-purpose schemas) | 9,544 | 9.2% | 1.3% | 24.6% | 15.6% | 2.6% |
| ScrapeGraphAI-100k, real LLM extraction calls, unique schemas outside one dominant template (HF rev 0f8d168) | 7,118 | 0.3% | 0.1% | 49.6% | 7.9% | 0.4% |
| BFCL v4 function schemas (gorilla 6ea5797) | 3,420 | 0% | 0% | 7.5% | 41.1% | 0% |

- The handbook's 9.2% re-runs exactly (identical counts block to the 10 Oct run).
- What it means for the intro: `minItems >= 1` is common in general-purpose schemas, but k >= 2 is rare,
  and in schemas written for LLM extraction the count pressure mostly comes from required arrays and from
  the prompt ("extract 5 ..."), not from `minItems`. Prompt wordings with an explicit k are counted in
  `../wordings.yaml` (for example 169 of 41,538 unique ScrapeGraphAI prompts give an exact k).
- JSONSchemaBench was curated for decoding difficulty, so it is not a random sample of schemas.
- 72% of ScrapeGraphAI's unique schemas are one book table-of-contents template; report the
  non-template subset (row 2 above).

## 2. The failure in the wild (n < k)

| Where | What happened | Quote |
|---|---|---|
| ScrapeGraphAI-100k rows 1141535-6 | Page content was only "Enable JavaScript and cookies to continue"; schema had `players` with `minItems: 20`; claude-3-haiku-20240307 returned 20 fully filled players, none in the page; rows marked `response_is_valid=True` | (data rows) |
| ScrapeGraphAI-100k rows 414128, 422510 | `minItems: 1` on empty pages; Qwen2.5 returned "NA" placeholder items instead | (data rows) |
| [firecrawl/firecrawl-docs#693](https://github.com/firecrawl/firecrawl-docs/pull/693) (merged 2026-03-26) | Vendor documentation change after a support ticket | "Setting `minItems: 20` will not make the LLM return more items - it may instead hallucinate entries to satisfy the constraint." |
| [huggingface/AnyLanguageModel#160](https://github.com/huggingface/AnyLanguageModel/issues/160) | Decoder forced a fixed count | "the model invents or repeats entries to fill the slots (and it can never produce an empty array)." |
| [dheeai/dhee-bundle-illustrated-story-h3#19](https://github.com/dheeai/dhee-bundle-illustrated-story-h3/issues/19) | 9 slots padded from 2 real subjects | "`maxItems: 9` reads to the model as a quota to fill, so it pads the array by repeating the cast it already has." |
| [vectorize-io/hindsight#4457](https://github.com/vectorize-io/hindsight/issues/4457) | Required field filled from a nearby value | "the model copied a nearby project date into an unrelated fact's `when` field" |
| [mlc-ai/xgrammar#160](https://github.com/mlc-ai/xgrammar/issues/160) | Engine ignored the count rule | "2 names should be generated due to JSON constraint, but 4 names is still generated" |
| [vllm-project/vllm-ascend#13646](https://github.com/vllm-project/vllm-ascend/issues/13646) | No maxItems: runaway array | "10271 items, 204 unique, 98% dup" |
| [OpenAI forum 308469](https://community.openai.com/t/how-to-make-function-calling-return-array-as-long-as-i-want/308469) (2023) | Why people add minItems | "requiring this amount using the minItems-maxItems property of json schema. It's not working. At best, it's giving 3." |

The plan's other citations were re-opened and still say what the plan claims: vllm#50502,
llama.cpp#29462, pydantic#604 and #9256, zod#6200. docker/model-runner#1018 is NOT about schema counts
(it is a WSL2 import error); the number in the plan is probably wrong.

## 3. Schema values copied into outputs (section I)

| Where | What happened | Quote |
|---|---|---|
| [getkoji/koji#490](https://github.com/getkoji/koji/pull/490) (merged 2026-07-06) | Example from the extraction hint returned as data | "Two production extractions returned premium: 9486 - the literal worked example '9,486.00' from the premium extraction_hint text, a figure that appears nowhere in either document." |
| ScrapeGraphAI-100k | 184 of 245 rows (75%) whose schema carried a creation timestamp as `default` returned that exact timestamp as `posted_date` (all gemini-2.0-flash, probably one user) | (data rows) |
| [openclaw/openclaw#164583](https://github.com/openclaw/openclaw/issues/164583) | Placeholder values for optional fields under strict schemas | "`messageId: \"x\"` ... `\"00000000-0000-0000-0000-000000000000\"`" |

## 4. Provider support for count rules (re-check before the paper)

- OpenAI Structured Outputs: `minItems` and `maxItems` supported (not for fine-tuned models).
  [docs](https://developers.openai.com/api/docs/guides/structured-outputs)
- Anthropic: "Array `minItems` (only values 0 and 1 supported)".
  [docs](https://docs.claude.com/en/docs/build-with-claude/structured-outputs)
