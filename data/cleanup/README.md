# Answer-list cleanup (13 Oct 2026)

A second check of every document's answer list (`gold_items`) and count (`n`). It fixes lists
that were clearly wrong, drops documents that have no single right count, and leaves the real judgment
calls to you. It never touches a document's text.

## The authors' check (13 Oct 2026)

Both authors went through the review queue below (the open questions, every pilot document, and the sample
of fixes and drops) and agreed with every decision. They also confirmed the calls listed under "The rules"
below (M5, M4, V2, E7, C4). The three open questions they settled, recorded as `ruling` in
`decisions.jsonl`:

| Document | Question | Ruling |
|---|---|---|
| mtg-415520 (meetings, pilot, n = 2) | Is the cut-off "you are working on the user requirements" a third job? | Coin flip: dropped. |
| mtg-d03940 (meetings, pilot, n = 2) | Is "look into these ideas and come up with new ones for the next meeting" a job for everyone? | Yes: n = 3, so it moved to the full set. |
| rev-afb7d0 (reviews, n = 6) | Is the "warm reception" a separate feature from the service? | Yes: n = 6 (the hotel itself removed, reception added). |

Wider than the queue: B, whose part of the study is the data, went through every document's answer list
locally, not only the queue above, and reported them correct apart from the cases raised here; A read the
queue, the pilot pages and the open questions and settled the rulings above. That pass was done on B's own
machine and in discussion, so the per-row columns of `review_sheet.csv` and `verify_sheet.csv` are empty in
the repository; what it left behind is the rulings in `decisions.jsonl` and this record. It is a check with
the answer lists in view, which is what it was for. The separate agreement number comes from the blind
check (`blind_check.py`, RUN-PLAN 5.3), where neither author sees a list.

After this check, every cell was trimmed to its final number (`../README.md` section 4). The pilot is now
60 documents. The review queue and its pages are still generated as the authors checked them: pilot means
pilot before trimming, and each row says where the document is now.

## What to review, fastest first

1. **Open questions.** Documents where this pass could not decide. Each has one plain question and a
   proposed list. They are at the top of `review_sheet.csv` (`why_in_sheet` contains "open question").
2. **Pilot documents.** Every document that is or was in the pilot (meetings and emails), changed or not,
   including the ones this pass dropped or moved to the full set because their count changed. Read them on
   GitHub in `review_pilot_meetings.md` and `review_pilot_emails.md`: each shows the text, the annotators'
   list and the list now, with added or split items marked **(cleanup)**.
3. **A sample of fixes and drops** in the other sets: `review_other.md`, same layout. The sample is fixed
   by the seed (20% of fixes, at least 4 per set; 5% of drops, at least 2 per set).

Write your answers in `review_sheet.csv` (one row per document, same order as the pages): `agree_y_n`,
`keep_y_n`, and if you disagree, `right_list_if_not`. Reviews are not in the repo (licence): after
`python build.py` their page and sheet are `local/review_reviews.md` and `local/review_sheet_reviews.csv`.

To see every change, not just the sample: `changes.csv` (one row per fixed, dropped, promoted, trimmed or
open document, with the old and new count and split, the reason and any ruling). Reviews: `changes_reviews_no_text.csv` here (positions
only), and `local/changes_reviews.csv` with the text. `REPORT.md` has the totals and the documents left in
every cell.

## The rules

`COUNTING_RULES.md`. One idea behind all of them: n must be the largest number of separate true items a
careful reader would list, because the study counts anything past n as invented. So a missed true item is
added, a non-item is removed, a bundled item is split, a repeated item is merged, and a document whose
count depends on a borderline call is dropped. Use the same rules when you check.

The calls you are most likely to disagree with (each applied to every document the same way):

- **Meetings, M5:** the Project Manager's own jobs count ("I'll put the minutes in the folder"). Annotators
  left these out almost every time, so many meeting windows went up by one, and several n = 3 windows moved
  into the 4-6 arm.
- **Meetings, M4/M9:** different jobs are separate items even in one annotator sentence; the final
  questionnaire and the meeting summary are two jobs.
- **Reviews, V2:** the product or service as a whole ("the hotel", "this course") is not a feature of
  itself. This removed an item from almost every review and is the main reason so many reviews were dropped.
- **Emails, E7:** advice ("I would recommend...") is borderline, so documents that depend on it were dropped.
- **Clinical, C4:** oxygen, fluids, blood products, contrast and similar substances are borderline, so
  documents that depend on them were dropped.

If you overrule one of these, change the rule in `COUNTING_RULES.md` and the affected rows of
`decisions.jsonl` together, so every document follows the same rule.

## How it is stored, and why it survives a rebuild

- `decisions.jsonl` is the source of truth: one row per checked document, with the status (`ok`, `fixed`,
  `dropped`, `needs_human`), the changes, the reason and the rule. `build.py` selects documents exactly as
  before, then `apply_cleanup.py` applies these rows. Nothing in the source loaders changed.
- Every row records a hash of the text and of the annotators' list it was decided on. If a rebuild ever
  produces a different text or list for that document, the build stops instead of applying a decision to
  something nobody checked.
- In `documents.jsonl` a fixed document keeps the annotators' list as `gold_items_original` (and
  `n_original`); every item carries `origin` (`annotator` or `cleanup`). Dropped documents stay in the
  file with `split: "dropped"`, so they can be audited, and get no prompts. `split_original` records
  where a document started.
- A changed count can move a document: a pilot document that reaches n = 3 goes to the full set, and in
  the pilot sets every n = 2 document is pilot (as in the original selection). A count outside a set's
  range drops it.
- Spares refill each cell to its original number of candidates, using only spares this pass checked and
  found clean, in a fixed seeded order (`cleanup.promoted` says which cell each one refilled).
- Because the first spares were not enough in some cells, `build.py` draws a second batch of spares
  (`EXTRA_SPARES`, `spare_batch: 2`) after every other pick, from groups nothing else uses, so the first
  selection did not change. They were checked under the same rules before any was promoted.
- Review text is never written here. Changes to reviews are stored as character positions plus a hash,
  and `python build.py check` fails if any 40-character stretch of a review appears in a committed file.

To change a decision: edit its row in `decisions.jsonl` (status, `changes`, `reason`), run
`python build.py`, then `python build.py check`.

## How the pass was done

- One AI model, Claude Opus 5.5 (`claude-opus-5.5`, run through Kiro CLI), as a lead and 14 reader
  sessions of the same model: one per set (meetings in two halves), then five more for the second batch of
  spares. Each reader read every document of its set in full, including n = 0 documents and spares, and
  wrote one decision per document with a reason and a rule.
- Readers did not see the first AI pre-check (`ai_precheck.jsonl`, the `ai_precheck` column). The lead
  read those notes only after the readers had decided, then compared the two (`REPORT.md`, last table)
  and re-read every document where they disagreed. That led to a handful of changes, each marked
  "lead reviewer override" in `checked_by`.
- The lead also overrode reader decisions where a rule had been applied two ways (for example interrupted
  quotations, Q2), and turned a few close calls in scarce cells into open questions for you.
- This is an AI second opinion, not a human label. Treat `fixed` lists as proposals you can overrule.
