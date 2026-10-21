# Matcher v0 on the dev outputs (PRELIMINARY)

Matcher `v0-dev-preliminary` (analysis/matcher.py); dev outputs only (the 312 reserve documents, arm
`dev`; 3 models). The review set is not included: its text is licensed and is not on this machine
(raw_restricted.jsonl, data/local/), so 293 documents are scored.
**The labels used to fit and check the matcher are provisional and NOT the authors' (the authors'
labels replace them in v1).** Every number here is preliminary. No document or output text is reproduced.

## Agreement with the provisional labels: held-out half of the development labels (documents not used to fit thresholds; the rules were written while these labels were visible)

Agreement = same label, and for true_item the same gold item.

| set | agree | n | share |
|---|---|---|---|
| clinical | 21 | 23 | 0.91 |
| emails | 16 | 19 | 0.84 |
| job_posts | 20 | 20 | 1.00 |
| job_posts_knowledge | 16 | 19 | 0.84 |
| meetings | 19 | 21 | 0.90 |
| novel_quotes | 21 | 23 | 0.91 |
| receipts | 26 | 26 | 1.00 |
| wiki_people | 21 | 22 | 0.95 |
| ALL | 160 | 173 | 0.92 |

Confusion (rows: provisional label, columns: matcher label):

| label \ matcher | true_item | split_of_true | in_text_wrong_type | plausible_invented | placeholder |
|---|---|---|---|---|---|
| true_item | 56 | 0 | 1 | 0 | 0 |
| split_of_true | 0 | 3 | 2 | 0 | 0 |
| in_text_wrong_type | 0 | 1 | 92 | 3 | 0 |
| plausible_invented | 0 | 0 | 2 | 9 | 0 |
| placeholder | 0 | 0 | 0 | 4 | 0 |

plausible_invented: the matcher said it 16 times, the label agreed 9 times; the label said it 11 times.

## Agreement with the provisional labels: fresh test labels (documents never seen before; drawn and labelled after the matcher was frozen, then one bug fix: see REPORT.md)

Agreement = same label, and for true_item the same gold item.

| set | agree | n | share |
|---|---|---|---|
| clinical | 10 | 13 | 0.77 |
| emails | 12 | 13 | 0.92 |
| job_posts | 11 | 11 | 1.00 |
| job_posts_knowledge | 11 | 13 | 0.85 |
| meetings | 10 | 13 | 0.77 |
| novel_quotes | 12 | 13 | 0.92 |
| receipts | 13 | 13 | 1.00 |
| wiki_people | 13 | 13 | 1.00 |
| ALL | 92 | 102 | 0.90 |

Confusion (rows: provisional label, columns: matcher label):

| label \ matcher | true_item | split_of_true | in_text_wrong_type | plausible_invented | placeholder |
|---|---|---|---|---|---|
| true_item | 41 | 0 | 0 | 0 | 0 |
| split_of_true | 1 | 2 | 0 | 1 | 0 |
| in_text_wrong_type | 0 | 0 | 48 | 3 | 0 |
| plausible_invented | 0 | 0 | 2 | 1 | 0 |
| placeholder | 0 | 0 | 0 | 3 | 0 |

plausible_invented: the matcher said it 8 times, the label agreed 1 times; the label said it 3 times.

Thresholds: analysis/matcher.py THRESHOLDS, chosen by grid search per set on the fit half; see REPORT.md.

## Precision audit of the invented calls

Random entries the matcher called plausible_invented (no note, no prompt echo) or in_text_wrong_type,
on documents with n < k, labelled WITH the matcher's call in view (not blind).

| set | invented calls checked | label: invented | label: wrong type | label: split | label: note | wrong-type calls checked | label: not invented | extras | matcher invented (plain) | rough corrected |
|---|---|---|---|---|---|---|---|---|---|---|
| clinical | 8 | 6 | 1 | 1 | 0 | 3 | 3 | 344 | 98 | 74 (21%) |
| emails | 8 | 3 | 3 | 2 | 0 | 3 | 3 | 2239 | 115 | 43 (2%) |
| job_posts | 4 | 0 | 4 | 0 | 0 | 3 | 3 | 546 | 14 | 0 (0%) |
| job_posts_knowledge | 8 | 1 | 7 | 0 | 0 | 3 | 3 | 716 | 108 | 14 (2%) |
| meetings | 6 | 3 | 3 | 0 | 0 | 3 | 3 | 835 | 43 | 22 (3%) |
| novel_quotes | 0 | 0 | 0 | 0 | 0 | 3 | 3 | 1185 | 0 | - |
| receipts | 3 | 2 | 0 | 0 | 1 | 3 | 3 | 881 | 6 | 4 (0%) |
| wiki_people | 0 | 0 | 0 | 0 | 0 | 3 | 3 | 694 | 0 | - |

