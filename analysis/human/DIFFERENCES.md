# The authors' checks: every difference from the scorer, and its cause

Answers: the two filled check pages (19 Oct, 11:08 UTC). The Excel copies sent at 11:58 hold the same
answers, field for field. Numbers come from `python analysis/full_study_sheets.py check` (`RESULTS.md`).
Every difference below has a cause in how the frozen scorer reads an output. None is a counting slip, and
none changes a frozen rule.

## (a) Scoring check: 9 fields on 4 of 65 outputs

| output | difference | cause |
|---|---|---|
| S02 | repeats: author 2, scorer 1; real entries: author 3, scorer 4 | "Could you please confirm this with Rod and Tracey" restates an earlier entry with a three-word prefix. The author counts it as a repeat. The scorer counts as repeats only entries with the same text or nearly the same words (overlap 0.85; here 0.67) and leaves repeats in other words to the matcher. |
| S45 | entries and real entries: author 2, scorer 1 | Cut at the token limit inside the second entry, which starts with a true item and runs on into the model's reasoning. The author counts the unfinished entry; the scorer keeps only the entries that close before the cut. |
| S46 | same as S45 | Same output pattern and cause. |
| S47 | entries and real entries: author 3, scorer 2; over-count: author yes, scorer no | Same cause: the third entry ("Thanks! (implied: ...") is cut at the token limit. |

## (c) Hand recount: 27 fields on 10 of 70 outputs

| outputs | difference | cause |
|---|---|---|
| R09-1 to R09-7 (Qwen3.5-0.8B, one email) | the author reads a list; the scorer marks the output unreadable (0 entries) | The model wrote its answer inside a copy of the schema (`"type": "object", "properties": {"requests": [...]}`). The frozen parser does not accept a list inside a schema copy, so the scorer counts it as unreadable with 0 entries. The author reads the list inside it. The length changes for R09-2, R09-3 and R09-5 follow from this. |
| R08-2, R08-3, R08-4 (gpt-oss-20b, one meeting) | true items left out: author 1, scorer 0 | The matcher matched an entry to the one true item (the Marketing Expert presents the requirements and researches which devices the remote controls) on shared words such as "market", "research" and "remote control". The entries name another task (R08-2, R08-3) or another person (R08-4). The author is right. Cases like this are what the matcher check in (b) measures. |

## (b) Matcher labels

Both authors labelled the same 400 entries alone and chose the same label for 370 (92.5%, kappa 0.896,
AC1 0.912). They settled the other 30 together on 19 Oct (`settle-labels.xlsx`, imported with
`forms.py settle-import` into `matcher_labels_settled.csv`). Matcher precision and recall against the
settled labels are in `RESULTS.md`. The 5 entries settled as a real item the list forgot are written into
`analysis/gold_overlay.jsonl` with the document's own wording and the authors' reason; the review-set
item's text stays in `data/local/gold_overlay_restricted.jsonl`.
