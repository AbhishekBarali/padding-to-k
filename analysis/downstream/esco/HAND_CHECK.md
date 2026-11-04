# Hand check of the ESCO linker

Written by `python analysis/downstream/esco/hand_check.py read hand_check_A.xlsx hand_check_B.xlsx`. 50 links drawn with seed 20261013 (`hand_check_ids.csv`): 25 from true items, 25 from model entries that are not true items; cutoff 0.5.

| who | links answered | correct | accuracy | 95% Wilson interval | true-item links | entry links |
|---|---|---|---|---|---|---|
| author A | 50 / 50 | 28 | 56% | 42% to 69% | 13 / 25 | 15 / 25 |
| author B | 50 / 50 | 26 | 52% | 39% to 65% | 12 / 25 | 14 / 25 |

- Answered by both: 50. Same answer: 48 (96%); Cohen's kappa 0.92.
- Correct according to both authors: 26 of 50 (52%).
- Answered differently: E07, T17.
