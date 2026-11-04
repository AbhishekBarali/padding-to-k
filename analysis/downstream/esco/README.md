# Job-ad skills linked to ESCO (OSF addendum 1, section 3.2)

Exploratory. What padding does to a pipeline that maps extracted job-ad skills onto the ESCO taxonomy: how
many ESCO concepts an output adds that the ad's true items do not have, under each condition against `none`.
Numbers: `RESULTS.md` (all of them, written by the script) and `tex/`.

| File | What it is |
|---|---|
| `fetch_esco.py` | downloads ESCO v1.2.1 (English, CSV package) from ec.europa.eu/esco/download, checks its sha256, writes the concept list |
| `esco_skills_v1.2.1_en.csv.gz`, `ESCO.json` | the skills pillar (13,960 concepts: URI, type, preferred and alternative labels, description); version, URL, date and hashes |
| `esco_linker.py` | the linker: all-mpnet-base-v2 (pinned revision), most similar label, cutoff 0.5 (sensitivity: none, 0.7) |
| `esco_downstream.py` | reads run folders, takes entry text and matcher labels, links, computes the measures with bootstrap intervals |
| `hand_check.py` | the 50-link hand check: `draw` (seed 20261013, ids in `hand_check_ids.csv`), `excel` (the two files), `read` (accuracy, agreement) |
| `hand_check_A.xlsx`, `hand_check_B.xlsx` | one per author, identical; fill "Correct link?" (Yes/No) on every row |
| `links_true_items.csv` | every true item of the two job-ad sets and the concept it links to |
| `requirements.txt` | pinned packages on top of `submission/release/requirements.txt` |

Re-run (from the repository root, with the venv described in `requirements.txt`):

```
.venv/bin/python analysis/downstream/esco/fetch_esco.py --check
.venv/bin/python analysis/downstream/esco/esco_downstream.py \
    --runs ../fs-runs/fs_*_full ../wt-closed/runs/a1_* \
    --scored analysis/full/scored ../wt-final-paper/analysis/full/scored analysis/downstream/esco/cache/scored
.venv/bin/python analysis/tests/test_esco_downstream.py
```

`--runs` takes any run folders: a new run is added by naming its folder. A run without a scored table is
scored first with the frozen scorer (`analysis/full_study_score.py`) into `cache/scored/`. Embeddings are
cached in `cache/`, so a re-run embeds only new texts. The hand-check draw is fixed by `hand_check_ids.csv`
and does not change when runs are added.

After both authors have filled their file:

```
.venv/bin/python analysis/downstream/esco/hand_check.py read analysis/downstream/esco/hand_check_A.xlsx analysis/downstream/esco/hand_check_B.xlsx
```

writes `HAND_CHECK.md` (accuracy per author, on true-item links and entry links apart, and agreement).
