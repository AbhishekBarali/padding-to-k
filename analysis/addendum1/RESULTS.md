# Closed models (OSF addendum 1, exploratory)

Registered at https://osf.io/45mfb before any request was sent. Each model on its own; never pooled.
Length change in substantive entries (documents with n < k, k = 3 and 5) with 95% group-bootstrap
intervals (10000 draws, seed 20261014). C1 dose, C2 min_k_shown vs none (main measure), C3 vs
max_k_shown, C4 exactly vs up to (wording 1), C5 escape vs enforced (only where the API enforces
minItems). The last row is the 8 main GPU models pooled on the same cells and wording, for reference.

| model | C1 | C2 | C3 | C4 | C5 | fewer_ok vs none | C2 over-count (points) | unreadable % | missing |
|---|---|---|---|---|---|---|---|---|---|
| Grok 4.3 | +0.71 [+0.54, +0.88] | +1.47 [+1.27, +1.70] | +1.64 [+1.45, +1.87] | +0.62 [+0.55, +0.70] | -0.67 [-0.73, -0.60] | +0.91 [+0.75, +1.08] | +34.2 [+30.4, +38.2] | 0.0 | 0 |
| GPT-6 Sol | +0.39 [+0.26, +0.54] | +0.96 [+0.85, +1.07] | +1.09 [+0.99, +1.19] | +1.38 [+1.29, +1.47] | -- | +0.14 [+0.09, +0.21] | +29.3 [+26.0, +32.7] | 0.0 | 8 |
| GPT-6 Luna | +0.15 [+0.02, +0.28] | +0.56 [+0.45, +0.67] | +0.79 [+0.68, +0.90] | +0.70 [+0.62, +0.78] | -0.66 [-0.73, -0.59] | +0.33 [+0.23, +0.44] | +15.7 [+12.9, +18.6] | 0.2 | 11 |
| 8 GPU models (pooled, wording 1) | +0.61 [+0.42, +0.80] | +0.62 [+0.46, +0.78] | +1.11 [+0.97, +1.25] | +0.22 [+0.14, +0.29] | -0.54 [-0.58, -0.50] | -0.77 [-0.93, -0.60] | +20.9 [+19.5, +22.3] | 4.5 | 10 |

## Per condition: over-count (n < k, k = 3 and 5) and empty documents (n = 0, k = 1)

### Grok 4.3

| condition | over-count % | outputs | empty docs with an entry % | outputs |
|---|---|---|---|---|
| none | 25.5 | 909 | 17.1 | 105 |
| prose_up_to_k | 34.9 | 909 | 18.1 | 105 |
| prose_exactly_k | 56.9 | 909 | 32.4 | 105 |
| max_k_shown | 27.3 | 909 | 9.5 | 105 |
| min_k_shown | 59.7 | 909 | 34.3 | 105 |
| min_k_shown_fewer_ok | 49.9 | 909 | 20.0 | 105 |
| min_k_enforced | 89.3 | 909 | 94.3 | 105 |
| min_k_escape | 37.7 | 909 | 7.6 | 105 |

### GPT-6 Sol

| condition | over-count % | outputs | empty docs with an entry % | outputs |
|---|---|---|---|---|
| none | 23.5 | 907 | 14.4 | 104 |
| prose_up_to_k | 22.1 | 909 | 11.4 | 105 |
| prose_exactly_k | 69.3 | 907 | 63.5 | 104 |
| max_k_shown | 20.8 | 909 | 12.4 | 105 |
| min_k_shown | 52.7 | 909 | 49.5 | 105 |
| min_k_shown_fewer_ok | 28.4 | 907 | 53.3 | 105 |

### GPT-6 Luna

| condition | over-count % | outputs | empty docs with an entry % | outputs |
|---|---|---|---|---|
| none | 24.3 | 907 | 10.6 | 104 |
| prose_up_to_k | 24.1 | 909 | 7.6 | 105 |
| prose_exactly_k | 50.8 | 907 | 20.2 | 104 |
| max_k_shown | 21.3 | 909 | 2.9 | 105 |
| min_k_shown | 39.8 | 909 | 57.1 | 105 |
| min_k_shown_fewer_ok | 36.1 | 907 | 79.0 | 105 |
| min_k_enforced | 90.2 | 906 | 71.4 | 105 |
| min_k_escape | 42.8 | 909 | 18.1 | 105 |

### 8 GPU models (pooled, wording 1)

| condition | over-count % | outputs | empty docs with an entry % | outputs |
|---|---|---|---|---|
| none | 34.5 | 7272 | 34.9 | 840 |
| prose_up_to_k | 45.2 | 7272 | 41.4 | 840 |
| prose_exactly_k | 59.7 | 7272 | 52.1 | 840 |
| max_k_shown | 35.7 | 7272 | 33.9 | 840 |
| min_k_shown | 55.4 | 7272 | 42.3 | 840 |
| min_k_shown_fewer_ok | 31.0 | 7272 | 31.8 | 840 |
| min_k_enforced | 90.1 | 7270 | 82.4 | 840 |
| min_k_escape | 51.0 | 7267 | 30.0 | 840 |

## Sorting of min_k_shown outputs (n < k, k = 3 and 5), and what fills the extra slots

| model | padded | says_short | honest_short | unreadable | extra: real text, wrong kind % | extra: invented % | extra entries |
|---|---|---|---|---|---|---|---|
| Grok 4.3 | 59.7 | 0.0 | 40.3 | 0.0 | 91.8 | 1.1 | 1966 |
| GPT-6 Sol | 52.7 | 0.0 | 47.3 | 0.0 | 85.2 | 0.3 | 1260 |
| GPT-6 Luna | 39.8 | 0.0 | 60.2 | 0.0 | 86.4 | 0.9 | 998 |
| 8 GPU models (pooled, wording 1) | 55.4 | 5.6 | 28.5 | 10.5 | 62.9 | 29.5 | 22665 |

## Requests refused by a provider's content filter (a result, not an output)

| model | refused |
|---|---|
| Grok 4.3 | 0 |
| GPT-6 Sol | 6 |
| GPT-6 Luna | 6 |

## Repeat check (300 prompts sent twice)

| model | pairs | identical % | over-count flips % |
|---|---|---|---|
| Grok 4.3 | 300 | 76.0 | 3.33 |
| GPT-6 Sol | 300 | 88.7 | 2.00 |
| GPT-6 Luna | 300 | 89.3 | 2.33 |

## Re-ask with "fewer is fine" (addendum section 2)

Over-count among the re-asked outputs: the registered re-ask against the same replies sent back with the fewer-is-fine line added. Only request ids answered in both runs.

| model | re-asked with n < k (answered in both) | over-count before % | after the registered re-ask % | after the re-ask + fewer is fine % | entries, fewer-is-fine minus registered | sorting after fewer-is-fine (padded / says_short / honest_short / unreadable) |
|---|---|---|---|---|---|---|
| Kimi K3 (Bedrock) | 508 | 14.0 | 78.3 | 37.6 | -1.35 | 38 / 2 / 60 / 0 |
| Ministral 3 14B (Bedrock) | 405 | 21.7 | 81.5 | 34.6 | -1.51 | 35 / 22 / 43 / 0 |
