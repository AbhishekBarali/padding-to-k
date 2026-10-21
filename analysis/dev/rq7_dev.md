# RQ7 preview: confidence of extra entries (dev set, PRELIMINARY)

True = true_item; extra = in_text_wrong_type or plausible_invented (matcher v0 labels, fitted on
provisional labels that are not the authors'). AUROC = how often an extra entry scores LOWER than a
true one (0.5 = no signal). 95% intervals from 2000 bootstrap draws over document groups. Dev outputs only.
`position` is the baseline: the entry's place in the list alone (a later entry counts as lower).

| model | score | true | extra | AUROC | 95% interval | wrong type only | invented only |
|---|---|---|---|---|---|---|---|
| qwen3.5-9b | mean_lp | 2583 | 2178 | 0.669 | 0.611 to 0.729 | 0.665 (2133) | 0.858 (45) |
| qwen3.5-9b | min_lp | 2583 | 2178 | 0.625 | 0.563 to 0.682 | 0.622 (2133) | 0.771 (45) |
| qwen3.5-9b | first_lp | 2583 | 2178 | 0.644 | 0.585 to 0.698 | 0.642 (2133) | 0.763 (45) |
| qwen3.5-9b | position | 2583 | 2178 | 0.760 | 0.725 to 0.793 | 0.759 (2133) | 0.818 (45) |
| ministral-3-14b | mean_lp | 2705 | 3233 | 0.748 | 0.693 to 0.793 | 0.720 (2834) | 0.947 (399) |
| ministral-3-14b | min_lp | 2705 | 3233 | 0.717 | 0.661 to 0.767 | 0.693 (2834) | 0.886 (399) |
| ministral-3-14b | first_lp | 2705 | 3233 | 0.726 | 0.679 to 0.773 | 0.703 (2834) | 0.892 (399) |
| ministral-3-14b | position | 2705 | 3233 | 0.736 | 0.705 to 0.767 | 0.719 (2834) | 0.861 (399) |
| gemma-4-31b | mean_lp | 2705 | 1761 | 0.692 | 0.637 to 0.742 | 0.685 (1678) | 0.845 (83) |
| gemma-4-31b | min_lp | 2705 | 1761 | 0.669 | 0.609 to 0.723 | 0.661 (1678) | 0.830 (83) |
| gemma-4-31b | first_lp | 2705 | 1761 | 0.717 | 0.665 to 0.768 | 0.710 (1678) | 0.860 (83) |
| gemma-4-31b | position | 2705 | 1761 | 0.736 | 0.701 to 0.771 | 0.735 (1678) | 0.772 (83) |

Inputs: tf_2026-10-14_qwen3.5-9b_dev_20261014T1931Z, tf_2026-10-14_ministral-3-14b_dev_20261014T1936Z, tf_2026-10-14_gemma-4-31b_dev_20261014T1945Z; labels matcher_entries_dev.csv.
