# Full study: every registered test and estimate

Written by `python analysis/full_study.py tables` from the scored run records in `analysis/full/scored/` (`analysis/full_study_score.py`); run folders in `runs.md`. Bootstrap: 10000 draws over document groups within set, seed 20261014. Length change in substantive entries; over-count in points. GPU results pool the 8 main models: Qwen3.5-0.8B, Qwen3.5-2B, Qwen3.5-9B, Qwen3.5-27B, Gemma 4 31B, Olmo 3.1 32B, Ministral 3 14B, gpt-oss-20b.

## 1. Confirmatory contrasts (8 main models pooled, documents with n < k, k = 3 and 5; Holm across the five)

Primary test: the 95% bootstrap interval of the mean paired difference over documents and models, and its two-sided bootstrap p-value (Holm-adjusted across the five). Contrasts 1 to 4: length change in substantive entries. Contrast 5: substantive extra entries per padded slot (excess / (k - n) per output). Next to it: the mixed model (contrasts 1-4: LMM of the paired difference, intercept = average difference; contrast 5: Poisson mixed model, rate ratio for the escape), the same test without the 60 pilot documents, and over-count (points) for contrasts 1 to 4.

| # | contrast | estimate [95% CI] | p | Holm p | pairs | groups | without pilot docs | mixed model | over-count (points) |
|---|---|---|---|---|---|---|---|---|---|
| C1 | Dose: min_k_shown, k = 5 vs k = 3 (n at most 2) | +0.61 [+0.42, +0.80] | < 0.0001 | < 0.0001 | 3000 | 366 | +0.54 [+0.30, +0.76] | +0.65 [+0.44, +0.87] (entries) | +0.8 [-0.2, +1.7] |
| C2 | min_k_shown vs none (main measure) | +0.62 [+0.46, +0.78] | < 0.0001 | < 0.0001 | 7272 | 520 | +0.66 [+0.48, +0.84] | +0.63 [+0.47, +0.79] (entries) | +20.9 [+19.5, +22.3] |
| C3 | min_k_shown vs max_k_shown | +1.11 [+0.97, +1.25] | < 0.0001 | < 0.0001 | 7272 | 520 | +1.16 [+1.01, +1.32] | +1.13 [+0.99, +1.28] (entries) | +19.7 [+18.4, +21.0] |
| C4 | prose_exactly_k vs prose_up_to_k (5 wordings averaged) | +0.10 [+0.06, +0.15] | < 0.0001 | < 0.0001 | 7272 | 520 | +0.11 [+0.05, +0.16] | +0.11 [+0.06, +0.16] (entries) | +8.2 [+7.3, +9.0] |
| C5 | min_k_escape vs min_k_enforced (substantive extra entries per padded slot) | -0.54 [-0.58, -0.50] | < 0.0001 | < 0.0001 | 7266 | 520 | -0.55 [-0.59, -0.51] | 0.57 [0.56, 0.58] (rate ratio) | -- |
- C1 mixed model: `diff ~ n_c + C(model_key, Sum) + C(set, Sum) + words_c + (1 | document), REML, optimiser powell`
- C2 mixed model: `diff ~ n_c + C(model_key, Sum) + C(set, Sum) + words_c + (1 | document), REML, optimiser powell`
- C3 mixed model: `diff ~ n_c + C(model_key, Sum) + C(set, Sum) + words_c + (1 | document), REML, optimiser powell`
- C4 mixed model: `diff ~ n_c + C(model_key, Sum) + C(set, Sum) + words_c + (1 | document), REML, optimiser powell`
- C5 mixed model: `y ~ escape + n_c + C(model_key, Sum) + C(set, Sum) + words_c + log_slots + (1 | document), Poisson, variational Bayes`

## 1a. Confirmatory contrasts, n = 0 apart from n >= 1 (section 6.1)

| # | n = 0 | n = 1 to 4 (n < k) |
|---|---|---|
| C1 | +0.76 [+0.36, +1.16] | +0.55 [+0.34, +0.76] |
| C2 | +0.73 [+0.42, +1.04] | +0.59 [+0.40, +0.78] |
| C3 | +1.19 [+0.89, +1.52] | +1.09 [+0.94, +1.24] |
| C4 | +0.01 [-0.11, +0.13] | +0.13 [+0.09, +0.18] |
| C5 | -0.69 [-0.75, -0.63] | -0.49 [-0.54, -0.45] |

## 2. Per main model (each with its own interval; the pooled row is section 1)

| model | C1 | C2 | C3 | C4 | C5 |
|---|---|---|---|---|---|
| Qwen3.5-0.8B | -0.38 [-0.84, +0.07] | -0.59 [-1.06, -0.13] | -0.32 [-0.73, +0.08] | -0.63 [-0.77, -0.49] | -0.31 [-0.47, -0.16] |
| Qwen3.5-2B | +0.12 [-1.39, +1.56] | +0.60 [-0.51, +1.72] | +2.13 [+1.22, +3.07] | -0.44 [-0.74, -0.13] | -0.22 [-0.32, -0.11] |
| Qwen3.5-9B | +0.51 [+0.39, +0.65] | +0.62 [+0.50, +0.74] | +0.80 [+0.69, +0.92] | +0.11 [+0.06, +0.15] | -0.64 [-0.81, -0.53] |
| Qwen3.5-27B | +1.20 [+1.07, +1.33] | +1.24 [+1.11, +1.37] | +1.29 [+1.18, +1.41] | +0.37 [+0.32, +0.41] | -0.57 [-0.61, -0.53] |
| Gemma 4 31B | +1.13 [+0.99, +1.27] | +1.68 [+1.55, +1.81] | +1.70 [+1.57, +1.83] | +0.93 [+0.87, +0.99] | -0.66 [-0.70, -0.62] |
| Olmo 3.1 32B | +0.47 [+0.29, +0.64] | +0.26 [+0.10, +0.42] | +1.20 [+1.00, +1.42] | +0.02 [-0.05, +0.08] | -0.64 [-0.73, -0.56] |
| Ministral 3 14B | +1.03 [+0.87, +1.19] | +0.30 [+0.12, +0.45] | +1.13 [+0.99, +1.27] | +0.19 [+0.14, +0.24] | -0.94 [-1.00, -0.88] |
| gpt-oss-20b | +0.83 [+0.65, +1.01] | +0.87 [+0.72, +1.01] | +0.98 [+0.86, +1.10] | +0.28 [+0.23, +0.33] | -0.32 [-0.38, -0.27] |
| 8 models pooled | +0.61 [+0.42, +0.80] | +0.62 [+0.46, +0.78] | +1.11 [+0.97, +1.25] | +0.10 [+0.06, +0.15] | -0.54 [-0.58, -0.50] |

## 3. Per set (8 main models pooled)

Same contrasts as section 1; the last column is contrast 2 on over-count (points). Job-ad skills is the least certain answer list (protocol 4.1).