rough corrected = matcher invented calls (plain) x the share of checked calls the label agreed with, per
set; sets with no plain invented calls to check show '-'. The audit is small (3 to 8 calls per set), so
read these as an order of magnitude, not an estimate with known error. Prompt echoes and possible notes
are not in it.

## Label distribution per model x condition x (n < k)

Entries of every ok output (shares of the row). `none` asks for no count, and its one answer serves
k = 1, 3, 5, so it is counted once and shown with '-'.

| model | condition | n vs k | entries | true_item | split_of_true | in_text_wrong_type | plausible_invented | placeholder | repeat |
|---|---|---|---|---|---|---|---|---|---|
| gemma-4-31b | max_k_shown | n<k | 725 | 582 (80%) | 16 (2%) | 127 (18%) | 0 (0%) | 0 (0%) | 0 (0%) |
| gemma-4-31b | max_k_shown | n>=k | 172 | 167 (97%) | 0 (0%) | 5 (3%) | 0 (0%) | 0 (0%) | 0 (0%) |
| gemma-4-31b | min_k_enforced | n<k | 2252 | 625 (28%) | 195 (9%) | 910 (40%) | 58 (3%) | 259 (12%) | 205 (9%) |
| gemma-4-31b | min_k_enforced | n>=k | 199 | 189 (95%) | 1 (1%) | 8 (4%) | 0 (0%) | 1 (1%) | 0 (0%) |
| gemma-4-31b | min_k_shown | n<k | 1303 | 571 (44%) | 145 (11%) | 533 (41%) | 25 (2%) | 0 (0%) | 29 (2%) |
| gemma-4-31b | min_k_shown | n>=k | 201 | 188 (94%) | 1 (0%) | 12 (6%) | 0 (0%) | 0 (0%) | 0 (0%) |
| gemma-4-31b | none | - | 476 | 383 (80%) | 10 (2%) | 83 (17%) | 0 (0%) | 0 (0%) | 0 (0%) |
| ministral-3-14b | max_k_shown | n<k | 1022 | 580 (57%) | 35 (3%) | 385 (38%) | 20 (2%) | 2 (0%) | 0 (0%) |
| ministral-3-14b | max_k_shown | n>=k | 188 | 179 (95%) | 2 (1%) | 6 (3%) | 1 (1%) | 0 (0%) | 0 (0%) |
| ministral-3-14b | min_k_enforced | n<k | 2389 | 595 (25%) | 209 (9%) | 1295 (54%) | 201 (8%) | 57 (2%) | 32 (1%) |
| ministral-3-14b | min_k_enforced | n>=k | 195 | 183 (94%) | 3 (2%) | 8 (4%) | 1 (1%) | 0 (0%) | 0 (0%) |
| ministral-3-14b | min_k_shown | n<k | 1683 | 600 (36%) | 141 (8%) | 803 (48%) | 134 (8%) | 1 (0%) | 4 (0%) |
| ministral-3-14b | min_k_shown | n>=k | 194 | 182 (94%) | 3 (2%) | 9 (5%) | 0 (0%) | 0 (0%) | 0 (0%) |
| ministral-3-14b | none | - | 775 | 386 (50%) | 18 (2%) | 328 (42%) | 42 (5%) | 1 (0%) | 0 (0%) |
| qwen3.5-9b | max_k_shown | n<k | 764 | 551 (72%) | 20 (3%) | 191 (25%) | 2 (0%) | 0 (0%) | 0 (0%) |
| qwen3.5-9b | max_k_shown | n>=k | 186 | 159 (85%) | 1 (1%) | 23 (12%) | 0 (0%) | 0 (0%) | 3 (2%) |
| qwen3.5-9b | min_k_enforced | n<k | 2379 | 605 (25%) | 116 (5%) | 1362 (57%) | 28 (1%) | 53 (2%) | 215 (9%) |
| qwen3.5-9b | min_k_enforced | n>=k | 188 | 164 (87%) | 0 (0%) | 21 (11%) | 2 (1%) | 0 (0%) | 1 (1%) |
| qwen3.5-9b | min_k_shown | n<k | 1077 | 567 (53%) | 75 (7%) | 402 (37%) | 12 (1%) | 0 (0%) | 21 (2%) |
| qwen3.5-9b | min_k_shown | n>=k | 204 | 174 (85%) | 4 (2%) | 24 (12%) | 0 (0%) | 0 (0%) | 2 (1%) |
| qwen3.5-9b | none | - | 487 | 363 (75%) | 12 (2%) | 110 (23%) | 1 (0%) | 0 (0%) | 1 (0%) |

