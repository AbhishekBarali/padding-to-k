# POST HOC: Qwen3.5-0.8B with a lenient parser

Written by `analysis/posthoc/lenient_08b.py`. Strict = the locked parser (the paper's numbers); lenient = the same ladder, plus the answer list taken from inside a schema copy or a wrapper object.

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