| set | C1 | C2 | C3 | C4 | C5 | C2 over-count |
|---|---|---|---|---|---|---|
| meetings | +1.58 [+1.50, +1.66] | +0.19 [-0.30, +0.61] | +0.64 [+0.38, +0.88] | +0.00 [-0.05, +0.05] | -0.46 [-0.58, -0.36] | +27.7 [+22.6, +33.3] |
| emails | +0.48 [+0.31, +0.65] | +0.90 [+0.76, +1.05] | +0.93 [+0.77, +1.12] | +0.16 [+0.10, +0.22] | -0.47 [-0.53, -0.42] | +27.7 [+22.3, +33.2] |
| receipts | +0.88 [+0.69, +1.07] | +1.01 [+0.84, +1.20] | +1.09 [+0.91, +1.28] | +0.38 [+0.30, +0.47] | -0.69 [-0.81, -0.57] | +31.2 [+26.2, +36.2] |
| job-ad skills | +0.74 [-0.42, +1.83] | +1.54 [+0.83, +2.30] | +2.55 [+1.84, +3.31] | +0.10 [-0.13, +0.34] | -0.61 [-0.72, -0.50] | +22.9 [+18.5, +27.4] |
| clinical | +0.16 [-0.01, +0.29] | +0.28 [+0.19, +0.37] | +0.30 [+0.20, +0.40] | +0.13 [+0.09, +0.17] | -0.57 [-0.64, -0.50] | +15.2 [+11.4, +19.1] |
| reviews | +1.10 [+0.94, +1.24] | +0.28 [+0.08, +0.47] | +0.88 [+0.77, +0.99] | +0.23 [+0.17, +0.29] | -0.07 [-0.11, -0.03] | +14.6 [+9.5, +20.2] |
| job-ad knowledge | +0.45 [-0.74, +1.66] | +0.76 [-0.26, +1.79] | +2.95 [+2.06, +3.82] | -0.34 [-0.60, -0.07] | -0.88 [-1.12, -0.69] | +24.4 [+21.5, +27.3] |
| Wikipedia people | -0.17 [-0.26, -0.09] | +0.07 [+0.01, +0.15] | +0.06 [+0.00, +0.13] | +0.05 [+0.02, +0.08] | -0.62 [-0.71, -0.55] | +6.5 [+4.6, +8.7] |
| novel quotes | +0.55 [+0.42, +0.69] | +0.61 [+0.47, +0.77] | +0.64 [+0.49, +0.80] | +0.30 [+0.25, +0.36] | -0.40 [-0.48, -0.32] | +18.7 [+15.6, +21.9] |

## 4. Named tests (section 6.3; 8 main models pooled; outside the Holm family)

Shares with at least one substantive entry on the 105 empty documents at k = 1: none 34.9%; prose_up_to_k 43.7%; prose_exactly_k 46.5%; max_k_shown 33.9%; min_k_shown 42.3%; min_k_shown_fewer_ok 31.8%; min_k_enforced 82.4%; min_k_escape 30.0%

| test | estimate [95% CI] | p (unadjusted) |
|---|---|---|
| fewer is fine: min_k_shown_fewer_ok vs none (length) | -0.77 [-0.93, -0.60] | < 0.0001 |
| fewer is fine: min_k_shown_fewer_ok vs min_k_shown (length) | -1.39 [-1.53, -1.25] | < 0.0001 |
| fewer is fine: min_k_shown_fewer_ok vs none (over-count, points) | -3.5 [-4.7, -2.4] | -- |
| maxItems: max_k_shown vs none (length) | -0.49 [-0.61, -0.37] | < 0.0001 |
| enough items (n >= k, k = 1, 3, 5): min_k_shown vs none (length) | -0.15 [-0.30, -0.02] | 0.0274 |
| enough items: min_k_shown vs none (share of true items left out, points) | +0.2 [-0.3, +0.8] | -- |
| part of the effect from filling missing slots, k = 3 and 5: change on n < k minus on n >= k | +0.93 [+0.63, +1.24] | -- |
| enough items, k = 1: n >= k -0.08 [-0.20, +0.04]; n < k +0.22 [-0.12, +0.57]; difference (n < k minus n >= k) | +0.30 [-0.06, +0.68] | -- |
| enough items, k = 3: n >= k -0.25 [-0.51, +0.01]; n < k +0.28 [+0.09, +0.49]; difference (n < k minus n >= k) | +0.54 [+0.20, +0.87] | -- |
| enough items, k = 5: n >= k -0.71 [-1.57, -0.02]; n < k +0.86 [+0.69, +1.03]; difference (n < k minus n >= k) | +1.57 [+0.84, +2.58] | -- |
| empty document, k = 1 (n = 0): prose_up_to_k vs none, share with at least one entry (points) | +8.8 [+7.3, +10.3] | < 0.0001 |
| empty document, k = 1 (n = 0): prose_exactly_k vs none, share with at least one entry (points) | +11.6 [+9.8, +13.4] | < 0.0001 |
| empty document, k = 1 (n = 0): max_k_shown vs none, share with at least one entry (points) | -1.0 [-2.4, +0.4] | 0.2034 |
| empty document, k = 1 (n = 0): min_k_shown vs none, share with at least one entry (points) | +7.4 [+5.6, +9.2] | < 0.0001 |
| empty document, k = 1 (n = 0): min_k_shown_fewer_ok vs none, share with at least one entry (points) | -3.1 [-5.0, -1.2] | 0.0010 |
| empty document, k = 1 (n = 0): min_k_enforced vs none, share with at least one entry (points) | +47.5 [+44.5, +50.5] | < 0.0001 |
| empty document, k = 1 (n = 0): min_k_escape vs none, share with at least one entry (points) | -4.9 [-6.9, -2.9] | < 0.0001 |

## 4a. Named tests per main model

| model | fewer_ok vs none | fewer_ok vs min_k_shown | max vs none | n >= k: shown vs none | slot-filling part (k 3, 5) | empty k = 1: shown vs none (points) |
|---|---|---|---|---|---|---|
| Qwen3.5-0.8B | +0.03 [-0.39, +0.47] | +0.62 [+0.19, +1.05] | -0.27 [-0.64, +0.09] | -0.25 [-0.60, +0.11] | +0.44 [-0.38, +1.29] | -1.0 [-3.8, +1.9] |
| Qwen3.5-2B | -2.70 [-3.91, -1.56] | -3.31 [-4.26, -2.35] | -1.52 [-2.37, -0.70] | -0.43 [-1.46, +0.52] | +0.55 [-1.42, +2.58] | +1.9 [+0.0, +4.8] |
| Qwen3.5-9B | -0.58 [-0.70, -0.46] | -1.20 [-1.34, -1.06] | -0.19 [-0.27, -0.10] | -0.00 [-0.13, +0.12] | +0.72 [+0.33, +1.03] | +6.7 [+2.9, +11.4] |
| Qwen3.5-27B | +0.46 [+0.37, +0.56] | -0.78 [-0.88, -0.68] | -0.05 [-0.12, +0.02] | -0.09 [-0.16, -0.03] | +1.52 [+1.31, +1.75] | +7.6 [+2.9, +12.4] |
| Gemma 4 31B | +0.02 [-0.02, +0.06] | -1.65 [-1.79, -1.52] | -0.02 [-0.05, +0.01] | +0.08 [+0.05, +0.12] | +1.48 [+1.34, +1.63] | +15.2 [+9.5, +21.0] |
| Olmo 3.1 32B | -1.92 [-2.20, -1.66] | -2.18 [-2.43, -1.95] | -0.94 [-1.19, -0.70] | -0.24 [-0.37, -0.12] | +0.89 [+0.63, +1.17] | +4.8 [-1.0, +10.5] |
| Ministral 3 14B | -1.50 [-1.76, -1.25] | -1.80 [-1.99, -1.62] | -0.83 [-1.02, -0.65] | -0.32 [-0.45, -0.19] | +1.01 [+0.72, +1.32] | +3.8 [-1.0, +8.6] |
| gpt-oss-20b | +0.06 [-0.08, +0.19] | -0.81 [-0.93, -0.69] | -0.11 [-0.26, +0.03] | +0.05 [-0.06, +0.17] | +0.80 [+0.54, +1.04] | +20.0 [+14.3, +25.7] |

