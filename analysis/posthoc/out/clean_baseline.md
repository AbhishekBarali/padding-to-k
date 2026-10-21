# Post hoc: over-count where the model is clean with no count

Pairs of (GPU model, document) whose no-count output was clean; documents with n < k, k = 3 and 5; one cell per (model, document, k), prose wordings averaged. Over-count % with 95% intervals from 10000 draws over document groups within set (seed 20261014). Clean (a): exactly n substantive entries with no count. Clean (b): at most n. Frozen scores: an unreadable output counts as 0 entries.

Sanity check (no clean filter, plain output share as in the paper): no count 34.5%, min_k_shown 55.4%.

## 8 GPU models

| subset | (model, document) pairs | cells | unreadable no-count outputs |
|---|---|---|---|
| all pairs | 4272 | 7272 | 502 |
| (a) exactly n | 2275 | 3884 | 106 |
| (b) at most n | 2827 | 4762 | 502 |

| condition | all pairs | (a) exactly n | (b) at most n |
|---|---|---|---|
| none | 34.5 [32.6, 36.4] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| prose_up_to_k | 42.7 [41.0, 44.5] | 14.2 [13.0, 15.4] | 16.0 [14.9, 17.2] |
| prose_exactly_k | 50.9 [49.3, 52.6] | 27.7 [26.2, 29.4] | 27.7 [26.2, 29.2] |
| max_k_shown | 35.7 [33.9, 37.6] | 5.0 [4.2, 5.9] | 5.1 [4.3, 5.8] |
| min_k_shown | 55.4 [53.7, 57.1] | 35.2 [33.0, 37.5] | 33.9 [32.1, 35.8] |
| min_k_shown_fewer_ok | 31.0 [29.3, 32.6] | 9.6 [8.5, 10.7] | 10.1 [9.0, 11.2] |
| min_k_enforced | 90.1 [89.1, 91.1] | 83.9 [82.2, 85.5] | 85.3 [83.8, 86.7] |
| min_k_escape | 51.0 [49.1, 52.9] | 29.2 [27.2, 31.2] | 36.1 [34.0, 38.1] |

## 7 GPU models, without Qwen3.5-0.8B

| subset | (model, document) pairs | cells | unreadable no-count outputs |
|---|---|---|---|
| all pairs | 3738 | 6363 | 9 |
| (a) exactly n | 2171 | 3698 | 6 |
| (b) at most n | 2453 | 4134 | 9 |

| condition | all pairs | (a) exactly n | (b) at most n |
|---|---|---|---|
| none | 35.0 [33.0, 37.1] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| prose_up_to_k | 41.7 [39.9, 43.6] | 13.2 [12.1, 14.3] | 13.9 [12.7, 15.0] |
| prose_exactly_k | 52.5 [50.7, 54.3] | 28.0 [26.3, 29.6] | 29.1 [27.6, 30.7] |
| max_k_shown | 36.6 [34.7, 38.6] | 5.2 [4.4, 6.1] | 5.7 [4.9, 6.6] |
| min_k_shown | 59.8 [57.9, 61.6] | 36.7 [34.5, 39.0] | 38.8 [36.7, 40.9] |
| min_k_shown_fewer_ok | 30.5 [28.7, 32.4] | 9.8 [8.7, 10.9] | 10.3 [9.2, 11.4] |
| min_k_enforced | 89.9 [88.8, 90.9] | 83.9 [82.2, 85.6] | 84.7 [83.1, 86.2] |
| min_k_escape | 45.4 [43.3, 47.6] | 27.1 [24.9, 29.3] | 28.5 [26.4, 30.6] |

## Per model: over-count % under min_k_shown

| model | all pairs | (a) exactly n | (a) pairs | (b) at most n | (b) pairs |
|---|---|---|---|---|---|
| Qwen3.5-0.8B | 24.9 [22.5, 27.3] | 4.8 [1.6, 8.6] | 104 | 2.1 [0.9, 3.5] | 374 |
| Qwen3.5-2B | 60.4 [57.7, 63.1] | 10.9 [7.3, 14.8] | 208 | 12.3 [9.0, 15.8] | 246 |
| Qwen3.5-9B | 44.8 [41.6, 47.9] | 24.2 [20.7, 27.8] | 328 | 26.0 [22.6, 29.4] | 396 |
| Qwen3.5-27B | 60.9 [57.9, 64.1] | 46.5 [42.7, 50.2] | 375 | 49.4 [45.7, 53.0] | 413 |
| Gemma 4 31B | 62.5 [59.5, 65.4] | 52.8 [49.4, 56.2] | 411 | 56.3 [53.1, 59.6] | 460 |
| Olmo 3.1 32B | 57.8 [54.6, 60.9] | 25.9 [21.6, 30.2] | 271 | 29.0 [25.0, 33.1] | 307 |
| Ministral 3 14B | 67.7 [64.7, 70.7] | 35.0 [30.2, 39.7] | 259 | 36.0 [31.4, 40.7] | 275 |
| gpt-oss-20b | 64.2 [61.1, 67.4] | 44.6 [40.0, 49.2] | 319 | 46.8 [42.5, 51.2] | 356 |

## Per model: over-count % per condition, clean (b)

| model | min_k_shown | min_k_shown_fewer_ok | min_k_enforced | min_k_escape | max_k_shown |
|---|---|---|---|---|---|
| Qwen3.5-0.8B | 2.1 [0.9, 3.5] | 8.8 [6.7, 10.9] | 88.9 [85.9, 91.7] | 86.0 [82.8, 89.1] | 0.8 [0.2, 1.7] |
| Qwen3.5-2B | 12.3 [9.0, 15.8] | 6.6 [4.5, 9.0] | 88.9 [85.8, 92.0] | 71.9 [66.2, 77.4] | 3.4 [1.7, 5.5] |
| Qwen3.5-9B | 26.0 [22.6, 29.4] | 5.4 [3.6, 7.3] | 90.9 [88.5, 93.2] | 34.0 [29.9, 38.3] | 5.1 [3.2, 7.1] |
| Qwen3.5-27B | 49.4 [45.7, 53.0] | 25.9 [22.9, 29.0] | 89.1 [86.5, 91.7] | 29.6 [26.2, 33.0] | 5.4 [3.7, 7.3] |
| Gemma 4 31B | 56.3 [53.1, 59.6] | 3.9 [2.2, 5.6] | 83.3 [80.4, 86.1] | 19.7 [16.6, 22.8] | 1.4 [0.5, 2.6] |
| Olmo 3.1 32B | 29.0 [25.0, 33.1] | 6.5 [4.2, 8.9] | 92.4 [89.6, 95.0] | 27.0 [22.5, 31.6] | 9.7 [7.2, 12.3] |
| Ministral 3 14B | 36.0 [31.4, 40.7] | 5.1 [3.3, 7.0] | 94.5 [92.0, 96.8] | 11.7 [8.6, 15.1] | 2.2 [0.9, 3.8] |
| gpt-oss-20b | 46.8 [42.5, 51.2] | 15.8 [13.4, 18.3] | 57.5 [53.3, 61.7] | 17.0 [14.2, 20.1] | 13.0 [10.4, 15.6] |
