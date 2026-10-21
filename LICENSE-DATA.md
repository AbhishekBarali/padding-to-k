# Data licence

The data in this repository (documents, answer lists, prompts, labels, scored tables and results) is
released under the **Creative Commons Attribution-ShareAlike 4.0 International** licence
([CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)). Three of the source datasets are
share-alike, so the benchmark as a whole must be too. The code is MIT (`LICENSE`).

The documents come from the datasets below. If you use them, please also credit and cite the source
dataset, as its licence asks.

| Set | Source dataset | Source licence | Text in this repository? |
|---|---|---|---|
| meetings | AMI Meeting Corpus (Carletta et al., 2005), manual annotations 1.6.2 | CC BY 4.0 | Yes |
| emails | MailEx (Srivastava et al., 2023), on Enron emails | CC BY-SA 4.0 | Yes |
| receipts | CORD v2 (Park et al., 2019) | CC BY 4.0 | Yes |
| job-ad skills | SkillSpan (Zhang et al., 2022) | CC BY 4.0; the TECH job ads are CC BY-SA | Yes |
| job-ad knowledge | SkillSpan (Zhang et al., 2022) | CC BY 4.0; the TECH job ads are CC BY-SA | Yes |
| clinical | MACCROBAT2020 (Caufield, 2019), PubMed Central case reports | CC BY 4.0 | Yes |
| reviews | ROAST (Chebolu et al., 2024) | Apache-2.0 for the annotations; the review text states no licence | **No.** Only ids and text hashes; `data/build.py` rebuilds the text from the original source |
| Wikipedia people | Few-NERD (Ding et al., 2021) | CC BY-SA 4.0 | Yes |
| novel quotes | PDNC (Vishnubhotla et al., 2022) | CC BY 4.0; the novels are public domain in the US | Yes |

`data/sources.yaml` gives each source's URL, pinned revision, the hash of every file and its exact
licence sentence. The only changes to a source text are removing lines that give the count away (for
example "TOTAL ITEMS 3" on receipts), whitespace, re-joined tokens and repaired characters, each recorded
in the document's `flags`.

The Enron emails are real people's mail, public since 2003. The case reports are published and
de-identified. Model weights are not redistributed; each model's licence is in its model card
(`configs/models.yaml` has the ids and revisions).