## 5. Over-count, excess, length distribution and true items left out (8 main models pooled, k = 3 and 5)

Over-count, excess and the length distribution on documents with n < k; true items left out on documents with n >= 1 (any n vs k), share of their true items no entry matches (matcher true-item and split labels). Placeholder bound: every substantive entry of 8 words or fewer holding no, none, not, only, other, additional or found taken as a note.

| condition | outputs (n < k) | over-count % | over-count %, placeholder bound | excess | unreadable % | fewer than k % | exactly k % | more than k % | exactly n % | true items left out % (n >= 1) |
|---|---|---|---|---|---|---|---|---|---|---|
| none | 7272 | 34.5 | 34.3 | 2.41 | 6.9 | 70.0 | 5.6 | 17.4 | 52.0 | 17.0 |
| prose_up_to_k | 36360 | 42.7 | 42.4 | 1.58 | 3.7 | 65.6 | 24.0 | 6.6 | 48.1 | 20.0 |
| prose_exactly_k | 36360 | 50.9 | 50.6 | 1.71 | 6.0 | 50.1 | 39.0 | 4.9 | 38.8 | 21.6 |
| max_k_shown | 7272 | 35.7 | 35.5 | 1.92 | 7.3 | 68.0 | 15.5 | 9.2 | 50.8 | 20.9 |
| min_k_shown | 7272 | 55.4 | 55.2 | 3.02 | 10.5 | 37.1 | 35.5 | 17.0 | 31.0 | 18.2 |
| min_k_shown_fewer_ok | 7272 | 31.0 | 30.8 | 1.76 | 7.3 | 67.4 | 15.0 | 10.2 | 48.5 | 24.3 |
| min_k_enforced | 7270 | 90.1 | 89.5 | 3.49 | 0.2 | 0.6 | 71.8 | 27.5 | 9.2 | 8.6 |
| min_k_escape | 7267 | 51.0 | 50.6 | 2.00 | 0.1 | 0.2 | 78.5 | 21.2 | 40.5 | 13.6 |

## 5a. The same per main model

