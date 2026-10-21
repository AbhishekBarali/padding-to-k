# POST HOC analyses (not in the registered plan)

Every result in this file is POST HOC: none of these analyses is in `preregistration/protocol-stage2.md`. Nothing in `preregistration/manifest-stage2.sha256` was changed; the locked parser, placeholder rules and matcher v0 are used as they are (the lenient parser of section 4 is a separate function in `analysis/posthoc/lenient_08b.py`). Every matcher-based number is matcher v0 and preliminary, as in the paper.

## Scope and inputs

- Runs: the `fs_<model>_full` runs, arm `main`, ok outputs (as `analysis/full_study.py`). **GPU** = the 8 main GPU models pooled (Qwen3.5-0.8B, Qwen3.5-2B, Qwen3.5-9B, Qwen3.5-27B, Gemma 4 31B, Olmo 3.1 32B, Ministral 3 14B, gpt-oss-20b); **hosted** = the 9 hosted models pooled (reference only, as in the paper).
- Labels: the cached matcher v0 labels in `analysis/full/scored/*.entries.csv.gz` (written by `analysis/full_study_score.py`); `analysis/posthoc/check_cache.py` confirms every cached table matches its run folder (same source hash the scorer uses). Entry text: re-parsed from the run records with the locked `common.parse_output` (`analysis/posthoc/build_entries.py`; it stops if parse and cache disagree on any output's entry count).
- Extra entry: a substantive entry the matcher does not match to a distinct true item (labels true-but-split, wrong kind, invented), the paper's definition (`full_study.py` section 6b).
- `none` is asked once and its answer reused at k = 1, 3 and 5; as in `full_study.py`, a `none` entry counts once per k it answers.

Checks that could fail:

- GPU extra entries per condition (n < k, k = 3 and 5) from the entry table equal the per-output sums the paper's table uses, for every condition: none 18109, prose_up_to_k 62574, prose_exactly_k 66808, max_k_shown 14697, min_k_shown 22665, min_k_shown_fewer_ok 13343, min_k_enforced 26193, min_k_escape 15198 (all equal: True).
- The 400-entry check frame (`analysis/human/matcher_frame.json`) against this table: wrong kind 408859 vs 408859, invented 78798 vs 78798, true or split 637855 vs 637844. The true-or-split difference is all in novel quotes: three GPU runs (0.8B, 2B, gpt-oss-20b) got resent records on 19 Oct, after the frame was drawn on 18 Oct.
- Lenient parser: of the 16973 0.8B outputs the locked parser reads, 0 change under the lenient one; the strict 0.8B contrast 2 of section 4 (-0.59 [-1.06, -0.13]) against RESULTS.md section 2 (-0.59 [-1.06, -0.13]): equal True.

Reproduce (from the repository root; `data/local` must hold the restricted review documents):

```
uv run --no-project --offline --python 3.12 --with pandas==3.0.6 --with numpy==2.5.4 --with scipy==1.18.1 --with statsmodels==0.15.0 --with patsy==1.0.3 --with rapidfuzz==3.14.6 --with pyyaml python analysis/posthoc/check_cache.py <runs-dir>
uv run --no-project --offline --python 3.12 --with pandas==3.0.6 --with numpy==2.5.4 --with scipy==1.18.1 --with statsmodels==0.15.0 --with patsy==1.0.3 --with rapidfuzz==3.14.6 --with pyyaml python analysis/posthoc/build_entries.py --runs-dir <runs-dir> --jobs 3
uv run --no-project --offline --python 3.12 --with pandas==3.0.6 --with numpy==2.5.4 --with scipy==1.18.1 --with statsmodels==0.15.0 --with patsy==1.0.3 --with rapidfuzz==3.14.6 --with pyyaml python analysis/posthoc/lenient_08b.py --runs-dir <runs-dir> --boot 10000
uv run --no-project --offline --python 3.12 --with pandas==3.0.6 --with numpy==2.5.4 --with scipy==1.18.1 --with statsmodels==0.15.0 --with patsy==1.0.3 --with rapidfuzz==3.14.6 --with pyyaml python analysis/posthoc/posthoc.py --boot 10000
```

`<runs-dir>` is the folder of `fs_*` run folders. `build_entries.py` writes `analysis/posthoc/cache/` (gitignored: it holds entry text, review text included). Outputs: `analysis/posthoc/out/`.

## 1. Source check: would a deployable grounding check catch the extra entries?

Each entry against its own source document. **exact**: the entry, normalised (Unicode NFKC, curly quotes and dashes made plain, lower case, whitespace collapsed, quotes and punctuation stripped from both ends; `common_posthoc.gnorm`), is a substring of the normalised document. **fuzzy**: exact, or rapidfuzz `fuzz.partial_ratio(entry, document) >= 90` on the same normalised strings. **in_document**: the repo's own `common.in_document` (punctuation removed, at least 4 characters), for reference. No entry is empty after normalising (0 empty extra entries). Pass = the check would let the entry through.

GPU, documents with n < k, k = 3 and 5:

|  | entries | exact substring % | fuzzy (partial_ratio >= 90) % | repo's own in_document % |
|---|---|---|---|---|
| extra entries, all | 239587 | 53.1 | 55.4 | 51.3 |
| extra: true-but-split | 18025 | 52.4 | 54.6 | 52.7 |
| extra: wrong kind | 173345 | 67.7 | 70.7 | 65.3 |
| extra: invented | 48217 | 0.6 | 0.9 | 0.2 |
| true-item entries (reference) | 137849 | 80.6 | 83.2 | 80.6 |
| extra entries, the 7 copied-text sets | 197662 | 60.3 | 63.1 | 58.4 |
| invented entries, the 7 copied-text sets | 45781 | 0.4 | 0.7 | 0.0 |
| true-item entries, the 7 copied-text sets | 108801 | 88.4 | 91.7 | 88.5 |

The 7 copied-text sets leave out meetings (the item is a one-sentence summary, so no item is a copy) and Wikipedia people (names). By condition (GPU, n < k, k = 3 and 5):

| condition | extra entries | exact % | fuzzy % | invented entries | invented exact % | invented fuzzy % | true items exact % | true items fuzzy % |
|---|---|---|---|---|---|---|---|---|
| none | 18109 | 46.5 | 49.0 | 5403 | 0.6 | 0.8 | 81.4 | 84.1 |
| prose_up_to_k | 62574 | 48.4 | 50.7 | 13172 | 0.4 | 0.6 | 79.5 | 82.0 |
| prose_exactly_k | 66808 | 53.7 | 56.0 | 11949 | 0.5 | 0.7 | 80.9 | 83.5 |
| max_k_shown | 14697 | 47.3 | 49.8 | 4110 | 0.6 | 0.9 | 81.5 | 84.1 |
| min_k_shown | 22665 | 46.6 | 48.7 | 6702 | 0.4 | 0.6 | 79.6 | 82.3 |
| min_k_shown_fewer_ok | 13343 | 56.5 | 58.7 | 2886 | 0.8 | 1.1 | 85.0 | 87.3 |
| min_k_enforced | 26193 | 65.6 | 68.2 | 2809 | 1.7 | 2.4 | 79.7 | 82.8 |
| min_k_escape | 15198 | 67.6 | 70.6 | 1186 | 3.1 | 3.8 | 80.7 | 83.8 |

By set (GPU, n < k, k = 3 and 5):

| set | extra entries | exact % | fuzzy % | invented entries | invented exact % | true items exact % | true items fuzzy % |
|---|---|---|---|---|---|---|---|
| meetings | 36408 | 7.5 | 7.5 | 2221 | 4.8 | 1.7 | 2.8 |
| emails | 14486 | 47.5 | 54.3 | 988 | 0.1 | 72.1 | 78.3 |
| receipts | 9216 | 99.6 | 99.8 | 31 | 51.6 | 99.6 | 99.9 |
| job-ad skills | 64523 | 65.4 | 67.8 | 12724 | 0.6 | 75.2 | 81.8 |
| clinical | 5735 | 54.9 | 56.3 | 2276 | 0.7 | 98.1 | 99.3 |
| reviews | 22684 | 62.8 | 67.1 | 2912 | 1.7 | 78.2 | 83.2 |
| job-ad knowledge | 70386 | 47.4 | 49.7 | 26726 | 0.1 | 92.4 | 93.4 |
| Wikipedia people | 5517 | 95.2 | 95.8 | 215 | 0.5 | 99.9 | 100.0 |
| novel quotes | 10632 | 96.1 | 98.7 | 124 | 0.0 | 96.2 | 99.9 |

GPU, all documents (any n), k = 3 and 5:

|  | entries | exact substring % | fuzzy (partial_ratio >= 90) % | repo's own in_document % |
|---|---|---|---|---|
| extra entries | 270346 | 52.7 | 55.1 | 50.8 |
| extra: true-but-split | 20668 | 51.5 | 53.6 | 51.4 |
| extra: wrong kind | 193312 | 68.0 | 71.0 | 65.5 |
| extra: invented | 56366 | 0.7 | 1.0 | 0.2 |
| true-item entries | 211919 | 80.4 | 82.9 | 80.3 |

Hosted, n < k, k = 3 and 5:

|  | entries | exact substring % | fuzzy (partial_ratio >= 90) % | repo's own in_document % |
|---|---|---|---|---|
| extra entries | 159690 | 59.0 | 61.6 | 58.0 |
| extra: true-but-split | 18467 | 51.6 | 54.0 | 52.4 |
| extra: wrong kind | 132184 | 64.0 | 66.7 | 62.8 |
| extra: invented | 9039 | 1.4 | 1.6 | 0.1 |
| true-item entries | 156093 | 82.3 | 84.8 | 82.3 |

The matcher calls an entry invented largely because it is not found in the text, so the invented rows above are close to circular. The 400 entries the authors labelled give a check that does not lean on the matcher (400 of 400 found in the entry table), by the authors' settled label:

|  | entries | exact substring % | fuzzy (partial_ratio >= 90) % | repo's own in_document % |
|---|---|---|---|---|
| true_item | 123 | 82.9 | 85.4 | 82.9 |
| plausible_invented | 99 | 0.0 | 0.0 | 0.0 |
| in_text_wrong_type | 135 | 74.8 | 77.0 | 74.8 |
| split_of_true | 36 | 63.9 | 69.4 | 44.4 |
| missed_gold | 5 | 40.0 | 40.0 | 40.0 |
| unsure | 2 | 0.0 | 0.0 | 0.0 |
| all | 400 | 57.0 | 59.0 | 55.2 |

**Result.** About half the extra entries pass: 53.1% exact and 55.4% fuzzy (GPU, n < k), against 80.6% and 83.2% of true-item entries. Wrong-kind entries pass at 67.7% / 70.7%; invented entries almost never do (0.6% / 0.9%), and none of the 99 entries the authors call invented passes either check. Under the shown minimum 46.6% of extra entries pass exact. So a grounding check removes the invented padding and keeps most of the wrong-kind padding; on the copied-text sets it passes 60.3% of extra entries.

## 2. Prevalence: what the extra entries are under the shown minimum

Share of extra entries by matcher v0 label, documents with n < k, k = 3 and 5, condition `min_k_shown`:

| pool | extra entries | true-but-split % | wrong kind % | invented % | invented, not prompt echo or note % | invented % of all substantive entries |
|---|---|---|---|---|---|---|
| GPU (8 main models) | 22665 | 7.5 | 62.9 | 29.6 | 29.5 | 21.5 |
| GPU, `none` (for comparison) | 18109 | 5.5 | 64.6 | 29.8 | 29.8 | 20.2 |
| hosted (9 models) | 18314 | 12.3 | 82.0 | 5.7 | 5.6 | 3.5 |
| all 17 models | 40979 | 9.7 | 71.5 | 18.9 | 18.8 | 12.8 |

Corrected with the authors' labels: each matcher label's extra entries are spread over the authors' categories in the proportions the settled 400-entry check gives for that matcher label (authors' missed_gold counted as a true item, 2 unsure rows dropped; the matcher's true-but-split label has only 10 checked rows). 95% interval: 10,000 resamples of the checked rows within each matcher label (seed 20261014). The proportions come from the whole check frame, not from this cell: only 7 checked rows are GPU `min_k_shown` with n < k.

| GPU `min_k_shown`, n < k, k = 3 and 5 (22665 matcher extra entries) | share [95% CI] |
|---|---|
| true item % of matcher extras | 5.5 [2.6, 8.7] |
| true-but-split % of matcher extras | 12.7 [9.4, 16.3] |
| wrong kind % of matcher extras | 58.4 [54.0, 62.6] |
| invented % of matcher extras | 23.4 [20.4, 26.6] |
| invented % of corrected extras (true items removed) | 24.7 [21.5, 28.2] |

Checked rows by matcher label and authors' label: matcher true_item: invented 2, true item 115, true-but-split 7; matcher plausible_invented: invented 91, true item 5, true-but-split 13, wrong kind 22; matcher in_text_wrong_type: invented 6, true item 6, true-but-split 8, wrong kind 113; matcher split_of_true: true item 2, true-but-split 8.

**Settled.** Both numbers are right; they have different denominators. The ~7% is the invented share of *all substantive entries* (true items included) over the whole check frame: all 17 models, all conditions, all k and n (7.0% from this table; the paper's 7.0% matcher / 7.3% corrected). The ~30% is the invented share of the *extra entries* on documents with n < k under the shown minimum, GPU models: 29.6% by the matcher (29.5% without prompt echoes and possible notes, the paper's 29.5%), 23.4 [20.4, 26.6]% after correcting with the authors' labels. So the reviewer's ~30% is the matcher's figure for the padding itself; the corrected figure is about a quarter; the 7% must not be read as the invented share of the padding. The share depends on the models: hosted models' extras are 5.7% invented, all 17 pooled 18.9%.

**Was the 400-entry sample stratified?** Yes, by matcher label: 134 true-or-split, 133 wrong kind, 133 invented (the protocol's 80 per label, with the two labels v0 never assigns given to the other three), and within a label as equally as possible over the 9 sets, at most one entry per output, from every substantive entry of the 17 full runs (`analysis/full_study_sheets.py`, `draw_matcher_labels`). The sample's own label shares are therefore not prevalences; the paper's 7.3% weights each stratum by its frame size.

## 3. Precision, recall and F1 per condition

Entry level, matcher v0, k = 3 and 5, ok outputs (unreadable outputs count as 0 entries, so they lower recall and leave precision alone). Precision = true-item entries / substantive entries (a split piece, a wrong-kind or an invented entry is not a correct entry; `precision, split ok` also counts true-but-split pieces as correct). Recall = true items some entry matches (true-item and split labels) / true items, on documents with n >= 1. F1 from the pooled P and R. Pooled = summed over outputs. 95% intervals: full_study's bootstrap, 10,000 draws over document groups within set, seed 20261014.

GPU, all documents:

| condition | outputs | substantive entries | precision | precision, split ok | recall | F1 | extra entries per output |
|---|---|---|---|---|---|---|---|
| none | 8928 | 35078 | 0.389 [0.365, 0.414] | 0.428 | 0.830 [0.817, 0.842] | 0.530 [0.506, 0.553] | 2.40 |
| prose_up_to_k | 44640 | 136607 | 0.480 [0.457, 0.503] | 0.514 | 0.800 [0.786, 0.815] | 0.600 [0.581, 0.619] | 1.59 |
| prose_exactly_k | 44640 | 138894 | 0.464 [0.441, 0.487] | 0.509 | 0.784 [0.770, 0.799] | 0.583 [0.564, 0.602] | 1.67 |
| max_k_shown | 8928 | 29865 | 0.435 [0.409, 0.460] | 0.468 | 0.791 [0.777, 0.806] | 0.561 [0.538, 0.583] | 1.89 |
| min_k_shown | 8928 | 39101 | 0.345 [0.324, 0.366] | 0.395 | 0.818 [0.807, 0.830] | 0.486 [0.464, 0.507] | 2.87 |
| min_k_shown_fewer_ok | 8928 | 27798 | 0.448 [0.422, 0.477] | 0.485 | 0.757 [0.742, 0.772] | 0.563 [0.540, 0.587] | 1.72 |
| min_k_enforced | 8926 | 43501 | 0.346 [0.325, 0.366] | 0.410 | 0.914 [0.902, 0.926] | 0.501 [0.479, 0.523] | 3.19 |
| min_k_escape | 8922 | 31421 | 0.452 [0.429, 0.474] | 0.507 | 0.864 [0.849, 0.878] | 0.593 [0.573, 0.613] | 1.93 |

GPU, documents with n < k:

| condition | outputs | substantive entries | precision | precision, split ok | recall | F1 | extra entries per output |
|---|---|---|---|---|---|---|---|
| none | 7272 | 26708 | 0.322 [0.299, 0.346] | 0.360 | 0.828 [0.814, 0.841] | 0.464 [0.439, 0.489] | 2.49 |
| prose_up_to_k | 36360 | 105741 | 0.408 [0.385, 0.431] | 0.446 | 0.831 [0.817, 0.844] | 0.548 [0.526, 0.568] | 1.72 |
| prose_exactly_k | 36360 | 109506 | 0.390 [0.369, 0.412] | 0.441 | 0.820 [0.807, 0.832] | 0.528 [0.508, 0.549] | 1.84 |
| max_k_shown | 7272 | 23145 | 0.365 [0.340, 0.390] | 0.401 | 0.813 [0.799, 0.826] | 0.504 [0.479, 0.528] | 2.02 |
| min_k_shown | 7272 | 31235 | 0.274 [0.256, 0.293] | 0.329 | 0.821 [0.810, 0.832] | 0.411 [0.391, 0.432] | 3.12 |
| min_k_shown_fewer_ok | 7272 | 21136 | 0.369 [0.344, 0.395] | 0.409 | 0.749 [0.733, 0.764] | 0.494 [0.470, 0.519] | 1.83 |
| min_k_enforced | 7270 | 35820 | 0.269 [0.253, 0.285] | 0.339 | 0.925 [0.914, 0.936] | 0.416 [0.397, 0.436] | 3.60 |
| min_k_escape | 7267 | 24145 | 0.371 [0.351, 0.389] | 0.433 | 0.861 [0.846, 0.875] | 0.518 [0.498, 0.537] | 2.09 |

Hosted, all documents (reference; `min_k_enforced` / `min_k_escape` only on the hosted models that ran them):

| condition | precision | recall | F1 | extra entries per output |
|---|---|---|---|---|
| none | 0.605 | 0.936 | 0.735 | 1.12 |
| prose_up_to_k | 0.625 | 0.889 | 0.734 | 0.97 |
| prose_exactly_k | 0.566 | 0.888 | 0.691 | 1.25 |
| max_k_shown | 0.659 | 0.895 | 0.759 | 0.85 |
| min_k_shown | 0.469 | 0.944 | 0.626 | 1.97 |
| min_k_shown_fewer_ok | 0.628 | 0.894 | 0.738 | 0.97 |
| min_k_enforced | 0.380 | 0.959 | 0.544 | 2.89 |
| min_k_escape | 0.539 | 0.925 | 0.681 | 1.46 |

Per model, all documents, precision / recall / F1 (every condition in `out/prf.csv`):

| model | none | min_k_shown | min_k_shown_fewer_ok | min_k_enforced |
|---|---|---|---|---|
| Qwen3.5-0.8B | 0.15 / 0.33 / 0.21 | 0.13 / 0.23 / 0.17 | 0.16 / 0.35 / 0.22 | 0.21 / 0.84 / 0.33 |
| Qwen3.5-2B | 0.15 / 0.85 / 0.26 | 0.14 / 0.83 / 0.24 | 0.19 / 0.76 / 0.30 | 0.26 / 0.88 / 0.40 |
| Qwen3.5-9B | 0.60 / 0.86 / 0.71 | 0.52 / 0.88 / 0.65 | 0.65 / 0.73 / 0.69 | 0.38 / 0.94 / 0.54 |
| Qwen3.5-27B | 0.75 / 0.95 / 0.84 | 0.54 / 0.95 / 0.69 | 0.66 / 0.93 / 0.77 | 0.44 / 0.96 / 0.61 |
| Gemma 4 31B | 0.87 / 0.91 / 0.89 | 0.53 / 0.95 / 0.68 | 0.88 / 0.92 / 0.90 | 0.47 / 0.96 / 0.63 |
| Olmo 3.1 32B | 0.44 / 0.89 / 0.59 | 0.42 / 0.87 / 0.57 | 0.69 / 0.65 / 0.67 | 0.33 / 0.91 / 0.49 |
| Ministral 3 14B | 0.46 / 0.93 / 0.61 | 0.44 / 0.92 / 0.59 | 0.68 / 0.83 / 0.75 | 0.37 / 0.90 / 0.53 |
| gpt-oss-20b | 0.60 / 0.91 / 0.72 | 0.48 / 0.91 / 0.62 | 0.59 / 0.89 / 0.71 | 0.46 / 0.93 / 0.61 |
| DeepSeek V4.1 Flash (Together) | 0.64 / 0.97 / 0.77 | 0.46 / 0.98 / 0.62 | 0.56 / 0.97 / 0.71 | 0.39 / 0.98 / 0.55 |
| Qwen3.5-9B (Together) | 0.58 / 0.85 / 0.69 | 0.51 / 0.88 / 0.65 | 0.65 / 0.71 / 0.68 | 0.37 / 0.94 / 0.53 |
| Kimi K3 (Bedrock) | 0.77 / 0.96 / 0.86 | 0.54 / 0.98 / 0.70 | 0.71 / 0.97 / 0.82 | -- |
| DeepSeek V3.2 (Bedrock) | 0.67 / 0.95 / 0.78 | 0.39 / 0.97 / 0.56 | 0.60 / 0.93 / 0.73 | -- |
| Qwen3-235B (Bedrock) | 0.65 / 0.94 / 0.77 | 0.48 / 0.96 / 0.64 | 0.61 / 0.94 / 0.74 | -- |
| Mistral Large 3 (Bedrock) | 0.60 / 0.94 / 0.73 | 0.48 / 0.95 / 0.64 | 0.70 / 0.89 / 0.78 | -- |
| Ministral 3 14B (Bedrock) | 0.44 / 0.94 / 0.60 | 0.43 / 0.93 / 0.59 | 0.67 / 0.83 / 0.74 | -- |
| gpt-oss-20b (Bedrock) | 0.60 / 0.91 / 0.72 | 0.48 / 0.91 / 0.63 | 0.59 / 0.88 / 0.70 | -- |
| gpt-oss-120b (Bedrock) | 0.61 / 0.95 / 0.74 | 0.48 / 0.94 / 0.64 | 0.61 / 0.92 / 0.74 | -- |

**Result.** A shown minimum costs precision and buys no recall: GPU pooled, all documents, precision 0.345 vs 0.389 with no count, recall 0.818 vs 0.830, F1 0.486 vs 0.530. An enforced minimum raises recall to 0.914 at precision 0.346 (F1 0.501).

Padding vs missed true items per (model, condition): `out/padding_vs_missed.csv` (all 17 models; x = mean extra entries per output, y = 100 x (1 - recall), k = 3 and 5, all documents; also the n < k padding and P, R, F1). `out/fig_padding_vs_missed.tex` plots the 8 GPU models (one mark per model and condition, condition by mark, `\footnotesize` labels): `\input{.../fig_padding_vs_missed.tex}` inside a `figure`; it uses pgfplots and the paper's `\cnd` macro.

## 4. Qwen3.5-0.8B with a lenient parser

The locked parser never takes a schema-shaped object as the answer, and 0.8B often writes its list inside a copy of the schema (`{"type": "object", "properties": {"requests": [ ... ]}}`). The lenient parser (`lenient_08b.py`, `parse_lenient`) runs the locked ladder first; only when it finds no list it searches every JSON object of the reply for the asked-for field and takes its list (directly, or the `items` list of a schema copy). A schema echo with no list in it, and broken JSON (missing commas, unescaped quotes), stay unreadable. The 0.8B run is then rescored with the repo's own scorer (`full_study_score.score_run`, parse call swapped in-process only) and analysed with `full_study.py`'s own pairing and bootstrap.

- Outputs the locked parser reads: 16973; of them changed by the lenient parser: 0 (must be 0).

| measure | strict | lenient |
|---|---|---|
| unreadable outputs, all conditions and k | 9810 of 26783 (36.63%) | 2634 of 26783 (9.83%) |
| C2 shown minimum vs no count, length change (entries) | -0.59 [-1.06, -0.13] (pairs 909) | -0.54 [-1.01, -0.06] (pairs 909) |
| C2 over-count (points) | -6.0 [-8.2, -3.8] (pairs 909) | -1.3 [-4.0, +1.4] (pairs 909) |
| C2 length, pairs readable on both sides | +1.22 [+0.36, +2.24] (pairs 293) | +0.23 [-0.36, +0.80] (pairs 622) |
| C2 over-count, pairs readable on both sides (points) | +3.4 [+1.3, +6.0] (pairs 293) | +7.4 [+5.0, +9.9] (pairs 622) |
| C1 dose k=5 vs k=3 (entries) | -0.38 [-0.84, +0.07] (pairs 375) | -0.09 [-0.55, +0.37] (pairs 375) |
| C3 shown minimum vs shown maximum (entries) | -0.32 [-0.73, +0.08] (pairs 909) | +0.06 [-0.36, +0.47] (pairs 909) |
| fewer-ok minimum vs no count (entries) | +0.03 [-0.39, +0.47] (pairs 909) | -0.57 [-1.04, -0.08] (pairs 909) |

Per condition, documents with n < k, k = 3 and 5 (unreadable outputs count as 0 entries, as in the paper):

| condition | outputs | mean entries strict | mean entries lenient | over-count % strict | over-count % lenient | unreadable % strict | unreadable % lenient |
|---|---|---|---|---|---|---|---|
| none | 909 | 4.03 | 5.59 | 30.9 | 52.8 | 54.2 | 18.6 |
| prose_up_to_k | 4545 | 3.69 | 4.51 | 50.0 | 64.9 | 28.0 | 2.9 |
| prose_exactly_k | 4545 | 3.07 | 4.42 | 39.6 | 67.4 | 45.0 | 7.3 |
| max_k_shown | 909 | 3.76 | 5.00 | 29.3 | 49.2 | 57.5 | 27.6 |
| min_k_shown | 909 | 3.44 | 5.06 | 24.9 | 51.5 | 67.4 | 30.9 |
| min_k_shown_fewer_ok | 909 | 4.06 | 5.03 | 34.0 | 49.3 | 49.1 | 28.1 |
| min_k_enforced | 909 | 7.56 | 7.56 | 91.9 | 91.9 | 0.8 | 0.8 |
| min_k_escape | 908 | 6.74 | 6.74 | 89.6 | 89.6 | 1.0 | 1.0 |

Lenient parse rungs (ok outputs): array_in_text 44, failed 289, fence 15166, first_object 1, lenient_schema_copy 7171, lenient_schema_copy_items 5, strict 3065, truncated_salvage 1042

**Result.** The lenient parser cuts 0.8B's unreadable share from 36.63% to 9.83%. The registered contrast 2 (unreadable = 0 entries) barely moves on length (-0.59 [-1.06, -0.13] strict, -0.54 [-1.01, -0.06] lenient), because the shown minimum still holds more pure schema echoes (30.9% unreadable vs 18.6% under `none`). On over-count it moves from -6.0 [-8.2, -3.8] to -1.3 [-4.0, +1.4] points. On the pairs readable on both sides the sign is positive under both parsers: locked parser +1.22 [+0.36, +2.24] entries and +3.4 [+1.3, +6.0] points (293 pairs); lenient +0.23 [-0.36, +0.80] entries and +7.4 [+5.0, +9.9] points (622 pairs). So the negative registered estimate for 0.8B comes from unreadable outputs counted as empty lists, not from shorter lists. With the lenient parser 0.8B shows the over-count effect but no clear length change; it pads under every condition (52.8% over-count with no count). Readable-pairs numbers condition on readability, which the condition itself changes, so they are descriptive only.

## 5. Examples: padding under the shown minimum

One real output per answer-list set: GPU main models, condition `min_k_shown`, k = 3 or 5, a document with 1 <= n < k, an over-count output (more substantive entries than true items), at most 6 entries of at most 200 characters, at least one extra entry; among those, the output with the smallest sha256 of run id and request id (no hand picking). Labels are matcher v0 and can be wrong: in the emails example the matcher pairs the first entry with a true item and calls the near-verbatim second entry a split; the count of extra entries (entries minus true items) is right either way. Entries and true items are verbatim; the review is paraphrased (restricted text).

### meetings: Olmo 3.1 32B, document `mtg-a6de72`, k = 3, n = 1 (3 entries, 2 extra)

True items:
- The group will find out if the kinetic energy component can provide enough energy.

The model's list (matcher v0 label):
1. Check with the R&D department to see if the kinetic metal technology can provide sufficient energy for the remote. -- **true item**
2. Consult with the R&D department regarding the readiness of the kinetic energy product for market. -- **true-but-split** (extra)
3. Gather and share pictures of the device cases with the Industrial Designer for material identification (titanium vs. plastic). -- **wrong kind** (extra)

### emails: Olmo 3.1 32B, document `eml-c10115`, k = 3, n = 2 (4 entries, 2 extra)

True items:
- What do we need to do to get this
- how soon can it be granted?

The model's list (matcher v0 label):
1. Everyone in risk management needs to get access to EOL bridge monitor and reports. -- **true item**
2. What do we need to do to get this access? -- **true-but-split** (extra)
3. How soon can the access be granted? -- **true item**
4. We need this access by Thursday to be prepared for testing. -- **wrong kind** (extra)

### receipts: Qwen3.5-9B, document `rcp-2dd118`, k = 3, n = 1 (3 entries, 2 extra)

True items:
- ALMOND CHOCO CREAM CHEESE

The model's list (matcher v0 label):
1. ALMOND CHOCO CREAM CHEESE -- **true item**
2. SUB TOTAL -- **wrong kind** (extra)
3. GRAND TOTAL -- **wrong kind** (extra)

### job-ad skills: Olmo 3.1 32B, document `job-2f4da8`, k = 5, n = 1 (5 entries, 4 extra)

True items:
- running with a full stack development

The model's list (matcher v0 label):
1. running full stack development -- **true item**
2. Java -- **wrong kind** (extra)
3. Python -- **wrong kind** (extra)
4. React JS -- **wrong kind** (extra)
5. Redux -- **wrong kind** (extra)

### clinical: Ministral 3 14B, document `med-748a61`, k = 5, n = 3 (5 entries, 2 extra)

True items:
- ACE inhibitor
- diuretic
- β-blocker

The model's list (matcher v0 label):
1. ACE inhibitor -- **true item**
2. diuretic -- **true item**
3. low-dose β-blocker -- **true item**
4. coronary angiography contrast agent (if applicable) -- **invented** (extra)
5. endomyocardial biopsy procedural sedation/anesthesia (if applicable) -- **invented** (extra)

### reviews: Qwen3.5-2B, document `rev-fb5a63`, k = 5, n = 1 (5 entries, 4 extra)

A short hotel review from the restricted reviews set (no review text is reproduced here). The reviewer calls the hotel a hidden gem of its city, says they had expected an ordinary chain hotel, says it beat every hotel they had used in a long time, and praises the staff. The answer list holds one item: the staff.

The model's list has five entries. Four copy short phrases from the review that name the hotel or praise it in general (its headline, the chain it was expected to resemble, the comparison with other hotels); the matcher calls all four real text of the wrong kind, so all four are extra. The fifth, praise of the staff, is the one true item.

### job-ad knowledge: Gemma 4 31B, document `jbk-22d8d3`, k = 5, n = 2 (5 entries, 3 extra)

True items:
- science
- pharmaceutical production

The model's list (matcher v0 label):
1. science education -- **true item**
2. pharmaceutical production -- **true item**
3. management experience -- **wrong kind** (extra)
4. communication skills -- **wrong kind** (extra)
5. collaboration skills -- **wrong kind** (extra)

### Wikipedia people: Qwen3.5-2B, document `ppl-83c086`, k = 5, n = 2 (3 entries, 1 extra)

True items:
- Stamatiad
- Emil Gârleanu

The model's list (matcher v0 label):
1. Stamatiad -- **true item**
2. Emil Gârleanu -- **true item**
3. Romanian Writers ' Society (SSR) -- **wrong kind** (extra)

### novel quotes: gpt-oss-20b, document `quo-682820`, k = 5, n = 3 (5 entries, 2 extra)

True items:
- After what happened at Vevey, I think I may certainly call upon them,
- If, after what happens--at Vevey and everywhere--you desire to keep up the acquaintance, you are very welcome. Of course a man may know everyone. Men are welcome to the privilege!
- Pray what is it that happens--here, for instance?

The model's list (matcher v0 label):
1. After what happened at Vevey -- **true item**
2. I think I may certainly call upon them, -- **true-but-split** (extra)
3. If, after what happens--at Vevey and everywhere--you desire to keep up the acquaintance, you are very welcome. -- **true item**
4. Of course a man may know everyone. Men are welcome to the privilege! -- **true-but-split** (extra)
5. Pray what is it that happens--here, for instance? -- **true item**


