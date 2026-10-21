# Post hoc: headline numbers without Qwen3.5-0.8B

Documents with n < k, k = 3 and 5; 95% intervals from 10000 draws over document groups within set.

| models | C2 length (entries) | C2 over-count (points) | over-count %, none | min_k_shown | min_k_enforced |
|---|---|---|---|---|---|
| 8 GPU models (registered) | +0.62 [+0.46, +0.78] | +20.9 [+19.5, +22.3] | 34.5 | 55.4 | 90.1 |
| 7 GPU models, without Qwen3.5-0.8B | +0.80 [+0.63, +0.96] | +24.7 [+23.1, +26.4] | 35.0 | 59.8 | 89.9 |