| model | condition | outputs (n < k) | over-count % | over-count %, placeholder bound | excess | unreadable % | fewer than k % | exactly k % | more than k % | exactly n % | true items left out % (n >= 1) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Qwen3.5-0.8B | none | 909 | 30.9 | 30.9 | 3.45 | 54.2 | 19.7 | 1.8 | 24.3 | 9.5 | 66.7 |
| Qwen3.5-0.8B | prose_up_to_k | 4545 | 50.0 | 49.8 | 2.75 | 28.0 | 32.5 | 20.2 | 19.4 | 16.3 | 53.5 |
| Qwen3.5-0.8B | prose_exactly_k | 4545 | 39.6 | 39.4 | 2.35 | 45.0 | 21.0 | 18.6 | 15.3 | 11.8 | 65.1 |
| Qwen3.5-0.8B | max_k_shown | 909 | 29.3 | 29.2 | 3.21 | 57.5 | 18.0 | 2.2 | 22.2 | 9.6 | 68.8 |
| Qwen3.5-0.8B | min_k_shown | 909 | 24.9 | 24.9 | 3.02 | 67.4 | 11.6 | 2.4 | 18.6 | 5.6 | 76.5 |
| Qwen3.5-0.8B | min_k_shown_fewer_ok | 909 | 34.0 | 33.9 | 3.42 | 49.1 | 21.2 | 3.7 | 26.0 | 12.9 | 65.1 |
| Qwen3.5-0.8B | min_k_enforced | 909 | 91.9 | 91.5 | 6.13 | 0.8 | 1.0 | 34.3 | 63.9 | 6.6 | 15.6 |
| Qwen3.5-0.8B | min_k_escape | 908 | 89.6 | 89.1 | 5.32 | 1.0 | 0.8 | 35.0 | 63.2 | 7.9 | 15.1 |
| Qwen3.5-2B | none | 909 | 55.1 | 55.0 | 8.97 | 0.1 | 56.8 | 5.9 | 37.2 | 38.3 | 15.1 |
| Qwen3.5-2B | prose_up_to_k | 4545 | 58.9 | 58.7 | 4.36 | 0.6 | 51.4 | 26.4 | 21.5 | 34.7 | 21.1 |
| Qwen3.5-2B | prose_exactly_k | 4545 | 58.4 | 58.3 | 3.92 | 0.2 | 50.8 | 30.4 | 18.7 | 35.8 | 21.8 |
| Qwen3.5-2B | max_k_shown | 909 | 55.7 | 55.3 | 7.45 | 0.1 | 55.7 | 9.4 | 34.9 | 37.3 | 17.5 |
| Qwen3.5-2B | min_k_shown | 909 | 60.4 | 60.3 | 9.56 | 0.2 | 47.9 | 14.6 | 37.3 | 34.1 | 17.0 |
| Qwen3.5-2B | min_k_shown_fewer_ok | 909 | 46.9 | 46.9 | 6.47 | 0.7 | 56.0 | 9.6 | 33.8 | 34.3 | 23.8 |
| Qwen3.5-2B | min_k_enforced | 908 | 94.5 | 94.1 | 4.65 | 0.0 | 1.1 | 43.7 | 55.2 | 5.2 | 12.1 |
| Qwen3.5-2B | min_k_escape | 907 | 83.0 | 82.8 | 3.99 | 0.1 | 0.8 | 48.8 | 50.3 | 13.9 | 13.6 |
| Qwen3.5-9B | none | 909 | 26.3 | 26.1 | 0.98 | 0.0 | 84.4 | 5.2 | 10.5 | 61.5 | 13.5 |
| Qwen3.5-9B | prose_up_to_k | 4545 | 34.1 | 33.7 | 0.81 | 0.1 | 79.3 | 18.7 | 1.9 | 56.9 | 17.8 |
| Qwen3.5-9B | prose_exactly_k | 4545 | 38.9 | 38.6 | 0.92 | 0.0 | 71.2 | 27.5 | 1.4 | 51.5 | 18.2 |
| Qwen3.5-9B | max_k_shown | 909 | 28.9 | 28.5 | 0.79 | 0.0 | 84.0 | 11.6 | 4.4 | 58.7 | 16.6 |
| Qwen3.5-9B | min_k_shown | 909 | 44.8 | 44.6 | 1.56 | 0.1 | 62.0 | 25.7 | 12.1 | 46.1 | 11.6 |
| Qwen3.5-9B | min_k_shown_fewer_ok | 909 | 18.0 | 17.9 | 0.67 | 0.0 | 86.4 | 6.6 | 7.0 | 55.1 | 26.9 |
| Qwen3.5-9B | min_k_enforced | 909 | 92.7 | 92.4 | 3.24 | 0.2 | 0.7 | 75.4 | 23.8 | 6.6 | 6.4 |
| Qwen3.5-9B | min_k_escape | 909 | 47.2 | 46.9 | 1.40 | 0.0 | 0.0 | 87.5 | 12.5 | 40.2 | 13.2 |
| Qwen3.5-27B | none | 909 | 23.1 | 23.1 | 0.52 | 0.0 | 88.6 | 5.8 | 5.6 | 71.0 | 5.2 |
| Qwen3.5-27B | prose_up_to_k | 4545 | 29.5 | 29.5 | 0.59 | 0.7 | 80.7 | 18.4 | 0.1 | 64.9 | 10.0 |
| Qwen3.5-27B | prose_exactly_k | 4545 | 42.1 | 42.0 | 0.94 | 0.8 | 64.2 | 34.9 | 0.1 | 53.6 | 9.8 |
| Qwen3.5-27B | max_k_shown | 909 | 26.4 | 26.3 | 0.46 | 0.0 | 85.9 | 14.1 | 0.0 | 68.6 | 9.5 |
| Qwen3.5-27B | min_k_shown | 909 | 60.9 | 60.6 | 1.72 | 2.4 | 38.9 | 51.4 | 7.3 | 35.0 | 4.8 |
| Qwen3.5-27B | min_k_shown_fewer_ok | 909 | 42.2 | 42.1 | 0.97 | 1.5 | 61.9 | 35.4 | 1.1 | 51.6 | 7.1 |
| Qwen3.5-27B | min_k_enforced | 909 | 91.6 | 91.4 | 2.57 | 0.0 | 0.6 | 91.2 | 8.3 | 7.9 | 4.1 |
| Qwen3.5-27B | min_k_escape | 909 | 43.6 | 43.1 | 0.97 | 0.0 | 0.1 | 97.2 | 2.6 | 53.8 | 6.2 |
| Gemma 4 31B | none | 909 | 14.4 | 14.2 | 0.20 | 0.0 | 95.6 | 3.2 | 1.2 | 77.8 | 8.6 |
| Gemma 4 31B | prose_up_to_k | 4545 | 16.5 | 16.2 | 0.24 | 0.0 | 95.1 | 4.9 | 0.0 | 76.5 | 12.0 |
| Gemma 4 31B | prose_exactly_k | 4545 | 50.9 | 50.5 | 1.12 | 0.9 | 56.3 | 42.8 | 0.0 | 46.4 | 9.8 |
| Gemma 4 31B | max_k_shown | 909 | 13.6 | 13.4 | 0.18 | 0.0 | 95.4 | 4.5 | 0.1 | 79.0 | 12.0 |
| Gemma 4 31B | min_k_shown | 909 | 62.5 | 62.4 | 1.82 | 4.0 | 38.2 | 44.8 | 13.1 | 33.4 | 5.2 |
| Gemma 4 31B | min_k_shown_fewer_ok | 909 | 16.0 | 15.7 | 0.22 | 0.0 | 93.8 | 5.4 | 0.8 | 77.2 | 7.9 |
| Gemma 4 31B | min_k_enforced | 909 | 85.6 | 85.3 | 2.38 | 0.0 | 0.1 | 86.7 | 13.2 | 13.5 | 4.2 |
| Gemma 4 31B | min_k_escape | 909 | 29.9 | 29.9 | 0.62 | 0.0 | 0.0 | 96.6 | 3.4 | 62.9 | 7.3 |
| Olmo 3.1 32B | none | 909 | 42.2 | 41.7 | 2.01 | 0.9 | 67.8 | 7.5 | 23.9 | 50.4 | 11.5 |
| Olmo 3.1 32B | prose_up_to_k | 4545 | 49.2 | 48.8 | 1.32 | 0.3 | 61.3 | 33.0 | 5.4 | 45.3 | 18.5 |
| Olmo 3.1 32B | prose_exactly_k | 4545 | 54.8 | 54.4 | 1.34 | 0.4 | 51.6 | 46.3 | 1.7 | 39.2 | 20.2 |
| Olmo 3.1 32B | max_k_shown | 909 | 45.0 | 44.7 | 1.07 | 0.9 | 64.4 | 31.7 | 3.1 | 47.4 | 18.4 |
| Olmo 3.1 32B | min_k_shown | 909 | 57.8 | 57.4 | 2.25 | 1.3 | 44.2 | 37.4 | 17.1 | 35.9 | 12.9 |
| Olmo 3.1 32B | min_k_shown_fewer_ok | 909 | 18.7 | 18.5 | 0.49 | 2.9 | 83.3 | 10.0 | 3.9 | 51.3 | 34.6 |
| Olmo 3.1 32B | min_k_enforced | 909 | 95.6 | 93.0 | 3.65 | 0.0 | 0.6 | 73.2 | 26.3 | 4.2 | 9.1 |
| Olmo 3.1 32B | min_k_escape | 909 | 49.5 | 49.3 | 1.90 | 0.0 | 0.0 | 80.5 | 19.5 | 41.9 | 15.3 |
| Ministral 3 14B | none | 909 | 50.2 | 49.9 | 2.07 | 0.0 | 68.0 | 7.5 | 24.5 | 47.5 | 6.9 |
| Ministral 3 14B | prose_up_to_k | 4545 | 59.9 | 59.6 | 1.51 | 0.1 | 58.0 | 39.0 | 2.9 | 38.5 | 12.5 |
| Ministral 3 14B | prose_exactly_k | 4545 | 67.5 | 67.1 | 1.70 | 0.2 | 45.4 | 52.9 | 1.5 | 31.2 | 12.7 |
| Ministral 3 14B | max_k_shown | 909 | 46.5 | 46.5 | 1.25 | 0.0 | 70.0 | 21.5 | 8.6 | 50.6 | 10.3 |
| Ministral 3 14B | min_k_shown | 909 | 67.7 | 67.2 | 2.35 | 0.0 | 42.1 | 40.4 | 17.5 | 31.8 | 8.1 |
| Ministral 3 14B | min_k_shown_fewer_ok | 909 | 32.7 | 32.6 | 0.72 | 0.0 | 77.9 | 19.8 | 2.3 | 55.8 | 17.2 |
| Ministral 3 14B | min_k_enforced | 909 | 97.2 | 96.9 | 3.14 | 0.3 | 0.3 | 82.2 | 17.2 | 2.2 | 9.9 |
| Ministral 3 14B | min_k_escape | 909 | 24.3 | 24.2 | 0.60 | 0.0 | 0.0 | 93.6 | 6.4 | 49.6 | 29.4 |
| gpt-oss-20b | none | 909 | 33.9 | 33.8 | 1.04 | 0.0 | 79.6 | 8.1 | 12.2 | 59.7 | 8.6 |
| gpt-oss-20b | prose_up_to_k | 4545 | 43.7 | 43.2 | 1.08 | 0.0 | 66.3 | 31.7 | 1.9 | 52.1 | 14.5 |
| gpt-oss-20b | prose_exactly_k | 4545 | 54.9 | 54.5 | 1.36 | 0.3 | 40.6 | 58.5 | 0.7 | 41.2 | 15.0 |
| gpt-oss-20b | max_k_shown | 909 | 40.3 | 40.0 | 0.91 | 0.0 | 70.6 | 29.4 | 0.0 | 55.2 | 14.0 |
| gpt-oss-20b | min_k_shown | 909 | 64.2 | 64.0 | 1.90 | 8.1 | 11.8 | 67.2 | 12.9 | 26.2 | 9.0 |
| gpt-oss-20b | min_k_shown_fewer_ok | 909 | 39.3 | 38.9 | 1.14 | 4.4 | 58.7 | 29.8 | 7.0 | 49.7 | 11.4 |
| gpt-oss-20b | min_k_enforced | 908 | 71.8 | 71.5 | 2.13 | 0.2 | 0.1 | 87.6 | 12.1 | 27.2 | 7.3 |
| gpt-oss-20b | min_k_escape | 907 | 40.6 | 39.9 | 1.21 | 0.0 | 0.0 | 88.4 | 11.6 | 53.8 | 8.7 |

