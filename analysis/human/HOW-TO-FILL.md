# How to fill the three check sheets

**Easiest way:** each author gets one page, `check-A.html` or `check-B.html` (built by
`python analysis/human/forms.py build --out <folder outside the repo>`). Open it in a browser, fill every
card, click "Save my answers file" and send back the one file it saves. Author A does jobs 1 and 2, author
B does jobs 3 and 2. `python analysis/human/forms.py import padk-answers-A.json` (and `-B`) fills the
sheets below. The rest of this guide describes the same jobs in sheet form.

There are three jobs. Each one has a sheet you fill in (a `.csv` file, open it in any spreadsheet) and a
reading file (`.md`) that shows you the text you need. Fill only the empty columns. Do not open any file
whose name ends in `_key` until you are done: those hold the computer's answers, and the point is to see
whether you and the computer agree.

Rows about product reviews are in separate files whose names end in `_restricted`. They stay on this
machine and never go into git. Fill them the same way.

| Job | Who | Rows | Time |
|---|---|---|---|
| 1. Scoring check | one of you | 65 replies | about 1 to 1.5 hours |
| 2. Matcher labels | both of you, each alone | 400 entries each | about 3 to 4 hours each, plus about 1 hour together to settle differences |
| 3. Hand recount | one of you | 10 documents, 70 replies | about 1.5 hours |

That is everything. No job comes back for a second round: if you disagree with the computer, you write
down why, and the fix is made in the code, not by you redoing the sheet.

## 1. Scoring check

Files: `scoring_check_sheet.csv` (fill), `scoring_check_pack.md` (read).

Each row is one model reply from the pilot. Find it in the reading file by its id (S01, S02, ...). Read
the reply and the document under it, then fill:

- `list_read_yes_no`: can you find the answer list in the reply? `no` if there is no list at all, or the
  reply only copies the schema, or it was cut off before the first full entry.
- `entries_total`: every entry in that list, good or bad.
- `placeholders`: entries that just say "nothing here", like "N/A", "None", "No further requests". An
  entry copied word for word from the document is never a placeholder.
- `repeats`: entries that say the same thing as an earlier entry, in the same words (small changes like a
  plural don't count as different).
- `substantive`: entries that are neither placeholders nor repeats.
- `over_count_yes_no`: `yes` if `substantive` is bigger than the `n` column (the number of true items).
- `notes`: anything you were unsure about.

Example: n = 1, and the reply is `{"requests": ["Send the report", "N/A", "send the report"]}`.
That is list_read `yes`, entries_total 3, placeholders 1, repeats 1, substantive 1, over_count `no`.

## 2. Matcher labels

Files: `matcher_labels_A.csv` for author A, `matcher_labels_B.csv` for author B (fill your own, without
talking to each other), `matcher_labels_docs.md` (read).

Each row is one list entry a model wrote. You see the entry, the document id, what counts as one item, and
the answer list. The full document is in the reading file under its id. You are not told which model wrote
it, under which instruction, or what the computer thinks it is. Write one word in `label`:

- `true_item`: it is one of the answer list's items (worded a bit differently is fine).
- `split_of_true`: it is a piece of a true item, or the same true item said again in other words.
- `in_text_wrong_type`: it is real text from the document, but not the kind of item asked for.
- `missed_gold`: it is a real item of the right kind that the answer list forgot. Say which in `notes`.
- `beyond_excerpt`: it is real text, but from outside this excerpt (you would only know this if you
  recognise the source; leave it if you don't).
- `plausible_invented`: it is not in the document at all.
- `unsure`: you can't tell. Say why in `notes`.

Example: the list asks for names of people, the sentence is "Anne Westfall met the mayor of Leeds", and
the entry is "Leeds". That is `in_text_wrong_type` (real text, but a place, not a person).

When both sheets are done, sit together, go through the rows where your labels differ, and agree on one
label each. Write the agreed labels in a new file `matcher_labels_settled.csv` with two columns,
`item_id,label` (every row, not only the ones you argued about). Any entry you settle as `missed_gold`
becomes a correction to the answer list later; the script lists those for you.

## 3. Hand recount

Files: `recount_sheet.csv` (fill), `recount_pack.md` (read).

There are 10 documents. For each, the reading file shows the document with its answer list, then 7
replies from one model (R01-1 to R01-7, and so on). For each reply, fill:

- `list_read_yes_no`: as in job 1.
- `substantive`: as in job 1.
- `true_items_left_out`: how many answer-list items no entry of the reply matches.
- `sort`: one of `padded` (more substantive entries than `n`), `says short` (not padded, and it says the
  list is short: an "N/A", a "none found" entry, or a note next to the list), `honest short` (not padded,
  no such note), `unreadable` (no list could be read).
- `notes`: anything odd.

Example: n = 2, k = 3, and the reply is `{"skills": ["teamwork", "attention to detail", "N/A"]}` where both
real skills are on the answer list. That is substantive 2, true_items_left_out 0, sort `says short`.

The script works out the length change (each reply's count minus the no-count reply's count) from your
numbers, so you don't need to.

## When you are done

Send the filled files back (or put them in this folder). Running
`python analysis/full_study_sheets.py check` compares your answers with the computer's and writes
`analysis/human/RESULTS.md`, listing every place you and the computer differ.