## Extra entries on documents with n < k

Extra = a substantive entry (not a placeholder, not a repeat) that is not matched to a distinct true
item: split_of_true + in_text_wrong_type + plausible_invented. Counted conditions only (`none` has no k).
Of plausible_invented, `note?` reads like a model note the placeholder rules missed and `echo` was
copied from the prompt or schema; both are in the count.

| model | condition | extras | split_of_true | in_text_wrong_type | plausible_invented | note? | echo |
|---|---|---|---|---|---|---|---|
| gemma-4-31b | max_k_shown | 143 | 16 (11%) | 127 (89%) | 0 (0%) | 0 | 0 |
| gemma-4-31b | min_k_enforced | 1163 | 195 (17%) | 910 (78%) | 58 (5%) | 19 | 25 |
| gemma-4-31b | min_k_shown | 703 | 145 (21%) | 533 (76%) | 25 (4%) | 1 | 12 |
| gemma-4-31b | all | 2009 | 356 (18%) | 1570 (78%) | 83 (4%) | 20 | 37 |
| ministral-3-14b | max_k_shown | 440 | 35 (8%) | 385 (88%) | 20 (5%) | 0 | 0 |
| ministral-3-14b | min_k_enforced | 1705 | 209 (12%) | 1295 (76%) | 201 (12%) | 25 | 10 |
| ministral-3-14b | min_k_shown | 1078 | 141 (13%) | 803 (74%) | 134 (12%) | 2 | 0 |
| ministral-3-14b | all | 3223 | 385 (12%) | 2483 (77%) | 355 (11%) | 27 | 10 |
| qwen3.5-9b | max_k_shown | 213 | 20 (9%) | 191 (90%) | 2 (1%) | 0 | 0 |
| qwen3.5-9b | min_k_enforced | 1506 | 116 (8%) | 1362 (90%) | 28 (2%) | 1 | 1 |
| qwen3.5-9b | min_k_shown | 489 | 75 (15%) | 402 (82%) | 12 (2%) | 0 | 0 |
| qwen3.5-9b | all | 2208 | 211 (10%) | 1955 (89%) | 42 (2%) | 1 | 1 |
| all | max_k_shown | 796 | 71 (9%) | 703 (88%) | 22 (3%) | 0 | 0 |
| all | min_k_enforced | 4374 | 520 (12%) | 3567 (82%) | 287 (7%) | 45 | 36 |
| all | min_k_shown | 2270 | 361 (16%) | 1738 (77%) | 171 (8%) | 3 | 12 |
| all | all | 7440 | 952 (13%) | 6008 (81%) | 480 (6%) | 48 | 48 |

Per set, all models and counted conditions pooled (n < k):

| set | extras | split_of_true | in_text_wrong_type | plausible_invented | note? | echo |
|---|---|---|---|---|---|---|
| clinical | 344 | 28 (8%) | 197 (57%) | 119 (35%) | 20 | 1 |
| emails | 2239 | 306 (14%) | 1775 (79%) | 158 (7%) | 6 | 37 |
| job_posts | 546 | 27 (5%) | 505 (92%) | 14 (3%) | 0 | 0 |
| job_posts_knowledge | 716 | 2 (0%) | 606 (85%) | 108 (15%) | 0 | 0 |
| meetings | 835 | 53 (6%) | 739 (89%) | 43 (5%) | 0 | 0 |
| novel_quotes | 1185 | 495 (42%) | 683 (58%) | 7 (1%) | 7 | 0 |
| receipts | 881 | 16 (2%) | 846 (96%) | 19 (2%) | 3 | 10 |
| wiki_people | 694 | 25 (4%) | 657 (95%) | 12 (2%) | 12 | 0 |