## 5b. Unreadable outputs, all conditions and k

JSON read but no answer list = the parse ladder found JSON but no list it may take as the answer; almost always the answer written inside a copy of the schema, which the frozen rules never take (protocol 5.1). Cut at the token limit = finish_reason length.

| model | ok outputs | unreadable | unreadable % | JSON read but no answer list | cut at the token limit |
|---|---|---|---|---|---|
| Qwen3.5-0.8B | 26783 | 9810 | 36.6 | 9521 | 21 |
| Qwen3.5-2B | 26781 | 93 | 0.3 | 0 | 3 |
| Qwen3.5-9B | 26784 | 10 | 0.0 | 2 | 2 |
| Qwen3.5-27B | 26784 | 122 | 0.5 | 0 | 5 |
| Gemma 4 31B | 26784 | 77 | 0.3 | 0 | 0 |
| Olmo 3.1 32B | 26784 | 178 | 0.7 | 85 | 18 |
| Ministral 3 14B | 26784 | 21 | 0.1 | 0 | 3 |
| gpt-oss-20b | 26778 | 128 | 0.5 | 0 | 4 |
| DeepSeek V4.1 Flash (Together) | 26784 | 0 | 0.0 | 0 | 0 |
| Qwen3.5-9B (Together) | 26784 | 8 | 0.0 | 1 | 1 |
| Kimi K3 (Bedrock) | 23436 | 0 | 0.0 | 0 | 0 |
| DeepSeek V3.2 (Bedrock) | 23436 | 13 | 0.1 | 3 | 0 |
| Qwen3-235B (Bedrock) | 23436 | 0 | 0.0 | 0 | 0 |
| Mistral Large 3 (Bedrock) | 23436 | 80 | 0.3 | 0 | 80 |
| Ministral 3 14B (Bedrock) | 23436 | 20 | 0.1 | 1 | 0 |
| gpt-oss-20b (Bedrock) | 23436 | 127 | 0.5 | 0 | 5 |
| gpt-oss-120b (Bedrock) | 23436 | 4 | 0.0 | 0 | 0 |

## 6. Sorting every output (C3), 8 main models pooled

Each output on a document with n < k (k = 3 and 5) sorted as padded (more substantive entries than n; wins over a note), says it is short (not padded; a placeholder, an N/A or a note outside the list), honest short list, or unreadable. Shares in %.

| condition | outputs | padded | says_short | honest_short | unreadable |
|---|---|---|---|---|---|
| none | 7272 | 34.5 | 0.3 | 58.3 | 6.9 |
| prose_up_to_k | 36360 | 42.7 | 0.1 | 53.5 | 3.7 |
| prose_exactly_k | 36360 | 50.9 | 0.6 | 42.5 | 6.0 |
| max_k_shown | 7272 | 35.7 | 0.2 | 56.7 | 7.3 |
| min_k_shown | 7272 | 55.4 | 5.6 | 28.5 | 10.5 |
| min_k_shown_fewer_ok | 7272 | 31.0 | 2.0 | 59.7 | 7.3 |
| min_k_enforced | 7270 | 90.1 | 4.0 | 5.7 | 0.2 |
| min_k_escape | 7267 | 51.0 | 48.0 | 0.9 | 0.1 |

## 6a. Sorting per main model (selected conditions)

