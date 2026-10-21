# The authors' checks: results

Written by `python analysis/full_study_sheets.py check`.

## (a) Scoring check

65 outputs read.

| id | field | author | scorer | notes |
|---|---|---|---|---|
| S02 | substantive | 3 | 4 |  |
| S02 | repeats | 2 | 1 |  |
| S45 | entries | 2 | 1 |  |
| S45 | substantive | 2 | 1 |  |
| S46 | entries | 2 | 1 |  |
| S46 | substantive | 2 | 1 |  |
| S47 | entries | 3 | 2 |  |
| S47 | substantive | 3 | 2 |  |
| S47 | over-count | True | False |  |

Disagreements: 9. Each needs its cause written next to it (the protocol asks for every one).

## (b) Matcher labels

Both authors labelled 400 entries: same label 370 (92.5%), kappa 0.896, AC1 0.912.

| matcher label | frame entries | checked | precision [95% CI] | recall, frame-weighted [95% CI] |
|---|---|---|---|---|
| true_or_split | 637844 | 134 | 0.98 [0.95, 1.00] | 0.94 [0.90, 0.97] |
| in_text_wrong_type | 408859 | 133 | 0.85 [0.78, 0.91] | 0.96 [0.93, 0.99] |
| missed_gold | 0 | 0 | -- | -- |
| beyond_excerpt | 0 | 0 | -- | -- |
| plausible_invented | 78798 | 131 | 0.69 [0.56, 0.83] | 0.66 [0.53, 0.83] |

- invented share of substantive entries, as the matcher gives it: 0.070; corrected with the authors' labels (frame-weighted): 0.073
- 5 entries settled as missed_gold written to overlay_candidates.jsonl; the authors add the item text, reason, who and date before any of them goes into analysis/gold_overlay.jsonl.

## (c) Hand recount

| output | field | author | scorer | notes |
|---|---|---|---|---|
| R08-2 | true items left out | 1 | 0 | Marketing Expert entry is about market research, not the user requirement specification or devices |
| R08-3 | true items left out | 1 | 0 | User requirements are given to the Project Manager, not the Marketing Expert; no entry matches the true item |
| R08-4 | true items left out | 1 | 0 | No Marketing Expert entry |
| R09-1 | substantive | 1 | 0 | List is wrapped in a schema-shaped object but readable; the attachment line is not a request |
| R09-1 | over-count | True | False | List is wrapped in a schema-shaped object but readable; the attachment line is not a request |
| R09-1 | sort | padded | unreadable | List is wrapped in a schema-shaped object but readable; the attachment line is not a request |
| R09-2 | substantive | 4 | 0 | Schema-shaped object; entries are statements from the email, not requests |
| R09-2 | over-count | True | False | Schema-shaped object; entries are statements from the email, not requests |
| R09-2 | sort | padded | unreadable | Schema-shaped object; entries are statements from the email, not requests |
| R09-3 | substantive | 5 | 0 | Schema-shaped object; entries are statements from the email, not requests ("Thanks!" counted as a real entry) |
| R09-3 | over-count | True | False | Schema-shaped object; entries are statements from the email, not requests ("Thanks!" counted as a real entry) |
| R09-3 | sort | padded | unreadable | Schema-shaped object; entries are statements from the email, not requests ("Thanks!" counted as a real entry) |
| R09-4 | substantive | 1 | 0 | List is wrapped in a schema-shaped object but readable; the attachment line is not a request |
| R09-4 | over-count | True | False | List is wrapped in a schema-shaped object but readable; the attachment line is not a request |
| R09-4 | sort | padded | unreadable | List is wrapped in a schema-shaped object but readable; the attachment line is not a request |
| R09-5 | substantive | 3 | 0 | Schema-shaped object; entries recast the sender's own actions as requests |
| R09-5 | over-count | True | False | Schema-shaped object; entries recast the sender's own actions as requests |
| R09-5 | sort | padded | unreadable | Schema-shaped object; entries recast the sender's own actions as requests |
| R09-6 | substantive | 1 | 0 | List is wrapped in a schema-shaped object but readable; the attachment line is not a request |
| R09-6 | over-count | True | False | List is wrapped in a schema-shaped object but readable; the attachment line is not a request |
| R09-6 | sort | padded | unreadable | List is wrapped in a schema-shaped object but readable; the attachment line is not a request |
| R09-7 | substantive | 1 | 0 | List is wrapped in a schema-shaped object but readable; the attachment line is not a request |
| R09-7 | over-count | True | False | List is wrapped in a schema-shaped object but readable; the attachment line is not a request |
| R09-7 | sort | padded | unreadable | List is wrapped in a schema-shaped object but readable; the attachment line is not a request |
| R09-2 | length change vs none | 3 | 0 | |
| R09-3 | length change vs none | 4 | 0 | |
| R09-5 | length change vs none | 2 | 0 | |

Differences: 27. Each is traced to its cause before any headline number is read.
