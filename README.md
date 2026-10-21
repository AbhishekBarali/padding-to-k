# Padding to k

Code, data and results for the paper **Padding to k: A Minimum Count in the Schema Makes Open-Weight
Models Pad Their Extraction Lists** by Abhishek Barali and Aayush Paudel (2026).

[Paper (PDF)](paper/padding-to-k.pdf) · arXiv: to be added · [Preregistration on OSF](https://osf.io/e4r9f) ·
Model outputs on Zenodo: to be added

Extraction pipelines often ask a language model for JSON that follows a schema, and the schema can say
that a list needs at least *k* entries. We tested what models do when the document holds fewer than *k*
items, with eight open-weight models on 558 real documents from nine annotated datasets, and six more
models on hosted services. Three findings:

- **Models treat the count as a target.** A minimum shown in the schema, but not enforced, raises the share
  of lists longer than the true count from 34.5% to 55.4%.
- **The padding is hard to catch.** Most added entries are real text from the document, so about half of
  them pass a check that each entry occurs in the source.
- **Common fixes help only partly.** Saying that fewer items are fine removes the effect on average but
  misses more true items; "up to *k*" in the prompt also raises over-counting; an "N/A" option under an
  enforced minimum still leaves half the lists padded; re-asking with the validation error makes padding
  far more common.

## What is here

| Folder | What it holds |
|---|---|
| `data/` | The benchmark: 558 documents, their answer lists, the prompts and schemas for every condition, the counting rules (`data/cleanup/COUNTING_RULES.md`), and `build.py`, which rebuilds every file from the original datasets |
| `configs/` | Every model with its pinned revision and server settings, and the chat templates |
| `harness/` | The code that runs the models (vLLM on a GPU, or hosted APIs) and the rules that count entries |
| `analysis/` | Scoring, the item matcher, the statistics, and every result: `analysis/full/` (the study), `analysis/posthoc/out/` (analyses added after the run) |
| `analysis/human/`, `data/blind/` | The human checks: blind counts, the 400 matcher labels from both authors, the scoring check and the recount |
| `preregistration/` | The registered plan and the hash of every file it froze |
| `runs/` | The hosted-model cost test, which the registered cost estimate reads |
| `paper/` | The paper as PDF and its LaTeX source |
| `tools/` | Two small checks, described below |

## Check and reproduce

Python 3.12. From the repository root:

```bash
python3.12 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python tools/check_frozen.py        # every file the plan froze still matches its registered hash
```

**Rebuild the review texts.** The reviews set's text has no licence that allows sharing, so the
repository holds only its ids and text hashes (`data/restricted_ids.jsonl`). This downloads the nine
source datasets once (about 300 MB, into `~/.cache/pad-to-k`) and rebuilds the review texts into
`data/local/`, checking each against its hash:

```bash
(cd data && python build.py && python build.py check)
```

**Rebuild the paper's tables** from the scored tables in `analysis/full/scored/` (about 3 minutes):

```bash
python analysis/full_study.py tables
git status --short analysis/full    # no output means every table matches
```

**Score the model outputs again.** Download the outputs zip from Zenodo and unzip it, then:

```bash
python analysis/full_study_score.py --runs-dir padding-to-k-outputs --cache /tmp/rescored
python tools/compare_scored.py analysis/full/scored /tmp/rescored
```

Every row outside the reviews set matches. Replies on the reviews set are not in the zip, because they
quote the review text.

**Run the models again.** `harness/README.md` has the commands: a GPU with the pinned vLLM image for the
open-weight models, or API keys for Together AI and Amazon Bedrock for the hosted ones.

**Tests:** `python -m pytest harness/tests analysis/tests analysis/posthoc/tests`

## Licences

- Code: MIT (`LICENSE`).
- Data, answer lists, labels and results: CC BY-SA 4.0, because three source datasets are share-alike.
  `LICENSE-DATA.md` lists every source with its licence and how to credit it.

## Citation

```bibtex
@misc{barali2026padding,
  title  = {Padding to $k$: A Minimum Count in the Schema Makes Open-Weight Models Pad Their Extraction Lists},
  author = {Barali, Abhishek and Paudel, Aayush},
  year   = {2026},
  note   = {arXiv identifier to be added}
}
```

Questions or problems: open an issue, or write to abhibidut@gmail.com.