| model | condition | padded | says_short | honest_short | unreadable |
|---|---|---|---|---|---|
| Qwen3.5-0.8B | none | 30.9 | 1.1 | 13.8 | 54.2 |
| Qwen3.5-0.8B | min_k_shown | 24.9 | 0.3 | 7.4 | 67.4 |
| Qwen3.5-0.8B | min_k_shown_fewer_ok | 34.0 | 0.4 | 16.5 | 49.1 |
| Qwen3.5-0.8B | max_k_shown | 29.3 | 0.2 | 13.0 | 57.5 |
| Qwen3.5-0.8B | min_k_enforced | 91.9 | 3.3 | 4.1 | 0.8 |
| Qwen3.5-2B | none | 55.1 | 0.0 | 44.8 | 0.1 |
| Qwen3.5-2B | min_k_shown | 60.4 | 0.0 | 39.4 | 0.2 |
| Qwen3.5-2B | min_k_shown_fewer_ok | 46.9 | 0.0 | 52.5 | 0.7 |
| Qwen3.5-2B | max_k_shown | 55.7 | 0.0 | 44.2 | 0.1 |
| Qwen3.5-2B | min_k_enforced | 94.5 | 1.1 | 4.4 | 0.0 |
| Qwen3.5-9B | none | 26.3 | 0.0 | 73.7 | 0.0 |
| Qwen3.5-9B | min_k_shown | 44.8 | 0.0 | 55.1 | 0.1 |
| Qwen3.5-9B | min_k_shown_fewer_ok | 18.0 | 0.0 | 82.0 | 0.0 |
| Qwen3.5-9B | max_k_shown | 28.9 | 0.0 | 71.1 | 0.0 |
| Qwen3.5-9B | min_k_enforced | 92.7 | 2.2 | 4.8 | 0.2 |
| Qwen3.5-27B | none | 23.1 | 0.0 | 76.9 | 0.0 |
| Qwen3.5-27B | min_k_shown | 60.9 | 0.0 | 36.6 | 2.4 |
| Qwen3.5-27B | min_k_shown_fewer_ok | 42.2 | 0.1 | 56.1 | 1.5 |
| Qwen3.5-27B | max_k_shown | 26.4 | 0.0 | 73.6 | 0.0 |
| Qwen3.5-27B | min_k_enforced | 91.6 | 2.2 | 6.2 | 0.0 |
| Gemma 4 31B | none | 14.4 | 0.0 | 85.6 | 0.0 |
| Gemma 4 31B | min_k_shown | 62.5 | 18.5 | 15.1 | 4.0 |
| Gemma 4 31B | min_k_shown_fewer_ok | 16.0 | 0.0 | 84.0 | 0.0 |
| Gemma 4 31B | max_k_shown | 13.6 | 0.0 | 86.4 | 0.0 |
| Gemma 4 31B | min_k_enforced | 85.6 | 8.0 | 6.4 | 0.0 |
| Olmo 3.1 32B | none | 42.2 | 1.5 | 55.3 | 0.9 |
| Olmo 3.1 32B | min_k_shown | 57.8 | 9.5 | 31.5 | 1.3 |
| Olmo 3.1 32B | min_k_shown_fewer_ok | 18.7 | 6.9 | 71.5 | 2.9 |
| Olmo 3.1 32B | max_k_shown | 45.0 | 1.7 | 52.5 | 0.9 |
| Olmo 3.1 32B | min_k_enforced | 95.6 | 4.4 | 0.0 | 0.0 |
| Ministral 3 14B | none | 50.2 | 0.0 | 49.8 | 0.0 |
| Ministral 3 14B | min_k_shown | 67.7 | 14.1 | 18.3 | 0.0 |
| Ministral 3 14B | min_k_shown_fewer_ok | 32.7 | 7.6 | 59.7 | 0.0 |
| Ministral 3 14B | max_k_shown | 46.5 | 0.0 | 53.5 | 0.0 |
| Ministral 3 14B | min_k_enforced | 97.2 | 2.0 | 0.4 | 0.3 |
| gpt-oss-20b | none | 33.9 | 0.0 | 66.1 | 0.0 |
| gpt-oss-20b | min_k_shown | 64.2 | 2.5 | 25.1 | 8.1 |
| gpt-oss-20b | min_k_shown_fewer_ok | 39.3 | 0.7 | 55.7 | 4.4 |
| gpt-oss-20b | max_k_shown | 40.3 | 0.0 | 59.7 | 0.0 |
| gpt-oss-20b | min_k_enforced | 71.8 | 9.0 | 18.9 | 0.2 |

## 6b. What the extra entries are (matcher v0, unchecked), 8 main models pooled

Matcher v0 labels of the extra entries (substantive entries not matched to a distinct true item) on documents with n < k, k = 3 and 5. These are the matcher's calls, not checked yet: an invented share is stated in the paper only with the authors' matcher check (5.3 b, C11). The matcher v0 does not decide missed_gold or beyond_excerpt (see REPORT.md). Placeholder and repeat shares are of all list entries.

| condition | extra entries | split or restated true item % | real text, wrong kind % | invented % | invented: prompt echo or possible note % | placeholder % of entries | repeat % of entries |
|---|---|---|---|---|---|---|---|
| none | 18109 | 5.5 | 64.6 | 29.8 | 0.0 | 0.0 | 12.5 |
| max_k_shown | 14697 | 5.7 | 66.3 | 27.9 | 0.1 | 0.1 | 17.3 |
| min_k_shown | 22665 | 7.5 | 62.9 | 29.5 | 0.1 | 0.7 | 13.9 |
| min_k_shown_fewer_ok | 13343 | 6.3 | 72.0 | 21.6 | 0.1 | 0.1 | 16.2 |
| min_k_enforced | 26193 | 9.6 | 79.6 | 9.9 | 0.9 | 5.8 | 16.1 |
| min_k_escape | 15198 | 9.8 | 82.4 | 7.2 | 0.6 | 34.2 | 13.3 |

## 7. Answer-key variants (sections 4.2, 4.3): frozen lists, the annotators' counts, kept vs changed lists, overlay

Length change does not need a count; the annotators' counts change only which documents are in the n < k cells. Kept / changed: whether the cleanup changed the document's answer list. overlay rows applied: 5.

| # | frozen lists (primary) | annotators' counts | list kept | list changed | overlay |
|---|---|---|---|---|---|
| C1 | +0.61 [+0.42, +0.80] | +0.65 [+0.43, +0.85] | +0.50 [+0.28, +0.70] | +0.98 [+0.55, +1.37] | +0.61 [+0.41, +0.79] |
| C2 | +0.62 [+0.46, +0.78] | +0.63 [+0.46, +0.79] | +0.68 [+0.49, +0.88] | +0.46 [+0.20, +0.72] | +0.62 [+0.46, +0.79] |
| C3 | +1.11 [+0.97, +1.25] | +1.13 [+0.98, +1.28] | +1.12 [+0.95, +1.30] | +1.08 [+0.87, +1.29] | +1.11 [+0.97, +1.25] |
| C4 | +0.10 [+0.06, +0.15] | +0.09 [+0.05, +0.14] | +0.09 [+0.04, +0.15] | +0.13 [+0.07, +0.19] | +0.10 [+0.06, +0.15] |

- Contrast 2 on over-count (points): frozen +20.9 [+19.5, +22.3]; annotators' counts +19.3 [+17.9, +20.7]; overlay +21.1 [+19.6, +22.6]

## 8. Generality summary (section 2; contrast 2)

- models whose own interval is above 0: 6 of 8 (Qwen3.5-9B, Qwen3.5-27B, Gemma 4 31B, Olmo 3.1 32B, Ministral 3 14B, gpt-oss-20b)
- the 5 families weighted equally (gemma, gpt-oss, mistral, olmo, qwen; within a family its models equally): +0.72 [+0.62, +0.81]
- leaving out gemma: +0.47 [+0.29, +0.65]
- leaving out gpt-oss: +0.59 [+0.40, +0.77]
- leaving out mistral: +0.67 [+0.48, +0.85]
- leaving out olmo: +0.67 [+0.49, +0.85]
- leaving out qwen: +0.78 [+0.69, +0.86]

## 9. Per wording (prose conditions; length change against none and over-count %, n < k, k = 3 and 5)

| condition | wording | vs none (length) | over-count % |
|---|---|---|---|
| prose_up_to_k | up_to_1 | -0.85 [-1.02, -0.69] | 45.2 |
| prose_up_to_k | up_to_2 | -0.79 [-0.97, -0.61] | 42.4 |
| prose_up_to_k | up_to_3 | -0.61 [-0.77, -0.45] | 40.2 |
| prose_up_to_k | up_to_4 | -0.84 [-1.02, -0.67] | 45.9 |
| prose_up_to_k | up_to_5 | -0.72 [-0.89, -0.56] | 40.0 |
| prose_exactly_k | exactly_1 | -0.64 [-0.81, -0.47] | 59.7 |
| prose_exactly_k | exactly_2 | -0.51 [-0.68, -0.33] | 53.7 |
| prose_exactly_k | exactly_3 | -0.43 [-0.61, -0.25] | 51.0 |
| prose_exactly_k | exactly_4 | -0.71 [-0.89, -0.52] | 44.2 |
| prose_exactly_k | exactly_5 | -1.02 [-1.19, -0.84] | 45.8 |

