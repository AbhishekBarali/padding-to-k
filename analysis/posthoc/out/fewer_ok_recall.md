# Post hoc: the recall cost of "fewer is fine", with an interval

True items left out (%), documents with n >= 1, k = 3 and 5, matcher v0 labels. Unpaired: every ok output of the condition, as in RESULTS.md section 5. Paired: (model, document, k) answered under both conditions; difference in points with a 95% interval from 10000 draws over document groups within set.

| models | left out, none | left out, fewer is fine | paired difference (points) | pairs | groups |
|---|---|---|---|---|---|
| 8 GPU models (registered) | 17.0 | 24.3 | +7.2 [+6.4, +8.1] | 7248 | 444 |
| 7 GPU models, without Qwen3.5-0.8B | 9.9 | 18.4 | +8.5 [+7.6, +9.5] | 6342 | 444 |
