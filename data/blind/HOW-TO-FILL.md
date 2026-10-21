# How to fill in your blind sheet

## Round 2 (25 texts)

The first round showed that five of the one-line definitions left out rules the answer lists follow, so
those five now say more. For example, skills now ends with "Not tools, technologies, fields of knowledge,
languages or certificates." This round checks the new wording on 25 texts that neither of you has seen:
5 meetings, 5 emails, 5 job ads for skills, 5 job ads for tools, and 5 clinical texts for medications.

- Abhishek: `blind_sheet_round2_A.csv`
- B: `blind_sheet_round2_B.csv`

Everything else works exactly as in the first round, described below. Read the `definition` column of
each row carefully, because it is the new wording. The five meeting transcripts are long, so the whole
sheet takes about 45 minutes to an hour.

## Round 1 (done 15 Oct)

About 35 minutes. 40 short texts. You count things in each one.

## Which file

- Abhishek: `blind_sheet_fresh_A.csv`
- B: `blind_sheet_fresh_B.csv`

Both files have the same 40 texts. Work alone. Do not look at the other person's sheet until both are done.

Ignore every other file in this folder. `blind_sheet.csv` is the old 100-row version, and the `blind_key`
files are only for the script. Also do not open `documents.jsonl`, `verify_sheet.csv` or the
cleanup pages while you work: they show the answers, and the whole point is that you do not see them.

## What each row asks

Each row is one text and one question. Read three columns:

- `text`: the document.
- `list_asked`: what to look for (people, requests, medications, and so on).
- `definition`: exactly what counts as one of those.

## What you write (4 columns)

| Column | What to put |
|---|---|
| `items_found` | The items you found, copied from the text, separated by `;`. Leave it empty if there are none. |
| `n_found` | How many items you found. A whole number: 0, 1, 2, 3 ... **Never leave this empty.** |
| `unclear_y_n` | `y` if two careful people could honestly count this text differently. Otherwise leave it empty. |
| `notes` | Optional. Anything odd, or why you marked it unclear. |

The number in `n_found` is the one that matters. `items_found` is there so we can see what you counted
when you and the answer list differ.

## Two examples

```
list_asked:  people
text:        Tjader died four months after the completion of "Heat Wave", it was his final recording.

items_found: Tjader
n_found:     1
```

```
list_asked:  people
text:        The single received a video on 20 of the following month, in which both singers sing and act.

items_found:
n_found:     0
```

"Both singers" is not a name, so it is 0.

## The rules, short

1. **Only what the text shows.** Do not add things from your own knowledge.
2. **The same thing twice is one item.** "Smith" and "John Smith" for the same person is 1.
3. **Count it like a to-do list.** If you turned the text into a plain list, how many separate lines
   would you write? Two things that could be done, bought or named on their own are two items.
4. **Do not overthink the exact words.** A few words too many or too few is fine.
5. **Not sure?** Still write your best count in `n_found`, and put `y` in `unclear_y_n`. "I am not
   sure" is a useful answer. A blank `n_found` is not, because the script skips that row.

The full rules, with examples for each kind of text, are in `../cleanup/COUNTING_RULES.md`. It contains
none of your 40 texts, so it is safe to read.

## When you are done

1. Save it as CSV (in Excel: "CSV UTF-8"). Keep the file name.
2. Send it back: upload it to the `blind-check-fresh` branch on GitHub (Add file, Upload files), or just
   send the file in chat.

When both sheets are in, the script compares your counts with the answer list and with each other, and
writes a short list of every text where someone differs. We go through that list together, once.