## 10. RQ3 (exploratory): asked for fewer than exist (k < n), share of true items left out by position

Position = rank of the item's first appearance in the document (1 = first; 6 = sixth or later). 8 main models pooled; matcher v0 true-item and split labels.

| condition | 1st | 2nd | 3rd | 4th | 5th | 6th+ |
|---|---|---|---|---|---|---|
| prose_up_to_k | 28.6 | 45.0 | 47.9 | 48.5 | 56.4 | 49.4 |
| prose_exactly_k | 29.7 | 53.4 | 56.4 | 57.7 | 64.4 | 62.0 |
| max_k_shown | 25.9 | 36.1 | 37.5 | 41.7 | 47.9 | 48.5 |
| min_k_shown | 19.1 | 18.1 | 17.1 | 16.4 | 19.1 | 14.0 |
| min_k_shown_fewer_ok | 21.1 | 19.9 | 19.7 | 19.4 | 23.3 | 19.3 |
| min_k_enforced | 13.6 | 11.2 | 10.6 | 8.6 | 13.8 | 7.2 |
| min_k_escape | 16.6 | 13.9 | 13.8 | 11.8 | 15.3 | 10.2 |

## 11. RQ4 (exploratory): item type inside job ads (skills, quoted, vs knowledge, named tools)

| set | contrast 2 (length) | contrast 2 (over-count, points) |
|---|---|---|
| job-ad skills | +1.54 [+0.83, +2.30] | +22.9 [+18.5, +27.4] |
| job-ad knowledge | +0.76 [-0.26, +1.79] | +24.4 [+21.5, +27.3] |

- skills minus knowledge, contrast 2 (length): +0.78 [-0.48, +2.05]

## 12. Hosted models (dated reference, never pooled with the GPU results)

Bedrock runs the prompt-side conditions only, so contrast 5 is empty there.

| model | C1 | C2 | C3 | C4 | C5 | fewer_ok vs none | unreadable % | missing |
|---|---|---|---|---|---|---|---|---|
| DeepSeek V4.1 Flash (Together) | +1.23 [+1.05, +1.43] | +1.40 [+1.25, +1.56] | +1.60 [+1.45, +1.75] | +0.54 [+0.49, +0.59] | -0.64 [-0.71, -0.57] | +0.53 [+0.39, +0.67] | 0.0 | 0 |
| Qwen3.5-9B (Together) | +0.50 [+0.32, +0.68] | +0.64 [+0.50, +0.78] | +0.84 [+0.73, +0.96] | +0.08 [+0.04, +0.13] | -0.58 [-0.67, -0.51] | -0.61 [-0.75, -0.48] | 0.0 | 0 |
| Kimi K3 (Bedrock) | +0.77 [+0.64, +0.91] | +1.25 [+1.12, +1.38] | +1.21 [+1.09, +1.33] | +0.55 [+0.49, +0.60] | -- | +0.32 [+0.24, +0.40] | 0.0 | 0 |
| DeepSeek V3.2 (Bedrock) | +1.30 [+1.07, +1.54] | +2.39 [+2.19, +2.59] | +2.19 [+2.01, +2.38] | +0.33 [+0.29, +0.37] | -- | +0.36 [+0.22, +0.50] | 0.1 | 0 |
| Qwen3-235B (Bedrock) | +1.50 [+1.34, +1.66] | +1.28 [+1.13, +1.43] | +1.35 [+1.23, +1.48] | +0.30 [+0.26, +0.34] | -- | +0.30 [+0.16, +0.43] | 0.0 | 0 |
| Mistral Large 3 (Bedrock) | +1.01 [+0.87, +1.15] | +0.98 [+0.82, +1.14] | +1.24 [+1.12, +1.38] | +0.30 [+0.26, +0.34] | -- | -0.49 [-0.63, -0.35] | 0.3 | 0 |
| Ministral 3 14B (Bedrock) | +0.99 [+0.80, +1.20] | +0.28 [+0.11, +0.45] | +1.25 [+1.11, +1.41] | +0.22 [+0.17, +0.26] | -- | -1.59 [-1.84, -1.34] | 0.1 | 0 |
| gpt-oss-20b (Bedrock) | +0.77 [+0.60, +0.93] | +0.83 [+0.69, +0.98] | +0.97 [+0.85, +1.10] | +0.27 [+0.21, +0.32] | -- | +0.07 [-0.06, +0.20] | 0.5 | 0 |
| gpt-oss-120b (Bedrock) | +0.97 [+0.83, +1.12] | +0.94 [+0.80, +1.08] | +1.08 [+0.97, +1.20] | +0.50 [+0.45, +0.54] | -- | +0.01 [-0.11, +0.12] | 0.0 | 0 |

## 12a. Sorting, hosted models pooled (reference only)

Each output on a document with n < k (k = 3 and 5) sorted as padded (more substantive entries than n; wins over a note), says it is short (not padded; a placeholder, an N/A or a note outside the list), honest short list, or unreadable. Shares in %.

| condition | outputs | padded | says_short | honest_short | unreadable |
|---|---|---|---|---|---|
| none | 8181 | 34.8 | 0.0 | 65.2 | 0.0 |
| prose_up_to_k | 40905 | 44.0 | 0.0 | 56.0 | 0.1 |
| prose_exactly_k | 40905 | 56.2 | 0.2 | 43.5 | 0.1 |
| max_k_shown | 8181 | 38.8 | 0.0 | 61.1 | 0.1 |
| min_k_shown | 8181 | 65.8 | 2.4 | 30.9 | 1.0 |
| min_k_shown_fewer_ok | 8181 | 38.5 | 1.0 | 59.9 | 0.6 |
| min_k_enforced | 1818 | 90.7 | 3.0 | 6.2 | 0.1 |
| min_k_escape | 1818 | 49.9 | 49.7 | 0.3 | 0.0 |

## 13. Same-weights pairs (contrast 2 on the same documents and k)

The serving stack is said not to drive the result if the pair's main contrast differs by less than 10 points; points are over-count points (the contrast is also given in entries).

| pair | hosted (length) | GPU (length) | difference (length) | difference (over-count, points) | under 10 points |
|---|---|---|---|---|---|
| Qwen3.5-9B (Together) vs Qwen3.5-9B | +0.64 [+0.50, +0.78] | +0.62 [+0.50, +0.74] | +0.02 [-0.09, +0.13] | +0.7 [-1.3, +2.6] | yes |
| Ministral 3 14B (Bedrock) vs Ministral 3 14B | +0.28 [+0.11, +0.45] | +0.30 [+0.12, +0.45] | -0.02 [-0.16, +0.12] | -1.1 [-3.4, +1.1] | yes |
| gpt-oss-20b (Bedrock) vs gpt-oss-20b | +0.83 [+0.69, +0.98] | +0.87 [+0.72, +1.01] | -0.04 [-0.18, +0.11] | +0.8 [-2.3, +3.8] | yes |

