# What changed after the pilot (read before uploading)

This is the short version of `preregistration/protocol-stage2.md`, the file you upload to OSF as an
Open-Ended Registration before the full run. The full list, with the stage-1 text each change replaces,
is in section 10 of that file. Stage 1 (`preregistration/protocol.md`, tag `prereg-v1`) is not touched.

## The main changes

**We now measure how much longer the list gets.** The main number is the list length on a document
under a shown minimum, minus its length on the same document with no count asked. It needs no answer
list, which matters because the answer list is the weakest part of the study. Over-count stays as a
second number. We also count the true items a list leaves out, and sort every answer as padded, an
honest short list, or "says it is short" (unreadable answers are a fourth group).

**We say what the right answer is.** When a document has fewer items than asked, the right answer lists
what is there and stops, or says the list is short. That answers "it just followed the instruction".

**One new condition.** `min_k_shown_fewer_ok` is the shown minimum plus one line saying a shorter list is
fine. If models still pad, it is not plain obedience. The wording and its 1,674 requests are in `data/build_fewer_ok.py` and `data/requests_fewer_ok.jsonl`.

**Three tests get a name.** They were already in the design but had no named result:
- documents that already have enough items (9,900 requests per model): a minimum should change little
  there, so the gap between these and the short documents shows how much of the effect is slot filling;
- k = 1 on the 105 documents with no true item (1,575 requests per model);
- maxItems against no count, with its interval.

The five confirmatory contrasts stay, the N/A escape among them. Contrasts 1 to 4 now use list length.

**One primary test per contrast.** The bootstrap interval of the paired difference is the test; the mixed
model and the per-model numbers go next to it, and the per-model numbers come first. The pilot's three
models differed a lot (13, 30, 60 points), so a single pooled number would hide that. This choice was
not in the list decided with you; change it before upload if you prefer the mixed model as primary.

## The answer key

- The blind check's second round passed rule 3 as registered (A 87.5%, B 95%, AC1 0.851). Round 1 stays
  reported as failed. Results go per set; job-ad skills is the least certain list.
- New check against the datasets' own counts (`analysis/answer_key_vs_source.py`): on the 558 study
  documents the cleaned count equals the original annotators' count on 423 (76%). Meetings went up most
  often, emails and reviews down. Receipts and novel quotes barely changed. On the 15 blind-check
  documents where the two counts differ, A's blind count matched the cleaned count 10 times and the
  original once; B's 9 times and once. Headline numbers will also be shown with the original counts.

## What you do (all listed in section 5.3)

1. Before the full run: read 40 random pilot outputs plus the 7 cut-off or unreadable ones against the
   scorer (about 1.5 hours, one of you).
2. After the full run: both of you label about 400 entries, blind to model and condition. The sample takes
   80 per matcher label, so the rare "invented" and "missed" entries get as many examples as the common
   ones. The pilot's "at most 4% invented" is dropped unless these labels support it.
3. After scoring: recount 10 documents by hand (70 outputs) and compare with the scorer.

## Models

Open-weight only, and the title and claims say so. No closed model; Claude stays out for the reason in
your cleanup statement. The local 8 models are unchanged. Hosted: Together runs DeepSeek V4.1 Flash and
Qwen3.5-9B in every condition; Bedrock (300 USD of credits) runs Kimi K3, DeepSeek V3.2, Qwen3-235B,
Mistral Large 3 and gpt-oss-120b, plus Ministral 3 14B and gpt-oss-20b as same-weights pairs, on the
prompt-side conditions. Kimi K3 with thinking on runs on the pilot documents only (all of them would cost about 338 USD).
The cost test dropped no model: Bedrock projects to about 91 USD and Together to about 9 USD. GLM-5.3 is not in the full run. Extra: Qwen3.5-9B thinking with
presence penalty 0 on the pilot documents, and an exploratory re-ask arm on five models. The final list is whatever
`configs/models.yaml` says at tag `prereg-v2.1`.

## Not done, named as limits

Lists of multi-field records, a second grammar engine, a schema sent only through the API, and
hand-checking the thinking text.

## Blanks for you to fill in `protocol-stage2.md`

- How the cleanup pass and the matcher's development labels were made (tool and version or person,
  propose or decide, counts per set, what each of you checked).
- Affiliations (non-anonymous copy only).
- The OSF link and date, and the date in the timeline.
- The Gemma 4 31B thinking pair's full-run scope.

The protocol names you only as author A and author B and gives repository paths, not links, so it can
go under an OSF embargo and an anonymous review link.
