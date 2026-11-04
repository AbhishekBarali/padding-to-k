# Job-ad skills linked to ESCO (OSF addendum 1, section 3.2; exploratory)

Written by `python analysis/downstream/esco/esco_downstream.py` (see its docstring for every definition). Every number below comes from that script; nothing is typed in by hand.

- ESCO v1.2.1 (English, skills pillar: 13960 concepts, 100650 preferred + alternative labels), package "ESCO dataset - v1.2.1 - classification - en - csv.zip" from ec.europa.eu/esco/download (Last-Modified Tue, 16 Dec 2025 15:27:28 GMT), fetched 2026-10-25T05:45:48Z; zip sha256 `f9761b0b52be1828b38a3e5e0ae59a93a7b0ce358bc800f52f57a8b002adeb3e` (`ESCO.json`, `fetch_esco.py`).
- Linker: `sentence-transformers/all-mpnet-base-v2` at revision `e8c3b32edf5434bc2275fc9bab85f82640a19130`; an entry links to the concept of its most similar label if the cosine is at least 0.5; sensitivity: no cutoff, 0.7.
- Cells: job-ad skills and job-ad knowledge, documents with n < k at k = 3 and 5, ok outputs; each condition paired with `none` per (model, document, k), prose wordings averaged.
- Intervals: 95% percentile, 10000 bootstrap draws over document groups within set, seed 20261014; p = two-sided bootstrap p-value of the difference.

## Runs read

| run | model | outputs in the cells | entries checked | matcher labels |
|---|---|---|---|---|
| fs_bedrock-deepseek-v3.2_full | bedrock-deepseek-v3.2 | 2954 | 13827 | reused |
| fs_bedrock-gpt-oss-120b_full | bedrock-gpt-oss-120b | 2954 | 14590 | reused |
| fs_bedrock-gpt-oss-20b_full | bedrock-gpt-oss-20b | 2954 | 15772 | reused |
| fs_bedrock-kimi-k3_full | bedrock-kimi-k3 | 2954 | 11546 | reused |
| fs_bedrock-ministral-3-14b_full | bedrock-ministral-3-14b | 2954 | 15361 | reused |
| fs_bedrock-mistral-large-3_full | bedrock-mistral-large-3 | 2954 | 13131 | reused |
| fs_bedrock-qwen3-235b_full | bedrock-qwen3-235b | 2954 | 12429 | reused |
| fs_gemma-4-31b_full | gemma-4-31b | 3376 | 11893 | reused |
| fs_gpt-oss-20b_full | gpt-oss-20b | 3376 | 19620 | reused |
| fs_ministral-3-14b_full | ministral-3-14b | 3376 | 18053 | reused |
| fs_olmo-3.1-32b_full | olmo-3.1-32b | 3376 | 23252 | reused |
| fs_qwen3.5-0.8b_full | qwen3.5-0.8b | 3376 | 94310 | reused |
| fs_qwen3.5-27b_full | qwen3.5-27b | 3376 | 13072 | reused |
| fs_qwen3.5-2b_full | qwen3.5-2b | 3376 | 120805 | reused |
| fs_qwen3.5-9b_full | qwen3.5-9b | 3376 | 16871 | reused |
| fs_together-deepseek-v4.1-flash_full | together-deepseek-v4.1-flash | 3376 | 19138 | reused |
| fs_together-qwen3.5-9b_full | together-qwen3.5-9b | 3376 | 17898 | reused |
| a1_azure-gpt-6-luna_addendum1 | azure-gpt-6-luna | 1266 | 3086 | scored |
| a1_azure-gpt-6-luna_addendum1-enforced | azure-gpt-6-luna | 422 | 2134 | scored |
| a1_azure-gpt-6-sol_addendum1 | azure-gpt-6-sol | 1266 | 3247 | scored |
| a1_bedrock-grok-4.3_addendum1 | bedrock-grok-4.3 | 1266 | 3725 | scored |
| a1_bedrock-grok-4.3_addendum1-enforced | bedrock-grok-4.3 | 422 | 3227 | scored |

Entries checked: every parsed entry of every ok job-ad output lined up with the frozen scorer's entry table (same count, same word count, same placeholder and repeat calls).

## How much gets linked

| cutoff | true items linked | substantive entries linked (8 main models, cells) |
|---|---|---|
| 0.5 | 206 / 221 | 152553 / 160992 |
| none | 221 / 221 | 160992 / 160992 |
| 0.7 | 115 / 221 | 89601 / 160992 |

## Headline (8 main models pooled, both sets, cutoff 0.5)

- False ESCO concepts per ad: 6.73 [6.10, 7.37] under `none`, 7.70 [7.12, 8.31] under `min_k_shown`; difference +0.97 [+0.47, +1.50] (p 0.0004; 1688 pairs, 121 ads, 107 document groups).
- Ads with at least one false concept: 62.7 [58.6, 66.8]% vs 81.2 [78.1, 84.2]%.
- ESCO precision: 9.6 [7.9, 11.5]% vs 8.9 [7.5, 10.5]%; recall 59.1 [54.0, 64.3]% vs 62.5 [57.7, 67.4]%.
- Of the 20 concepts linked most often, not among the true items' top 20: 15 under `none`, 14 under `min_k_shown`.

## 1. 8 main models pooled, both sets, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 1688 | False ESCO concepts per ad | 6.73 [6.10, 7.37] | 4.03 [3.76, 4.31] | -2.70 [-3.23, -2.20] | < 0.0001 |
| `prose_up_to_k` | 1688 | Ads with at least one false concept (%) | 62.7 [58.6, 66.8] | 70.6 [67.3, 74.0] | +8.0 [+6.0, +10.0] | < 0.0001 |
| `prose_up_to_k` | 1688 | ESCO precision (%) | 9.6 [7.9, 11.5] | 14.7 [12.4, 17.0] | +5.1 [+4.0, +6.2] | < 0.0001 |
| `prose_up_to_k` | 1688 | ESCO recall (%) | 59.1 [54.0, 64.3] | 57.2 [52.3, 62.2] | -1.9 [-4.2, +0.5] | 0.1148 |
| `prose_up_to_k` | 1688 | Top-20 concepts not in the true items' top 20 | 15 [12, 18] | 13 [10, 17] | -2 [-4, +1] | 0.4766 |
| `prose_exactly_k` | 1688 | False ESCO concepts per ad | 6.73 [6.10, 7.37] | 3.97 [3.69, 4.26] | -2.76 [-3.31, -2.22] | < 0.0001 |
| `prose_exactly_k` | 1688 | Ads with at least one false concept (%) | 62.7 [58.6, 66.8] | 76.9 [73.6, 80.2] | +14.2 [+12.0, +16.4] | < 0.0001 |
| `prose_exactly_k` | 1688 | ESCO precision (%) | 9.6 [7.9, 11.5] | 14.8 [12.6, 17.3] | +5.3 [+4.1, +6.5] | < 0.0001 |
| `prose_exactly_k` | 1688 | ESCO recall (%) | 59.1 [54.0, 64.3] | 57.3 [52.7, 61.9] | -1.9 [-4.3, +0.6] | 0.1418 |
| `prose_exactly_k` | 1688 | Top-20 concepts not in the true items' top 20 | 15 [12, 18] | 14 [10, 17] | -1 [-4, +1] | 0.6366 |
| `max_k_shown` | 1688 | False ESCO concepts per ad | 6.73 [6.10, 7.37] | 5.41 [4.92, 5.95] | -1.32 [-1.72, -0.91] | < 0.0001 |
| `max_k_shown` | 1688 | Ads with at least one false concept (%) | 62.7 [58.6, 66.8] | 64.9 [61.1, 68.8] | +2.3 [+0.5, +4.1] | 0.0110 |
| `max_k_shown` | 1688 | ESCO precision (%) | 9.6 [7.9, 11.5] | 11.4 [9.5, 13.6] | +1.8 [+1.1, +2.6] | < 0.0001 |
| `max_k_shown` | 1688 | ESCO recall (%) | 59.1 [54.0, 64.3] | 57.8 [52.8, 62.8] | -1.3 [-3.0, +0.5] | 0.1410 |
| `max_k_shown` | 1688 | Top-20 concepts not in the true items' top 20 | 15 [12, 18] | 14 [11, 17] | -1 [-2, +1] | 1.0000 |
| `min_k_shown` | 1688 | False ESCO concepts per ad | 6.73 [6.10, 7.37] | 7.70 [7.12, 8.31] | +0.97 [+0.47, +1.50] | 0.0004 |
| `min_k_shown` | 1688 | Ads with at least one false concept (%) | 62.7 [58.6, 66.8] | 81.2 [78.1, 84.2] | +18.5 [+16.1, +21.1] | < 0.0001 |
| `min_k_shown` | 1688 | ESCO precision (%) | 9.6 [7.9, 11.5] | 8.9 [7.5, 10.5] | -0.7 [-1.5, +0.1] | 0.0738 |
| `min_k_shown` | 1688 | ESCO recall (%) | 59.1 [54.0, 64.3] | 62.5 [57.7, 67.4] | +3.4 [+1.2, +5.7] | 0.0020 |
| `min_k_shown` | 1688 | Top-20 concepts not in the true items' top 20 | 15 [12, 18] | 14 [12, 18] | -1 [-1, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 1688 | False ESCO concepts per ad | 6.73 [6.10, 7.37] | 4.89 [4.43, 5.36] | -1.84 [-2.42, -1.28] | < 0.0001 |
| `min_k_shown_fewer_ok` | 1688 | Ads with at least one false concept (%) | 62.7 [58.6, 66.8] | 54.4 [50.5, 58.7] | -8.2 [-10.8, -5.7] | < 0.0001 |
| `min_k_shown_fewer_ok` | 1688 | ESCO precision (%) | 9.6 [7.9, 11.5] | 11.4 [9.4, 13.5] | +1.8 [+0.8, +2.8] | 0.0006 |
| `min_k_shown_fewer_ok` | 1688 | ESCO recall (%) | 59.1 [54.0, 64.3] | 51.8 [47.3, 56.3] | -7.3 [-9.7, -5.0] | < 0.0001 |
| `min_k_shown_fewer_ok` | 1688 | Top-20 concepts not in the true items' top 20 | 15 [12, 18] | 14 [11, 17] | -1 [-3, +1] | 0.9296 |
| `min_k_enforced` | 1688 | False ESCO concepts per ad | 6.73 [6.10, 7.37] | 5.30 [4.97, 5.65] | -1.43 [-2.01, -0.87] | < 0.0001 |
| `min_k_enforced` | 1688 | Ads with at least one false concept (%) | 62.7 [58.6, 66.8] | 98.3 [97.4, 99.1] | +35.6 [+31.7, +39.5] | < 0.0001 |
| `min_k_enforced` | 1688 | ESCO precision (%) | 9.6 [7.9, 11.5] | 13.2 [11.1, 15.4] | +3.6 [+2.6, +4.7] | < 0.0001 |
| `min_k_enforced` | 1688 | ESCO recall (%) | 59.1 [54.0, 64.3] | 66.7 [61.8, 71.6] | +7.6 [+5.0, +10.3] | < 0.0001 |
| `min_k_enforced` | 1688 | Top-20 concepts not in the true items' top 20 | 15 [12, 18] | 14 [11, 17] | -1 [-3, +2] | 1.0000 |
| `min_k_escape` | 1688 | False ESCO concepts per ad | 6.73 [6.10, 7.37] | 3.37 [3.11, 3.64] | -3.36 [-3.96, -2.81] | < 0.0001 |
| `min_k_escape` | 1688 | Ads with at least one false concept (%) | 62.7 [58.6, 66.8] | 58.3 [53.8, 63.0] | -4.4 [-7.7, -1.1] | 0.0080 |
| `min_k_escape` | 1688 | ESCO precision (%) | 9.6 [7.9, 11.5] | 16.3 [14.0, 18.7] | +6.7 [+5.5, +7.9] | < 0.0001 |
| `min_k_escape` | 1688 | ESCO recall (%) | 59.1 [54.0, 64.3] | 54.3 [49.5, 58.9] | -4.9 [-7.6, -2.2] | 0.0004 |
| `min_k_escape` | 1688 | Top-20 concepts not in the true items' top 20 | 15 [12, 18] | 13 [10, 16] | -2 [-5, +1] | 0.3076 |

Top 20 concepts of the `min_k_shown` outputs: English; computer engineering; Java (computer programming); Agile development; cloud technologies; project commissioning; team building; cooperate with colleagues; DevOps; seek innovation in current practices; Python (computer programming); communication; react to events in time-critical environments; JavaScript; ICT project management methodologies; teach communication methods; manage ICT virtualisation environments; quality assurance methodologies; statistics; develop strategy to solve problems

Top 20 concepts of the true items of the same ads: English; teach communication methods; SAP Data Services; German; computer engineering; recruit members; design cloud architecture; Danish; perform scientific research; computer science; react to events in time-critical environments; web services; perform business research; systems development life-cycle; Ruby (computer programming); solve technical problems; communication; Java (computer programming); body language; manage budgets

## 2. 8 main models pooled, job-ad skills, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 872 | False ESCO concepts per ad | 5.51 [4.73, 6.34] | 3.84 [3.46, 4.24] | -1.66 [-2.34, -1.07] | < 0.0001 |
| `prose_up_to_k` | 872 | Ads with at least one false concept (%) | 72.5 [66.5, 78.5] | 82.6 [78.3, 86.9] | +10.2 [+7.2, +13.5] | < 0.0001 |
| `prose_up_to_k` | 872 | ESCO precision (%) | 9.0 [6.6, 11.9] | 11.3 [8.5, 14.5] | +2.2 [+0.9, +3.6] | 0.0004 |
| `prose_up_to_k` | 872 | ESCO recall (%) | 44.9 [38.4, 51.8] | 40.0 [33.8, 46.6] | -4.9 [-8.6, -1.3] | 0.0070 |
| `prose_up_to_k` | 872 | Top-20 concepts not in the true items' top 20 | 17 [13, 19] | 17 [13, 19] | +0 [-3, +2] | 1.0000 |
| `prose_exactly_k` | 872 | False ESCO concepts per ad | 5.51 [4.73, 6.34] | 3.93 [3.57, 4.29] | -1.58 [-2.27, -0.96] | < 0.0001 |
| `prose_exactly_k` | 872 | Ads with at least one false concept (%) | 72.5 [66.5, 78.5] | 87.8 [83.8, 91.4] | +15.3 [+12.0, +18.8] | < 0.0001 |
| `prose_exactly_k` | 872 | ESCO precision (%) | 9.0 [6.6, 11.9] | 11.5 [8.7, 14.7] | +2.5 [+1.2, +3.8] | < 0.0001 |
| `prose_exactly_k` | 872 | ESCO recall (%) | 44.9 [38.4, 51.8] | 41.8 [35.9, 48.3] | -3.1 [-6.8, +0.6] | 0.0930 |
| `prose_exactly_k` | 872 | Top-20 concepts not in the true items' top 20 | 17 [13, 19] | 17 [13, 19] | +0 [-3, +2] | 1.0000 |
| `max_k_shown` | 872 | False ESCO concepts per ad | 5.51 [4.73, 6.34] | 4.75 [4.10, 5.48] | -0.76 [-1.14, -0.35] | 0.0006 |
| `max_k_shown` | 872 | Ads with at least one false concept (%) | 72.5 [66.5, 78.5] | 75.8 [70.4, 81.0] | +3.3 [+0.9, +6.0] | 0.0056 |
| `max_k_shown` | 872 | ESCO precision (%) | 9.0 [6.6, 11.9] | 9.7 [7.0, 13.0] | +0.6 [-0.2, +1.6] | 0.1464 |
| `max_k_shown` | 872 | ESCO recall (%) | 44.9 [38.4, 51.8] | 41.8 [35.6, 48.4] | -3.1 [-5.8, -0.4] | 0.0246 |
| `max_k_shown` | 872 | Top-20 concepts not in the true items' top 20 | 17 [13, 19] | 17 [13, 19] | +0 [-2, +1] | 1.0000 |
| `min_k_shown` | 872 | False ESCO concepts per ad | 5.51 [4.73, 6.34] | 6.81 [6.03, 7.65] | +1.30 [+0.78, +1.88] | < 0.0001 |
| `min_k_shown` | 872 | Ads with at least one false concept (%) | 72.5 [66.5, 78.5] | 87.2 [82.8, 90.9] | +14.7 [+10.8, +18.8] | < 0.0001 |
| `min_k_shown` | 872 | ESCO precision (%) | 9.0 [6.6, 11.9] | 8.2 [6.2, 10.5] | -0.9 [-1.9, -0.1] | 0.0314 |
| `min_k_shown` | 872 | ESCO recall (%) | 44.9 [38.4, 51.8] | 49.8 [43.4, 56.4] | +4.9 [+2.3, +7.7] | 0.0002 |
| `min_k_shown` | 872 | Top-20 concepts not in the true items' top 20 | 17 [13, 19] | 17 [13, 19] | +0 [-2, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 872 | False ESCO concepts per ad | 5.51 [4.73, 6.34] | 4.67 [4.04, 5.32] | -0.84 [-1.43, -0.27] | 0.0056 |
| `min_k_shown_fewer_ok` | 872 | Ads with at least one false concept (%) | 72.5 [66.5, 78.5] | 60.6 [54.7, 66.4] | -11.9 [-15.7, -8.4] | < 0.0001 |
| `min_k_shown_fewer_ok` | 872 | ESCO precision (%) | 9.0 [6.6, 11.9] | 9.0 [6.6, 11.9] | -0.1 [-1.1, +1.0] | 0.9076 |
| `min_k_shown_fewer_ok` | 872 | ESCO recall (%) | 44.9 [38.4, 51.8] | 37.8 [32.4, 43.4] | -7.1 [-10.6, -3.9] | 0.0004 |
| `min_k_shown_fewer_ok` | 872 | Top-20 concepts not in the true items' top 20 | 17 [13, 19] | 17 [13, 19] | +0 [-3, +2] | 1.0000 |
| `min_k_enforced` | 872 | False ESCO concepts per ad | 5.51 [4.73, 6.34] | 5.15 [4.72, 5.61] | -0.36 [-1.03, +0.23] | 0.2584 |
| `min_k_enforced` | 872 | Ads with at least one false concept (%) | 72.5 [66.5, 78.5] | 99.0 [98.2, 99.6] | +26.5 [+20.7, +32.4] | < 0.0001 |
| `min_k_enforced` | 872 | ESCO precision (%) | 9.0 [6.6, 11.9] | 11.1 [8.5, 13.9] | +2.0 [+0.8, +3.2] | 0.0006 |
| `min_k_enforced` | 872 | ESCO recall (%) | 44.9 [38.4, 51.8] | 52.6 [46.0, 59.6] | +7.7 [+4.1, +11.6] | < 0.0001 |
| `min_k_enforced` | 872 | Top-20 concepts not in the true items' top 20 | 17 [13, 19] | 16 [13, 19] | -1 [-3, +2] | 1.0000 |
| `min_k_escape` | 872 | False ESCO concepts per ad | 5.51 [4.73, 6.34] | 3.53 [3.13, 3.96] | -1.97 [-2.74, -1.29] | < 0.0001 |
| `min_k_escape` | 872 | Ads with at least one false concept (%) | 72.5 [66.5, 78.5] | 66.7 [60.6, 72.9] | -5.7 [-9.9, -1.4] | 0.0080 |
| `min_k_escape` | 872 | ESCO precision (%) | 9.0 [6.6, 11.9] | 12.5 [9.6, 15.8] | +3.5 [+2.0, +5.0] | < 0.0001 |
| `min_k_escape` | 872 | ESCO recall (%) | 44.9 [38.4, 51.8] | 41.4 [34.8, 48.3] | -3.5 [-6.5, -0.5] | 0.0256 |
| `min_k_escape` | 872 | Top-20 concepts not in the true items' top 20 | 17 [13, 19] | 16 [13, 19] | -1 [-3, +2] | 0.9910 |

## 3. 8 main models pooled, job-ad knowledge, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 816 | False ESCO concepts per ad | 8.04 [7.07, 9.03] | 4.22 [3.84, 4.64] | -3.82 [-4.66, -2.98] | < 0.0001 |
| `prose_up_to_k` | 816 | Ads with at least one false concept (%) | 52.2 [46.9, 57.7] | 57.8 [53.3, 62.4] | +5.6 [+3.2, +8.0] | 0.0002 |
| `prose_up_to_k` | 816 | ESCO precision (%) | 10.0 [7.7, 12.6] | 17.7 [14.2, 21.4] | +7.7 [+6.0, +9.5] | < 0.0001 |
| `prose_up_to_k` | 816 | ESCO recall (%) | 74.6 [68.3, 80.7] | 76.0 [70.4, 81.3] | +1.4 [-1.6, +4.7] | 0.3744 |
| `prose_up_to_k` | 816 | Top-20 concepts not in the true items' top 20 | 18 [11, 18] | 13 [6, 14] | -5 [-9, -1] | 0.0106 |
| `prose_exactly_k` | 816 | False ESCO concepts per ad | 8.04 [7.07, 9.03] | 4.01 [3.61, 4.44] | -4.02 [-4.93, -3.13] | < 0.0001 |
| `prose_exactly_k` | 816 | Ads with at least one false concept (%) | 52.2 [46.9, 57.7] | 65.2 [60.1, 70.5] | +13.0 [+10.2, +15.7] | < 0.0001 |
| `prose_exactly_k` | 816 | ESCO precision (%) | 10.0 [7.7, 12.6] | 18.1 [14.4, 22.1] | +8.1 [+6.1, +10.2] | < 0.0001 |
| `prose_exactly_k` | 816 | ESCO recall (%) | 74.6 [68.3, 80.7] | 74.1 [68.7, 79.2] | -0.5 [-3.5, +2.6] | 0.7370 |
| `prose_exactly_k` | 816 | Top-20 concepts not in the true items' top 20 | 18 [11, 18] | 14 [7, 14] | -4 [-8, -1] | 0.0174 |
| `max_k_shown` | 816 | False ESCO concepts per ad | 8.04 [7.07, 9.03] | 6.12 [5.42, 6.84] | -1.92 [-2.67, -1.17] | < 0.0001 |
| `max_k_shown` | 816 | Ads with at least one false concept (%) | 52.2 [46.9, 57.7] | 53.3 [47.7, 59.0] | +1.1 [-1.4, +3.6] | 0.4208 |
| `max_k_shown` | 816 | ESCO precision (%) | 10.0 [7.7, 12.6] | 12.8 [10.1, 15.8] | +2.8 [+1.7, +4.0] | < 0.0001 |
| `max_k_shown` | 816 | ESCO recall (%) | 74.6 [68.3, 80.7] | 75.2 [69.4, 81.0] | +0.6 [-1.4, +2.9] | 0.6052 |
| `max_k_shown` | 816 | Top-20 concepts not in the true items' top 20 | 18 [11, 18] | 18 [9, 16] | +0 [-5, +0] | 0.1788 |
| `min_k_shown` | 816 | False ESCO concepts per ad | 8.04 [7.07, 9.03] | 8.66 [7.82, 9.51] | +0.62 [-0.28, +1.53] | 0.1768 |
| `min_k_shown` | 816 | Ads with at least one false concept (%) | 52.2 [46.9, 57.7] | 74.9 [70.4, 79.3] | +22.7 [+19.6, +25.7] | < 0.0001 |
| `min_k_shown` | 816 | ESCO precision (%) | 10.0 [7.7, 12.6] | 9.6 [7.5, 11.8] | -0.4 [-1.7, +0.7] | 0.4498 |
| `min_k_shown` | 816 | ESCO recall (%) | 74.6 [68.3, 80.7] | 76.4 [70.4, 82.2] | +1.8 [-1.8, +5.8] | 0.3504 |
| `min_k_shown` | 816 | Top-20 concepts not in the true items' top 20 | 18 [11, 18] | 18 [11, 18] | +0 [-2, +3] | 1.0000 |
| `min_k_shown_fewer_ok` | 816 | False ESCO concepts per ad | 8.04 [7.07, 9.03] | 5.12 [4.49, 5.79] | -2.92 [-3.87, -1.97] | < 0.0001 |
| `min_k_shown_fewer_ok` | 816 | Ads with at least one false concept (%) | 52.2 [46.9, 57.7] | 47.9 [42.7, 53.5] | -4.3 [-7.5, -1.2] | 0.0096 |
| `min_k_shown_fewer_ok` | 816 | ESCO precision (%) | 10.0 [7.7, 12.6] | 13.6 [10.5, 16.9] | +3.6 [+1.9, +5.4] | < 0.0001 |
| `min_k_shown_fewer_ok` | 816 | ESCO recall (%) | 74.6 [68.3, 80.7] | 67.1 [60.8, 73.0] | -7.5 [-10.9, -4.3] | < 0.0001 |
| `min_k_shown_fewer_ok` | 816 | Top-20 concepts not in the true items' top 20 | 18 [11, 18] | 15 [9, 16] | -3 [-6, +0] | 0.1794 |
| `min_k_enforced` | 816 | False ESCO concepts per ad | 8.04 [7.07, 9.03] | 5.46 [4.97, 6.03] | -2.57 [-3.55, -1.59] | < 0.0001 |
| `min_k_enforced` | 816 | Ads with at least one false concept (%) | 52.2 [46.9, 57.7] | 97.5 [95.9, 99.0] | +45.3 [+40.1, +50.5] | < 0.0001 |
| `min_k_enforced` | 816 | ESCO precision (%) | 10.0 [7.7, 12.6] | 15.2 [11.9, 18.7] | +5.2 [+3.4, +7.2] | < 0.0001 |
| `min_k_enforced` | 816 | ESCO recall (%) | 74.6 [68.3, 80.7] | 82.1 [76.7, 87.1] | +7.5 [+3.6, +11.8] | < 0.0001 |
| `min_k_enforced` | 816 | Top-20 concepts not in the true items' top 20 | 18 [11, 18] | 14 [10, 17] | -4 [-5, +2] | 0.6464 |
| `min_k_escape` | 816 | False ESCO concepts per ad | 8.04 [7.07, 9.03] | 3.19 [2.83, 3.56] | -4.84 [-5.71, -4.00] | < 0.0001 |
| `min_k_escape` | 816 | Ads with at least one false concept (%) | 52.2 [46.9, 57.7] | 49.3 [42.9, 55.4] | -2.9 [-7.9, +1.8] | 0.2378 |
| `min_k_escape` | 816 | ESCO precision (%) | 10.0 [7.7, 12.6] | 20.4 [16.7, 24.0] | +10.4 [+8.4, +12.3] | < 0.0001 |
| `min_k_escape` | 816 | ESCO recall (%) | 74.6 [68.3, 80.7] | 68.2 [62.6, 73.7] | -6.4 [-10.5, -2.0] | 0.0042 |
| `min_k_escape` | 816 | Top-20 concepts not in the true items' top 20 | 18 [11, 18] | 12 [7, 14] | -6 [-8, -1] | 0.0262 |

## 4. Qwen3.5-0.8B (main model alone; not registered), both sets, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 10.82 [9.38, 12.35] | 8.65 [7.89, 9.49] | -2.17 [-3.32, -1.07] | < 0.0001 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 90.0 [84.3, 95.0] | 99.6 [99.1, 100.0] | +9.6 [+4.6, +15.3] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 5.0 [3.8, 6.3] | 6.1 [4.8, 7.5] | +1.1 [+0.4, +1.9] | 0.0036 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 47.1 [39.5, 55.1] | 46.5 [40.2, 53.1] | -0.5 [-6.2, +5.6] | 0.8422 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 14 [14, 19] | 15 [14, 19] | +1 [-2, +2] | 1.0000 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 10.82 [9.38, 12.35] | 7.98 [7.18, 8.90] | -2.84 [-4.03, -1.71] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 90.0 [84.3, 95.0] | 96.4 [94.8, 97.8] | +6.4 [+2.2, +11.0] | 0.0016 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 5.0 [3.8, 6.3] | 6.7 [5.2, 8.3] | +1.7 [+0.8, +2.6] | 0.0002 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 47.1 [39.5, 55.1] | 47.2 [40.8, 53.7] | +0.2 [-6.1, +6.6] | 0.9838 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 14 [14, 19] | 14 [13, 19] | +0 [-3, +1] | 1.0000 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 10.82 [9.38, 12.35] | 10.97 [9.51, 12.53] | +0.15 [-0.73, +1.05] | 0.7372 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 90.0 [84.3, 95.0] | 89.6 [84.1, 94.5] | -0.5 [-2.8, +2.1] | 0.8046 |
| `max_k_shown` | 211 | ESCO precision (%) | 5.0 [3.8, 6.3] | 5.0 [3.9, 6.3] | +0.0 [-0.5, +0.5] | 0.9646 |
| `max_k_shown` | 211 | ESCO recall (%) | 47.1 [39.5, 55.1] | 47.8 [40.7, 55.4] | +0.8 [-2.0, +3.8] | 0.7112 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 14 [14, 19] | 14 [14, 19] | +0 [-2, +1] | 1.0000 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 10.82 [9.38, 12.35] | 10.59 [9.01, 12.32] | -0.23 [-1.33, +0.87] | 0.6892 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 90.0 [84.3, 95.0] | 77.7 [71.6, 83.4] | -12.3 [-17.8, -7.1] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 5.0 [3.8, 6.3] | 5.0 [3.8, 6.4] | +0.0 [-0.7, +0.8] | 0.9714 |
| `min_k_shown` | 211 | ESCO recall (%) | 47.1 [39.5, 55.1] | 46.3 [38.4, 54.2] | -0.8 [-6.2, +5.1] | 0.8080 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 14 [14, 19] | 15 [14, 19] | +1 [-2, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 10.82 [9.38, 12.35] | 11.27 [10.08, 12.55] | +0.45 [-0.64, +1.62] | 0.4324 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 90.0 [84.3, 95.0] | 99.1 [97.6, 100.0] | +9.0 [+3.7, +15.0] | 0.0006 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 5.0 [3.8, 6.3] | 5.1 [3.9, 6.5] | +0.1 [-0.7, +0.9] | 0.7922 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 47.1 [39.5, 55.1] | 50.2 [42.4, 58.0] | +3.1 [-3.8, +10.4] | 0.4122 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 14 [14, 19] | 15 [13, 19] | +1 [-2, +1] | 1.0000 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 10.82 [9.38, 12.35] | 9.37 [8.52, 10.36] | -1.45 [-2.87, -0.06] | 0.0428 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 90.0 [84.3, 95.0] | 99.1 [97.0, 100.0] | +9.0 [+3.5, +15.1] | 0.0022 |
| `min_k_enforced` | 211 | ESCO precision (%) | 5.0 [3.8, 6.3] | 5.4 [4.1, 6.8] | +0.5 [-0.6, +1.4] | 0.4002 |
| `min_k_enforced` | 211 | ESCO recall (%) | 47.1 [39.5, 55.1] | 44.7 [36.4, 52.9] | -2.4 [-10.5, +5.3] | 0.5988 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 14 [14, 19] | 15 [14, 19] | +1 [-2, +3] | 1.0000 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 10.82 [9.38, 12.35] | 8.92 [8.05, 9.91] | -1.90 [-3.29, -0.53] | 0.0036 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 90.0 [84.3, 95.0] | 99.1 [97.0, 100.0] | +9.0 [+3.5, +15.1] | 0.0022 |
| `min_k_escape` | 211 | ESCO precision (%) | 5.0 [3.8, 6.3] | 6.3 [4.9, 7.7] | +1.3 [+0.3, +2.3] | 0.0150 |
| `min_k_escape` | 211 | ESCO recall (%) | 47.1 [39.5, 55.1] | 49.4 [41.5, 57.3] | +2.4 [-5.8, +10.4] | 0.6040 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 14 [14, 19] | 16 [14, 19] | +2 [-2, +3] | 1.0000 |

Top 20 concepts of the `min_k_shown` outputs: Java (computer programming); English; team building; communication; Python (computer programming); computer engineering; JavaScript; application process; manage ICT virtualisation environments; cloud technologies; project commissioning; react to events in time-critical environments; ICT project management methodologies; organisational structure; DevOps; cooperate with colleagues; learning management systems; develop strategy to solve problems; statistics; query languages

Top 20 concepts of the true items of the same ads: English; teach communication methods; SAP Data Services; German; computer engineering; recruit members; design cloud architecture; Danish; perform scientific research; computer science; react to events in time-critical environments; web services; perform business research; systems development life-cycle; Ruby (computer programming); solve technical problems; communication; Java (computer programming); body language; manage budgets

## 5. Qwen3.5-0.8B (main model alone; not registered), job-ad skills, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 109 | False ESCO concepts per ad | 8.84 [6.88, 11.06] | 6.22 [5.43, 7.10] | -2.62 [-4.59, -0.92] | 0.0006 |
| `prose_up_to_k` | 109 | Ads with at least one false concept (%) | 80.7 [70.4, 90.2] | 99.8 [99.4, 100.0] | +19.1 [+9.7, +29.4] | < 0.0001 |
| `prose_up_to_k` | 109 | ESCO precision (%) | 3.1 [1.7, 5.0] | 3.9 [2.4, 5.8] | +0.8 [-0.2, +1.9] | 0.1394 |
| `prose_up_to_k` | 109 | ESCO recall (%) | 23.3 [13.6, 33.8] | 20.9 [13.6, 28.8] | -2.4 [-9.0, +4.1] | 0.4772 |
| `prose_up_to_k` | 109 | Top-20 concepts not in the true items' top 20 | 18 [16, 20] | 18 [17, 20] | +0 [-2, +3] | 1.0000 |
| `prose_exactly_k` | 109 | False ESCO concepts per ad | 8.84 [6.88, 11.06] | 5.04 [4.37, 5.83] | -3.80 [-5.89, -1.94] | < 0.0001 |
| `prose_exactly_k` | 109 | Ads with at least one false concept (%) | 80.7 [70.4, 90.2] | 93.2 [90.2, 95.9] | +12.5 [+4.6, +21.1] | 0.0018 |
| `prose_exactly_k` | 109 | ESCO precision (%) | 3.1 [1.7, 5.0] | 5.1 [3.2, 7.4] | +2.0 [+0.6, +3.5] | 0.0040 |
| `prose_exactly_k` | 109 | ESCO recall (%) | 23.3 [13.6, 33.8] | 22.1 [15.3, 29.5] | -1.2 [-8.1, +5.5] | 0.7550 |
| `prose_exactly_k` | 109 | Top-20 concepts not in the true items' top 20 | 18 [16, 20] | 18 [16, 20] | +0 [-2, +2] | 1.0000 |
| `max_k_shown` | 109 | False ESCO concepts per ad | 8.84 [6.88, 11.06] | 8.84 [6.96, 10.90] | +0.00 [-1.26, +1.13] | 0.9576 |
| `max_k_shown` | 109 | Ads with at least one false concept (%) | 80.7 [70.4, 90.2] | 79.8 [69.6, 89.2] | -0.9 [-5.5, +4.3] | 0.8196 |
| `max_k_shown` | 109 | ESCO precision (%) | 3.1 [1.7, 5.0] | 3.1 [1.8, 4.9] | +0.0 [-0.7, +0.7] | 0.9816 |
| `max_k_shown` | 109 | ESCO recall (%) | 23.3 [13.6, 33.8] | 23.3 [14.4, 32.9] | +0.0 [-4.0, +4.4] | 1.0000 |
| `max_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 18 [16, 20] | 19 [16, 20] | +1 [-1, +2] | 1.0000 |
| `min_k_shown` | 109 | False ESCO concepts per ad | 8.84 [6.88, 11.06] | 7.56 [5.30, 10.25] | -1.28 [-2.92, +0.37] | 0.1278 |
| `min_k_shown` | 109 | Ads with at least one false concept (%) | 80.7 [70.4, 90.2] | 56.9 [45.9, 67.9] | -23.9 [-34.3, -13.6] | < 0.0001 |
| `min_k_shown` | 109 | ESCO precision (%) | 3.1 [1.7, 5.0] | 3.6 [2.0, 5.9] | +0.5 [-0.3, +1.6] | 0.2572 |
| `min_k_shown` | 109 | ESCO recall (%) | 23.3 [13.6, 33.8] | 23.3 [14.3, 33.0] | +0.0 [-6.2, +6.4] | 1.0000 |
| `min_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 18 [16, 20] | 18 [16, 20] | +0 [-2, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 109 | False ESCO concepts per ad | 8.84 [6.88, 11.06] | 10.52 [8.84, 12.27] | +1.68 [+0.06, +3.35] | 0.0410 |
| `min_k_shown_fewer_ok` | 109 | Ads with at least one false concept (%) | 80.7 [70.4, 90.2] | 99.1 [97.1, 100.0] | +18.3 [+8.5, +29.0] | 0.0006 |
| `min_k_shown_fewer_ok` | 109 | ESCO precision (%) | 3.1 [1.7, 5.0] | 3.0 [1.7, 4.7] | -0.1 [-1.3, +1.1] | 0.8804 |
| `min_k_shown_fewer_ok` | 109 | ESCO recall (%) | 23.3 [13.6, 33.8] | 27.1 [17.4, 37.2] | +3.8 [-4.7, +12.9] | 0.4560 |
| `min_k_shown_fewer_ok` | 109 | Top-20 concepts not in the true items' top 20 | 18 [16, 20] | 17 [16, 20] | -1 [-2, +2] | 1.0000 |
| `min_k_enforced` | 109 | False ESCO concepts per ad | 8.84 [6.88, 11.06] | 8.71 [7.46, 10.18] | -0.14 [-2.14, +1.74] | 0.9028 |
| `min_k_enforced` | 109 | Ads with at least one false concept (%) | 80.7 [70.4, 90.2] | 100.0 [100.0, 100.0] | +19.3 [+9.8, +29.6] | < 0.0001 |
| `min_k_enforced` | 109 | ESCO precision (%) | 3.1 [1.7, 5.0] | 4.3 [2.8, 6.1] | +1.2 [-0.3, +2.6] | 0.1030 |
| `min_k_enforced` | 109 | ESCO recall (%) | 23.3 [13.6, 33.8] | 32.3 [22.7, 42.4] | +9.0 [-0.8, +19.3] | 0.0844 |
| `min_k_enforced` | 109 | Top-20 concepts not in the true items' top 20 | 18 [16, 20] | 19 [16, 20] | +1 [-2, +3] | 1.0000 |
| `min_k_escape` | 109 | False ESCO concepts per ad | 8.84 [6.88, 11.06] | 7.68 [6.56, 9.06] | -1.17 [-3.25, +0.74] | 0.2482 |
| `min_k_escape` | 109 | Ads with at least one false concept (%) | 80.7 [70.4, 90.2] | 100.0 [100.0, 100.0] | +19.3 [+9.8, +29.6] | < 0.0001 |
| `min_k_escape` | 109 | ESCO precision (%) | 3.1 [1.7, 5.0] | 5.2 [3.4, 7.3] | +2.1 [+0.6, +3.6] | 0.0072 |
| `min_k_escape` | 109 | ESCO recall (%) | 23.3 [13.6, 33.8] | 34.6 [24.6, 45.3] | +11.3 [+1.3, +22.1] | 0.0356 |
| `min_k_escape` | 109 | Top-20 concepts not in the true items' top 20 | 18 [16, 20] | 19 [16, 20] | +1 [-2, +3] | 1.0000 |

## 6. Qwen3.5-0.8B (main model alone; not registered), job-ad knowledge, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 102 | False ESCO concepts per ad | 12.93 [10.90, 15.28] | 11.24 [9.97, 12.72] | -1.70 [-3.07, -0.34] | 0.0120 |
| `prose_up_to_k` | 102 | Ads with at least one false concept (%) | 100.0 [100.0, 100.0] | 99.4 [98.4, 100.0] | -0.6 [-1.6, +0.0] | 0.2740 |
| `prose_up_to_k` | 102 | ESCO precision (%) | 6.3 [4.6, 8.3] | 7.3 [5.5, 9.4] | +1.0 [+0.1, +2.0] | 0.0362 |
| `prose_up_to_k` | 102 | ESCO recall (%) | 73.0 [61.2, 83.7] | 74.4 [66.1, 82.3] | +1.5 [-8.4, +12.2] | 0.8238 |
| `prose_up_to_k` | 102 | Top-20 concepts not in the true items' top 20 | 19 [17, 20] | 19 [15, 19] | +0 [-4, +1] | 0.5938 |
| `prose_exactly_k` | 102 | False ESCO concepts per ad | 12.93 [10.90, 15.28] | 11.12 [9.71, 12.73] | -1.81 [-3.22, -0.43] | 0.0092 |
| `prose_exactly_k` | 102 | Ads with at least one false concept (%) | 100.0 [100.0, 100.0] | 99.8 [99.4, 100.0] | -0.2 [-0.6, +0.0] | 0.7458 |
| `prose_exactly_k` | 102 | ESCO precision (%) | 6.3 [4.6, 8.3] | 7.4 [5.5, 9.6] | +1.1 [+0.0, +2.2] | 0.0406 |
| `prose_exactly_k` | 102 | ESCO recall (%) | 73.0 [61.2, 83.7] | 74.6 [65.1, 83.4] | +1.6 [-9.6, +13.5] | 0.8108 |
| `prose_exactly_k` | 102 | Top-20 concepts not in the true items' top 20 | 19 [17, 20] | 19 [14, 19] | +0 [-4, +0] | 0.5216 |
| `max_k_shown` | 102 | False ESCO concepts per ad | 12.93 [10.90, 15.28] | 13.25 [11.13, 15.72] | +0.31 [-1.03, +1.74] | 0.6856 |
| `max_k_shown` | 102 | Ads with at least one false concept (%) | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | +0.0 [+0.0, +0.0] | 1.0000 |
| `max_k_shown` | 102 | ESCO precision (%) | 6.3 [4.6, 8.3] | 6.3 [4.7, 8.2] | -0.0 [-0.7, +0.7] | 0.9974 |
| `max_k_shown` | 102 | ESCO recall (%) | 73.0 [61.2, 83.7] | 74.6 [63.8, 84.7] | +1.6 [-1.8, +6.1] | 0.5790 |
| `max_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 19 [17, 20] | 19 [16, 20] | +0 [-2, +1] | 1.0000 |
| `min_k_shown` | 102 | False ESCO concepts per ad | 12.93 [10.90, 15.28] | 13.83 [11.77, 16.24] | +0.90 [-0.50, +2.40] | 0.2248 |
| `min_k_shown` | 102 | Ads with at least one false concept (%) | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | +0.0 [+0.0, +0.0] | 1.0000 |
| `min_k_shown` | 102 | ESCO precision (%) | 6.3 [4.6, 8.3] | 5.8 [4.2, 7.7] | -0.5 [-1.6, +0.5] | 0.3328 |
| `min_k_shown` | 102 | ESCO recall (%) | 73.0 [61.2, 83.7] | 71.3 [59.2, 82.5] | -1.6 [-10.7, +8.5] | 0.7666 |
| `min_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 19 [17, 20] | 18 [16, 20] | -1 [-2, +1] | 1.0000 |
| `min_k_shown_fewer_ok` | 102 | False ESCO concepts per ad | 12.93 [10.90, 15.28] | 12.08 [10.39, 14.02] | -0.85 [-2.23, +0.50] | 0.2216 |
| `min_k_shown_fewer_ok` | 102 | Ads with at least one false concept (%) | 100.0 [100.0, 100.0] | 99.0 [97.0, 100.0] | -1.0 [-3.0, +0.0] | 0.7566 |
| `min_k_shown_fewer_ok` | 102 | ESCO precision (%) | 6.3 [4.6, 8.3] | 6.9 [5.0, 9.2] | +0.6 [-0.4, +1.7] | 0.2414 |
| `min_k_shown_fewer_ok` | 102 | ESCO recall (%) | 73.0 [61.2, 83.7] | 75.4 [63.9, 85.7] | +2.5 [-8.0, +14.0] | 0.7444 |
| `min_k_shown_fewer_ok` | 102 | Top-20 concepts not in the true items' top 20 | 19 [17, 20] | 18 [15, 19] | -1 [-3, +0] | 0.9390 |
| `min_k_enforced` | 102 | False ESCO concepts per ad | 12.93 [10.90, 15.28] | 10.09 [8.84, 11.43] | -2.84 [-4.91, -0.83] | 0.0054 |
| `min_k_enforced` | 102 | Ads with at least one false concept (%) | 100.0 [100.0, 100.0] | 98.0 [93.9, 100.0] | -2.0 [-6.1, +0.0] | 0.7298 |
| `min_k_enforced` | 102 | ESCO precision (%) | 6.3 [4.6, 8.3] | 6.5 [4.5, 8.6] | +0.1 [-1.4, +1.5] | 0.8608 |
| `min_k_enforced` | 102 | ESCO recall (%) | 73.0 [61.2, 83.7] | 58.2 [45.6, 70.8] | -14.8 [-26.6, -4.1] | 0.0062 |
| `min_k_enforced` | 102 | Top-20 concepts not in the true items' top 20 | 19 [17, 20] | 17 [15, 20] | -2 [-4, +1] | 0.7212 |
| `min_k_escape` | 102 | False ESCO concepts per ad | 12.93 [10.90, 15.28] | 10.25 [8.95, 11.69] | -2.69 [-4.65, -0.78] | 0.0046 |
| `min_k_escape` | 102 | Ads with at least one false concept (%) | 100.0 [100.0, 100.0] | 98.0 [93.9, 100.0] | -2.0 [-6.1, +0.0] | 0.7298 |
| `min_k_escape` | 102 | ESCO precision (%) | 6.3 [4.6, 8.3] | 7.1 [5.3, 9.1] | +0.8 [-0.6, +2.0] | 0.2500 |
| `min_k_escape` | 102 | ESCO recall (%) | 73.0 [61.2, 83.7] | 65.6 [53.7, 77.2] | -7.4 [-19.8, +4.4] | 0.2630 |
| `min_k_escape` | 102 | Top-20 concepts not in the true items' top 20 | 19 [17, 20] | 19 [16, 20] | +0 [-3, +2] | 1.0000 |

## 7. Qwen3.5-2B (main model alone; not registered), both sets, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 28.20 [24.41, 32.35] | 13.25 [11.85, 14.74] | -14.95 [-18.65, -11.43] | < 0.0001 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 99.1 [97.0, 100.0] | 100.0 [100.0, 100.0] | +0.9 [+0.0, +3.0] | 0.7266 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 2.5 [2.0, 3.2] | 4.4 [3.5, 5.4] | +1.9 [+1.3, +2.6] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 60.0 [52.0, 67.6] | 50.8 [43.4, 58.1] | -9.2 [-14.6, -3.8] | 0.0006 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 16 [15, 20] | 16 [14, 19] | +0 [-4, +1] | 0.5836 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 28.20 [24.41, 32.35] | 11.78 [10.29, 13.36] | -16.42 [-20.31, -12.70] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 99.1 [97.0, 100.0] | 99.2 [98.2, 100.0] | +0.2 [-1.3, +2.2] | 1.0000 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 2.5 [2.0, 3.2] | 4.9 [3.9, 6.1] | +2.4 [+1.7, +3.3] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 60.0 [52.0, 67.6] | 50.6 [43.0, 58.0] | -9.4 [-14.9, -3.9] | 0.0012 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 16 [15, 20] | 15 [14, 19] | -1 [-4, +1] | 0.5832 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 28.20 [24.41, 32.35] | 23.06 [20.14, 26.16] | -5.14 [-8.27, -2.05] | 0.0008 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 99.1 [97.0, 100.0] | 99.5 [98.5, 100.0] | +0.5 [-1.4, +2.9] | 0.9274 |
| `max_k_shown` | 211 | ESCO precision (%) | 2.5 [2.0, 3.2] | 3.0 [2.4, 3.8] | +0.5 [+0.1, +0.9] | 0.0058 |
| `max_k_shown` | 211 | ESCO recall (%) | 60.0 [52.0, 67.6] | 59.6 [51.6, 67.3] | -0.4 [-4.6, +4.2] | 0.9090 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 16 [15, 20] | 16 [15, 19] | +0 [-2, +1] | 1.0000 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 28.20 [24.41, 32.35] | 30.34 [27.02, 33.92] | +2.14 [-1.69, +6.00] | 0.2748 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 99.1 [97.0, 100.0] | 100.0 [100.0, 100.0] | +0.9 [+0.0, +3.0] | 0.7266 |
| `min_k_shown` | 211 | ESCO precision (%) | 2.5 [2.0, 3.2] | 2.2 [1.7, 2.7] | -0.3 [-0.7, +0.1] | 0.1046 |
| `min_k_shown` | 211 | ESCO recall (%) | 60.0 [52.0, 67.6] | 56.9 [48.5, 64.9] | -3.1 [-8.9, +2.6] | 0.3288 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 16 [15, 20] | 18 [16, 20] | +2 [-1, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 28.20 [24.41, 32.35] | 20.23 [17.33, 23.32] | -7.97 [-12.30, -3.77] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 99.1 [97.0, 100.0] | 98.1 [95.6, 100.0] | -0.9 [-2.4, +0.0] | 0.2706 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 2.5 [2.0, 3.2] | 3.8 [3.1, 4.7] | +1.3 [+0.7, +2.0] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 60.0 [52.0, 67.6] | 66.3 [59.4, 73.0] | +6.3 [+0.3, +12.7] | 0.0492 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 16 [15, 20] | 16 [14, 19] | +0 [-3, +1] | 0.7636 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 28.20 [24.41, 32.35] | 8.10 [7.42, 8.81] | -20.09 [-24.14, -16.42] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 99.1 [97.0, 100.0] | 99.5 [98.5, 100.0] | +0.5 [-1.4, +2.9] | 0.9392 |
| `min_k_enforced` | 211 | ESCO precision (%) | 2.5 [2.0, 3.2] | 7.9 [6.3, 9.6] | +5.4 [+4.1, +6.8] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO recall (%) | 60.0 [52.0, 67.6] | 57.3 [49.4, 65.2] | -2.7 [-9.3, +4.3] | 0.4758 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 16 [15, 20] | 16 [13, 19] | +0 [-4, +1] | 0.4220 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 28.20 [24.41, 32.35] | 6.89 [6.17, 7.66] | -21.31 [-25.44, -17.56] | < 0.0001 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 99.1 [97.0, 100.0] | 91.5 [86.1, 96.1] | -7.6 [-12.8, -3.3] | 0.0004 |
| `min_k_escape` | 211 | ESCO precision (%) | 2.5 [2.0, 3.2] | 9.9 [8.1, 11.9] | +7.4 [+5.9, +9.1] | < 0.0001 |
| `min_k_escape` | 211 | ESCO recall (%) | 60.0 [52.0, 67.6] | 62.7 [55.7, 69.9] | +2.7 [-3.8, +9.8] | 0.4484 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 16 [15, 20] | 14 [12, 18] | -2 [-6, +0] | 0.2128 |

Top 20 concepts of the `min_k_shown` outputs: project commissioning; Agile development; team building; communication; computer engineering; cloud technologies; adapt to change; risk management; seek innovation in current practices; manage relationships with stakeholders; manage time; cyber security; solve problems; statistics; ICT project management methodologies; cooperate with colleagues; think critically; quality assurance methodologies; DevOps; work in teams

Top 20 concepts of the true items of the same ads: English; teach communication methods; SAP Data Services; German; computer engineering; recruit members; design cloud architecture; Danish; perform scientific research; computer science; react to events in time-critical environments; web services; perform business research; systems development life-cycle; Ruby (computer programming); solve technical problems; communication; Java (computer programming); body language; manage budgets

## 8. Qwen3.5-2B (main model alone; not registered), job-ad skills, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 109 | False ESCO concepts per ad | 17.53 [13.58, 22.11] | 11.09 [9.29, 13.03] | -6.44 [-10.59, -2.91] | < 0.0001 |
| `prose_up_to_k` | 109 | Ads with at least one false concept (%) | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | +0.0 [+0.0, +0.0] | 1.0000 |
| `prose_up_to_k` | 109 | ESCO precision (%) | 2.7 [1.8, 4.0] | 3.1 [2.0, 4.6] | +0.4 [-0.5, +1.4] | 0.3928 |
| `prose_up_to_k` | 109 | ESCO recall (%) | 39.8 [30.7, 49.6] | 29.3 [20.5, 38.7] | -10.5 [-18.4, -3.0] | 0.0050 |
| `prose_up_to_k` | 109 | Top-20 concepts not in the true items' top 20 | 18 [16, 20] | 19 [17, 20] | +1 [-1, +2] | 1.0000 |
| `prose_exactly_k` | 109 | False ESCO concepts per ad | 17.53 [13.58, 22.11] | 11.00 [9.15, 13.08] | -6.53 [-10.56, -3.10] | < 0.0001 |
| `prose_exactly_k` | 109 | Ads with at least one false concept (%) | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | +0.0 [+0.0, +0.0] | 1.0000 |
| `prose_exactly_k` | 109 | ESCO precision (%) | 2.7 [1.8, 4.0] | 3.4 [2.2, 4.8] | +0.7 [-0.2, +1.6] | 0.1474 |
| `prose_exactly_k` | 109 | ESCO recall (%) | 39.8 [30.7, 49.6] | 31.4 [22.9, 40.7] | -8.4 [-15.6, -1.6] | 0.0152 |
| `prose_exactly_k` | 109 | Top-20 concepts not in the true items' top 20 | 18 [16, 20] | 19 [16, 20] | +1 [-2, +2] | 1.0000 |
| `max_k_shown` | 109 | False ESCO concepts per ad | 17.53 [13.58, 22.11] | 16.24 [12.70, 20.45] | -1.29 [-3.86, +1.38] | 0.3256 |
| `max_k_shown` | 109 | Ads with at least one false concept (%) | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | +0.0 [+0.0, +0.0] | 1.0000 |
| `max_k_shown` | 109 | ESCO precision (%) | 2.7 [1.8, 4.0] | 2.7 [1.7, 4.1] | -0.0 [-0.5, +0.5] | 0.9888 |
| `max_k_shown` | 109 | ESCO recall (%) | 39.8 [30.7, 49.6] | 36.8 [27.4, 46.9] | -3.0 [-8.5, +1.6] | 0.3038 |
| `max_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 18 [16, 20] | 18 [16, 20] | +0 [-2, +1] | 1.0000 |
| `min_k_shown` | 109 | False ESCO concepts per ad | 17.53 [13.58, 22.11] | 22.88 [18.35, 27.70] | +5.35 [+1.67, +9.51] | 0.0050 |
| `min_k_shown` | 109 | Ads with at least one false concept (%) | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | +0.0 [+0.0, +0.0] | 1.0000 |
| `min_k_shown` | 109 | ESCO precision (%) | 2.7 [1.8, 4.0] | 2.0 [1.4, 2.9] | -0.7 [-1.5, -0.1] | 0.0214 |
| `min_k_shown` | 109 | ESCO recall (%) | 39.8 [30.7, 49.6] | 39.1 [29.3, 49.6] | -0.8 [-8.8, +7.8] | 0.9234 |
| `min_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 18 [16, 20] | 19 [16, 20] | +1 [-2, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 109 | False ESCO concepts per ad | 17.53 [13.58, 22.11] | 16.48 [12.98, 20.45] | -1.06 [-5.17, +2.91] | 0.6152 |
| `min_k_shown_fewer_ok` | 109 | Ads with at least one false concept (%) | 100.0 [100.0, 100.0] | 100.0 [100.0, 100.0] | +0.0 [+0.0, +0.0] | 1.0000 |
| `min_k_shown_fewer_ok` | 109 | ESCO precision (%) | 2.7 [1.8, 4.0] | 3.3 [2.2, 4.7] | +0.6 [-0.3, +1.5] | 0.1808 |
| `min_k_shown_fewer_ok` | 109 | ESCO recall (%) | 39.8 [30.7, 49.6] | 45.9 [37.1, 54.6] | +6.0 [-3.3, +15.0] | 0.2348 |
| `min_k_shown_fewer_ok` | 109 | Top-20 concepts not in the true items' top 20 | 18 [16, 20] | 18 [16, 20] | +0 [-2, +2] | 1.0000 |
| `min_k_enforced` | 109 | False ESCO concepts per ad | 17.53 [13.58, 22.11] | 7.28 [6.38, 8.27] | -10.25 [-14.89, -6.24] | < 0.0001 |
| `min_k_enforced` | 109 | Ads with at least one false concept (%) | 100.0 [100.0, 100.0] | 99.1 [97.1, 100.0] | -0.9 [-2.9, +0.0] | 0.7312 |
| `min_k_enforced` | 109 | ESCO precision (%) | 2.7 [1.8, 4.0] | 6.1 [4.2, 8.6] | +3.4 [+1.7, +5.5] | < 0.0001 |
| `min_k_enforced` | 109 | ESCO recall (%) | 39.8 [30.7, 49.6] | 39.1 [28.9, 50.0] | -0.8 [-10.0, +8.7] | 0.9460 |
| `min_k_enforced` | 109 | Top-20 concepts not in the true items' top 20 | 18 [16, 20] | 19 [16, 20] | +1 [-2, +2] | 1.0000 |
| `min_k_escape` | 109 | False ESCO concepts per ad | 17.53 [13.58, 22.11] | 7.00 [6.16, 7.90] | -10.53 [-15.11, -6.61] | < 0.0001 |
| `min_k_escape` | 109 | Ads with at least one false concept (%) | 100.0 [100.0, 100.0] | 98.2 [95.3, 100.0] | -1.8 [-4.7, +0.0] | 0.2668 |
| `min_k_escape` | 109 | ESCO precision (%) | 2.7 [1.8, 4.0] | 6.6 [4.4, 9.3] | +3.9 [+2.0, +6.1] | < 0.0001 |
| `min_k_escape` | 109 | ESCO recall (%) | 39.8 [30.7, 49.6] | 40.6 [29.8, 51.6] | +0.8 [-9.2, +10.6] | 0.9292 |
| `min_k_escape` | 109 | Top-20 concepts not in the true items' top 20 | 18 [16, 20] | 18 [16, 20] | +0 [-2, +2] | 1.0000 |

## 9. Qwen3.5-2B (main model alone; not registered), job-ad knowledge, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 102 | False ESCO concepts per ad | 39.60 [33.15, 46.04] | 15.56 [13.58, 17.69] | -24.03 [-30.15, -17.90] | < 0.0001 |
| `prose_up_to_k` | 102 | Ads with at least one false concept (%) | 98.0 [93.9, 100.0] | 100.0 [100.0, 100.0] | +2.0 [+0.0, +6.1] | 0.7302 |
| `prose_up_to_k` | 102 | ESCO precision (%) | 2.4 [1.8, 3.2] | 5.4 [4.1, 6.9] | +3.0 [+2.1, +4.0] | < 0.0001 |
| `prose_up_to_k` | 102 | ESCO recall (%) | 82.0 [70.8, 91.7] | 74.3 [64.4, 83.2] | -7.7 [-15.4, -0.8] | 0.0316 |
| `prose_up_to_k` | 102 | Top-20 concepts not in the true items' top 20 | 19 [16, 20] | 18 [15, 19] | -1 [-4, +0] | 0.3690 |
| `prose_exactly_k` | 102 | False ESCO concepts per ad | 39.60 [33.15, 46.04] | 12.61 [10.46, 14.84] | -26.98 [-33.71, -20.30] | < 0.0001 |
| `prose_exactly_k` | 102 | Ads with at least one false concept (%) | 98.0 [93.9, 100.0] | 98.4 [96.3, 100.0] | +0.4 [-2.7, +4.4] | 0.9946 |
| `prose_exactly_k` | 102 | ESCO precision (%) | 2.4 [1.8, 3.2] | 6.3 [4.6, 8.3] | +3.9 [+2.6, +5.5] | < 0.0001 |
| `prose_exactly_k` | 102 | ESCO recall (%) | 82.0 [70.8, 91.7] | 71.5 [60.7, 81.6] | -10.5 [-19.4, -2.2] | 0.0134 |
| `prose_exactly_k` | 102 | Top-20 concepts not in the true items' top 20 | 19 [16, 20] | 18 [14, 19] | -1 [-4, +0] | 0.3188 |
| `max_k_shown` | 102 | False ESCO concepts per ad | 39.60 [33.15, 46.04] | 30.34 [26.04, 34.84] | -9.25 [-14.92, -3.62] | 0.0010 |
| `max_k_shown` | 102 | Ads with at least one false concept (%) | 98.0 [93.9, 100.0] | 99.0 [97.0, 100.0] | +1.0 [-2.9, +5.9] | 0.9308 |
| `max_k_shown` | 102 | ESCO precision (%) | 2.4 [1.8, 3.2] | 3.2 [2.4, 4.2] | +0.8 [+0.3, +1.4] | 0.0016 |
| `max_k_shown` | 102 | ESCO recall (%) | 82.0 [70.8, 91.7] | 84.4 [74.4, 93.0] | +2.5 [-3.9, +10.4] | 0.6460 |
| `max_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 19 [16, 20] | 18 [16, 20] | -1 [-2, +1] | 1.0000 |
| `min_k_shown` | 102 | False ESCO concepts per ad | 39.60 [33.15, 46.04] | 38.31 [33.34, 43.31] | -1.28 [-7.97, +5.58] | 0.7148 |
| `min_k_shown` | 102 | Ads with at least one false concept (%) | 98.0 [93.9, 100.0] | 100.0 [100.0, 100.0] | +2.0 [+0.0, +6.1] | 0.7302 |
| `min_k_shown` | 102 | ESCO precision (%) | 2.4 [1.8, 3.2] | 2.3 [1.7, 3.0] | -0.1 [-0.6, +0.4] | 0.7112 |
| `min_k_shown` | 102 | ESCO recall (%) | 82.0 [70.8, 91.7] | 76.2 [64.3, 87.2] | -5.7 [-14.7, +2.0] | 0.1882 |
| `min_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 19 [16, 20] | 19 [16, 20] | +0 [-2, +1] | 1.0000 |
| `min_k_shown_fewer_ok` | 102 | False ESCO concepts per ad | 39.60 [33.15, 46.04] | 24.24 [19.92, 28.75] | -15.36 [-22.71, -8.07] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | Ads with at least one false concept (%) | 98.0 [93.9, 100.0] | 96.1 [90.7, 100.0] | -2.0 [-5.0, +0.0] | 0.2526 |
| `min_k_shown_fewer_ok` | 102 | ESCO precision (%) | 2.4 [1.8, 3.2] | 4.2 [3.2, 5.5] | +1.8 [+1.0, +2.8] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | ESCO recall (%) | 82.0 [70.8, 91.7] | 88.5 [79.3, 95.9] | +6.6 [-1.0, +15.7] | 0.1314 |
| `min_k_shown_fewer_ok` | 102 | Top-20 concepts not in the true items' top 20 | 19 [16, 20] | 18 [15, 19] | -1 [-3, +1] | 0.5874 |
| `min_k_enforced` | 102 | False ESCO concepts per ad | 39.60 [33.15, 46.04] | 8.98 [7.94, 10.13] | -30.62 [-36.84, -24.29] | < 0.0001 |
| `min_k_enforced` | 102 | Ads with at least one false concept (%) | 98.0 [93.9, 100.0] | 100.0 [100.0, 100.0] | +2.0 [+0.0, +6.1] | 0.7302 |
| `min_k_enforced` | 102 | ESCO precision (%) | 2.4 [1.8, 3.2] | 9.3 [6.9, 12.0] | +6.9 [+4.9, +9.1] | < 0.0001 |
| `min_k_enforced` | 102 | ESCO recall (%) | 82.0 [70.8, 91.7] | 77.0 [65.8, 87.4] | -4.9 [-13.1, +3.2] | 0.2714 |
| `min_k_enforced` | 102 | Top-20 concepts not in the true items' top 20 | 19 [16, 20] | 18 [14, 19] | -1 [-4, +1] | 0.3104 |
| `min_k_escape` | 102 | False ESCO concepts per ad | 39.60 [33.15, 46.04] | 6.77 [5.59, 7.97] | -32.82 [-39.16, -26.55] | < 0.0001 |
| `min_k_escape` | 102 | Ads with at least one false concept (%) | 98.0 [93.9, 100.0] | 84.3 [73.3, 93.9] | -13.7 [-23.8, -5.7] | 0.0008 |
| `min_k_escape` | 102 | ESCO precision (%) | 2.4 [1.8, 3.2] | 13.3 [10.5, 16.4] | +10.9 [+8.5, +13.6] | < 0.0001 |
| `min_k_escape` | 102 | ESCO recall (%) | 82.0 [70.8, 91.7] | 86.9 [79.5, 93.7] | +4.9 [-3.1, +14.5] | 0.3048 |
| `min_k_escape` | 102 | Top-20 concepts not in the true items' top 20 | 19 [16, 20] | 17 [13, 19] | -2 [-5, +0] | 0.1868 |

## 10. Qwen3.5-9B (main model alone; not registered), both sets, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 2.28 [1.71, 2.93] | 1.59 [1.30, 1.91] | -0.69 [-1.09, -0.32] | 0.0004 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 42.7 [34.9, 50.7] | 52.6 [46.0, 59.1] | +10.0 [+4.6, +15.4] | 0.0002 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 19.4 [14.6, 25.3] | 27.0 [21.3, 33.2] | +7.5 [+4.2, +10.7] | 0.0004 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 45.5 [36.1, 54.9] | 48.6 [40.8, 56.4] | +3.1 [-3.2, +9.2] | 0.3174 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 14 [12, 19] | 12 [10, 17] | -2 [-5, +1] | 0.3936 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 2.28 [1.71, 2.93] | 1.61 [1.36, 1.88] | -0.67 [-1.10, -0.27] | 0.0008 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 42.7 [34.9, 50.7] | 55.5 [48.6, 62.3] | +12.8 [+7.4, +18.3] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 19.4 [14.6, 25.3] | 25.0 [20.0, 30.5] | +5.6 [+2.0, +8.6] | 0.0038 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 45.5 [36.1, 54.9] | 44.5 [36.9, 52.4] | -1.0 [-7.4, +5.2] | 0.7830 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 14 [12, 19] | 13 [10, 17] | -1 [-5, +1] | 0.4488 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 2.28 [1.71, 2.93] | 1.84 [1.37, 2.37] | -0.44 [-0.72, -0.18] | 0.0018 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 42.7 [34.9, 50.7] | 48.3 [40.7, 55.9] | +5.7 [+1.0, +10.8] | 0.0256 |
| `max_k_shown` | 211 | ESCO precision (%) | 19.4 [14.6, 25.3] | 22.7 [17.0, 29.7] | +3.3 [+0.7, +6.4] | 0.0120 |
| `max_k_shown` | 211 | ESCO recall (%) | 45.5 [36.1, 54.9] | 44.7 [35.6, 53.8] | -0.8 [-4.8, +3.4] | 0.7804 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 14 [12, 19] | 15 [12, 18] | +1 [-3, +2] | 1.0000 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 2.28 [1.71, 2.93] | 2.76 [2.18, 3.39] | +0.48 [+0.16, +0.86] | 0.0028 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 42.7 [34.9, 50.7] | 54.0 [46.6, 61.5] | +11.4 [+5.3, +18.0] | 0.0004 |
| `min_k_shown` | 211 | ESCO precision (%) | 19.4 [14.6, 25.3] | 18.3 [14.2, 23.3] | -1.1 [-4.1, +1.4] | 0.4154 |
| `min_k_shown` | 211 | ESCO recall (%) | 45.5 [36.1, 54.9] | 51.4 [42.2, 60.7] | +5.9 [+0.8, +11.2] | 0.0290 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 14 [12, 19] | 14 [12, 18] | +0 [-2, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 2.28 [1.71, 2.93] | 1.73 [1.15, 2.36] | -0.55 [-0.84, -0.28] | 0.0002 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 42.7 [34.9, 50.7] | 28.4 [21.2, 35.9] | -14.2 [-20.6, -8.2] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 19.4 [14.6, 25.3] | 17.3 [11.8, 24.8] | -2.2 [-5.8, +2.1] | 0.3056 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 45.5 [36.1, 54.9] | 29.8 [21.4, 38.5] | -15.7 [-23.7, -8.1] | 0.0002 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 14 [12, 19] | 15 [13, 20] | +1 [-1, +4] | 0.5958 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 2.28 [1.71, 2.93] | 4.50 [3.70, 5.64] | +2.22 [+1.21, +3.48] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 42.7 [34.9, 50.7] | 98.6 [96.8, 100.0] | +55.9 [+48.1, +63.6] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 19.4 [14.6, 25.3] | 17.2 [13.4, 21.6] | -2.2 [-7.9, +2.8] | 0.4020 |
| `min_k_enforced` | 211 | ESCO recall (%) | 45.5 [36.1, 54.9] | 77.3 [70.5, 83.8] | +31.8 [+21.5, +42.0] | < 0.0001 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 14 [12, 19] | 16 [12, 18] | +2 [-4, +3] | 1.0000 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 2.28 [1.71, 2.93] | 1.68 [1.30, 2.07] | -0.60 [-1.09, -0.17] | 0.0052 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 42.7 [34.9, 50.7] | 42.2 [34.5, 50.2] | -0.5 [-8.5, +7.7] | 0.9560 |
| `min_k_escape` | 211 | ESCO precision (%) | 19.4 [14.6, 25.3] | 26.2 [20.5, 32.6] | +6.8 [+2.4, +11.3] | 0.0034 |
| `min_k_escape` | 211 | ESCO recall (%) | 45.5 [36.1, 54.9] | 49.4 [40.2, 58.4] | +3.9 [-3.8, +11.5] | 0.3276 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 14 [12, 19] | 13 [10, 17] | -1 [-5, +1] | 0.4890 |

Top 20 concepts of the `min_k_shown` outputs: Java (computer programming); react to events in time-critical environments; Python (computer programming); JavaScript; computer engineering; teach communication methods; English; DevOps; manage ICT virtualisation environments; cloud technologies; implement front-end website design; ICT project management methodologies; automation technology; web services; continuous improvement philosophies; cooperate with colleagues; C#; tools for ICT test automation; service-oriented modelling; query languages

Top 20 concepts of the true items of the same ads: English; teach communication methods; SAP Data Services; German; computer engineering; recruit members; design cloud architecture; Danish; perform scientific research; computer science; react to events in time-critical environments; web services; perform business research; systems development life-cycle; Ruby (computer programming); solve technical problems; communication; Java (computer programming); body language; manage budgets

## 11. Qwen3.5-9B (main model alone; not registered), job-ad skills, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 109 | False ESCO concepts per ad | 4.02 [2.99, 5.15] | 2.81 [2.29, 3.39] | -1.21 [-1.92, -0.54] | 0.0004 |
| `prose_up_to_k` | 109 | Ads with at least one false concept (%) | 70.6 [58.6, 82.1] | 86.1 [78.2, 92.9] | +15.4 [+7.7, +24.0] | < 0.0001 |
| `prose_up_to_k` | 109 | ESCO precision (%) | 11.9 [7.7, 17.2] | 15.1 [10.2, 20.9] | +3.2 [+0.2, +6.4] | 0.0390 |
| `prose_up_to_k` | 109 | ESCO recall (%) | 44.4 [32.1, 56.7] | 40.9 [30.8, 51.4] | -3.5 [-13.0, +5.8] | 0.4838 |
| `prose_up_to_k` | 109 | Top-20 concepts not in the true items' top 20 | 17 [15, 20] | 16 [13, 19] | -1 [-4, +1] | 0.5116 |
| `prose_exactly_k` | 109 | False ESCO concepts per ad | 4.02 [2.99, 5.15] | 2.68 [2.25, 3.12] | -1.34 [-2.12, -0.62] | < 0.0001 |
| `prose_exactly_k` | 109 | Ads with at least one false concept (%) | 70.6 [58.6, 82.1] | 86.2 [78.2, 93.3] | +15.6 [+7.9, +24.3] | < 0.0001 |
| `prose_exactly_k` | 109 | ESCO precision (%) | 11.9 [7.7, 17.2] | 15.1 [10.3, 20.6] | +3.2 [+0.2, +6.0] | 0.0342 |
| `prose_exactly_k` | 109 | ESCO recall (%) | 44.4 [32.1, 56.7] | 38.9 [29.4, 49.1] | -5.4 [-14.4, +2.9] | 0.2284 |
| `prose_exactly_k` | 109 | Top-20 concepts not in the true items' top 20 | 17 [15, 20] | 16 [13, 19] | -1 [-5, +1] | 0.4754 |
| `max_k_shown` | 109 | False ESCO concepts per ad | 4.02 [2.99, 5.15] | 3.23 [2.40, 4.17] | -0.79 [-1.30, -0.32] | 0.0018 |
| `max_k_shown` | 109 | Ads with at least one false concept (%) | 70.6 [58.6, 82.1] | 80.7 [70.6, 90.0] | +10.1 [+2.8, +18.3] | 0.0058 |
| `max_k_shown` | 109 | ESCO precision (%) | 11.9 [7.7, 17.2] | 13.9 [9.1, 20.3] | +2.1 [-0.3, +5.0] | 0.0814 |
| `max_k_shown` | 109 | ESCO recall (%) | 44.4 [32.1, 56.7] | 42.9 [31.6, 54.3] | -1.5 [-8.6, +5.8] | 0.7378 |
| `max_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 17 [15, 20] | 17 [15, 20] | +0 [-2, +2] | 1.0000 |
| `min_k_shown` | 109 | False ESCO concepts per ad | 4.02 [2.99, 5.15] | 4.55 [3.63, 5.54] | +0.53 [+0.02, +1.06] | 0.0414 |
| `min_k_shown` | 109 | Ads with at least one false concept (%) | 70.6 [58.6, 82.1] | 87.2 [78.1, 95.1] | +16.5 [+6.5, +27.0] | 0.0002 |
| `min_k_shown` | 109 | ESCO precision (%) | 11.9 [7.7, 17.2] | 13.0 [8.9, 18.0] | +1.1 [-1.2, +3.3] | 0.3340 |
| `min_k_shown` | 109 | ESCO recall (%) | 44.4 [32.1, 56.7] | 55.6 [44.0, 67.3] | +11.3 [+3.9, +19.3] | 0.0018 |
| `min_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 17 [15, 20] | 17 [14, 20] | +0 [-3, +1] | 1.0000 |
| `min_k_shown_fewer_ok` | 109 | False ESCO concepts per ad | 4.02 [2.99, 5.15] | 2.83 [1.80, 3.98] | -1.19 [-1.73, -0.71] | < 0.0001 |
| `min_k_shown_fewer_ok` | 109 | Ads with at least one false concept (%) | 70.6 [58.6, 82.1] | 43.1 [31.5, 54.7] | -27.5 [-38.9, -16.7] | < 0.0001 |
| `min_k_shown_fewer_ok` | 109 | ESCO precision (%) | 11.9 [7.7, 17.2] | 10.7 [5.9, 17.5] | -1.1 [-4.5, +2.9] | 0.5456 |
| `min_k_shown_fewer_ok` | 109 | ESCO recall (%) | 44.4 [32.1, 56.7] | 27.8 [16.9, 39.1] | -16.5 [-27.5, -6.1] | 0.0032 |
| `min_k_shown_fewer_ok` | 109 | Top-20 concepts not in the true items' top 20 | 17 [15, 20] | 19 [16, 20] | +2 [-2, +3] | 0.8584 |
| `min_k_enforced` | 109 | False ESCO concepts per ad | 4.02 [2.99, 5.15] | 4.39 [3.76, 5.13] | +0.38 [-0.74, +1.45] | 0.4972 |
| `min_k_enforced` | 109 | Ads with at least one false concept (%) | 70.6 [58.6, 82.1] | 100.0 [100.0, 100.0] | +29.4 [+17.9, +41.4] | < 0.0001 |
| `min_k_enforced` | 109 | ESCO precision (%) | 11.9 [7.7, 17.2] | 15.1 [10.8, 19.9] | +3.2 [-1.3, +7.2] | 0.1574 |
| `min_k_enforced` | 109 | ESCO recall (%) | 44.4 [32.1, 56.7] | 63.9 [52.7, 74.8] | +19.5 [+5.8, +33.9] | 0.0064 |
| `min_k_enforced` | 109 | Top-20 concepts not in the true items' top 20 | 17 [15, 20] | 17 [13, 19] | +0 [-5, +1] | 0.5090 |
| `min_k_escape` | 109 | False ESCO concepts per ad | 4.02 [2.99, 5.15] | 2.97 [2.30, 3.68] | -1.05 [-1.89, -0.30] | 0.0026 |
| `min_k_escape` | 109 | Ads with at least one false concept (%) | 70.6 [58.6, 82.1] | 68.8 [56.9, 80.0] | -1.8 [-13.0, +9.3] | 0.7948 |
| `min_k_escape` | 109 | ESCO precision (%) | 11.9 [7.7, 17.2] | 17.6 [12.5, 23.4] | +5.7 [+2.2, +9.3] | 0.0012 |
| `min_k_escape` | 109 | ESCO recall (%) | 44.4 [32.1, 56.7] | 51.9 [40.2, 63.2] | +7.5 [-2.0, +16.9] | 0.1442 |
| `min_k_escape` | 109 | Top-20 concepts not in the true items' top 20 | 17 [15, 20] | 17 [13, 19] | +0 [-5, +1] | 0.3688 |

## 12. Qwen3.5-9B (main model alone; not registered), job-ad knowledge, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 102 | False ESCO concepts per ad | 0.42 [0.08, 0.88] | 0.29 [0.14, 0.48] | -0.13 [-0.48, +0.14] | 0.4286 |
| `prose_up_to_k` | 102 | Ads with at least one false concept (%) | 12.7 [4.9, 22.3] | 16.9 [9.2, 25.4] | +4.1 [-3.5, +11.6] | 0.2834 |
| `prose_up_to_k` | 102 | ESCO precision (%) | 57.0 [38.1, 85.7] | 70.2 [58.9, 82.6] | +13.2 [-10.0, +24.9] | 0.2264 |
| `prose_up_to_k` | 102 | ESCO recall (%) | 46.7 [31.8, 61.3] | 57.0 [45.3, 68.1] | +10.3 [+1.3, +20.5] | 0.0260 |
| `prose_up_to_k` | 102 | Top-20 concepts not in the true items' top 20 | 12 [6, 15] | 11 [5, 12] | -1 [-7, +1] | 0.3322 |
| `prose_exactly_k` | 102 | False ESCO concepts per ad | 0.42 [0.08, 0.88] | 0.47 [0.27, 0.72] | +0.05 [-0.25, +0.29] | 0.6930 |
| `prose_exactly_k` | 102 | Ads with at least one false concept (%) | 12.7 [4.9, 22.3] | 22.5 [14.1, 31.7] | +9.8 [+2.6, +17.1] | 0.0052 |
| `prose_exactly_k` | 102 | ESCO precision (%) | 57.0 [38.1, 85.7] | 56.2 [44.8, 68.5] | -0.8 [-23.4, +10.4] | 0.8798 |
| `prose_exactly_k` | 102 | ESCO recall (%) | 46.7 [31.8, 61.3] | 50.5 [38.7, 62.0] | +3.8 [-5.2, +12.8] | 0.4152 |
| `prose_exactly_k` | 102 | Top-20 concepts not in the true items' top 20 | 12 [6, 15] | 13 [6, 13] | +1 [-5, +3] | 0.8532 |
| `max_k_shown` | 102 | False ESCO concepts per ad | 0.42 [0.08, 0.88] | 0.35 [0.09, 0.77] | -0.07 [-0.27, +0.08] | 0.5348 |
| `max_k_shown` | 102 | Ads with at least one false concept (%) | 12.7 [4.9, 22.3] | 13.7 [5.8, 23.2] | +1.0 [-4.9, +6.7] | 0.8802 |
| `max_k_shown` | 102 | ESCO precision (%) | 57.0 [38.1, 85.7] | 61.3 [41.4, 85.7] | +4.3 [-7.1, +16.8] | 0.5114 |
| `max_k_shown` | 102 | ESCO recall (%) | 46.7 [31.8, 61.3] | 46.7 [32.4, 61.0] | +0.0 [-3.1, +3.4] | 1.0000 |
| `max_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 12 [6, 15] | 12 [6, 14] | +0 [-3, +1] | 1.0000 |
| `min_k_shown` | 102 | False ESCO concepts per ad | 0.42 [0.08, 0.88] | 0.85 [0.27, 1.65] | +0.43 [+0.09, +0.94] | 0.0038 |
| `min_k_shown` | 102 | Ads with at least one false concept (%) | 12.7 [4.9, 22.3] | 18.6 [9.6, 29.0] | +5.9 [+0.0, +12.9] | 0.0762 |
| `min_k_shown` | 102 | ESCO precision (%) | 57.0 [38.1, 85.7] | 39.6 [25.6, 65.3] | -17.4 [-30.3, -5.1] | 0.0018 |
| `min_k_shown` | 102 | ESCO recall (%) | 46.7 [31.8, 61.3] | 46.7 [31.6, 61.7] | +0.0 [-7.3, +6.6] | 1.0000 |
| `min_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 12 [6, 15] | 11 [7, 16] | -1 [-2, +6] | 0.7338 |
| `min_k_shown_fewer_ok` | 102 | False ESCO concepts per ad | 0.42 [0.08, 0.88] | 0.55 [0.16, 1.06] | +0.13 [-0.09, +0.42] | 0.3748 |
| `min_k_shown_fewer_ok` | 102 | Ads with at least one false concept (%) | 12.7 [4.9, 22.3] | 12.7 [5.2, 21.7] | +0.0 [-7.1, +7.1] | 1.0000 |
| `min_k_shown_fewer_ok` | 102 | ESCO precision (%) | 57.0 [38.1, 85.7] | 41.1 [26.9, 67.3] | -15.9 [-35.6, -3.2] | 0.0158 |
| `min_k_shown_fewer_ok` | 102 | ESCO recall (%) | 46.7 [31.8, 61.3] | 32.0 [19.7, 45.2] | -14.8 [-26.2, -4.2] | 0.0058 |
| `min_k_shown_fewer_ok` | 102 | Top-20 concepts not in the true items' top 20 | 12 [6, 15] | 14 [9, 16] | +2 [-1, +6] | 0.2788 |
| `min_k_enforced` | 102 | False ESCO concepts per ad | 0.42 [0.08, 0.88] | 4.61 [3.18, 6.92] | +4.19 [+2.69, +6.52] | < 0.0001 |
| `min_k_enforced` | 102 | Ads with at least one false concept (%) | 12.7 [4.9, 22.3] | 97.1 [93.3, 100.0] | +84.3 [+74.7, +92.5] | < 0.0001 |
| `min_k_enforced` | 102 | ESCO precision (%) | 57.0 [38.1, 85.7] | 19.2 [12.8, 27.7] | -37.8 [-67.2, -18.3] | < 0.0001 |
| `min_k_enforced` | 102 | ESCO recall (%) | 46.7 [31.8, 61.3] | 91.8 [85.7, 97.1] | +45.1 [+30.4, +60.3] | < 0.0001 |
| `min_k_enforced` | 102 | Top-20 concepts not in the true items' top 20 | 12 [6, 15] | 12 [10, 18] | +0 [-1, +9] | 0.2018 |
| `min_k_escape` | 102 | False ESCO concepts per ad | 0.42 [0.08, 0.88] | 0.30 [0.13, 0.51] | -0.12 [-0.62, +0.28] | 0.6650 |
| `min_k_escape` | 102 | Ads with at least one false concept (%) | 12.7 [4.9, 22.3] | 13.7 [6.0, 22.5] | +1.0 [-10.4, +12.1] | 0.9310 |
| `min_k_escape` | 102 | ESCO precision (%) | 57.0 [38.1, 85.7] | 64.8 [53.3, 78.7] | +7.8 [-23.6, +32.9] | 0.6480 |
| `min_k_escape` | 102 | ESCO recall (%) | 46.7 [31.8, 61.3] | 46.7 [31.5, 61.6] | +0.0 [-12.0, +12.6] | 1.0000 |
| `min_k_escape` | 102 | Top-20 concepts not in the true items' top 20 | 12 [6, 15] | 13 [7, 14] | +1 [-4, +3] | 1.0000 |

## 13. Qwen3.5-27B (main model alone; not registered), both sets, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 0.92 [0.65, 1.21] | 0.82 [0.63, 1.01] | -0.10 [-0.30, +0.09] | 0.3050 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 39.8 [31.6, 48.1] | 42.6 [35.1, 50.3] | +2.7 [-2.0, +7.6] | 0.2582 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 45.4 [37.1, 55.1] | 50.5 [43.6, 58.0] | +5.2 [-1.7, +11.4] | 0.1408 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 63.1 [54.7, 71.5] | 68.9 [61.7, 75.9] | +5.8 [-0.2, +12.4] | 0.0600 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 11 [7, 15] | 10 [6, 13] | -1 [-5, +2] | 0.5444 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 0.92 [0.65, 1.21] | 1.26 [1.08, 1.45] | +0.35 [+0.14, +0.55] | 0.0020 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 39.8 [31.6, 48.1] | 55.6 [49.0, 62.5] | +15.8 [+10.5, +21.5] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 45.4 [37.1, 55.1] | 39.6 [34.5, 45.0] | -5.7 [-13.0, +0.2] | 0.0626 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 63.1 [54.7, 71.5] | 68.6 [62.4, 74.8] | +5.5 [-0.4, +11.8] | 0.0698 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 11 [7, 15] | 13 [8, 15] | +2 [-4, +4] | 1.0000 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 0.92 [0.65, 1.21] | 0.83 [0.65, 1.01] | -0.09 [-0.26, +0.07] | 0.2878 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 39.8 [31.6, 48.1] | 46.0 [37.7, 54.1] | +6.2 [+2.8, +10.1] | < 0.0001 |
| `max_k_shown` | 211 | ESCO precision (%) | 45.4 [37.1, 55.1] | 49.0 [42.0, 56.3] | +3.6 [-1.9, +8.3] | 0.1834 |
| `max_k_shown` | 211 | ESCO recall (%) | 63.1 [54.7, 71.5] | 65.9 [58.2, 73.5] | +2.7 [-2.3, +8.6] | 0.3922 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 11 [7, 15] | 10 [6, 14] | -1 [-4, +2] | 0.5900 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 0.92 [0.65, 1.21] | 2.63 [2.35, 2.90] | +1.71 [+1.37, +2.04] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 39.8 [31.6, 48.1] | 82.5 [75.8, 88.7] | +42.7 [+33.8, +51.6] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 45.4 [37.1, 55.1] | 25.4 [21.6, 29.5] | -19.9 [-28.5, -12.8] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 63.1 [54.7, 71.5] | 74.1 [67.6, 80.5] | +11.0 [+4.1, +18.6] | 0.0016 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 11 [7, 15] | 13 [11, 17] | +2 [-1, +7] | 0.2926 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 0.92 [0.65, 1.21] | 1.45 [1.22, 1.70] | +0.54 [+0.31, +0.77] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 39.8 [31.6, 48.1] | 60.7 [53.2, 68.1] | +20.9 [+14.1, +28.0] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 45.4 [37.1, 55.1] | 36.2 [31.0, 41.7] | -9.2 [-16.3, -3.4] | 0.0016 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 63.1 [54.7, 71.5] | 68.2 [61.3, 75.2] | +5.1 [-1.6, +12.3] | 0.1686 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 11 [7, 15] | 15 [9, 16] | +4 [-2, +5] | 0.6956 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 0.92 [0.65, 1.21] | 3.18 [2.98, 3.39] | +2.27 [+1.98, +2.54] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 39.8 [31.6, 48.1] | 98.1 [96.1, 99.5] | +58.3 [+50.0, +66.5] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 45.4 [37.1, 55.1] | 22.4 [19.0, 26.1] | -23.0 [-31.3, -16.0] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO recall (%) | 63.1 [54.7, 71.5] | 76.1 [69.9, 82.1] | +12.9 [+5.9, +20.7] | < 0.0001 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 11 [7, 15] | 13 [11, 17] | +2 [-1, +8] | 0.2536 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 0.92 [0.65, 1.21] | 1.52 [1.26, 1.78] | +0.60 [+0.34, +0.85] | < 0.0001 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 39.8 [31.6, 48.1] | 58.3 [50.0, 66.5] | +18.5 [+11.4, +26.2] | < 0.0001 |
| `min_k_escape` | 211 | ESCO precision (%) | 45.4 [37.1, 55.1] | 36.6 [31.7, 41.9] | -8.7 [-16.0, -2.6] | 0.0064 |
| `min_k_escape` | 211 | ESCO recall (%) | 63.1 [54.7, 71.5] | 72.5 [65.8, 79.2] | +9.4 [+2.1, +17.3] | 0.0112 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 11 [7, 15] | 12 [9, 15] | +1 [-3, +4] | 0.9546 |

Top 20 concepts of the `min_k_shown` outputs: English; cooperate with colleagues; continuous improvement philosophies; apply knowledge of science, technology and engineering; computer engineering; SAP R3; Agile development; DevOps; automation technology; teach communication methods; support managers; computer science; design cloud architecture; use concurrent programming; flexography; German; perform scientific research; computer vision; mammalogy; integrated development environment software

Top 20 concepts of the true items of the same ads: English; teach communication methods; SAP Data Services; German; computer engineering; recruit members; design cloud architecture; Danish; perform scientific research; computer science; react to events in time-critical environments; web services; perform business research; systems development life-cycle; Ruby (computer programming); solve technical problems; communication; Java (computer programming); body language; manage budgets

## 14. Qwen3.5-27B (main model alone; not registered), job-ad skills, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 109 | False ESCO concepts per ad | 1.50 [1.01, 2.03] | 1.32 [1.01, 1.64] | -0.18 [-0.57, +0.19] | 0.3630 |
| `prose_up_to_k` | 109 | Ads with at least one false concept (%) | 56.0 [43.4, 68.5] | 63.7 [52.7, 74.3] | +7.7 [+0.5, +15.7] | 0.0364 |
| `prose_up_to_k` | 109 | ESCO precision (%) | 30.0 [21.7, 40.9] | 34.8 [26.5, 43.7] | +4.7 [-3.6, +12.2] | 0.2698 |
| `prose_up_to_k` | 109 | ESCO recall (%) | 52.6 [42.3, 63.2] | 57.6 [47.4, 67.5] | +5.0 [-4.9, +15.6] | 0.3594 |
| `prose_up_to_k` | 109 | Top-20 concepts not in the true items' top 20 | 17 [10, 18] | 15 [9, 17] | -2 [-6, +2] | 0.5500 |
| `prose_exactly_k` | 109 | False ESCO concepts per ad | 1.50 [1.01, 2.03] | 1.90 [1.60, 2.21] | +0.41 [+0.01, +0.80] | 0.0470 |
| `prose_exactly_k` | 109 | Ads with at least one false concept (%) | 56.0 [43.4, 68.5] | 76.1 [66.7, 84.9] | +20.2 [+11.8, +29.3] | < 0.0001 |
| `prose_exactly_k` | 109 | ESCO precision (%) | 30.0 [21.7, 40.9] | 27.2 [21.3, 33.6] | -2.8 [-11.3, +3.9] | 0.4132 |
| `prose_exactly_k` | 109 | ESCO recall (%) | 52.6 [42.3, 63.2] | 58.3 [49.7, 67.3] | +5.7 [-3.4, +15.7] | 0.2376 |
| `prose_exactly_k` | 109 | Top-20 concepts not in the true items' top 20 | 17 [10, 18] | 17 [10, 17] | +0 [-4, +3] | 1.0000 |
| `max_k_shown` | 109 | False ESCO concepts per ad | 1.50 [1.01, 2.03] | 1.29 [0.98, 1.62] | -0.20 [-0.53, +0.10] | 0.2162 |
| `max_k_shown` | 109 | Ads with at least one false concept (%) | 56.0 [43.4, 68.5] | 62.4 [50.4, 74.3] | +6.4 [+1.8, +12.1] | 0.0032 |
| `max_k_shown` | 109 | ESCO precision (%) | 30.0 [21.7, 40.9] | 33.8 [25.6, 42.9] | +3.8 [-2.8, +9.7] | 0.2668 |
| `max_k_shown` | 109 | ESCO recall (%) | 52.6 [42.3, 63.2] | 54.1 [43.9, 64.5] | +1.5 [-5.9, +10.3] | 0.8414 |
| `max_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 17 [10, 18] | 14 [9, 16] | -3 [-5, +2] | 0.5208 |
| `min_k_shown` | 109 | False ESCO concepts per ad | 1.50 [1.01, 2.03] | 3.27 [2.92, 3.61] | +1.77 [+1.25, +2.29] | < 0.0001 |
| `min_k_shown` | 109 | Ads with at least one false concept (%) | 56.0 [43.4, 68.5] | 94.5 [88.9, 99.0] | +38.5 [+26.2, +50.9] | < 0.0001 |
| `min_k_shown` | 109 | ESCO precision (%) | 30.0 [21.7, 40.9] | 18.5 [14.2, 23.3] | -11.5 [-20.8, -4.7] | 0.0002 |
| `min_k_shown` | 109 | ESCO recall (%) | 52.6 [42.3, 63.2] | 60.9 [51.9, 70.1] | +8.3 [+0.0, +17.5] | 0.0580 |
| `min_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 17 [10, 18] | 17 [12, 18] | +0 [-3, +5] | 0.8270 |
| `min_k_shown_fewer_ok` | 109 | False ESCO concepts per ad | 1.50 [1.01, 2.03] | 1.86 [1.48, 2.24] | +0.37 [+0.00, +0.75] | 0.0538 |
| `min_k_shown_fewer_ok` | 109 | Ads with at least one false concept (%) | 56.0 [43.4, 68.5] | 74.3 [63.3, 84.8] | +18.3 [+9.8, +28.0] | < 0.0001 |
| `min_k_shown_fewer_ok` | 109 | ESCO precision (%) | 30.0 [21.7, 40.9] | 27.5 [21.1, 34.7] | -2.5 [-10.1, +3.5] | 0.4026 |
| `min_k_shown_fewer_ok` | 109 | ESCO recall (%) | 52.6 [42.3, 63.2] | 57.9 [48.6, 67.7] | +5.3 [-3.3, +15.0] | 0.2784 |
| `min_k_shown_fewer_ok` | 109 | Top-20 concepts not in the true items' top 20 | 17 [10, 18] | 16 [11, 18] | -1 [-3, +3] | 1.0000 |
| `min_k_enforced` | 109 | False ESCO concepts per ad | 1.50 [1.01, 2.03] | 3.41 [3.11, 3.71] | +1.92 [+1.47, +2.35] | < 0.0001 |
| `min_k_enforced` | 109 | Ads with at least one false concept (%) | 56.0 [43.4, 68.5] | 97.2 [93.6, 100.0] | +41.3 [+28.4, +54.0] | < 0.0001 |
| `min_k_enforced` | 109 | ESCO precision (%) | 30.0 [21.7, 40.9] | 18.4 [14.1, 23.1] | -11.6 [-20.6, -5.1] | < 0.0001 |
| `min_k_enforced` | 109 | ESCO recall (%) | 52.6 [42.3, 63.2] | 63.2 [54.3, 72.3] | +10.5 [+1.8, +20.1] | 0.0220 |
| `min_k_enforced` | 109 | Top-20 concepts not in the true items' top 20 | 17 [10, 18] | 16 [13, 18] | -1 [-2, +5] | 0.7408 |
| `min_k_escape` | 109 | False ESCO concepts per ad | 1.50 [1.01, 2.03] | 2.13 [1.71, 2.54] | +0.63 [+0.17, +1.08] | 0.0098 |
| `min_k_escape` | 109 | Ads with at least one false concept (%) | 56.0 [43.4, 68.5] | 72.5 [61.1, 83.2] | +16.5 [+6.2, +27.6] | 0.0034 |
| `min_k_escape` | 109 | ESCO precision (%) | 30.0 [21.7, 40.9] | 24.7 [19.0, 31.1] | -5.4 [-13.4, +1.0] | 0.0986 |
| `min_k_escape` | 109 | ESCO recall (%) | 52.6 [42.3, 63.2] | 57.1 [47.1, 67.5] | +4.5 [-4.7, +14.5] | 0.3978 |
| `min_k_escape` | 109 | Top-20 concepts not in the true items' top 20 | 17 [10, 18] | 17 [11, 18] | +0 [-3, +4] | 1.0000 |

## 15. Qwen3.5-27B (main model alone; not registered), job-ad knowledge, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 102 | False ESCO concepts per ad | 0.30 [0.15, 0.49] | 0.28 [0.15, 0.44] | -0.02 [-0.11, +0.05] | 0.5854 |
| `prose_up_to_k` | 102 | Ads with at least one false concept (%) | 22.5 [12.0, 34.3] | 20.0 [11.0, 30.1] | -2.5 [-8.5, +2.3] | 0.3812 |
| `prose_up_to_k` | 102 | ESCO precision (%) | 74.6 [63.9, 85.6] | 77.6 [68.3, 87.0] | +3.0 [-2.2, +8.3] | 0.2480 |
| `prose_up_to_k` | 102 | ESCO recall (%) | 74.6 [62.1, 85.5] | 81.3 [72.2, 89.7] | +6.7 [+1.5, +14.1] | 0.0016 |
| `prose_up_to_k` | 102 | Top-20 concepts not in the true items' top 20 | 7 [3, 9] | 7 [3, 8] | +0 [-3, +1] | 0.6402 |
| `prose_exactly_k` | 102 | False ESCO concepts per ad | 0.30 [0.15, 0.49] | 0.58 [0.40, 0.77] | +0.28 [+0.15, +0.42] | < 0.0001 |
| `prose_exactly_k` | 102 | Ads with at least one false concept (%) | 22.5 [12.0, 34.3] | 33.7 [24.0, 44.1] | +11.2 [+4.7, +17.9] | 0.0012 |
| `prose_exactly_k` | 102 | ESCO precision (%) | 74.6 [63.9, 85.6] | 62.2 [54.1, 70.6] | -12.4 [-20.5, -5.7] | 0.0004 |
| `prose_exactly_k` | 102 | ESCO recall (%) | 74.6 [62.1, 85.5] | 79.8 [71.8, 87.3] | +5.2 [-1.2, +13.1] | 0.1260 |
| `prose_exactly_k` | 102 | Top-20 concepts not in the true items' top 20 | 7 [3, 9] | 7 [4, 10] | +0 [-2, +3] | 1.0000 |
| `max_k_shown` | 102 | False ESCO concepts per ad | 0.30 [0.15, 0.49] | 0.33 [0.20, 0.49] | +0.03 [-0.06, +0.11] | 0.5604 |
| `max_k_shown` | 102 | Ads with at least one false concept (%) | 22.5 [12.0, 34.3] | 28.4 [17.3, 40.0] | +5.9 [+1.0, +11.6] | 0.0124 |
| `max_k_shown` | 102 | ESCO precision (%) | 74.6 [63.9, 85.6] | 73.8 [64.4, 82.9] | -0.7 [-6.4, +3.9] | 0.7778 |
| `max_k_shown` | 102 | ESCO recall (%) | 74.6 [62.1, 85.5] | 78.7 [68.1, 88.1] | +4.1 [-1.0, +12.0] | 0.2874 |
| `max_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 7 [3, 9] | 8 [4, 9] | +1 [-2, +2] | 1.0000 |
| `min_k_shown` | 102 | False ESCO concepts per ad | 0.30 [0.15, 0.49] | 1.94 [1.50, 2.41] | +1.64 [+1.21, +2.11] | < 0.0001 |
| `min_k_shown` | 102 | Ads with at least one false concept (%) | 22.5 [12.0, 34.3] | 69.6 [57.3, 81.4] | +47.1 [+34.3, +60.0] | < 0.0001 |
| `min_k_shown` | 102 | ESCO precision (%) | 74.6 [63.9, 85.6] | 35.3 [27.9, 43.3] | -39.3 [-50.9, -28.9] | < 0.0001 |
| `min_k_shown` | 102 | ESCO recall (%) | 74.6 [62.1, 85.5] | 88.5 [80.9, 95.2] | +13.9 [+3.4, +26.4] | 0.0104 |
| `min_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 7 [3, 9] | 12 [9, 16] | +5 [+2, +10] | 0.0036 |
| `min_k_shown_fewer_ok` | 102 | False ESCO concepts per ad | 0.30 [0.15, 0.49] | 1.02 [0.72, 1.34] | +0.72 [+0.46, +1.00] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | Ads with at least one false concept (%) | 22.5 [12.0, 34.3] | 46.1 [34.3, 57.8] | +23.5 [+13.0, +34.3] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | ESCO precision (%) | 74.6 [63.9, 85.6] | 48.3 [39.6, 57.6] | -26.3 [-36.9, -17.1] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | ESCO recall (%) | 74.6 [62.1, 85.5] | 79.5 [69.7, 88.1] | +4.9 [-4.7, +15.4] | 0.3616 |
| `min_k_shown_fewer_ok` | 102 | Top-20 concepts not in the true items' top 20 | 7 [3, 9] | 11 [6, 14] | +4 [+0, +7] | 0.0674 |
| `min_k_enforced` | 102 | False ESCO concepts per ad | 0.30 [0.15, 0.49] | 2.94 [2.64, 3.27] | +2.64 [+2.28, +3.01] | < 0.0001 |
| `min_k_enforced` | 102 | Ads with at least one false concept (%) | 22.5 [12.0, 34.3] | 99.0 [97.0, 100.0] | +76.5 [+64.8, +87.1] | < 0.0001 |
| `min_k_enforced` | 102 | ESCO precision (%) | 74.6 [63.9, 85.6] | 26.8 [21.1, 32.8] | -47.8 [-59.2, -37.3] | < 0.0001 |
| `min_k_enforced` | 102 | ESCO recall (%) | 74.6 [62.1, 85.5] | 90.2 [83.3, 96.2] | +15.6 [+5.8, +27.6] | < 0.0001 |
| `min_k_enforced` | 102 | Top-20 concepts not in the true items' top 20 | 7 [3, 9] | 14 [11, 17] | +7 [+3, +12] | 0.0004 |
| `min_k_escape` | 102 | False ESCO concepts per ad | 0.30 [0.15, 0.49] | 0.86 [0.60, 1.15] | +0.56 [+0.34, +0.80] | < 0.0001 |
| `min_k_escape` | 102 | Ads with at least one false concept (%) | 22.5 [12.0, 34.3] | 43.1 [31.0, 55.4] | +20.6 [+10.9, +31.1] | < 0.0001 |
| `min_k_escape` | 102 | ESCO precision (%) | 74.6 [63.9, 85.6] | 55.3 [47.0, 64.4] | -19.3 [-28.4, -11.2] | < 0.0001 |
| `min_k_escape` | 102 | ESCO recall (%) | 74.6 [62.1, 85.5] | 89.3 [82.6, 95.3] | +14.8 [+4.4, +26.9] | 0.0054 |
| `min_k_escape` | 102 | Top-20 concepts not in the true items' top 20 | 7 [3, 9] | 7 [5, 12] | +0 [-1, +5] | 0.3828 |

## 16. Gemma 4 31B (main model alone; not registered), both sets, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 0.48 [0.31, 0.67] | 0.50 [0.36, 0.65] | +0.02 [-0.08, +0.12] | 0.6594 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 28.4 [20.5, 36.8] | 31.9 [24.2, 39.9] | +3.5 [-0.9, +8.2] | 0.1304 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 64.1 [54.9, 74.0] | 63.5 [55.8, 71.5] | -0.5 [-5.8, +4.1] | 0.8190 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 70.6 [63.5, 77.9] | 72.1 [65.6, 78.5] | +1.5 [-1.3, +4.5] | 0.3274 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 8 [4, 13] | 9 [4, 11] | +1 [-4, +2] | 0.8238 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 0.48 [0.31, 0.67] | 1.52 [1.33, 1.72] | +1.05 [+0.86, +1.24] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 28.4 [20.5, 36.8] | 60.9 [54.3, 67.5] | +32.5 [+26.0, +39.5] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 64.1 [54.9, 74.0] | 38.7 [33.6, 44.2] | -25.3 [-33.9, -17.6] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 70.6 [63.5, 77.9] | 79.8 [73.7, 85.5] | +9.2 [+4.6, +14.0] | < 0.0001 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 8 [4, 13] | 14 [7, 14] | +6 [-2, +7] | 0.3758 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 0.48 [0.31, 0.67] | 0.45 [0.32, 0.61] | -0.02 [-0.12, +0.05] | 0.6532 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 28.4 [20.5, 36.8] | 28.9 [21.3, 37.0] | +0.5 [-3.3, +4.2] | 0.9004 |
| `max_k_shown` | 211 | ESCO precision (%) | 64.1 [54.9, 74.0] | 66.0 [58.2, 74.0] | +1.9 [-2.6, +6.5] | 0.4462 |
| `max_k_shown` | 211 | ESCO recall (%) | 70.6 [63.5, 77.9] | 72.9 [65.8, 79.8] | +2.4 [-0.8, +5.5] | 0.1820 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 8 [4, 13] | 8 [4, 11] | +0 [-4, +1] | 0.7612 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 0.48 [0.31, 0.67] | 2.87 [2.61, 3.14] | +2.39 [+2.10, +2.69] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 28.4 [20.5, 36.8] | 88.6 [83.5, 93.3] | +60.2 [+51.7, +68.5] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 64.1 [54.9, 74.0] | 25.1 [21.0, 29.5] | -39.0 [-48.0, -30.6] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 70.6 [63.5, 77.9] | 79.6 [73.6, 85.5] | +9.0 [+4.1, +14.2] | 0.0002 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 8 [4, 13] | 15 [11, 17] | +7 [+1, +11] | 0.0334 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 0.48 [0.31, 0.67] | 0.44 [0.29, 0.61] | -0.04 [-0.17, +0.07] | 0.5936 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 28.4 [20.5, 36.8] | 27.0 [19.3, 35.0] | -1.4 [-7.5, +4.3] | 0.6826 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 64.1 [54.9, 74.0] | 66.4 [58.5, 75.1] | +2.4 [-3.0, +8.8] | 0.4550 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 70.6 [63.5, 77.9] | 72.2 [64.8, 79.3] | +1.6 [-1.3, +4.7] | 0.3882 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 8 [4, 13] | 8 [4, 11] | +0 [-4, +2] | 1.0000 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 0.48 [0.31, 0.67] | 3.10 [2.92, 3.29] | +2.63 [+2.38, +2.86] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 28.4 [20.5, 36.8] | 98.6 [96.8, 100.0] | +70.1 [+61.8, +78.0] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 64.1 [54.9, 74.0] | 23.8 [20.3, 27.6] | -40.2 [-49.3, -31.8] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO recall (%) | 70.6 [63.5, 77.9] | 80.4 [74.5, 86.1] | +9.8 [+4.9, +15.0] | < 0.0001 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 8 [4, 13] | 15 [11, 18] | +7 [+1, +11] | 0.0244 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 0.48 [0.31, 0.67] | 0.80 [0.58, 1.03] | +0.32 [+0.12, +0.52] | 0.0030 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 28.4 [20.5, 36.8] | 35.5 [27.2, 44.1] | +7.1 [-0.9, +15.0] | 0.0908 |
| `min_k_escape` | 211 | ESCO precision (%) | 64.1 [54.9, 74.0] | 51.2 [44.5, 59.0] | -12.9 [-21.2, -4.6] | 0.0034 |
| `min_k_escape` | 211 | ESCO recall (%) | 70.6 [63.5, 77.9] | 69.4 [61.6, 76.7] | -1.2 [-7.7, +4.6] | 0.7718 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 8 [4, 13] | 12 [6, 13] | +4 [-2, +5] | 0.6336 |

Top 20 concepts of the `min_k_shown` outputs: English; computer engineering; cooperate with colleagues; seek innovation in current practices; perform scientific research; automation technology; implement front-end website design; German; develop strategy to solve problems; DevOps; circulate information; teach communication methods; think creatively; industrial research and development; business intelligence; manage personal progression; comply with schedule; manage the customer experience; support managers; project commissioning

Top 20 concepts of the true items of the same ads: English; teach communication methods; SAP Data Services; German; computer engineering; recruit members; design cloud architecture; Danish; perform scientific research; computer science; react to events in time-critical environments; web services; perform business research; systems development life-cycle; Ruby (computer programming); solve technical problems; communication; Java (computer programming); body language; manage budgets

## 17. Gemma 4 31B (main model alone; not registered), job-ad skills, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 109 | False ESCO concepts per ad | 0.68 [0.42, 0.97] | 0.75 [0.52, 1.00] | +0.07 [-0.06, +0.21] | 0.3008 |
| `prose_up_to_k` | 109 | Ads with at least one false concept (%) | 37.6 [25.5, 50.0] | 45.1 [33.3, 57.1] | +7.5 [+2.4, +13.8] | 0.0006 |
| `prose_up_to_k` | 109 | ESCO precision (%) | 49.7 [36.4, 64.4] | 47.2 [36.2, 58.8] | -2.5 [-9.0, +2.7] | 0.3762 |
| `prose_up_to_k` | 109 | ESCO recall (%) | 54.9 [43.3, 66.7] | 54.7 [44.0, 65.2] | -0.2 [-4.2, +3.7] | 0.9980 |
| `prose_up_to_k` | 109 | Top-20 concepts not in the true items' top 20 | 13 [7, 16] | 12 [7, 15] | -1 [-2, +3] | 1.0000 |
| `prose_exactly_k` | 109 | False ESCO concepts per ad | 0.68 [0.42, 0.97] | 2.00 [1.72, 2.29] | +1.32 [+1.07, +1.58] | < 0.0001 |
| `prose_exactly_k` | 109 | Ads with at least one false concept (%) | 37.6 [25.5, 50.0] | 73.2 [65.4, 80.7] | +35.6 [+26.5, +45.2] | < 0.0001 |
| `prose_exactly_k` | 109 | ESCO precision (%) | 49.7 [36.4, 64.4] | 29.2 [22.7, 36.4] | -20.4 [-31.8, -10.8] | < 0.0001 |
| `prose_exactly_k` | 109 | ESCO recall (%) | 54.9 [43.3, 66.7] | 67.8 [58.4, 76.8] | +12.9 [+5.7, +21.1] | 0.0002 |
| `prose_exactly_k` | 109 | Top-20 concepts not in the true items' top 20 | 13 [7, 16] | 16 [9, 17] | +3 [-2, +6] | 0.5412 |
| `max_k_shown` | 109 | False ESCO concepts per ad | 0.68 [0.42, 0.97] | 0.70 [0.47, 0.95] | +0.02 [-0.12, +0.15] | 0.8132 |
| `max_k_shown` | 109 | Ads with at least one false concept (%) | 37.6 [25.5, 50.0] | 41.3 [29.4, 53.3] | +3.7 [-0.9, +9.2] | 0.1808 |
| `max_k_shown` | 109 | ESCO precision (%) | 49.7 [36.4, 64.4] | 50.0 [38.8, 62.1] | +0.3 [-6.2, +6.9] | 0.9616 |
| `max_k_shown` | 109 | ESCO recall (%) | 54.9 [43.3, 66.7] | 57.1 [45.9, 68.0] | +2.3 [-2.9, +7.9] | 0.4996 |
| `max_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 13 [7, 16] | 11 [7, 15] | -2 [-3, +2] | 1.0000 |
| `min_k_shown` | 109 | False ESCO concepts per ad | 0.68 [0.42, 0.97] | 3.13 [2.78, 3.48] | +2.45 [+2.07, +2.83] | < 0.0001 |
| `min_k_shown` | 109 | Ads with at least one false concept (%) | 37.6 [25.5, 50.0] | 94.5 [88.4, 99.1] | +56.9 [+44.6, +69.2] | < 0.0001 |
| `min_k_shown` | 109 | ESCO precision (%) | 49.7 [36.4, 64.4] | 21.1 [16.0, 26.8] | -28.6 [-40.9, -18.2] | < 0.0001 |
| `min_k_shown` | 109 | ESCO recall (%) | 54.9 [43.3, 66.7] | 68.4 [58.8, 78.0] | +13.5 [+6.1, +22.0] | 0.0006 |
| `min_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 13 [7, 16] | 18 [12, 19] | +5 [+0, +9] | 0.0880 |
| `min_k_shown_fewer_ok` | 109 | False ESCO concepts per ad | 0.68 [0.42, 0.97] | 0.56 [0.34, 0.80] | -0.12 [-0.36, +0.06] | 0.2748 |
| `min_k_shown_fewer_ok` | 109 | Ads with at least one false concept (%) | 37.6 [25.5, 50.0] | 32.1 [20.8, 43.9] | -5.5 [-13.8, +1.9] | 0.1930 |
| `min_k_shown_fewer_ok` | 109 | ESCO precision (%) | 49.7 [36.4, 64.4] | 55.5 [43.8, 68.5] | +5.8 [-1.9, +15.4] | 0.1608 |
| `min_k_shown_fewer_ok` | 109 | ESCO recall (%) | 54.9 [43.3, 66.7] | 57.1 [45.3, 68.7] | +2.3 [-1.7, +7.1] | 0.3956 |
| `min_k_shown_fewer_ok` | 109 | Top-20 concepts not in the true items' top 20 | 13 [7, 16] | 12 [6, 14] | -1 [-5, +1] | 0.8084 |
| `min_k_enforced` | 109 | False ESCO concepts per ad | 0.68 [0.42, 0.97] | 3.31 [3.06, 3.56] | +2.63 [+2.31, +2.96] | < 0.0001 |
| `min_k_enforced` | 109 | Ads with at least one false concept (%) | 37.6 [25.5, 50.0] | 100.0 [100.0, 100.0] | +62.4 [+50.0, +74.5] | < 0.0001 |
| `min_k_enforced` | 109 | ESCO precision (%) | 49.7 [36.4, 64.4] | 20.3 [15.5, 25.5] | -29.4 [-41.9, -18.6] | < 0.0001 |
| `min_k_enforced` | 109 | ESCO recall (%) | 54.9 [43.3, 66.7] | 69.2 [59.8, 78.4] | +14.3 [+6.7, +22.8] | 0.0002 |
| `min_k_enforced` | 109 | Top-20 concepts not in the true items' top 20 | 13 [7, 16] | 17 [13, 19] | +4 [+0, +9] | 0.0760 |
| `min_k_escape` | 109 | False ESCO concepts per ad | 0.68 [0.42, 0.97] | 1.06 [0.71, 1.42] | +0.38 [+0.04, +0.71] | 0.0340 |
| `min_k_escape` | 109 | Ads with at least one false concept (%) | 37.6 [25.5, 50.0] | 44.0 [32.1, 56.4] | +6.4 [-5.1, +17.6] | 0.3194 |
| `min_k_escape` | 109 | ESCO precision (%) | 49.7 [36.4, 64.4] | 39.5 [30.4, 50.3] | -10.2 [-21.0, +0.6] | 0.0680 |
| `min_k_escape` | 109 | ESCO recall (%) | 54.9 [43.3, 66.7] | 56.4 [44.7, 67.8] | +1.5 [-7.1, +10.0] | 0.7938 |
| `min_k_escape` | 109 | Top-20 concepts not in the true items' top 20 | 13 [7, 16] | 13 [8, 16] | +0 [-3, +5] | 0.6652 |

## 18. Gemma 4 31B (main model alone; not registered), job-ad knowledge, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 102 | False ESCO concepts per ad | 0.26 [0.12, 0.44] | 0.24 [0.12, 0.37] | -0.03 [-0.14, +0.09] | 0.6252 |
| `prose_up_to_k` | 102 | Ads with at least one false concept (%) | 18.6 [9.2, 29.1] | 17.8 [9.4, 27.5] | -0.8 [-7.9, +6.3] | 0.8560 |
| `prose_up_to_k` | 102 | ESCO precision (%) | 79.9 [70.4, 89.8] | 82.2 [73.8, 90.1] | +2.4 [-5.4, +8.6] | 0.5236 |
| `prose_up_to_k` | 102 | ESCO recall (%) | 87.7 [80.0, 94.7] | 91.0 [85.3, 96.1] | +3.3 [-0.3, +8.0] | 0.0914 |
| `prose_up_to_k` | 102 | Top-20 concepts not in the true items' top 20 | 5 [2, 8] | 4 [1, 7] | -1 [-4, +1] | 0.5814 |
| `prose_exactly_k` | 102 | False ESCO concepts per ad | 0.26 [0.12, 0.44] | 1.01 [0.76, 1.28] | +0.75 [+0.50, +1.03] | < 0.0001 |
| `prose_exactly_k` | 102 | Ads with at least one false concept (%) | 18.6 [9.2, 29.1] | 47.8 [37.6, 58.2] | +29.2 [+20.0, +38.8] | < 0.0001 |
| `prose_exactly_k` | 102 | ESCO precision (%) | 79.9 [70.4, 89.8] | 52.3 [43.8, 60.8] | -27.5 [-39.2, -17.4] | < 0.0001 |
| `prose_exactly_k` | 102 | ESCO recall (%) | 87.7 [80.0, 94.7] | 92.8 [87.7, 97.1] | +5.1 [-1.4, +12.0] | 0.1360 |
| `prose_exactly_k` | 102 | Top-20 concepts not in the true items' top 20 | 5 [2, 8] | 6 [4, 12] | +1 [-1, +7] | 0.1578 |
| `max_k_shown` | 102 | False ESCO concepts per ad | 0.26 [0.12, 0.44] | 0.20 [0.09, 0.33] | -0.07 [-0.15, +0.00] | 0.0606 |
| `max_k_shown` | 102 | Ads with at least one false concept (%) | 18.6 [9.2, 29.1] | 15.7 [7.4, 25.3] | -2.9 [-9.5, +2.0] | 0.4268 |
| `max_k_shown` | 102 | ESCO precision (%) | 79.9 [70.4, 89.8] | 84.6 [76.8, 92.4] | +4.8 [+0.4, +9.2] | 0.0288 |
| `max_k_shown` | 102 | ESCO recall (%) | 87.7 [80.0, 94.7] | 90.2 [83.0, 96.2] | +2.5 [+0.0, +6.4] | 0.2688 |
| `max_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 5 [2, 8] | 3 [1, 6] | -2 [-3, +0] | 0.5106 |
| `min_k_shown` | 102 | False ESCO concepts per ad | 0.26 [0.12, 0.44] | 2.60 [2.20, 2.99] | +2.33 [+1.91, +2.76] | < 0.0001 |
| `min_k_shown` | 102 | Ads with at least one false concept (%) | 18.6 [9.2, 29.1] | 82.4 [73.5, 90.2] | +63.7 [+52.0, +75.0] | < 0.0001 |
| `min_k_shown` | 102 | ESCO precision (%) | 79.9 [70.4, 89.8] | 29.7 [22.9, 37.2] | -50.1 [-61.5, -39.9] | < 0.0001 |
| `min_k_shown` | 102 | ESCO recall (%) | 87.7 [80.0, 94.7] | 91.8 [85.8, 96.8] | +4.1 [-3.5, +11.9] | 0.3508 |
| `min_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 5 [2, 8] | 13 [9, 17] | +8 [+4, +13] | 0.0002 |
| `min_k_shown_fewer_ok` | 102 | False ESCO concepts per ad | 0.26 [0.12, 0.44] | 0.31 [0.16, 0.50] | +0.05 [-0.05, +0.15] | 0.3716 |
| `min_k_shown_fewer_ok` | 102 | Ads with at least one false concept (%) | 18.6 [9.2, 29.1] | 21.6 [11.7, 32.7] | +2.9 [-5.8, +11.8] | 0.5844 |
| `min_k_shown_fewer_ok` | 102 | ESCO precision (%) | 79.9 [70.4, 89.8] | 77.1 [68.4, 86.9] | -2.7 [-9.0, +3.4] | 0.3744 |
| `min_k_shown_fewer_ok` | 102 | ESCO recall (%) | 87.7 [80.0, 94.7] | 88.5 [81.1, 94.7] | +0.8 [-4.8, +5.8] | 0.8986 |
| `min_k_shown_fewer_ok` | 102 | Top-20 concepts not in the true items' top 20 | 5 [2, 8] | 5 [2, 8] | +0 [-1, +3] | 0.9296 |
| `min_k_enforced` | 102 | False ESCO concepts per ad | 0.26 [0.12, 0.44] | 2.88 [2.60, 3.16] | +2.62 [+2.29, +2.94] | < 0.0001 |
| `min_k_enforced` | 102 | Ads with at least one false concept (%) | 18.6 [9.2, 29.1] | 97.1 [93.3, 100.0] | +78.4 [+68.0, +88.2] | < 0.0001 |
| `min_k_enforced` | 102 | ESCO precision (%) | 79.9 [70.4, 89.8] | 27.8 [22.0, 33.8] | -52.1 [-63.0, -42.3] | < 0.0001 |
| `min_k_enforced` | 102 | ESCO recall (%) | 87.7 [80.0, 94.7] | 92.6 [86.7, 97.5] | +4.9 [-2.5, +12.6] | 0.2344 |
| `min_k_enforced` | 102 | Top-20 concepts not in the true items' top 20 | 5 [2, 8] | 15 [10, 17] | +10 [+5, +13] | < 0.0001 |
| `min_k_escape` | 102 | False ESCO concepts per ad | 0.26 [0.12, 0.44] | 0.53 [0.29, 0.80] | +0.26 [+0.06, +0.50] | 0.0070 |
| `min_k_escape` | 102 | Ads with at least one false concept (%) | 18.6 [9.2, 29.1] | 26.5 [15.8, 38.0] | +7.8 [-2.0, +18.2] | 0.1448 |
| `min_k_escape` | 102 | ESCO precision (%) | 79.9 [70.4, 89.8] | 65.4 [54.7, 77.5] | -14.5 [-26.1, -4.0] | 0.0050 |
| `min_k_escape` | 102 | ESCO recall (%) | 87.7 [80.0, 94.7] | 83.6 [72.8, 92.4] | -4.1 [-15.0, +5.0] | 0.4624 |
| `min_k_escape` | 102 | Top-20 concepts not in the true items' top 20 | 5 [2, 8] | 8 [4, 11] | +3 [-1, +6] | 0.2380 |

## 19. Olmo 3.1 32B (main model alone; not registered), both sets, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 4.76 [3.88, 5.67] | 2.66 [2.31, 3.00] | -2.10 [-2.81, -1.43] | < 0.0001 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 63.0 [54.7, 71.5] | 72.3 [65.6, 78.9] | +9.3 [+3.6, +15.0] | 0.0006 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 12.8 [10.2, 15.9] | 18.4 [15.0, 22.0] | +5.6 [+3.5, +7.7] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 57.6 [49.6, 65.7] | 49.5 [42.5, 56.7] | -8.2 [-13.2, -3.1] | 0.0020 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 15 [13, 18] | 14 [11, 18] | -1 [-4, +2] | 0.6988 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 4.76 [3.88, 5.67] | 2.47 [2.25, 2.69] | -2.29 [-3.09, -1.55] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 63.0 [54.7, 71.5] | 77.4 [72.0, 82.8] | +14.4 [+8.7, +20.2] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 12.8 [10.2, 15.9] | 19.1 [15.8, 22.6] | +6.3 [+4.0, +8.6] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 57.6 [49.6, 65.7] | 48.2 [41.6, 55.1] | -9.5 [-15.1, -3.6] | 0.0022 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 15 [13, 18] | 14 [11, 18] | -1 [-4, +2] | 0.7048 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 4.76 [3.88, 5.67] | 2.09 [1.76, 2.46] | -2.66 [-3.44, -1.92] | < 0.0001 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 63.0 [54.7, 71.5] | 62.6 [54.3, 71.1] | -0.5 [-6.0, +5.1] | 0.9496 |
| `max_k_shown` | 211 | ESCO precision (%) | 12.8 [10.2, 15.9] | 21.8 [17.6, 26.5] | +9.0 [+6.1, +12.1] | < 0.0001 |
| `max_k_shown` | 211 | ESCO recall (%) | 57.6 [49.6, 65.7] | 48.2 [40.7, 56.2] | -9.4 [-15.3, -3.1] | 0.0044 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 15 [13, 18] | 15 [12, 18] | +0 [-4, +2] | 0.7920 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 4.76 [3.88, 5.67] | 4.78 [4.03, 5.60] | +0.02 [-0.44, +0.50] | 0.9346 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 63.0 [54.7, 71.5] | 74.9 [67.6, 82.2] | +11.8 [+6.7, +17.5] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 12.8 [10.2, 15.9] | 13.2 [10.7, 16.3] | +0.5 [-1.1, +1.9] | 0.5194 |
| `min_k_shown` | 211 | ESCO recall (%) | 57.6 [49.6, 65.7] | 60.4 [52.7, 68.3] | +2.7 [-2.3, +8.1] | 0.3300 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 15 [13, 18] | 15 [13, 18] | +0 [-2, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 4.76 [3.88, 5.67] | 0.76 [0.45, 1.11] | -4.00 [-4.86, -3.20] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 63.0 [54.7, 71.5] | 19.4 [12.8, 26.7] | -43.6 [-52.0, -35.7] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 12.8 [10.2, 15.9] | 25.9 [18.4, 36.4] | +13.2 [+6.5, +22.5] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 57.6 [49.6, 65.7] | 22.0 [14.7, 29.6] | -35.7 [-44.7, -26.6] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 15 [13, 18] | 14 [12, 18] | -1 [-4, +2] | 0.8092 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 4.76 [3.88, 5.67] | 6.55 [5.83, 7.37] | +1.80 [+1.03, +2.65] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 63.0 [54.7, 71.5] | 100.0 [100.0, 100.0] | +37.0 [+28.5, +45.3] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 12.8 [10.2, 15.9] | 10.7 [8.6, 13.0] | -2.1 [-4.3, -0.3] | 0.0232 |
| `min_k_enforced` | 211 | ESCO recall (%) | 57.6 [49.6, 65.7] | 65.1 [57.7, 72.7] | +7.5 [+1.8, +13.6] | 0.0108 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 15 [13, 18] | 14 [13, 18] | -1 [-2, +2] | 1.0000 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 4.76 [3.88, 5.67] | 4.29 [3.53, 5.12] | -0.47 [-1.26, +0.31] | 0.2304 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 63.0 [54.7, 71.5] | 64.0 [55.4, 72.6] | +0.9 [-8.3, +9.9] | 0.8834 |
| `min_k_escape` | 211 | ESCO precision (%) | 12.8 [10.2, 15.9] | 14.0 [11.4, 17.0] | +1.2 [-0.8, +3.2] | 0.2242 |
| `min_k_escape` | 211 | ESCO recall (%) | 57.6 [49.6, 65.7] | 57.6 [49.6, 65.7] | +0.0 [-6.2, +6.4] | 1.0000 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 15 [13, 18] | 15 [12, 18] | +0 [-3, +2] | 1.0000 |

Top 20 concepts of the `min_k_shown` outputs: English; teach communication methods; Java (computer programming); react to events in time-critical environments; Python (computer programming); JavaScript; manage ICT virtualisation environments; cloud technologies; understand written English; computer engineering; maintain internal communication systems; seek innovation in current practices; query languages; apply technical communication skills; Agile development; design thinking; continuous improvement philosophies; work in an international environment; service-oriented modelling; strategic planning

Top 20 concepts of the true items of the same ads: English; teach communication methods; SAP Data Services; German; computer engineering; recruit members; design cloud architecture; Danish; perform scientific research; computer science; react to events in time-critical environments; web services; perform business research; systems development life-cycle; Ruby (computer programming); solve technical problems; communication; Java (computer programming); body language; manage budgets

## 20. Olmo 3.1 32B (main model alone; not registered), job-ad skills, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 109 | False ESCO concepts per ad | 4.71 [3.45, 6.05] | 2.91 [2.43, 3.42] | -1.80 [-2.88, -0.81] | 0.0004 |
| `prose_up_to_k` | 109 | Ads with at least one false concept (%) | 65.1 [52.8, 77.4] | 77.1 [68.3, 85.5] | +11.9 [+2.8, +21.2] | 0.0108 |
| `prose_up_to_k` | 109 | ESCO precision (%) | 9.7 [6.6, 13.5] | 11.3 [7.7, 15.5] | +1.6 [-1.3, +4.3] | 0.3022 |
| `prose_up_to_k` | 109 | ESCO recall (%) | 41.4 [30.6, 52.3] | 30.2 [21.8, 39.2] | -11.1 [-19.7, -2.6] | 0.0128 |
| `prose_up_to_k` | 109 | Top-20 concepts not in the true items' top 20 | 18 [16, 20] | 18 [15, 20] | +0 [-3, +2] | 1.0000 |
| `prose_exactly_k` | 109 | False ESCO concepts per ad | 4.71 [3.45, 6.05] | 2.84 [2.52, 3.18] | -1.86 [-3.08, -0.76] | 0.0004 |
| `prose_exactly_k` | 109 | Ads with at least one false concept (%) | 65.1 [52.8, 77.4] | 83.3 [76.7, 89.6] | +18.2 [+8.7, +27.8] | < 0.0001 |
| `prose_exactly_k` | 109 | ESCO precision (%) | 9.7 [6.6, 13.5] | 10.9 [7.3, 14.9] | +1.2 [-2.0, +4.3] | 0.4786 |
| `prose_exactly_k` | 109 | ESCO recall (%) | 41.4 [30.6, 52.3] | 28.6 [20.3, 37.3] | -12.8 [-22.0, -3.0] | 0.0116 |
| `prose_exactly_k` | 109 | Top-20 concepts not in the true items' top 20 | 18 [16, 20] | 18 [15, 20] | +0 [-3, +2] | 0.9978 |
| `max_k_shown` | 109 | False ESCO concepts per ad | 4.71 [3.45, 6.05] | 2.57 [2.03, 3.16] | -2.14 [-3.32, -1.07] | < 0.0001 |
| `max_k_shown` | 109 | Ads with at least one false concept (%) | 65.1 [52.8, 77.4] | 67.9 [56.5, 79.2] | +2.8 [-5.6, +11.0] | 0.5788 |
| `max_k_shown` | 109 | ESCO precision (%) | 9.7 [6.6, 13.5] | 12.2 [7.9, 17.3] | +2.5 [-1.0, +6.2] | 0.1692 |
| `max_k_shown` | 109 | ESCO recall (%) | 41.4 [30.6, 52.3] | 29.3 [19.4, 40.0] | -12.0 [-21.8, -1.5] | 0.0316 |
| `max_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 18 [16, 20] | 18 [15, 20] | +0 [-3, +2] | 1.0000 |
| `min_k_shown` | 109 | False ESCO concepts per ad | 4.71 [3.45, 6.05] | 4.95 [3.83, 6.16] | +0.25 [-0.27, +0.81] | 0.3808 |
| `min_k_shown` | 109 | Ads with at least one false concept (%) | 65.1 [52.8, 77.4] | 77.1 [66.4, 87.2] | +11.9 [+4.8, +20.2] | < 0.0001 |
| `min_k_shown` | 109 | ESCO precision (%) | 9.7 [6.6, 13.5] | 10.6 [7.2, 14.7] | +0.9 [-1.0, +2.9] | 0.3488 |
| `min_k_shown` | 109 | ESCO recall (%) | 41.4 [30.6, 52.3] | 48.1 [36.2, 60.0] | +6.8 [-1.6, +15.8] | 0.1400 |
| `min_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 18 [16, 20] | 18 [16, 20] | +0 [-2, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 109 | False ESCO concepts per ad | 4.71 [3.45, 6.05] | 1.07 [0.54, 1.69] | -3.63 [-4.86, -2.54] | < 0.0001 |
| `min_k_shown_fewer_ok` | 109 | Ads with at least one false concept (%) | 65.1 [52.8, 77.4] | 21.1 [11.6, 31.5] | -44.0 [-56.4, -32.1] | < 0.0001 |
| `min_k_shown_fewer_ok` | 109 | ESCO precision (%) | 9.7 [6.6, 13.5] | 11.4 [5.6, 17.4] | +1.7 [-4.2, +7.5] | 0.5690 |
| `min_k_shown_fewer_ok` | 109 | ESCO recall (%) | 41.4 [30.6, 52.3] | 11.3 [4.2, 19.9] | -30.1 [-42.5, -17.6] | < 0.0001 |
| `min_k_shown_fewer_ok` | 109 | Top-20 concepts not in the true items' top 20 | 18 [16, 20] | 17 [15, 20] | -1 [-3, +2] | 0.9898 |
| `min_k_enforced` | 109 | False ESCO concepts per ad | 4.71 [3.45, 6.05] | 6.02 [5.10, 7.07] | +1.31 [+0.49, +2.13] | 0.0022 |
| `min_k_enforced` | 109 | Ads with at least one false concept (%) | 65.1 [52.8, 77.4] | 100.0 [100.0, 100.0] | +34.9 [+22.6, +47.2] | < 0.0001 |
| `min_k_enforced` | 109 | ESCO precision (%) | 9.7 [6.6, 13.5] | 9.6 [6.7, 13.0] | -0.0 [-2.6, +2.1] | 0.9580 |
| `min_k_enforced` | 109 | ESCO recall (%) | 41.4 [30.6, 52.3] | 52.6 [40.6, 64.7] | +11.3 [+2.0, +21.3] | 0.0214 |
| `min_k_enforced` | 109 | Top-20 concepts not in the true items' top 20 | 18 [16, 20] | 18 [15, 20] | +0 [-2, +2] | 1.0000 |
| `min_k_escape` | 109 | False ESCO concepts per ad | 4.71 [3.45, 6.05] | 3.61 [2.60, 4.82] | -1.09 [-2.32, +0.09] | 0.0730 |
| `min_k_escape` | 109 | Ads with at least one false concept (%) | 65.1 [52.8, 77.4] | 58.7 [46.4, 71.4] | -6.4 [-19.3, +6.4] | 0.3668 |
| `min_k_escape` | 109 | ESCO precision (%) | 9.7 [6.6, 13.5] | 11.7 [7.9, 16.3] | +2.0 [-1.0, +5.3] | 0.2096 |
| `min_k_escape` | 109 | ESCO recall (%) | 41.4 [30.6, 52.3] | 39.1 [27.1, 51.9] | -2.3 [-12.1, +8.1] | 0.6932 |
| `min_k_escape` | 109 | Top-20 concepts not in the true items' top 20 | 18 [16, 20] | 18 [15, 20] | +0 [-3, +2] | 1.0000 |

## 21. Olmo 3.1 32B (main model alone; not registered), job-ad knowledge, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 102 | False ESCO concepts per ad | 4.81 [3.47, 6.25] | 2.39 [1.91, 2.90] | -2.42 [-3.48, -1.42] | < 0.0001 |
| `prose_up_to_k` | 102 | Ads with at least one false concept (%) | 60.8 [47.6, 73.6] | 67.3 [56.1, 77.9] | +6.5 [+0.2, +13.7] | 0.0446 |
| `prose_up_to_k` | 102 | ESCO precision (%) | 15.8 [11.4, 21.8] | 26.1 [20.4, 32.7] | +10.3 [+6.8, +13.4] | < 0.0001 |
| `prose_up_to_k` | 102 | ESCO recall (%) | 75.4 [65.0, 85.0] | 70.5 [61.4, 79.6] | -4.9 [-10.8, +0.9] | 0.0950 |
| `prose_up_to_k` | 102 | Top-20 concepts not in the true items' top 20 | 17 [14, 19] | 15 [9, 16] | -2 [-7, -1] | 0.0346 |
| `prose_exactly_k` | 102 | False ESCO concepts per ad | 4.81 [3.47, 6.25] | 2.06 [1.76, 2.37] | -2.75 [-4.00, -1.59] | < 0.0001 |
| `prose_exactly_k` | 102 | Ads with at least one false concept (%) | 60.8 [47.6, 73.6] | 71.2 [62.0, 79.8] | +10.4 [+2.9, +18.6] | 0.0056 |
| `prose_exactly_k` | 102 | ESCO precision (%) | 15.8 [11.4, 21.8] | 28.7 [23.0, 35.1] | +12.9 [+8.7, +16.8] | < 0.0001 |
| `prose_exactly_k` | 102 | ESCO recall (%) | 75.4 [65.0, 85.0] | 69.5 [60.2, 79.0] | -5.9 [-12.4, +0.6] | 0.0812 |
| `prose_exactly_k` | 102 | Top-20 concepts not in the true items' top 20 | 17 [14, 19] | 16 [9, 16] | -1 [-8, -1] | 0.0292 |
| `max_k_shown` | 102 | False ESCO concepts per ad | 4.81 [3.47, 6.25] | 1.59 [1.17, 2.03] | -3.23 [-4.41, -2.15] | < 0.0001 |
| `max_k_shown` | 102 | Ads with at least one false concept (%) | 60.8 [47.6, 73.6] | 56.9 [43.7, 69.9] | -3.9 [-11.7, +3.0] | 0.3414 |
| `max_k_shown` | 102 | ESCO precision (%) | 15.8 [11.4, 21.8] | 34.1 [26.4, 43.5] | +18.4 [+13.3, +24.1] | < 0.0001 |
| `max_k_shown` | 102 | ESCO recall (%) | 75.4 [65.0, 85.0] | 68.9 [58.6, 79.0] | -6.6 [-13.8, +0.7] | 0.0868 |
| `max_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 17 [14, 19] | 13 [9, 16] | -4 [-7, +0] | 0.0550 |
| `min_k_shown` | 102 | False ESCO concepts per ad | 4.81 [3.47, 6.25] | 4.60 [3.57, 5.69] | -0.22 [-1.20, +0.68] | 0.6614 |
| `min_k_shown` | 102 | Ads with at least one false concept (%) | 60.8 [47.6, 73.6] | 72.5 [60.8, 83.3] | +11.8 [+3.8, +21.0] | 0.0024 |
| `min_k_shown` | 102 | ESCO precision (%) | 15.8 [11.4, 21.8] | 16.1 [12.1, 21.0] | +0.3 [-2.9, +2.9] | 0.8008 |
| `min_k_shown` | 102 | ESCO recall (%) | 75.4 [65.0, 85.0] | 73.8 [64.2, 82.9] | -1.6 [-7.3, +3.5] | 0.7014 |
| `min_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 17 [14, 19] | 18 [14, 19] | +1 [-2, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 102 | False ESCO concepts per ad | 4.81 [3.47, 6.25] | 0.42 [0.19, 0.70] | -4.39 [-5.80, -3.09] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | Ads with at least one false concept (%) | 60.8 [47.6, 73.6] | 17.6 [8.9, 27.1] | -43.1 [-55.9, -30.8] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | ESCO precision (%) | 15.8 [11.4, 21.8] | 48.8 [32.5, 69.2] | +33.0 [+18.4, +51.5] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | ESCO recall (%) | 75.4 [65.0, 85.0] | 33.6 [20.5, 46.6] | -41.8 [-55.4, -29.2] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | Top-20 concepts not in the true items' top 20 | 17 [14, 19] | 11 [8, 15] | -6 [-9, -1] | 0.0430 |
| `min_k_enforced` | 102 | False ESCO concepts per ad | 4.81 [3.47, 6.25] | 7.13 [6.03, 8.36] | +2.31 [+0.90, +3.88] | 0.0004 |
| `min_k_enforced` | 102 | Ads with at least one false concept (%) | 60.8 [47.6, 73.6] | 100.0 [100.0, 100.0] | +39.2 [+26.4, +52.4] | < 0.0001 |
| `min_k_enforced` | 102 | ESCO precision (%) | 15.8 [11.4, 21.8] | 11.7 [8.7, 15.1] | -4.1 [-8.8, -1.0] | 0.0058 |
| `min_k_enforced` | 102 | ESCO recall (%) | 75.4 [65.0, 85.0] | 78.7 [70.4, 86.6] | +3.3 [-3.0, +10.1] | 0.4476 |
| `min_k_enforced` | 102 | Top-20 concepts not in the true items' top 20 | 17 [14, 19] | 18 [15, 19] | +1 [-1, +4] | 0.8668 |
| `min_k_escape` | 102 | False ESCO concepts per ad | 4.81 [3.47, 6.25] | 5.01 [3.85, 6.20] | +0.20 [-0.89, +1.31] | 0.7586 |
| `min_k_escape` | 102 | Ads with at least one false concept (%) | 60.8 [47.6, 73.6] | 69.6 [56.7, 81.6] | +8.8 [-4.0, +21.8] | 0.2118 |
| `min_k_escape` | 102 | ESCO precision (%) | 15.8 [11.4, 21.8] | 15.7 [12.3, 19.9] | -0.1 [-3.7, +2.4] | 0.9728 |
| `min_k_escape` | 102 | ESCO recall (%) | 75.4 [65.0, 85.0] | 77.9 [69.3, 85.9] | +2.5 [-4.9, +9.9] | 0.6050 |
| `min_k_escape` | 102 | Top-20 concepts not in the true items' top 20 | 17 [14, 19] | 18 [14, 19] | +1 [-2, +3] | 1.0000 |

## 22. Ministral 3 14B (main model alone; not registered), both sets, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 4.06 [3.22, 4.95] | 2.41 [2.16, 2.67] | -1.65 [-2.39, -0.96] | < 0.0001 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 75.8 [68.3, 83.0] | 83.9 [78.9, 88.7] | +8.1 [+2.0, +14.4] | 0.0066 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 16.2 [12.6, 20.8] | 22.4 [18.4, 26.6] | +6.2 [+3.1, +8.9] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 65.1 [57.3, 72.9] | 57.6 [50.6, 64.7] | -7.5 [-13.7, -1.2] | 0.0220 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 16 [11, 17] | +0 [-6, +1] | 0.2988 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 4.06 [3.22, 4.95] | 2.55 [2.32, 2.77] | -1.52 [-2.26, -0.81] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 75.8 [68.3, 83.0] | 84.7 [79.7, 89.4] | +8.9 [+3.7, +14.2] | 0.0008 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 16.2 [12.6, 20.8] | 22.1 [18.4, 26.0] | +5.8 [+2.8, +8.3] | 0.0006 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 65.1 [57.3, 72.9] | 59.6 [52.9, 66.5] | -5.5 [-11.8, +0.1] | 0.0558 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 15 [11, 17] | -1 [-5, +1] | 0.3864 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 4.06 [3.22, 4.95] | 2.01 [1.64, 2.43] | -2.05 [-2.75, -1.40] | < 0.0001 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 75.8 [68.3, 83.0] | 66.4 [58.6, 74.0] | -9.5 [-15.5, -3.7] | 0.0012 |
| `max_k_shown` | 211 | ESCO precision (%) | 16.2 [12.6, 20.8] | 27.0 [21.7, 33.0] | +10.7 [+7.7, +14.2] | < 0.0001 |
| `max_k_shown` | 211 | ESCO recall (%) | 65.1 [57.3, 72.9] | 61.6 [53.8, 69.5] | -3.5 [-7.3, +0.0] | 0.0582 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 17 [11, 18] | +1 [-5, +1] | 0.4072 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 4.06 [3.22, 4.95] | 4.27 [3.64, 4.98] | +0.21 [-0.33, +0.67] | 0.3996 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 75.8 [68.3, 83.0] | 85.3 [79.4, 90.9] | +9.5 [+4.6, +14.6] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 16.2 [12.6, 20.8] | 15.2 [12.2, 18.8] | -1.0 [-3.2, +0.9] | 0.2798 |
| `min_k_shown` | 211 | ESCO recall (%) | 65.1 [57.3, 72.9] | 63.5 [55.9, 71.1] | -1.6 [-6.3, +3.7] | 0.5548 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 17 [12, 19] | +1 [-3, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 4.06 [3.22, 4.95] | 0.61 [0.41, 0.84] | -3.45 [-4.34, -2.63] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 75.8 [68.3, 83.0] | 30.3 [22.4, 38.9] | -45.5 [-54.8, -36.2] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 16.2 [12.6, 20.8] | 48.0 [39.1, 57.9] | +31.7 [+23.6, +41.0] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 65.1 [57.3, 72.9] | 46.3 [37.6, 55.0] | -18.8 [-26.3, -12.0] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 13 [8, 15] | -3 [-9, -1] | 0.0254 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 4.06 [3.22, 4.95] | 4.03 [3.57, 4.57] | -0.03 [-0.67, +0.59] | 0.9228 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 75.8 [68.3, 83.0] | 97.6 [95.3, 99.5] | +21.8 [+14.6, +29.2] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 16.2 [12.6, 20.8] | 16.1 [13.1, 19.5] | -0.1 [-3.0, +2.2] | 0.9192 |
| `min_k_enforced` | 211 | ESCO recall (%) | 65.1 [57.3, 72.9] | 63.9 [56.6, 71.4] | -1.2 [-7.1, +4.9] | 0.7406 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 16 [13, 19] | +0 [-3, +2] | 1.0000 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 4.06 [3.22, 4.95] | 0.48 [0.23, 0.79] | -3.58 [-4.50, -2.72] | < 0.0001 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 75.8 [68.3, 83.0] | 14.7 [9.0, 21.0] | -61.1 [-69.9, -52.3] | < 0.0001 |
| `min_k_escape` | 211 | ESCO precision (%) | 16.2 [12.6, 20.8] | 29.9 [18.9, 45.8] | +13.6 [+2.8, +29.7] | 0.0128 |
| `min_k_escape` | 211 | ESCO recall (%) | 65.1 [57.3, 72.9] | 16.9 [10.5, 23.7] | -48.2 [-58.0, -38.7] | < 0.0001 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 16 [13, 19] | +0 [-4, +4] | 1.0000 |

Top 20 concepts of the `min_k_shown` outputs: English; industrial research and development; cooperate with colleagues; build team spirit; Agile development; DevOps; seek innovation in current practices; systems development life-cycle; web programming; statistics; computer engineering; SAP R3; think creatively; design thinking; develop test procedures; automation technology; continuous improvement philosophies; work in an international environment; project commissioning; work in shifts

Top 20 concepts of the true items of the same ads: English; teach communication methods; SAP Data Services; German; computer engineering; recruit members; design cloud architecture; Danish; perform scientific research; computer science; react to events in time-critical environments; web services; perform business research; systems development life-cycle; Ruby (computer programming); solve technical problems; communication; Java (computer programming); body language; manage budgets

## 23. Ministral 3 14B (main model alone; not registered), job-ad skills, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 109 | False ESCO concepts per ad | 3.35 [2.55, 4.24] | 2.83 [2.56, 3.10] | -0.52 [-1.28, +0.17] | 0.1402 |
| `prose_up_to_k` | 109 | Ads with at least one false concept (%) | 86.2 [77.1, 94.3] | 96.9 [94.2, 99.1] | +10.6 [+3.2, +19.1] | 0.0020 |
| `prose_up_to_k` | 109 | ESCO precision (%) | 15.7 [10.8, 22.0] | 14.8 [10.4, 19.5] | -0.9 [-5.2, +2.3] | 0.6030 |
| `prose_up_to_k` | 109 | ESCO recall (%) | 51.1 [40.0, 62.6] | 40.2 [31.0, 49.6] | -11.0 [-20.4, -3.1] | 0.0040 |
| `prose_up_to_k` | 109 | Top-20 concepts not in the true items' top 20 | 18 [14, 20] | 18 [13, 19] | +0 [-4, +2] | 0.6280 |
| `prose_exactly_k` | 109 | False ESCO concepts per ad | 3.35 [2.55, 4.24] | 2.95 [2.73, 3.17] | -0.40 [-1.19, +0.32] | 0.2888 |
| `prose_exactly_k` | 109 | Ads with at least one false concept (%) | 86.2 [77.1, 94.3] | 96.1 [93.6, 98.2] | +9.9 [+3.6, +17.1] | 0.0004 |
| `prose_exactly_k` | 109 | ESCO precision (%) | 15.7 [10.8, 22.0] | 16.2 [11.8, 20.9] | +0.4 [-3.4, +3.3] | 0.8054 |
| `prose_exactly_k` | 109 | ESCO recall (%) | 51.1 [40.0, 62.6] | 46.6 [37.0, 56.2] | -4.5 [-13.3, +2.9] | 0.2694 |
| `prose_exactly_k` | 109 | Top-20 concepts not in the true items' top 20 | 18 [14, 20] | 18 [12, 18] | +0 [-5, +1] | 0.4210 |
| `max_k_shown` | 109 | False ESCO concepts per ad | 3.35 [2.55, 4.24] | 2.56 [2.01, 3.17] | -0.79 [-1.19, -0.43] | < 0.0001 |
| `max_k_shown` | 109 | Ads with at least one false concept (%) | 86.2 [77.1, 94.3] | 84.4 [75.0, 92.6] | -1.8 [-6.7, +1.9] | 0.5800 |
| `max_k_shown` | 109 | ESCO precision (%) | 15.7 [10.8, 22.0] | 18.9 [13.1, 26.0] | +3.2 [+1.2, +5.3] | 0.0014 |
| `max_k_shown` | 109 | ESCO recall (%) | 51.1 [40.0, 62.6] | 48.9 [38.3, 60.1] | -2.3 [-6.4, +0.9] | 0.3392 |
| `max_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 18 [14, 20] | 18 [12, 19] | +0 [-4, +1] | 0.5476 |
| `min_k_shown` | 109 | False ESCO concepts per ad | 3.35 [2.55, 4.24] | 4.02 [3.38, 4.73] | +0.67 [+0.23, +1.09] | 0.0022 |
| `min_k_shown` | 109 | Ads with at least one false concept (%) | 86.2 [77.1, 94.3] | 92.7 [86.3, 98.1] | +6.4 [+2.6, +11.3] | 0.0010 |
| `min_k_shown` | 109 | ESCO precision (%) | 15.7 [10.8, 22.0] | 13.1 [9.2, 17.6] | -2.6 [-5.6, -0.5] | 0.0108 |
| `min_k_shown` | 109 | ESCO recall (%) | 51.1 [40.0, 62.6] | 49.6 [38.7, 60.9] | -1.5 [-6.9, +4.1] | 0.6774 |
| `min_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 18 [14, 20] | 18 [14, 19] | +0 [-2, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 109 | False ESCO concepts per ad | 3.35 [2.55, 4.24] | 0.72 [0.43, 1.03] | -2.63 [-3.59, -1.80] | < 0.0001 |
| `min_k_shown_fewer_ok` | 109 | Ads with at least one false concept (%) | 86.2 [77.1, 94.3] | 33.9 [22.4, 45.6] | -52.3 [-65.1, -40.0] | < 0.0001 |
| `min_k_shown_fewer_ok` | 109 | ESCO precision (%) | 15.7 [10.8, 22.0] | 31.0 [19.2, 44.4] | +15.3 [+5.5, +26.8] | 0.0014 |
| `min_k_shown_fewer_ok` | 109 | ESCO recall (%) | 51.1 [40.0, 62.6] | 26.3 [15.6, 37.9] | -24.8 [-35.4, -15.0] | < 0.0001 |
| `min_k_shown_fewer_ok` | 109 | Top-20 concepts not in the true items' top 20 | 18 [14, 20] | 15 [11, 18] | -3 [-6, +1] | 0.3368 |
| `min_k_enforced` | 109 | False ESCO concepts per ad | 3.35 [2.55, 4.24] | 3.85 [3.40, 4.37] | +0.50 [-0.13, +1.07] | 0.1154 |
| `min_k_enforced` | 109 | Ads with at least one false concept (%) | 86.2 [77.1, 94.3] | 98.2 [95.2, 100.0] | +11.9 [+3.7, +21.1] | 0.0018 |
| `min_k_enforced` | 109 | ESCO precision (%) | 15.7 [10.8, 22.0] | 13.6 [9.7, 18.2] | -2.1 [-6.1, +0.8] | 0.1638 |
| `min_k_enforced` | 109 | ESCO recall (%) | 51.1 [40.0, 62.6] | 49.6 [38.9, 60.8] | -1.5 [-10.8, +6.9] | 0.8336 |
| `min_k_enforced` | 109 | Top-20 concepts not in the true items' top 20 | 18 [14, 20] | 18 [14, 20] | +0 [-2, +3] | 1.0000 |
| `min_k_escape` | 109 | False ESCO concepts per ad | 3.35 [2.55, 4.24] | 0.50 [0.20, 0.85] | -2.85 [-3.81, -1.99] | < 0.0001 |
| `min_k_escape` | 109 | Ads with at least one false concept (%) | 86.2 [77.1, 94.3] | 15.6 [7.8, 24.1] | -70.6 [-81.1, -59.8] | < 0.0001 |
| `min_k_escape` | 109 | ESCO precision (%) | 15.7 [10.8, 22.0] | 19.4 [8.5, 33.9] | +3.7 [-8.0, +18.4] | 0.5690 |
| `min_k_escape` | 109 | ESCO recall (%) | 51.1 [40.0, 62.6] | 9.8 [3.1, 17.7] | -41.4 [-53.1, -30.4] | < 0.0001 |
| `min_k_escape` | 109 | Top-20 concepts not in the true items' top 20 | 18 [14, 20] | 16 [14, 19] | -2 [-5, +4] | 1.0000 |

## 24. Ministral 3 14B (main model alone; not registered), job-ad knowledge, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 102 | False ESCO concepts per ad | 4.82 [3.37, 6.38] | 1.97 [1.53, 2.43] | -2.85 [-4.09, -1.73] | < 0.0001 |
| `prose_up_to_k` | 102 | Ads with at least one false concept (%) | 64.7 [51.5, 76.9] | 70.0 [59.8, 79.4] | +5.3 [-4.0, +14.9] | 0.2764 |
| `prose_up_to_k` | 102 | ESCO precision (%) | 16.6 [11.7, 23.5] | 31.8 [24.1, 40.7] | +15.2 [+10.6, +20.2] | < 0.0001 |
| `prose_up_to_k` | 102 | ESCO recall (%) | 80.3 [70.5, 89.5] | 76.7 [67.2, 85.7] | -3.6 [-12.0, +5.9] | 0.4342 |
| `prose_up_to_k` | 102 | Top-20 concepts not in the true items' top 20 | 17 [13, 19] | 13 [7, 15] | -4 [-9, -1] | 0.0108 |
| `prose_exactly_k` | 102 | False ESCO concepts per ad | 4.82 [3.37, 6.38] | 2.11 [1.69, 2.51] | -2.71 [-3.99, -1.54] | < 0.0001 |
| `prose_exactly_k` | 102 | Ads with at least one false concept (%) | 64.7 [51.5, 76.9] | 72.5 [62.3, 81.7] | +7.8 [-0.4, +16.3] | 0.0650 |
| `prose_exactly_k` | 102 | ESCO precision (%) | 16.6 [11.7, 23.5] | 29.5 [22.9, 37.0] | +12.9 [+8.6, +16.9] | < 0.0001 |
| `prose_exactly_k` | 102 | ESCO recall (%) | 80.3 [70.5, 89.5] | 73.8 [65.4, 82.3] | -6.6 [-14.0, +1.1] | 0.0962 |
| `prose_exactly_k` | 102 | Top-20 concepts not in the true items' top 20 | 17 [13, 19] | 13 [8, 16] | -4 [-8, +0] | 0.0616 |
| `max_k_shown` | 102 | False ESCO concepts per ad | 4.82 [3.37, 6.38] | 1.43 [0.92, 2.01] | -3.39 [-4.77, -2.17] | < 0.0001 |
| `max_k_shown` | 102 | Ads with at least one false concept (%) | 64.7 [51.5, 76.9] | 47.1 [33.7, 60.4] | -17.6 [-29.4, -6.5] | 0.0024 |
| `max_k_shown` | 102 | ESCO precision (%) | 16.6 [11.7, 23.5] | 38.7 [29.1, 50.8] | +22.0 [+15.0, +31.3] | < 0.0001 |
| `max_k_shown` | 102 | ESCO recall (%) | 80.3 [70.5, 89.5] | 75.4 [64.8, 85.6] | -4.9 [-11.5, +0.9] | 0.1448 |
| `max_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 17 [13, 19] | 12 [7, 15] | -5 [-9, -1] | 0.0226 |
| `min_k_shown` | 102 | False ESCO concepts per ad | 4.82 [3.37, 6.38] | 4.55 [3.44, 5.74] | -0.27 [-1.31, +0.54] | 0.5948 |
| `min_k_shown` | 102 | Ads with at least one false concept (%) | 64.7 [51.5, 76.9] | 77.5 [66.7, 87.1] | +12.7 [+3.9, +22.3] | 0.0056 |
| `min_k_shown` | 102 | ESCO precision (%) | 16.6 [11.7, 23.5] | 17.1 [12.4, 23.1] | +0.5 [-2.7, +3.7] | 0.7714 |
| `min_k_shown` | 102 | ESCO recall (%) | 80.3 [70.5, 89.5] | 78.7 [69.3, 87.6] | -1.6 [-10.0, +7.6] | 0.7546 |
| `min_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 17 [13, 19] | 16 [12, 19] | -1 [-4, +1] | 0.8538 |
| `min_k_shown_fewer_ok` | 102 | False ESCO concepts per ad | 4.82 [3.37, 6.38] | 0.49 [0.23, 0.84] | -4.33 [-5.88, -2.92] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | Ads with at least one false concept (%) | 64.7 [51.5, 76.9] | 26.5 [15.5, 38.1] | -38.2 [-51.9, -24.7] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | ESCO precision (%) | 16.6 [11.7, 23.5] | 62.4 [48.2, 78.1] | +45.8 [+32.5, +60.5] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | ESCO recall (%) | 80.3 [70.5, 89.5] | 68.0 [54.5, 81.0] | -12.3 [-22.8, -2.3] | 0.0176 |
| `min_k_shown_fewer_ok` | 102 | Top-20 concepts not in the true items' top 20 | 17 [13, 19] | 10 [5, 12] | -7 [-13, -4] | 0.0004 |
| `min_k_enforced` | 102 | False ESCO concepts per ad | 4.82 [3.37, 6.38] | 4.22 [3.44, 5.18] | -0.61 [-1.78, +0.54] | 0.3112 |
| `min_k_enforced` | 102 | Ads with at least one false concept (%) | 64.7 [51.5, 76.9] | 97.1 [93.3, 100.0] | +32.4 [+20.0, +45.3] | < 0.0001 |
| `min_k_enforced` | 102 | ESCO precision (%) | 16.6 [11.7, 23.5] | 18.4 [13.7, 23.7] | +1.8 [-2.5, +5.2] | 0.3814 |
| `min_k_enforced` | 102 | ESCO recall (%) | 80.3 [70.5, 89.5] | 79.5 [70.2, 88.2] | -0.8 [-8.7, +8.3] | 0.8736 |
| `min_k_enforced` | 102 | Top-20 concepts not in the true items' top 20 | 17 [13, 19] | 16 [12, 19] | -1 [-5, +2] | 0.7756 |
| `min_k_escape` | 102 | False ESCO concepts per ad | 4.82 [3.37, 6.38] | 0.46 [0.10, 1.02] | -4.36 [-5.91, -2.95] | < 0.0001 |
| `min_k_escape` | 102 | Ads with at least one false concept (%) | 64.7 [51.5, 76.9] | 13.7 [6.5, 22.5] | -51.0 [-64.4, -37.5] | < 0.0001 |
| `min_k_escape` | 102 | ESCO precision (%) | 16.6 [11.7, 23.5] | 39.0 [19.2, 73.7] | +22.4 [+4.1, +56.2] | 0.0112 |
| `min_k_escape` | 102 | ESCO recall (%) | 80.3 [70.5, 89.5] | 24.6 [13.7, 36.4] | -55.7 [-69.5, -41.5] | < 0.0001 |
| `min_k_escape` | 102 | Top-20 concepts not in the true items' top 20 | 17 [13, 19] | 15 [10, 18] | -2 [-7, +2] | 0.4582 |

## 25. gpt-oss-20b (main model alone; not registered), both sets, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 2.33 [1.88, 2.80] | 2.33 [2.13, 2.51] | +0.00 [-0.42, +0.40] | 0.9868 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 62.6 [54.1, 71.0] | 82.2 [77.4, 86.6] | +19.6 [+12.3, +27.4] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 24.9 [20.6, 30.0] | 24.9 [21.2, 28.8] | -0.1 [-3.8, +3.2] | 0.9608 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 63.9 [55.5, 72.1] | 63.7 [57.5, 69.8] | -0.2 [-7.0, +7.1] | 0.9326 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 13 [11, 17] | 13 [9, 16] | +0 [-5, +1] | 0.5242 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 2.33 [1.88, 2.80] | 2.58 [2.40, 2.75] | +0.25 [-0.15, +0.64] | 0.2156 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 62.6 [54.1, 71.0] | 85.0 [81.0, 89.0] | +22.5 [+15.3, +30.0] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 24.9 [20.6, 30.0] | 21.8 [18.6, 25.3] | -3.1 [-6.7, +0.0] | 0.0504 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 63.9 [55.5, 72.1] | 59.6 [53.8, 65.6] | -4.3 [-11.2, +3.0] | 0.2424 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 13 [11, 17] | 14 [10, 17] | +1 [-4, +2] | 0.7424 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 2.33 [1.88, 2.80] | 2.04 [1.80, 2.28] | -0.28 [-0.70, +0.14] | 0.1916 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 62.6 [54.1, 71.0] | 78.2 [71.2, 84.7] | +15.6 [+8.3, +23.4] | 0.0004 |
| `max_k_shown` | 211 | ESCO precision (%) | 24.9 [20.6, 30.0] | 26.7 [22.3, 31.6] | +1.8 [-2.2, +5.5] | 0.3718 |
| `max_k_shown` | 211 | ESCO recall (%) | 63.9 [55.5, 72.1] | 61.6 [54.5, 68.9] | -2.4 [-9.1, +4.5] | 0.5466 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 13 [11, 17] | 12 [10, 17] | -1 [-4, +2] | 0.9402 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 2.33 [1.88, 2.80] | 3.37 [3.02, 3.74] | +1.05 [+0.68, +1.40] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 62.6 [54.1, 71.0] | 86.7 [81.2, 91.8] | +24.2 [+16.2, +32.4] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 24.9 [20.6, 30.0] | 19.6 [16.6, 23.0] | -5.3 [-8.8, -2.3] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 63.9 [55.5, 72.1] | 68.2 [61.3, 75.3] | +4.3 [-2.5, +11.7] | 0.2468 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 13 [11, 17] | 13 [11, 17] | +0 [-3, +3] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 2.33 [1.88, 2.80] | 2.60 [2.20, 3.03] | +0.27 [-0.13, +0.69] | 0.1936 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 62.6 [54.1, 71.0] | 72.5 [65.0, 79.8] | +10.0 [+0.5, +19.4] | 0.0438 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 24.9 [20.6, 30.0] | 21.7 [17.9, 25.9] | -3.2 [-7.3, +0.3] | 0.0774 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 63.9 [55.5, 72.1] | 59.6 [52.0, 67.1] | -4.3 [-11.3, +2.6] | 0.2398 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 13 [11, 17] | 13 [11, 18] | +0 [-3, +3] | 1.0000 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 2.33 [1.88, 2.80] | 3.55 [3.21, 3.93] | +1.23 [+0.87, +1.59] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 62.6 [54.1, 71.0] | 94.8 [91.5, 97.7] | +32.2 [+24.3, +40.4] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 24.9 [20.6, 30.0] | 19.0 [15.8, 22.3] | -5.9 [-9.5, -3.0] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO recall (%) | 63.9 [55.5, 72.1] | 69.0 [61.9, 76.2] | +5.1 [-2.4, +13.3] | 0.2106 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 13 [11, 17] | 13 [11, 17] | +0 [-3, +2] | 1.0000 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 2.33 [1.88, 2.80] | 2.38 [1.91, 2.87] | +0.05 [-0.37, +0.49] | 0.8288 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 62.6 [54.1, 71.0] | 61.1 [53.1, 69.3] | -1.4 [-10.0, +7.3] | 0.7930 |
| `min_k_escape` | 211 | ESCO precision (%) | 24.9 [20.6, 30.0] | 22.2 [18.1, 26.9] | -2.8 [-6.8, +1.1] | 0.1570 |
| `min_k_escape` | 211 | ESCO recall (%) | 63.9 [55.5, 72.1] | 56.1 [48.1, 63.9] | -7.8 [-16.0, +0.4] | 0.0720 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 13 [11, 17] | 11 [11, 17] | -2 [-3, +3] | 1.0000 |

Top 20 concepts of the `min_k_shown` outputs: English; Java (computer programming); computer engineering; cooperate with colleagues; learning management systems; cloud technologies; implement front-end website design; JavaScript; perform scientific research; continuous improvement philosophies; German; web programming; SAP R3; react to events in time-critical environments; types of spring; Python (computer programming); web services; interact verbally in Danish; apply knowledge of science, technology and engineering; work in teams

Top 20 concepts of the true items of the same ads: English; teach communication methods; SAP Data Services; German; computer engineering; recruit members; design cloud architecture; Danish; perform scientific research; computer science; react to events in time-critical environments; web services; perform business research; systems development life-cycle; Ruby (computer programming); solve technical problems; communication; Java (computer programming); body language; manage budgets

## 26. gpt-oss-20b (main model alone; not registered), job-ad skills, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 109 | False ESCO concepts per ad | 3.45 [2.74, 4.21] | 2.83 [2.54, 3.12] | -0.62 [-1.32, +0.02] | 0.0580 |
| `prose_up_to_k` | 109 | Ads with at least one false concept (%) | 83.5 [73.1, 92.7] | 92.5 [87.5, 96.5] | +9.0 [-0.2, +18.7] | 0.0578 |
| `prose_up_to_k` | 109 | ESCO precision (%) | 15.5 [11.1, 20.9] | 16.6 [11.8, 21.9] | +1.1 [-2.5, +4.6] | 0.5400 |
| `prose_up_to_k` | 109 | ESCO recall (%) | 51.9 [40.1, 63.8] | 46.3 [36.6, 55.9] | -5.6 [-15.3, +4.2] | 0.2638 |
| `prose_up_to_k` | 109 | Top-20 concepts not in the true items' top 20 | 17 [14, 19] | 17 [13, 19] | +0 [-4, +2] | 0.9184 |
| `prose_exactly_k` | 109 | False ESCO concepts per ad | 3.45 [2.74, 4.21] | 3.00 [2.75, 3.23] | -0.45 [-1.12, +0.15] | 0.1564 |
| `prose_exactly_k` | 109 | Ads with at least one false concept (%) | 83.5 [73.1, 92.7] | 93.8 [89.7, 97.1] | +10.3 [+2.1, +19.1] | 0.0108 |
| `prose_exactly_k` | 109 | ESCO precision (%) | 15.5 [11.1, 20.9] | 14.3 [10.1, 18.8] | -1.2 [-4.7, +1.8] | 0.4348 |
| `prose_exactly_k` | 109 | ESCO recall (%) | 51.9 [40.1, 63.8] | 40.9 [32.2, 49.9] | -11.0 [-20.7, -1.8] | 0.0192 |
| `prose_exactly_k` | 109 | Top-20 concepts not in the true items' top 20 | 17 [14, 19] | 18 [14, 20] | +1 [-3, +3] | 1.0000 |
| `max_k_shown` | 109 | False ESCO concepts per ad | 3.45 [2.74, 4.21] | 2.60 [2.26, 2.92] | -0.85 [-1.53, -0.23] | 0.0066 |
| `max_k_shown` | 109 | Ads with at least one false concept (%) | 83.5 [73.1, 92.7] | 89.9 [82.6, 96.3] | +6.4 [-2.8, +16.0] | 0.2128 |
| `max_k_shown` | 109 | ESCO precision (%) | 15.5 [11.1, 20.9] | 16.5 [11.0, 22.8] | +1.0 [-3.5, +5.5] | 0.6776 |
| `max_k_shown` | 109 | ESCO recall (%) | 51.9 [40.1, 63.8] | 42.1 [30.8, 53.7] | -9.8 [-21.1, +0.6] | 0.0702 |
| `max_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 17 [14, 19] | 19 [13, 19] | +2 [-4, +3] | 1.0000 |
| `min_k_shown` | 109 | False ESCO concepts per ad | 3.45 [2.74, 4.21] | 4.14 [3.62, 4.68] | +0.69 [+0.11, +1.22] | 0.0220 |
| `min_k_shown` | 109 | Ads with at least one false concept (%) | 83.5 [73.1, 92.7] | 94.5 [89.0, 99.0] | +11.0 [+1.8, +20.9] | 0.0228 |
| `min_k_shown` | 109 | ESCO precision (%) | 15.5 [11.1, 20.9] | 13.6 [10.1, 17.7] | -1.9 [-5.4, +1.2] | 0.2442 |
| `min_k_shown` | 109 | ESCO recall (%) | 51.9 [40.1, 63.8] | 53.4 [43.2, 63.8] | +1.5 [-8.5, +12.2] | 0.8330 |
| `min_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 17 [14, 19] | 17 [14, 19] | +0 [-3, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 109 | False ESCO concepts per ad | 3.45 [2.74, 4.21] | 3.31 [2.63, 4.04] | -0.14 [-0.76, +0.50] | 0.6746 |
| `min_k_shown_fewer_ok` | 109 | Ads with at least one false concept (%) | 83.5 [73.1, 92.7] | 80.7 [71.2, 89.3] | -2.8 [-12.7, +6.6] | 0.6446 |
| `min_k_shown_fewer_ok` | 109 | ESCO precision (%) | 15.5 [11.1, 20.9] | 15.3 [10.5, 20.9] | -0.2 [-4.3, +3.4] | 0.9290 |
| `min_k_shown_fewer_ok` | 109 | ESCO recall (%) | 51.9 [40.1, 63.8] | 48.9 [37.7, 59.7] | -3.0 [-13.0, +6.4] | 0.5832 |
| `min_k_shown_fewer_ok` | 109 | Top-20 concepts not in the true items' top 20 | 17 [14, 19] | 17 [14, 20] | +0 [-3, +3] | 1.0000 |
| `min_k_enforced` | 109 | False ESCO concepts per ad | 3.45 [2.74, 4.21] | 4.19 [3.63, 4.80] | +0.74 [+0.20, +1.24] | 0.0096 |
| `min_k_enforced` | 109 | Ads with at least one false concept (%) | 83.5 [73.1, 92.7] | 97.2 [93.9, 100.0] | +13.8 [+4.8, +23.4] | 0.0012 |
| `min_k_enforced` | 109 | ESCO precision (%) | 15.5 [11.1, 20.9] | 13.0 [9.3, 17.1] | -2.6 [-6.1, +0.6] | 0.1142 |
| `min_k_enforced` | 109 | ESCO recall (%) | 51.9 [40.1, 63.8] | 51.1 [40.5, 61.9] | -0.8 [-11.8, +10.9] | 0.9276 |
| `min_k_enforced` | 109 | Top-20 concepts not in the true items' top 20 | 17 [14, 19] | 17 [14, 20] | +0 [-3, +3] | 1.0000 |
| `min_k_escape` | 109 | False ESCO concepts per ad | 3.45 [2.74, 4.21] | 3.33 [2.59, 4.13] | -0.12 [-0.81, +0.60] | 0.7574 |
| `min_k_escape` | 109 | Ads with at least one false concept (%) | 83.5 [73.1, 92.7] | 76.1 [65.4, 86.4] | -7.3 [-18.0, +3.6] | 0.1980 |
| `min_k_escape` | 109 | ESCO precision (%) | 15.5 [11.1, 20.9] | 13.4 [9.1, 18.5] | -2.1 [-6.3, +1.8] | 0.2874 |
| `min_k_escape` | 109 | ESCO recall (%) | 51.9 [40.1, 63.8] | 42.1 [31.0, 53.1] | -9.8 [-20.2, +0.7] | 0.0728 |
| `min_k_escape` | 109 | Top-20 concepts not in the true items' top 20 | 17 [14, 19] | 19 [15, 20] | +2 [-2, +3] | 1.0000 |

## 27. gpt-oss-20b (main model alone; not registered), job-ad knowledge, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 102 | False ESCO concepts per ad | 1.13 [0.63, 1.71] | 1.79 [1.54, 2.04] | +0.66 [+0.18, +1.08] | 0.0070 |
| `prose_up_to_k` | 102 | Ads with at least one false concept (%) | 40.2 [27.1, 53.5] | 71.2 [63.5, 78.6] | +31.0 [+20.2, +41.9] | < 0.0001 |
| `prose_up_to_k` | 102 | ESCO precision (%) | 45.0 [33.7, 58.9] | 35.6 [29.7, 41.6] | -9.4 [-21.4, -1.0] | 0.0246 |
| `prose_up_to_k` | 102 | ESCO recall (%) | 77.0 [65.5, 87.3] | 82.6 [76.5, 88.1] | +5.6 [-4.2, +16.6] | 0.2874 |
| `prose_up_to_k` | 102 | Top-20 concepts not in the true items' top 20 | 12 [7, 16] | 10 [6, 14] | -2 [-7, +3] | 0.5592 |
| `prose_exactly_k` | 102 | False ESCO concepts per ad | 1.13 [0.63, 1.71] | 2.13 [1.88, 2.39] | +1.00 [+0.53, +1.45] | 0.0004 |
| `prose_exactly_k` | 102 | Ads with at least one false concept (%) | 40.2 [27.1, 53.5] | 75.7 [68.5, 82.4] | +35.5 [+23.8, +47.4] | < 0.0001 |
| `prose_exactly_k` | 102 | ESCO precision (%) | 45.0 [33.7, 58.9] | 31.0 [25.5, 36.6] | -14.0 [-26.3, -5.1] | 0.0010 |
| `prose_exactly_k` | 102 | ESCO recall (%) | 77.0 [65.5, 87.3] | 80.0 [73.2, 86.4] | +3.0 [-7.1, +14.4] | 0.5858 |
| `prose_exactly_k` | 102 | Top-20 concepts not in the true items' top 20 | 12 [7, 16] | 13 [7, 15] | +1 [-6, +4] | 0.7888 |
| `max_k_shown` | 102 | False ESCO concepts per ad | 1.13 [0.63, 1.71] | 1.45 [1.12, 1.79] | +0.32 [-0.22, +0.82] | 0.2284 |
| `max_k_shown` | 102 | Ads with at least one false concept (%) | 40.2 [27.1, 53.5] | 65.7 [54.1, 76.7] | +25.5 [+13.9, +37.4] | < 0.0001 |
| `max_k_shown` | 102 | ESCO precision (%) | 45.0 [33.7, 58.9] | 40.6 [32.4, 49.2] | -4.4 [-16.3, +4.4] | 0.3590 |
| `max_k_shown` | 102 | ESCO recall (%) | 77.0 [65.5, 87.3] | 82.8 [74.5, 90.4] | +5.7 [-2.5, +14.9] | 0.2078 |
| `max_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 12 [7, 16] | 11 [8, 15] | -1 [-5, +4] | 0.9588 |
| `min_k_shown` | 102 | False ESCO concepts per ad | 1.13 [0.63, 1.71] | 2.56 [2.10, 3.07] | +1.43 [+0.98, +1.88] | < 0.0001 |
| `min_k_shown` | 102 | Ads with at least one false concept (%) | 40.2 [27.1, 53.5] | 78.4 [68.6, 87.4] | +38.2 [+25.7, +51.0] | < 0.0001 |
| `min_k_shown` | 102 | ESCO precision (%) | 45.0 [33.7, 58.9] | 28.3 [22.7, 34.3] | -16.7 [-28.2, -8.5] | < 0.0001 |
| `min_k_shown` | 102 | ESCO recall (%) | 77.0 [65.5, 87.3] | 84.4 [76.2, 92.1] | +7.4 [-1.8, +18.0] | 0.1402 |
| `min_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 12 [7, 16] | 12 [10, 17] | +0 [-2, +6] | 0.7920 |
| `min_k_shown_fewer_ok` | 102 | False ESCO concepts per ad | 1.13 [0.63, 1.71] | 1.84 [1.45, 2.25] | +0.72 [+0.19, +1.23] | 0.0088 |
| `min_k_shown_fewer_ok` | 102 | Ads with at least one false concept (%) | 40.2 [27.1, 53.5] | 63.7 [52.5, 74.5] | +23.5 [+7.8, +38.8] | 0.0048 |
| `min_k_shown_fewer_ok` | 102 | ESCO precision (%) | 45.0 [33.7, 58.9] | 31.6 [25.2, 38.5] | -13.3 [-26.2, -4.1] | 0.0024 |
| `min_k_shown_fewer_ok` | 102 | ESCO recall (%) | 77.0 [65.5, 87.3] | 71.3 [61.2, 80.5] | -5.7 [-16.4, +4.9] | 0.3236 |
| `min_k_shown_fewer_ok` | 102 | Top-20 concepts not in the true items' top 20 | 12 [7, 16] | 13 [10, 17] | +1 [-3, +6] | 0.8282 |
| `min_k_enforced` | 102 | False ESCO concepts per ad | 1.13 [0.63, 1.71] | 2.87 [2.49, 3.29] | +1.75 [+1.28, +2.20] | < 0.0001 |
| `min_k_enforced` | 102 | Ads with at least one false concept (%) | 40.2 [27.1, 53.5] | 92.2 [86.1, 97.1] | +52.0 [+39.8, +64.4] | < 0.0001 |
| `min_k_enforced` | 102 | ESCO precision (%) | 45.0 [33.7, 58.9] | 26.9 [21.5, 32.6] | -18.0 [-30.2, -9.5] | < 0.0001 |
| `min_k_enforced` | 102 | ESCO recall (%) | 77.0 [65.5, 87.3] | 88.5 [80.8, 95.3] | +11.5 [+1.7, +23.1] | 0.0234 |
| `min_k_enforced` | 102 | Top-20 concepts not in the true items' top 20 | 12 [7, 16] | 14 [10, 17] | +2 [-2, +7] | 0.6584 |
| `min_k_escape` | 102 | False ESCO concepts per ad | 1.13 [0.63, 1.71] | 1.36 [0.89, 1.89] | +0.24 [-0.18, +0.66] | 0.2826 |
| `min_k_escape` | 102 | Ads with at least one false concept (%) | 40.2 [27.1, 53.5] | 45.1 [33.3, 56.9] | +4.9 [-8.6, +18.4] | 0.5198 |
| `min_k_escape` | 102 | ESCO precision (%) | 45.0 [33.7, 58.9] | 38.5 [30.2, 48.6] | -6.5 [-16.1, +0.6] | 0.0822 |
| `min_k_escape` | 102 | ESCO recall (%) | 77.0 [65.5, 87.3] | 71.3 [61.2, 80.8] | -5.7 [-18.9, +8.0] | 0.4446 |
| `min_k_escape` | 102 | Top-20 concepts not in the true items' top 20 | 12 [7, 16] | 12 [8, 16] | +0 [-4, +4] | 1.0000 |

## 28. GPT-6 Luna (Azure), both sets, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 1.20 [0.89, 1.54] | 0.93 [0.72, 1.14] | -0.27 [-0.50, -0.06] | 0.0130 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 48.3 [39.4, 57.3] | 47.4 [39.0, 55.9] | -0.9 [-7.7, +6.2] | 0.8328 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 38.0 [30.5, 47.0] | 47.2 [40.2, 54.9] | +9.1 [+3.5, +14.2] | 0.0022 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 61.2 [53.1, 69.1] | 68.6 [61.6, 75.7] | +7.5 [+1.7, +13.1] | 0.0128 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 11 [9, 16] | 12 [7, 14] | +1 [-6, +1] | 0.2312 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 1.20 [0.89, 1.54] | 1.76 [1.52, 2.00] | +0.56 [+0.27, +0.85] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 48.3 [39.4, 57.3] | 73.5 [66.2, 80.7] | +25.1 [+17.6, +33.0] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 38.0 [30.5, 47.0] | 33.8 [28.9, 39.0] | -4.2 [-11.4, +1.4] | 0.1482 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 61.2 [53.1, 69.1] | 74.5 [67.5, 81.2] | +13.3 [+8.0, +19.0] | < 0.0001 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 11 [9, 16] | 12 [8, 15] | +1 [-4, +3] | 0.8070 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 1.20 [0.89, 1.54] | 0.81 [0.61, 1.00] | -0.40 [-0.66, -0.17] | 0.0010 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 48.3 [39.4, 57.3] | 40.3 [31.9, 48.8] | -8.1 [-14.7, -1.8] | 0.0162 |
| `max_k_shown` | 211 | ESCO precision (%) | 38.0 [30.5, 47.0] | 46.7 [39.0, 55.2] | +8.7 [+2.5, +14.5] | 0.0052 |
| `max_k_shown` | 211 | ESCO recall (%) | 61.2 [53.1, 69.1] | 58.4 [49.4, 67.2] | -2.7 [-9.1, +2.8] | 0.3916 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 11 [9, 16] | 10 [7, 14] | -1 [-6, +1] | 0.3948 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 1.20 [0.89, 1.54] | 2.07 [1.74, 2.43] | +0.87 [+0.56, +1.21] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 48.3 [39.4, 57.3] | 72.5 [64.7, 80.0] | +24.2 [+16.5, +32.3] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 38.0 [30.5, 47.0] | 29.5 [24.3, 35.2] | -8.5 [-15.3, -3.2] | 0.0008 |
| `min_k_shown` | 211 | ESCO recall (%) | 61.2 [53.1, 69.1] | 71.8 [64.7, 78.7] | +10.6 [+5.9, +15.6] | < 0.0001 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 11 [9, 16] | 12 [9, 16] | +1 [-3, +4] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 1.20 [0.89, 1.54] | 1.83 [1.51, 2.18] | +0.63 [+0.33, +0.96] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 48.3 [39.4, 57.3] | 66.4 [58.5, 74.0] | +18.0 [+10.8, +25.5] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 38.0 [30.5, 47.0] | 31.1 [25.4, 37.3] | -7.0 [-13.5, -1.9] | 0.0052 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 61.2 [53.1, 69.1] | 68.2 [61.0, 75.2] | +7.1 [+2.2, +12.0] | 0.0044 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 11 [9, 16] | 12 [9, 16] | +1 [-3, +4] | 1.0000 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 1.20 [0.89, 1.54] | 3.53 [3.24, 3.83] | +2.32 [+1.99, +2.69] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 48.3 [39.4, 57.3] | 98.6 [96.8, 100.0] | +50.2 [+41.5, +59.0] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 38.0 [30.5, 47.0] | 20.0 [16.7, 23.5] | -18.0 [-25.3, -12.3] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO recall (%) | 61.2 [53.1, 69.1] | 72.9 [65.8, 79.9] | +11.8 [+6.4, +17.5] | < 0.0001 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 11 [9, 16] | 13 [12, 18] | +2 [-2, +6] | 0.4008 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 1.20 [0.89, 1.54] | 2.33 [2.02, 2.66] | +1.12 [+0.83, +1.44] | < 0.0001 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 48.3 [39.4, 57.3] | 79.1 [72.1, 85.9] | +30.8 [+21.7, +40.2] | < 0.0001 |
| `min_k_escape` | 211 | ESCO precision (%) | 38.0 [30.5, 47.0] | 26.6 [21.9, 31.7] | -11.4 [-18.1, -6.3] | < 0.0001 |
| `min_k_escape` | 211 | ESCO recall (%) | 61.2 [53.1, 69.1] | 69.8 [62.4, 77.3] | +8.6 [+2.7, +14.6] | 0.0052 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 11 [9, 16] | 14 [10, 17] | +3 [-2, +5] | 0.7352 |

Top 20 concepts of the `min_k_shown` outputs: English; perform scientific research; computer engineering; Agile development; German; computer technology; apply knowledge of science, technology and engineering; SAP Data Services; cooperate with colleagues; design cloud architecture; Danish; develop automated software tests; learning management systems; teach mathematics; computer science; mammalogy; cloud technologies; think creatively; quality assurance methodologies; continuous improvement philosophies

Top 20 concepts of the true items of the same ads: English; teach communication methods; SAP Data Services; German; computer engineering; recruit members; design cloud architecture; Danish; perform scientific research; computer science; react to events in time-critical environments; web services; perform business research; systems development life-cycle; Ruby (computer programming); solve technical problems; communication; Java (computer programming); body language; manage budgets

## 29. GPT-6 Luna (Azure), job-ad skills, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 109 | False ESCO concepts per ad | 1.50 [1.01, 2.01] | 0.97 [0.68, 1.29] | -0.52 [-0.85, -0.25] | < 0.0001 |
| `prose_up_to_k` | 109 | Ads with at least one false concept (%) | 50.5 [38.0, 63.0] | 47.7 [36.0, 59.6] | -2.8 [-9.5, +4.6] | 0.5184 |
| `prose_up_to_k` | 109 | ESCO precision (%) | 25.2 [17.0, 35.9] | 40.4 [30.4, 51.7] | +15.2 [+8.2, +22.6] | < 0.0001 |
| `prose_up_to_k` | 109 | ESCO recall (%) | 41.4 [30.6, 52.8] | 54.1 [43.3, 65.2] | +12.8 [+4.0, +22.0] | 0.0054 |
| `prose_up_to_k` | 109 | Top-20 concepts not in the true items' top 20 | 19 [11, 19] | 13 [8, 16] | -6 [-7, +0] | 0.0638 |
| `prose_exactly_k` | 109 | False ESCO concepts per ad | 1.50 [1.01, 2.01] | 2.04 [1.66, 2.40] | +0.54 [+0.12, +0.96] | 0.0124 |
| `prose_exactly_k` | 109 | Ads with at least one false concept (%) | 50.5 [38.0, 63.0] | 78.0 [67.6, 87.3] | +27.5 [+17.3, +38.5] | < 0.0001 |
| `prose_exactly_k` | 109 | ESCO precision (%) | 25.2 [17.0, 35.9] | 26.2 [19.8, 33.6] | +1.0 [-6.8, +7.2] | 0.7902 |
| `prose_exactly_k` | 109 | ESCO recall (%) | 41.4 [30.6, 52.8] | 59.4 [49.2, 69.7] | +18.0 [+10.1, +26.6] | < 0.0001 |
| `prose_exactly_k` | 109 | Top-20 concepts not in the true items' top 20 | 19 [11, 19] | 17 [10, 18] | -2 [-5, +2] | 0.4866 |
| `max_k_shown` | 109 | False ESCO concepts per ad | 1.50 [1.01, 2.01] | 1.01 [0.73, 1.31] | -0.49 [-0.86, -0.17] | 0.0010 |
| `max_k_shown` | 109 | Ads with at least one false concept (%) | 50.5 [38.0, 63.0] | 48.6 [36.4, 61.0] | -1.8 [-8.0, +4.6] | 0.6588 |
| `max_k_shown` | 109 | ESCO precision (%) | 25.2 [17.0, 35.9] | 36.0 [26.0, 47.2] | +10.8 [+3.6, +18.2] | 0.0036 |
| `max_k_shown` | 109 | ESCO recall (%) | 41.4 [30.6, 52.8] | 46.6 [35.1, 58.5] | +5.3 [-1.6, +12.6] | 0.1722 |
| `max_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 19 [11, 19] | 16 [9, 17] | -3 [-6, +1] | 0.2190 |
| `min_k_shown` | 109 | False ESCO concepts per ad | 1.50 [1.01, 2.01] | 2.22 [1.79, 2.65] | +0.72 [+0.35, +1.13] | < 0.0001 |
| `min_k_shown` | 109 | Ads with at least one false concept (%) | 50.5 [38.0, 63.0] | 75.2 [64.5, 85.1] | +24.8 [+15.2, +35.2] | < 0.0001 |
| `min_k_shown` | 109 | ESCO precision (%) | 25.2 [17.0, 35.9] | 23.4 [17.3, 30.6] | -1.8 [-8.7, +3.4] | 0.5194 |
| `min_k_shown` | 109 | ESCO recall (%) | 41.4 [30.6, 52.8] | 55.6 [45.1, 66.4] | +14.3 [+7.0, +22.7] | < 0.0001 |
| `min_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 19 [11, 19] | 18 [11, 18] | -1 [-4, +3] | 0.7094 |
| `min_k_shown_fewer_ok` | 109 | False ESCO concepts per ad | 1.50 [1.01, 2.01] | 2.02 [1.59, 2.45] | +0.52 [+0.18, +0.88] | 0.0042 |
| `min_k_shown_fewer_ok` | 109 | Ads with at least one false concept (%) | 50.5 [38.0, 63.0] | 71.6 [60.7, 81.7] | +21.1 [+11.9, +31.0] | < 0.0001 |
| `min_k_shown_fewer_ok` | 109 | ESCO precision (%) | 25.2 [17.0, 35.9] | 23.6 [17.0, 31.3] | -1.6 [-8.0, +3.2] | 0.5296 |
| `min_k_shown_fewer_ok` | 109 | ESCO recall (%) | 41.4 [30.6, 52.8] | 51.1 [40.3, 62.2] | +9.8 [+3.1, +17.4] | 0.0048 |
| `min_k_shown_fewer_ok` | 109 | Top-20 concepts not in the true items' top 20 | 19 [11, 19] | 18 [11, 18] | -1 [-4, +2] | 0.7610 |
| `min_k_enforced` | 109 | False ESCO concepts per ad | 1.50 [1.01, 2.01] | 3.61 [3.21, 4.04] | +2.12 [+1.68, +2.59] | < 0.0001 |
| `min_k_enforced` | 109 | Ads with at least one false concept (%) | 50.5 [38.0, 63.0] | 97.2 [93.8, 100.0] | +46.8 [+34.9, +59.1] | < 0.0001 |
| `min_k_enforced` | 109 | ESCO precision (%) | 25.2 [17.0, 35.9] | 15.6 [11.5, 20.2] | -9.6 [-17.7, -4.0] | 0.0002 |
| `min_k_enforced` | 109 | ESCO recall (%) | 41.4 [30.6, 52.8] | 54.9 [43.8, 66.2] | +13.5 [+5.4, +22.0] | 0.0012 |
| `min_k_enforced` | 109 | Top-20 concepts not in the true items' top 20 | 19 [11, 19] | 19 [14, 20] | +0 [-1, +5] | 0.6140 |
| `min_k_escape` | 109 | False ESCO concepts per ad | 1.50 [1.01, 2.01] | 2.84 [2.45, 3.25] | +1.35 [+0.95, +1.75] | < 0.0001 |
| `min_k_escape` | 109 | Ads with at least one false concept (%) | 50.5 [38.0, 63.0] | 89.9 [82.6, 96.3] | +39.4 [+28.3, +51.3] | < 0.0001 |
| `min_k_escape` | 109 | ESCO precision (%) | 25.2 [17.0, 35.9] | 17.8 [12.8, 23.2] | -7.5 [-14.9, -1.9] | 0.0070 |
| `min_k_escape` | 109 | ESCO recall (%) | 41.4 [30.6, 52.8] | 50.4 [39.1, 62.3] | +9.0 [+0.7, +18.0] | 0.0484 |
| `min_k_escape` | 109 | Top-20 concepts not in the true items' top 20 | 19 [11, 19] | 18 [13, 19] | -1 [-2, +4] | 1.0000 |

## 30. GPT-6 Luna (Azure), job-ad knowledge, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 102 | False ESCO concepts per ad | 0.89 [0.53, 1.33] | 0.88 [0.60, 1.19] | -0.01 [-0.32, +0.29] | 0.9632 |
| `prose_up_to_k` | 102 | Ads with at least one false concept (%) | 46.1 [33.0, 59.4] | 47.1 [34.3, 60.2] | +1.0 [-11.8, +13.7] | 0.9300 |
| `prose_up_to_k` | 102 | ESCO precision (%) | 52.6 [40.4, 66.2] | 53.4 [43.1, 64.5] | +0.8 [-9.1, +8.9] | 0.8682 |
| `prose_up_to_k` | 102 | ESCO recall (%) | 82.8 [74.1, 90.9] | 84.4 [76.6, 91.8] | +1.6 [-4.9, +8.8] | 0.7362 |
| `prose_up_to_k` | 102 | Top-20 concepts not in the true items' top 20 | 9 [5, 15] | 9 [6, 13] | +0 [-4, +4] | 0.9666 |
| `prose_exactly_k` | 102 | False ESCO concepts per ad | 0.89 [0.53, 1.33] | 1.47 [1.18, 1.78] | +0.58 [+0.17, +0.95] | 0.0072 |
| `prose_exactly_k` | 102 | Ads with at least one false concept (%) | 46.1 [33.0, 59.4] | 68.6 [57.5, 79.2] | +22.5 [+10.5, +35.0] | 0.0006 |
| `prose_exactly_k` | 102 | ESCO precision (%) | 52.6 [40.4, 66.2] | 42.5 [35.2, 49.8] | -10.1 [-21.5, -0.3] | 0.0444 |
| `prose_exactly_k` | 102 | ESCO recall (%) | 82.8 [74.1, 90.9] | 91.0 [84.8, 96.4] | +8.2 [+1.7, +15.9] | 0.0138 |
| `prose_exactly_k` | 102 | Top-20 concepts not in the true items' top 20 | 9 [5, 15] | 9 [7, 14] | +0 [-4, +5] | 1.0000 |
| `max_k_shown` | 102 | False ESCO concepts per ad | 0.89 [0.53, 1.33] | 0.59 [0.34, 0.87] | -0.30 [-0.66, -0.01] | 0.0482 |
| `max_k_shown` | 102 | Ads with at least one false concept (%) | 46.1 [33.0, 59.4] | 31.4 [20.0, 43.3] | -14.7 [-26.3, -3.0] | 0.0164 |
| `max_k_shown` | 102 | ESCO precision (%) | 52.6 [40.4, 66.2] | 59.2 [47.7, 71.9] | +6.6 [-3.7, +17.2] | 0.2226 |
| `max_k_shown` | 102 | ESCO recall (%) | 82.8 [74.1, 90.9] | 71.3 [59.1, 82.3] | -11.5 [-20.9, -3.3] | 0.0064 |
| `max_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 9 [5, 15] | 8 [5, 12] | -1 [-6, +3] | 0.7058 |
| `min_k_shown` | 102 | False ESCO concepts per ad | 0.89 [0.53, 1.33] | 1.91 [1.38, 2.49] | +1.02 [+0.54, +1.58] | < 0.0001 |
| `min_k_shown` | 102 | Ads with at least one false concept (%) | 46.1 [33.0, 59.4] | 69.6 [58.3, 80.8] | +23.5 [+12.4, +35.7] | 0.0004 |
| `min_k_shown` | 102 | ESCO precision (%) | 52.6 [40.4, 66.2] | 35.9 [27.4, 45.9] | -16.7 [-28.2, -7.4] | < 0.0001 |
| `min_k_shown` | 102 | ESCO recall (%) | 82.8 [74.1, 90.9] | 89.3 [82.3, 95.9] | +6.6 [+1.5, +13.4] | 0.0320 |
| `min_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 9 [5, 15] | 11 [8, 16] | +2 [-1, +7] | 0.4078 |
| `min_k_shown_fewer_ok` | 102 | False ESCO concepts per ad | 0.89 [0.53, 1.33] | 1.63 [1.13, 2.20] | +0.74 [+0.25, +1.32] | 0.0016 |
| `min_k_shown_fewer_ok` | 102 | Ads with at least one false concept (%) | 46.1 [33.0, 59.4] | 60.8 [49.5, 72.0] | +14.7 [+4.0, +26.0] | 0.0082 |
| `min_k_shown_fewer_ok` | 102 | ESCO precision (%) | 52.6 [40.4, 66.2] | 39.0 [29.4, 50.4] | -13.6 [-25.7, -3.5] | 0.0048 |
| `min_k_shown_fewer_ok` | 102 | ESCO recall (%) | 82.8 [74.1, 90.9] | 86.9 [80.0, 93.5] | +4.1 [-2.6, +11.5] | 0.2834 |
| `min_k_shown_fewer_ok` | 102 | Top-20 concepts not in the true items' top 20 | 9 [5, 15] | 9 [7, 16] | +0 [-2, +6] | 0.6662 |
| `min_k_enforced` | 102 | False ESCO concepts per ad | 0.89 [0.53, 1.33] | 3.43 [3.03, 3.90] | +2.54 [+2.03, +3.11] | < 0.0001 |
| `min_k_enforced` | 102 | Ads with at least one false concept (%) | 46.1 [33.0, 59.4] | 100.0 [100.0, 100.0] | +53.9 [+40.6, +67.0] | < 0.0001 |
| `min_k_enforced` | 102 | ESCO precision (%) | 52.6 [40.4, 66.2] | 24.4 [19.2, 29.9] | -28.2 [-40.5, -18.0] | < 0.0001 |
| `min_k_enforced` | 102 | ESCO recall (%) | 82.8 [74.1, 90.9] | 92.6 [86.5, 97.7] | +9.8 [+3.2, +17.8] | 0.0032 |
| `min_k_enforced` | 102 | Top-20 concepts not in the true items' top 20 | 9 [5, 15] | 14 [11, 17] | +5 [-1, +9] | 0.1534 |
| `min_k_escape` | 102 | False ESCO concepts per ad | 0.89 [0.53, 1.33] | 1.77 [1.31, 2.28] | +0.88 [+0.43, +1.40] | < 0.0001 |
| `min_k_escape` | 102 | Ads with at least one false concept (%) | 46.1 [33.0, 59.4] | 67.6 [56.1, 78.8] | +21.6 [+5.9, +37.3] | 0.0084 |
| `min_k_escape` | 102 | ESCO precision (%) | 52.6 [40.4, 66.2] | 38.0 [29.1, 48.2] | -14.6 [-26.4, -5.0] | 0.0020 |
| `min_k_escape` | 102 | ESCO recall (%) | 82.8 [74.1, 90.9] | 91.0 [84.1, 96.7] | +8.2 [+0.0, +17.1] | 0.0578 |
| `min_k_escape` | 102 | Top-20 concepts not in the true items' top 20 | 9 [5, 15] | 12 [8, 16] | +3 [-2, +8] | 0.4604 |

## 31. GPT-6 Sol (Azure), both sets, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 1.17 [0.90, 1.47] | 0.91 [0.72, 1.11] | -0.26 [-0.47, -0.06] | 0.0098 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 54.5 [45.9, 63.3] | 50.7 [42.3, 59.3] | -3.8 [-9.5, +1.9] | 0.2198 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 41.9 [34.8, 49.5] | 48.2 [41.0, 55.7] | +6.4 [+1.7, +10.7] | 0.0082 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 69.8 [61.5, 77.8] | 70.2 [62.5, 77.8] | +0.4 [-2.0, +2.7] | 0.8800 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 12 [8, 16] | 9 [7, 14] | -3 [-5, +1] | 0.4400 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 1.17 [0.90, 1.47] | 2.60 [2.40, 2.79] | +1.43 [+1.11, +1.73] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 54.5 [45.9, 63.3] | 96.2 [93.2, 98.6] | +41.7 [+33.3, +50.2] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 41.9 [34.8, 49.5] | 26.3 [22.3, 30.4] | -15.5 [-22.1, -9.8] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 69.8 [61.5, 77.8] | 76.9 [70.7, 83.0] | +7.1 [+1.9, +12.5] | 0.0094 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 12 [8, 16] | 15 [11, 18] | +3 [-2, +7] | 0.3972 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 1.17 [0.90, 1.47] | 0.79 [0.63, 0.97] | -0.38 [-0.58, -0.20] | < 0.0001 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 54.5 [45.9, 63.3] | 46.9 [38.8, 55.3] | -7.6 [-13.1, -2.7] | 0.0024 |
| `max_k_shown` | 211 | ESCO precision (%) | 41.9 [34.8, 49.5] | 51.6 [44.5, 58.8] | +9.7 [+5.5, +13.7] | < 0.0001 |
| `max_k_shown` | 211 | ESCO recall (%) | 69.8 [61.5, 77.8] | 69.8 [62.1, 77.5] | +0.0 [-1.9, +1.8] | 1.0000 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 12 [8, 16] | 7 [5, 12] | -5 [-7, +0] | 0.0810 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 1.17 [0.90, 1.47] | 2.12 [1.80, 2.47] | +0.95 [+0.66, +1.27] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 54.5 [45.9, 63.3] | 79.6 [73.2, 85.9] | +25.1 [+17.6, +32.9] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 41.9 [34.8, 49.5] | 30.0 [25.0, 35.5] | -11.8 [-17.6, -7.1] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 69.8 [61.5, 77.8] | 75.3 [68.4, 82.1] | +5.5 [+1.3, +9.7] | 0.0124 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 12 [8, 16] | 14 [10, 17] | +2 [-2, +6] | 0.5350 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 1.17 [0.90, 1.47] | 1.34 [1.07, 1.64] | +0.17 [-0.04, +0.39] | 0.1116 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 54.5 [45.9, 63.3] | 57.8 [49.8, 65.9] | +3.3 [-1.4, +8.4] | 0.2086 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 41.9 [34.8, 49.5] | 40.3 [33.9, 47.0] | -1.6 [-6.3, +2.7] | 0.4680 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 69.8 [61.5, 77.8] | 74.9 [67.9, 81.8] | +5.1 [+1.1, +9.6] | 0.0138 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 12 [8, 16] | 12 [8, 16] | +0 [-3, +2] | 1.0000 |

Top 20 concepts of the `min_k_shown` outputs: English; cooperate with colleagues; perform scientific research; think creatively; computer engineering; process applications; provide improvement strategies; computer technology; continuous improvement philosophies; teach mathematics; design cloud architecture; Danish; German; apply knowledge of science, technology and engineering; detect bottlenecks; engage with stakeholders; coordinate operational activities; quality assurance methodologies; design thinking; offer financial services

Top 20 concepts of the true items of the same ads: English; teach communication methods; SAP Data Services; German; computer engineering; recruit members; design cloud architecture; Danish; perform scientific research; computer science; react to events in time-critical environments; web services; perform business research; systems development life-cycle; Ruby (computer programming); solve technical problems; communication; Java (computer programming); body language; manage budgets

## 32. GPT-6 Sol (Azure), job-ad skills, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 109 | False ESCO concepts per ad | 1.37 [1.01, 1.76] | 1.07 [0.82, 1.35] | -0.29 [-0.60, -0.01] | 0.0456 |
| `prose_up_to_k` | 109 | Ads with at least one false concept (%) | 66.1 [53.7, 78.2] | 60.6 [49.1, 72.2] | -5.5 [-14.2, +3.5] | 0.2626 |
| `prose_up_to_k` | 109 | ESCO precision (%) | 30.0 [21.8, 39.6] | 36.1 [26.8, 46.2] | +6.0 [+0.3, +11.7] | 0.0386 |
| `prose_up_to_k` | 109 | ESCO recall (%) | 48.1 [36.4, 60.5] | 49.6 [38.3, 61.7] | +1.5 [-2.6, +5.6] | 0.6038 |
| `prose_up_to_k` | 109 | Top-20 concepts not in the true items' top 20 | 17 [11, 18] | 17 [9, 17] | +0 [-4, +1] | 0.6570 |
| `prose_exactly_k` | 109 | False ESCO concepts per ad | 1.37 [1.01, 1.76] | 2.74 [2.47, 3.01] | +1.38 [+0.95, +1.77] | < 0.0001 |
| `prose_exactly_k` | 109 | Ads with at least one false concept (%) | 66.1 [53.7, 78.2] | 98.2 [95.3, 100.0] | +32.1 [+20.6, +44.0] | < 0.0001 |
| `prose_exactly_k` | 109 | ESCO precision (%) | 30.0 [21.8, 39.6] | 21.7 [16.4, 27.5] | -8.3 [-15.9, -2.1] | 0.0096 |
| `prose_exactly_k` | 109 | ESCO recall (%) | 48.1 [36.4, 60.5] | 62.4 [53.0, 71.9] | +14.3 [+5.4, +23.2] | 0.0010 |
| `prose_exactly_k` | 109 | Top-20 concepts not in the true items' top 20 | 17 [11, 18] | 18 [12, 19] | +1 [-2, +5] | 0.6042 |
| `max_k_shown` | 109 | False ESCO concepts per ad | 1.37 [1.01, 1.76] | 0.92 [0.70, 1.15] | -0.45 [-0.74, -0.21] | < 0.0001 |
| `max_k_shown` | 109 | Ads with at least one false concept (%) | 66.1 [53.7, 78.2] | 57.8 [46.2, 69.6] | -8.3 [-16.7, -0.9] | 0.0432 |
| `max_k_shown` | 109 | ESCO precision (%) | 30.0 [21.8, 39.6] | 39.0 [29.4, 49.4] | +9.0 [+4.0, +14.3] | 0.0002 |
| `max_k_shown` | 109 | ESCO recall (%) | 48.1 [36.4, 60.5] | 48.1 [36.9, 59.8] | +0.0 [-3.7, +3.6] | 1.0000 |
| `max_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 17 [11, 18] | 15 [8, 16] | -2 [-6, +0] | 0.2660 |
| `min_k_shown` | 109 | False ESCO concepts per ad | 1.37 [1.01, 1.76] | 2.20 [1.83, 2.63] | +0.83 [+0.43, +1.27] | 0.0002 |
| `min_k_shown` | 109 | Ads with at least one false concept (%) | 66.1 [53.7, 78.2] | 91.7 [85.0, 97.3] | +25.7 [+14.8, +37.1] | < 0.0001 |
| `min_k_shown` | 109 | ESCO precision (%) | 30.0 [21.8, 39.6] | 25.2 [18.9, 32.5] | -4.8 [-11.7, +1.1] | 0.1190 |
| `min_k_shown` | 109 | ESCO recall (%) | 48.1 [36.4, 60.5] | 60.9 [50.8, 71.2] | +12.8 [+6.4, +19.6] | < 0.0001 |
| `min_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 17 [11, 18] | 17 [11, 18] | +0 [-2, +4] | 1.0000 |
| `min_k_shown_fewer_ok` | 109 | False ESCO concepts per ad | 1.37 [1.01, 1.76] | 1.29 [0.97, 1.65] | -0.07 [-0.37, +0.21] | 0.6380 |
| `min_k_shown_fewer_ok` | 109 | Ads with at least one false concept (%) | 66.1 [53.7, 78.2] | 64.2 [53.0, 75.5] | -1.8 [-7.8, +4.6] | 0.6370 |
| `min_k_shown_fewer_ok` | 109 | ESCO precision (%) | 30.0 [21.8, 39.6] | 35.6 [27.4, 45.1] | +5.6 [-0.3, +11.7] | 0.0624 |
| `min_k_shown_fewer_ok` | 109 | ESCO recall (%) | 48.1 [36.4, 60.5] | 58.6 [48.2, 69.4] | +10.5 [+3.0, +19.0] | 0.0048 |
| `min_k_shown_fewer_ok` | 109 | Top-20 concepts not in the true items' top 20 | 17 [11, 18] | 15 [9, 16] | -2 [-5, +1] | 0.4112 |

## 33. GPT-6 Sol (Azure), job-ad knowledge, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 102 | False ESCO concepts per ad | 0.96 [0.58, 1.44] | 0.74 [0.46, 1.05] | -0.23 [-0.51, +0.04] | 0.0992 |
| `prose_up_to_k` | 102 | Ads with at least one false concept (%) | 42.2 [29.3, 55.4] | 40.2 [27.9, 53.4] | -2.0 [-9.2, +5.0] | 0.7152 |
| `prose_up_to_k` | 102 | ESCO precision (%) | 53.8 [41.9, 66.5] | 60.1 [48.9, 71.4] | +6.3 [-1.4, +12.6] | 0.1066 |
| `prose_up_to_k` | 102 | ESCO recall (%) | 93.4 [87.0, 98.4] | 92.6 [86.2, 97.7] | -0.8 [-2.7, +0.0] | 0.7312 |
| `prose_up_to_k` | 102 | Top-20 concepts not in the true items' top 20 | 9 [5, 14] | 5 [4, 12] | -4 [-5, +1] | 0.4396 |
| `prose_exactly_k` | 102 | False ESCO concepts per ad | 0.96 [0.58, 1.44] | 2.44 [2.18, 2.70] | +1.48 [+1.01, +1.91] | < 0.0001 |
| `prose_exactly_k` | 102 | Ads with at least one false concept (%) | 42.2 [29.3, 55.4] | 94.1 [88.5, 99.0] | +52.0 [+38.5, +65.1] | < 0.0001 |
| `prose_exactly_k` | 102 | ESCO precision (%) | 53.8 [41.9, 66.5] | 31.2 [25.2, 37.1] | -22.6 [-34.6, -12.7] | < 0.0001 |
| `prose_exactly_k` | 102 | ESCO recall (%) | 93.4 [87.0, 98.4] | 92.6 [86.7, 97.4] | -0.8 [-4.7, +3.8] | 0.7888 |
| `prose_exactly_k` | 102 | Top-20 concepts not in the true items' top 20 | 9 [5, 14] | 14 [10, 17] | +5 [+0, +9] | 0.1348 |
| `max_k_shown` | 102 | False ESCO concepts per ad | 0.96 [0.58, 1.44] | 0.66 [0.41, 0.93] | -0.30 [-0.60, -0.05] | 0.0188 |
| `max_k_shown` | 102 | Ads with at least one false concept (%) | 42.2 [29.3, 55.4] | 35.3 [23.6, 48.0] | -6.9 [-14.0, -1.0] | 0.0360 |
| `max_k_shown` | 102 | ESCO precision (%) | 53.8 [41.9, 66.5] | 63.0 [52.1, 74.0] | +9.2 [+1.8, +15.1] | 0.0188 |
| `max_k_shown` | 102 | ESCO recall (%) | 93.4 [87.0, 98.4] | 93.4 [87.0, 98.4] | +0.0 [+0.0, +0.0] | 1.0000 |
| `max_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 9 [5, 14] | 6 [3, 11] | -3 [-6, +1] | 0.2148 |
| `min_k_shown` | 102 | False ESCO concepts per ad | 0.96 [0.58, 1.44] | 2.03 [1.51, 2.59] | +1.07 [+0.68, +1.50] | < 0.0001 |
| `min_k_shown` | 102 | Ads with at least one false concept (%) | 42.2 [29.3, 55.4] | 66.7 [54.8, 77.9] | +24.5 [+14.1, +35.6] | < 0.0001 |
| `min_k_shown` | 102 | ESCO precision (%) | 53.8 [41.9, 66.5] | 34.9 [26.9, 44.0] | -18.9 [-28.5, -11.1] | < 0.0001 |
| `min_k_shown` | 102 | ESCO recall (%) | 93.4 [87.0, 98.4] | 91.0 [84.1, 96.8] | -2.5 [-6.4, +0.0] | 0.2500 |
| `min_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 9 [5, 14] | 10 [9, 17] | +1 [+0, +8] | 0.0896 |
| `min_k_shown_fewer_ok` | 102 | False ESCO concepts per ad | 0.96 [0.58, 1.44] | 1.39 [0.94, 1.90] | +0.43 [+0.15, +0.76] | 0.0014 |
| `min_k_shown_fewer_ok` | 102 | Ads with at least one false concept (%) | 42.2 [29.3, 55.4] | 51.0 [39.0, 63.2] | +8.8 [+1.9, +16.8] | 0.0218 |
| `min_k_shown_fewer_ok` | 102 | ESCO precision (%) | 53.8 [41.9, 66.5] | 44.3 [34.6, 55.3] | -9.5 [-17.2, -3.2] | 0.0012 |
| `min_k_shown_fewer_ok` | 102 | ESCO recall (%) | 93.4 [87.0, 98.4] | 92.6 [86.2, 97.7] | -0.8 [-2.7, +0.0] | 0.7312 |
| `min_k_shown_fewer_ok` | 102 | Top-20 concepts not in the true items' top 20 | 9 [5, 14] | 9 [7, 15] | +0 [-1, +5] | 0.5508 |

## 34. DeepSeek V3.2 (Bedrock), both sets, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 1.55 [1.19, 1.92] | 1.92 [1.71, 2.12] | +0.37 [+0.04, +0.69] | 0.0290 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 50.2 [41.5, 58.7] | 72.1 [65.8, 78.2] | +21.9 [+15.0, +29.2] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 33.4 [27.3, 40.8] | 30.7 [26.1, 35.6] | -2.7 [-8.0, +1.6] | 0.2346 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 64.3 [56.4, 72.2] | 70.4 [63.8, 77.0] | +6.1 [+0.8, +11.7] | 0.0210 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 14 [9, 17] | 12 [8, 15] | -2 [-5, +1] | 0.5094 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 1.55 [1.19, 1.92] | 2.19 [2.00, 2.38] | +0.64 [+0.29, +0.98] | 0.0004 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 50.2 [41.5, 58.7] | 80.5 [75.2, 85.5] | +30.2 [+23.0, +37.9] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 33.4 [27.3, 40.8] | 27.7 [23.6, 32.1] | -5.7 [-11.2, -1.2] | 0.0112 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 64.3 [56.4, 72.2] | 69.5 [63.0, 76.0] | +5.2 [-0.6, +11.2] | 0.0826 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 14 [9, 17] | 12 [9, 16] | -2 [-4, +2] | 0.8324 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 1.55 [1.19, 1.92] | 1.81 [1.58, 2.03] | +0.26 [-0.08, +0.57] | 0.1304 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 50.2 [41.5, 58.7] | 72.0 [64.7, 79.0] | +21.8 [+15.2, +29.0] | < 0.0001 |
| `max_k_shown` | 211 | ESCO precision (%) | 33.4 [27.3, 40.8] | 31.5 [26.3, 36.9] | -1.9 [-7.1, +2.6] | 0.3972 |
| `max_k_shown` | 211 | ESCO recall (%) | 64.3 [56.4, 72.2] | 68.6 [61.2, 75.8] | +4.3 [-1.3, +10.1] | 0.1626 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 14 [9, 17] | 14 [9, 16] | +0 [-4, +3] | 1.0000 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 1.55 [1.19, 1.92] | 4.34 [3.84, 4.88] | +2.79 [+2.23, +3.39] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 50.2 [41.5, 58.7] | 93.8 [89.9, 97.2] | +43.6 [+35.3, +52.0] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 33.4 [27.3, 40.8] | 17.0 [14.0, 20.6] | -16.4 [-22.5, -11.4] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 64.3 [56.4, 72.2] | 73.7 [66.9, 80.3] | +9.4 [+3.5, +15.5] | 0.0012 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 14 [9, 17] | 16 [12, 18] | +2 [-1, +6] | 0.3722 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 1.55 [1.19, 1.92] | 2.03 [1.67, 2.39] | +0.48 [+0.08, +0.89] | 0.0186 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 50.2 [41.5, 58.7] | 62.6 [54.3, 70.8] | +12.3 [+3.7, +21.0] | 0.0060 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 33.4 [27.3, 40.8] | 28.2 [23.7, 33.3] | -5.2 [-11.7, +0.3] | 0.0660 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 64.3 [56.4, 72.2] | 65.9 [58.4, 73.2] | +1.6 [-4.7, +7.5] | 0.6450 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 14 [9, 17] | 14 [10, 17] | +0 [-3, +4] | 1.0000 |

Top 20 concepts of the `min_k_shown` outputs: English; cooperate with colleagues; computer engineering; Agile development; work in an international environment; ICT project management methodologies; automation technology; German; work in shifts; process applications; engage with stakeholders; think innovatively; comply with schedule; perform scientific research; apply knowledge of science, technology and engineering; respect the diversity of cultural values and norms; monitor social impact; develop strategy to solve problems; build team spirit; promote inclusion

Top 20 concepts of the true items of the same ads: English; teach communication methods; SAP Data Services; German; computer engineering; recruit members; design cloud architecture; Danish; perform scientific research; computer science; react to events in time-critical environments; web services; perform business research; systems development life-cycle; Ruby (computer programming); solve technical problems; communication; Java (computer programming); body language; manage budgets

## 35. DeepSeek V3.2 (Bedrock), job-ad skills, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 109 | False ESCO concepts per ad | 2.59 [1.97, 3.27] | 2.60 [2.34, 2.86] | +0.01 [-0.56, +0.54] | 0.9504 |
| `prose_up_to_k` | 109 | Ads with at least one false concept (%) | 69.7 [57.8, 81.1] | 90.1 [84.1, 95.2] | +20.4 [+11.6, +29.9] | < 0.0001 |
| `prose_up_to_k` | 109 | ESCO precision (%) | 19.7 [13.9, 26.6] | 20.3 [14.8, 26.4] | +0.6 [-3.6, +4.3] | 0.7544 |
| `prose_up_to_k` | 109 | ESCO recall (%) | 51.9 [40.7, 63.7] | 54.3 [44.0, 64.8] | +2.4 [-5.5, +9.9] | 0.5406 |
| `prose_up_to_k` | 109 | Top-20 concepts not in the true items' top 20 | 18 [13, 19] | 18 [11, 18] | +0 [-5, +1] | 0.4118 |
| `prose_exactly_k` | 109 | False ESCO concepts per ad | 2.59 [1.97, 3.27] | 2.79 [2.54, 3.03] | +0.20 [-0.41, +0.75] | 0.4978 |
| `prose_exactly_k` | 109 | Ads with at least one false concept (%) | 69.7 [57.8, 81.1] | 94.5 [90.6, 97.6] | +24.8 [+15.0, +35.2] | < 0.0001 |
| `prose_exactly_k` | 109 | ESCO precision (%) | 19.7 [13.9, 26.6] | 18.7 [13.8, 24.2] | -0.9 [-5.4, +2.8] | 0.6348 |
| `prose_exactly_k` | 109 | ESCO recall (%) | 51.9 [40.7, 63.7] | 52.6 [42.7, 63.0] | +0.8 [-8.1, +9.5] | 0.8780 |
| `prose_exactly_k` | 109 | Top-20 concepts not in the true items' top 20 | 18 [13, 19] | 18 [11, 18] | +0 [-5, +2] | 0.5902 |
| `max_k_shown` | 109 | False ESCO concepts per ad | 2.59 [1.97, 3.27] | 2.33 [2.02, 2.65] | -0.26 [-0.81, +0.24] | 0.3398 |
| `max_k_shown` | 109 | Ads with at least one false concept (%) | 69.7 [57.8, 81.1] | 82.6 [73.9, 90.5] | +12.8 [+5.6, +20.9] | 0.0006 |
| `max_k_shown` | 109 | ESCO precision (%) | 19.7 [13.9, 26.6] | 21.8 [15.7, 28.7] | +2.2 [-2.0, +6.0] | 0.3038 |
| `max_k_shown` | 109 | ESCO recall (%) | 51.9 [40.7, 63.7] | 53.4 [42.6, 64.9] | +1.5 [-7.0, +10.0] | 0.7966 |
| `max_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 18 [13, 19] | 15 [11, 18] | -3 [-4, +1] | 0.6040 |
| `min_k_shown` | 109 | False ESCO concepts per ad | 2.59 [1.97, 3.27] | 4.53 [4.02, 5.07] | +1.94 [+1.35, +2.51] | < 0.0001 |
| `min_k_shown` | 109 | Ads with at least one false concept (%) | 69.7 [57.8, 81.1] | 98.2 [95.3, 100.0] | +28.4 [+17.4, +40.2] | < 0.0001 |
| `min_k_shown` | 109 | ESCO precision (%) | 19.7 [13.9, 26.6] | 13.6 [10.1, 17.7] | -6.0 [-11.0, -2.3] | 0.0008 |
| `min_k_shown` | 109 | ESCO recall (%) | 51.9 [40.7, 63.7] | 58.6 [47.9, 69.6] | +6.8 [-2.0, +15.7] | 0.1458 |
| `min_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 18 [13, 19] | 18 [14, 20] | +0 [-2, +4] | 1.0000 |
| `min_k_shown_fewer_ok` | 109 | False ESCO concepts per ad | 2.59 [1.97, 3.27] | 2.17 [1.70, 2.68] | -0.41 [-0.98, +0.14] | 0.1486 |
| `min_k_shown_fewer_ok` | 109 | Ads with at least one false concept (%) | 69.7 [57.8, 81.1] | 62.4 [50.9, 73.7] | -7.3 [-18.3, +3.7] | 0.2214 |
| `min_k_shown_fewer_ok` | 109 | ESCO precision (%) | 19.7 [13.9, 26.6] | 22.0 [16.4, 28.7] | +2.4 [-2.6, +7.2] | 0.3426 |
| `min_k_shown_fewer_ok` | 109 | ESCO recall (%) | 51.9 [40.7, 63.7] | 50.4 [39.7, 61.3] | -1.5 [-10.6, +7.2] | 0.8152 |
| `min_k_shown_fewer_ok` | 109 | Top-20 concepts not in the true items' top 20 | 18 [13, 19] | 18 [12, 19] | +0 [-4, +2] | 0.9390 |

## 36. DeepSeek V3.2 (Bedrock), job-ad knowledge, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 102 | False ESCO concepts per ad | 0.44 [0.25, 0.66] | 1.19 [0.91, 1.48] | +0.75 [+0.50, +1.03] | < 0.0001 |
| `prose_up_to_k` | 102 | Ads with at least one false concept (%) | 29.4 [17.6, 42.0] | 52.9 [42.6, 63.5] | +23.5 [+13.3, +34.3] | < 0.0001 |
| `prose_up_to_k` | 102 | ESCO precision (%) | 67.9 [56.3, 79.8] | 47.0 [38.9, 55.0] | -20.9 [-30.9, -12.6] | < 0.0001 |
| `prose_up_to_k` | 102 | ESCO recall (%) | 77.9 [66.4, 88.2] | 88.0 [81.6, 93.8] | +10.2 [+3.4, +18.6] | 0.0002 |
| `prose_up_to_k` | 102 | Top-20 concepts not in the true items' top 20 | 7 [4, 11] | 6 [5, 13] | -1 [-2, +5] | 0.7856 |
| `prose_exactly_k` | 102 | False ESCO concepts per ad | 0.44 [0.25, 0.66] | 1.55 [1.27, 1.84] | +1.11 [+0.83, +1.41] | < 0.0001 |
| `prose_exactly_k` | 102 | Ads with at least one false concept (%) | 29.4 [17.6, 42.0] | 65.5 [55.7, 74.7] | +36.1 [+25.7, +47.0] | < 0.0001 |
| `prose_exactly_k` | 102 | ESCO precision (%) | 67.9 [56.3, 79.8] | 40.4 [33.5, 47.4] | -27.4 [-38.0, -18.7] | < 0.0001 |
| `prose_exactly_k` | 102 | ESCO recall (%) | 77.9 [66.4, 88.2] | 87.9 [81.4, 93.6] | +10.0 [+3.0, +18.3] | 0.0018 |
| `prose_exactly_k` | 102 | Top-20 concepts not in the true items' top 20 | 7 [4, 11] | 8 [6, 13] | +1 [-1, +6] | 0.4466 |
| `max_k_shown` | 102 | False ESCO concepts per ad | 0.44 [0.25, 0.66] | 1.25 [0.94, 1.57] | +0.80 [+0.54, +1.11] | < 0.0001 |
| `max_k_shown` | 102 | Ads with at least one false concept (%) | 29.4 [17.6, 42.0] | 60.8 [49.0, 72.0] | +31.4 [+20.6, +43.1] | < 0.0001 |
| `max_k_shown` | 102 | ESCO precision (%) | 67.9 [56.3, 79.8] | 45.0 [36.4, 53.9] | -22.8 [-33.3, -14.2] | < 0.0001 |
| `max_k_shown` | 102 | ESCO recall (%) | 77.9 [66.4, 88.2] | 85.2 [76.9, 92.7] | +7.4 [+0.0, +16.0] | 0.0584 |
| `max_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 7 [4, 11] | 11 [7, 14] | +4 [+0, +7] | 0.1850 |
| `min_k_shown` | 102 | False ESCO concepts per ad | 0.44 [0.25, 0.66] | 4.13 [3.28, 5.11] | +3.69 [+2.81, +4.70] | < 0.0001 |
| `min_k_shown` | 102 | Ads with at least one false concept (%) | 29.4 [17.6, 42.0] | 89.2 [81.8, 95.2] | +59.8 [+47.6, +71.8] | < 0.0001 |
| `min_k_shown` | 102 | ESCO precision (%) | 67.9 [56.3, 79.8] | 20.7 [15.2, 27.4] | -47.1 [-59.1, -36.2] | < 0.0001 |
| `min_k_shown` | 102 | ESCO recall (%) | 77.9 [66.4, 88.2] | 90.2 [84.3, 95.5] | +12.3 [+5.0, +20.4] | 0.0006 |
| `min_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 7 [4, 11] | 15 [11, 18] | +8 [+3, +12] | 0.0004 |
| `min_k_shown_fewer_ok` | 102 | False ESCO concepts per ad | 0.44 [0.25, 0.66] | 1.87 [1.37, 2.42] | +1.43 [+0.93, +2.01] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | Ads with at least one false concept (%) | 29.4 [17.6, 42.0] | 62.7 [51.0, 74.0] | +33.3 [+20.0, +46.5] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | ESCO precision (%) | 67.9 [56.3, 79.8] | 34.6 [26.9, 43.1] | -33.3 [-45.9, -21.6] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | ESCO recall (%) | 77.9 [66.4, 88.2] | 82.8 [73.4, 91.1] | +4.9 [-3.3, +12.9] | 0.2768 |
| `min_k_shown_fewer_ok` | 102 | Top-20 concepts not in the true items' top 20 | 7 [4, 11] | 12 [8, 16] | +5 [+1, +9] | 0.0452 |

## 37. gpt-oss-120b (Bedrock), both sets, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 1.90 [1.53, 2.30] | 1.93 [1.73, 2.12] | +0.03 [-0.31, +0.34] | 0.8368 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 65.4 [57.5, 73.1] | 72.6 [66.9, 78.1] | +7.2 [+1.6, +12.9] | 0.0090 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 32.4 [27.0, 38.5] | 28.8 [24.6, 33.1] | -3.6 [-7.7, +0.2] | 0.0626 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 75.3 [68.4, 82.2] | 64.6 [58.8, 70.5] | -10.7 [-15.7, -5.7] | < 0.0001 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 17] | 14 [9, 15] | -1 [-4, +2] | 0.7938 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 1.90 [1.53, 2.30] | 2.59 [2.42, 2.76] | +0.69 [+0.33, +1.03] | 0.0004 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 65.4 [57.5, 73.1] | 84.3 [79.8, 88.4] | +18.9 [+12.8, +25.0] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 32.4 [27.0, 38.5] | 23.1 [19.7, 26.5] | -9.3 [-14.0, -5.3] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 75.3 [68.4, 82.2] | 64.3 [58.6, 70.0] | -11.0 [-16.0, -5.9] | < 0.0001 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 17] | 12 [10, 16] | -3 [-4, +3] | 1.0000 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 1.90 [1.53, 2.30] | 2.06 [1.82, 2.29] | +0.16 [-0.20, +0.49] | 0.3826 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 65.4 [57.5, 73.1] | 74.4 [67.3, 81.1] | +9.0 [+2.9, +15.1] | 0.0032 |
| `max_k_shown` | 211 | ESCO precision (%) | 32.4 [27.0, 38.5] | 27.7 [23.4, 32.2] | -4.7 [-9.4, -0.5] | 0.0246 |
| `max_k_shown` | 211 | ESCO recall (%) | 75.3 [68.4, 82.2] | 65.1 [58.1, 71.9] | -10.2 [-16.2, -4.3] | 0.0014 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 17] | 16 [10, 16] | +1 [-3, +3] | 1.0000 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 1.90 [1.53, 2.30] | 3.38 [3.14, 3.63] | +1.48 [+1.12, +1.84] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 65.4 [57.5, 73.1] | 96.7 [93.7, 99.1] | +31.3 [+23.6, +38.9] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 32.4 [27.0, 38.5] | 19.3 [16.0, 22.6] | -13.1 [-17.9, -9.0] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 75.3 [68.4, 82.2] | 66.7 [59.9, 73.3] | -8.6 [-15.0, -2.3] | 0.0090 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 17] | 15 [11, 17] | +0 [-2, +4] | 0.8302 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 1.90 [1.53, 2.30] | 2.32 [1.99, 2.67] | +0.42 [+0.14, +0.73] | 0.0032 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 65.4 [57.5, 73.1] | 75.8 [68.6, 82.8] | +10.4 [+3.4, +17.6] | 0.0034 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 32.4 [27.0, 38.5] | 25.9 [21.3, 30.8] | -6.5 [-10.8, -3.0] | 0.0004 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 75.3 [68.4, 82.2] | 67.1 [59.6, 74.4] | -8.2 [-14.4, -2.3] | 0.0088 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 17] | 12 [10, 16] | -3 [-3, +3] | 1.0000 |

Top 20 concepts of the `min_k_shown` outputs: English; Agile development; DevOps; cooperate with colleagues; computer engineering; implement front-end website design; perform scientific research; develop test procedures; seek innovation in current practices; continuous improvement philosophies; project commissioning; follow work schedule; maintain internal communication systems; web programming; develop strategy to solve problems; health care system; ICT project management methodologies; quality assurance methodologies; teach communication methods; SAP Data Services

Top 20 concepts of the true items of the same ads: English; teach communication methods; SAP Data Services; German; computer engineering; recruit members; design cloud architecture; Danish; perform scientific research; computer science; react to events in time-critical environments; web services; perform business research; systems development life-cycle; Ruby (computer programming); solve technical problems; communication; Java (computer programming); body language; manage budgets

## 38. gpt-oss-120b (Bedrock), job-ad skills, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 109 | False ESCO concepts per ad | 2.67 [2.18, 3.19] | 2.63 [2.36, 2.89] | -0.04 [-0.48, +0.37] | 0.8666 |
| `prose_up_to_k` | 109 | Ads with at least one false concept (%) | 89.0 [80.6, 96.3] | 90.5 [84.5, 95.5] | +1.5 [-3.0, +6.7] | 0.6038 |
| `prose_up_to_k` | 109 | ESCO precision (%) | 23.2 [17.8, 29.1] | 18.0 [13.4, 22.9] | -5.2 [-9.1, -1.8] | 0.0028 |
| `prose_up_to_k` | 109 | ESCO recall (%) | 66.2 [55.7, 76.6] | 47.2 [38.9, 55.8] | -18.9 [-27.2, -11.3] | < 0.0001 |
| `prose_up_to_k` | 109 | Top-20 concepts not in the true items' top 20 | 18 [13, 19] | 17 [12, 18] | -1 [-4, +3] | 1.0000 |
| `prose_exactly_k` | 109 | False ESCO concepts per ad | 2.67 [2.18, 3.19] | 3.10 [2.85, 3.33] | +0.43 [-0.04, +0.87] | 0.0800 |
| `prose_exactly_k` | 109 | Ads with at least one false concept (%) | 89.0 [80.6, 96.3] | 94.1 [88.6, 98.5] | +5.1 [+0.4, +10.9] | 0.0322 |
| `prose_exactly_k` | 109 | ESCO precision (%) | 23.2 [17.8, 29.1] | 15.7 [12.0, 19.7] | -7.5 [-11.8, -3.9] | < 0.0001 |
| `prose_exactly_k` | 109 | ESCO recall (%) | 66.2 [55.7, 76.6] | 47.2 [39.8, 55.0] | -18.9 [-27.2, -10.8] | < 0.0001 |
| `prose_exactly_k` | 109 | Top-20 concepts not in the true items' top 20 | 18 [13, 19] | 17 [13, 19] | -1 [-3, +3] | 1.0000 |
| `max_k_shown` | 109 | False ESCO concepts per ad | 2.67 [2.18, 3.19] | 2.79 [2.46, 3.11] | +0.12 [-0.38, +0.59] | 0.6296 |
| `max_k_shown` | 109 | Ads with at least one false concept (%) | 89.0 [80.6, 96.3] | 92.7 [85.2, 98.2] | +3.7 [-2.8, +10.7] | 0.3538 |
| `max_k_shown` | 109 | ESCO precision (%) | 23.2 [17.8, 29.1] | 17.2 [12.4, 22.4] | -6.1 [-10.9, -1.5] | 0.0070 |
| `max_k_shown` | 109 | ESCO recall (%) | 66.2 [55.7, 76.6] | 47.4 [36.8, 58.2] | -18.8 [-29.0, -8.7] | 0.0002 |
| `max_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 18 [13, 19] | 17 [13, 19] | -1 [-3, +4] | 1.0000 |
| `min_k_shown` | 109 | False ESCO concepts per ad | 2.67 [2.18, 3.19] | 3.58 [3.24, 3.92] | +0.91 [+0.43, +1.36] | < 0.0001 |
| `min_k_shown` | 109 | Ads with at least one false concept (%) | 89.0 [80.6, 96.3] | 97.2 [92.6, 100.0] | +8.3 [+1.0, +16.5] | 0.0234 |
| `min_k_shown` | 109 | ESCO precision (%) | 23.2 [17.8, 29.1] | 14.5 [10.6, 18.6] | -8.7 [-13.1, -5.0] | < 0.0001 |
| `min_k_shown` | 109 | ESCO recall (%) | 66.2 [55.7, 76.6] | 49.6 [39.6, 60.0] | -16.5 [-25.7, -7.5] | 0.0006 |
| `min_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 18 [13, 19] | 18 [13, 19] | +0 [-3, +4] | 0.9628 |
| `min_k_shown_fewer_ok` | 109 | False ESCO concepts per ad | 2.67 [2.18, 3.19] | 2.76 [2.37, 3.17] | +0.09 [-0.35, +0.53] | 0.6954 |
| `min_k_shown_fewer_ok` | 109 | Ads with at least one false concept (%) | 89.0 [80.6, 96.3] | 90.8 [84.1, 96.4] | +1.8 [-4.3, +8.3] | 0.6802 |
| `min_k_shown_fewer_ok` | 109 | ESCO precision (%) | 23.2 [17.8, 29.1] | 18.2 [13.1, 23.8] | -5.0 [-9.5, -1.1] | 0.0112 |
| `min_k_shown_fewer_ok` | 109 | ESCO recall (%) | 66.2 [55.7, 76.6] | 50.4 [39.3, 61.4] | -15.8 [-25.7, -6.7] | 0.0008 |
| `min_k_shown_fewer_ok` | 109 | Top-20 concepts not in the true items' top 20 | 18 [13, 19] | 18 [12, 19] | +0 [-3, +3] | 1.0000 |

## 39. gpt-oss-120b (Bedrock), job-ad knowledge, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 102 | False ESCO concepts per ad | 1.08 [0.56, 1.77] | 1.18 [0.91, 1.47] | +0.10 [-0.46, +0.54] | 0.6508 |
| `prose_up_to_k` | 102 | Ads with at least one false concept (%) | 40.2 [27.3, 53.4] | 53.5 [43.9, 63.1] | +13.3 [+3.0, +23.7] | 0.0122 |
| `prose_up_to_k` | 102 | ESCO precision (%) | 48.6 [34.5, 65.5] | 45.8 [37.7, 54.5] | -2.8 [-16.3, +7.4] | 0.6096 |
| `prose_up_to_k` | 102 | ESCO recall (%) | 85.2 [76.2, 93.1] | 83.6 [77.1, 89.8] | -1.6 [-8.2, +5.7] | 0.6652 |
| `prose_up_to_k` | 102 | Top-20 concepts not in the true items' top 20 | 10 [6, 17] | 9 [5, 13] | -1 [-8, +3] | 0.5734 |
| `prose_exactly_k` | 102 | False ESCO concepts per ad | 1.08 [0.56, 1.77] | 2.06 [1.83, 2.29] | +0.98 [+0.36, +1.47] | 0.0034 |
| `prose_exactly_k` | 102 | Ads with at least one false concept (%) | 40.2 [27.3, 53.4] | 73.7 [66.9, 80.4] | +33.5 [+22.3, +44.9] | < 0.0001 |
| `prose_exactly_k` | 102 | ESCO precision (%) | 48.6 [34.5, 65.5] | 32.5 [26.7, 38.5] | -16.1 [-31.1, -4.6] | 0.0032 |
| `prose_exactly_k` | 102 | ESCO recall (%) | 85.2 [76.2, 93.1] | 83.0 [76.2, 89.4] | -2.3 [-8.8, +4.7] | 0.5194 |
| `prose_exactly_k` | 102 | Top-20 concepts not in the true items' top 20 | 10 [6, 17] | 12 [6, 14] | +2 [-6, +5] | 0.9540 |
| `max_k_shown` | 102 | False ESCO concepts per ad | 1.08 [0.56, 1.77] | 1.27 [0.95, 1.61] | +0.20 [-0.37, +0.65] | 0.4500 |
| `max_k_shown` | 102 | Ads with at least one false concept (%) | 40.2 [27.3, 53.4] | 54.9 [43.3, 66.3] | +14.7 [+4.8, +25.0] | 0.0054 |
| `max_k_shown` | 102 | ESCO precision (%) | 48.6 [34.5, 65.5] | 44.2 [35.7, 53.6] | -4.4 [-17.9, +6.0] | 0.4280 |
| `max_k_shown` | 102 | ESCO recall (%) | 85.2 [76.2, 93.1] | 84.4 [77.2, 91.2] | -0.8 [-7.2, +6.0] | 0.9120 |
| `max_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 10 [6, 17] | 10 [6, 13] | +0 [-6, +4] | 0.7824 |
| `min_k_shown` | 102 | False ESCO concepts per ad | 1.08 [0.56, 1.77] | 3.17 [2.83, 3.55] | +2.09 [+1.50, +2.62] | < 0.0001 |
| `min_k_shown` | 102 | Ads with at least one false concept (%) | 40.2 [27.3, 53.4] | 96.1 [92.1, 99.0] | +55.9 [+42.6, +69.0] | < 0.0001 |
| `min_k_shown` | 102 | ESCO precision (%) | 48.6 [34.5, 65.5] | 24.4 [19.0, 29.9] | -24.2 [-39.8, -12.5] | < 0.0001 |
| `min_k_shown` | 102 | ESCO recall (%) | 85.2 [76.2, 93.1] | 85.2 [78.3, 91.9] | +0.0 [-8.7, +9.2] | 1.0000 |
| `min_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 10 [6, 17] | 12 [10, 16] | +2 [-3, +8] | 0.4942 |
| `min_k_shown_fewer_ok` | 102 | False ESCO concepts per ad | 1.08 [0.56, 1.77] | 1.85 [1.35, 2.44] | +0.77 [+0.40, +1.16] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | Ads with at least one false concept (%) | 40.2 [27.3, 53.4] | 59.8 [47.2, 72.0] | +19.6 [+6.7, +32.7] | 0.0026 |
| `min_k_shown_fewer_ok` | 102 | ESCO precision (%) | 48.6 [34.5, 65.5] | 35.5 [27.0, 45.1] | -13.1 [-25.5, -4.4] | 0.0006 |
| `min_k_shown_fewer_ok` | 102 | ESCO recall (%) | 85.2 [76.2, 93.1] | 85.2 [77.7, 92.3] | +0.0 [-8.4, +8.8] | 1.0000 |
| `min_k_shown_fewer_ok` | 102 | Top-20 concepts not in the true items' top 20 | 10 [6, 17] | 11 [7, 16] | +1 [-3, +5] | 0.9464 |

## 40. gpt-oss-20b (Bedrock), both sets, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 2.46 [1.96, 3.01] | 2.30 [2.11, 2.49] | -0.16 [-0.62, +0.28] | 0.4988 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 61.1 [52.8, 69.5] | 81.2 [76.5, 85.6] | +20.1 [+12.8, +27.8] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 21.7 [17.3, 27.0] | 25.2 [21.4, 29.2] | +3.5 [-0.5, +6.9] | 0.0850 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 56.5 [48.1, 64.8] | 64.1 [57.8, 70.3] | +7.6 [+0.8, +14.6] | 0.0274 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 13 [11, 18] | 13 [9, 16] | +0 [-5, +1] | 0.3830 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 2.46 [1.96, 3.01] | 2.58 [2.41, 2.75] | +0.11 [-0.34, +0.55] | 0.5898 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 61.1 [52.8, 69.5] | 85.4 [81.3, 89.4] | +24.3 [+17.4, +31.5] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 21.7 [17.3, 27.0] | 21.6 [18.4, 24.9] | -0.1 [-4.2, +3.3] | 0.9428 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 56.5 [48.1, 64.8] | 58.8 [52.9, 64.9] | +2.4 [-5.1, +10.1] | 0.5472 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 13 [11, 18] | 14 [10, 17] | +1 [-4, +2] | 0.6874 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 2.46 [1.96, 3.01] | 1.91 [1.67, 2.14] | -0.56 [-1.03, -0.11] | 0.0116 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 61.1 [52.8, 69.5] | 72.5 [65.4, 79.5] | +11.4 [+3.5, +19.5] | 0.0058 |
| `max_k_shown` | 211 | ESCO precision (%) | 21.7 [17.3, 27.0] | 28.6 [24.1, 33.5] | +6.9 [+2.6, +10.9] | 0.0020 |
| `max_k_shown` | 211 | ESCO recall (%) | 56.5 [48.1, 64.8] | 63.1 [56.3, 70.0] | +6.7 [-0.4, +14.0] | 0.0658 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 13 [11, 18] | 12 [9, 16] | -1 [-5, +1] | 0.4534 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 2.46 [1.96, 3.01] | 3.40 [3.02, 3.79] | +0.93 [+0.57, +1.29] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 61.1 [52.8, 69.5] | 88.2 [82.6, 93.2] | +27.0 [+19.5, +34.9] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 21.7 [17.3, 27.0] | 19.1 [16.1, 22.4] | -2.6 [-6.3, +0.4] | 0.0972 |
| `min_k_shown` | 211 | ESCO recall (%) | 56.5 [48.1, 64.8] | 66.3 [59.6, 73.1] | +9.8 [+2.7, +17.2] | 0.0074 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 13 [11, 18] | 11 [11, 17] | -2 [-4, +2] | 0.8808 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 2.46 [1.96, 3.01] | 2.53 [2.13, 2.95] | +0.06 [-0.35, +0.46] | 0.7614 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 61.1 [52.8, 69.5] | 72.5 [64.7, 80.2] | +11.4 [+2.8, +20.4] | 0.0108 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 21.7 [17.3, 27.0] | 21.7 [17.7, 26.3] | +0.0 [-4.0, +3.6] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 56.5 [48.1, 64.8] | 58.0 [50.7, 65.5] | +1.6 [-6.8, +10.0] | 0.7500 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 13 [11, 18] | 15 [12, 18] | +2 [-3, +4] | 0.9848 |

Top 20 concepts of the `min_k_shown` outputs: English; Java (computer programming); computer engineering; continuous improvement philosophies; JavaScript; cloud technologies; German; apply knowledge of science, technology and engineering; web programming; react to events in time-critical environments; implement front-end website design; Python (computer programming); DevOps; web services; design cloud architecture; Danish; perform scientific research; manage ICT virtualisation environments; SAP R3; Agile development

Top 20 concepts of the true items of the same ads: English; teach communication methods; SAP Data Services; German; computer engineering; recruit members; design cloud architecture; Danish; perform scientific research; computer science; react to events in time-critical environments; web services; perform business research; systems development life-cycle; Ruby (computer programming); solve technical problems; communication; Java (computer programming); body language; manage budgets

## 41. gpt-oss-20b (Bedrock), job-ad skills, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 109 | False ESCO concepts per ad | 3.55 [2.79, 4.37] | 2.78 [2.48, 3.07] | -0.77 [-1.47, -0.13] | 0.0172 |
| `prose_up_to_k` | 109 | Ads with at least one false concept (%) | 86.2 [76.7, 94.5] | 91.2 [85.7, 95.8] | +5.0 [-3.6, +14.4] | 0.2786 |
| `prose_up_to_k` | 109 | ESCO precision (%) | 12.4 [8.2, 17.3] | 16.9 [12.1, 22.5] | +4.5 [+1.0, +8.0] | 0.0124 |
| `prose_up_to_k` | 109 | ESCO recall (%) | 41.4 [29.7, 53.5] | 46.5 [36.5, 56.3] | +5.1 [-5.0, +14.9] | 0.3174 |
| `prose_up_to_k` | 109 | Top-20 concepts not in the true items' top 20 | 19 [15, 20] | 17 [13, 19] | -2 [-5, +2] | 0.5334 |
| `prose_exactly_k` | 109 | False ESCO concepts per ad | 3.55 [2.79, 4.37] | 2.95 [2.73, 3.17] | -0.60 [-1.34, +0.07] | 0.0832 |
| `prose_exactly_k` | 109 | Ads with at least one false concept (%) | 86.2 [76.7, 94.5] | 93.2 [88.9, 96.9] | +7.0 [-0.0, +15.3] | 0.0564 |
| `prose_exactly_k` | 109 | ESCO precision (%) | 12.4 [8.2, 17.3] | 14.6 [10.5, 19.0] | +2.1 [-1.3, +5.4] | 0.2312 |
| `prose_exactly_k` | 109 | ESCO recall (%) | 41.4 [29.7, 53.5] | 41.2 [33.0, 49.6] | -0.2 [-11.3, +10.6] | 0.9950 |
| `prose_exactly_k` | 109 | Top-20 concepts not in the true items' top 20 | 19 [15, 20] | 18 [14, 20] | -1 [-4, +2] | 0.8344 |
| `max_k_shown` | 109 | False ESCO concepts per ad | 3.55 [2.79, 4.37] | 2.50 [2.15, 2.82] | -1.06 [-1.75, -0.43] | < 0.0001 |
| `max_k_shown` | 109 | Ads with at least one false concept (%) | 86.2 [76.7, 94.5] | 87.2 [79.0, 94.4] | +0.9 [-7.4, +9.6] | 0.9094 |
| `max_k_shown` | 109 | ESCO precision (%) | 12.4 [8.2, 17.3] | 17.8 [12.6, 23.8] | +5.4 [+1.6, +9.3] | 0.0032 |
| `max_k_shown` | 109 | ESCO recall (%) | 41.4 [29.7, 53.5] | 44.4 [34.2, 54.5] | +3.0 [-6.3, +12.4] | 0.5916 |
| `max_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 19 [15, 20] | 18 [13, 19] | -1 [-4, +2] | 0.6252 |
| `min_k_shown` | 109 | False ESCO concepts per ad | 3.55 [2.79, 4.37] | 4.01 [3.51, 4.54] | +0.46 [-0.13, +1.01] | 0.1234 |
| `min_k_shown` | 109 | Ads with at least one false concept (%) | 86.2 [76.7, 94.5] | 96.3 [91.4, 100.0] | +10.1 [+2.7, +18.9] | 0.0086 |
| `min_k_shown` | 109 | ESCO precision (%) | 12.4 [8.2, 17.3] | 12.6 [9.0, 16.9] | +0.2 [-3.2, +3.5] | 0.9472 |
| `min_k_shown` | 109 | ESCO recall (%) | 41.4 [29.7, 53.5] | 47.4 [37.1, 58.3] | +6.0 [-4.8, +17.0] | 0.3030 |
| `min_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 19 [15, 20] | 18 [14, 20] | -1 [-3, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 109 | False ESCO concepts per ad | 3.55 [2.79, 4.37] | 3.23 [2.61, 3.91] | -0.32 [-0.85, +0.17] | 0.2146 |
| `min_k_shown_fewer_ok` | 109 | Ads with at least one false concept (%) | 86.2 [76.7, 94.5] | 84.4 [75.5, 92.3] | -1.8 [-11.3, +8.3] | 0.7730 |
| `min_k_shown_fewer_ok` | 109 | ESCO precision (%) | 12.4 [8.2, 17.3] | 15.4 [10.7, 21.1] | +2.9 [-0.6, +6.9] | 0.1084 |
| `min_k_shown_fewer_ok` | 109 | ESCO recall (%) | 41.4 [29.7, 53.5] | 48.1 [37.8, 58.3] | +6.8 [-4.7, +18.5] | 0.2826 |
| `min_k_shown_fewer_ok` | 109 | Top-20 concepts not in the true items' top 20 | 19 [15, 20] | 17 [14, 20] | -2 [-3, +2] | 1.0000 |

## 42. gpt-oss-20b (Bedrock), job-ad knowledge, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 102 | False ESCO concepts per ad | 1.30 [0.67, 2.07] | 1.79 [1.52, 2.07] | +0.49 [-0.14, +1.04] | 0.1244 |
| `prose_up_to_k` | 102 | Ads with at least one false concept (%) | 34.3 [22.3, 47.1] | 70.6 [62.8, 78.0] | +36.3 [+25.0, +47.5] | < 0.0001 |
| `prose_up_to_k` | 102 | ESCO precision (%) | 40.1 [28.2, 56.4] | 35.7 [29.3, 42.2] | -4.3 [-18.6, +4.8] | 0.4086 |
| `prose_up_to_k` | 102 | ESCO recall (%) | 73.0 [61.5, 83.3] | 83.3 [77.2, 88.5] | +10.3 [+0.8, +21.2] | 0.0326 |
| `prose_up_to_k` | 102 | Top-20 concepts not in the true items' top 20 | 12 [8, 17] | 11 [6, 14] | -1 [-8, +3] | 0.4438 |
| `prose_exactly_k` | 102 | False ESCO concepts per ad | 1.30 [0.67, 2.07] | 2.18 [1.92, 2.45] | +0.88 [+0.26, +1.42] | 0.0078 |
| `prose_exactly_k` | 102 | Ads with at least one false concept (%) | 34.3 [22.3, 47.1] | 77.1 [69.8, 83.9] | +42.7 [+31.5, +54.0] | < 0.0001 |
| `prose_exactly_k` | 102 | ESCO precision (%) | 40.1 [28.2, 56.4] | 30.0 [24.6, 35.3] | -10.1 [-24.8, -0.6] | 0.0320 |
| `prose_exactly_k` | 102 | ESCO recall (%) | 73.0 [61.5, 83.3] | 78.0 [70.4, 85.2] | +5.1 [-5.7, +17.5] | 0.3726 |
| `prose_exactly_k` | 102 | Top-20 concepts not in the true items' top 20 | 12 [8, 17] | 12 [7, 15] | +0 [-7, +4] | 0.6482 |
| `max_k_shown` | 102 | False ESCO concepts per ad | 1.30 [0.67, 2.07] | 1.27 [0.96, 1.60] | -0.03 [-0.75, +0.60] | 0.9916 |
| `max_k_shown` | 102 | Ads with at least one false concept (%) | 34.3 [22.3, 47.1] | 56.9 [45.1, 68.5] | +22.5 [+9.0, +36.0] | 0.0018 |
| `max_k_shown` | 102 | ESCO precision (%) | 40.1 [28.2, 56.4] | 44.0 [35.9, 52.6] | +3.9 [-11.2, +14.6] | 0.5984 |
| `max_k_shown` | 102 | ESCO recall (%) | 73.0 [61.5, 83.3] | 83.6 [75.2, 91.4] | +10.7 [+0.8, +22.3] | 0.0450 |
| `max_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 12 [8, 17] | 11 [7, 14] | -1 [-8, +3] | 0.4760 |
| `min_k_shown` | 102 | False ESCO concepts per ad | 1.30 [0.67, 2.07] | 2.75 [2.23, 3.30] | +1.44 [+0.97, +1.90] | < 0.0001 |
| `min_k_shown` | 102 | Ads with at least one false concept (%) | 34.3 [22.3, 47.1] | 79.4 [69.5, 88.5] | +45.1 [+31.7, +57.7] | < 0.0001 |
| `min_k_shown` | 102 | ESCO precision (%) | 40.1 [28.2, 56.4] | 27.5 [22.0, 33.4] | -12.6 [-25.9, -4.7] | 0.0004 |
| `min_k_shown` | 102 | ESCO recall (%) | 73.0 [61.5, 83.3] | 86.9 [79.0, 93.9] | +13.9 [+5.0, +24.8] | 0.0010 |
| `min_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 12 [8, 17] | 12 [10, 17] | +0 [-3, +5] | 1.0000 |
| `min_k_shown_fewer_ok` | 102 | False ESCO concepts per ad | 1.30 [0.67, 2.07] | 1.77 [1.34, 2.24] | +0.47 [-0.21, +1.11] | 0.1754 |
| `min_k_shown_fewer_ok` | 102 | Ads with at least one false concept (%) | 34.3 [22.3, 47.1] | 59.8 [47.6, 71.7] | +25.5 [+10.4, +40.6] | 0.0018 |
| `min_k_shown_fewer_ok` | 102 | ESCO precision (%) | 40.1 [28.2, 56.4] | 31.7 [24.6, 39.5] | -8.4 [-23.5, +1.9] | 0.1140 |
| `min_k_shown_fewer_ok` | 102 | ESCO recall (%) | 73.0 [61.5, 83.3] | 68.9 [58.6, 78.6] | -4.1 [-15.7, +7.8] | 0.5460 |
| `min_k_shown_fewer_ok` | 102 | Top-20 concepts not in the true items' top 20 | 12 [8, 17] | 15 [10, 17] | +3 [-4, +7] | 0.9056 |

## 43. Grok 4.3 (Bedrock), both sets, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 1.24 [0.87, 1.63] | 1.22 [1.01, 1.43] | -0.01 [-0.37, +0.33] | 0.9832 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 40.3 [32.2, 48.2] | 55.0 [47.8, 62.0] | +14.7 [+8.0, +21.5] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 35.1 [27.5, 44.8] | 37.2 [30.8, 44.4] | +2.2 [-6.2, +9.2] | 0.6174 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 55.3 [47.2, 63.6] | 60.0 [52.2, 68.1] | +4.7 [-1.5, +11.5] | 0.1744 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 13 [9, 17] | 13 [9, 16] | +0 [-5, +3] | 0.7184 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 1.24 [0.87, 1.63] | 1.93 [1.68, 2.16] | +0.69 [+0.29, +1.07] | 0.0006 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 40.3 [32.2, 48.2] | 72.5 [65.0, 79.7] | +32.2 [+23.6, +40.8] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 35.1 [27.5, 44.8] | 29.8 [25.0, 35.2] | -5.2 [-13.5, +1.3] | 0.1272 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 55.3 [47.2, 63.6] | 67.8 [60.5, 75.4] | +12.5 [+5.6, +19.9] | < 0.0001 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 13 [9, 17] | 13 [9, 16] | +0 [-4, +3] | 0.8718 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 1.24 [0.87, 1.63] | 1.03 [0.82, 1.25] | -0.20 [-0.51, +0.09] | 0.1842 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 40.3 [32.2, 48.2] | 46.0 [38.8, 53.1] | +5.7 [+0.0, +11.7] | 0.0528 |
| `max_k_shown` | 211 | ESCO precision (%) | 35.1 [27.5, 44.8] | 40.1 [33.0, 48.0] | +5.0 [-1.8, +10.9] | 0.1496 |
| `max_k_shown` | 211 | ESCO recall (%) | 55.3 [47.2, 63.6] | 57.3 [49.1, 65.6] | +2.0 [-2.8, +7.1] | 0.4904 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 13 [9, 17] | 13 [8, 15] | +0 [-5, +1] | 0.4138 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 1.24 [0.87, 1.63] | 3.36 [2.71, 4.05] | +2.12 [+1.46, +2.84] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 40.3 [32.2, 48.2] | 76.3 [69.2, 83.0] | +36.0 [+27.5, +44.8] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 35.1 [27.5, 44.8] | 19.5 [15.3, 24.5] | -15.6 [-24.2, -9.0] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 55.3 [47.2, 63.6] | 67.1 [59.6, 74.4] | +11.8 [+5.2, +18.7] | < 0.0001 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 13 [9, 17] | 16 [12, 18] | +3 [-1, +6] | 0.4288 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 1.24 [0.87, 1.63] | 2.41 [2.00, 2.82] | +1.17 [+0.70, +1.67] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 40.3 [32.2, 48.2] | 65.9 [58.9, 72.6] | +25.6 [+17.5, +33.8] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 35.1 [27.5, 44.8] | 23.7 [19.1, 29.2] | -11.4 [-19.8, -4.7] | 0.0008 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 55.3 [47.2, 63.6] | 62.0 [54.2, 69.9] | +6.7 [+0.8, +12.9] | 0.0288 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 13 [9, 17] | 14 [10, 17] | +1 [-3, +5] | 0.9610 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 1.24 [0.87, 1.63] | 3.86 [3.41, 4.37] | +2.62 [+2.04, +3.27] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 40.3 [32.2, 48.2] | 98.1 [96.0, 99.5] | +57.8 [+50.2, +65.6] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 35.1 [27.5, 44.8] | 17.9 [14.4, 21.8] | -17.1 [-26.0, -10.4] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO recall (%) | 55.3 [47.2, 63.6] | 69.8 [62.3, 77.3] | +14.5 [+7.0, +22.3] | 0.0004 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 13 [9, 17] | 15 [13, 18] | +2 [-2, +7] | 0.4042 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 1.24 [0.87, 1.63] | 1.46 [1.12, 1.82] | +0.22 [-0.18, +0.63] | 0.2814 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 40.3 [32.2, 48.2] | 45.0 [37.3, 53.1] | +4.7 [-2.9, +12.3] | 0.2430 |
| `min_k_escape` | 211 | ESCO precision (%) | 35.1 [27.5, 44.8] | 26.1 [19.9, 33.2] | -8.9 [-17.6, -1.4] | 0.0204 |
| `min_k_escape` | 211 | ESCO recall (%) | 55.3 [47.2, 63.6] | 42.7 [34.4, 51.3] | -12.5 [-20.9, -4.7] | 0.0014 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 13 [9, 17] | 14 [10, 17] | +1 [-4, +4] | 1.0000 |

Top 20 concepts of the `min_k_shown` outputs: English; cooperate with colleagues; Agile development; Java (computer programming); apply knowledge of science, technology and engineering; cloud technologies; manage ICT virtualisation environments; team building; continuous improvement philosophies; business intelligence; German; strategic planning; engage with stakeholders; ICT project management methodologies; Python (computer programming); design cloud architecture; JavaScript; write Danish; mathematics; comply with schedule

Top 20 concepts of the true items of the same ads: English; teach communication methods; SAP Data Services; German; computer engineering; recruit members; design cloud architecture; Danish; perform scientific research; computer science; react to events in time-critical environments; web services; perform business research; systems development life-cycle; Ruby (computer programming); solve technical problems; communication; Java (computer programming); body language; manage budgets

## 44. Grok 4.3 (Bedrock), job-ad skills, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 109 | False ESCO concepts per ad | 2.22 [1.56, 2.93] | 2.05 [1.72, 2.38] | -0.17 [-0.83, +0.43] | 0.6164 |
| `prose_up_to_k` | 109 | Ads with at least one false concept (%) | 63.3 [50.5, 75.2] | 85.3 [76.6, 92.8] | +22.0 [+12.7, +32.4] | < 0.0001 |
| `prose_up_to_k` | 109 | ESCO precision (%) | 20.9 [14.7, 29.5] | 21.8 [15.2, 29.1] | +0.8 [-5.5, +6.4] | 0.8046 |
| `prose_up_to_k` | 109 | ESCO recall (%) | 48.1 [37.1, 59.6] | 46.6 [35.4, 58.3] | -1.5 [-9.0, +6.1] | 0.7594 |
| `prose_up_to_k` | 109 | Top-20 concepts not in the true items' top 20 | 17 [13, 19] | 16 [12, 18] | -1 [-5, +2] | 0.5476 |
| `prose_exactly_k` | 109 | False ESCO concepts per ad | 2.22 [1.56, 2.93] | 2.52 [2.20, 2.82] | +0.30 [-0.38, +0.93] | 0.3736 |
| `prose_exactly_k` | 109 | Ads with at least one false concept (%) | 63.3 [50.5, 75.2] | 89.9 [81.7, 96.5] | +26.6 [+16.0, +38.3] | < 0.0001 |
| `prose_exactly_k` | 109 | ESCO precision (%) | 20.9 [14.7, 29.5] | 20.1 [14.4, 26.6] | -0.9 [-6.8, +3.8] | 0.7138 |
| `prose_exactly_k` | 109 | ESCO recall (%) | 48.1 [37.1, 59.6] | 51.9 [40.5, 63.9] | +3.8 [-3.2, +11.6] | 0.3608 |
| `prose_exactly_k` | 109 | Top-20 concepts not in the true items' top 20 | 17 [13, 19] | 16 [12, 19] | -1 [-5, +2] | 0.6024 |
| `max_k_shown` | 109 | False ESCO concepts per ad | 2.22 [1.56, 2.93] | 1.85 [1.49, 2.22] | -0.37 [-0.94, +0.18] | 0.1948 |
| `max_k_shown` | 109 | Ads with at least one false concept (%) | 63.3 [50.5, 75.2] | 77.1 [66.1, 87.2] | +13.8 [+5.7, +22.8] | 0.0002 |
| `max_k_shown` | 109 | ESCO precision (%) | 20.9 [14.7, 29.5] | 23.5 [16.5, 31.6] | +2.6 [-3.1, +7.5] | 0.3526 |
| `max_k_shown` | 109 | ESCO recall (%) | 48.1 [37.1, 59.6] | 46.6 [35.3, 58.3] | -1.5 [-8.5, +5.4] | 0.7448 |
| `max_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 17 [13, 19] | 17 [11, 18] | +0 [-5, +2] | 0.5290 |
| `min_k_shown` | 109 | False ESCO concepts per ad | 2.22 [1.56, 2.93] | 3.94 [3.30, 4.59] | +1.72 [+1.13, +2.37] | < 0.0001 |
| `min_k_shown` | 109 | Ads with at least one false concept (%) | 63.3 [50.5, 75.2] | 92.7 [85.3, 98.2] | +29.4 [+18.4, +41.3] | < 0.0001 |
| `min_k_shown` | 109 | ESCO precision (%) | 20.9 [14.7, 29.5] | 13.8 [9.6, 19.1] | -7.1 [-12.5, -3.3] | < 0.0001 |
| `min_k_shown` | 109 | ESCO recall (%) | 48.1 [37.1, 59.6] | 51.9 [40.1, 64.2] | +3.8 [-1.7, +10.4] | 0.2454 |
| `min_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 17 [13, 19] | 18 [13, 20] | +1 [-2, +4] | 1.0000 |
| `min_k_shown_fewer_ok` | 109 | False ESCO concepts per ad | 2.22 [1.56, 2.93] | 3.40 [2.87, 3.95] | +1.18 [+0.50, +1.90] | 0.0016 |
| `min_k_shown_fewer_ok` | 109 | Ads with at least one false concept (%) | 63.3 [50.5, 75.2] | 93.6 [86.4, 99.1] | +30.3 [+19.3, +42.3] | < 0.0001 |
| `min_k_shown_fewer_ok` | 109 | ESCO precision (%) | 20.9 [14.7, 29.5] | 15.7 [10.8, 21.6] | -5.2 [-11.2, -0.9] | 0.0160 |
| `min_k_shown_fewer_ok` | 109 | ESCO recall (%) | 48.1 [37.1, 59.6] | 51.9 [40.2, 64.1] | +3.8 [-3.0, +11.1] | 0.3362 |
| `min_k_shown_fewer_ok` | 109 | Top-20 concepts not in the true items' top 20 | 17 [13, 19] | 19 [13, 20] | +2 [-3, +4] | 1.0000 |
| `min_k_enforced` | 109 | False ESCO concepts per ad | 2.22 [1.56, 2.93] | 3.72 [3.26, 4.22] | +1.50 [+0.78, +2.23] | 0.0006 |
| `min_k_enforced` | 109 | Ads with at least one false concept (%) | 63.3 [50.5, 75.2] | 98.2 [95.3, 100.0] | +34.9 [+23.1, +47.2] | < 0.0001 |
| `min_k_enforced` | 109 | ESCO precision (%) | 20.9 [14.7, 29.5] | 14.2 [9.9, 19.0] | -6.8 [-12.8, -2.6] | 0.0016 |
| `min_k_enforced` | 109 | ESCO recall (%) | 48.1 [37.1, 59.6] | 50.4 [38.7, 62.3] | +2.3 [-4.3, +9.3] | 0.5866 |
| `min_k_enforced` | 109 | Top-20 concepts not in the true items' top 20 | 17 [13, 19] | 19 [14, 20] | +2 [-2, +4] | 0.9790 |
| `min_k_escape` | 109 | False ESCO concepts per ad | 2.22 [1.56, 2.93] | 2.50 [1.94, 3.09] | +0.28 [-0.44, +0.96] | 0.4462 |
| `min_k_escape` | 109 | Ads with at least one false concept (%) | 63.3 [50.5, 75.2] | 72.5 [62.0, 82.6] | +9.2 [+0.0, +19.1] | 0.0668 |
| `min_k_escape` | 109 | ESCO precision (%) | 20.9 [14.7, 29.5] | 19.3 [13.4, 26.5] | -1.6 [-7.4, +3.4] | 0.5316 |
| `min_k_escape` | 109 | ESCO recall (%) | 48.1 [37.1, 59.6] | 48.9 [37.8, 60.3] | +0.8 [-5.5, +7.5] | 0.9148 |
| `min_k_escape` | 109 | Top-20 concepts not in the true items' top 20 | 17 [13, 19] | 18 [12, 19] | +1 [-4, +2] | 0.7478 |

## 45. Grok 4.3 (Bedrock), job-ad knowledge, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 102 | False ESCO concepts per ad | 0.19 [0.08, 0.31] | 0.34 [0.17, 0.56] | +0.16 [-0.01, +0.37] | 0.0878 |
| `prose_up_to_k` | 102 | Ads with at least one false concept (%) | 15.7 [6.8, 25.8] | 22.5 [12.9, 33.0] | +6.9 [-2.0, +16.7] | 0.1744 |
| `prose_up_to_k` | 102 | ESCO precision (%) | 80.2 [68.1, 90.9] | 72.2 [58.7, 85.1] | -8.0 [-22.3, +4.6] | 0.2466 |
| `prose_up_to_k` | 102 | ESCO recall (%) | 63.1 [49.6, 75.5] | 74.6 [64.1, 84.2] | +11.5 [+1.5, +22.8] | 0.0298 |
| `prose_up_to_k` | 102 | Top-20 concepts not in the true items' top 20 | 8 [4, 11] | 8 [4, 11] | +0 [-4, +4] | 1.0000 |
| `prose_exactly_k` | 102 | False ESCO concepts per ad | 0.19 [0.08, 0.31] | 1.29 [0.97, 1.62] | +1.11 [+0.78, +1.44] | < 0.0001 |
| `prose_exactly_k` | 102 | Ads with at least one false concept (%) | 15.7 [6.8, 25.8] | 53.9 [42.0, 65.7] | +38.2 [+25.3, +50.5] | < 0.0001 |
| `prose_exactly_k` | 102 | ESCO precision (%) | 80.2 [68.1, 90.9] | 44.1 [36.3, 52.7] | -36.1 [-48.1, -24.1] | < 0.0001 |
| `prose_exactly_k` | 102 | ESCO recall (%) | 63.1 [49.6, 75.5] | 85.2 [78.0, 92.2] | +22.1 [+10.5, +35.3] | < 0.0001 |
| `prose_exactly_k` | 102 | Top-20 concepts not in the true items' top 20 | 8 [4, 11] | 10 [7, 14] | +2 [-1, +7] | 0.2478 |
| `max_k_shown` | 102 | False ESCO concepts per ad | 0.19 [0.08, 0.31] | 0.16 [0.07, 0.27] | -0.03 [-0.11, +0.05] | 0.5618 |
| `max_k_shown` | 102 | Ads with at least one false concept (%) | 15.7 [6.8, 25.8] | 12.7 [5.9, 20.6] | -2.9 [-10.2, +3.8] | 0.5138 |
| `max_k_shown` | 102 | ESCO precision (%) | 80.2 [68.1, 90.9] | 84.0 [73.6, 92.6] | +3.8 [-3.9, +11.8] | 0.3388 |
| `max_k_shown` | 102 | ESCO recall (%) | 63.1 [49.6, 75.5] | 68.9 [56.1, 80.2] | +5.7 [-1.5, +14.3] | 0.1680 |
| `max_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 8 [4, 11] | 8 [4, 10] | +0 [-3, +1] | 1.0000 |
| `min_k_shown` | 102 | False ESCO concepts per ad | 0.19 [0.08, 0.31] | 2.73 [1.65, 3.99] | +2.54 [+1.46, +3.81] | < 0.0001 |
| `min_k_shown` | 102 | Ads with at least one false concept (%) | 15.7 [6.8, 25.8] | 58.8 [46.7, 70.5] | +43.1 [+30.9, +55.4] | < 0.0001 |
| `min_k_shown` | 102 | ESCO precision (%) | 80.2 [68.1, 90.9] | 26.8 [18.5, 39.7] | -53.4 [-65.6, -39.3] | < 0.0001 |
| `min_k_shown` | 102 | ESCO recall (%) | 63.1 [49.6, 75.5] | 83.6 [75.9, 90.9] | +20.5 [+9.0, +33.3] | 0.0004 |
| `min_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 8 [4, 11] | 14 [9, 18] | +6 [+2, +12] | 0.0200 |
| `min_k_shown_fewer_ok` | 102 | False ESCO concepts per ad | 0.19 [0.08, 0.31] | 1.34 [0.82, 1.91] | +1.16 [+0.64, +1.73] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | Ads with at least one false concept (%) | 15.7 [6.8, 25.8] | 36.3 [25.7, 47.4] | +20.6 [+10.8, +31.1] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | ESCO precision (%) | 80.2 [68.1, 90.9] | 39.4 [29.2, 52.6] | -40.8 [-53.9, -26.8] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | ESCO recall (%) | 63.1 [49.6, 75.5] | 73.0 [61.5, 83.2] | +9.8 [+0.0, +21.0] | 0.0540 |
| `min_k_shown_fewer_ok` | 102 | Top-20 concepts not in the true items' top 20 | 8 [4, 11] | 11 [6, 15] | +3 [-1, +8] | 0.2618 |
| `min_k_enforced` | 102 | False ESCO concepts per ad | 0.19 [0.08, 0.31] | 4.00 [3.26, 4.90] | +3.81 [+3.07, +4.73] | < 0.0001 |
| `min_k_enforced` | 102 | Ads with at least one false concept (%) | 15.7 [6.8, 25.8] | 98.0 [95.1, 100.0] | +82.4 [+72.2, +91.3] | < 0.0001 |
| `min_k_enforced` | 102 | ESCO precision (%) | 80.2 [68.1, 90.9] | 21.4 [16.1, 27.6] | -58.8 [-70.1, -47.4] | < 0.0001 |
| `min_k_enforced` | 102 | ESCO recall (%) | 63.1 [49.6, 75.5] | 91.0 [84.0, 96.9] | +27.9 [+14.8, +42.2] | < 0.0001 |
| `min_k_enforced` | 102 | Top-20 concepts not in the true items' top 20 | 8 [4, 11] | 16 [11, 18] | +8 [+3, +12] | 0.0030 |
| `min_k_escape` | 102 | False ESCO concepts per ad | 0.19 [0.08, 0.31] | 0.35 [0.13, 0.62] | +0.17 [-0.08, +0.46] | 0.2372 |
| `min_k_escape` | 102 | Ads with at least one false concept (%) | 15.7 [6.8, 25.8] | 15.7 [7.1, 25.3] | +0.0 [-11.5, +11.5] | 1.0000 |
| `min_k_escape` | 102 | ESCO precision (%) | 80.2 [68.1, 90.9] | 55.0 [41.3, 73.3] | -25.2 [-41.8, -3.9] | 0.0212 |
| `min_k_escape` | 102 | ESCO recall (%) | 63.1 [49.6, 75.5] | 36.1 [22.1, 50.5] | -27.0 [-41.5, -13.0] | 0.0002 |
| `min_k_escape` | 102 | Top-20 concepts not in the true items' top 20 | 8 [4, 11] | 10 [8, 15] | +2 [+0, +8] | 0.0988 |

## 46. Kimi K3 (Bedrock), both sets, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 0.95 [0.69, 1.21] | 1.03 [0.84, 1.22] | +0.08 [-0.07, +0.24] | 0.2974 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 39.8 [31.4, 48.3] | 47.7 [40.2, 55.1] | +7.9 [+3.5, +12.6] | 0.0008 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 47.2 [39.5, 56.1] | 45.6 [38.9, 52.7] | -1.6 [-6.7, +2.4] | 0.4484 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 70.2 [63.4, 77.1] | 71.5 [64.7, 78.1] | +1.3 [-2.3, +4.9] | 0.5220 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 12 [7, 15] | 10 [6, 14] | -2 [-4, +1] | 0.5492 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 0.95 [0.69, 1.21] | 1.88 [1.68, 2.07] | +0.93 [+0.71, +1.16] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 39.8 [31.4, 48.3] | 72.1 [65.6, 78.4] | +32.3 [+25.3, +39.6] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 47.2 [39.5, 56.1] | 32.2 [27.7, 36.9] | -15.0 [-21.9, -9.6] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 70.2 [63.4, 77.1] | 73.7 [67.1, 80.2] | +3.5 [+0.1, +7.2] | 0.0428 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 12 [7, 15] | 12 [8, 15] | +0 [-2, +4] | 0.9920 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 0.95 [0.69, 1.21] | 0.93 [0.72, 1.15] | -0.01 [-0.15, +0.12] | 0.8632 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 39.8 [31.4, 48.3] | 46.4 [37.5, 55.4] | +6.6 [+2.6, +11.4] | 0.0010 |
| `max_k_shown` | 211 | ESCO precision (%) | 47.2 [39.5, 56.1] | 48.0 [40.8, 56.2] | +0.8 [-3.2, +4.3] | 0.6886 |
| `max_k_shown` | 211 | ESCO recall (%) | 70.2 [63.4, 77.1] | 71.4 [64.2, 78.2] | +1.2 [-2.1, +4.4] | 0.5406 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 12 [7, 15] | 12 [7, 14] | +0 [-3, +2] | 1.0000 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 0.95 [0.69, 1.21] | 2.98 [2.62, 3.36] | +2.03 [+1.67, +2.43] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 39.8 [31.4, 48.3] | 86.3 [80.0, 91.8] | +46.4 [+37.7, +55.2] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 47.2 [39.5, 56.1] | 23.1 [19.0, 27.6] | -24.1 [-31.8, -17.9] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 70.2 [63.4, 77.1] | 74.1 [67.8, 80.4] | +3.9 [-0.4, +8.2] | 0.0830 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 12 [7, 15] | 11 [10, 17] | -1 [-1, +7] | 0.2776 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 0.95 [0.69, 1.21] | 1.44 [1.14, 1.75] | +0.49 [+0.29, +0.72] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 39.8 [31.4, 48.3] | 56.4 [47.2, 65.2] | +16.6 [+9.8, +23.9] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 47.2 [39.5, 56.1] | 37.6 [30.9, 45.2] | -9.7 [-15.2, -5.1] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 70.2 [63.4, 77.1] | 71.8 [64.9, 78.7] | +1.6 [-2.2, +5.5] | 0.4972 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 12 [7, 15] | 12 [9, 16] | +0 [-1, +5] | 0.6744 |

Top 20 concepts of the `min_k_shown` outputs: English; cooperate with colleagues; computer engineering; perform scientific research; Agile development; implement front-end website design; DevOps; German; apply knowledge of science, technology and engineering; automation technology; communication; Java (computer programming); work in shifts; monitor technology trends; computer science; process applications; communicate analytical insights; SAP Data Services; continuous improvement philosophies; design cloud architecture

Top 20 concepts of the true items of the same ads: English; teach communication methods; SAP Data Services; German; computer engineering; recruit members; design cloud architecture; Danish; perform scientific research; computer science; react to events in time-critical environments; web services; perform business research; systems development life-cycle; Ruby (computer programming); solve technical problems; communication; Java (computer programming); body language; manage budgets

## 47. Kimi K3 (Bedrock), job-ad skills, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 109 | False ESCO concepts per ad | 1.50 [1.07, 1.95] | 1.55 [1.24, 1.86] | +0.06 [-0.19, +0.29] | 0.6576 |
| `prose_up_to_k` | 109 | Ads with at least one false concept (%) | 58.7 [46.2, 70.9] | 67.9 [57.1, 78.2] | +9.2 [+4.0, +15.1] | < 0.0001 |
| `prose_up_to_k` | 109 | ESCO precision (%) | 30.6 [22.2, 41.0] | 29.8 [21.7, 38.8] | -0.8 [-5.5, +3.0] | 0.6856 |
| `prose_up_to_k` | 109 | ESCO recall (%) | 54.1 [43.7, 64.7] | 54.0 [43.2, 65.2] | -0.2 [-5.4, +5.2] | 0.9648 |
| `prose_up_to_k` | 109 | Top-20 concepts not in the true items' top 20 | 17 [10, 18] | 16 [9, 17] | -1 [-4, +2] | 0.8858 |
| `prose_exactly_k` | 109 | False ESCO concepts per ad | 1.50 [1.07, 1.95] | 2.37 [2.09, 2.63] | +0.87 [+0.54, +1.19] | < 0.0001 |
| `prose_exactly_k` | 109 | Ads with at least one false concept (%) | 58.7 [46.2, 70.9] | 85.0 [78.4, 90.9] | +26.2 [+17.6, +35.5] | < 0.0001 |
| `prose_exactly_k` | 109 | ESCO precision (%) | 30.6 [22.2, 41.0] | 23.0 [17.2, 29.2] | -7.7 [-14.2, -3.0] | 0.0002 |
| `prose_exactly_k` | 109 | ESCO recall (%) | 54.1 [43.7, 64.7] | 57.7 [47.3, 68.5] | +3.6 [-1.3, +8.8] | 0.1696 |
| `prose_exactly_k` | 109 | Top-20 concepts not in the true items' top 20 | 17 [10, 18] | 17 [11, 18] | +0 [-2, +3] | 1.0000 |
| `max_k_shown` | 109 | False ESCO concepts per ad | 1.50 [1.07, 1.95] | 1.31 [0.97, 1.65] | -0.18 [-0.37, -0.02] | 0.0258 |
| `max_k_shown` | 109 | Ads with at least one false concept (%) | 58.7 [46.2, 70.9] | 61.5 [49.1, 73.4] | +2.8 [+0.0, +7.4] | 0.2670 |
| `max_k_shown` | 109 | ESCO precision (%) | 30.6 [22.2, 41.0] | 34.1 [25.2, 44.4] | +3.5 [-0.0, +6.9] | 0.0544 |
| `max_k_shown` | 109 | ESCO recall (%) | 54.1 [43.7, 64.7] | 55.6 [44.4, 66.9] | +1.5 [-4.2, +6.9] | 0.6854 |
| `max_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 17 [10, 18] | 16 [10, 18] | -1 [-3, +2] | 1.0000 |
| `min_k_shown` | 109 | False ESCO concepts per ad | 1.50 [1.07, 1.95] | 3.26 [2.75, 3.79] | +1.76 [+1.26, +2.33] | < 0.0001 |
| `min_k_shown` | 109 | Ads with at least one false concept (%) | 58.7 [46.2, 70.9] | 93.6 [87.0, 98.3] | +34.9 [+23.4, +46.8] | < 0.0001 |
| `min_k_shown` | 109 | ESCO precision (%) | 30.6 [22.2, 41.0] | 18.4 [13.3, 24.5] | -12.2 [-19.8, -6.8] | < 0.0001 |
| `min_k_shown` | 109 | ESCO recall (%) | 54.1 [43.7, 64.7] | 60.2 [50.4, 70.2] | +6.0 [+1.5, +10.9] | 0.0128 |
| `min_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 17 [10, 18] | 17 [13, 19] | +0 [-1, +6] | 0.4490 |
| `min_k_shown_fewer_ok` | 109 | False ESCO concepts per ad | 1.50 [1.07, 1.95] | 1.71 [1.27, 2.17] | +0.21 [+0.00, +0.46] | 0.0594 |
| `min_k_shown_fewer_ok` | 109 | Ads with at least one false concept (%) | 58.7 [46.2, 70.9] | 65.1 [53.2, 76.8] | +6.4 [+0.9, +13.6] | 0.0302 |
| `min_k_shown_fewer_ok` | 109 | ESCO precision (%) | 30.6 [22.2, 41.0] | 27.3 [19.2, 37.1] | -3.3 [-8.1, +0.4] | 0.0874 |
| `min_k_shown_fewer_ok` | 109 | ESCO recall (%) | 54.1 [43.7, 64.7] | 52.6 [41.7, 64.1] | -1.5 [-7.1, +3.2] | 0.7008 |
| `min_k_shown_fewer_ok` | 109 | Top-20 concepts not in the true items' top 20 | 17 [10, 18] | 17 [11, 18] | +0 [-2, +3] | 1.0000 |

## 48. Kimi K3 (Bedrock), job-ad knowledge, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 102 | False ESCO concepts per ad | 0.36 [0.17, 0.60] | 0.47 [0.28, 0.68] | +0.11 [-0.09, +0.32] | 0.2806 |
| `prose_up_to_k` | 102 | Ads with at least one false concept (%) | 19.6 [9.7, 30.6] | 26.1 [16.4, 36.5] | +6.5 [-0.6, +14.0] | 0.0748 |
| `prose_up_to_k` | 102 | ESCO precision (%) | 74.3 [63.3, 86.3] | 69.6 [59.5, 79.9] | -4.7 [-16.0, +4.7] | 0.3476 |
| `prose_up_to_k` | 102 | ESCO recall (%) | 87.7 [79.6, 94.7] | 90.5 [84.9, 95.3] | +2.8 [-1.8, +8.2] | 0.2816 |
| `prose_up_to_k` | 102 | Top-20 concepts not in the true items' top 20 | 7 [3, 10] | 5 [2, 9] | -2 [-4, +3] | 0.8966 |
| `prose_exactly_k` | 102 | False ESCO concepts per ad | 0.36 [0.17, 0.60] | 1.36 [1.07, 1.64] | +0.99 [+0.70, +1.30] | < 0.0001 |
| `prose_exactly_k` | 102 | Ads with at least one false concept (%) | 19.6 [9.7, 30.6] | 58.4 [47.3, 69.3] | +38.8 [+28.2, +50.2] | < 0.0001 |
| `prose_exactly_k` | 102 | ESCO precision (%) | 74.3 [63.3, 86.3] | 44.6 [37.4, 51.8] | -29.8 [-41.9, -19.5] | < 0.0001 |
| `prose_exactly_k` | 102 | ESCO recall (%) | 87.7 [79.6, 94.7] | 91.1 [85.4, 96.0] | +3.4 [-1.2, +9.1] | 0.1764 |
| `prose_exactly_k` | 102 | Top-20 concepts not in the true items' top 20 | 7 [3, 10] | 8 [5, 12] | +1 [-2, +7] | 0.3356 |
| `max_k_shown` | 102 | False ESCO concepts per ad | 0.36 [0.17, 0.60] | 0.53 [0.31, 0.77] | +0.17 [-0.03, +0.39] | 0.1072 |
| `max_k_shown` | 102 | Ads with at least one false concept (%) | 19.6 [9.7, 30.6] | 30.4 [18.4, 43.0] | +10.8 [+3.0, +19.8] | 0.0044 |
| `max_k_shown` | 102 | ESCO precision (%) | 74.3 [63.3, 86.3] | 66.7 [56.3, 78.3] | -7.6 [-18.5, +1.6] | 0.1112 |
| `max_k_shown` | 102 | ESCO recall (%) | 87.7 [79.6, 94.7] | 88.5 [81.2, 94.8] | +0.8 [-1.8, +3.8] | 0.7854 |
| `max_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 7 [3, 10] | 8 [3, 11] | +1 [-2, +4] | 0.8334 |
| `min_k_shown` | 102 | False ESCO concepts per ad | 0.36 [0.17, 0.60] | 2.68 [2.15, 3.24] | +2.31 [+1.77, +2.90] | < 0.0001 |
| `min_k_shown` | 102 | Ads with at least one false concept (%) | 19.6 [9.7, 30.6] | 78.4 [67.7, 88.5] | +58.8 [+46.0, +71.6] | < 0.0001 |
| `min_k_shown` | 102 | ESCO precision (%) | 74.3 [63.3, 86.3] | 28.5 [21.8, 36.3] | -45.8 [-58.4, -34.7] | < 0.0001 |
| `min_k_shown` | 102 | ESCO recall (%) | 87.7 [79.6, 94.7] | 89.3 [81.9, 95.8] | +1.6 [-5.4, +9.1] | 0.8266 |
| `min_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 7 [3, 10] | 12 [9, 17] | +5 [+2, +12] | 0.0050 |
| `min_k_shown_fewer_ok` | 102 | False ESCO concepts per ad | 0.36 [0.17, 0.60] | 1.16 [0.77, 1.57] | +0.79 [+0.41, +1.21] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | Ads with at least one false concept (%) | 19.6 [9.7, 30.6] | 47.1 [34.3, 60.2] | +27.5 [+14.8, +40.4] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | ESCO precision (%) | 74.3 [63.3, 86.3] | 48.9 [38.2, 61.1] | -25.4 [-39.2, -13.2] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | ESCO recall (%) | 87.7 [79.6, 94.7] | 92.6 [87.1, 97.4] | +4.9 [+0.0, +11.7] | 0.1000 |
| `min_k_shown_fewer_ok` | 102 | Top-20 concepts not in the true items' top 20 | 7 [3, 10] | 10 [6, 15] | +3 [+0, +9] | 0.1002 |

## 49. Ministral 3 14B (Bedrock), both sets, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 4.49 [3.63, 5.42] | 2.42 [2.18, 2.67] | -2.07 [-2.86, -1.35] | < 0.0001 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 80.6 [73.5, 87.2] | 83.6 [78.6, 88.3] | +3.0 [-2.1, +8.6] | 0.2742 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 14.6 [11.5, 18.5] | 22.4 [18.5, 26.6] | +7.8 [+5.3, +10.3] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 63.5 [56.0, 71.0] | 58.0 [50.9, 64.9] | -5.6 [-10.9, -0.1] | 0.0500 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 17 [11, 17] | +1 [-6, +1] | 0.2874 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 4.49 [3.63, 5.42] | 2.62 [2.40, 2.84] | -1.87 [-2.66, -1.13] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 80.6 [73.5, 87.2] | 87.1 [82.5, 91.4] | +6.5 [+1.8, +11.6] | 0.0048 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 14.6 [11.5, 18.5] | 21.8 [18.2, 25.6] | +7.2 [+4.5, +9.4] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 63.5 [56.0, 71.0] | 60.2 [53.6, 67.1] | -3.3 [-8.7, +2.0] | 0.2270 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 15 [11, 17] | -1 [-5, +1] | 0.3482 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 4.49 [3.63, 5.42] | 2.09 [1.72, 2.49] | -2.40 [-3.17, -1.71] | < 0.0001 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 80.6 [73.5, 87.2] | 68.7 [61.1, 76.1] | -11.8 [-17.9, -6.4] | < 0.0001 |
| `max_k_shown` | 211 | ESCO precision (%) | 14.6 [11.5, 18.5] | 26.4 [21.5, 32.0] | +11.8 [+8.7, +15.3] | < 0.0001 |
| `max_k_shown` | 211 | ESCO recall (%) | 63.5 [56.0, 71.0] | 62.0 [54.2, 69.8] | -1.6 [-6.0, +2.6] | 0.5308 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 18 [11, 18] | +2 [-5, +1] | 0.4920 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 4.49 [3.63, 5.42] | 4.86 [4.22, 5.55] | +0.37 [-0.19, +0.90] | 0.1910 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 80.6 [73.5, 87.2] | 89.6 [84.4, 94.4] | +9.0 [+3.9, +14.5] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 14.6 [11.5, 18.5] | 13.6 [10.9, 16.6] | -1.0 [-2.9, +0.4] | 0.1830 |
| `min_k_shown` | 211 | ESCO recall (%) | 63.5 [56.0, 71.0] | 63.1 [55.7, 70.5] | -0.4 [-4.6, +4.4] | 0.8872 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 16 [13, 19] | +0 [-3, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 4.49 [3.63, 5.42] | 0.66 [0.46, 0.90] | -3.83 [-4.72, -3.00] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 80.6 [73.5, 87.2] | 32.7 [24.3, 41.6] | -47.9 [-56.9, -38.7] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 14.6 [11.5, 18.5] | 45.9 [37.6, 55.6] | +31.4 [+24.0, +39.8] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 63.5 [56.0, 71.0] | 46.7 [38.0, 55.4] | -16.9 [-24.8, -9.4] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 13 [8, 15] | -3 [-9, -1] | 0.0306 |

Top 20 concepts of the `min_k_shown` outputs: English; cooperate with colleagues; industrial research and development; build team spirit; Agile development; design thinking; seek innovation in current practices; continuous improvement philosophies; work in shifts; computer engineering; think creatively; team building; DevOps; work in an international environment; systems development life-cycle; maintain psychological well-being; perform scientific research; web programming; international business; engage with stakeholders

Top 20 concepts of the true items of the same ads: English; teach communication methods; SAP Data Services; German; computer engineering; recruit members; design cloud architecture; Danish; perform scientific research; computer science; react to events in time-critical environments; web services; perform business research; systems development life-cycle; Ruby (computer programming); solve technical problems; communication; Java (computer programming); body language; manage budgets

## 50. Ministral 3 14B (Bedrock), job-ad skills, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 109 | False ESCO concepts per ad | 3.46 [2.73, 4.27] | 2.88 [2.60, 3.16] | -0.58 [-1.25, +0.02] | 0.0588 |
| `prose_up_to_k` | 109 | Ads with at least one false concept (%) | 89.0 [80.6, 96.3] | 96.1 [92.7, 98.9] | +7.2 [+0.5, +14.9] | 0.0326 |
| `prose_up_to_k` | 109 | ESCO precision (%) | 15.1 [10.5, 20.7] | 15.2 [10.8, 20.0] | +0.1 [-3.5, +2.9] | 0.9602 |
| `prose_up_to_k` | 109 | ESCO recall (%) | 50.4 [39.7, 61.6] | 42.1 [32.8, 51.8] | -8.3 [-17.4, -0.7] | 0.0310 |
| `prose_up_to_k` | 109 | Top-20 concepts not in the true items' top 20 | 19 [14, 19] | 18 [12, 18] | -1 [-4, +2] | 0.5716 |
| `prose_exactly_k` | 109 | False ESCO concepts per ad | 3.46 [2.73, 4.27] | 3.04 [2.82, 3.26] | -0.42 [-1.11, +0.19] | 0.2020 |
| `prose_exactly_k` | 109 | Ads with at least one false concept (%) | 89.0 [80.6, 96.3] | 96.5 [94.2, 98.4] | +7.5 [+1.5, +14.4] | 0.0090 |
| `prose_exactly_k` | 109 | ESCO precision (%) | 15.1 [10.5, 20.7] | 15.8 [11.6, 20.4] | +0.7 [-2.6, +3.3] | 0.6430 |
| `prose_exactly_k` | 109 | ESCO recall (%) | 50.4 [39.7, 61.6] | 46.8 [37.6, 56.0] | -3.6 [-12.6, +3.9] | 0.4010 |
| `prose_exactly_k` | 109 | Top-20 concepts not in the true items' top 20 | 19 [14, 19] | 17 [12, 18] | -2 [-4, +2] | 0.5732 |
| `max_k_shown` | 109 | False ESCO concepts per ad | 3.46 [2.73, 4.27] | 2.66 [2.12, 3.28] | -0.80 [-1.18, -0.46] | < 0.0001 |
| `max_k_shown` | 109 | Ads with at least one false concept (%) | 89.0 [80.6, 96.3] | 86.2 [77.2, 93.8] | -2.8 [-6.5, +0.0] | 0.0916 |
| `max_k_shown` | 109 | ESCO precision (%) | 15.1 [10.5, 20.7] | 18.8 [13.2, 25.5] | +3.7 [+2.0, +5.9] | < 0.0001 |
| `max_k_shown` | 109 | ESCO recall (%) | 50.4 [39.7, 61.6] | 50.4 [39.5, 61.8] | +0.0 [-2.9, +2.9] | 1.0000 |
| `max_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 19 [14, 19] | 18 [12, 19] | -1 [-4, +1] | 0.7458 |
| `min_k_shown` | 109 | False ESCO concepts per ad | 3.46 [2.73, 4.27] | 4.28 [3.62, 5.04] | +0.83 [+0.38, +1.24] | 0.0004 |
| `min_k_shown` | 109 | Ads with at least one false concept (%) | 89.0 [80.6, 96.3] | 94.5 [88.5, 99.1] | +5.5 [+0.9, +10.9] | 0.0110 |
| `min_k_shown` | 109 | ESCO precision (%) | 15.1 [10.5, 20.7] | 12.2 [8.6, 16.6] | -2.9 [-5.2, -1.2] | 0.0004 |
| `min_k_shown` | 109 | ESCO recall (%) | 50.4 [39.7, 61.6] | 48.9 [38.7, 59.5] | -1.5 [-5.6, +2.7] | 0.5852 |
| `min_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 19 [14, 19] | 18 [14, 19] | -1 [-2, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 109 | False ESCO concepts per ad | 3.46 [2.73, 4.27] | 0.78 [0.48, 1.11] | -2.68 [-3.54, -1.93] | < 0.0001 |
| `min_k_shown_fewer_ok` | 109 | Ads with at least one false concept (%) | 89.0 [80.6, 96.3] | 35.8 [23.8, 47.8] | -53.2 [-65.8, -40.7] | < 0.0001 |
| `min_k_shown_fewer_ok` | 109 | ESCO precision (%) | 15.1 [10.5, 20.7] | 29.2 [18.1, 42.6] | +14.1 [+5.1, +25.4] | 0.0010 |
| `min_k_shown_fewer_ok` | 109 | ESCO recall (%) | 50.4 [39.7, 61.6] | 26.3 [15.7, 37.5] | -24.1 [-34.9, -14.3] | < 0.0001 |
| `min_k_shown_fewer_ok` | 109 | Top-20 concepts not in the true items' top 20 | 19 [14, 19] | 14 [11, 18] | -5 [-6, +2] | 0.4210 |

## 51. Ministral 3 14B (Bedrock), job-ad knowledge, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 102 | False ESCO concepts per ad | 5.60 [4.03, 7.30] | 1.94 [1.52, 2.37] | -3.66 [-5.10, -2.39] | < 0.0001 |
| `prose_up_to_k` | 102 | Ads with at least one false concept (%) | 71.6 [59.3, 83.0] | 70.2 [60.0, 79.6] | -1.4 [-9.1, +6.6] | 0.7570 |
| `prose_up_to_k` | 102 | ESCO precision (%) | 14.3 [10.2, 20.0] | 31.7 [24.3, 40.3] | +17.5 [+12.8, +22.6] | < 0.0001 |
| `prose_up_to_k` | 102 | ESCO recall (%) | 77.9 [68.3, 87.2] | 75.2 [66.1, 84.3] | -2.6 [-10.8, +6.9] | 0.5450 |
| `prose_up_to_k` | 102 | Top-20 concepts not in the true items' top 20 | 16 [14, 19] | 12 [7, 15] | -4 [-10, -2] | 0.0054 |
| `prose_exactly_k` | 102 | False ESCO concepts per ad | 5.60 [4.03, 7.30] | 2.17 [1.78, 2.54] | -3.43 [-4.86, -2.12] | < 0.0001 |
| `prose_exactly_k` | 102 | Ads with at least one false concept (%) | 71.6 [59.3, 83.0] | 77.1 [67.8, 85.5] | +5.5 [-1.9, +13.4] | 0.1476 |
| `prose_exactly_k` | 102 | ESCO precision (%) | 14.3 [10.2, 20.0] | 29.2 [22.9, 36.3] | +15.0 [+11.0, +18.9] | < 0.0001 |
| `prose_exactly_k` | 102 | ESCO recall (%) | 77.9 [68.3, 87.2] | 74.9 [66.5, 83.4] | -3.0 [-8.9, +4.2] | 0.3888 |
| `prose_exactly_k` | 102 | Top-20 concepts not in the true items' top 20 | 16 [14, 19] | 14 [8, 16] | -2 [-9, -1] | 0.0174 |
| `max_k_shown` | 102 | False ESCO concepts per ad | 5.60 [4.03, 7.30] | 1.48 [0.99, 2.02] | -4.12 [-5.68, -2.76] | < 0.0001 |
| `max_k_shown` | 102 | Ads with at least one false concept (%) | 71.6 [59.3, 83.0] | 50.0 [36.7, 63.0] | -21.6 [-32.7, -11.2] | < 0.0001 |
| `max_k_shown` | 102 | ESCO precision (%) | 14.3 [10.2, 20.0] | 37.6 [28.8, 48.7] | +23.3 [+16.6, +32.0] | < 0.0001 |
| `max_k_shown` | 102 | ESCO recall (%) | 77.9 [68.3, 87.2] | 74.6 [64.3, 84.5] | -3.3 [-11.4, +4.2] | 0.4924 |
| `max_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 16 [14, 19] | 13 [8, 15] | -3 [-9, -1] | 0.0116 |
| `min_k_shown` | 102 | False ESCO concepts per ad | 5.60 [4.03, 7.30] | 5.48 [4.36, 6.65] | -0.12 [-1.18, +0.88] | 0.8552 |
| `min_k_shown` | 102 | Ads with at least one false concept (%) | 71.6 [59.3, 83.0] | 84.3 [74.5, 92.9] | +12.7 [+3.9, +22.7] | 0.0042 |
| `min_k_shown` | 102 | ESCO precision (%) | 14.3 [10.2, 20.0] | 14.7 [10.9, 19.2] | +0.4 [-2.3, +2.5] | 0.7772 |
| `min_k_shown` | 102 | ESCO recall (%) | 77.9 [68.3, 87.2] | 78.7 [69.6, 87.4] | +0.8 [-6.9, +9.7] | 0.9742 |
| `min_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 16 [14, 19] | 16 [13, 19] | +0 [-3, +1] | 0.9352 |
| `min_k_shown_fewer_ok` | 102 | False ESCO concepts per ad | 5.60 [4.03, 7.30] | 0.54 [0.27, 0.88] | -5.06 [-6.69, -3.58] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | Ads with at least one false concept (%) | 71.6 [59.3, 83.0] | 29.4 [18.2, 41.2] | -42.2 [-54.9, -29.5] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | ESCO precision (%) | 14.3 [10.2, 20.0] | 60.4 [47.9, 75.2] | +46.2 [+35.4, +59.2] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | ESCO recall (%) | 77.9 [68.3, 87.2] | 68.9 [55.3, 81.8] | -9.0 [-20.5, +1.7] | 0.1282 |
| `min_k_shown_fewer_ok` | 102 | Top-20 concepts not in the true items' top 20 | 16 [14, 19] | 10 [5, 12] | -6 [-12, -4] | < 0.0001 |

## 52. Mistral Large 3 (Bedrock), both sets, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 1.88 [1.41, 2.41] | 1.80 [1.58, 2.01] | -0.08 [-0.48, +0.27] | 0.6792 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 53.6 [44.6, 62.5] | 67.5 [61.1, 73.7] | +13.9 [+8.2, +20.3] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 29.4 [22.9, 37.5] | 30.5 [25.6, 35.5] | +1.1 [-4.1, +5.2] | 0.6746 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 64.7 [57.0, 72.6] | 65.2 [58.7, 71.6] | +0.5 [-5.4, +6.4] | 0.9008 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 18] | 16 [9, 16] | +1 [-5, +2] | 0.6120 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 1.88 [1.41, 2.41] | 2.23 [2.03, 2.43] | +0.35 [-0.07, +0.73] | 0.0976 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 53.6 [44.6, 62.5] | 76.6 [71.2, 81.8] | +23.0 [+16.6, +30.0] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 29.4 [22.9, 37.5] | 26.5 [22.4, 30.7] | -2.9 [-8.6, +1.5] | 0.2130 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 64.7 [57.0, 72.6] | 66.5 [60.6, 72.2] | +1.8 [-3.9, +7.7] | 0.5676 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 18] | 17 [10, 16] | +2 [-4, +2] | 0.7826 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 1.88 [1.41, 2.41] | 1.54 [1.27, 1.82] | -0.35 [-0.69, -0.04] | 0.0240 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 53.6 [44.6, 62.5] | 60.2 [52.1, 68.1] | +6.6 [+0.9, +12.8] | 0.0248 |
| `max_k_shown` | 211 | ESCO precision (%) | 29.4 [22.9, 37.5] | 32.9 [26.8, 39.4] | +3.6 [-0.6, +7.3] | 0.0938 |
| `max_k_shown` | 211 | ESCO recall (%) | 64.7 [57.0, 72.6] | 62.4 [55.1, 69.2] | -2.4 [-8.5, +3.7] | 0.4754 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 18] | 14 [10, 16] | -1 [-4, +2] | 0.7616 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 1.88 [1.41, 2.41] | 3.49 [3.06, 3.97] | +1.61 [+1.14, +2.11] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 53.6 [44.6, 62.5] | 86.7 [81.7, 91.5] | +33.2 [+24.5, +42.1] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 29.4 [22.9, 37.5] | 18.7 [14.9, 22.8] | -10.7 [-16.9, -5.9] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 64.7 [57.0, 72.6] | 66.3 [59.3, 73.3] | +1.6 [-4.3, +7.6] | 0.6790 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 18] | 16 [12, 18] | +1 [-2, +5] | 0.8156 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 1.88 [1.41, 2.41] | 0.87 [0.67, 1.08] | -1.01 [-1.47, -0.61] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 53.6 [44.6, 62.5] | 39.8 [32.0, 47.8] | -13.7 [-20.4, -7.3] | 0.0002 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 29.4 [22.9, 37.5] | 42.3 [35.1, 50.2] | +13.0 [+6.8, +19.0] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 64.7 [57.0, 72.6] | 52.9 [44.0, 61.9] | -11.8 [-19.2, -5.0] | 0.0008 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 18] | 14 [8, 15] | -1 [-7, +1] | 0.2770 |

Top 20 concepts of the `min_k_shown` outputs: English; cooperate with colleagues; Agile development; computer engineering; implement front-end website design; maintain internal communication systems; project commissioning; web programming; design user interface; moderate a discussion; computer science; health care system; SAP R3; circulate information; automation technology; seek innovation in current practices; systems development life-cycle; business intelligence; manage relationships with stakeholders; use concurrent programming

Top 20 concepts of the true items of the same ads: English; teach communication methods; SAP Data Services; German; computer engineering; recruit members; design cloud architecture; Danish; perform scientific research; computer science; react to events in time-critical environments; web services; perform business research; systems development life-cycle; Ruby (computer programming); solve technical problems; communication; Java (computer programming); body language; manage budgets

## 53. Mistral Large 3 (Bedrock), job-ad skills, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 109 | False ESCO concepts per ad | 2.40 [1.78, 3.10] | 2.57 [2.27, 2.87] | +0.17 [-0.41, +0.66] | 0.5336 |
| `prose_up_to_k` | 109 | Ads with at least one false concept (%) | 71.6 [59.8, 82.4] | 88.3 [81.9, 93.7] | +16.7 [+8.2, +26.0] | < 0.0001 |
| `prose_up_to_k` | 109 | ESCO precision (%) | 20.6 [14.1, 29.1] | 19.5 [14.5, 24.9] | -1.1 [-6.5, +3.2] | 0.6074 |
| `prose_up_to_k` | 109 | ESCO recall (%) | 51.1 [39.8, 62.5] | 51.0 [42.8, 59.1] | -0.2 [-9.1, +8.9] | 0.9644 |
| `prose_up_to_k` | 109 | Top-20 concepts not in the true items' top 20 | 18 [13, 19] | 18 [12, 18] | +0 [-4, +2] | 0.7006 |
| `prose_exactly_k` | 109 | False ESCO concepts per ad | 2.40 [1.78, 3.10] | 2.90 [2.65, 3.15] | +0.49 [-0.11, +1.03] | 0.1044 |
| `prose_exactly_k` | 109 | Ads with at least one false concept (%) | 71.6 [59.8, 82.4] | 93.6 [89.6, 96.9] | +22.0 [+12.6, +32.1] | < 0.0001 |
| `prose_exactly_k` | 109 | ESCO precision (%) | 20.6 [14.1, 29.1] | 18.1 [13.5, 22.8] | -2.5 [-8.2, +1.8] | 0.2716 |
| `prose_exactly_k` | 109 | ESCO recall (%) | 51.1 [39.8, 62.5] | 52.3 [44.1, 60.4] | +1.2 [-7.5, +10.1] | 0.8240 |
| `prose_exactly_k` | 109 | Top-20 concepts not in the true items' top 20 | 18 [13, 19] | 17 [12, 19] | -1 [-4, +2] | 0.7916 |
| `max_k_shown` | 109 | False ESCO concepts per ad | 2.40 [1.78, 3.10] | 2.10 [1.73, 2.49] | -0.30 [-0.78, +0.12] | 0.1780 |
| `max_k_shown` | 109 | Ads with at least one false concept (%) | 71.6 [59.8, 82.4] | 78.9 [69.3, 87.9] | +7.3 [-1.8, +17.1] | 0.1408 |
| `max_k_shown` | 109 | ESCO precision (%) | 20.6 [14.1, 29.1] | 22.4 [16.3, 29.2] | +1.8 [-2.6, +5.8] | 0.4508 |
| `max_k_shown` | 109 | ESCO recall (%) | 51.1 [39.8, 62.5] | 49.6 [40.2, 59.2] | -1.5 [-10.1, +7.4] | 0.7876 |
| `max_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 18 [13, 19] | 18 [12, 19] | +0 [-4, +2] | 0.7674 |
| `min_k_shown` | 109 | False ESCO concepts per ad | 2.40 [1.78, 3.10] | 3.66 [3.25, 4.13] | +1.26 [+0.67, +1.79] | < 0.0001 |
| `min_k_shown` | 109 | Ads with at least one false concept (%) | 71.6 [59.8, 82.4] | 97.2 [93.6, 100.0] | +25.7 [+14.3, +37.7] | < 0.0001 |
| `min_k_shown` | 109 | ESCO precision (%) | 20.6 [14.1, 29.1] | 14.4 [10.3, 19.0] | -6.2 [-12.1, -1.8] | 0.0052 |
| `min_k_shown` | 109 | ESCO recall (%) | 51.1 [39.8, 62.5] | 50.4 [40.8, 60.3] | -0.8 [-9.4, +8.3] | 0.9208 |
| `min_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 18 [13, 19] | 20 [14, 20] | +2 [-2, +4] | 0.9416 |
| `min_k_shown_fewer_ok` | 109 | False ESCO concepts per ad | 2.40 [1.78, 3.10] | 1.33 [1.01, 1.67] | -1.07 [-1.73, -0.50] | < 0.0001 |
| `min_k_shown_fewer_ok` | 109 | Ads with at least one false concept (%) | 71.6 [59.8, 82.4] | 56.0 [44.5, 67.3] | -15.6 [-26.5, -5.4] | 0.0042 |
| `min_k_shown_fewer_ok` | 109 | ESCO precision (%) | 20.6 [14.1, 29.1] | 25.6 [17.8, 34.2] | +5.0 [-2.1, +11.6] | 0.1676 |
| `min_k_shown_fewer_ok` | 109 | ESCO recall (%) | 51.1 [39.8, 62.5] | 37.6 [26.0, 49.6] | -13.5 [-25.4, -2.7] | 0.0166 |
| `min_k_shown_fewer_ok` | 109 | Top-20 concepts not in the true items' top 20 | 18 [13, 19] | 14 [11, 18] | -4 [-6, +2] | 0.4128 |

## 54. Mistral Large 3 (Bedrock), job-ad knowledge, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 102 | False ESCO concepts per ad | 1.32 [0.67, 2.10] | 0.98 [0.68, 1.30] | -0.35 [-0.89, +0.10] | 0.1508 |
| `prose_up_to_k` | 102 | Ads with at least one false concept (%) | 34.3 [21.9, 47.5] | 45.3 [33.8, 56.9] | +11.0 [+4.2, +18.7] | 0.0004 |
| `prose_up_to_k` | 102 | ESCO precision (%) | 41.8 [28.8, 60.6] | 49.7 [38.9, 61.5] | +7.9 [-3.0, +14.5] | 0.1314 |
| `prose_up_to_k` | 102 | ESCO recall (%) | 79.5 [69.4, 88.9] | 80.7 [70.5, 89.4] | +1.1 [-6.0, +9.6] | 0.8488 |
| `prose_up_to_k` | 102 | Top-20 concepts not in the true items' top 20 | 11 [6, 17] | 11 [5, 13] | +0 [-7, +1] | 0.2884 |
| `prose_exactly_k` | 102 | False ESCO concepts per ad | 1.32 [0.67, 2.10] | 1.52 [1.19, 1.87] | +0.20 [-0.37, +0.68] | 0.4452 |
| `prose_exactly_k` | 102 | Ads with at least one false concept (%) | 34.3 [21.9, 47.5] | 58.4 [48.3, 68.5] | +24.1 [+16.1, +33.0] | < 0.0001 |
| `prose_exactly_k` | 102 | ESCO precision (%) | 41.8 [28.8, 60.6] | 39.2 [30.7, 48.4] | -2.7 [-15.8, +5.2] | 0.5358 |
| `prose_exactly_k` | 102 | ESCO recall (%) | 79.5 [69.4, 88.9] | 82.0 [74.0, 88.9] | +2.5 [-3.9, +10.7] | 0.5782 |
| `prose_exactly_k` | 102 | Top-20 concepts not in the true items' top 20 | 11 [6, 17] | 12 [6, 14] | +1 [-6, +3] | 0.5498 |
| `max_k_shown` | 102 | False ESCO concepts per ad | 1.32 [0.67, 2.10] | 0.93 [0.57, 1.34] | -0.39 [-0.90, +0.03] | 0.0758 |
| `max_k_shown` | 102 | Ads with at least one false concept (%) | 34.3 [21.9, 47.5] | 40.2 [27.4, 53.5] | +5.9 [+0.0, +13.5] | 0.0958 |
| `max_k_shown` | 102 | ESCO precision (%) | 41.8 [28.8, 60.6] | 49.5 [36.8, 64.0] | +7.7 [-2.1, +14.7] | 0.1106 |
| `max_k_shown` | 102 | ESCO recall (%) | 79.5 [69.4, 88.9] | 76.2 [65.5, 85.4] | -3.3 [-11.9, +5.9] | 0.4870 |
| `max_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 11 [6, 17] | 9 [5, 14] | -2 [-6, +2] | 0.4222 |
| `min_k_shown` | 102 | False ESCO concepts per ad | 1.32 [0.67, 2.10] | 3.31 [2.54, 4.16] | +1.99 [+1.30, +2.77] | < 0.0001 |
| `min_k_shown` | 102 | Ads with at least one false concept (%) | 34.3 [21.9, 47.5] | 75.5 [66.0, 84.5] | +41.2 [+30.1, +52.8] | < 0.0001 |
| `min_k_shown` | 102 | ESCO precision (%) | 41.8 [28.8, 60.6] | 23.2 [16.6, 31.3] | -18.6 [-33.8, -9.1] | < 0.0001 |
| `min_k_shown` | 102 | ESCO recall (%) | 79.5 [69.4, 88.9] | 83.6 [73.8, 91.9] | +4.1 [-3.3, +13.0] | 0.3868 |
| `min_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 11 [6, 17] | 13 [10, 18] | +2 [-2, +8] | 0.5844 |
| `min_k_shown_fewer_ok` | 102 | False ESCO concepts per ad | 1.32 [0.67, 2.10] | 0.38 [0.20, 0.60] | -0.94 [-1.60, -0.41] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | Ads with at least one false concept (%) | 34.3 [21.9, 47.5] | 22.5 [12.7, 33.7] | -11.8 [-20.0, -4.9] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | ESCO precision (%) | 41.8 [28.8, 60.6] | 68.5 [55.0, 81.9] | +26.7 [+15.5, +36.3] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | ESCO recall (%) | 79.5 [69.4, 88.9] | 69.7 [56.5, 81.4] | -9.8 [-19.8, -0.8] | 0.0464 |
| `min_k_shown_fewer_ok` | 102 | Top-20 concepts not in the true items' top 20 | 11 [6, 17] | 9 [4, 11] | -2 [-9, +0] | 0.1214 |

## 55. Qwen3-235B (Bedrock), both sets, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 1.73 [1.36, 2.11] | 1.42 [1.20, 1.63] | -0.31 [-0.60, -0.04] | 0.0230 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 59.2 [51.2, 67.1] | 55.1 [48.4, 61.8] | -4.2 [-9.2, +0.7] | 0.0932 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 29.7 [23.9, 36.9] | 33.8 [28.3, 39.8] | +4.0 [+0.3, +7.4] | 0.0370 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 60.4 [51.8, 69.1] | 59.8 [52.7, 67.1] | -0.6 [-5.5, +3.9] | 0.8084 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 17] | 14 [8, 16] | -1 [-5, +1] | 0.4742 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 1.73 [1.36, 2.11] | 1.98 [1.76, 2.19] | +0.25 [-0.05, +0.54] | 0.0976 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 59.2 [51.2, 67.1] | 70.2 [64.1, 76.1] | +11.0 [+4.9, +17.3] | 0.0002 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 29.7 [23.9, 36.9] | 27.3 [23.2, 31.7] | -2.4 [-6.7, +1.0] | 0.1642 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 60.4 [51.8, 69.1] | 61.5 [54.7, 68.5] | +1.1 [-4.8, +6.7] | 0.7132 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 17] | 15 [10, 16] | +0 [-4, +2] | 0.8928 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 1.73 [1.36, 2.11] | 1.60 [1.36, 1.83] | -0.13 [-0.40, +0.13] | 0.3810 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 59.2 [51.2, 67.1] | 63.0 [55.4, 70.5] | +3.8 [-1.0, +8.7] | 0.1350 |
| `max_k_shown` | 211 | ESCO precision (%) | 29.7 [23.9, 36.9] | 31.1 [25.7, 37.1] | +1.4 [-2.1, +4.2] | 0.4360 |
| `max_k_shown` | 211 | ESCO recall (%) | 60.4 [51.8, 69.1] | 59.6 [51.8, 67.8] | -0.8 [-4.9, +3.1] | 0.7874 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 17] | 16 [10, 17] | +1 [-4, +2] | 0.9272 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 1.73 [1.36, 2.11] | 3.52 [3.29, 3.75] | +1.79 [+1.38, +2.19] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 59.2 [51.2, 67.1] | 99.1 [97.6, 100.0] | +39.8 [+32.1, +47.7] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 29.7 [23.9, 36.9] | 18.7 [15.6, 22.0] | -11.0 [-16.5, -6.7] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 60.4 [51.8, 69.1] | 67.1 [60.3, 74.2] | +6.7 [+0.8, +12.8] | 0.0298 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 17] | 15 [12, 18] | +0 [-2, +5] | 0.5200 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 1.73 [1.36, 2.11] | 1.94 [1.69, 2.20] | +0.22 [-0.16, +0.57] | 0.2448 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 59.2 [51.2, 67.1] | 71.6 [63.6, 79.1] | +12.3 [+3.7, +21.0] | 0.0042 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 29.7 [23.9, 36.9] | 29.8 [25.2, 34.8] | +0.1 [-4.7, +4.2] | 0.9858 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 60.4 [51.8, 69.1] | 68.2 [61.2, 75.3] | +7.8 [+0.8, +15.2] | 0.0316 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 17] | 12 [10, 16] | -3 [-4, +2] | 0.8626 |

Top 20 concepts of the `min_k_shown` outputs: English; cooperate with colleagues; Agile development; follow work schedule; process applications; apply knowledge of science, technology and engineering; SAP R3; implement front-end website design; Java (computer programming); work in shifts; computer engineering; engage with stakeholders; cloud technologies; computer technology; teach communication methods; continuous improvement philosophies; work in an international environment; design cloud architecture; embedded systems; JavaScript

Top 20 concepts of the true items of the same ads: English; teach communication methods; SAP Data Services; German; computer engineering; recruit members; design cloud architecture; Danish; perform scientific research; computer science; react to events in time-critical environments; web services; perform business research; systems development life-cycle; Ruby (computer programming); solve technical problems; communication; Java (computer programming); body language; manage budgets

## 56. Qwen3-235B (Bedrock), job-ad skills, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 109 | False ESCO concepts per ad | 2.44 [1.91, 2.99] | 2.13 [1.80, 2.45] | -0.31 [-0.71, +0.06] | 0.1088 |
| `prose_up_to_k` | 109 | Ads with at least one false concept (%) | 81.7 [71.2, 90.9] | 77.6 [68.5, 86.0] | -4.0 [-10.4, +1.7] | 0.1780 |
| `prose_up_to_k` | 109 | ESCO precision (%) | 19.6 [13.6, 27.3] | 21.9 [16.0, 28.9] | +2.3 [-1.0, +5.2] | 0.1654 |
| `prose_up_to_k` | 109 | ESCO recall (%) | 48.9 [37.6, 60.6] | 49.0 [39.1, 59.5] | +0.2 [-6.2, +6.0] | 0.9852 |
| `prose_up_to_k` | 109 | Top-20 concepts not in the true items' top 20 | 19 [13, 19] | 18 [11, 18] | -1 [-5, +1] | 0.4436 |
| `prose_exactly_k` | 109 | False ESCO concepts per ad | 2.44 [1.91, 2.99] | 2.54 [2.26, 2.82] | +0.10 [-0.33, +0.52] | 0.6258 |
| `prose_exactly_k` | 109 | Ads with at least one false concept (%) | 81.7 [71.2, 90.9] | 84.8 [77.4, 91.2] | +3.1 [-4.7, +11.6] | 0.4436 |
| `prose_exactly_k` | 109 | ESCO precision (%) | 19.6 [13.6, 27.3] | 19.3 [14.4, 24.7] | -0.3 [-4.3, +2.8] | 0.8078 |
| `prose_exactly_k` | 109 | ESCO recall (%) | 48.9 [37.6, 60.6] | 49.9 [40.5, 60.0] | +1.1 [-6.1, +7.7] | 0.7840 |
| `prose_exactly_k` | 109 | Top-20 concepts not in the true items' top 20 | 19 [13, 19] | 18 [11, 18] | -1 [-4, +2] | 0.7290 |
| `max_k_shown` | 109 | False ESCO concepts per ad | 2.44 [1.91, 2.99] | 2.09 [1.75, 2.43] | -0.35 [-0.71, +0.00] | 0.0508 |
| `max_k_shown` | 109 | Ads with at least one false concept (%) | 81.7 [71.2, 90.9] | 81.7 [72.1, 90.2] | +0.0 [-5.6, +4.8] | 1.0000 |
| `max_k_shown` | 109 | ESCO precision (%) | 19.6 [13.6, 27.3] | 21.9 [15.8, 29.1] | +2.3 [-0.5, +4.6] | 0.0956 |
| `max_k_shown` | 109 | ESCO recall (%) | 48.9 [37.6, 60.6] | 48.1 [37.3, 59.4] | -0.8 [-6.1, +4.0] | 0.8884 |
| `max_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 19 [13, 19] | 17 [12, 19] | -2 [-4, +2] | 0.7550 |
| `min_k_shown` | 109 | False ESCO concepts per ad | 2.44 [1.91, 2.99] | 3.64 [3.34, 3.96] | +1.20 [+0.73, +1.69] | < 0.0001 |
| `min_k_shown` | 109 | Ads with at least one false concept (%) | 81.7 [71.2, 90.9] | 99.1 [97.1, 100.0] | +17.4 [+8.5, +27.4] | < 0.0001 |
| `min_k_shown` | 109 | ESCO precision (%) | 19.6 [13.6, 27.3] | 15.0 [10.9, 19.6] | -4.6 [-9.6, -0.9] | 0.0134 |
| `min_k_shown` | 109 | ESCO recall (%) | 48.9 [37.6, 60.6] | 52.6 [42.0, 63.8] | +3.8 [-2.9, +10.5] | 0.3210 |
| `min_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 19 [13, 19] | 19 [13, 19] | +0 [-2, +3] | 1.0000 |
| `min_k_shown_fewer_ok` | 109 | False ESCO concepts per ad | 2.44 [1.91, 2.99] | 2.06 [1.69, 2.45] | -0.38 [-0.94, +0.14] | 0.1742 |
| `min_k_shown_fewer_ok` | 109 | Ads with at least one false concept (%) | 81.7 [71.2, 90.9] | 72.5 [61.1, 83.2] | -9.2 [-20.4, +2.0] | 0.1254 |
| `min_k_shown_fewer_ok` | 109 | ESCO precision (%) | 19.6 [13.6, 27.3] | 23.7 [17.9, 30.4] | +4.1 [-0.5, +8.4] | 0.0778 |
| `min_k_shown_fewer_ok` | 109 | ESCO recall (%) | 48.9 [37.6, 60.6] | 52.6 [42.0, 63.6] | +3.8 [-3.8, +11.6] | 0.3912 |
| `min_k_shown_fewer_ok` | 109 | Top-20 concepts not in the true items' top 20 | 19 [13, 19] | 18 [11, 18] | -1 [-5, +1] | 0.4780 |

## 57. Qwen3-235B (Bedrock), job-ad knowledge, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 102 | False ESCO concepts per ad | 0.96 [0.48, 1.55] | 0.66 [0.43, 0.91] | -0.30 [-0.78, +0.08] | 0.1452 |
| `prose_up_to_k` | 102 | Ads with at least one false concept (%) | 35.3 [22.9, 48.5] | 31.0 [21.6, 41.0] | -4.3 [-13.0, +3.6] | 0.3140 |
| `prose_up_to_k` | 102 | ESCO precision (%) | 47.6 [34.2, 65.2] | 56.5 [45.5, 68.3] | +9.0 [-3.3, +18.9] | 0.1576 |
| `prose_up_to_k` | 102 | ESCO recall (%) | 73.0 [59.5, 85.2] | 71.5 [60.9, 81.2] | -1.5 [-9.1, +5.8] | 0.7242 |
| `prose_up_to_k` | 102 | Top-20 concepts not in the true items' top 20 | 10 [6, 16] | 9 [4, 12] | -1 [-8, +1] | 0.2110 |
| `prose_exactly_k` | 102 | False ESCO concepts per ad | 0.96 [0.48, 1.55] | 1.38 [1.08, 1.68] | +0.42 [-0.01, +0.78] | 0.0564 |
| `prose_exactly_k` | 102 | Ads with at least one false concept (%) | 35.3 [22.9, 48.5] | 54.7 [44.9, 64.5] | +19.4 [+9.2, +29.3] | < 0.0001 |
| `prose_exactly_k` | 102 | ESCO precision (%) | 47.6 [34.2, 65.2] | 39.1 [31.8, 46.6] | -8.5 [-21.3, +0.1] | 0.0542 |
| `prose_exactly_k` | 102 | ESCO recall (%) | 73.0 [59.5, 85.2] | 74.1 [63.8, 83.9] | +1.1 [-8.7, +10.4] | 0.7866 |
| `prose_exactly_k` | 102 | Top-20 concepts not in the true items' top 20 | 10 [6, 16] | 9 [7, 14] | -1 [-5, +3] | 0.8054 |
| `max_k_shown` | 102 | False ESCO concepts per ad | 0.96 [0.48, 1.55] | 1.07 [0.74, 1.42] | +0.11 [-0.33, +0.49] | 0.5960 |
| `max_k_shown` | 102 | Ads with at least one false concept (%) | 35.3 [22.9, 48.5] | 43.1 [31.1, 55.1] | +7.8 [-0.9, +16.3] | 0.0842 |
| `max_k_shown` | 102 | ESCO precision (%) | 47.6 [34.2, 65.2] | 44.7 [34.7, 55.9] | -2.9 [-15.2, +5.6] | 0.5296 |
| `max_k_shown` | 102 | ESCO recall (%) | 73.0 [59.5, 85.2] | 72.1 [59.8, 83.6] | -0.8 [-7.4, +5.8] | 0.9232 |
| `max_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 10 [6, 16] | 9 [7, 15] | -1 [-5, +4] | 0.9998 |
| `min_k_shown` | 102 | False ESCO concepts per ad | 0.96 [0.48, 1.55] | 3.38 [3.05, 3.75] | +2.42 [+1.74, +3.04] | < 0.0001 |
| `min_k_shown` | 102 | Ads with at least one false concept (%) | 35.3 [22.9, 48.5] | 99.0 [97.0, 100.0] | +63.7 [+50.5, +76.0] | < 0.0001 |
| `min_k_shown` | 102 | ESCO precision (%) | 47.6 [34.2, 65.2] | 22.6 [17.6, 28.1] | -24.9 [-41.1, -13.4] | < 0.0001 |
| `min_k_shown` | 102 | ESCO recall (%) | 73.0 [59.5, 85.2] | 82.8 [74.1, 91.1] | +9.8 [+0.0, +20.6] | 0.0578 |
| `min_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 10 [6, 16] | 16 [11, 18] | +6 [-1, +9] | 0.2952 |
| `min_k_shown_fewer_ok` | 102 | False ESCO concepts per ad | 0.96 [0.48, 1.55] | 1.81 [1.47, 2.16] | +0.85 [+0.31, +1.34] | 0.0038 |
| `min_k_shown_fewer_ok` | 102 | Ads with at least one false concept (%) | 35.3 [22.9, 48.5] | 70.6 [59.4, 81.4] | +35.3 [+22.9, +48.0] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | ESCO precision (%) | 47.6 [34.2, 65.2] | 36.0 [28.7, 43.8] | -11.6 [-26.1, -1.4] | 0.0226 |
| `min_k_shown_fewer_ok` | 102 | ESCO recall (%) | 73.0 [59.5, 85.2] | 85.2 [76.2, 93.3] | +12.3 [+0.0, +25.4] | 0.0566 |
| `min_k_shown_fewer_ok` | 102 | Top-20 concepts not in the true items' top 20 | 10 [6, 16] | 12 [9, 16] | +2 [-3, +6] | 0.9194 |

## 58. DeepSeek V4.1 Flash (Together), both sets, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 2.04 [1.55, 2.61] | 1.80 [1.57, 2.03] | -0.24 [-0.68, +0.11] | 0.2108 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 59.7 [51.1, 68.2] | 69.3 [62.4, 75.9] | +9.6 [+4.3, +14.8] | 0.0006 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 27.6 [21.6, 35.0] | 31.5 [26.4, 36.9] | +3.9 [-0.3, +7.8] | 0.0720 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 64.3 [57.1, 71.7] | 68.4 [61.6, 75.3] | +4.1 [+0.0, +8.2] | 0.0512 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 14 [10, 18] | 13 [9, 16] | -1 [-5, +1] | 0.3336 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 2.04 [1.55, 2.61] | 2.39 [2.20, 2.57] | +0.35 [-0.14, +0.75] | 0.1504 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 59.7 [51.1, 68.2] | 84.7 [80.6, 88.6] | +25.0 [+18.5, +31.8] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 27.6 [21.6, 35.0] | 25.6 [21.5, 29.8] | -2.0 [-7.1, +2.3] | 0.3552 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 64.3 [57.1, 71.7] | 68.0 [61.2, 74.9] | +3.7 [-0.4, +8.0] | 0.0804 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 14 [10, 18] | 13 [10, 16] | -1 [-5, +2] | 0.7232 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 2.04 [1.55, 2.61] | 1.47 [1.23, 1.72] | -0.56 [-1.00, -0.22] | 0.0004 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 59.7 [51.1, 68.2] | 64.5 [56.0, 72.6] | +4.7 [+0.0, +9.7] | 0.0548 |
| `max_k_shown` | 211 | ESCO precision (%) | 27.6 [21.6, 35.0] | 35.5 [29.5, 42.0] | +7.9 [+3.8, +11.9] | 0.0002 |
| `max_k_shown` | 211 | ESCO recall (%) | 64.3 [57.1, 71.7] | 67.1 [59.5, 74.6] | +2.7 [-1.4, +7.0] | 0.2194 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 14 [10, 18] | 13 [9, 16] | -1 [-5, +1] | 0.4980 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 2.04 [1.55, 2.61] | 3.56 [3.09, 4.07] | +1.53 [+1.12, +1.96] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 59.7 [51.1, 68.2] | 85.3 [79.3, 90.6] | +25.6 [+18.4, +33.5] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 27.6 [21.6, 35.0] | 18.6 [15.0, 22.7] | -9.0 [-13.8, -5.3] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 64.3 [57.1, 71.7] | 67.5 [60.5, 74.5] | +3.1 [+0.3, +6.4] | 0.0486 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 14 [10, 18] | 14 [12, 18] | +0 [-2, +4] | 0.8654 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 2.04 [1.55, 2.61] | 2.73 [2.31, 3.20] | +0.70 [+0.27, +1.12] | 0.0024 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 59.7 [51.1, 68.2] | 80.6 [73.2, 87.2] | +20.9 [+13.7, +28.3] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 27.6 [21.6, 35.0] | 22.7 [18.1, 27.9] | -5.0 [-9.4, -1.2] | 0.0074 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 64.3 [57.1, 71.7] | 66.3 [59.1, 73.4] | +2.0 [-1.4, +5.6] | 0.3130 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 14 [10, 18] | 13 [11, 18] | -1 [-2, +4] | 1.0000 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 2.04 [1.55, 2.61] | 4.62 [4.15, 5.15] | +2.58 [+1.99, +3.21] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 59.7 [51.1, 68.2] | 99.5 [98.5, 100.0] | +39.8 [+31.3, +48.4] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 27.6 [21.6, 35.0] | 16.0 [13.0, 19.2] | -11.6 [-17.5, -7.0] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO recall (%) | 64.3 [57.1, 71.7] | 72.9 [65.9, 79.9] | +8.6 [+4.6, +12.9] | < 0.0001 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 14 [10, 18] | 17 [13, 19] | +3 [-2, +5] | 0.5790 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 2.04 [1.55, 2.61] | 1.90 [1.49, 2.33] | -0.14 [-0.59, +0.24] | 0.5098 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 59.7 [51.1, 68.2] | 52.1 [43.6, 60.6] | -7.6 [-16.1, +0.5] | 0.0672 |
| `min_k_escape` | 211 | ESCO precision (%) | 27.6 [21.6, 35.0] | 29.0 [23.7, 35.3] | +1.3 [-3.0, +5.7] | 0.5546 |
| `min_k_escape` | 211 | ESCO recall (%) | 64.3 [57.1, 71.7] | 63.9 [56.6, 71.4] | -0.4 [-4.3, +3.2] | 0.9248 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 14 [10, 18] | 14 [10, 17] | +0 [-4, +2] | 0.8836 |

Top 20 concepts of the `min_k_shown` outputs: English; computer engineering; Agile development; implement front-end website design; DevOps; cooperate with colleagues; perform scientific research; SAP R3; cloud technologies; Java (computer programming); moderate a discussion; apply knowledge of science, technology and engineering; computer vision; computer science; process applications; build team spirit; team building; automation technology; continuous improvement philosophies; design cloud architecture

Top 20 concepts of the true items of the same ads: English; teach communication methods; SAP Data Services; German; computer engineering; recruit members; design cloud architecture; Danish; perform scientific research; computer science; react to events in time-critical environments; web services; perform business research; systems development life-cycle; Ruby (computer programming); solve technical problems; communication; Java (computer programming); body language; manage budgets

## 59. DeepSeek V4.1 Flash (Together), job-ad skills, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 109 | False ESCO concepts per ad | 2.42 [1.88, 2.98] | 2.38 [2.07, 2.68] | -0.04 [-0.39, +0.29] | 0.8236 |
| `prose_up_to_k` | 109 | Ads with at least one false concept (%) | 76.1 [65.0, 86.6] | 86.8 [79.5, 93.5] | +10.6 [+5.0, +17.3] | < 0.0001 |
| `prose_up_to_k` | 109 | ESCO precision (%) | 18.8 [12.8, 26.4] | 20.2 [14.5, 26.7] | +1.5 [-1.5, +4.0] | 0.3266 |
| `prose_up_to_k` | 109 | ESCO recall (%) | 45.9 [35.5, 56.9] | 49.5 [39.2, 60.4] | +3.6 [-1.2, +8.9] | 0.1642 |
| `prose_up_to_k` | 109 | Top-20 concepts not in the true items' top 20 | 18 [13, 20] | 17 [12, 19] | -1 [-4, +1] | 0.7118 |
| `prose_exactly_k` | 109 | False ESCO concepts per ad | 2.42 [1.88, 2.98] | 2.73 [2.47, 3.00] | +0.31 [-0.10, +0.71] | 0.1368 |
| `prose_exactly_k` | 109 | Ads with at least one false concept (%) | 76.1 [65.0, 86.6] | 94.5 [90.7, 97.6] | +18.3 [+9.8, +27.6] | < 0.0001 |
| `prose_exactly_k` | 109 | ESCO precision (%) | 18.8 [12.8, 26.4] | 17.8 [12.8, 23.5] | -1.0 [-4.6, +1.8] | 0.5020 |
| `prose_exactly_k` | 109 | ESCO recall (%) | 45.9 [35.5, 56.9] | 48.6 [38.2, 59.5] | +2.7 [-2.7, +8.2] | 0.3272 |
| `prose_exactly_k` | 109 | Top-20 concepts not in the true items' top 20 | 18 [13, 20] | 17 [12, 19] | -1 [-3, +2] | 0.8324 |
| `max_k_shown` | 109 | False ESCO concepts per ad | 2.42 [1.88, 2.98] | 1.91 [1.56, 2.25] | -0.51 [-0.85, -0.22] | < 0.0001 |
| `max_k_shown` | 109 | Ads with at least one false concept (%) | 76.1 [65.0, 86.6] | 78.9 [68.4, 88.9] | +2.8 [+0.0, +7.4] | 0.2552 |
| `max_k_shown` | 109 | ESCO precision (%) | 18.8 [12.8, 26.4] | 23.5 [16.6, 31.5] | +4.8 [+1.4, +8.1] | 0.0044 |
| `max_k_shown` | 109 | ESCO recall (%) | 45.9 [35.5, 56.9] | 48.1 [37.2, 59.7] | +2.3 [-3.9, +8.9] | 0.5498 |
| `max_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 18 [13, 20] | 17 [12, 19] | -1 [-4, +1] | 0.6454 |
| `min_k_shown` | 109 | False ESCO concepts per ad | 2.42 [1.88, 2.98] | 3.40 [2.85, 3.94] | +0.98 [+0.60, +1.40] | < 0.0001 |
| `min_k_shown` | 109 | Ads with at least one false concept (%) | 76.1 [65.0, 86.6] | 89.9 [82.3, 96.3] | +13.8 [+6.1, +22.4] | < 0.0001 |
| `min_k_shown` | 109 | ESCO precision (%) | 18.8 [12.8, 26.4] | 15.3 [10.6, 21.1] | -3.5 [-6.8, -1.0] | 0.0052 |
| `min_k_shown` | 109 | ESCO recall (%) | 45.9 [35.5, 56.9] | 50.4 [39.7, 61.6] | +4.5 [+0.7, +9.3] | 0.0388 |
| `min_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 18 [13, 20] | 18 [13, 20] | +0 [-2, +3] | 1.0000 |
| `min_k_shown_fewer_ok` | 109 | False ESCO concepts per ad | 2.42 [1.88, 2.98] | 2.91 [2.40, 3.44] | +0.49 [+0.12, +0.92] | 0.0064 |
| `min_k_shown_fewer_ok` | 109 | Ads with at least one false concept (%) | 76.1 [65.0, 86.6] | 86.2 [77.1, 93.9] | +10.1 [+3.6, +17.9] | 0.0020 |
| `min_k_shown_fewer_ok` | 109 | ESCO precision (%) | 18.8 [12.8, 26.4] | 16.8 [11.4, 23.5] | -2.0 [-5.5, +0.8] | 0.1776 |
| `min_k_shown_fewer_ok` | 109 | ESCO recall (%) | 45.9 [35.5, 56.9] | 48.1 [37.4, 59.2] | +2.3 [-3.8, +8.5] | 0.5536 |
| `min_k_shown_fewer_ok` | 109 | Top-20 concepts not in the true items' top 20 | 18 [13, 20] | 18 [13, 20] | +0 [-2, +3] | 1.0000 |
| `min_k_enforced` | 109 | False ESCO concepts per ad | 2.42 [1.88, 2.98] | 4.19 [3.72, 4.69] | +1.77 [+1.30, +2.29] | < 0.0001 |
| `min_k_enforced` | 109 | Ads with at least one false concept (%) | 76.1 [65.0, 86.6] | 100.0 [100.0, 100.0] | +23.9 [+13.4, +35.0] | < 0.0001 |
| `min_k_enforced` | 109 | ESCO precision (%) | 18.8 [12.8, 26.4] | 14.1 [10.3, 18.3] | -4.7 [-9.3, -1.3] | 0.0062 |
| `min_k_enforced` | 109 | ESCO recall (%) | 45.9 [35.5, 56.9] | 56.4 [46.3, 67.2] | +10.5 [+4.8, +16.9] | < 0.0001 |
| `min_k_enforced` | 109 | Top-20 concepts not in the true items' top 20 | 18 [13, 20] | 19 [14, 20] | +1 [-2, +4] | 1.0000 |
| `min_k_escape` | 109 | False ESCO concepts per ad | 2.42 [1.88, 2.98] | 2.16 [1.58, 2.76] | -0.27 [-0.77, +0.24] | 0.3116 |
| `min_k_escape` | 109 | Ads with at least one false concept (%) | 76.1 [65.0, 86.6] | 59.6 [47.3, 72.0] | -16.5 [-27.9, -5.6] | 0.0042 |
| `min_k_escape` | 109 | ESCO precision (%) | 18.8 [12.8, 26.4] | 20.1 [14.0, 27.7] | +1.3 [-2.9, +5.6] | 0.5446 |
| `min_k_escape` | 109 | ESCO recall (%) | 45.9 [35.5, 56.9] | 44.4 [33.8, 55.1] | -1.5 [-8.2, +4.3] | 0.7334 |
| `min_k_escape` | 109 | Top-20 concepts not in the true items' top 20 | 18 [13, 20] | 18 [12, 19] | +0 [-4, +2] | 1.0000 |

## 60. DeepSeek V4.1 Flash (Together), job-ad knowledge, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 102 | False ESCO concepts per ad | 1.63 [0.84, 2.62] | 1.17 [0.86, 1.51] | -0.45 [-1.27, +0.16] | 0.1972 |
| `prose_up_to_k` | 102 | Ads with at least one false concept (%) | 42.2 [29.1, 55.8] | 50.6 [39.4, 61.9] | +8.4 [-0.2, +16.9] | 0.0560 |
| `prose_up_to_k` | 102 | ESCO precision (%) | 38.3 [26.6, 55.8] | 47.5 [38.4, 57.2] | +9.3 [-3.0, +18.0] | 0.1422 |
| `prose_up_to_k` | 102 | ESCO recall (%) | 84.4 [75.8, 92.2] | 89.0 [82.6, 94.8] | +4.6 [-2.0, +11.8] | 0.1750 |
| `prose_up_to_k` | 102 | Top-20 concepts not in the true items' top 20 | 11 [7, 17] | 11 [5, 13] | +0 [-9, +1] | 0.2302 |
| `prose_exactly_k` | 102 | False ESCO concepts per ad | 1.63 [0.84, 2.62] | 2.02 [1.76, 2.28] | +0.39 [-0.50, +1.07] | 0.3386 |
| `prose_exactly_k` | 102 | Ads with at least one false concept (%) | 42.2 [29.1, 55.8] | 74.3 [67.0, 81.4] | +32.2 [+22.3, +42.1] | < 0.0001 |
| `prose_exactly_k` | 102 | ESCO precision (%) | 38.3 [26.6, 55.8] | 34.6 [28.3, 41.0] | -3.7 [-18.6, +5.9] | 0.4788 |
| `prose_exactly_k` | 102 | ESCO recall (%) | 84.4 [75.8, 92.2] | 89.2 [83.5, 94.3] | +4.8 [-1.2, +11.4] | 0.1276 |
| `prose_exactly_k` | 102 | Top-20 concepts not in the true items' top 20 | 11 [7, 17] | 11 [7, 14] | +0 [-8, +3] | 0.5296 |
| `max_k_shown` | 102 | False ESCO concepts per ad | 1.63 [0.84, 2.62] | 1.01 [0.69, 1.36] | -0.62 [-1.44, +0.01] | 0.0554 |
| `max_k_shown` | 102 | Ads with at least one false concept (%) | 42.2 [29.1, 55.8] | 49.0 [35.6, 62.6] | +6.9 [-2.0, +16.2] | 0.1596 |
| `max_k_shown` | 102 | ESCO precision (%) | 38.3 [26.6, 55.8] | 51.0 [40.8, 62.2] | +12.7 [+0.7, +21.8] | 0.0412 |
| `max_k_shown` | 102 | ESCO recall (%) | 84.4 [75.8, 92.2] | 87.7 [80.3, 94.3] | +3.3 [-1.8, +9.4] | 0.2978 |
| `max_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 11 [7, 17] | 9 [6, 14] | -2 [-8, +2] | 0.3506 |
| `min_k_shown` | 102 | False ESCO concepts per ad | 1.63 [0.84, 2.62] | 3.74 [2.91, 4.62] | +2.11 [+1.40, +2.88] | < 0.0001 |
| `min_k_shown` | 102 | Ads with at least one false concept (%) | 42.2 [29.1, 55.8] | 80.4 [70.4, 89.3] | +38.2 [+26.5, +50.5] | < 0.0001 |
| `min_k_shown` | 102 | ESCO precision (%) | 38.3 [26.6, 55.8] | 21.6 [16.0, 28.5] | -16.7 [-30.8, -8.1] | < 0.0001 |
| `min_k_shown` | 102 | ESCO recall (%) | 84.4 [75.8, 92.2] | 86.1 [78.6, 92.7] | +1.6 [-2.5, +6.6] | 0.6396 |
| `min_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 11 [7, 17] | 15 [11, 18] | +4 [-2, +8] | 0.4516 |
| `min_k_shown_fewer_ok` | 102 | False ESCO concepts per ad | 1.63 [0.84, 2.62] | 2.55 [1.84, 3.34] | +0.92 [+0.15, +1.71] | 0.0220 |
| `min_k_shown_fewer_ok` | 102 | Ads with at least one false concept (%) | 42.2 [29.1, 55.8] | 74.5 [63.3, 85.1] | +32.4 [+19.8, +45.5] | < 0.0001 |
| `min_k_shown_fewer_ok` | 102 | ESCO precision (%) | 38.3 [26.6, 55.8] | 28.8 [21.1, 38.4] | -9.5 [-23.0, -0.9] | 0.0276 |
| `min_k_shown_fewer_ok` | 102 | ESCO recall (%) | 84.4 [75.8, 92.2] | 86.1 [78.0, 93.4] | +1.6 [+0.0, +5.5] | 0.7340 |
| `min_k_shown_fewer_ok` | 102 | Top-20 concepts not in the true items' top 20 | 11 [7, 17] | 12 [10, 18] | +1 [-3, +7] | 0.6848 |
| `min_k_enforced` | 102 | False ESCO concepts per ad | 1.63 [0.84, 2.62] | 5.08 [4.26, 6.05] | +3.45 [+2.38, +4.59] | < 0.0001 |
| `min_k_enforced` | 102 | Ads with at least one false concept (%) | 42.2 [29.1, 55.8] | 99.0 [96.9, 100.0] | +56.9 [+43.4, +70.0] | < 0.0001 |
| `min_k_enforced` | 102 | ESCO precision (%) | 38.3 [26.6, 55.8] | 17.6 [13.1, 22.8] | -20.6 [-36.7, -10.7] | < 0.0001 |
| `min_k_enforced` | 102 | ESCO recall (%) | 84.4 [75.8, 92.2] | 91.0 [83.7, 96.8] | +6.6 [+1.5, +13.1] | 0.0324 |
| `min_k_enforced` | 102 | Top-20 concepts not in the true items' top 20 | 11 [7, 17] | 16 [13, 19] | +5 [-1, +10] | 0.2776 |
| `min_k_escape` | 102 | False ESCO concepts per ad | 1.63 [0.84, 2.62] | 1.62 [1.00, 2.31] | -0.01 [-0.72, +0.61] | 0.9878 |
| `min_k_escape` | 102 | Ads with at least one false concept (%) | 42.2 [29.1, 55.8] | 44.1 [31.7, 56.7] | +2.0 [-11.9, +15.3] | 0.8304 |
| `min_k_escape` | 102 | ESCO precision (%) | 38.3 [26.6, 55.8] | 38.7 [29.3, 50.4] | +0.4 [-11.2, +9.3] | 0.9892 |
| `min_k_escape` | 102 | ESCO recall (%) | 84.4 [75.8, 92.2] | 85.2 [76.9, 92.8] | +0.8 [-2.3, +4.8] | 0.9292 |
| `min_k_escape` | 102 | Top-20 concepts not in the true items' top 20 | 11 [7, 17] | 12 [7, 16] | +1 [-6, +4] | 0.9134 |

## 61. Qwen3.5-9B (Together), both sets, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 2.40 [1.79, 3.07] | 1.64 [1.34, 1.94] | -0.76 [-1.22, -0.34] | 0.0002 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 44.1 [36.4, 51.9] | 52.7 [46.2, 59.2] | +8.6 [+3.4, +14.1] | 0.0012 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 17.2 [12.5, 23.1] | 26.7 [21.3, 32.7] | +9.6 [+5.7, +13.3] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 41.2 [32.1, 50.4] | 49.4 [41.9, 56.9] | +8.2 [+0.9, +15.5] | 0.0298 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 15 [12, 19] | 11 [10, 17] | -4 [-6, +1] | 0.2416 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 2.40 [1.79, 3.07] | 1.61 [1.35, 1.88] | -0.79 [-1.25, -0.37] | 0.0002 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 44.1 [36.4, 51.9] | 54.4 [47.5, 61.0] | +10.3 [+5.3, +15.6] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 17.2 [12.5, 23.1] | 24.8 [20.0, 30.2] | +7.6 [+3.8, +11.2] | 0.0006 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 41.2 [32.1, 50.4] | 43.9 [36.7, 51.6] | +2.7 [-4.4, +9.7] | 0.4302 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 15 [12, 19] | 13 [10, 17] | -2 [-5, +1] | 0.3880 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 2.40 [1.79, 3.07] | 1.81 [1.37, 2.31] | -0.59 [-0.93, -0.28] | 0.0008 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 44.1 [36.4, 51.9] | 50.2 [42.8, 57.3] | +6.2 [+1.9, +11.2] | 0.0072 |
| `max_k_shown` | 211 | ESCO precision (%) | 17.2 [12.5, 23.1] | 23.8 [17.8, 30.9] | +6.6 [+3.4, +10.2] | 0.0002 |
| `max_k_shown` | 211 | ESCO recall (%) | 41.2 [32.1, 50.4] | 46.7 [37.8, 55.3] | +5.5 [+0.4, +11.2] | 0.0474 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 15 [12, 19] | 15 [12, 18] | +0 [-3, +2] | 0.8452 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 2.40 [1.79, 3.07] | 2.87 [2.30, 3.46] | +0.47 [+0.12, +0.85] | 0.0104 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 44.1 [36.4, 51.9] | 57.8 [50.0, 65.6] | +13.7 [+7.7, +20.4] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 17.2 [12.5, 23.1] | 18.7 [14.3, 23.8] | +1.5 [-1.7, +4.3] | 0.3408 |
| `min_k_shown` | 211 | ESCO recall (%) | 41.2 [32.1, 50.4] | 54.5 [44.8, 64.0] | +13.3 [+6.5, +20.7] | < 0.0001 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 15 [12, 19] | 14 [11, 18] | -1 [-3, +1] | 0.6938 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 2.40 [1.79, 3.07] | 1.87 [1.25, 2.58] | -0.53 [-0.86, -0.19] | 0.0030 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 44.1 [36.4, 51.9] | 30.8 [23.3, 38.6] | -13.3 [-19.9, -6.8] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 17.2 [12.5, 23.1] | 16.5 [11.3, 23.5] | -0.7 [-4.4, +3.4] | 0.7788 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 41.2 [32.1, 50.4] | 30.6 [22.7, 39.0] | -10.6 [-18.6, -3.1] | 0.0068 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 15 [12, 19] | 15 [13, 19] | +0 [-2, +3] | 0.9500 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 2.40 [1.79, 3.07] | 5.24 [4.43, 6.28] | +2.84 [+2.07, +3.85] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 44.1 [36.4, 51.9] | 99.1 [97.6, 100.0] | +55.0 [+47.3, +62.6] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 17.2 [12.5, 23.1] | 15.1 [11.8, 18.8] | -2.1 [-7.0, +1.8] | 0.3326 |
| `min_k_enforced` | 211 | ESCO recall (%) | 41.2 [32.1, 50.4] | 77.3 [70.7, 83.5] | +36.1 [+27.3, +45.3] | < 0.0001 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 15 [12, 19] | 13 [11, 18] | -2 [-4, +2] | 0.5726 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 2.40 [1.79, 3.07] | 2.82 [2.18, 3.56] | +0.42 [+0.05, +0.83] | 0.0244 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 44.1 [36.4, 51.9] | 55.5 [47.6, 63.3] | +11.4 [+4.7, +18.3] | 0.0006 |
| `min_k_escape` | 211 | ESCO precision (%) | 17.2 [12.5, 23.1] | 19.8 [14.9, 25.6] | +2.6 [-0.6, +5.8] | 0.1064 |
| `min_k_escape` | 211 | ESCO recall (%) | 41.2 [32.1, 50.4] | 57.6 [47.7, 67.1] | +16.5 [+9.1, +24.2] | < 0.0001 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 15 [12, 19] | 15 [11, 18] | +0 [-4, +2] | 0.7968 |

Top 20 concepts of the `min_k_shown` outputs: Java (computer programming); English; Python (computer programming); react to events in time-critical environments; JavaScript; teach communication methods; computer engineering; manage ICT virtualisation environments; cloud technologies; implement front-end website design; DevOps; support managers; ICT project management methodologies; types of spring; Agile development; web services; continuous improvement philosophies; C#; tools for ICT test automation; automation technology

Top 20 concepts of the true items of the same ads: English; teach communication methods; SAP Data Services; German; computer engineering; recruit members; design cloud architecture; Danish; perform scientific research; computer science; react to events in time-critical environments; web services; perform business research; systems development life-cycle; Ruby (computer programming); solve technical problems; communication; Java (computer programming); body language; manage budgets

## 62. Qwen3.5-9B (Together), job-ad skills, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 109 | False ESCO concepts per ad | 4.21 [3.11, 5.40] | 2.89 [2.38, 3.43] | -1.32 [-2.12, -0.57] | < 0.0001 |
| `prose_up_to_k` | 109 | Ads with at least one false concept (%) | 73.4 [61.9, 84.5] | 85.7 [77.9, 92.5] | +12.3 [+4.9, +20.3] | 0.0002 |
| `prose_up_to_k` | 109 | ESCO precision (%) | 11.0 [7.0, 16.4] | 14.1 [9.4, 19.8] | +3.0 [-0.1, +6.0] | 0.0562 |
| `prose_up_to_k` | 109 | ESCO recall (%) | 42.9 [30.8, 55.3] | 38.8 [28.7, 49.4] | -4.1 [-13.4, +4.6] | 0.3826 |
| `prose_up_to_k` | 109 | Top-20 concepts not in the true items' top 20 | 17 [15, 20] | 16 [13, 19] | -1 [-4, +1] | 0.5616 |
| `prose_exactly_k` | 109 | False ESCO concepts per ad | 4.21 [3.11, 5.40] | 2.73 [2.30, 3.19] | -1.48 [-2.31, -0.71] | < 0.0001 |
| `prose_exactly_k` | 109 | Ads with at least one false concept (%) | 73.4 [61.9, 84.5] | 85.5 [77.3, 92.7] | +12.1 [+5.1, +19.8] | < 0.0001 |
| `prose_exactly_k` | 109 | ESCO precision (%) | 11.0 [7.0, 16.4] | 14.2 [9.5, 19.7] | +3.1 [+0.1, +5.8] | 0.0456 |
| `prose_exactly_k` | 109 | ESCO recall (%) | 42.9 [30.8, 55.3] | 37.0 [27.1, 47.5] | -5.9 [-14.7, +1.9] | 0.1570 |
| `prose_exactly_k` | 109 | Top-20 concepts not in the true items' top 20 | 17 [15, 20] | 16 [13, 19] | -1 [-4, +1] | 0.6468 |
| `max_k_shown` | 109 | False ESCO concepts per ad | 4.21 [3.11, 5.40] | 3.19 [2.41, 4.07] | -1.02 [-1.66, -0.43] | 0.0006 |
| `max_k_shown` | 109 | Ads with at least one false concept (%) | 73.4 [61.9, 84.5] | 83.5 [73.4, 92.5] | +10.1 [+2.7, +18.9] | 0.0072 |
| `max_k_shown` | 109 | ESCO precision (%) | 11.0 [7.0, 16.4] | 14.5 [9.5, 21.0] | +3.4 [+1.1, +6.3] | 0.0028 |
| `max_k_shown` | 109 | ESCO recall (%) | 42.9 [30.8, 55.3] | 44.4 [33.1, 55.9] | +1.5 [-4.5, +7.9] | 0.7414 |
| `max_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 17 [15, 20] | 17 [15, 20] | +0 [-2, +2] | 1.0000 |
| `min_k_shown` | 109 | False ESCO concepts per ad | 4.21 [3.11, 5.40] | 4.64 [3.68, 5.70] | +0.43 [-0.19, +1.13] | 0.1976 |
| `min_k_shown` | 109 | Ads with at least one false concept (%) | 73.4 [61.9, 84.5] | 88.1 [79.0, 96.1] | +14.7 [+5.6, +24.5] | 0.0002 |
| `min_k_shown` | 109 | ESCO precision (%) | 11.0 [7.0, 16.4] | 12.9 [8.9, 17.9] | +1.9 [-0.7, +4.1] | 0.1312 |
| `min_k_shown` | 109 | ESCO recall (%) | 42.9 [30.8, 55.3] | 56.4 [45.0, 67.8] | +13.5 [+6.7, +21.2] | < 0.0001 |
| `min_k_shown` | 109 | Top-20 concepts not in the true items' top 20 | 17 [15, 20] | 17 [14, 20] | +0 [-2, +1] | 1.0000 |
| `min_k_shown_fewer_ok` | 109 | False ESCO concepts per ad | 4.21 [3.11, 5.40] | 3.17 [2.02, 4.50] | -1.04 [-1.66, -0.38] | 0.0020 |
| `min_k_shown_fewer_ok` | 109 | Ads with at least one false concept (%) | 73.4 [61.9, 84.5] | 45.9 [34.0, 57.7] | -27.5 [-39.4, -16.0] | < 0.0001 |
| `min_k_shown_fewer_ok` | 109 | ESCO precision (%) | 11.0 [7.0, 16.4] | 9.4 [5.1, 15.5] | -1.6 [-4.6, +1.5] | 0.3092 |
| `min_k_shown_fewer_ok` | 109 | ESCO recall (%) | 42.9 [30.8, 55.3] | 27.1 [16.1, 38.7] | -15.8 [-25.8, -6.2] | 0.0018 |
| `min_k_shown_fewer_ok` | 109 | Top-20 concepts not in the true items' top 20 | 17 [15, 20] | 19 [15, 20] | +2 [-2, +3] | 1.0000 |
| `min_k_enforced` | 109 | False ESCO concepts per ad | 4.21 [3.11, 5.40] | 5.77 [4.86, 6.82] | +1.56 [+0.82, +2.36] | < 0.0001 |
| `min_k_enforced` | 109 | Ads with at least one false concept (%) | 73.4 [61.9, 84.5] | 100.0 [100.0, 100.0] | +26.6 [+15.5, +38.1] | < 0.0001 |
| `min_k_enforced` | 109 | ESCO precision (%) | 11.0 [7.0, 16.4] | 11.7 [8.2, 15.7] | +0.6 [-2.3, +3.0] | 0.6476 |
| `min_k_enforced` | 109 | ESCO recall (%) | 42.9 [30.8, 55.3] | 62.4 [51.8, 72.8] | +19.5 [+10.4, +29.9] | < 0.0001 |
| `min_k_enforced` | 109 | Top-20 concepts not in the true items' top 20 | 17 [15, 20] | 16 [14, 20] | -1 [-3, +1] | 0.8396 |
| `min_k_escape` | 109 | False ESCO concepts per ad | 4.21 [3.11, 5.40] | 4.82 [3.68, 6.18] | +0.61 [-0.06, +1.36] | 0.0838 |
| `min_k_escape` | 109 | Ads with at least one false concept (%) | 73.4 [61.9, 84.5] | 86.2 [76.6, 94.5] | +12.8 [+3.5, +23.3] | 0.0080 |
| `min_k_escape` | 109 | ESCO precision (%) | 11.0 [7.0, 16.4] | 12.5 [8.4, 17.8] | +1.5 [-1.0, +4.0] | 0.2318 |
| `min_k_escape` | 109 | ESCO recall (%) | 42.9 [30.8, 55.3] | 56.4 [44.5, 68.1] | +13.5 [+5.7, +22.5] | < 0.0001 |
| `min_k_escape` | 109 | Top-20 concepts not in the true items' top 20 | 17 [15, 20] | 18 [14, 20] | +1 [-3, +2] | 1.0000 |

## 63. Qwen3.5-9B (Together), job-ad knowledge, cutoff 0.5

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 102 | False ESCO concepts per ad | 0.46 [0.08, 0.98] | 0.29 [0.15, 0.46] | -0.17 [-0.60, +0.16] | 0.3972 |
| `prose_up_to_k` | 102 | Ads with at least one false concept (%) | 12.7 [4.9, 22.3] | 17.5 [9.8, 26.0] | +4.7 [-3.0, +12.4] | 0.2274 |
| `prose_up_to_k` | 102 | ESCO precision (%) | 50.5 [30.1, 83.9] | 71.4 [61.2, 82.4] | +20.9 [-8.5, +36.3] | 0.1564 |
| `prose_up_to_k` | 102 | ESCO recall (%) | 39.3 [25.2, 53.7] | 61.0 [50.3, 70.8] | +21.6 [+10.5, +33.7] | < 0.0001 |
| `prose_up_to_k` | 102 | Top-20 concepts not in the true items' top 20 | 13 [8, 16] | 10 [4, 11] | -3 [-9, +0] | 0.0784 |
| `prose_exactly_k` | 102 | False ESCO concepts per ad | 0.46 [0.08, 0.98] | 0.41 [0.23, 0.62] | -0.05 [-0.42, +0.23] | 0.8052 |
| `prose_exactly_k` | 102 | Ads with at least one false concept (%) | 12.7 [4.9, 22.3] | 21.2 [13.2, 30.0] | +8.4 [+1.6, +15.5] | 0.0124 |
| `prose_exactly_k` | 102 | ESCO precision (%) | 50.5 [30.1, 83.9] | 60.3 [49.3, 72.4] | +9.7 [-18.0, +23.9] | 0.4410 |
| `prose_exactly_k` | 102 | ESCO recall (%) | 39.3 [25.2, 53.7] | 51.5 [40.4, 62.4] | +12.1 [+0.9, +23.6] | 0.0364 |
| `prose_exactly_k` | 102 | Top-20 concepts not in the true items' top 20 | 13 [8, 16] | 13 [6, 13] | +0 [-7, +2] | 0.3954 |
| `max_k_shown` | 102 | False ESCO concepts per ad | 0.46 [0.08, 0.98] | 0.33 [0.09, 0.74] | -0.13 [-0.36, +0.03] | 0.2022 |
| `max_k_shown` | 102 | Ads with at least one false concept (%) | 12.7 [4.9, 22.3] | 14.7 [6.9, 23.8] | +2.0 [-1.9, +5.9] | 0.4460 |
| `max_k_shown` | 102 | ESCO precision (%) | 50.5 [30.1, 83.9] | 63.8 [43.2, 86.6] | +13.3 [-0.6, +24.6] | 0.0592 |
| `max_k_shown` | 102 | ESCO recall (%) | 39.3 [25.2, 53.7] | 49.2 [34.6, 63.2] | +9.8 [+1.5, +20.0] | 0.0286 |
| `max_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 13 [8, 16] | 13 [6, 14] | +0 [-6, +1] | 0.4358 |
| `min_k_shown` | 102 | False ESCO concepts per ad | 0.46 [0.08, 0.98] | 0.97 [0.48, 1.57] | +0.51 [+0.23, +0.84] | < 0.0001 |
| `min_k_shown` | 102 | Ads with at least one false concept (%) | 12.7 [4.9, 22.3] | 25.5 [15.2, 37.0] | +12.7 [+5.1, +21.4] | < 0.0001 |
| `min_k_shown` | 102 | ESCO precision (%) | 50.5 [30.1, 83.9] | 39.3 [27.8, 55.3] | -11.3 [-35.0, +0.6] | 0.0648 |
| `min_k_shown` | 102 | ESCO recall (%) | 39.3 [25.2, 53.7] | 52.5 [37.2, 66.7] | +13.1 [+0.8, +26.0] | 0.0406 |
| `min_k_shown` | 102 | Top-20 concepts not in the true items' top 20 | 13 [8, 16] | 10 [8, 16] | -3 [-4, +4] | 1.0000 |
| `min_k_shown_fewer_ok` | 102 | False ESCO concepts per ad | 0.46 [0.08, 0.98] | 0.47 [0.16, 0.91] | +0.01 [-0.23, +0.23] | 0.9474 |
| `min_k_shown_fewer_ok` | 102 | Ads with at least one false concept (%) | 12.7 [4.9, 22.3] | 14.7 [6.7, 24.5] | +2.0 [-5.1, +9.0] | 0.6844 |
| `min_k_shown_fewer_ok` | 102 | ESCO precision (%) | 50.5 [30.1, 83.9] | 46.7 [31.1, 69.8] | -3.9 [-25.4, +9.5] | 0.6106 |
| `min_k_shown_fewer_ok` | 102 | ESCO recall (%) | 39.3 [25.2, 53.7] | 34.4 [21.9, 47.0] | -4.9 [-18.2, +7.0] | 0.4850 |
| `min_k_shown_fewer_ok` | 102 | Top-20 concepts not in the true items' top 20 | 13 [8, 16] | 13 [8, 15] | +0 [-4, +4] | 1.0000 |
| `min_k_enforced` | 102 | False ESCO concepts per ad | 0.46 [0.08, 0.98] | 4.67 [3.41, 6.46] | +4.21 [+2.97, +6.00] | < 0.0001 |
| `min_k_enforced` | 102 | Ads with at least one false concept (%) | 12.7 [4.9, 22.3] | 98.0 [95.1, 100.0] | +85.3 [+75.7, +93.3] | < 0.0001 |
| `min_k_enforced` | 102 | ESCO precision (%) | 50.5 [30.1, 83.9] | 19.3 [13.2, 27.0] | -31.2 [-64.6, -11.2] | < 0.0001 |
| `min_k_enforced` | 102 | ESCO recall (%) | 39.3 [25.2, 53.7] | 93.4 [87.7, 98.1] | +54.1 [+39.5, +69.0] | < 0.0001 |
| `min_k_enforced` | 102 | Top-20 concepts not in the true items' top 20 | 13 [8, 16] | 14 [11, 18] | +1 [-2, +8] | 0.3336 |
| `min_k_escape` | 102 | False ESCO concepts per ad | 0.46 [0.08, 0.98] | 0.69 [0.30, 1.18] | +0.23 [-0.07, +0.56] | 0.1564 |
| `min_k_escape` | 102 | Ads with at least one false concept (%) | 12.7 [4.9, 22.3] | 22.5 [12.7, 33.7] | +9.8 [+1.0, +18.8] | 0.0348 |
| `min_k_escape` | 102 | ESCO precision (%) | 50.5 [30.1, 83.9] | 50.7 [37.1, 68.8] | +0.2 [-25.2, +13.5] | 0.9946 |
| `min_k_escape` | 102 | ESCO recall (%) | 39.3 [25.2, 53.7] | 59.0 [43.5, 73.0] | +19.7 [+6.8, +33.6] | 0.0028 |
| `min_k_escape` | 102 | Top-20 concepts not in the true items' top 20 | 13 [8, 16] | 11 [6, 15] | -2 [-5, +3] | 0.6188 |

## 64. 8 main models pooled, both sets, cutoff none

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 1688 | False ESCO concepts per ad | 7.07 [6.42, 7.75] | 4.23 [3.95, 4.54] | -2.84 [-3.38, -2.32] | < 0.0001 |
| `prose_up_to_k` | 1688 | Ads with at least one false concept (%) | 62.7 [58.5, 66.8] | 70.6 [67.1, 74.0] | +7.9 [+6.0, +10.0] | < 0.0001 |
| `prose_up_to_k` | 1688 | ESCO precision (%) | 9.6 [8.0, 11.4] | 14.7 [12.5, 17.1] | +5.1 [+4.1, +6.2] | < 0.0001 |
| `prose_up_to_k` | 1688 | ESCO recall (%) | 57.2 [52.3, 62.2] | 55.7 [50.9, 60.5] | -1.6 [-3.7, +0.7] | 0.1682 |
| `prose_up_to_k` | 1688 | Top-20 concepts not in the true items' top 20 | 15 [12, 18] | 13 [10, 17] | -2 [-4, +1] | 0.4684 |
| `prose_exactly_k` | 1688 | False ESCO concepts per ad | 7.07 [6.42, 7.75] | 4.16 [3.88, 4.47] | -2.91 [-3.47, -2.36] | < 0.0001 |
| `prose_exactly_k` | 1688 | Ads with at least one false concept (%) | 62.7 [58.5, 66.8] | 77.1 [73.8, 80.5] | +14.5 [+12.3, +16.8] | < 0.0001 |
| `prose_exactly_k` | 1688 | ESCO precision (%) | 9.6 [8.0, 11.4] | 15.0 [12.7, 17.4] | +5.4 [+4.3, +6.6] | < 0.0001 |
| `prose_exactly_k` | 1688 | ESCO recall (%) | 57.2 [52.3, 62.2] | 55.9 [51.5, 60.4] | -1.3 [-3.6, +0.9] | 0.2608 |
| `prose_exactly_k` | 1688 | Top-20 concepts not in the true items' top 20 | 15 [12, 18] | 14 [11, 17] | -1 [-4, +1] | 0.6066 |
| `max_k_shown` | 1688 | False ESCO concepts per ad | 7.07 [6.42, 7.75] | 5.70 [5.17, 6.25] | -1.38 [-1.79, -0.97] | < 0.0001 |
| `max_k_shown` | 1688 | Ads with at least one false concept (%) | 62.7 [58.5, 66.8] | 65.0 [61.1, 69.0] | +2.3 [+0.6, +4.1] | 0.0086 |
| `max_k_shown` | 1688 | ESCO precision (%) | 9.6 [8.0, 11.4] | 11.4 [9.5, 13.6] | +1.8 [+1.1, +2.6] | < 0.0001 |
| `max_k_shown` | 1688 | ESCO recall (%) | 57.2 [52.3, 62.2] | 56.0 [51.3, 60.8] | -1.2 [-2.8, +0.4] | 0.1478 |
| `max_k_shown` | 1688 | Top-20 concepts not in the true items' top 20 | 15 [12, 18] | 14 [11, 18] | -1 [-2, +1] | 1.0000 |
| `min_k_shown` | 1688 | False ESCO concepts per ad | 7.07 [6.42, 7.75] | 8.06 [7.44, 8.71] | +0.99 [+0.46, +1.54] | 0.0004 |
| `min_k_shown` | 1688 | Ads with at least one false concept (%) | 62.7 [58.5, 66.8] | 81.7 [78.6, 84.7] | +19.0 [+16.4, +21.8] | < 0.0001 |
| `min_k_shown` | 1688 | ESCO precision (%) | 9.6 [8.0, 11.4] | 9.0 [7.6, 10.6] | -0.6 [-1.4, +0.2] | 0.1282 |
| `min_k_shown` | 1688 | ESCO recall (%) | 57.2 [52.3, 62.2] | 61.1 [56.3, 65.8] | +3.8 [+1.8, +6.0] | 0.0002 |
| `min_k_shown` | 1688 | Top-20 concepts not in the true items' top 20 | 15 [12, 18] | 14 [12, 18] | -1 [-1, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 1688 | False ESCO concepts per ad | 7.07 [6.42, 7.75] | 5.19 [4.70, 5.69] | -1.88 [-2.47, -1.31] | < 0.0001 |
| `min_k_shown_fewer_ok` | 1688 | Ads with at least one false concept (%) | 62.7 [58.5, 66.8] | 54.3 [50.2, 58.5] | -8.4 [-11.1, -5.8] | < 0.0001 |
| `min_k_shown_fewer_ok` | 1688 | ESCO precision (%) | 9.6 [8.0, 11.4] | 11.3 [9.4, 13.5] | +1.7 [+0.7, +2.8] | 0.0006 |
| `min_k_shown_fewer_ok` | 1688 | ESCO recall (%) | 57.2 [52.3, 62.2] | 50.5 [46.2, 54.8] | -6.8 [-9.1, -4.5] | < 0.0001 |
| `min_k_shown_fewer_ok` | 1688 | Top-20 concepts not in the true items' top 20 | 15 [12, 18] | 14 [11, 18] | -1 [-3, +1] | 0.9092 |
| `min_k_enforced` | 1688 | False ESCO concepts per ad | 7.07 [6.42, 7.75] | 5.61 [5.25, 6.00] | -1.46 [-2.07, -0.88] | < 0.0001 |
| `min_k_enforced` | 1688 | Ads with at least one false concept (%) | 62.7 [58.5, 66.8] | 98.8 [98.1, 99.4] | +36.1 [+32.2, +40.1] | < 0.0001 |
| `min_k_enforced` | 1688 | ESCO precision (%) | 9.6 [8.0, 11.4] | 13.2 [11.2, 15.4] | +3.6 [+2.6, +4.7] | < 0.0001 |
| `min_k_enforced` | 1688 | ESCO recall (%) | 57.2 [52.3, 62.2] | 65.0 [60.3, 69.7] | +7.8 [+5.3, +10.4] | < 0.0001 |
| `min_k_enforced` | 1688 | Top-20 concepts not in the true items' top 20 | 15 [12, 18] | 14 [11, 18] | -1 [-3, +2] | 1.0000 |
| `min_k_escape` | 1688 | False ESCO concepts per ad | 7.07 [6.42, 7.75] | 3.61 [3.32, 3.91] | -3.47 [-4.08, -2.89] | < 0.0001 |
| `min_k_escape` | 1688 | Ads with at least one false concept (%) | 62.7 [58.5, 66.8] | 58.3 [53.7, 63.0] | -4.4 [-7.8, -1.1] | 0.0096 |
| `min_k_escape` | 1688 | ESCO precision (%) | 9.6 [8.0, 11.4] | 16.1 [13.8, 18.4] | +6.5 [+5.3, +7.7] | < 0.0001 |
| `min_k_escape` | 1688 | ESCO recall (%) | 57.2 [52.3, 62.2] | 52.7 [48.2, 57.3] | -4.5 [-7.2, -2.0] | 0.0008 |
| `min_k_escape` | 1688 | Top-20 concepts not in the true items' top 20 | 15 [12, 18] | 14 [10, 17] | -1 [-4, +1] | 0.3642 |

## 65. Qwen3.5-0.8B (main model alone; not registered), both sets, cutoff none

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 11.75 [10.18, 13.40] | 9.22 [8.39, 10.15] | -2.54 [-3.79, -1.33] | < 0.0001 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 90.0 [84.3, 95.0] | 99.6 [99.1, 100.0] | +9.6 [+4.6, +15.3] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 4.8 [3.7, 6.1] | 6.0 [4.7, 7.3] | +1.1 [+0.4, +1.9] | 0.0024 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 45.5 [38.4, 52.8] | 44.6 [38.6, 50.8] | -0.9 [-6.5, +5.0] | 0.7668 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 14 [14, 19] | 15 [14, 19] | +1 [-2, +1] | 1.0000 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 11.75 [10.18, 13.40] | 8.50 [7.62, 9.49] | -3.25 [-4.55, -2.02] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 90.0 [84.3, 95.0] | 96.4 [94.8, 97.8] | +6.4 [+2.2, +11.0] | 0.0016 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 4.8 [3.7, 6.1] | 6.5 [5.1, 8.1] | +1.7 [+0.8, +2.6] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 45.5 [38.4, 52.8] | 45.3 [39.2, 51.5] | -0.2 [-6.3, +5.9] | 0.9330 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 14 [14, 19] | 14 [13, 19] | +0 [-3, +1] | 1.0000 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 11.75 [10.18, 13.40] | 11.84 [10.25, 13.51] | +0.09 [-0.86, +1.03] | 0.8640 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 90.0 [84.3, 95.0] | 89.6 [84.1, 94.5] | -0.5 [-2.8, +2.1] | 0.8046 |
| `max_k_shown` | 211 | ESCO precision (%) | 4.8 [3.7, 6.1] | 4.8 [3.8, 6.1] | +0.0 [-0.4, +0.5] | 0.9944 |
| `max_k_shown` | 211 | ESCO recall (%) | 45.5 [38.4, 52.8] | 45.8 [39.2, 52.8] | +0.4 [-2.5, +3.3] | 0.9094 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 14 [14, 19] | 14 [14, 19] | +0 [-2, +1] | 1.0000 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 11.75 [10.18, 13.40] | 11.56 [9.80, 13.50] | -0.19 [-1.45, +1.09] | 0.7630 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 90.0 [84.3, 95.0] | 77.7 [71.6, 83.4] | -12.3 [-17.8, -7.1] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 4.8 [3.7, 6.1] | 4.8 [3.6, 6.1] | -0.1 [-0.8, +0.7] | 0.8354 |
| `min_k_shown` | 211 | ESCO recall (%) | 45.5 [38.4, 52.8] | 44.0 [36.7, 51.4] | -1.4 [-6.6, +4.2] | 0.6206 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 14 [14, 19] | 15 [14, 19] | +1 [-2, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 11.75 [10.18, 13.40] | 12.09 [10.76, 13.50] | +0.34 [-0.91, +1.66] | 0.6108 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 90.0 [84.3, 95.0] | 99.1 [97.6, 100.0] | +9.0 [+3.7, +15.0] | 0.0006 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 4.8 [3.7, 6.1] | 5.1 [3.9, 6.4] | +0.2 [-0.6, +1.0] | 0.5886 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 45.5 [38.4, 52.8] | 49.1 [41.6, 56.4] | +3.6 [-2.8, +10.4] | 0.3044 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 14 [14, 19] | 15 [13, 19] | +1 [-2, +1] | 1.0000 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 11.75 [10.18, 13.40] | 10.00 [9.05, 11.13] | -1.75 [-3.32, -0.20] | 0.0248 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 90.0 [84.3, 95.0] | 99.1 [97.0, 100.0] | +9.0 [+3.5, +15.1] | 0.0022 |
| `min_k_enforced` | 211 | ESCO precision (%) | 4.8 [3.7, 6.1] | 5.3 [4.1, 6.7] | +0.5 [-0.5, +1.5] | 0.3364 |
| `min_k_enforced` | 211 | ESCO recall (%) | 45.5 [38.4, 52.8] | 43.0 [35.0, 50.6] | -2.5 [-10.3, +4.8] | 0.5438 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 14 [14, 19] | 15 [14, 19] | +1 [-2, +3] | 1.0000 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 11.75 [10.18, 13.40] | 9.71 [8.72, 10.86] | -2.04 [-3.58, -0.51] | 0.0050 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 90.0 [84.3, 95.0] | 99.1 [97.0, 100.0] | +9.0 [+3.5, +15.1] | 0.0022 |
| `min_k_escape` | 211 | ESCO precision (%) | 4.8 [3.7, 6.1] | 6.0 [4.7, 7.4] | +1.2 [+0.2, +2.1] | 0.0234 |
| `min_k_escape` | 211 | ESCO recall (%) | 45.5 [38.4, 52.8] | 47.3 [39.8, 54.7] | +1.8 [-6.1, +9.6] | 0.6924 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 14 [14, 19] | 16 [14, 19] | +2 [-2, +2] | 1.0000 |

## 66. Qwen3.5-2B (main model alone; not registered), both sets, cutoff none

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 29.19 [25.31, 33.35] | 13.83 [12.39, 15.38] | -15.36 [-19.12, -11.76] | < 0.0001 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 99.1 [97.0, 100.0] | 100.0 [100.0, 100.0] | +0.9 [+0.0, +3.0] | 0.7266 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 2.5 [2.0, 3.2] | 4.5 [3.6, 5.4] | +1.9 [+1.4, +2.6] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 57.4 [49.8, 64.5] | 49.1 [42.2, 56.0] | -8.3 [-13.2, -3.4] | 0.0010 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 16 [16, 20] | 16 [14, 19] | +0 [-4, +1] | 0.5798 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 29.19 [25.31, 33.35] | 12.24 [10.71, 13.84] | -16.95 [-20.94, -13.16] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 99.1 [97.0, 100.0] | 99.2 [98.2, 100.0] | +0.2 [-1.3, +2.2] | 1.0000 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 2.5 [2.0, 3.2] | 4.9 [3.9, 6.1] | +2.4 [+1.7, +3.3] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 57.4 [49.8, 64.5] | 48.5 [41.5, 55.4] | -8.9 [-13.9, -3.8] | 0.0010 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 16 [16, 20] | 15 [14, 19] | -1 [-4, +1] | 0.5842 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 29.19 [25.31, 33.35] | 24.00 [21.00, 27.16] | -5.18 [-8.37, -2.04] | 0.0008 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 99.1 [97.0, 100.0] | 99.5 [98.5, 100.0] | +0.5 [-1.4, +2.9] | 0.9274 |
| `max_k_shown` | 211 | ESCO precision (%) | 2.5 [2.0, 3.2] | 3.0 [2.4, 3.8] | +0.5 [+0.1, +0.9] | 0.0068 |
| `max_k_shown` | 211 | ESCO recall (%) | 57.4 [49.8, 64.5] | 57.0 [49.6, 64.2] | -0.4 [-4.3, +3.9] | 0.9090 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 16 [16, 20] | 16 [15, 19] | +0 [-2, +1] | 1.0000 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 29.19 [25.31, 33.35] | 31.20 [27.82, 34.84] | +2.01 [-1.90, +5.92] | 0.3148 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 99.1 [97.0, 100.0] | 100.0 [100.0, 100.0] | +0.9 [+0.0, +3.0] | 0.7266 |
| `min_k_shown` | 211 | ESCO precision (%) | 2.5 [2.0, 3.2] | 2.3 [1.8, 2.8] | -0.3 [-0.7, +0.1] | 0.1514 |
| `min_k_shown` | 211 | ESCO recall (%) | 57.4 [49.8, 64.5] | 54.9 [47.1, 62.3] | -2.5 [-7.9, +2.8] | 0.3982 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 16 [16, 20] | 18 [16, 20] | +2 [-1, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 29.19 [25.31, 33.35] | 21.36 [18.36, 24.55] | -7.83 [-12.21, -3.54] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 99.1 [97.0, 100.0] | 98.1 [95.6, 100.0] | -0.9 [-2.4, +0.0] | 0.2706 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 2.5 [2.0, 3.2] | 3.7 [3.0, 4.6] | +1.2 [+0.6, +1.8] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 57.4 [49.8, 64.5] | 62.8 [56.2, 69.3] | +5.4 [-0.4, +11.5] | 0.0790 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 16 [16, 20] | 16 [15, 19] | +0 [-3, +1] | 0.7266 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 29.19 [25.31, 33.35] | 8.60 [7.85, 9.38] | -20.59 [-24.73, -16.83] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 99.1 [97.0, 100.0] | 99.5 [98.5, 100.0] | +0.5 [-1.4, +2.9] | 0.9392 |
| `min_k_enforced` | 211 | ESCO precision (%) | 2.5 [2.0, 3.2] | 7.7 [6.2, 9.5] | +5.2 [+4.0, +6.6] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO recall (%) | 57.4 [49.8, 64.5] | 54.9 [47.5, 62.4] | -2.5 [-8.5, +3.9] | 0.4758 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 16 [16, 20] | 16 [14, 19] | +0 [-4, +1] | 0.4472 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 29.19 [25.31, 33.35] | 7.30 [6.53, 8.11] | -21.89 [-26.08, -18.05] | < 0.0001 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 99.1 [97.0, 100.0] | 91.5 [86.1, 96.1] | -7.6 [-12.8, -3.3] | 0.0004 |
| `min_k_escape` | 211 | ESCO precision (%) | 2.5 [2.0, 3.2] | 9.7 [8.0, 11.7] | +7.2 [+5.7, +8.9] | < 0.0001 |
| `min_k_escape` | 211 | ESCO recall (%) | 57.4 [49.8, 64.5] | 59.9 [53.1, 66.8] | +2.5 [-3.5, +9.0] | 0.4484 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 16 [16, 20] | 14 [13, 18] | -2 [-5, +1] | 0.2450 |

## 67. Qwen3.5-9B (main model alone; not registered), both sets, cutoff none

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 2.46 [1.80, 3.24] | 1.71 [1.35, 2.12] | -0.76 [-1.19, -0.36] | 0.0004 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 41.7 [34.0, 49.8] | 52.3 [45.8, 58.7] | +10.6 [+5.3, +16.0] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 19.1 [14.2, 25.3] | 26.9 [21.0, 33.5] | +7.8 [+4.7, +10.8] | 0.0002 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 44.4 [35.4, 53.5] | 48.0 [40.5, 55.5] | +3.6 [-2.4, +9.5] | 0.2414 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 14 [12, 19] | 12 [10, 17] | -2 [-5, +1] | 0.2970 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 2.46 [1.80, 3.24] | 1.72 [1.42, 2.05] | -0.75 [-1.24, -0.30] | 0.0006 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 41.7 [34.0, 49.8] | 55.5 [48.6, 62.2] | +13.7 [+8.4, +19.3] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 19.1 [14.2, 25.3] | 25.3 [20.1, 31.0] | +6.1 [+2.8, +9.0] | 0.0016 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 44.4 [35.4, 53.5] | 44.3 [37.0, 51.8] | -0.1 [-6.1, +5.8] | 0.9854 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 14 [12, 19] | 14 [10, 17] | +0 [-5, +1] | 0.3658 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 2.46 [1.80, 3.24] | 2.00 [1.43, 2.68] | -0.46 [-0.74, -0.20] | 0.0004 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 41.7 [34.0, 49.8] | 47.4 [39.6, 54.9] | +5.7 [+1.0, +10.8] | 0.0256 |
| `max_k_shown` | 211 | ESCO precision (%) | 19.1 [14.2, 25.3] | 22.9 [16.7, 30.5] | +3.7 [+1.1, +7.0] | 0.0040 |
| `max_k_shown` | 211 | ESCO recall (%) | 44.4 [35.4, 53.5] | 45.1 [36.3, 53.9] | +0.7 [-3.6, +5.5] | 0.8170 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 14 [12, 19] | 15 [12, 19] | +1 [-3, +2] | 1.0000 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 2.46 [1.80, 3.24] | 2.97 [2.31, 3.72] | +0.51 [+0.17, +0.89] | 0.0024 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 41.7 [34.0, 49.8] | 55.0 [47.7, 62.3] | +13.3 [+6.8, +20.2] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 19.1 [14.2, 25.3] | 18.5 [14.2, 23.6] | -0.7 [-3.8, +1.8] | 0.6088 |
| `min_k_shown` | 211 | ESCO recall (%) | 44.4 [35.4, 53.5] | 51.3 [42.4, 60.1] | +6.9 [+1.6, +12.3] | 0.0126 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 14 [12, 19] | 14 [12, 19] | +0 [-2, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 2.46 [1.80, 3.24] | 1.89 [1.22, 2.67] | -0.57 [-0.88, -0.27] | 0.0002 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 41.7 [34.0, 49.8] | 28.4 [21.2, 35.9] | -13.3 [-19.6, -7.4] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 19.1 [14.2, 25.3] | 16.9 [11.3, 24.8] | -2.3 [-5.8, +2.1] | 0.2960 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 44.4 [35.4, 53.5] | 29.2 [20.9, 37.6] | -15.2 [-23.0, -7.7] | 0.0002 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 14 [12, 19] | 15 [13, 20] | +1 [-2, +4] | 0.6118 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 2.46 [1.80, 3.24] | 4.82 [3.92, 6.18] | +2.35 [+1.17, +3.85] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 41.7 [34.0, 49.8] | 99.5 [98.5, 100.0] | +57.8 [+49.8, +65.6] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 19.1 [14.2, 25.3] | 17.1 [13.1, 21.8] | -2.0 [-8.2, +3.4] | 0.4972 |
| `min_k_enforced` | 211 | ESCO recall (%) | 44.4 [35.4, 53.5] | 75.8 [69.0, 82.5] | +31.4 [+21.8, +41.3] | < 0.0001 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 14 [12, 19] | 16 [12, 18] | +2 [-4, +3] | 0.9806 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 2.46 [1.80, 3.24] | 1.82 [1.41, 2.24] | -0.64 [-1.25, -0.15] | 0.0094 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 41.7 [34.0, 49.8] | 41.7 [33.8, 49.8] | +0.0 [-8.0, +8.1] | 1.0000 |
| `min_k_escape` | 211 | ESCO precision (%) | 19.1 [14.2, 25.3] | 26.0 [20.6, 32.1] | +6.9 [+2.3, +11.5] | 0.0042 |
| `min_k_escape` | 211 | ESCO recall (%) | 44.4 [35.4, 53.5] | 48.7 [39.8, 57.5] | +4.3 [-3.1, +11.7] | 0.2634 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 14 [12, 19] | 13 [10, 17] | -1 [-5, +1] | 0.4082 |

## 68. Qwen3.5-27B (main model alone; not registered), both sets, cutoff none

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 1.03 [0.73, 1.36] | 0.84 [0.65, 1.04] | -0.19 [-0.41, +0.02] | 0.0846 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 40.8 [32.5, 49.1] | 42.6 [34.9, 50.4] | +1.8 [-2.9, +6.6] | 0.4622 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 44.4 [36.1, 54.0] | 51.4 [44.5, 58.9] | +7.0 [+0.4, +13.2] | 0.0386 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 62.5 [54.3, 70.7] | 67.8 [60.9, 74.6] | +5.3 [-0.4, +11.5] | 0.0680 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 12 [8, 16] | 9 [6, 13] | -3 [-6, +2] | 0.4338 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 1.03 [0.73, 1.36] | 1.34 [1.14, 1.54] | +0.31 [+0.07, +0.53] | 0.0106 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 40.8 [32.5, 49.1] | 55.5 [48.6, 62.4] | +14.7 [+9.6, +20.2] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 44.4 [36.1, 54.0] | 39.8 [34.8, 45.0] | -4.5 [-11.7, +1.3] | 0.1320 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 62.5 [54.3, 70.7] | 67.4 [61.4, 73.3] | +4.9 [-0.7, +10.9] | 0.0898 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 12 [8, 16] | 13 [8, 15] | +1 [-4, +4] | 1.0000 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 1.03 [0.73, 1.36] | 0.89 [0.70, 1.09] | -0.14 [-0.33, +0.04] | 0.1472 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 40.8 [32.5, 49.1] | 46.4 [38.1, 54.8] | +5.7 [+2.4, +9.6] | < 0.0001 |
| `max_k_shown` | 211 | ESCO precision (%) | 44.4 [36.1, 54.0] | 48.8 [41.8, 56.2] | +4.4 [-1.0, +9.1] | 0.1112 |
| `max_k_shown` | 211 | ESCO recall (%) | 62.5 [54.3, 70.7] | 64.6 [57.3, 71.9] | +2.2 [-2.6, +7.8] | 0.4942 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 12 [8, 16] | 12 [7, 14] | +0 [-5, +2] | 0.5948 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 1.03 [0.73, 1.36] | 2.80 [2.50, 3.09] | +1.77 [+1.42, +2.12] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 40.8 [32.5, 49.1] | 82.5 [75.7, 88.6] | +41.7 [+33.0, +50.7] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 44.4 [36.1, 54.0] | 25.6 [21.8, 29.5] | -18.8 [-27.2, -11.8] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 62.5 [54.3, 70.7] | 73.3 [66.9, 79.4] | +10.8 [+4.3, +18.1] | 0.0010 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 12 [8, 16] | 13 [11, 17] | +1 [-1, +7] | 0.3532 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 1.03 [0.73, 1.36] | 1.55 [1.30, 1.81] | +0.52 [+0.28, +0.76] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 40.8 [32.5, 49.1] | 60.7 [53.1, 68.3] | +19.9 [+13.2, +27.1] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 44.4 [36.1, 54.0] | 36.1 [31.0, 41.5] | -8.2 [-15.2, -2.7] | 0.0030 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 62.5 [54.3, 70.7] | 66.8 [60.0, 73.5] | +4.3 [-1.8, +10.9] | 0.2008 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 12 [8, 16] | 14 [9, 16] | +2 [-2, +5] | 0.8010 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 1.03 [0.73, 1.36] | 3.36 [3.16, 3.57] | +2.34 [+2.04, +2.61] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 40.8 [32.5, 49.1] | 99.1 [97.6, 100.0] | +58.3 [+50.2, +66.7] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 44.4 [36.1, 54.0] | 22.4 [19.1, 25.9] | -22.0 [-30.3, -15.1] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO recall (%) | 62.5 [54.3, 70.7] | 74.0 [67.9, 80.0] | +11.6 [+5.0, +18.8] | < 0.0001 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 12 [8, 16] | 14 [11, 17] | +2 [-1, +7] | 0.2842 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 1.03 [0.73, 1.36] | 1.57 [1.31, 1.84] | +0.55 [+0.26, +0.82] | 0.0006 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 40.8 [32.5, 49.1] | 58.8 [50.5, 66.8] | +18.0 [+11.2, +25.6] | < 0.0001 |
| `min_k_escape` | 211 | ESCO precision (%) | 44.4 [36.1, 54.0] | 37.4 [32.8, 42.3] | -7.0 [-14.3, -0.8] | 0.0274 |
| `min_k_escape` | 211 | ESCO recall (%) | 62.5 [54.3, 70.7] | 71.5 [64.9, 78.1] | +9.0 [+2.2, +16.5] | 0.0084 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 12 [8, 16] | 11 [8, 15] | -1 [-4, +4] | 1.0000 |

## 69. Gemma 4 31B (main model alone; not registered), both sets, cutoff none

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 0.49 [0.32, 0.69] | 0.51 [0.37, 0.67] | +0.02 [-0.08, +0.11] | 0.7120 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 28.4 [20.5, 36.8] | 32.0 [24.2, 40.1] | +3.6 [-0.8, +8.3] | 0.1226 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 64.3 [55.1, 74.3] | 63.7 [55.9, 71.7] | -0.6 [-5.8, +4.1] | 0.7976 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 67.5 [60.6, 74.7] | 68.2 [61.7, 74.7] | +0.6 [-2.3, +3.6] | 0.6962 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 9 [4, 13] | 9 [4, 11] | +0 [-4, +2] | 0.9552 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 0.49 [0.32, 0.69] | 1.59 [1.39, 1.79] | +1.09 [+0.91, +1.28] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 28.4 [20.5, 36.8] | 62.3 [55.7, 68.7] | +33.8 [+27.2, +40.9] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 64.3 [55.1, 74.3] | 38.8 [33.8, 44.0] | -25.5 [-33.9, -18.0] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 67.5 [60.6, 74.7] | 76.5 [70.6, 82.3] | +9.0 [+4.7, +13.5] | < 0.0001 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 9 [4, 13] | 14 [7, 15] | +5 [-2, +7] | 0.3256 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 0.49 [0.32, 0.69] | 0.46 [0.32, 0.62] | -0.03 [-0.12, +0.05] | 0.5828 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 28.4 [20.5, 36.8] | 28.9 [21.2, 37.1] | +0.5 [-3.3, +4.2] | 0.9004 |
| `max_k_shown` | 211 | ESCO precision (%) | 64.3 [55.1, 74.3] | 66.1 [58.4, 74.3] | +1.8 [-2.7, +6.4] | 0.4634 |
| `max_k_shown` | 211 | ESCO recall (%) | 67.5 [60.6, 74.7] | 69.0 [62.1, 75.7] | +1.4 [-1.8, +4.6] | 0.4462 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 9 [4, 13] | 8 [4, 11] | -1 [-4, +1] | 0.8434 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 0.49 [0.32, 0.69] | 2.98 [2.72, 3.24] | +2.48 [+2.19, +2.77] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 28.4 [20.5, 36.8] | 90.0 [84.9, 94.6] | +61.6 [+53.1, +70.1] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 64.3 [55.1, 74.3] | 25.4 [21.4, 29.7] | -38.8 [-48.0, -30.6] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 67.5 [60.6, 74.7] | 77.3 [71.3, 83.3] | +9.7 [+5.0, +14.9] | < 0.0001 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 9 [4, 13] | 15 [11, 17] | +6 [+1, +11] | 0.0318 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 0.49 [0.32, 0.69] | 0.45 [0.30, 0.63] | -0.04 [-0.17, +0.08] | 0.6142 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 28.4 [20.5, 36.8] | 26.1 [18.4, 33.8] | -2.4 [-8.8, +3.7] | 0.5050 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 64.3 [55.1, 74.3] | 66.7 [58.8, 75.2] | +2.4 [-3.3, +9.1] | 0.4670 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 67.5 [60.6, 74.7] | 69.3 [62.2, 76.4] | +1.8 [-1.6, +5.3] | 0.3598 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 9 [4, 13] | 8 [5, 12] | -1 [-4, +2] | 1.0000 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 0.49 [0.32, 0.69] | 3.19 [3.02, 3.38] | +2.70 [+2.45, +2.94] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 28.4 [20.5, 36.8] | 99.5 [98.5, 100.0] | +71.1 [+62.8, +79.1] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 64.3 [55.1, 74.3] | 24.2 [20.7, 27.9] | -40.1 [-49.3, -31.7] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO recall (%) | 67.5 [60.6, 74.7] | 77.6 [71.7, 83.5] | +10.1 [+5.3, +15.1] | < 0.0001 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 9 [4, 13] | 15 [12, 18] | +6 [+1, +11] | 0.0224 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 0.49 [0.32, 0.69] | 0.83 [0.61, 1.07] | +0.34 [+0.13, +0.54] | 0.0020 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 28.4 [20.5, 36.8] | 34.6 [26.4, 43.1] | +6.2 [-1.4, +13.8] | 0.1350 |
| `min_k_escape` | 211 | ESCO precision (%) | 64.3 [55.1, 74.3] | 51.1 [44.7, 58.7] | -13.2 [-21.4, -4.9] | 0.0026 |
| `min_k_escape` | 211 | ESCO recall (%) | 67.5 [60.6, 74.7] | 66.4 [59.0, 73.5] | -1.1 [-7.5, +4.7] | 0.7734 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 9 [4, 13] | 13 [7, 13] | +4 [-2, +5] | 0.6038 |

## 70. Olmo 3.1 32B (main model alone; not registered), both sets, cutoff none

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 5.04 [4.09, 6.06] | 2.80 [2.44, 3.16] | -2.24 [-3.06, -1.52] | < 0.0001 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 64.0 [55.8, 72.4] | 72.6 [65.9, 79.2] | +8.6 [+3.2, +14.1] | 0.0016 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 12.4 [9.8, 15.5] | 18.3 [15.0, 21.9] | +6.0 [+3.8, +8.1] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 54.2 [46.6, 61.6] | 47.8 [41.1, 54.6] | -6.4 [-11.2, -1.4] | 0.0114 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 15 [13, 19] | 14 [12, 18] | -1 [-4, +2] | 0.6668 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 5.04 [4.09, 6.06] | 2.57 [2.34, 2.80] | -2.47 [-3.37, -1.66] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 64.0 [55.8, 72.4] | 77.7 [72.3, 83.1] | +13.7 [+8.3, +19.3] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 12.4 [9.8, 15.5] | 19.4 [16.1, 22.9] | +7.1 [+4.7, +9.4] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 54.2 [46.6, 61.6] | 47.2 [40.9, 53.7] | -6.9 [-12.6, -1.3] | 0.0178 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 15 [13, 19] | 14 [12, 18] | -1 [-4, +2] | 0.6700 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 5.04 [4.09, 6.06] | 2.18 [1.83, 2.57] | -2.86 [-3.74, -2.06] | < 0.0001 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 64.0 [55.8, 72.4] | 63.0 [54.8, 71.6] | -0.9 [-6.1, +4.1] | 0.7940 |
| `max_k_shown` | 211 | ESCO precision (%) | 12.4 [9.8, 15.5] | 21.6 [17.5, 26.2] | +9.3 [+6.4, +12.4] | < 0.0001 |
| `max_k_shown` | 211 | ESCO recall (%) | 54.2 [46.6, 61.6] | 45.8 [38.8, 53.1] | -8.3 [-13.9, -2.4] | 0.0066 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 15 [13, 19] | 15 [12, 18] | +0 [-4, +2] | 0.7472 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 5.04 [4.09, 6.06] | 5.03 [4.21, 5.96] | -0.00 [-0.47, +0.48] | 0.9872 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 64.0 [55.8, 72.4] | 74.9 [67.6, 82.2] | +10.9 [+6.0, +16.1] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 12.4 [9.8, 15.5] | 13.1 [10.5, 16.2] | +0.7 [-0.7, +2.0] | 0.2906 |
| `min_k_shown` | 211 | ESCO recall (%) | 54.2 [46.6, 61.6] | 57.8 [50.2, 65.4] | +3.6 [-1.2, +8.8] | 0.1680 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 15 [13, 19] | 15 [13, 19] | +0 [-2, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 5.04 [4.09, 6.06] | 0.80 [0.48, 1.17] | -4.24 [-5.20, -3.38] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 64.0 [55.8, 72.4] | 19.4 [12.8, 26.7] | -44.5 [-53.1, -36.7] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 12.4 [9.8, 15.5] | 25.9 [18.3, 36.2] | +13.5 [+6.7, +22.8] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 54.2 [46.6, 61.6] | 21.3 [14.3, 28.6] | -32.9 [-41.5, -24.1] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 15 [13, 19] | 15 [12, 18] | +0 [-4, +2] | 0.7476 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 5.04 [4.09, 6.06] | 6.93 [6.14, 7.84] | +1.90 [+1.13, +2.75] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 64.0 [55.8, 72.4] | 100.0 [100.0, 100.0] | +36.0 [+27.6, +44.2] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 12.4 [9.8, 15.5] | 10.7 [8.6, 13.0] | -1.7 [-3.8, -0.0] | 0.0438 |
| `min_k_enforced` | 211 | ESCO recall (%) | 54.2 [46.6, 61.6] | 63.2 [56.1, 70.4] | +9.0 [+3.6, +14.8] | 0.0006 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 15 [13, 19] | 14 [13, 19] | -1 [-2, +2] | 1.0000 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 5.04 [4.09, 6.06] | 4.53 [3.73, 5.40] | -0.51 [-1.40, +0.34] | 0.2432 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 64.0 [55.8, 72.4] | 64.0 [55.4, 72.6] | +0.0 [-9.0, +8.7] | 1.0000 |
| `min_k_escape` | 211 | ESCO precision (%) | 12.4 [9.8, 15.5] | 13.7 [11.2, 16.6] | +1.4 [-0.7, +3.4] | 0.1860 |
| `min_k_escape` | 211 | ESCO recall (%) | 54.2 [46.6, 61.6] | 54.9 [47.3, 62.5] | +0.7 [-5.1, +6.7] | 0.8530 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 15 [13, 19] | 14 [13, 18] | -1 [-3, +2] | 1.0000 |

## 71. Ministral 3 14B (main model alone; not registered), both sets, cutoff none

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 4.15 [3.28, 5.05] | 2.49 [2.23, 2.75] | -1.66 [-2.42, -0.96] | < 0.0001 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 74.9 [67.3, 82.3] | 83.9 [78.8, 88.6] | +9.0 [+3.3, +15.1] | 0.0010 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 16.8 [13.2, 21.6] | 23.2 [19.2, 27.5] | +6.4 [+3.3, +9.1] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 63.9 [56.3, 71.5] | 57.3 [50.3, 64.1] | -6.6 [-12.6, -0.9] | 0.0272 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 15 [10, 17] | -1 [-6, +1] | 0.2704 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 4.15 [3.28, 5.05] | 2.63 [2.41, 2.86] | -1.51 [-2.28, -0.79] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 74.9 [67.3, 82.3] | 85.3 [80.5, 89.9] | +10.4 [+5.5, +15.7] | 0.0002 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 16.8 [13.2, 21.6] | 22.9 [19.2, 26.7] | +6.0 [+2.9, +8.6] | 0.0002 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 63.9 [56.3, 71.5] | 59.5 [52.8, 66.3] | -4.4 [-10.5, +0.9] | 0.1120 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 15 [11, 17] | -1 [-6, +1] | 0.3270 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 4.15 [3.28, 5.05] | 2.06 [1.67, 2.48] | -2.09 [-2.81, -1.43] | < 0.0001 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 74.9 [67.3, 82.3] | 66.4 [58.4, 74.1] | -8.5 [-14.3, -2.9] | 0.0026 |
| `max_k_shown` | 211 | ESCO precision (%) | 16.8 [13.2, 21.6] | 27.9 [22.7, 34.0] | +11.1 [+7.9, +14.6] | < 0.0001 |
| `max_k_shown` | 211 | ESCO recall (%) | 63.9 [56.3, 71.5] | 60.6 [53.1, 68.3] | -3.2 [-6.9, +0.0] | 0.0720 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 16 [11, 17] | +0 [-5, +1] | 0.3614 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 4.15 [3.28, 5.05] | 4.41 [3.77, 5.11] | +0.26 [-0.30, +0.73] | 0.3282 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 74.9 [67.3, 82.3] | 85.8 [79.9, 91.3] | +10.9 [+5.9, +16.4] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 16.8 [13.2, 21.6] | 15.9 [12.8, 19.5] | -0.9 [-3.2, +1.1] | 0.3550 |
| `min_k_shown` | 211 | ESCO recall (%) | 63.9 [56.3, 71.5] | 63.5 [56.1, 70.9] | -0.4 [-5.2, +4.8] | 0.9142 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 17 [12, 18] | +1 [-3, +2] | 0.9124 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 4.15 [3.28, 5.05] | 0.63 [0.42, 0.87] | -3.52 [-4.42, -2.67] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 74.9 [67.3, 82.3] | 30.3 [22.4, 38.8] | -44.5 [-53.8, -35.2] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 16.8 [13.2, 21.6] | 49.0 [40.2, 58.7] | +32.2 [+24.0, +41.4] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 63.9 [56.3, 71.5] | 45.8 [37.3, 54.5] | -18.1 [-25.6, -11.2] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 12 [8, 15] | -4 [-9, -1] | 0.0304 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 4.15 [3.28, 5.05] | 4.19 [3.73, 4.75] | +0.05 [-0.60, +0.68] | 0.9004 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 74.9 [67.3, 82.3] | 99.1 [97.6, 100.0] | +24.2 [+16.7, +31.9] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 16.8 [13.2, 21.6] | 16.7 [13.7, 20.1] | -0.1 [-3.0, +2.3] | 0.9486 |
| `min_k_enforced` | 211 | ESCO recall (%) | 63.9 [56.3, 71.5] | 64.3 [57.2, 71.6] | +0.4 [-5.5, +6.2] | 0.9582 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 16 [13, 18] | +0 [-3, +2] | 1.0000 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 4.15 [3.28, 5.05] | 0.51 [0.26, 0.83] | -3.64 [-4.56, -2.77] | < 0.0001 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 74.9 [67.3, 82.3] | 15.6 [9.7, 22.1] | -59.2 [-68.1, -50.2] | < 0.0001 |
| `min_k_escape` | 211 | ESCO precision (%) | 16.8 [13.2, 21.6] | 30.3 [19.4, 45.5] | +13.5 [+2.7, +28.8] | 0.0108 |
| `min_k_escape` | 211 | ESCO recall (%) | 63.9 [56.3, 71.5] | 17.0 [10.6, 23.7] | -46.9 [-56.6, -37.5] | < 0.0001 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 16 [13, 19] | +0 [-4, +4] | 1.0000 |

## 72. gpt-oss-20b (main model alone; not registered), both sets, cutoff none

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 2.47 [1.98, 2.98] | 2.45 [2.23, 2.65] | -0.02 [-0.49, +0.41] | 0.9290 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 62.6 [54.2, 70.8] | 81.5 [76.4, 86.1] | +19.0 [+12.0, +26.2] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 24.9 [20.7, 30.0] | 25.1 [21.5, 29.1] | +0.2 [-3.6, +3.6] | 0.9256 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 62.5 [54.6, 70.2] | 62.5 [56.6, 68.5] | +0.1 [-6.2, +6.9] | 1.0000 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 13 [11, 18] | 13 [10, 16] | +0 [-5, +1] | 0.4930 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 2.47 [1.98, 2.98] | 2.70 [2.52, 2.88] | +0.23 [-0.20, +0.64] | 0.2888 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 62.6 [54.2, 70.8] | 85.2 [81.2, 89.1] | +22.7 [+15.6, +30.0] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 24.9 [20.7, 30.0] | 22.1 [19.0, 25.4] | -2.8 [-6.6, +0.3] | 0.0780 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 62.5 [54.6, 70.2] | 58.3 [52.7, 64.0] | -4.1 [-10.5, +2.6] | 0.2268 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 13 [11, 18] | 14 [10, 17] | +1 [-4, +2] | 0.7202 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 2.47 [1.98, 2.98] | 2.14 [1.89, 2.37] | -0.33 [-0.79, +0.11] | 0.1540 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 62.6 [54.2, 70.8] | 78.7 [71.8, 85.2] | +16.1 [+9.0, +23.6] | < 0.0001 |
| `max_k_shown` | 211 | ESCO precision (%) | 24.9 [20.7, 30.0] | 26.9 [22.5, 31.7] | +2.0 [-2.1, +5.7] | 0.3360 |
| `max_k_shown` | 211 | ESCO recall (%) | 62.5 [54.6, 70.2] | 59.9 [53.0, 67.2] | -2.5 [-8.9, +4.0] | 0.4836 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 13 [11, 18] | 12 [10, 17] | -1 [-4, +2] | 0.9032 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 2.47 [1.98, 2.98] | 3.56 [3.19, 3.94] | +1.09 [+0.69, +1.48] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 62.6 [54.2, 70.8] | 87.7 [82.4, 92.5] | +25.1 [+17.3, +33.0] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 24.9 [20.7, 30.0] | 19.7 [16.7, 22.9] | -5.2 [-8.9, -2.2] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 62.5 [54.6, 70.2] | 66.4 [59.5, 73.5] | +4.0 [-2.5, +11.0] | 0.2628 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 13 [11, 18] | 13 [11, 17] | +0 [-3, +3] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 2.47 [1.98, 2.98] | 2.74 [2.31, 3.20] | +0.27 [-0.16, +0.71] | 0.2352 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 62.6 [54.2, 70.8] | 72.0 [64.6, 79.2] | +9.5 [+0.0, +18.9] | 0.0542 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 24.9 [20.7, 30.0] | 22.1 [18.4, 26.4] | -2.8 [-6.9, +0.7] | 0.1212 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 62.5 [54.6, 70.2] | 59.2 [51.8, 66.8] | -3.2 [-9.8, +3.2] | 0.3502 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 13 [11, 18] | 13 [11, 18] | +0 [-3, +3] | 1.0000 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 2.47 [1.98, 2.98] | 3.76 [3.39, 4.16] | +1.29 [+0.89, +1.68] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 62.6 [54.2, 70.8] | 94.8 [91.1, 98.0] | +32.2 [+24.4, +40.3] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 24.9 [20.7, 30.0] | 19.1 [16.0, 22.4] | -5.9 [-9.5, -2.8] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO recall (%) | 62.5 [54.6, 70.2] | 67.5 [60.5, 74.5] | +5.1 [-2.1, +12.8] | 0.1886 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 13 [11, 18] | 13 [11, 17] | +0 [-3, +2] | 1.0000 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 2.47 [1.98, 2.98] | 2.56 [2.06, 3.10] | +0.09 [-0.36, +0.59] | 0.7102 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 62.6 [54.2, 70.8] | 61.1 [53.0, 69.3] | -1.4 [-9.7, +7.1] | 0.7932 |
| `min_k_escape` | 211 | ESCO precision (%) | 24.9 [20.7, 30.0] | 22.3 [18.2, 27.0] | -2.7 [-6.9, +1.1] | 0.1802 |
| `min_k_escape` | 211 | ESCO recall (%) | 62.5 [54.6, 70.2] | 56.0 [48.1, 63.7] | -6.5 [-14.5, +1.6] | 0.1188 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 13 [11, 18] | 12 [11, 18] | -1 [-3, +3] | 1.0000 |

## 73. GPT-6 Luna (Azure), both sets, cutoff none

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 1.27 [0.94, 1.62] | 1.00 [0.79, 1.21] | -0.27 [-0.50, -0.05] | 0.0162 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 47.9 [38.9, 56.9] | 48.8 [40.6, 57.1] | +0.9 [-5.6, +7.8] | 0.8284 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 39.0 [31.6, 47.9] | 47.5 [40.8, 54.8] | +8.5 [+3.1, +13.5] | 0.0022 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 61.7 [53.8, 69.4] | 68.6 [61.9, 75.4] | +6.9 [+1.1, +12.8] | 0.0236 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 13 [8, 16] | 12 [7, 14] | -1 [-5, +1] | 0.2958 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 1.27 [0.94, 1.62] | 1.88 [1.64, 2.13] | +0.62 [+0.32, +0.92] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 47.9 [38.9, 56.9] | 73.5 [65.9, 80.9] | +25.6 [+18.1, +33.5] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 39.0 [31.6, 47.9] | 33.8 [29.2, 38.8] | -5.2 [-12.3, +0.5] | 0.0740 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 61.7 [53.8, 69.4] | 73.3 [66.7, 79.8] | +11.6 [+5.6, +17.6] | < 0.0001 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 13 [8, 16] | 13 [8, 15] | +0 [-4, +3] | 0.9336 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 1.27 [0.94, 1.62] | 0.85 [0.64, 1.06] | -0.42 [-0.69, -0.18] | 0.0008 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 47.9 [38.9, 56.9] | 39.8 [31.3, 48.3] | -8.1 [-14.7, -1.8] | 0.0162 |
| `max_k_shown` | 211 | ESCO precision (%) | 39.0 [31.6, 47.9] | 47.4 [39.7, 55.7] | +8.3 [+2.2, +14.3] | 0.0056 |
| `max_k_shown` | 211 | ESCO recall (%) | 61.7 [53.8, 69.4] | 58.1 [49.5, 66.5] | -3.6 [-9.5, +1.7] | 0.2184 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 13 [8, 16] | 11 [7, 14] | -2 [-6, +2] | 0.4584 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 1.27 [0.94, 1.62] | 2.17 [1.84, 2.53] | +0.91 [+0.59, +1.25] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 47.9 [38.9, 56.9] | 72.0 [64.4, 79.5] | +24.2 [+16.4, +32.2] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 39.0 [31.6, 47.9] | 30.5 [25.4, 36.1] | -8.5 [-15.1, -3.4] | 0.0004 |
| `min_k_shown` | 211 | ESCO recall (%) | 61.7 [53.8, 69.4] | 72.6 [65.6, 79.3] | +10.8 [+6.2, +15.8] | < 0.0001 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 13 [8, 16] | 12 [9, 16] | -1 [-3, +4] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 1.27 [0.94, 1.62] | 1.96 [1.64, 2.30] | +0.69 [+0.40, +1.02] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 47.9 [38.9, 56.9] | 68.7 [61.0, 76.2] | +20.9 [+13.9, +28.1] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 39.0 [31.6, 47.9] | 31.4 [26.0, 37.4] | -7.6 [-14.0, -2.7] | 0.0016 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 61.7 [53.8, 69.4] | 68.2 [61.4, 74.9] | +6.5 [+1.4, +11.8] | 0.0148 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 13 [8, 16] | 12 [9, 16] | -1 [-3, +4] | 1.0000 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 1.27 [0.94, 1.62] | 3.72 [3.43, 4.02] | +2.45 [+2.12, +2.82] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 47.9 [38.9, 56.9] | 98.6 [96.8, 100.0] | +50.7 [+41.9, +59.6] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 39.0 [31.6, 47.9] | 20.5 [17.2, 24.0] | -18.5 [-25.6, -12.9] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO recall (%) | 61.7 [53.8, 69.4] | 73.3 [66.2, 80.2] | +11.6 [+6.4, +17.2] | < 0.0001 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 13 [8, 16] | 14 [12, 18] | +1 [-1, +6] | 0.3614 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 1.27 [0.94, 1.62] | 2.48 [2.17, 2.80] | +1.21 [+0.92, +1.53] | < 0.0001 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 47.9 [38.9, 56.9] | 81.5 [74.9, 87.7] | +33.6 [+24.9, +42.6] | < 0.0001 |
| `min_k_escape` | 211 | ESCO precision (%) | 39.0 [31.6, 47.9] | 27.1 [22.5, 31.8] | -12.0 [-18.4, -6.9] | < 0.0001 |
| `min_k_escape` | 211 | ESCO recall (%) | 61.7 [53.8, 69.4] | 70.0 [62.6, 77.4] | +8.3 [+2.5, +14.3] | 0.0064 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 13 [8, 16] | 14 [10, 17] | +1 [-2, +5] | 0.7530 |

## 74. GPT-6 Sol (Azure), both sets, cutoff none

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 1.23 [0.94, 1.55] | 0.95 [0.76, 1.16] | -0.28 [-0.51, -0.07] | 0.0074 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 54.0 [45.3, 62.6] | 51.7 [43.3, 60.2] | -2.4 [-8.0, +3.4] | 0.4684 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 42.5 [35.4, 50.1] | 49.2 [42.2, 56.6] | +6.8 [+2.0, +11.1] | 0.0046 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 69.3 [61.4, 77.1] | 70.0 [62.4, 77.5] | +0.7 [-1.6, +2.9] | 0.6530 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 13 [8, 16] | 11 [6, 14] | -2 [-5, +1] | 0.4054 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 1.23 [0.94, 1.55] | 2.73 [2.56, 2.91] | +1.50 [+1.19, +1.80] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 54.0 [45.3, 62.6] | 97.2 [94.3, 99.5] | +43.1 [+34.9, +51.6] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 42.5 [35.4, 50.1] | 26.8 [22.9, 30.6] | -15.7 [-22.4, -10.0] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 69.3 [61.4, 77.1] | 76.2 [69.8, 82.5] | +6.9 [+1.8, +12.0] | 0.0086 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 13 [8, 16] | 15 [11, 17] | +2 [-2, +7] | 0.4084 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 1.23 [0.94, 1.55] | 0.84 [0.67, 1.03] | -0.39 [-0.60, -0.20] | < 0.0001 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 54.0 [45.3, 62.6] | 47.9 [39.6, 56.2] | -6.2 [-11.4, -1.4] | 0.0130 |
| `max_k_shown` | 211 | ESCO precision (%) | 42.5 [35.4, 50.1] | 52.0 [45.2, 59.1] | +9.5 [+5.5, +13.3] | < 0.0001 |
| `max_k_shown` | 211 | ESCO recall (%) | 69.3 [61.4, 77.1] | 69.7 [62.1, 77.1] | +0.4 [-1.5, +2.2] | 0.8476 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 13 [8, 16] | 9 [5, 12] | -4 [-7, +0] | 0.0828 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 1.23 [0.94, 1.55] | 2.22 [1.90, 2.57] | +0.99 [+0.70, +1.31] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 54.0 [45.3, 62.6] | 80.1 [73.7, 86.2] | +26.1 [+18.6, +33.8] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 42.5 [35.4, 50.1] | 30.6 [25.6, 36.0] | -11.9 [-17.8, -6.9] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 69.3 [61.4, 77.1] | 74.7 [68.0, 81.4] | +5.4 [+1.2, +9.7] | 0.0166 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 13 [8, 16] | 14 [10, 17] | +1 [-2, +6] | 0.5732 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 1.23 [0.94, 1.55] | 1.41 [1.13, 1.72] | +0.18 [-0.03, +0.41] | 0.0946 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 54.0 [45.3, 62.6] | 57.8 [49.8, 65.9] | +3.8 [-0.9, +8.7] | 0.1336 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 42.5 [35.4, 50.1] | 40.8 [34.5, 47.4] | -1.7 [-6.4, +2.4] | 0.4168 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 69.3 [61.4, 77.1] | 74.0 [67.1, 80.8] | +4.7 [+0.8, +9.0] | 0.0188 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 13 [8, 16] | 13 [8, 16] | +0 [-3, +3] | 1.0000 |

## 75. DeepSeek V3.2 (Bedrock), both sets, cutoff none

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 1.66 [1.29, 2.05] | 2.04 [1.82, 2.25] | +0.37 [+0.03, +0.71] | 0.0356 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 50.7 [42.1, 59.0] | 72.9 [66.4, 79.1] | +22.2 [+15.5, +29.2] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 33.8 [27.7, 41.0] | 31.1 [26.6, 35.8] | -2.7 [-8.0, +1.6] | 0.2304 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 64.6 [57.0, 72.1] | 69.9 [63.5, 76.3] | +5.3 [+0.1, +10.7] | 0.0482 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 13 [9, 17] | 12 [8, 15] | -1 [-5, +1] | 0.5758 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 1.66 [1.29, 2.05] | 2.35 [2.14, 2.54] | +0.68 [+0.32, +1.04] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 50.7 [42.1, 59.0] | 81.3 [76.0, 86.3] | +30.6 [+23.5, +38.3] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 33.8 [27.7, 41.0] | 27.9 [23.9, 32.0] | -5.9 [-11.4, -1.4] | 0.0094 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 64.6 [57.0, 72.1] | 69.2 [62.8, 75.6] | +4.6 [-0.9, +10.4] | 0.1068 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 13 [9, 17] | 12 [9, 16] | -1 [-4, +2] | 0.8966 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 1.66 [1.29, 2.05] | 1.93 [1.69, 2.16] | +0.27 [-0.08, +0.59] | 0.1248 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 50.7 [42.1, 59.0] | 72.5 [65.2, 79.4] | +21.8 [+15.2, +29.0] | < 0.0001 |
| `max_k_shown` | 211 | ESCO precision (%) | 33.8 [27.7, 41.0] | 32.1 [27.1, 37.2] | -1.7 [-7.0, +2.8] | 0.4558 |
| `max_k_shown` | 211 | ESCO recall (%) | 64.6 [57.0, 72.1] | 69.3 [62.2, 76.3] | +4.7 [-0.8, +10.4] | 0.1124 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 13 [9, 17] | 12 [9, 16] | -1 [-4, +3] | 1.0000 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 1.66 [1.29, 2.05] | 4.57 [4.05, 5.13] | +2.91 [+2.33, +3.54] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 50.7 [42.1, 59.0] | 94.8 [91.1, 97.8] | +44.1 [+35.8, +52.6] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 33.8 [27.7, 41.0] | 17.4 [14.3, 20.9] | -16.4 [-22.5, -11.4] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 64.6 [57.0, 72.1] | 73.3 [66.5, 79.9] | +8.7 [+3.1, +14.4] | 0.0022 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 13 [9, 17] | 15 [12, 18] | +2 [-1, +6] | 0.3190 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 1.66 [1.29, 2.05] | 2.14 [1.78, 2.50] | +0.47 [+0.06, +0.90] | 0.0248 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 50.7 [42.1, 59.0] | 62.6 [54.4, 70.6] | +11.8 [+3.3, +20.5] | 0.0080 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 33.8 [27.7, 41.0] | 28.3 [23.9, 33.2] | -5.5 [-11.9, -0.0] | 0.0480 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 64.6 [57.0, 72.1] | 64.3 [56.9, 71.5] | -0.4 [-6.6, +5.6] | 0.9586 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 13 [9, 17] | 15 [10, 17] | +2 [-3, +4] | 0.9784 |

## 76. gpt-oss-120b (Bedrock), both sets, cutoff none

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 2.00 [1.61, 2.41] | 2.01 [1.81, 2.21] | +0.01 [-0.34, +0.33] | 0.9210 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 66.4 [58.3, 74.2] | 73.4 [67.6, 79.0] | +7.0 [+1.3, +12.9] | 0.0128 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 32.7 [27.4, 38.7] | 29.1 [24.9, 33.3] | -3.7 [-8.0, +0.2] | 0.0598 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 74.0 [67.5, 80.7] | 62.7 [57.1, 68.4] | -11.3 [-16.5, -6.2] | < 0.0001 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 17] | 14 [9, 16] | -1 [-5, +2] | 0.7402 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 2.00 [1.61, 2.41] | 2.70 [2.53, 2.87] | +0.71 [+0.33, +1.05] | 0.0004 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 66.4 [58.3, 74.2] | 85.6 [81.2, 89.6] | +19.2 [+13.0, +25.6] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 32.7 [27.4, 38.7] | 23.1 [19.9, 26.4] | -9.6 [-14.4, -5.6] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 74.0 [67.5, 80.7] | 61.8 [56.5, 67.1] | -12.2 [-17.3, -7.2] | < 0.0001 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 17] | 12 [10, 16] | -3 [-4, +3] | 0.9852 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 2.00 [1.61, 2.41] | 2.12 [1.88, 2.34] | +0.12 [-0.24, +0.47] | 0.5046 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 66.4 [58.3, 74.2] | 75.8 [69.3, 82.2] | +9.5 [+3.6, +15.6] | 0.0022 |
| `max_k_shown` | 211 | ESCO precision (%) | 32.7 [27.4, 38.7] | 28.1 [24.0, 32.6] | -4.6 [-9.3, -0.5] | 0.0262 |
| `max_k_shown` | 211 | ESCO recall (%) | 74.0 [67.5, 80.7] | 63.2 [56.4, 69.9] | -10.8 [-16.6, -5.1] | 0.0002 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 17] | 16 [11, 17] | +1 [-3, +3] | 1.0000 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 2.00 [1.61, 2.41] | 3.52 [3.30, 3.76] | +1.53 [+1.16, +1.89] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 66.4 [58.3, 74.2] | 97.6 [95.0, 99.5] | +31.3 [+23.5, +39.3] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 32.7 [27.4, 38.7] | 19.7 [16.6, 22.8] | -13.1 [-18.0, -8.9] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 74.0 [67.5, 80.7] | 65.7 [59.2, 71.9] | -8.3 [-14.6, -2.0] | 0.0110 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 17] | 17 [11, 17] | +2 [-3, +4] | 0.8656 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 2.00 [1.61, 2.41] | 2.45 [2.12, 2.81] | +0.46 [+0.16, +0.78] | 0.0020 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 66.4 [58.3, 74.2] | 77.7 [70.8, 84.5] | +11.4 [+4.2, +18.8] | 0.0018 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 32.7 [27.4, 38.7] | 25.4 [21.0, 30.0] | -7.4 [-11.8, -3.8] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 74.0 [67.5, 80.7] | 63.5 [56.6, 70.4] | -10.5 [-16.4, -4.7] | 0.0014 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 17] | 12 [10, 17] | -3 [-3, +3] | 1.0000 |

## 77. gpt-oss-20b (Bedrock), both sets, cutoff none

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 2.58 [2.05, 3.17] | 2.43 [2.22, 2.63] | -0.16 [-0.66, +0.32] | 0.5498 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 61.6 [53.1, 70.1] | 81.4 [76.5, 85.9] | +19.8 [+12.5, +27.5] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 22.0 [17.6, 27.5] | 25.5 [21.8, 29.5] | +3.5 [-0.7, +7.0] | 0.0996 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 55.6 [47.8, 63.7] | 63.2 [57.2, 69.3] | +7.7 [+1.3, +14.1] | 0.0174 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 13 [12, 18] | 13 [9, 16] | +0 [-5, +1] | 0.3808 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 2.58 [2.05, 3.17] | 2.70 [2.52, 2.87] | +0.11 [-0.38, +0.58] | 0.6168 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 61.6 [53.1, 70.1] | 85.4 [81.4, 89.4] | +23.8 [+16.9, +31.1] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 22.0 [17.6, 27.5] | 21.9 [18.8, 25.1] | -0.1 [-4.3, +3.3] | 0.9232 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 55.6 [47.8, 63.7] | 57.6 [51.9, 63.5] | +2.0 [-4.9, +9.1] | 0.5822 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 13 [12, 18] | 14 [10, 17] | +1 [-4, +2] | 0.7096 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 2.58 [2.05, 3.17] | 1.98 [1.74, 2.22] | -0.60 [-1.12, -0.12] | 0.0148 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 61.6 [53.1, 70.1] | 73.5 [66.2, 80.4] | +11.8 [+4.1, +20.0] | 0.0028 |
| `max_k_shown` | 211 | ESCO precision (%) | 22.0 [17.6, 27.5] | 28.9 [24.6, 33.7] | +6.9 [+2.5, +10.9] | 0.0018 |
| `max_k_shown` | 211 | ESCO recall (%) | 55.6 [47.8, 63.7] | 61.4 [54.8, 68.1] | +5.8 [-0.7, +12.5] | 0.0864 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 13 [12, 18] | 13 [10, 16] | +0 [-5, +1] | 0.4758 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 2.58 [2.05, 3.17] | 3.62 [3.23, 4.02] | +1.03 [+0.63, +1.42] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 61.6 [53.1, 70.1] | 89.1 [83.7, 94.0] | +27.5 [+19.5, +35.6] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 22.0 [17.6, 27.5] | 18.7 [15.8, 21.9] | -3.3 [-7.2, -0.1] | 0.0444 |
| `min_k_shown` | 211 | ESCO recall (%) | 55.6 [47.8, 63.7] | 63.5 [57.0, 70.2] | +7.9 [+1.3, +14.8] | 0.0230 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 13 [12, 18] | 11 [11, 17] | -2 [-3, +2] | 0.9566 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 2.58 [2.05, 3.17] | 2.65 [2.23, 3.10] | +0.07 [-0.36, +0.49] | 0.7354 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 61.6 [53.1, 70.1] | 72.5 [64.7, 80.2] | +10.9 [+2.3, +20.0] | 0.0164 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 22.0 [17.6, 27.5] | 22.3 [18.4, 26.8] | +0.3 [-3.6, +3.7] | 0.8884 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 55.6 [47.8, 63.7] | 58.1 [50.8, 65.5] | +2.5 [-5.2, +10.4] | 0.5582 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 13 [12, 18] | 14 [12, 18] | +1 [-3, +3] | 1.0000 |

## 78. Grok 4.3 (Bedrock), both sets, cutoff none

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 1.40 [0.99, 1.84] | 1.37 [1.14, 1.60] | -0.03 [-0.44, +0.35] | 0.9532 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 40.8 [32.9, 48.8] | 54.5 [47.2, 61.6] | +13.7 [+7.0, +20.6] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 34.2 [27.0, 43.6] | 36.1 [30.0, 43.1] | +1.9 [-6.2, +8.8] | 0.6632 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 55.6 [47.6, 63.7] | 59.2 [51.9, 66.9] | +3.6 [-2.4, +10.0] | 0.2866 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 14 [9, 17] | 14 [9, 16] | +0 [-5, +3] | 0.8126 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 1.40 [0.99, 1.84] | 2.12 [1.86, 2.36] | +0.72 [+0.27, +1.13] | 0.0020 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 40.8 [32.9, 48.8] | 73.0 [65.4, 80.3] | +32.2 [+23.4, +41.2] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 34.2 [27.0, 43.6] | 29.5 [25.0, 34.5] | -4.7 [-12.7, +1.6] | 0.1514 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 55.6 [47.6, 63.7] | 67.5 [60.4, 74.7] | +11.9 [+5.2, +18.9] | 0.0004 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 14 [9, 17] | 13 [9, 16] | -1 [-4, +3] | 0.9766 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 1.40 [0.99, 1.84] | 1.16 [0.93, 1.38] | -0.25 [-0.61, +0.08] | 0.1628 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 40.8 [32.9, 48.8] | 46.0 [38.7, 53.1] | +5.2 [+0.0, +11.2] | 0.0814 |
| `max_k_shown` | 211 | ESCO precision (%) | 34.2 [27.0, 43.6] | 39.5 [32.7, 47.0] | +5.2 [-1.6, +11.1] | 0.1310 |
| `max_k_shown` | 211 | ESCO recall (%) | 55.6 [47.6, 63.7] | 57.4 [49.6, 65.4] | +1.8 [-2.6, +6.5] | 0.4904 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 14 [9, 17] | 13 [8, 16] | -1 [-5, +1] | 0.5372 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 1.40 [0.99, 1.84] | 3.64 [2.98, 4.33] | +2.23 [+1.56, +2.97] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 40.8 [32.9, 48.8] | 77.3 [70.3, 83.7] | +36.5 [+28.0, +45.3] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 34.2 [27.0, 43.6] | 19.4 [15.5, 24.2] | -14.8 [-22.9, -8.6] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 55.6 [47.6, 63.7] | 66.8 [59.7, 73.9] | +11.2 [+5.1, +17.5] | < 0.0001 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 14 [9, 17] | 16 [12, 18] | +2 [-1, +6] | 0.4340 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 1.40 [0.99, 1.84] | 2.64 [2.21, 3.06] | +1.23 [+0.72, +1.76] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 40.8 [32.9, 48.8] | 66.8 [59.7, 73.5] | +26.1 [+17.8, +34.6] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 34.2 [27.0, 43.6] | 23.6 [19.2, 28.8] | -10.6 [-18.7, -4.2] | 0.0010 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 55.6 [47.6, 63.7] | 62.1 [54.5, 69.7] | +6.5 [+1.0, +12.2] | 0.0222 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 14 [9, 17] | 14 [11, 17] | +0 [-2, +5] | 0.9104 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 1.40 [0.99, 1.84] | 4.17 [3.75, 4.66] | +2.77 [+2.18, +3.41] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 40.8 [32.9, 48.8] | 99.1 [97.6, 100.0] | +58.3 [+50.5, +66.2] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 34.2 [27.0, 43.6] | 17.9 [14.6, 21.5] | -16.3 [-24.6, -10.0] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO recall (%) | 55.6 [47.6, 63.7] | 69.3 [62.0, 76.6] | +13.7 [+6.8, +20.9] | 0.0002 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 14 [9, 17] | 16 [13, 18] | +2 [-1, +7] | 0.3770 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 1.40 [0.99, 1.84] | 1.63 [1.27, 2.00] | +0.22 [-0.23, +0.65] | 0.3204 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 40.8 [32.9, 48.8] | 46.0 [38.3, 54.0] | +5.2 [-2.5, +12.8] | 0.2044 |
| `min_k_escape` | 211 | ESCO precision (%) | 34.2 [27.0, 43.6] | 26.1 [20.2, 32.7] | -8.1 [-16.2, -1.2] | 0.0234 |
| `min_k_escape` | 211 | ESCO recall (%) | 55.6 [47.6, 63.7] | 43.7 [35.6, 51.8] | -11.9 [-19.8, -4.6] | 0.0010 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 14 [9, 17] | 14 [10, 17] | +0 [-3, +4] | 1.0000 |

## 79. Kimi K3 (Bedrock), both sets, cutoff none

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 1.03 [0.77, 1.31] | 1.12 [0.91, 1.32] | +0.09 [-0.07, +0.25] | 0.2776 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 40.8 [32.2, 49.3] | 47.4 [39.8, 54.8] | +6.6 [+1.3, +11.9] | 0.0170 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 46.9 [39.5, 55.5] | 45.5 [38.9, 52.5] | -1.5 [-6.2, +2.5] | 0.4932 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 69.3 [62.5, 76.2] | 71.0 [64.3, 77.5] | +1.7 [-2.1, +5.6] | 0.3950 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 12 [7, 15] | 10 [6, 14] | -2 [-4, +1] | 0.5990 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 1.03 [0.77, 1.31] | 2.03 [1.82, 2.23] | +1.00 [+0.76, +1.24] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 40.8 [32.2, 49.3] | 73.1 [66.6, 79.2] | +32.3 [+25.0, +39.8] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 46.9 [39.5, 55.5] | 32.0 [27.8, 36.5] | -14.9 [-21.3, -9.6] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 69.3 [62.5, 76.2] | 72.8 [66.3, 79.1] | +3.5 [-0.1, +7.3] | 0.0548 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 12 [7, 15] | 12 [8, 15] | +0 [-2, +4] | 0.9316 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 1.03 [0.77, 1.31] | 1.01 [0.78, 1.24] | -0.02 [-0.15, +0.11] | 0.8046 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 40.8 [32.2, 49.3] | 46.4 [37.6, 55.3] | +5.7 [+1.0, +10.8] | 0.0198 |
| `max_k_shown` | 211 | ESCO precision (%) | 46.9 [39.5, 55.5] | 48.2 [41.2, 56.2] | +1.2 [-2.4, +4.6] | 0.5062 |
| `max_k_shown` | 211 | ESCO recall (%) | 69.3 [62.5, 76.2] | 71.5 [64.5, 78.2] | +2.2 [-1.5, +5.8] | 0.2744 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 12 [7, 15] | 12 [7, 14] | +0 [-3, +2] | 1.0000 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 1.03 [0.77, 1.31] | 3.14 [2.79, 3.51] | +2.11 [+1.75, +2.51] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 40.8 [32.2, 49.3] | 87.2 [81.2, 92.6] | +46.4 [+37.7, +55.2] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 46.9 [39.5, 55.5] | 23.5 [19.5, 27.9] | -23.4 [-30.6, -17.5] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 69.3 [62.5, 76.2] | 73.6 [67.4, 79.9] | +4.3 [+0.4, +8.5] | 0.0394 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 12 [7, 15] | 12 [11, 17] | +0 [-1, +7] | 0.2662 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 1.03 [0.77, 1.31] | 1.53 [1.22, 1.84] | +0.50 [+0.29, +0.73] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 40.8 [32.2, 49.3] | 56.4 [47.3, 65.3] | +15.6 [+8.5, +23.1] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 46.9 [39.5, 55.5] | 38.4 [31.7, 45.8] | -8.6 [-13.9, -4.1] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 69.3 [62.5, 76.2] | 72.6 [65.7, 79.3] | +3.2 [-0.8, +7.5] | 0.1356 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 12 [7, 15] | 12 [8, 16] | +0 [-2, +4] | 0.8220 |

## 80. Ministral 3 14B (Bedrock), both sets, cutoff none

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 4.56 [3.69, 5.50] | 2.49 [2.25, 2.74] | -2.07 [-2.87, -1.34] | < 0.0001 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 79.6 [72.4, 86.4] | 84.2 [79.4, 88.7] | +4.5 [-0.2, +9.8] | 0.0642 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 15.2 [12.0, 19.3] | 23.2 [19.3, 27.4] | +8.0 [+5.4, +10.5] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 62.5 [55.1, 69.7] | 57.5 [50.7, 64.4] | -4.9 [-9.9, +0.3] | 0.0652 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 16 [10, 17] | +0 [-6, +1] | 0.2526 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 4.56 [3.69, 5.50] | 2.70 [2.49, 2.92] | -1.86 [-2.66, -1.12] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 79.6 [72.4, 86.4] | 87.8 [83.3, 91.9] | +8.2 [+3.6, +13.0] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 15.2 [12.0, 19.3] | 22.6 [19.1, 26.3] | +7.4 [+4.7, +9.7] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 62.5 [55.1, 69.7] | 60.1 [53.4, 66.8] | -2.4 [-7.6, +2.7] | 0.3660 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 15 [11, 17] | -1 [-6, +1] | 0.3068 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 4.56 [3.69, 5.50] | 2.15 [1.77, 2.56] | -2.42 [-3.20, -1.73] | < 0.0001 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 79.6 [72.4, 86.4] | 68.7 [61.1, 76.2] | -10.9 [-16.7, -5.7] | < 0.0001 |
| `max_k_shown` | 211 | ESCO precision (%) | 15.2 [12.0, 19.3] | 27.2 [22.2, 32.8] | +11.9 [+8.8, +15.5] | < 0.0001 |
| `max_k_shown` | 211 | ESCO recall (%) | 62.5 [55.1, 69.7] | 61.0 [53.5, 68.6] | -1.4 [-5.7, +2.5] | 0.5376 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 17 [11, 18] | +1 [-5, +1] | 0.4440 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 4.56 [3.69, 5.50] | 4.95 [4.31, 5.64] | +0.39 [-0.19, +0.94] | 0.1806 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 79.6 [72.4, 86.4] | 90.0 [84.9, 94.9] | +10.4 [+5.3, +16.1] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 15.2 [12.0, 19.3] | 14.3 [11.6, 17.5] | -0.9 [-2.9, +0.7] | 0.2850 |
| `min_k_shown` | 211 | ESCO recall (%) | 62.5 [55.1, 69.7] | 63.2 [55.9, 70.4] | +0.7 [-3.5, +5.4] | 0.8394 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 16 [13, 19] | +0 [-3, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 4.56 [3.69, 5.50] | 0.71 [0.49, 0.95] | -3.86 [-4.77, -3.01] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 79.6 [72.4, 86.4] | 32.7 [24.4, 41.6] | -46.9 [-56.0, -37.8] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 15.2 [12.0, 19.3] | 46.2 [38.1, 55.6] | +31.0 [+23.7, +39.3] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 62.5 [55.1, 69.7] | 46.2 [37.6, 55.0] | -16.2 [-24.1, -8.9] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 12 [8, 15] | -4 [-9, -1] | 0.0318 |

## 81. Mistral Large 3 (Bedrock), both sets, cutoff none

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 1.95 [1.47, 2.49] | 1.86 [1.64, 2.08] | -0.09 [-0.49, +0.27] | 0.6536 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 52.6 [43.6, 61.5] | 67.3 [60.8, 73.5] | +14.7 [+8.8, +21.2] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 30.5 [23.8, 39.0] | 31.6 [26.8, 36.6] | +1.1 [-4.1, +5.1] | 0.6860 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 65.3 [57.7, 73.0] | 65.5 [59.1, 71.7] | +0.1 [-5.3, +5.7] | 0.9902 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 18] | 15 [9, 16] | +0 [-5, +2] | 0.6088 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 1.95 [1.47, 2.49] | 2.31 [2.10, 2.52] | +0.36 [-0.07, +0.75] | 0.0928 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 52.6 [43.6, 61.5] | 76.1 [70.5, 81.4] | +23.5 [+17.0, +30.6] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 30.5 [23.8, 39.0] | 27.3 [23.3, 31.5] | -3.2 [-9.0, +1.2] | 0.1698 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 65.3 [57.7, 73.0] | 66.2 [60.2, 71.9] | +0.9 [-4.5, +6.4] | 0.7942 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 18] | 16 [10, 16] | +1 [-4, +2] | 0.7816 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 1.95 [1.47, 2.49] | 1.58 [1.30, 1.87] | -0.37 [-0.72, -0.06] | 0.0178 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 52.6 [43.6, 61.5] | 59.2 [51.1, 67.4] | +6.6 [+0.9, +12.8] | 0.0248 |
| `max_k_shown` | 211 | ESCO precision (%) | 30.5 [23.8, 39.0] | 34.4 [28.3, 41.0] | +3.9 [-0.2, +7.4] | 0.0624 |
| `max_k_shown` | 211 | ESCO recall (%) | 65.3 [57.7, 73.0] | 63.2 [56.1, 69.9] | -2.2 [-7.9, +3.6] | 0.4856 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 18] | 15 [9, 16] | +0 [-4, +2] | 0.7374 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 1.95 [1.47, 2.49] | 3.58 [3.15, 4.06] | +1.63 [+1.15, +2.13] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 52.6 [43.6, 61.5] | 85.8 [80.5, 90.8] | +33.2 [+24.5, +42.1] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 30.5 [23.8, 39.0] | 19.6 [15.8, 23.7] | -10.9 [-17.3, -6.1] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 65.3 [57.7, 73.0] | 66.4 [59.4, 73.5] | +1.1 [-4.6, +6.8] | 0.7824 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 18] | 16 [12, 18] | +1 [-2, +5] | 0.8088 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 1.95 [1.47, 2.49] | 0.90 [0.69, 1.12] | -1.06 [-1.52, -0.65] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 52.6 [43.6, 61.5] | 38.9 [31.1, 46.9] | -13.7 [-20.4, -7.3] | 0.0002 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 30.5 [23.8, 39.0] | 43.9 [36.6, 52.0] | +13.4 [+7.3, +19.4] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 65.3 [57.7, 73.0] | 53.4 [44.7, 62.0] | -11.9 [-19.1, -5.4] | 0.0006 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 18] | 14 [8, 15] | -1 [-7, +1] | 0.3002 |

## 82. Qwen3-235B (Bedrock), both sets, cutoff none

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 1.82 [1.43, 2.21] | 1.51 [1.28, 1.73] | -0.31 [-0.60, -0.04] | 0.0214 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 58.3 [50.2, 66.2] | 54.3 [47.3, 61.1] | -4.0 [-9.1, +0.9] | 0.1096 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 30.5 [24.7, 37.7] | 34.3 [28.9, 40.4] | +3.8 [+0.1, +7.1] | 0.0412 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 60.6 [52.4, 69.0] | 59.9 [53.0, 66.9] | -0.8 [-5.9, +4.3] | 0.7726 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 17] | 12 [8, 16] | -3 [-5, +1] | 0.4426 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 1.82 [1.43, 2.21] | 2.07 [1.84, 2.29] | +0.26 [-0.05, +0.55] | 0.1036 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 58.3 [50.2, 66.2] | 69.4 [63.0, 75.4] | +11.1 [+5.0, +17.4] | 0.0002 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 30.5 [24.7, 37.7] | 28.1 [24.0, 32.5] | -2.4 [-6.7, +1.0] | 0.1678 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 60.6 [52.4, 69.0] | 61.5 [55.0, 68.1] | +0.9 [-5.0, +6.6] | 0.7794 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 17] | 16 [10, 16] | +1 [-4, +2] | 0.9132 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 1.82 [1.43, 2.21] | 1.69 [1.44, 1.93] | -0.13 [-0.41, +0.14] | 0.3816 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 58.3 [50.2, 66.2] | 62.6 [54.8, 70.1] | +4.3 [-0.9, +9.5] | 0.1078 |
| `max_k_shown` | 211 | ESCO precision (%) | 30.5 [24.7, 37.7] | 31.7 [26.3, 37.7] | +1.2 [-2.2, +4.0] | 0.4922 |
| `max_k_shown` | 211 | ESCO recall (%) | 60.6 [52.4, 69.0] | 59.6 [52.0, 67.3] | -1.1 [-5.1, +2.7] | 0.6642 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 17] | 15 [10, 16] | +0 [-4, +2] | 0.9026 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 1.82 [1.43, 2.21] | 3.69 [3.45, 3.93] | +1.87 [+1.45, +2.28] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 58.3 [50.2, 66.2] | 99.1 [97.6, 100.0] | +40.8 [+33.0, +48.8] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 30.5 [24.7, 37.7] | 19.3 [16.3, 22.6] | -11.2 [-16.7, -6.9] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 60.6 [52.4, 69.0] | 67.1 [60.3, 74.1] | +6.5 [+1.0, +12.4] | 0.0236 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 17] | 15 [12, 18] | +0 [-2, +5] | 0.6292 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 1.82 [1.43, 2.21] | 2.04 [1.77, 2.31] | +0.22 [-0.17, +0.59] | 0.2530 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 58.3 [50.2, 66.2] | 71.1 [62.9, 78.8] | +12.8 [+4.1, +21.6] | 0.0034 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 30.5 [24.7, 37.7] | 30.6 [26.2, 35.6] | +0.2 [-4.7, +4.4] | 0.9892 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 60.6 [52.4, 69.0] | 68.6 [61.9, 75.3] | +7.9 [+1.1, +15.2] | 0.0268 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 15 [10, 17] | 13 [10, 16] | -2 [-4, +2] | 0.8454 |

## 83. DeepSeek V4.1 Flash (Together), both sets, cutoff none

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 2.25 [1.73, 2.84] | 1.97 [1.72, 2.22] | -0.28 [-0.73, +0.08] | 0.1542 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 62.1 [53.5, 70.6] | 69.7 [62.8, 76.2] | +7.6 [+1.9, +13.1] | 0.0096 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 27.2 [21.6, 34.2] | 31.0 [26.1, 36.3] | +3.8 [-0.1, +7.5] | 0.0568 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 63.9 [56.6, 71.3] | 67.4 [60.6, 74.3] | +3.5 [-0.4, +7.5] | 0.0792 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 14 [11, 18] | 13 [9, 16] | -1 [-5, +1] | 0.3714 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 2.25 [1.73, 2.84] | 2.60 [2.40, 2.80] | +0.36 [-0.15, +0.77] | 0.1546 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 62.1 [53.5, 70.6] | 85.1 [81.0, 89.0] | +23.0 [+16.3, +30.0] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 27.2 [21.6, 34.2] | 25.3 [21.4, 29.3] | -1.9 [-6.6, +2.2] | 0.3648 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 63.9 [56.6, 71.3] | 67.2 [60.5, 74.0] | +3.3 [-0.6, +7.4] | 0.0992 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 14 [11, 18] | 15 [10, 17] | +1 [-4, +2] | 0.7528 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 2.25 [1.73, 2.84] | 1.61 [1.35, 1.88] | -0.64 [-1.08, -0.28] | 0.0002 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 62.1 [53.5, 70.6] | 64.5 [55.7, 72.9] | +2.4 [-3.2, +7.9] | 0.4390 |
| `max_k_shown` | 211 | ESCO precision (%) | 27.2 [21.6, 34.2] | 35.0 [29.0, 41.5] | +7.8 [+4.0, +11.7] | < 0.0001 |
| `max_k_shown` | 211 | ESCO recall (%) | 63.9 [56.6, 71.3] | 66.1 [58.7, 73.5] | +2.2 [-1.9, +6.2] | 0.3188 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 14 [11, 18] | 14 [9, 16] | +0 [-5, +1] | 0.6014 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 2.25 [1.73, 2.84] | 3.83 [3.35, 4.35] | +1.58 [+1.16, +2.02] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 62.1 [53.5, 70.6] | 86.7 [81.0, 91.9] | +24.6 [+17.4, +32.4] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 27.2 [21.6, 34.2] | 18.6 [15.1, 22.6] | -8.6 [-13.1, -5.1] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 63.9 [56.6, 71.3] | 66.8 [59.8, 73.9] | +2.9 [+0.3, +5.9] | 0.0486 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 14 [11, 18] | 15 [12, 18] | +1 [-2, +4] | 0.8270 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 2.25 [1.73, 2.84] | 2.95 [2.50, 3.44] | +0.71 [+0.27, +1.15] | 0.0026 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 62.1 [53.5, 70.6] | 82.0 [74.9, 88.3] | +19.9 [+12.7, +27.4] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 27.2 [21.6, 34.2] | 22.8 [18.3, 28.0] | -4.4 [-8.5, -1.0] | 0.0096 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 63.9 [56.6, 71.3] | 66.4 [59.1, 73.7] | +2.5 [+0.0, +5.6] | 0.0832 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 14 [11, 18] | 13 [11, 18] | -1 [-2, +3] | 1.0000 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 2.25 [1.73, 2.84] | 4.96 [4.48, 5.49] | +2.71 [+2.11, +3.36] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 62.1 [53.5, 70.6] | 100.0 [100.0, 100.0] | +37.9 [+29.4, +46.5] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 27.2 [21.6, 34.2] | 16.0 [13.1, 19.1] | -11.2 [-16.8, -6.9] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO recall (%) | 63.9 [56.6, 71.3] | 71.8 [64.7, 78.9] | +7.9 [+4.2, +11.9] | < 0.0001 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 14 [11, 18] | 16 [13, 18] | +2 [-2, +5] | 0.5350 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 2.25 [1.73, 2.84] | 2.08 [1.65, 2.55] | -0.17 [-0.63, +0.24] | 0.4594 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 62.1 [53.5, 70.6] | 53.1 [44.6, 61.5] | -9.0 [-17.5, -1.0] | 0.0316 |
| `min_k_escape` | 211 | ESCO precision (%) | 27.2 [21.6, 34.2] | 28.5 [23.4, 34.4] | +1.3 [-2.8, +5.4] | 0.5364 |
| `min_k_escape` | 211 | ESCO recall (%) | 63.9 [56.6, 71.3] | 63.2 [55.7, 70.7] | -0.7 [-4.8, +2.9] | 0.7814 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 14 [11, 18] | 14 [10, 17] | +0 [-4, +2] | 0.9896 |

## 84. Qwen3.5-9B (Together), both sets, cutoff none

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 2.58 [1.88, 3.38] | 1.74 [1.40, 2.11] | -0.84 [-1.35, -0.39] | 0.0002 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 43.1 [35.4, 51.2] | 52.0 [45.3, 58.5] | +8.9 [+3.7, +14.4] | 0.0006 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 17.0 [12.3, 23.3] | 26.9 [21.3, 33.2] | +9.8 [+6.2, +13.3] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 40.4 [31.5, 49.4] | 48.7 [41.4, 56.0] | +8.3 [+1.4, +15.2] | 0.0206 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 15 [13, 19] | 11 [10, 17] | -4 [-6, +0] | 0.1884 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 2.58 [1.88, 3.38] | 1.72 [1.41, 2.06] | -0.86 [-1.38, -0.40] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 43.1 [35.4, 51.2] | 54.4 [47.6, 61.0] | +11.3 [+6.3, +16.5] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 17.0 [12.3, 23.3] | 25.0 [20.0, 30.7] | +8.0 [+4.3, +11.3] | 0.0002 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 40.4 [31.5, 49.4] | 43.8 [36.7, 51.1] | +3.3 [-3.4, +9.9] | 0.3204 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 15 [13, 19] | 13 [10, 17] | -2 [-5, +1] | 0.3258 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 2.58 [1.88, 3.38] | 1.97 [1.43, 2.61] | -0.62 [-0.97, -0.30] | 0.0002 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 43.1 [35.4, 51.2] | 49.3 [41.7, 56.6] | +6.2 [+1.9, +11.2] | 0.0072 |
| `max_k_shown` | 211 | ESCO precision (%) | 17.0 [12.3, 23.3] | 23.7 [17.5, 31.3] | +6.7 [+3.6, +10.6] | < 0.0001 |
| `max_k_shown` | 211 | ESCO recall (%) | 40.4 [31.5, 49.4] | 46.6 [37.9, 54.9] | +6.1 [+1.0, +11.8] | 0.0224 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 15 [13, 19] | 15 [12, 18] | +0 [-4, +1] | 0.7440 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 2.58 [1.88, 3.38] | 3.09 [2.44, 3.80] | +0.50 [+0.15, +0.90] | 0.0072 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 43.1 [35.4, 51.2] | 58.8 [51.0, 66.4] | +15.6 [+9.2, +22.6] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 17.0 [12.3, 23.3] | 18.7 [14.2, 24.0] | +1.7 [-1.5, +4.4] | 0.2748 |
| `min_k_shown` | 211 | ESCO recall (%) | 40.4 [31.5, 49.4] | 54.2 [44.6, 63.6] | +13.7 [+7.0, +21.0] | < 0.0001 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 15 [13, 19] | 14 [12, 18] | -1 [-3, +1] | 0.6956 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 2.58 [1.88, 3.38] | 2.05 [1.33, 2.91] | -0.54 [-0.87, -0.19] | 0.0028 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 43.1 [35.4, 51.2] | 30.8 [23.3, 38.6] | -12.3 [-18.9, -6.0] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 17.0 [12.3, 23.3] | 16.0 [10.7, 23.1] | -1.1 [-4.7, +2.8] | 0.5960 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 40.4 [31.5, 49.4] | 29.6 [22.0, 37.5] | -10.8 [-18.6, -3.7] | 0.0038 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 15 [13, 19] | 15 [13, 20] | +0 [-2, +3] | 0.9668 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 2.58 [1.88, 3.38] | 5.53 [4.67, 6.65] | +2.95 [+2.18, +3.96] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 43.1 [35.4, 51.2] | 99.5 [98.5, 100.0] | +56.4 [+48.4, +64.1] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 17.0 [12.3, 23.3] | 15.2 [11.9, 18.9] | -1.9 [-6.8, +1.9] | 0.3720 |
| `min_k_enforced` | 211 | ESCO recall (%) | 40.4 [31.5, 49.4] | 75.5 [68.8, 82.0] | +35.0 [+26.6, +44.0] | < 0.0001 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 15 [13, 19] | 14 [11, 18] | -1 [-4, +2] | 0.5886 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 2.58 [1.88, 3.38] | 3.07 [2.33, 3.97] | +0.48 [+0.10, +0.90] | 0.0104 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 43.1 [35.4, 51.2] | 55.5 [47.6, 63.1] | +12.3 [+5.4, +19.4] | 0.0002 |
| `min_k_escape` | 211 | ESCO precision (%) | 17.0 [12.3, 23.3] | 19.6 [14.7, 25.6] | +2.6 [-0.5, +5.6] | 0.0880 |
| `min_k_escape` | 211 | ESCO recall (%) | 40.4 [31.5, 49.4] | 57.0 [47.7, 66.1] | +16.6 [+9.6, +23.9] | < 0.0001 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 15 [13, 19] | 15 [11, 18] | +0 [-4, +1] | 0.7608 |

## 85. 8 main models pooled, both sets, cutoff 0.7

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 1688 | False ESCO concepts per ad | 4.12 [3.66, 4.62] | 2.38 [2.19, 2.57] | -1.74 [-2.14, -1.36] | < 0.0001 |
| `prose_up_to_k` | 1688 | Ads with at least one false concept (%) | 52.1 [48.2, 56.0] | 57.8 [54.2, 61.5] | +5.7 [+3.5, +8.1] | < 0.0001 |
| `prose_up_to_k` | 1688 | ESCO precision (%) | 9.8 [7.6, 12.4] | 15.6 [12.5, 18.8] | +5.8 [+4.4, +7.2] | < 0.0001 |
| `prose_up_to_k` | 1688 | ESCO recall (%) | 63.7 [56.8, 70.7] | 62.5 [55.9, 69.2] | -1.2 [-4.5, +2.3] | 0.4940 |
| `prose_up_to_k` | 1688 | Top-20 concepts not in the true items' top 20 | 16 [11, 17] | 14 [9, 16] | -2 [-5, +1] | 0.4226 |
| `prose_exactly_k` | 1688 | False ESCO concepts per ad | 4.12 [3.66, 4.62] | 2.37 [2.17, 2.57] | -1.75 [-2.18, -1.34] | < 0.0001 |
| `prose_exactly_k` | 1688 | Ads with at least one false concept (%) | 52.1 [48.2, 56.0] | 64.7 [61.0, 68.5] | +12.6 [+10.2, +15.1] | < 0.0001 |
| `prose_exactly_k` | 1688 | ESCO precision (%) | 9.8 [7.6, 12.4] | 15.5 [12.4, 18.6] | +5.6 [+4.2, +7.2] | < 0.0001 |
| `prose_exactly_k` | 1688 | ESCO recall (%) | 63.7 [56.8, 70.7] | 61.3 [55.2, 67.7] | -2.3 [-5.9, +1.2] | 0.2060 |
| `prose_exactly_k` | 1688 | Top-20 concepts not in the true items' top 20 | 16 [11, 17] | 16 [10, 16] | +0 [-4, +1] | 0.6276 |
| `max_k_shown` | 1688 | False ESCO concepts per ad | 4.12 [3.66, 4.62] | 3.29 [2.93, 3.68] | -0.83 [-1.15, -0.50] | < 0.0001 |
| `max_k_shown` | 1688 | Ads with at least one false concept (%) | 52.1 [48.2, 56.0] | 52.0 [48.1, 55.8] | -0.2 [-2.3, +2.1] | 0.8906 |
| `max_k_shown` | 1688 | ESCO precision (%) | 9.8 [7.6, 12.4] | 11.9 [9.3, 14.7] | +2.0 [+1.1, +3.1] | < 0.0001 |
| `max_k_shown` | 1688 | ESCO recall (%) | 63.7 [56.8, 70.7] | 62.8 [56.3, 69.5] | -0.8 [-3.2, +1.7] | 0.5320 |
| `max_k_shown` | 1688 | Top-20 concepts not in the true items' top 20 | 16 [11, 17] | 15 [10, 17] | -1 [-3, +1] | 1.0000 |
| `min_k_shown` | 1688 | False ESCO concepts per ad | 4.12 [3.66, 4.62] | 4.86 [4.43, 5.30] | +0.74 [+0.33, +1.16] | 0.0004 |
| `min_k_shown` | 1688 | Ads with at least one false concept (%) | 52.1 [48.2, 56.0] | 71.0 [67.3, 74.6] | +18.9 [+16.3, +21.5] | < 0.0001 |
| `min_k_shown` | 1688 | ESCO precision (%) | 9.8 [7.6, 12.4] | 8.8 [6.9, 10.8] | -1.1 [-2.2, -0.1] | 0.0284 |
| `min_k_shown` | 1688 | ESCO recall (%) | 63.7 [56.8, 70.7] | 66.1 [59.8, 72.4] | +2.4 [-0.7, +5.7] | 0.1332 |
| `min_k_shown` | 1688 | Top-20 concepts not in the true items' top 20 | 16 [11, 17] | 16 [12, 18] | +0 [-1, +3] | 0.9924 |
| `min_k_shown_fewer_ok` | 1688 | False ESCO concepts per ad | 4.12 [3.66, 4.62] | 2.90 [2.58, 3.23] | -1.22 [-1.68, -0.78] | < 0.0001 |
| `min_k_shown_fewer_ok` | 1688 | Ads with at least one false concept (%) | 52.1 [48.2, 56.0] | 45.9 [42.3, 49.6] | -6.3 [-8.8, -3.8] | < 0.0001 |
| `min_k_shown_fewer_ok` | 1688 | ESCO precision (%) | 9.8 [7.6, 12.4] | 12.0 [9.3, 14.8] | +2.1 [+0.8, +3.6] | 0.0016 |
| `min_k_shown_fewer_ok` | 1688 | ESCO recall (%) | 63.7 [56.8, 70.7] | 55.9 [49.8, 61.9] | -7.8 [-11.0, -4.6] | < 0.0001 |
| `min_k_shown_fewer_ok` | 1688 | Top-20 concepts not in the true items' top 20 | 16 [11, 17] | 15 [10, 17] | -1 [-3, +1] | 0.9792 |
| `min_k_enforced` | 1688 | False ESCO concepts per ad | 4.12 [3.66, 4.62] | 2.86 [2.65, 3.08] | -1.26 [-1.69, -0.85] | < 0.0001 |
| `min_k_enforced` | 1688 | Ads with at least one false concept (%) | 52.1 [48.2, 56.0] | 84.3 [81.0, 87.3] | +32.2 [+28.3, +36.1] | < 0.0001 |
| `min_k_enforced` | 1688 | ESCO precision (%) | 9.8 [7.6, 12.4] | 14.7 [11.7, 17.7] | +4.8 [+3.5, +6.2] | < 0.0001 |
| `min_k_enforced` | 1688 | ESCO recall (%) | 63.7 [56.8, 70.7] | 69.6 [63.3, 75.9] | +6.0 [+2.3, +9.8] | 0.0018 |
| `min_k_enforced` | 1688 | Top-20 concepts not in the true items' top 20 | 16 [11, 17] | 14 [10, 17] | -2 [-3, +2] | 0.9546 |
| `min_k_escape` | 1688 | False ESCO concepts per ad | 4.12 [3.66, 4.62] | 1.78 [1.60, 1.97] | -2.34 [-2.80, -1.92] | < 0.0001 |
| `min_k_escape` | 1688 | Ads with at least one false concept (%) | 52.1 [48.2, 56.0] | 49.2 [45.2, 53.4] | -2.9 [-6.0, +0.2] | 0.0750 |
| `min_k_escape` | 1688 | ESCO precision (%) | 9.8 [7.6, 12.4] | 18.6 [15.0, 22.2] | +8.7 [+6.8, +10.6] | < 0.0001 |
| `min_k_escape` | 1688 | ESCO recall (%) | 63.7 [56.8, 70.7] | 57.4 [51.6, 63.2] | -6.3 [-10.3, -2.2] | 0.0020 |
| `min_k_escape` | 1688 | Top-20 concepts not in the true items' top 20 | 16 [11, 17] | 14 [9, 15] | -2 [-5, +1] | 0.2570 |

## 86. Qwen3.5-0.8B (main model alone; not registered), both sets, cutoff 0.7

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 5.64 [4.70, 6.69] | 5.02 [4.54, 5.56] | -0.63 [-1.47, +0.17] | 0.1282 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 82.0 [75.0, 88.6] | 96.4 [93.5, 98.6] | +14.4 [+8.0, +21.3] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 6.2 [4.4, 8.3] | 7.1 [5.3, 9.0] | +0.8 [-0.5, +2.1] | 0.2136 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 53.0 [42.1, 64.4] | 54.0 [45.2, 62.9] | +0.9 [-8.4, +10.2] | 0.8564 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 17 [14, 19] | 17 [13, 18] | +0 [-3, +1] | 0.8654 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 5.64 [4.70, 6.69] | 4.60 [4.05, 5.22] | -1.04 [-1.90, -0.25] | 0.0070 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 82.0 [75.0, 88.6] | 91.6 [88.1, 94.7] | +9.6 [+3.5, +16.1] | 0.0028 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 6.2 [4.4, 8.3] | 7.8 [5.7, 10.1] | +1.5 [+0.1, +3.0] | 0.0346 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 53.0 [42.1, 64.4] | 54.9 [46.2, 63.9] | +1.9 [-8.5, +11.8] | 0.7262 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 17 [14, 19] | 16 [13, 18] | -1 [-3, +1] | 0.7714 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 5.64 [4.70, 6.69] | 5.97 [4.98, 7.09] | +0.33 [-0.33, +0.97] | 0.3204 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 82.0 [75.0, 88.6] | 83.9 [77.3, 90.0] | +1.9 [-1.0, +5.6] | 0.3282 |
| `max_k_shown` | 211 | ESCO precision (%) | 6.2 [4.4, 8.3] | 6.4 [4.7, 8.4] | +0.2 [-0.7, +1.0] | 0.6990 |
| `max_k_shown` | 211 | ESCO recall (%) | 53.0 [42.1, 64.4] | 57.7 [47.4, 68.1] | +4.7 [+0.0, +10.0] | 0.0600 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 17 [14, 19] | 17 [13, 19] | +0 [-2, +2] | 1.0000 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 5.64 [4.70, 6.69] | 5.87 [4.91, 6.92] | +0.23 [-0.51, +1.01] | 0.5760 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 82.0 [75.0, 88.6] | 73.5 [66.8, 79.9] | -8.5 [-14.5, -2.7] | 0.0084 |
| `min_k_shown` | 211 | ESCO precision (%) | 6.2 [4.4, 8.3] | 6.1 [4.4, 8.1] | -0.1 [-1.3, +1.1] | 0.8778 |
| `min_k_shown` | 211 | ESCO recall (%) | 53.0 [42.1, 64.4] | 54.4 [44.0, 64.8] | +1.3 [-7.9, +10.7] | 0.8634 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 17 [14, 19] | 17 [13, 19] | +0 [-3, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 5.64 [4.70, 6.69] | 6.19 [5.43, 6.98] | +0.55 [-0.27, +1.33] | 0.1852 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 82.0 [75.0, 88.6] | 93.8 [89.5, 97.7] | +11.8 [+5.4, +18.7] | 0.0002 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 6.2 [4.4, 8.3] | 6.2 [4.6, 8.0] | -0.0 [-1.3, +1.1] | 0.9276 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 53.0 [42.1, 64.4] | 57.7 [47.0, 68.5] | +4.7 [-4.7, +14.5] | 0.3816 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 17 [14, 19] | 16 [13, 18] | -1 [-3, +1] | 0.8072 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 5.64 [4.70, 6.69] | 5.16 [4.58, 5.79] | -0.49 [-1.51, +0.53] | 0.3574 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 82.0 [75.0, 88.6] | 92.4 [87.5, 96.7] | +10.4 [+3.3, +18.0] | 0.0058 |
| `min_k_enforced` | 211 | ESCO precision (%) | 6.2 [4.4, 8.3] | 5.8 [4.0, 7.7] | -0.4 [-2.2, +1.1] | 0.5950 |
| `min_k_enforced` | 211 | ESCO recall (%) | 53.0 [42.1, 64.4] | 45.0 [34.2, 55.7] | -8.1 [-20.4, +2.6] | 0.1748 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 17 [14, 19] | 17 [13, 19] | +0 [-3, +3] | 1.0000 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 5.64 [4.70, 6.69] | 4.42 [3.85, 5.02] | -1.23 [-2.20, -0.29] | 0.0112 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 82.0 [75.0, 88.6] | 89.1 [83.3, 94.4] | +7.1 [+0.0, +14.5] | 0.0526 |
| `min_k_escape` | 211 | ESCO precision (%) | 6.2 [4.4, 8.3] | 7.3 [5.2, 9.5] | +1.0 [-0.7, +2.6] | 0.2232 |
| `min_k_escape` | 211 | ESCO recall (%) | 53.0 [42.1, 64.4] | 49.0 [38.2, 59.7] | -4.0 [-16.3, +7.0] | 0.5306 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 17 [14, 19] | 17 [13, 19] | +0 [-3, +3] | 1.0000 |

## 87. Qwen3.5-2B (main model alone; not registered), both sets, cutoff 0.7

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 19.56 [16.54, 22.88] | 8.68 [7.69, 9.74] | -10.88 [-13.83, -8.13] | < 0.0001 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 97.6 [94.5, 100.0] | 98.2 [96.5, 99.5] | +0.6 [-2.0, +3.8] | 0.7758 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 2.4 [1.7, 3.2] | 4.6 [3.5, 5.9] | +2.2 [+1.5, +3.0] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 67.8 [57.1, 77.6] | 59.2 [49.3, 68.8] | -8.6 [-16.4, -0.7] | 0.0340 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 17 [15, 20] | 17 [13, 19] | +0 [-3, +1] | 0.7162 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 19.56 [16.54, 22.88] | 7.80 [6.75, 8.92] | -11.76 [-14.87, -8.84] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 97.6 [94.5, 100.0] | 95.8 [93.5, 97.9] | -1.8 [-4.7, +1.4] | 0.2506 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 2.4 [1.7, 3.2] | 5.1 [3.8, 6.5] | +2.7 [+1.8, +3.7] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 67.8 [57.1, 77.6] | 58.9 [49.0, 68.6] | -8.9 [-16.9, -0.8] | 0.0314 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 17 [15, 20] | 17 [14, 19] | +0 [-3, +1] | 0.7708 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 19.56 [16.54, 22.88] | 15.53 [13.38, 17.86] | -4.04 [-6.61, -1.50] | 0.0014 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 97.6 [94.5, 100.0] | 97.6 [94.9, 99.5] | +0.0 [-2.0, +2.5] | 1.0000 |
| `max_k_shown` | 211 | ESCO precision (%) | 2.4 [1.7, 3.2] | 3.0 [2.2, 3.9] | +0.6 [+0.1, +1.1] | 0.0102 |
| `max_k_shown` | 211 | ESCO recall (%) | 67.8 [57.1, 77.6] | 67.8 [58.1, 76.9] | +0.0 [-6.2, +7.1] | 1.0000 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 17 [15, 20] | 17 [14, 19] | +0 [-2, +1] | 1.0000 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 19.56 [16.54, 22.88] | 21.73 [19.16, 24.53] | +2.17 [-0.98, +5.34] | 0.1766 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 97.6 [94.5, 100.0] | 99.5 [98.5, 100.0] | +1.9 [+0.0, +4.8] | 0.2620 |
| `min_k_shown` | 211 | ESCO precision (%) | 2.4 [1.7, 3.2] | 2.0 [1.5, 2.6] | -0.4 [-0.9, -0.0] | 0.0466 |
| `min_k_shown` | 211 | ESCO recall (%) | 67.8 [57.1, 77.6] | 62.4 [51.7, 72.5] | -5.4 [-13.1, +1.7] | 0.1784 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 17 [15, 20] | 19 [15, 20] | +2 [-1, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 19.56 [16.54, 22.88] | 13.03 [10.99, 15.30] | -6.53 [-9.90, -3.21] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 97.6 [94.5, 100.0] | 97.6 [94.9, 99.5] | +0.0 [-2.0, +2.4] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 2.4 [1.7, 3.2] | 3.9 [2.9, 5.0] | +1.5 [+0.8, +2.3] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 67.8 [57.1, 77.6] | 74.5 [65.9, 82.7] | +6.7 [-1.2, +15.6] | 0.1258 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 17 [15, 20] | 17 [14, 19] | +0 [-3, +1] | 0.9266 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 19.56 [16.54, 22.88] | 4.76 [4.26, 5.29] | -14.81 [-18.02, -11.86] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 97.6 [94.5, 100.0] | 94.8 [90.8, 98.1] | -2.8 [-6.7, +0.5] | 0.1446 |
| `min_k_enforced` | 211 | ESCO precision (%) | 2.4 [1.7, 3.2] | 8.5 [6.4, 10.7] | +6.1 [+4.4, +7.9] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO recall (%) | 67.8 [57.1, 77.6] | 62.4 [51.3, 73.5] | -5.4 [-15.0, +5.0] | 0.3304 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 17 [15, 20] | 17 [13, 18] | +0 [-4, +1] | 0.5710 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 19.56 [16.54, 22.88] | 3.79 [3.31, 4.30] | -15.77 [-19.06, -12.78] | < 0.0001 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 97.6 [94.5, 100.0] | 88.6 [82.7, 94.0] | -9.0 [-14.5, -4.3] | < 0.0001 |
| `min_k_escape` | 211 | ESCO precision (%) | 2.4 [1.7, 3.2] | 11.7 [9.1, 14.4] | +9.3 [+7.2, +11.6] | < 0.0001 |
| `min_k_escape` | 211 | ESCO recall (%) | 67.8 [57.1, 77.6] | 71.1 [61.8, 80.6] | +3.4 [-5.7, +14.1] | 0.5566 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 17 [15, 20] | 15 [12, 18] | -2 [-5, +1] | 0.3062 |

## 88. Qwen3.5-9B (main model alone; not registered), both sets, cutoff 0.7

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 1.23 [0.90, 1.59] | 0.82 [0.64, 1.02] | -0.41 [-0.64, -0.20] | < 0.0001 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 37.0 [29.4, 44.5] | 39.8 [33.4, 46.2] | +2.8 [-2.7, +8.3] | 0.3146 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 21.5 [15.4, 28.8] | 30.6 [23.7, 38.2] | +9.2 [+5.0, +13.3] | 0.0002 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 47.7 [35.2, 60.3] | 51.5 [41.4, 61.6] | +3.9 [-5.7, +13.0] | 0.4038 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 16 [12, 18] | 14 [9, 16] | -2 [-6, +1] | 0.2486 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 1.23 [0.90, 1.59] | 0.88 [0.70, 1.07] | -0.35 [-0.60, -0.13] | 0.0016 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 37.0 [29.4, 44.5] | 42.8 [36.2, 49.6] | +5.9 [+0.3, +11.5] | 0.0430 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 21.5 [15.4, 28.8] | 27.0 [20.6, 34.0] | +5.5 [+0.5, +10.2] | 0.0314 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 47.7 [35.2, 60.3] | 45.9 [36.3, 56.0] | -1.7 [-11.6, +8.4] | 0.7466 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 16 [12, 18] | 14 [9, 16] | -2 [-6, +1] | 0.3988 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 1.23 [0.90, 1.59] | 0.96 [0.69, 1.24] | -0.27 [-0.45, -0.12] | < 0.0001 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 37.0 [29.4, 44.5] | 36.0 [28.6, 43.5] | -0.9 [-6.4, +4.6] | 0.7834 |
| `max_k_shown` | 211 | ESCO precision (%) | 21.5 [15.4, 28.8] | 24.9 [18.0, 33.3] | +3.5 [+0.0, +7.5] | 0.0498 |
| `max_k_shown` | 211 | ESCO recall (%) | 47.7 [35.2, 60.3] | 45.0 [33.5, 56.9] | -2.7 [-8.4, +3.1] | 0.4434 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 16 [12, 18] | 17 [11, 18] | +1 [-3, +2] | 1.0000 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 1.23 [0.90, 1.59] | 1.48 [1.13, 1.85] | +0.25 [+0.07, +0.44] | 0.0058 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 37.0 [29.4, 44.5] | 46.0 [38.6, 53.2] | +9.0 [+3.2, +15.2] | 0.0026 |
| `min_k_shown` | 211 | ESCO precision (%) | 21.5 [15.4, 28.8] | 19.8 [14.6, 25.8] | -1.7 [-5.2, +1.4] | 0.2880 |
| `min_k_shown` | 211 | ESCO recall (%) | 47.7 [35.2, 60.3] | 51.7 [39.9, 63.9] | +4.0 [-2.4, +10.1] | 0.2268 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 16 [12, 18] | 17 [11, 18] | +1 [-2, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 1.23 [0.90, 1.59] | 0.94 [0.61, 1.29] | -0.29 [-0.46, -0.13] | 0.0008 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 37.0 [29.4, 44.5] | 25.6 [18.6, 32.7] | -11.4 [-17.6, -5.5] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 21.5 [15.4, 28.8] | 20.2 [13.4, 29.0] | -1.3 [-5.9, +4.0] | 0.6428 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 47.7 [35.2, 60.3] | 33.6 [23.0, 45.0] | -14.1 [-23.6, -4.8] | 0.0040 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 16 [12, 18] | 17 [12, 19] | +1 [-2, +4] | 0.8082 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 1.23 [0.90, 1.59] | 2.20 [1.76, 2.78] | +0.97 [+0.42, +1.61] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 37.0 [29.4, 44.5] | 78.7 [71.4, 85.4] | +41.7 [+32.2, +51.4] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 21.5 [15.4, 28.8] | 20.8 [15.7, 26.7] | -0.6 [-7.6, +5.7] | 0.8818 |
| `min_k_enforced` | 211 | ESCO recall (%) | 47.7 [35.2, 60.3] | 81.9 [74.5, 89.0] | +34.2 [+20.2, +47.8] | < 0.0001 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 16 [12, 18] | 14 [11, 18] | -2 [-4, +3] | 1.0000 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 1.23 [0.90, 1.59] | 0.90 [0.66, 1.16] | -0.33 [-0.60, -0.08] | 0.0074 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 37.0 [29.4, 44.5] | 33.2 [25.9, 40.5] | -3.8 [-11.0, +3.3] | 0.3400 |
| `min_k_escape` | 211 | ESCO precision (%) | 21.5 [15.4, 28.8] | 29.9 [21.9, 38.8] | +8.4 [+2.8, +14.8] | 0.0036 |
| `min_k_escape` | 211 | ESCO recall (%) | 47.7 [35.2, 60.3] | 54.4 [41.8, 66.4] | +6.7 [-2.9, +17.1] | 0.2000 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 16 [12, 18] | 14 [9, 16] | -2 [-5, +1] | 0.4354 |

## 89. Qwen3.5-27B (main model alone; not registered), both sets, cutoff 0.7

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 0.36 [0.22, 0.51] | 0.39 [0.26, 0.53] | +0.04 [-0.08, +0.14] | 0.5062 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 20.9 [14.1, 27.8] | 25.3 [18.3, 32.6] | +4.5 [-0.9, +9.9] | 0.1020 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 55.9 [44.3, 68.5] | 56.2 [47.4, 66.2] | +0.4 [-7.6, +8.6] | 0.9502 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 63.8 [51.3, 75.8] | 71.4 [61.5, 80.7] | +7.7 [-0.1, +16.6] | 0.0558 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 12 [6, 14] | 11 [6, 13] | -1 [-4, +3] | 0.9410 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 0.36 [0.22, 0.51] | 0.59 [0.46, 0.74] | +0.24 [+0.11, +0.35] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 20.9 [14.1, 27.8] | 36.1 [29.4, 43.0] | +15.3 [+10.0, +20.8] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 55.9 [44.3, 68.5] | 45.1 [37.6, 53.2] | -10.8 [-19.2, -2.8] | 0.0068 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 63.8 [51.3, 75.8] | 68.9 [59.3, 78.0] | +5.1 [-3.5, +14.7] | 0.2730 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 12 [6, 14] | 13 [7, 14] | +1 [-3, +4] | 0.9262 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 0.36 [0.22, 0.51] | 0.34 [0.23, 0.45] | -0.02 [-0.12, +0.07] | 0.7506 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 20.9 [14.1, 27.8] | 25.1 [18.0, 32.5] | +4.3 [-0.5, +9.3] | 0.0990 |
| `max_k_shown` | 211 | ESCO precision (%) | 55.9 [44.3, 68.5] | 59.2 [49.7, 69.2] | +3.3 [-3.9, +9.8] | 0.3590 |
| `max_k_shown` | 211 | ESCO recall (%) | 63.8 [51.3, 75.8] | 69.1 [57.1, 80.1] | +5.4 [-2.0, +14.6] | 0.2352 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 12 [6, 14] | 11 [6, 12] | -1 [-4, +2] | 0.7378 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 0.36 [0.22, 0.51] | 1.16 [0.97, 1.36] | +0.81 [+0.60, +1.02] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 20.9 [14.1, 27.8] | 60.7 [52.7, 68.1] | +39.8 [+32.1, +47.6] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 55.9 [44.3, 68.5] | 31.8 [25.5, 38.2] | -24.1 [-34.8, -14.5] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 63.8 [51.3, 75.8] | 76.5 [65.7, 86.3] | +12.8 [+3.1, +23.8] | 0.0088 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 12 [6, 14] | 14 [10, 17] | +2 [-1, +8] | 0.1616 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 0.36 [0.22, 0.51] | 0.65 [0.50, 0.82] | +0.30 [+0.15, +0.44] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 20.9 [14.1, 27.8] | 38.9 [31.2, 46.6] | +18.0 [+11.6, +24.9] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 55.9 [44.3, 68.5] | 42.7 [34.8, 51.1] | -13.1 [-22.5, -4.8] | 0.0012 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 63.8 [51.3, 75.8] | 69.1 [57.5, 79.8] | +5.4 [-4.3, +15.6] | 0.3230 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 12 [6, 14] | 13 [8, 15] | +1 [-2, +5] | 0.7348 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 0.36 [0.22, 0.51] | 1.48 [1.29, 1.68] | +1.13 [+0.92, +1.33] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 20.9 [14.1, 27.8] | 74.9 [68.0, 81.6] | +54.0 [+46.1, +62.2] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 55.9 [44.3, 68.5] | 27.0 [21.5, 32.7] | -28.8 [-39.5, -19.6] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO recall (%) | 63.8 [51.3, 75.8] | 77.9 [67.1, 87.4] | +14.1 [+4.6, +25.0] | 0.0026 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 12 [6, 14] | 16 [11, 17] | +4 [+0, +9] | 0.0824 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 0.36 [0.22, 0.51] | 0.72 [0.53, 0.90] | +0.36 [+0.19, +0.53] | < 0.0001 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 20.9 [14.1, 27.8] | 38.4 [30.4, 46.4] | +17.5 [+10.6, +24.9] | < 0.0001 |
| `min_k_escape` | 211 | ESCO precision (%) | 55.9 [44.3, 68.5] | 43.0 [35.0, 52.0] | -12.9 [-22.6, -4.0] | 0.0042 |
| `min_k_escape` | 211 | ESCO recall (%) | 63.8 [51.3, 75.8] | 76.5 [66.4, 85.9] | +12.8 [+2.7, +23.8] | 0.0108 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 12 [6, 14] | 13 [7, 15] | +1 [-3, +5] | 0.7666 |

## 90. Gemma 4 31B (main model alone; not registered), both sets, cutoff 0.7

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 0.28 [0.15, 0.43] | 0.30 [0.20, 0.42] | +0.02 [-0.06, +0.10] | 0.5608 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 17.5 [10.7, 24.8] | 21.4 [14.9, 28.3] | +3.9 [-0.0, +8.2] | 0.0552 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 65.7 [54.2, 78.8] | 64.9 [55.5, 74.6] | -0.8 [-8.1, +5.4] | 0.7716 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 75.8 [67.5, 84.2] | 79.3 [71.8, 86.8] | +3.5 [+0.7, +6.6] | 0.0132 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 9 [4, 12] | 10 [4, 11] | +1 [-4, +2] | 1.0000 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 0.28 [0.15, 0.43] | 1.01 [0.85, 1.18] | +0.73 [+0.58, +0.90] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 17.5 [10.7, 24.8] | 50.1 [43.4, 56.8] | +32.6 [+25.8, +39.6] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 65.7 [54.2, 78.8] | 37.5 [31.2, 44.0] | -28.2 [-39.9, -18.0] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 75.8 [67.5, 84.2] | 86.2 [80.2, 91.6] | +10.3 [+4.6, +16.2] | < 0.0001 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 9 [4, 12] | 12 [7, 14] | +3 [-2, +7] | 0.4358 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 0.28 [0.15, 0.43] | 0.25 [0.15, 0.36] | -0.03 [-0.12, +0.04] | 0.5870 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 17.5 [10.7, 24.8] | 17.5 [11.2, 24.2] | +0.0 [-3.8, +3.6] | 1.0000 |
| `max_k_shown` | 211 | ESCO precision (%) | 65.7 [54.2, 78.8] | 69.5 [60.4, 79.1] | +3.8 [-2.4, +10.8] | 0.3140 |
| `max_k_shown` | 211 | ESCO recall (%) | 75.8 [67.5, 84.2] | 81.2 [73.6, 88.5] | +5.4 [+1.3, +9.9] | 0.0126 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 9 [4, 12] | 9 [3, 10] | +0 [-5, +1] | 0.8452 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 0.28 [0.15, 0.43] | 1.84 [1.60, 2.09] | +1.56 [+1.31, +1.83] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 17.5 [10.7, 24.8] | 75.8 [68.9, 82.4] | +58.3 [+49.8, +66.7] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 65.7 [54.2, 78.8] | 24.2 [19.1, 29.7] | -41.5 [-54.0, -30.8] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 75.8 [67.5, 84.2] | 83.2 [76.3, 89.9] | +7.4 [+1.4, +13.5] | 0.0162 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 9 [4, 12] | 15 [11, 17] | +6 [+1, +11] | 0.0220 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 0.28 [0.15, 0.43] | 0.28 [0.16, 0.43] | +0.00 [-0.07, +0.06] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 17.5 [10.7, 24.8] | 18.0 [11.5, 25.0] | +0.5 [-4.3, +5.1] | 0.9074 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 65.7 [54.2, 78.8] | 66.1 [55.4, 77.8] | +0.4 [-5.4, +6.5] | 0.9306 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 75.8 [67.5, 84.2] | 77.2 [69.3, 85.1] | +1.3 [-2.7, +5.6] | 0.6546 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 9 [4, 12] | 10 [4, 12] | +1 [-3, +2] | 1.0000 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 0.28 [0.15, 0.43] | 1.94 [1.73, 2.15] | +1.66 [+1.44, +1.89] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 17.5 [10.7, 24.8] | 86.3 [80.6, 91.4] | +68.7 [+60.8, +76.2] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 65.7 [54.2, 78.8] | 23.6 [18.9, 28.4] | -42.1 [-54.5, -31.4] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO recall (%) | 75.8 [67.5, 84.2] | 84.6 [77.8, 91.2] | +8.7 [+3.0, +14.9] | 0.0012 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 9 [4, 12] | 15 [11, 18] | +6 [+2, +12] | 0.0138 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 0.28 [0.15, 0.43] | 0.53 [0.36, 0.70] | +0.25 [+0.11, +0.39] | 0.0002 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 17.5 [10.7, 24.8] | 29.4 [21.7, 37.3] | +11.8 [+4.6, +19.4] | 0.0016 |
| `min_k_escape` | 211 | ESCO precision (%) | 65.7 [54.2, 78.8] | 50.2 [41.7, 60.1] | -15.5 [-26.6, -5.7] | 0.0012 |
| `min_k_escape` | 211 | ESCO recall (%) | 75.8 [67.5, 84.2] | 75.2 [65.7, 83.7] | -0.7 [-10.7, +8.2] | 0.9604 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 9 [4, 12] | 13 [7, 13] | +4 [-2, +6] | 0.4876 |

## 91. Olmo 3.1 32B (main model alone; not registered), both sets, cutoff 0.7

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 2.77 [2.20, 3.39] | 1.54 [1.30, 1.79] | -1.23 [-1.69, -0.82] | < 0.0001 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 59.2 [50.7, 67.8] | 63.6 [56.6, 70.5] | +4.4 [-2.0, +10.5] | 0.1822 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 14.0 [10.5, 18.2] | 19.7 [15.2, 24.5] | +5.7 [+3.4, +8.1] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 63.8 [54.1, 73.5] | 53.6 [44.4, 63.0] | -10.2 [-16.2, -4.2] | 0.0008 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 16 [12, 18] | 14 [11, 17] | -2 [-5, +1] | 0.4988 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 2.77 [2.20, 3.39] | 1.41 [1.23, 1.59] | -1.36 [-1.88, -0.90] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 59.2 [50.7, 67.8] | 67.3 [61.0, 73.4] | +8.1 [+1.2, +14.5] | 0.0224 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 14.0 [10.5, 18.2] | 20.4 [15.8, 25.2] | +6.4 [+3.6, +9.3] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 63.8 [54.1, 73.5] | 51.1 [42.4, 60.4] | -12.6 [-19.2, -5.7] | < 0.0001 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 16 [12, 18] | 14 [11, 17] | -2 [-5, +2] | 0.5908 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 2.77 [2.20, 3.39] | 1.24 [1.00, 1.49] | -1.54 [-2.01, -1.10] | < 0.0001 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 59.2 [50.7, 67.8] | 54.0 [45.8, 62.4] | -5.2 [-11.5, +1.0] | 0.1110 |
| `max_k_shown` | 211 | ESCO precision (%) | 14.0 [10.5, 18.2] | 23.0 [17.6, 29.1] | +9.0 [+5.6, +12.8] | < 0.0001 |
| `max_k_shown` | 211 | ESCO recall (%) | 63.8 [54.1, 73.5] | 52.3 [42.4, 62.6] | -11.4 [-18.2, -4.4] | 0.0026 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 16 [12, 18] | 14 [11, 17] | -2 [-4, +2] | 0.7766 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 2.77 [2.20, 3.39] | 2.80 [2.29, 3.34] | +0.02 [-0.27, +0.31] | 0.8882 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 59.2 [50.7, 67.8] | 69.2 [61.4, 76.9] | +10.0 [+4.5, +15.6] | 0.0004 |
| `min_k_shown` | 211 | ESCO precision (%) | 14.0 [10.5, 18.2] | 13.4 [10.1, 17.3] | -0.6 [-2.5, +1.0] | 0.5124 |
| `min_k_shown` | 211 | ESCO recall (%) | 63.8 [54.1, 73.5] | 61.1 [52.1, 70.3] | -2.7 [-8.6, +2.5] | 0.4156 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 16 [12, 18] | 17 [12, 18] | +1 [-1, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 2.77 [2.20, 3.39] | 0.40 [0.22, 0.60] | -2.37 [-2.94, -1.86] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 59.2 [50.7, 67.8] | 15.2 [9.5, 21.4] | -44.1 [-52.1, -36.2] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 14.0 [10.5, 18.2] | 28.8 [18.3, 43.1] | +14.8 [+5.5, +27.6] | 0.0008 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 63.8 [54.1, 73.5] | 22.8 [13.9, 32.5] | -40.9 [-52.1, -30.0] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 16 [12, 18] | 15 [11, 17] | -1 [-5, +2] | 0.7700 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 2.77 [2.20, 3.39] | 3.54 [3.05, 4.07] | +0.77 [+0.29, +1.27] | 0.0012 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 59.2 [50.7, 67.8] | 92.4 [87.9, 96.5] | +33.2 [+24.4, +41.8] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 14.0 [10.5, 18.2] | 11.4 [8.6, 14.5] | -2.6 [-5.0, -0.6] | 0.0068 |
| `min_k_enforced` | 211 | ESCO recall (%) | 63.8 [54.1, 73.5] | 64.4 [54.9, 74.1] | +0.7 [-5.4, +7.1] | 0.9236 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 16 [12, 18] | 16 [13, 18] | +0 [-2, +3] | 1.0000 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 2.77 [2.20, 3.39] | 2.40 [1.91, 2.94] | -0.37 [-0.80, +0.07] | 0.0976 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 59.2 [50.7, 67.8] | 58.8 [50.2, 67.3] | -0.5 [-9.6, +8.4] | 0.9494 |
| `min_k_escape` | 211 | ESCO precision (%) | 14.0 [10.5, 18.2] | 14.7 [10.9, 19.2] | +0.7 [-1.3, +2.9] | 0.4880 |
| `min_k_escape` | 211 | ESCO recall (%) | 63.8 [54.1, 73.5] | 58.4 [48.2, 68.8] | -5.4 [-12.4, +1.6] | 0.1560 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 16 [12, 18] | 16 [12, 18] | +0 [-3, +2] | 1.0000 |

## 92. Ministral 3 14B (main model alone; not registered), both sets, cutoff 0.7

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 2.09 [1.59, 2.61] | 1.15 [0.96, 1.34] | -0.94 [-1.37, -0.53] | < 0.0001 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 56.4 [47.5, 65.0] | 57.1 [50.0, 64.0] | +0.7 [-6.9, +8.6] | 0.8808 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 18.8 [13.8, 25.3] | 28.0 [21.8, 34.6] | +9.2 [+4.4, +13.7] | 0.0002 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 68.5 [57.1, 79.5] | 63.1 [52.8, 73.5] | -5.4 [-13.8, +3.8] | 0.2370 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 14 [12, 19] | 14 [8, 15] | +0 [-8, +0] | 0.0930 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 2.09 [1.59, 2.61] | 1.33 [1.14, 1.51] | -0.76 [-1.21, -0.33] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 56.4 [47.5, 65.0] | 63.5 [56.8, 70.1] | +7.1 [+0.4, +13.9] | 0.0388 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 18.8 [13.8, 25.3] | 24.8 [19.7, 30.3] | +6.0 [+1.2, +10.0] | 0.0166 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 68.5 [57.1, 79.5] | 62.0 [52.4, 72.2] | -6.4 [-14.6, +0.8] | 0.0914 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 14 [12, 19] | 14 [10, 16] | +0 [-6, +1] | 0.2046 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 2.09 [1.59, 2.61] | 1.03 [0.77, 1.32] | -1.06 [-1.44, -0.69] | < 0.0001 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 56.4 [47.5, 65.0] | 45.0 [36.7, 53.5] | -11.4 [-18.1, -5.2] | 0.0004 |
| `max_k_shown` | 211 | ESCO precision (%) | 18.8 [13.8, 25.3] | 30.9 [23.2, 39.9] | +12.1 [+7.7, +17.4] | < 0.0001 |
| `max_k_shown` | 211 | ESCO recall (%) | 68.5 [57.1, 79.5] | 65.1 [53.5, 76.8] | -3.4 [-9.2, +2.1] | 0.2912 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 14 [12, 19] | 13 [9, 17] | -1 [-6, +1] | 0.2518 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 2.09 [1.59, 2.61] | 2.35 [1.90, 2.85] | +0.27 [-0.01, +0.53] | 0.0622 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 56.4 [47.5, 65.0] | 70.6 [62.7, 78.3] | +14.2 [+8.5, +20.3] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 18.8 [13.8, 25.3] | 16.8 [12.5, 21.7] | -2.0 [-4.7, +0.1] | 0.0590 |
| `min_k_shown` | 211 | ESCO recall (%) | 68.5 [57.1, 79.5] | 67.1 [55.9, 77.7] | -1.3 [-6.6, +5.7] | 0.6756 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 14 [12, 19] | 16 [12, 19] | +2 [-3, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 2.09 [1.59, 2.61] | 0.32 [0.18, 0.48] | -1.77 [-2.28, -1.29] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 56.4 [47.5, 65.0] | 18.0 [11.6, 24.9] | -38.4 [-47.4, -29.3] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 18.8 [13.8, 25.3] | 51.8 [37.8, 66.3] | +33.0 [+21.2, +46.0] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 68.5 [57.1, 79.5] | 48.3 [35.5, 61.1] | -20.1 [-29.8, -11.3] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 14 [12, 19] | 12 [7, 15] | -2 [-9, -1] | 0.0376 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 2.09 [1.59, 2.61] | 2.11 [1.81, 2.44] | +0.02 [-0.45, +0.46] | 0.9194 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 56.4 [47.5, 65.0] | 80.6 [74.4, 86.3] | +24.2 [+15.7, +32.9] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 18.8 [13.8, 25.3] | 17.9 [13.9, 22.2] | -0.9 [-5.6, +2.9] | 0.6546 |
| `min_k_enforced` | 211 | ESCO recall (%) | 68.5 [57.1, 79.5] | 65.1 [55.1, 75.3] | -3.4 [-12.3, +6.3] | 0.5204 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 14 [12, 19] | 16 [12, 18] | +2 [-4, +3] | 1.0000 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 2.09 [1.59, 2.61] | 0.29 [0.11, 0.53] | -1.80 [-2.35, -1.29] | < 0.0001 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 56.4 [47.5, 65.0] | 10.0 [5.0, 15.7] | -46.4 [-56.7, -35.8] | < 0.0001 |
| `min_k_escape` | 211 | ESCO precision (%) | 18.8 [13.8, 25.3] | 29.9 [15.8, 51.7] | +11.1 [-3.2, +32.9] | 0.1418 |
| `min_k_escape` | 211 | ESCO recall (%) | 68.5 [57.1, 79.5] | 17.4 [9.6, 26.2] | -51.0 [-64.2, -37.7] | < 0.0001 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 14 [12, 19] | 16 [12, 19] | +2 [-5, +4] | 1.0000 |

## 93. gpt-oss-20b (main model alone; not registered), both sets, cutoff 0.7

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 1.02 [0.76, 1.30] | 1.13 [0.99, 1.27] | +0.11 [-0.12, +0.33] | 0.3220 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 46.4 [37.2, 55.8] | 60.9 [54.8, 66.9] | +14.5 [+6.5, +22.8] | 0.0008 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 32.4 [25.5, 40.3] | 29.7 [24.1, 35.3] | -2.7 [-8.2, +1.8] | 0.2616 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 69.1 [58.1, 79.4] | 67.7 [60.3, 75.1] | -1.5 [-10.3, +8.1] | 0.7552 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 13 [10, 17] | 14 [8, 15] | +1 [-6, +1] | 0.3288 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 1.02 [0.76, 1.30] | 1.33 [1.18, 1.47] | +0.31 [+0.08, +0.53] | 0.0114 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 46.4 [37.2, 55.8] | 70.6 [65.5, 75.7] | +24.2 [+16.1, +32.4] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 32.4 [25.5, 40.3] | 25.1 [20.1, 30.1] | -7.3 [-13.0, -2.7] | 0.0008 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 69.1 [58.1, 79.4] | 62.8 [55.1, 70.8] | -6.3 [-15.9, +3.9] | 0.2274 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 13 [10, 17] | 14 [9, 16] | +1 [-5, +2] | 0.7054 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 1.02 [0.76, 1.30] | 1.04 [0.86, 1.22] | +0.02 [-0.25, +0.28] | 0.8736 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 46.4 [37.2, 55.8] | 56.4 [48.1, 64.7] | +10.0 [+1.4, +18.9] | 0.0232 |
| `max_k_shown` | 211 | ESCO precision (%) | 32.4 [25.5, 40.3] | 30.5 [24.0, 37.4] | -1.9 [-7.8, +3.2] | 0.4730 |
| `max_k_shown` | 211 | ESCO recall (%) | 69.1 [58.1, 79.4] | 64.4 [55.1, 74.0] | -4.7 [-13.7, +4.6] | 0.3634 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 13 [10, 17] | 13 [10, 16] | +0 [-4, +2] | 0.7908 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 1.02 [0.76, 1.30] | 1.65 [1.43, 1.88] | +0.64 [+0.39, +0.87] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 46.4 [37.2, 55.8] | 73.0 [66.3, 79.3] | +26.5 [+17.8, +35.7] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 32.4 [25.5, 40.3] | 23.6 [19.1, 28.4] | -8.8 [-14.4, -4.0] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 69.1 [58.1, 79.4] | 72.5 [64.0, 81.0] | +3.4 [-4.6, +11.9] | 0.4570 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 13 [10, 17] | 14 [11, 17] | +1 [-3, +3] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 1.02 [0.76, 1.30] | 1.36 [1.11, 1.63] | +0.34 [+0.07, +0.62] | 0.0164 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 46.4 [37.2, 55.8] | 59.7 [51.9, 67.8] | +13.3 [+2.9, +23.4] | 0.0114 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 32.4 [25.5, 40.3] | 24.9 [19.2, 30.9] | -7.5 [-13.8, -2.0] | 0.0060 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 69.1 [58.1, 79.4] | 63.8 [53.4, 73.5] | -5.4 [-14.3, +3.5] | 0.2662 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 13 [10, 17] | 14 [11, 17] | +1 [-3, +3] | 1.0000 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 1.02 [0.76, 1.30] | 1.71 [1.46, 1.96] | +0.69 [+0.44, +0.94] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 46.4 [37.2, 55.8] | 74.4 [67.5, 81.1] | +28.0 [+17.8, +38.2] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 32.4 [25.5, 40.3] | 23.9 [19.0, 29.2] | -8.5 [-14.2, -3.6] | 0.0004 |
| `min_k_enforced` | 211 | ESCO recall (%) | 69.1 [58.1, 79.4] | 75.8 [67.2, 84.4] | +6.7 [-2.0, +16.5] | 0.1538 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 13 [10, 17] | 14 [11, 17] | +1 [-3, +3] | 1.0000 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 1.02 [0.76, 1.30] | 1.18 [0.88, 1.50] | +0.16 [-0.12, +0.45] | 0.2724 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 46.4 [37.2, 55.8] | 46.4 [38.0, 54.6] | +0.0 [-9.2, +9.2] | 1.0000 |
| `min_k_escape` | 211 | ESCO precision (%) | 32.4 [25.5, 40.3] | 25.4 [19.3, 32.8] | -6.9 [-12.8, -1.4] | 0.0152 |
| `min_k_escape` | 211 | ESCO recall (%) | 69.1 [58.1, 79.4] | 57.0 [46.6, 67.5] | -12.1 [-22.8, -0.7] | 0.0442 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 13 [10, 17] | 15 [10, 17] | +2 [-4, +3] | 1.0000 |

## 94. GPT-6 Luna (Azure), both sets, cutoff 0.7

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 0.52 [0.33, 0.73] | 0.49 [0.35, 0.65] | -0.02 [-0.18, +0.13] | 0.7818 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 25.6 [18.1, 33.5] | 30.3 [22.6, 38.1] | +4.7 [-3.0, +12.7] | 0.2628 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 46.8 [35.2, 60.0] | 50.0 [40.4, 60.5] | +3.2 [-5.8, +10.5] | 0.4538 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 64.4 [54.2, 75.0] | 69.8 [61.1, 78.6] | +5.4 [-1.4, +11.9] | 0.1448 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 11 [7, 15] | 11 [7, 13] | +0 [-5, +3] | 0.7166 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 0.52 [0.33, 0.73] | 0.84 [0.69, 1.01] | +0.33 [+0.14, +0.51] | 0.0010 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 25.6 [18.1, 33.5] | 50.2 [42.6, 57.7] | +24.6 [+16.2, +33.3] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 46.8 [35.2, 60.0] | 38.6 [31.4, 45.7] | -8.2 [-18.5, -0.1] | 0.0452 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 64.4 [54.2, 75.0] | 75.2 [66.9, 83.2] | +10.7 [+4.3, +17.2] | 0.0008 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 11 [7, 15] | 12 [8, 14] | +1 [-4, +4] | 1.0000 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 0.52 [0.33, 0.73] | 0.32 [0.20, 0.45] | -0.19 [-0.37, -0.04] | 0.0100 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 25.6 [18.1, 33.5] | 19.0 [12.9, 25.2] | -6.6 [-13.9, +0.4] | 0.0720 |
| `max_k_shown` | 211 | ESCO precision (%) | 46.8 [35.2, 60.0] | 57.8 [46.4, 69.3] | +10.9 [+2.2, +19.4] | 0.0146 |
| `max_k_shown` | 211 | ESCO recall (%) | 64.4 [54.2, 75.0] | 62.4 [50.3, 73.8] | -2.0 [-11.8, +7.3] | 0.7054 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 11 [7, 15] | 10 [6, 12] | -1 [-6, +2] | 0.3924 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 0.52 [0.33, 0.73] | 0.96 [0.74, 1.19] | +0.44 [+0.25, +0.65] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 25.6 [18.1, 33.5] | 45.5 [37.9, 53.1] | +19.9 [+12.5, +27.6] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 46.8 [35.2, 60.0] | 34.8 [26.7, 43.8] | -12.0 [-21.8, -4.4] | 0.0010 |
| `min_k_shown` | 211 | ESCO recall (%) | 64.4 [54.2, 75.0] | 72.5 [62.6, 81.8] | +8.1 [+2.6, +14.0] | 0.0006 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 11 [7, 15] | 13 [9, 16] | +2 [-2, +6] | 0.7280 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 0.52 [0.33, 0.73] | 0.80 [0.59, 1.02] | +0.28 [+0.09, +0.49] | 0.0028 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 25.6 [18.1, 33.5] | 38.9 [31.3, 46.5] | +13.3 [+6.2, +20.5] | 0.0002 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 46.8 [35.2, 60.0] | 38.9 [29.9, 48.9] | -7.9 [-17.7, -0.2] | 0.0418 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 64.4 [54.2, 75.0] | 71.8 [62.4, 81.0] | +7.4 [+2.6, +12.8] | 0.0016 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 11 [7, 15] | 12 [8, 15] | +1 [-3, +5] | 1.0000 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 0.52 [0.33, 0.73] | 1.55 [1.32, 1.81] | +1.04 [+0.80, +1.30] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 25.6 [18.1, 33.5] | 68.7 [61.5, 75.5] | +43.1 [+33.8, +51.9] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 46.8 [35.2, 60.0] | 25.1 [19.5, 31.0] | -21.7 [-32.6, -13.2] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO recall (%) | 64.4 [54.2, 75.0] | 73.8 [64.4, 83.3] | +9.4 [+3.6, +16.0] | 0.0008 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 11 [7, 15] | 15 [11, 17] | +4 [-1, +8] | 0.2554 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 0.52 [0.33, 0.73] | 0.96 [0.75, 1.20] | +0.45 [+0.25, +0.67] | < 0.0001 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 25.6 [18.1, 33.5] | 49.3 [41.8, 56.9] | +23.7 [+15.0, +32.8] | < 0.0001 |
| `min_k_escape` | 211 | ESCO precision (%) | 46.8 [35.2, 60.0] | 34.3 [26.4, 43.0] | -12.5 [-22.7, -4.8] | 0.0002 |
| `min_k_escape` | 211 | ESCO recall (%) | 64.4 [54.2, 75.0] | 71.1 [61.6, 80.6] | +6.7 [+0.7, +13.0] | 0.0322 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 11 [7, 15] | 11 [9, 16] | +0 [-2, +6] | 0.7622 |

## 95. GPT-6 Sol (Azure), both sets, cutoff 0.7

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 0.63 [0.43, 0.86] | 0.49 [0.36, 0.64] | -0.13 [-0.31, +0.02] | 0.1078 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 32.7 [25.0, 40.7] | 31.8 [24.3, 39.6] | -0.9 [-7.1, +5.1] | 0.8398 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 44.8 [34.6, 55.9] | 50.2 [40.4, 60.4] | +5.5 [-1.8, +12.3] | 0.1392 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 71.8 [60.7, 82.3] | 70.5 [60.0, 80.7] | -1.3 [-5.3, +2.1] | 0.6112 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 12 [8, 16] | 11 [7, 14] | -1 [-5, +2] | 0.6472 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 0.63 [0.43, 0.86] | 1.41 [1.21, 1.61] | +0.79 [+0.54, +1.02] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 32.7 [25.0, 40.7] | 70.6 [62.9, 78.0] | +37.9 [+29.2, +46.9] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 44.8 [34.6, 55.9] | 28.2 [22.2, 34.3] | -16.6 [-25.5, -8.9] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 71.8 [60.7, 82.3] | 78.5 [70.1, 86.7] | +6.7 [+0.7, +13.0] | 0.0302 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 12 [8, 16] | 14 [11, 17] | +2 [-2, +7] | 0.4102 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 0.63 [0.43, 0.86] | 0.42 [0.29, 0.56] | -0.21 [-0.38, -0.06] | 0.0052 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 32.7 [25.0, 40.7] | 25.6 [19.1, 32.5] | -7.1 [-13.4, -1.4] | 0.0206 |
| `max_k_shown` | 211 | ESCO precision (%) | 44.8 [34.6, 55.9] | 55.3 [45.0, 65.7] | +10.6 [+3.7, +17.1] | 0.0034 |
| `max_k_shown` | 211 | ESCO recall (%) | 71.8 [60.7, 82.3] | 73.2 [62.2, 83.6] | +1.3 [+0.0, +3.6] | 0.2648 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 12 [8, 16] | 10 [5, 12] | -2 [-7, +0] | 0.1192 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 0.63 [0.43, 0.86] | 1.13 [0.88, 1.40] | +0.50 [+0.32, +0.71] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 32.7 [25.0, 40.7] | 51.7 [43.4, 59.9] | +19.0 [+12.3, +26.1] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 44.8 [34.6, 55.9] | 32.0 [24.6, 39.9] | -12.8 [-20.2, -6.6] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 71.8 [60.7, 82.3] | 75.2 [64.5, 85.1] | +3.4 [-1.3, +7.9] | 0.1962 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 12 [8, 16] | 14 [9, 17] | +2 [-2, +5] | 0.6090 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 0.63 [0.43, 0.86] | 0.82 [0.60, 1.07] | +0.20 [+0.03, +0.38] | 0.0252 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 32.7 [25.0, 40.7] | 39.3 [31.5, 47.6] | +6.6 [+0.9, +12.9] | 0.0328 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 44.8 [34.6, 55.9] | 39.4 [30.7, 48.5] | -5.4 [-12.6, +0.8] | 0.0932 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 71.8 [60.7, 82.3] | 75.8 [64.8, 86.0] | +4.0 [-0.8, +10.4] | 0.1954 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 12 [8, 16] | 13 [8, 16] | +1 [-2, +4] | 1.0000 |

## 96. DeepSeek V3.2 (Bedrock), both sets, cutoff 0.7

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 0.63 [0.42, 0.84] | 0.91 [0.76, 1.05] | +0.28 [+0.07, +0.48] | 0.0100 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 30.3 [22.0, 38.8] | 49.7 [42.9, 56.3] | +19.3 [+12.5, +26.6] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 41.6 [32.4, 52.8] | 35.3 [28.6, 42.1] | -6.3 [-14.7, +0.3] | 0.0614 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 63.1 [52.7, 73.4] | 69.9 [61.6, 78.6] | +6.8 [-0.8, +15.2] | 0.0808 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 12 [8, 16] | 11 [8, 15] | -1 [-4, +3] | 0.8644 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 0.63 [0.42, 0.84] | 0.93 [0.80, 1.07] | +0.31 [+0.09, +0.51] | 0.0060 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 30.3 [22.0, 38.8] | 53.4 [46.8, 59.8] | +23.0 [+15.1, +31.4] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 41.6 [32.4, 52.8] | 34.4 [27.7, 41.0] | -7.2 [-15.5, -0.6] | 0.0296 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 63.1 [52.7, 73.4] | 69.3 [60.7, 78.0] | +6.2 [-2.0, +14.6] | 0.1492 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 12 [8, 16] | 11 [8, 14] | -1 [-5, +2] | 0.7432 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 0.63 [0.42, 0.84] | 0.77 [0.61, 0.93] | +0.14 [-0.06, +0.34] | 0.1744 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 30.3 [22.0, 38.8] | 44.1 [36.1, 51.9] | +13.7 [+6.2, +21.9] | 0.0006 |
| `max_k_shown` | 211 | ESCO precision (%) | 41.6 [32.4, 52.8] | 38.9 [30.8, 47.0] | -2.7 [-11.1, +4.1] | 0.4352 |
| `max_k_shown` | 211 | ESCO recall (%) | 63.1 [52.7, 73.4] | 69.1 [59.5, 78.4] | +6.0 [-1.5, +14.1] | 0.1520 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 12 [8, 16] | 13 [8, 15] | +1 [-4, +3] | 1.0000 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 0.63 [0.42, 0.84] | 1.93 [1.61, 2.29] | +1.31 [+0.98, +1.68] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 30.3 [22.0, 38.8] | 73.0 [66.0, 79.6] | +42.7 [+34.1, +51.6] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 41.6 [32.4, 52.8] | 21.2 [16.4, 26.7] | -20.4 [-29.7, -13.1] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 63.1 [52.7, 73.4] | 73.8 [65.4, 82.1] | +10.7 [+3.6, +18.1] | 0.0040 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 12 [8, 16] | 14 [12, 18] | +2 [-1, +7] | 0.2890 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 0.63 [0.42, 0.84] | 1.00 [0.79, 1.23] | +0.38 [+0.12, +0.65] | 0.0040 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 30.3 [22.0, 38.8] | 46.0 [38.3, 53.5] | +15.6 [+6.9, +24.6] | 0.0002 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 41.6 [32.4, 52.8] | 32.1 [25.5, 39.5] | -9.5 [-19.3, -1.6] | 0.0166 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 63.1 [52.7, 73.4] | 67.1 [57.3, 76.6] | +4.0 [-3.6, +11.5] | 0.3394 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 12 [8, 16] | 13 [10, 16] | +1 [-3, +4] | 0.9064 |

## 97. gpt-oss-120b (Bedrock), both sets, cutoff 0.7

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 1.09 [0.82, 1.40] | 1.13 [0.96, 1.31] | +0.04 [-0.22, +0.28] | 0.7076 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 49.3 [40.3, 58.1] | 55.1 [48.5, 61.6] | +5.8 [-1.2, +12.9] | 0.1018 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 33.3 [26.0, 41.6] | 30.7 [24.9, 36.7] | -2.7 [-8.2, +2.1] | 0.2842 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 77.2 [67.6, 86.1] | 71.0 [63.3, 78.8] | -6.2 [-11.9, -0.5] | 0.0350 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 14 [10, 17] | 13 [8, 15] | -1 [-5, +2] | 0.5786 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 1.09 [0.82, 1.40] | 1.51 [1.34, 1.68] | +0.42 [+0.15, +0.67] | 0.0038 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 49.3 [40.3, 58.1] | 69.4 [63.6, 74.8] | +20.1 [+12.6, +27.8] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 33.3 [26.0, 41.6] | 24.4 [19.6, 29.2] | -8.9 [-14.9, -4.0] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 77.2 [67.6, 86.1] | 69.0 [61.2, 76.9] | -8.2 [-14.4, -2.0] | 0.0102 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 14 [10, 17] | 12 [9, 16] | -2 [-4, +3] | 0.8840 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 1.09 [0.82, 1.40] | 1.15 [0.95, 1.36] | +0.06 [-0.21, +0.31] | 0.6406 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 49.3 [40.3, 58.1] | 55.9 [48.2, 63.6] | +6.6 [-0.9, +14.6] | 0.0938 |
| `max_k_shown` | 211 | ESCO precision (%) | 33.3 [26.0, 41.6] | 29.4 [23.3, 36.0] | -4.0 [-9.6, +1.1] | 0.1194 |
| `max_k_shown` | 211 | ESCO recall (%) | 77.2 [67.6, 86.1] | 67.8 [58.3, 77.2] | -9.4 [-16.5, -2.3] | 0.0136 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 14 [10, 17] | 14 [10, 17] | +0 [-3, +3] | 1.0000 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 1.09 [0.82, 1.40] | 1.82 [1.60, 2.04] | +0.73 [+0.47, +0.98] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 49.3 [40.3, 58.1] | 80.1 [73.3, 86.4] | +30.8 [+21.5, +40.1] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 33.3 [26.0, 41.6] | 22.2 [17.4, 27.0] | -11.2 [-17.1, -6.4] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 77.2 [67.6, 86.1] | 73.2 [64.1, 81.7] | -4.0 [-11.1, +2.9] | 0.3122 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 14 [10, 17] | 13 [10, 17] | -1 [-3, +4] | 0.9976 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 1.09 [0.82, 1.40] | 1.43 [1.16, 1.72] | +0.34 [+0.12, +0.56] | 0.0012 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 49.3 [40.3, 58.1] | 60.2 [52.2, 68.1] | +10.9 [+3.7, +18.8] | 0.0038 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 33.3 [26.0, 41.6] | 26.9 [20.9, 33.4] | -6.4 [-11.6, -2.4] | 0.0006 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 77.2 [67.6, 86.1] | 74.5 [64.8, 83.5] | -2.7 [-9.0, +3.3] | 0.4510 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 14 [10, 17] | 14 [10, 17] | +0 [-2, +3] | 1.0000 |

## 98. gpt-oss-20b (Bedrock), both sets, cutoff 0.7

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 1.14 [0.85, 1.45] | 1.13 [0.98, 1.27] | -0.01 [-0.28, +0.25] | 0.9596 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 43.6 [35.4, 51.9] | 60.9 [55.0, 66.4] | +17.3 [+9.5, +25.1] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 28.4 [21.5, 36.7] | 30.1 [24.4, 35.8] | +1.8 [-4.5, +7.1] | 0.5818 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 63.8 [52.2, 75.5] | 68.7 [61.1, 76.4] | +5.0 [-3.4, +14.0] | 0.2664 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 14 [10, 17] | 13 [8, 15] | -1 [-6, +1] | 0.3840 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 1.14 [0.85, 1.45] | 1.37 [1.23, 1.52] | +0.24 [-0.04, +0.50] | 0.0944 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 43.6 [35.4, 51.9] | 70.5 [65.3, 75.7] | +26.9 [+19.3, +34.7] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 28.4 [21.5, 36.7] | 23.6 [19.1, 28.3] | -4.7 [-11.2, +0.5] | 0.0812 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 63.8 [52.2, 75.5] | 60.1 [52.6, 68.5] | -3.6 [-12.4, +5.7] | 0.4382 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 14 [10, 17] | 15 [10, 16] | +1 [-4, +2] | 0.9106 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 1.14 [0.85, 1.45] | 0.96 [0.79, 1.13] | -0.18 [-0.46, +0.09] | 0.2056 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 43.6 [35.4, 51.9] | 55.0 [47.0, 62.7] | +11.4 [+2.9, +20.0] | 0.0110 |
| `max_k_shown` | 211 | ESCO precision (%) | 28.4 [21.5, 36.7] | 32.7 [26.2, 39.6] | +4.3 [-2.4, +10.3] | 0.1980 |
| `max_k_shown` | 211 | ESCO recall (%) | 63.8 [52.2, 75.5] | 65.8 [57.1, 74.8] | +2.0 [-6.9, +11.8] | 0.7362 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 14 [10, 17] | 13 [9, 15] | -1 [-5, +2] | 0.5112 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 1.14 [0.85, 1.45] | 1.73 [1.46, 2.01] | +0.59 [+0.36, +0.81] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 43.6 [35.4, 51.9] | 74.9 [67.9, 81.5] | +31.3 [+23.1, +39.7] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 28.4 [21.5, 36.7] | 22.7 [18.1, 27.8] | -5.6 [-11.4, -0.9] | 0.0184 |
| `min_k_shown` | 211 | ESCO recall (%) | 63.8 [52.2, 75.5] | 71.8 [63.4, 80.4] | +8.1 [-1.4, +18.6] | 0.1132 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 14 [10, 17] | 15 [10, 16] | +1 [-3, +3] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 1.14 [0.85, 1.45] | 1.34 [1.07, 1.64] | +0.20 [-0.06, +0.46] | 0.1324 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 43.6 [35.4, 51.9] | 58.3 [50.0, 66.2] | +14.7 [+6.0, +23.8] | 0.0012 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 28.4 [21.5, 36.7] | 23.7 [18.1, 30.3] | -4.6 [-10.2, +0.3] | 0.0688 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 63.8 [52.2, 75.5] | 59.1 [49.7, 68.5] | -4.7 [-14.3, +4.7] | 0.3814 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 14 [10, 17] | 15 [11, 18] | +1 [-2, +4] | 0.7128 |

## 99. Grok 4.3 (Bedrock), both sets, cutoff 0.7

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 0.35 [0.19, 0.53] | 0.40 [0.26, 0.55] | +0.05 [-0.13, +0.23] | 0.5644 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 17.1 [10.7, 24.0] | 23.2 [16.4, 30.3] | +6.2 [+0.5, +12.1] | 0.0420 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 50.7 [37.7, 66.4] | 50.0 [38.2, 63.2] | -0.7 [-15.2, +12.4] | 0.9026 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 51.0 [40.1, 62.1] | 57.0 [45.9, 68.3] | +6.0 [-1.6, +14.9] | 0.1596 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 13 [8, 15] | 13 [7, 14] | +0 [-4, +3] | 1.0000 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 0.35 [0.19, 0.53] | 0.70 [0.55, 0.85] | +0.35 [+0.15, +0.54] | 0.0010 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 17.1 [10.7, 24.0] | 42.2 [34.6, 49.5] | +25.1 [+17.2, +32.7] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 50.7 [37.7, 66.4] | 40.1 [32.2, 48.5] | -10.6 [-24.5, +1.0] | 0.0778 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 51.0 [40.1, 62.1] | 66.4 [56.9, 76.1] | +15.4 [+7.1, +25.0] | < 0.0001 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 13 [8, 15] | 11 [8, 14] | -2 [-4, +4] | 1.0000 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 0.35 [0.19, 0.53] | 0.28 [0.19, 0.39] | -0.07 [-0.21, +0.06] | 0.3682 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 17.1 [10.7, 24.0] | 19.0 [12.8, 25.1] | +1.9 [-3.3, +7.2] | 0.5302 |
| `max_k_shown` | 211 | ESCO precision (%) | 50.7 [37.7, 66.4] | 57.1 [45.3, 69.2] | +6.5 [-5.4, +16.4] | 0.2674 |
| `max_k_shown` | 211 | ESCO recall (%) | 51.0 [40.1, 62.1] | 53.7 [43.2, 64.6] | +2.7 [-2.2, +8.9] | 0.4144 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 13 [8, 15] | 13 [7, 14] | +0 [-4, +1] | 0.9508 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 0.35 [0.19, 0.53] | 1.31 [0.95, 1.71] | +0.96 [+0.59, +1.37] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 17.1 [10.7, 24.0] | 46.9 [38.9, 54.8] | +29.9 [+21.6, +38.3] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 50.7 [37.7, 66.4] | 26.2 [19.5, 34.5] | -24.5 [-39.1, -12.4] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 51.0 [40.1, 62.1] | 65.8 [56.2, 75.4] | +14.8 [+7.1, +23.9] | < 0.0001 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 13 [8, 15] | 15 [11, 18] | +2 [+0, +8] | 0.1306 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 0.35 [0.19, 0.53] | 0.80 [0.60, 1.02] | +0.45 [+0.23, +0.69] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 17.1 [10.7, 24.0] | 35.5 [27.7, 43.5] | +18.5 [+11.4, +25.9] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 50.7 [37.7, 66.4] | 32.9 [24.8, 41.9] | -17.7 [-31.9, -6.6] | 0.0004 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 51.0 [40.1, 62.1] | 55.7 [44.6, 67.1] | +4.7 [-2.2, +12.7] | 0.2286 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 13 [8, 15] | 14 [9, 16] | +1 [-2, +5] | 0.5724 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 0.35 [0.19, 0.53] | 1.61 [1.34, 1.90] | +1.26 [+0.95, +1.58] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 17.1 [10.7, 24.0] | 66.4 [59.4, 73.2] | +49.3 [+41.4, +57.0] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 50.7 [37.7, 66.4] | 23.1 [17.7, 29.0] | -27.5 [-41.9, -16.2] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO recall (%) | 51.0 [40.1, 62.1] | 68.5 [58.6, 78.3] | +17.4 [+7.6, +28.4] | 0.0002 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 13 [8, 15] | 14 [11, 18] | +1 [-1, +8] | 0.1612 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 0.35 [0.19, 0.53] | 0.43 [0.29, 0.57] | +0.08 [-0.11, +0.25] | 0.4142 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 17.1 [10.7, 24.0] | 24.2 [17.6, 31.0] | +7.1 [+0.5, +13.7] | 0.0434 |
| `min_k_escape` | 211 | ESCO precision (%) | 50.7 [37.7, 66.4] | 34.3 [24.5, 44.4] | -16.4 [-30.5, -3.9] | 0.0102 |
| `min_k_escape` | 211 | ESCO recall (%) | 51.0 [40.1, 62.1] | 31.5 [21.4, 42.0] | -19.5 [-30.5, -9.6] | < 0.0001 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 13 [8, 15] | 14 [10, 16] | +1 [-1, +6] | 0.3382 |

## 100. Kimi K3 (Bedrock), both sets, cutoff 0.7

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 0.33 [0.20, 0.47] | 0.43 [0.32, 0.55] | +0.10 [+0.01, +0.20] | 0.0266 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 20.9 [13.6, 28.6] | 27.7 [21.3, 34.3] | +6.8 [+2.2, +11.6] | 0.0022 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 59.9 [48.3, 72.6] | 54.0 [44.6, 63.6] | -5.9 [-13.4, +0.1] | 0.0516 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 69.1 [60.0, 78.4] | 71.7 [63.5, 80.0] | +2.6 [-1.7, +7.9] | 0.2904 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 11 [5, 13] | 9 [5, 12] | -2 [-4, +2] | 1.0000 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 0.33 [0.20, 0.47] | 0.90 [0.76, 1.04] | +0.57 [+0.44, +0.72] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 20.9 [13.6, 28.6] | 50.7 [43.7, 57.5] | +29.9 [+22.8, +37.1] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 59.9 [48.3, 72.6] | 36.6 [30.0, 43.3] | -23.3 [-33.5, -15.0] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 69.1 [60.0, 78.4] | 73.6 [65.4, 81.4] | +4.4 [-0.1, +9.5] | 0.0630 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 11 [5, 13] | 12 [7, 14] | +1 [-2, +5] | 0.5682 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 0.33 [0.20, 0.47] | 0.39 [0.26, 0.52] | +0.06 [-0.03, +0.16] | 0.2232 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 20.9 [13.6, 28.6] | 25.1 [17.5, 33.0] | +4.3 [+0.0, +9.0] | 0.0530 |
| `max_k_shown` | 211 | ESCO precision (%) | 59.9 [48.3, 72.6] | 56.1 [46.0, 67.3] | -3.7 [-11.0, +2.5] | 0.2516 |
| `max_k_shown` | 211 | ESCO recall (%) | 69.1 [60.0, 78.4] | 70.5 [61.9, 79.1] | +1.3 [-2.1, +5.2] | 0.6148 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 11 [5, 13] | 11 [5, 13] | +0 [-3, +3] | 1.0000 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 0.33 [0.20, 0.47] | 1.40 [1.14, 1.67] | +1.07 [+0.83, +1.33] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 20.9 [13.6, 28.6] | 62.1 [53.5, 70.4] | +41.2 [+32.9, +49.8] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 59.9 [48.3, 72.6] | 26.6 [20.5, 33.5] | -33.3 [-44.1, -24.2] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 69.1 [60.0, 78.4] | 71.8 [62.9, 80.5] | +2.7 [-2.6, +7.9] | 0.4436 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 11 [5, 13] | 12 [10, 17] | +1 [+0, +9] | 0.0988 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 0.33 [0.20, 0.47] | 0.70 [0.51, 0.90] | +0.37 [+0.22, +0.54] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 20.9 [13.6, 28.6] | 36.5 [28.2, 44.8] | +15.6 [+9.4, +22.3] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 59.9 [48.3, 72.6] | 42.6 [33.5, 52.8] | -17.3 [-26.2, -10.0] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 69.1 [60.0, 78.4] | 73.2 [64.5, 81.7] | +4.0 [+0.0, +9.3] | 0.1062 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 11 [5, 13] | 10 [8, 15] | -1 [-1, +7] | 0.2318 |

## 101. Ministral 3 14B (Bedrock), both sets, cutoff 0.7

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 2.35 [1.83, 2.91] | 1.10 [0.92, 1.29] | -1.25 [-1.75, -0.79] | < 0.0001 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 59.7 [50.7, 68.5] | 55.9 [49.1, 62.6] | -3.8 [-11.6, +3.9] | 0.3306 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 16.8 [12.6, 22.0] | 28.1 [22.1, 34.5] | +11.3 [+7.0, +15.7] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 67.1 [56.7, 77.2] | 60.8 [51.1, 70.9] | -6.3 [-13.7, +2.2] | 0.1372 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 14 [8, 15] | -2 [-8, -1] | 0.0298 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 2.35 [1.83, 2.91] | 1.34 [1.16, 1.51] | -1.01 [-1.51, -0.55] | < 0.0001 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 59.7 [50.7, 68.5] | 65.3 [59.0, 71.5] | +5.6 [-0.8, +12.3] | 0.0892 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 16.8 [12.6, 22.0] | 24.6 [19.6, 30.0] | +7.8 [+3.7, +11.6] | 0.0004 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 67.1 [56.7, 77.2] | 61.9 [52.2, 72.1] | -5.2 [-12.7, +2.5] | 0.1754 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 13 [9, 16] | -3 [-7, +0] | 0.1184 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 2.35 [1.83, 2.91] | 1.06 [0.81, 1.34] | -1.29 [-1.75, -0.86] | < 0.0001 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 59.7 [50.7, 68.5] | 46.0 [37.6, 54.5] | -13.7 [-20.8, -6.9] | < 0.0001 |
| `max_k_shown` | 211 | ESCO precision (%) | 16.8 [12.6, 22.0] | 30.9 [23.6, 39.3] | +14.1 [+9.4, +19.4] | < 0.0001 |
| `max_k_shown` | 211 | ESCO recall (%) | 67.1 [56.7, 77.2] | 67.1 [55.8, 78.3] | +0.0 [-6.1, +5.8] | 1.0000 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 13 [10, 17] | -3 [-6, +0] | 0.1576 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 2.35 [1.83, 2.91] | 2.62 [2.18, 3.10] | +0.27 [-0.10, +0.62] | 0.1568 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 59.7 [50.7, 68.5] | 72.5 [64.7, 80.1] | +12.8 [+6.3, +19.7] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 16.8 [12.6, 22.0] | 15.3 [11.6, 19.6] | -1.4 [-3.9, +0.5] | 0.1510 |
| `min_k_shown` | 211 | ESCO recall (%) | 67.1 [56.7, 77.2] | 67.1 [55.8, 77.9] | +0.0 [-6.5, +7.6] | 1.0000 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 16 [12, 19] | +0 [-3, +2] | 1.0000 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 2.35 [1.83, 2.91] | 0.34 [0.20, 0.49] | -2.01 [-2.54, -1.52] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 59.7 [50.7, 68.5] | 20.4 [13.7, 27.5] | -39.3 [-48.8, -30.0] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 16.8 [12.6, 22.0] | 50.7 [38.1, 64.8] | +33.9 [+23.3, +45.9] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 67.1 [56.7, 77.2] | 49.0 [36.2, 61.9] | -18.1 [-28.4, -8.3] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 16 [13, 19] | 11 [7, 14] | -5 [-9, -1] | 0.0146 |

## 102. Mistral Large 3 (Bedrock), both sets, cutoff 0.7

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 0.92 [0.61, 1.27] | 0.95 [0.78, 1.13] | +0.03 [-0.23, +0.26] | 0.7840 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 30.3 [22.0, 39.1] | 46.8 [40.2, 53.6] | +16.5 [+10.7, +22.3] | < 0.0001 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 34.0 [24.4, 46.5] | 33.5 [26.6, 40.7] | -0.5 [-8.7, +5.2] | 0.8612 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 67.1 [55.3, 78.5] | 67.8 [57.9, 77.7] | +0.7 [-6.9, +9.0] | 0.8970 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 12 [9, 17] | 14 [8, 16] | +2 [-5, +2] | 0.6836 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 0.92 [0.61, 1.27] | 1.25 [1.07, 1.43] | +0.33 [+0.06, +0.57] | 0.0200 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 30.3 [22.0, 39.1] | 58.4 [52.0, 64.6] | +28.1 [+21.2, +34.9] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 34.0 [24.4, 46.5] | 28.1 [22.4, 34.0] | -5.9 [-14.7, +0.4] | 0.0632 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 67.1 [55.3, 78.5] | 69.3 [61.1, 77.2] | +2.1 [-5.7, +10.7] | 0.6442 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 12 [9, 17] | 13 [9, 16] | +1 [-4, +3] | 1.0000 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 0.92 [0.61, 1.27] | 0.79 [0.59, 1.01] | -0.13 [-0.34, +0.06] | 0.2048 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 30.3 [22.0, 39.1] | 38.9 [30.6, 47.0] | +8.5 [+2.8, +14.7] | 0.0032 |
| `max_k_shown` | 211 | ESCO precision (%) | 34.0 [24.4, 46.5] | 36.3 [27.5, 45.8] | +2.2 [-3.8, +7.1] | 0.4486 |
| `max_k_shown` | 211 | ESCO recall (%) | 67.1 [55.3, 78.5] | 63.8 [52.6, 74.6] | -3.4 [-11.0, +5.1] | 0.4508 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 12 [9, 17] | 13 [9, 16] | +1 [-4, +2] | 0.8166 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 0.92 [0.61, 1.27] | 1.85 [1.52, 2.21] | +0.93 [+0.63, +1.25] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 30.3 [22.0, 39.1] | 66.8 [59.9, 73.6] | +36.5 [+28.2, +44.9] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 34.0 [24.4, 46.5] | 20.7 [15.4, 26.6] | -13.3 [-22.5, -6.5] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 67.1 [55.3, 78.5] | 68.5 [58.3, 78.3] | +1.3 [-7.1, +10.3] | 0.8424 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 12 [9, 17] | 16 [11, 18] | +4 [-2, +6] | 0.5462 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 0.92 [0.61, 1.27] | 0.36 [0.24, 0.50] | -0.55 [-0.87, -0.29] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 30.3 [22.0, 39.1] | 20.4 [13.8, 27.2] | -10.0 [-16.5, -3.9] | 0.0004 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 34.0 [24.4, 46.5] | 52.8 [42.1, 64.2] | +18.7 [+9.9, +27.7] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 67.1 [55.3, 78.5] | 57.7 [45.2, 70.2] | -9.4 [-18.8, +0.0] | 0.0530 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 12 [9, 17] | 12 [6, 14] | +0 [-8, +1] | 0.2042 |

## 103. Qwen3-235B (Bedrock), both sets, cutoff 0.7

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 0.55 [0.36, 0.78] | 0.50 [0.38, 0.62] | -0.05 [-0.23, +0.10] | 0.5608 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 30.3 [22.3, 38.4] | 30.2 [23.5, 36.9] | -0.1 [-5.9, +5.7] | 0.9988 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 40.3 [30.0, 53.5] | 43.8 [35.0, 53.2] | +3.5 [-4.4, +9.9] | 0.3830 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 53.0 [41.2, 65.1] | 55.3 [45.9, 65.3] | +2.3 [-3.4, +7.6] | 0.4192 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 14 [9, 16] | 13 [8, 15] | -1 [-6, +1] | 0.4476 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 0.55 [0.36, 0.78] | 0.79 [0.64, 0.94] | +0.23 [+0.07, +0.38] | 0.0064 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 30.3 [22.3, 38.4] | 43.6 [36.6, 50.5] | +13.3 [+7.0, +19.7] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 40.3 [30.0, 53.5] | 33.1 [25.9, 41.0] | -7.2 [-15.1, -1.3] | 0.0146 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 53.0 [41.2, 65.1] | 55.2 [45.2, 65.5] | +2.1 [-5.8, +9.2] | 0.5806 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 14 [9, 16] | 14 [9, 16] | +0 [-4, +2] | 0.8480 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 0.55 [0.36, 0.78] | 0.59 [0.44, 0.75] | +0.04 [-0.13, +0.20] | 0.6490 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 30.3 [22.3, 38.4] | 33.6 [25.9, 41.5] | +3.3 [-2.9, +10.1] | 0.3396 |
| `max_k_shown` | 211 | ESCO precision (%) | 40.3 [30.0, 53.5] | 39.3 [30.2, 49.5] | -1.0 [-8.3, +5.1] | 0.7418 |
| `max_k_shown` | 211 | ESCO recall (%) | 53.0 [41.2, 65.1] | 54.4 [43.1, 65.8] | +1.3 [-3.6, +6.2] | 0.6842 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 14 [9, 16] | 14 [8, 16] | +0 [-4, +2] | 0.7496 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 0.55 [0.36, 0.78] | 1.49 [1.30, 1.68] | +0.93 [+0.67, +1.19] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 30.3 [22.3, 38.4] | 72.5 [66.1, 78.5] | +42.2 [+33.3, +50.7] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 40.3 [30.0, 53.5] | 22.5 [17.5, 27.8] | -17.8 [-28.4, -10.0] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 53.0 [41.2, 65.1] | 61.1 [51.2, 71.2] | +8.1 [+0.5, +16.6] | 0.0498 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 14 [9, 16] | 14 [12, 18] | +0 [-2, +6] | 0.5414 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 0.55 [0.36, 0.78] | 0.78 [0.61, 0.95] | +0.22 [+0.04, +0.40] | 0.0170 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 30.3 [22.3, 38.4] | 46.9 [37.9, 55.7] | +16.6 [+8.4, +24.9] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 40.3 [30.0, 53.5] | 36.4 [28.6, 45.1] | -3.9 [-12.2, +2.7] | 0.2502 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 53.0 [41.2, 65.1] | 63.1 [53.4, 73.4] | +10.1 [+0.0, +20.4] | 0.0534 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 14 [9, 16] | 12 [8, 15] | -2 [-4, +2] | 0.7172 |

## 104. DeepSeek V4.1 Flash (Together), both sets, cutoff 0.7

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 0.81 [0.52, 1.15] | 0.73 [0.58, 0.89] | -0.07 [-0.34, +0.13] | 0.5422 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 33.2 [24.4, 42.4] | 39.5 [32.4, 46.8] | +6.4 [+1.3, +11.5] | 0.0150 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 36.1 [26.1, 48.8] | 39.8 [31.6, 48.4] | +3.7 [-3.6, +9.8] | 0.3248 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 64.4 [54.1, 74.6] | 68.5 [59.4, 77.6] | +4.0 [-1.7, +9.8] | 0.1732 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 13 [9, 17] | 13 [7, 14] | +0 [-6, +1] | 0.2876 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 0.81 [0.52, 1.15] | 1.02 [0.86, 1.18] | +0.21 [-0.08, +0.45] | 0.1326 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 33.2 [24.4, 42.4] | 53.7 [47.3, 60.3] | +20.6 [+13.8, +27.5] | < 0.0001 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 36.1 [26.1, 48.8] | 32.1 [25.4, 38.8] | -4.0 [-12.8, +2.7] | 0.2506 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 64.4 [54.1, 74.6] | 67.9 [58.6, 77.1] | +3.5 [-1.5, +8.8] | 0.1854 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 13 [9, 17] | 14 [8, 15] | +1 [-6, +2] | 0.5730 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 0.81 [0.52, 1.15] | 0.63 [0.46, 0.81] | -0.18 [-0.45, +0.04] | 0.1320 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 33.2 [24.4, 42.4] | 33.6 [25.4, 42.4] | +0.5 [-4.9, +6.0] | 0.9372 |
| `max_k_shown` | 211 | ESCO precision (%) | 36.1 [26.1, 48.8] | 42.9 [33.1, 53.7] | +6.8 [-0.9, +14.2] | 0.0804 |
| `max_k_shown` | 211 | ESCO recall (%) | 64.4 [54.1, 74.6] | 67.1 [56.8, 77.2] | +2.7 [-2.8, +8.5] | 0.4308 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 13 [9, 17] | 12 [8, 15] | -1 [-6, +2] | 0.5318 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 0.81 [0.52, 1.15] | 1.54 [1.22, 1.89] | +0.73 [+0.49, +1.00] | < 0.0001 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 33.2 [24.4, 42.4] | 58.8 [50.5, 66.8] | +25.6 [+18.6, +32.8] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 36.1 [26.1, 48.8] | 23.2 [17.5, 29.8] | -12.9 [-21.4, -6.8] | < 0.0001 |
| `min_k_shown` | 211 | ESCO recall (%) | 64.4 [54.1, 74.6] | 65.8 [55.7, 75.7] | +1.3 [-2.2, +5.4] | 0.6150 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 13 [9, 17] | 15 [11, 18] | +2 [-2, +5] | 0.6420 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 0.81 [0.52, 1.15] | 1.06 [0.81, 1.33] | +0.26 [+0.02, +0.48] | 0.0352 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 33.2 [24.4, 42.4] | 48.3 [39.4, 57.1] | +15.2 [+8.5, +22.2] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 36.1 [26.1, 48.8] | 30.7 [23.0, 39.4] | -5.4 [-13.0, +0.2] | 0.0590 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 64.4 [54.1, 74.6] | 66.4 [56.3, 76.5] | +2.0 [+0.0, +5.4] | 0.2752 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 13 [9, 17] | 12 [10, 17] | -1 [-2, +4] | 1.0000 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 0.81 [0.52, 1.15] | 2.04 [1.68, 2.47] | +1.24 [+0.86, +1.68] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 33.2 [24.4, 42.4] | 73.5 [66.5, 80.1] | +40.3 [+32.0, +48.5] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 36.1 [26.1, 48.8] | 20.2 [15.2, 25.6] | -15.9 [-26.1, -8.4] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO recall (%) | 64.4 [54.1, 74.6] | 73.2 [63.6, 82.2] | +8.7 [+3.4, +14.4] | 0.0004 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 13 [9, 17] | 16 [12, 18] | +3 [-2, +7] | 0.4878 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 0.81 [0.52, 1.15] | 0.81 [0.58, 1.07] | +0.00 [-0.25, +0.23] | 0.9760 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 33.2 [24.4, 42.4] | 33.6 [25.8, 41.5] | +0.5 [-6.8, +7.5] | 0.9452 |
| `min_k_escape` | 211 | ESCO precision (%) | 36.1 [26.1, 48.8] | 36.4 [28.1, 46.1] | +0.3 [-7.4, +7.0] | 0.9362 |
| `min_k_escape` | 211 | ESCO recall (%) | 64.4 [54.1, 74.6] | 65.8 [55.6, 75.8] | +1.3 [-1.4, +4.9] | 0.5934 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 13 [9, 17] | 14 [8, 16] | +1 [-5, +2] | 0.7244 |

## 105. Qwen3.5-9B (Together), both sets, cutoff 0.7

| condition | pairs | measure | none | condition | difference | p |
|---|---|---|---|---|---|---|
| `prose_up_to_k` | 211 | False ESCO concepts per ad | 1.25 [0.90, 1.62] | 0.89 [0.68, 1.10] | -0.36 [-0.60, -0.14] | 0.0002 |
| `prose_up_to_k` | 211 | Ads with at least one false concept (%) | 37.0 [29.7, 44.3] | 40.9 [34.4, 47.3] | +3.9 [-1.5, +9.3] | 0.1550 |
| `prose_up_to_k` | 211 | ESCO precision (%) | 19.1 [13.1, 26.6] | 29.7 [22.9, 37.2] | +10.6 [+5.5, +15.6] | 0.0002 |
| `prose_up_to_k` | 211 | ESCO recall (%) | 41.6 [29.9, 53.8] | 53.0 [43.4, 62.5] | +11.4 [+0.3, +21.9] | 0.0450 |
| `prose_up_to_k` | 211 | Top-20 concepts not in the true items' top 20 | 17 [12, 18] | 14 [9, 16] | -3 [-7, +0] | 0.1466 |
| `prose_exactly_k` | 211 | False ESCO concepts per ad | 1.25 [0.90, 1.62] | 0.89 [0.70, 1.08] | -0.36 [-0.60, -0.13] | 0.0008 |
| `prose_exactly_k` | 211 | Ads with at least one false concept (%) | 37.0 [29.7, 44.3] | 42.0 [35.3, 48.7] | +5.0 [-0.3, +10.4] | 0.0616 |
| `prose_exactly_k` | 211 | ESCO precision (%) | 19.1 [13.1, 26.6] | 26.6 [20.4, 33.4] | +7.5 [+1.7, +12.9] | 0.0130 |
| `prose_exactly_k` | 211 | ESCO recall (%) | 41.6 [29.9, 53.8] | 45.5 [36.3, 55.2] | +3.9 [-7.1, +14.5] | 0.4772 |
| `prose_exactly_k` | 211 | Top-20 concepts not in the true items' top 20 | 17 [12, 18] | 14 [10, 17] | -3 [-6, +1] | 0.3384 |
| `max_k_shown` | 211 | False ESCO concepts per ad | 1.25 [0.90, 1.62] | 0.91 [0.66, 1.17] | -0.34 [-0.54, -0.15] | 0.0002 |
| `max_k_shown` | 211 | Ads with at least one false concept (%) | 37.0 [29.7, 44.3] | 36.0 [29.0, 42.9] | -0.9 [-6.7, +4.8] | 0.7906 |
| `max_k_shown` | 211 | ESCO precision (%) | 19.1 [13.1, 26.6] | 27.0 [19.6, 35.8] | +7.9 [+3.7, +13.0] | < 0.0001 |
| `max_k_shown` | 211 | ESCO recall (%) | 41.6 [29.9, 53.8] | 47.7 [36.4, 59.3] | +6.0 [-1.3, +14.2] | 0.1304 |
| `max_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 17 [12, 18] | 16 [11, 17] | -1 [-4, +1] | 0.6554 |
| `min_k_shown` | 211 | False ESCO concepts per ad | 1.25 [0.90, 1.62] | 1.56 [1.22, 1.91] | +0.31 [+0.13, +0.50] | 0.0010 |
| `min_k_shown` | 211 | Ads with at least one false concept (%) | 37.0 [29.7, 44.3] | 50.2 [42.5, 58.0] | +13.3 [+6.8, +20.1] | < 0.0001 |
| `min_k_shown` | 211 | ESCO precision (%) | 19.1 [13.1, 26.6] | 20.1 [14.8, 26.1] | +1.1 [-3.1, +4.7] | 0.6000 |
| `min_k_shown` | 211 | ESCO recall (%) | 41.6 [29.9, 53.8] | 55.7 [43.3, 67.9] | +14.1 [+3.8, +24.6] | 0.0092 |
| `min_k_shown` | 211 | Top-20 concepts not in the true items' top 20 | 17 [12, 18] | 16 [11, 17] | -1 [-3, +1] | 0.7274 |
| `min_k_shown_fewer_ok` | 211 | False ESCO concepts per ad | 1.25 [0.90, 1.62] | 1.01 [0.68, 1.36] | -0.24 [-0.44, -0.02] | 0.0350 |
| `min_k_shown_fewer_ok` | 211 | Ads with at least one false concept (%) | 37.0 [29.7, 44.3] | 27.0 [20.0, 34.1] | -10.0 [-15.8, -4.5] | < 0.0001 |
| `min_k_shown_fewer_ok` | 211 | ESCO precision (%) | 19.1 [13.1, 26.6] | 19.9 [13.5, 27.6] | +0.8 [-4.5, +6.0] | 0.7102 |
| `min_k_shown_fewer_ok` | 211 | ESCO recall (%) | 41.6 [29.9, 53.8] | 35.6 [25.4, 46.0] | -6.0 [-17.0, +4.0] | 0.2786 |
| `min_k_shown_fewer_ok` | 211 | Top-20 concepts not in the true items' top 20 | 17 [12, 18] | 17 [12, 19] | +0 [-2, +3] | 1.0000 |
| `min_k_enforced` | 211 | False ESCO concepts per ad | 1.25 [0.90, 1.62] | 3.00 [2.42, 3.81] | +1.75 [+1.20, +2.55] | < 0.0001 |
| `min_k_enforced` | 211 | Ads with at least one false concept (%) | 37.0 [29.7, 44.3] | 86.3 [80.3, 91.7] | +49.3 [+41.3, +57.6] | < 0.0001 |
| `min_k_enforced` | 211 | ESCO precision (%) | 19.1 [13.1, 26.6] | 16.3 [11.8, 21.4] | -2.8 [-9.5, +2.9] | 0.3632 |
| `min_k_enforced` | 211 | ESCO recall (%) | 41.6 [29.9, 53.8] | 82.6 [75.4, 89.1] | +40.9 [+28.9, +53.1] | < 0.0001 |
| `min_k_enforced` | 211 | Top-20 concepts not in the true items' top 20 | 17 [12, 18] | 15 [11, 17] | -2 [-4, +2] | 0.7432 |
| `min_k_escape` | 211 | False ESCO concepts per ad | 1.25 [0.90, 1.62] | 1.45 [1.10, 1.81] | +0.20 [+0.01, +0.40] | 0.0392 |
| `min_k_escape` | 211 | Ads with at least one false concept (%) | 37.0 [29.7, 44.3] | 42.7 [35.0, 50.2] | +5.7 [-0.9, +12.3] | 0.0964 |
| `min_k_escape` | 211 | ESCO precision (%) | 19.1 [13.1, 26.6] | 23.8 [17.8, 30.7] | +4.7 [+0.5, +8.8] | 0.0298 |
| `min_k_escape` | 211 | ESCO recall (%) | 41.6 [29.9, 53.8] | 63.8 [51.4, 75.4] | +22.1 [+11.9, +32.7] | < 0.0001 |
| `min_k_escape` | 211 | Top-20 concepts not in the true items' top 20 | 17 [12, 18] | 17 [11, 18] | +0 [-4, +2] | 0.6714 |

## Notes

- Second linker: the SkillSpan authors' follow-up on linking to ESCO (Zhang, van der Goot and Plank, Findings of EACL 2024, github.com/jjzha/el_esco) fine-tunes BLINK and GENRE and releases training code and data, but no trained linker and no recommendation of one to use; so no second linker is added.
- Hand check of the linker: `hand_check.py` (50 links, seed 20261013); its result is written to `HAND_CHECK.md` once both files are filled.