## 14. Repeat check (300 prompts per model sent twice; the repeat on a newly started server)

Identical = the same reply text. Flip = the over-count verdict differs. Length differs = the number of substantive entries differs. Request ids answered in both runs only.

| model | prompts in both | identical % | over-count flips % | length differs % |
|---|---|---|---|---|
| DeepSeek V3.2 (Bedrock) | 300 | 52.7 | 4.00 | 12.0 |
| gpt-oss-120b (Bedrock) | 300 | 18.0 | 8.00 | 13.0 |
| gpt-oss-20b (Bedrock) | 300 | 31.0 | 4.00 | 10.3 |
| Kimi K3 (Bedrock) | 300 | 92.7 | 0.67 | 2.7 |
| Ministral 3 14B (Bedrock) | 300 | 67.0 | 1.33 | 5.3 |
| Mistral Large 3 (Bedrock) | 300 | 54.0 | 7.00 | 14.7 |
| Qwen3-235B (Bedrock) | 300 | 64.3 | 3.00 | 4.3 |
| Gemma 4 31B | 300 | 98.7 | 0.00 | 0.3 |
| gpt-oss-20b | 300 | 59.3 | 3.00 | 11.3 |
| Ministral 3 14B | 300 | 88.7 | 1.00 | 3.0 |
| Olmo 3.1 32B | 300 | 87.7 | 0.67 | 2.3 |
| Qwen3.5-0.8B | 300 | 71.7 | 3.00 | 12.3 |
| Qwen3.5-27B | 300 | 94.7 | 0.33 | 0.7 |
| Qwen3.5-2B | 300 | 82.3 | 1.67 | 9.3 |
| Qwen3.5-9B | 300 | 90.3 | 0.67 | 2.0 |
| DeepSeek V4.1 Flash (Together) | 300 | 65.3 | 5.00 | 9.7 |
| Qwen3.5-9B (Together) | 300 | 84.0 | 2.33 | 5.7 |

## 15. Re-ask arm (exploratory): min_k_shown replies shorter than k sent back once with the validation error

Before = the first reply, after = the reply to the re-ask. Sorting after, on n < k: padded / says_short / honest_short / unreadable (%).

| model | re-asked | after: k or more entries % | re-asked with n < k | over-count before % | over-count after % | length change | sorting after |
|---|---|---|---|---|---|---|---|
| Kimi K3 (Bedrock) | 510 | 100.0 | 508 | 14.0 | 78.3 | +1.89 | 78 / 6 / 16 / 0 |
| Ministral 3 14B (Bedrock) | 410 | 85.6 | 405 | 21.7 | 81.5 | +1.99 | 81 / 10 / 3 / 6 |
| Gemma 4 31B | 429 | 89.7 | 427 | 11.2 | 44.0 | +0.63 | 44 / 30 / 19 / 7 |
| Ministral 3 14B | 425 | 86.6 | 419 | 21.5 | 81.6 | +1.98 | 82 / 9 / 4 / 5 |
| Qwen3.5-9B | 678 | 73.0 | 639 | 10.0 | 69.0 | +1.70 | 69 / 1 / 30 / 0 |

## 16. Thinking side test (exploratory; sampled decoding, per request seed)

| thinking on | partner (off) | seed | C2 on (length) | C2 off (length) | on minus off | min_k_shown over-count on % | off % |
|---|---|---|---|---|---|---|---|
| qwen3.5-9b-think | qwen3.5-9b-nothink | 1 | +1.77 [+1.62, +1.92] | +0.64 [+0.50, +0.77] | +1.14 [+0.94, +1.32] | 81.3 | 45.2 |
| qwen3.5-9b-think | qwen3.5-9b-nothink | 2 | +1.78 [+1.64, +1.92] | +0.59 [+0.44, +0.74] | +1.19 [+0.98, +1.39] | 83.2 | 47.1 |
| qwen3.5-9b-think | qwen3.5-9b-nothink | 3 | +1.69 [+1.46, +1.88] | +0.55 [+0.38, +0.71] | +1.14 [+0.91, +1.36] | 81.5 | 43.0 |
| qwen3.5-9b-think-pp0 | qwen3.5-9b-nothink-pp0 | 1 | +2.45 [+2.16, +2.73] | +1.37 [+1.03, +1.72] | +1.08 [+0.63, +1.51] | 100.0 | 75.0 |
| qwen3.5-9b-think-pp0 | qwen3.5-9b-nothink-pp0 | 2 | +2.33 [+2.00, +2.64] | +1.25 [+0.69, +1.71] | +1.08 [+0.62, +1.56] | 99.2 | 80.0 |
| qwen3.5-9b-think-pp0 | qwen3.5-9b-nothink-pp0 | 3 | +2.43 [+2.09, +2.78] | +1.29 [+0.91, +1.66] | +1.14 [+0.68, +1.62] | 98.3 | 74.2 |
| gemma-4-31b-think | gemma-4-31b-sampled | 1 | +1.52 [+1.39, +1.64] | +1.63 [+1.50, +1.76] | -0.11 [-0.23, +0.01] | 66.1 | 61.8 |
| bedrock-kimi-k3-think | bedrock-kimi-k3 | - | +2.42 [+2.09, +2.76] | +1.84 [+1.48, +2.24] | +0.58 [+0.23, +0.91] | 97.5 | 91.7 |

Thinking text naming a shortfall (phrase search, NOT checked by hand; C16), outputs with n < k:

| model | seed | outputs | trace names a shortfall % | of padded outputs % |
|---|---|---|---|---|
| qwen3.5-9b-think | 1 | 2727 | 87.2 | 87.9 |
| qwen3.5-9b-think | 2 | 2727 | 88.5 | 89.0 |
| qwen3.5-9b-think | 3 | 2727 | 88.1 | 88.3 |
| qwen3.5-9b-think-pp0 | 1 | 360 | 78.9 | 80.1 |
| qwen3.5-9b-think-pp0 | 2 | 360 | 83.6 | 84.5 |
| qwen3.5-9b-think-pp0 | 3 | 360 | 80.8 | 82.4 |
| gemma-4-31b-think | 1 | 2726 | 51.7 | 59.2 |
| bedrock-kimi-k3-think | - | 1820 | 31.3 | 29.6 |

## 17. Not computed from these runs

- RQ5 (closing probability), RQ7 (token confidence) and RQ8 (hidden-state probe) need the teacher-forced and hidden-state passes (harness/teacher_forced.py, analysis/rq7.py); none was run on the full-study outputs, so they are not in these tables.
- The robustness arms (block_llamaindex, base_neutral) ran on the pilot documents in the pilot only; they are not part of the full-study runs.
- The dev runs (reserve documents) are scored (runs.md) but enter no test.
