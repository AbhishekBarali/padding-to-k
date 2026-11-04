# POST HOC: count wordings in real extraction prompts (ScrapeGraphAI-100k)

POST HOC: not in the registered plan. Source: `analysis/posthoc/count_wordings.py`.

Data: `scrapegraphai/scrapegraphai-100k` at revision `0f8d168f2a64632a3ec860059919059273314e66` (licence Apache-2.0), file `data/train.parquet`, 93,695 rows; columns read: id, prompt, schema, schema_hash. Remote LFS sha256 `b0d4e38dad678b9e29379eea9fc1a8bbdce821132c5e3b2a83cadd701b1a16bd`; columns fetched 2026-11-01 04:28 UTC.

Reproduce (from the repository root; reads four columns of the 793 MB file and keeps them as a 16 MB parquet in the gitignored `analysis/posthoc/cache/`):

```
python -m venv .venv
.venv/Scripts/python -m pip install huggingface_hub pyarrow
.venv/Scripts/python analysis/posthoc/count_wordings.py
```

Headline line printed by the script: `HEADLINE rows=93695 any=606 (0.65%) asked_types=517 (0.55%) top=193 up_to=88 at_least=41 at_most=56 exactly=63 first_k=89 bare=127 k1=112 k3=181 k5=136 rules=beff03d2e371`

## Summary

Of 93,695 extraction prompts, 606 (0.65%) carry a count wording of any type below; 517 (0.55%) carry one of the six types named in the ask (all but first_k). 181 prompts (0.19%) ask for k = 3 and 136 (0.15%) for k = 5. Over the 41,538 distinct prompt texts the share is 0.70%. For comparison, 0.01% of rows (0.03% of the 25,453 distinct schemas) have a schema with an open list of strings or objects with minItems >= 2 (JSONSchemaBench: 0.3%, `out/schema_prevalence.md`).

The share is a count of pattern matches, not of judged count wordings: no person has yet checked the matches. Twenty random matches are listed below for that check. Only English wordings are counted.

## Patterns (verbatim from the script)

`NUM` (k in digits or a number word):

```
(?P<num>\d{1,3}(?:,\d{3})+(?![.,]?\d)|\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|hundred)\b
```

| Pattern | Regex |
|---|---|
| top | `\btop[\s-]+(?P<num>\d{1,3}(?:,\d{3})+(?![.,]?\d)\|\d+\|one\|two\|three\|four\|five\|six\|seven\|eight\|nine\|ten\|eleven\|twelve\|thirteen\|fourteen\|fifteen\|sixteen\|seventeen\|eighteen\|nineteen\|twenty\|thirty\|forty\|fifty\|hundred)\b` |
| up_to | `\bup\s+to\s+(?P<num>\d{1,3}(?:,\d{3})+(?![.,]?\d)\|\d+\|one\|two\|three\|four\|five\|six\|seven\|eight\|nine\|ten\|eleven\|twelve\|thirteen\|fourteen\|fifteen\|sixteen\|seventeen\|eighteen\|nineteen\|twenty\|thirty\|forty\|fifty\|hundred)\b` |
| at_least | `\b(?:at\s+least\|a\s+minimum\s+of\|minimum\s+of\|no\s+fewer\s+than\|no\s+less\s+than\|not\s+less\s+than)\s+(?P<num>\d{1,3}(?:,\d{3})+(?![.,]?\d)\|\d+\|one\|two\|three\|four\|five\|six\|seven\|eight\|nine\|ten\|eleven\|twelve\|thirteen\|fourteen\|fifteen\|sixteen\|seventeen\|eighteen\|nineteen\|twenty\|thirty\|forty\|fifty\|hundred)\b` |
| at_most | `\b(?:at\s+most\|no\s+more\s+than\|not\s+more\s+than\|a\s+maximum\s+of\|maximum\s+of\|max(?:imum)?\.?\|limit(?:ed)?\s+to)\s+(?P<num>\d{1,3}(?:,\d{3})+(?![.,]?\d)\|\d+\|one\|two\|three\|four\|five\|six\|seven\|eight\|nine\|ten\|eleven\|twelve\|thirteen\|fourteen\|fifteen\|sixteen\|seventeen\|eighteen\|nineteen\|twenty\|thirty\|forty\|fifty\|hundred)\b` |
| exactly | `\bexactly\s+(?P<num>\d{1,3}(?:,\d{3})+(?![.,]?\d)\|\d+\|one\|two\|three\|four\|five\|six\|seven\|eight\|nine\|ten\|eleven\|twelve\|thirteen\|fourteen\|fifteen\|sixteen\|seventeen\|eighteen\|nineteen\|twenty\|thirty\|forty\|fifty\|hundred)\b` |
| first_k | `\b(?:first\|last\|latest\|next\|most\s+recent\|newest)\s+(?P<num>\d{1,3}(?:,\d{3})+(?![.,]?\d)\|\d+\|one\|two\|three\|four\|five\|six\|seven\|eight\|nine\|ten\|eleven\|twelve\|thirteen\|fourteen\|fifteen\|sixteen\|seventeen\|eighteen\|nineteen\|twenty\|thirty\|forty\|fifty\|hundred)\b` |
| bare | `\b(?:list\|extract\|get\|return\|give\|find\|scrape\|show\|provide\|collect\|fetch\|retrieve\|pull\|grab\|select\|pick\|identify\|name\|choose\|output\|generate\|suggest\|recommend\|gather\|include)(?:\s+(?:me\|us))?(?:\s+(?:the\|only\|just))?\s+(?P<num>\d{1,3}(?:,\d{3})+(?![.,]?\d)\|\d+\|one\|two\|three\|four\|five\|six\|seven\|eight\|nine\|ten\|eleven\|twelve\|thirteen\|fourteen\|fifteen\|sixteen\|seventeen\|eighteen\|nineteen\|twenty\|thirty\|forty\|fifty\|hundred)\b` |

A candidate is then kept or dropped by `accept()` (see the script's docstring): it is dropped when k is a percentage, a decimal, the start of a range, glued to letters, followed by a unit word, followed by "of", or has no noun head within four words (a plural, or any word when k = 1); bare "top k" and "first k" at a clause end are kept.

Unit words: byte, bytes, char, character, characters, chars, cm, day, days, decade, decades, decimal, decimals, digit, digits, dollar, dollars, eur, euro, euros, feet, foot, ft, g, gb, gram, grams, hour, hours, hr, hrs, inch, inches, kb, kg, kgs, km, lb, lbs, letter, letters, line, lines, m, mb, meter, meters, metre, metres, mile, miles, min, mins, minute, minutes, mm, month, months, paragraph, paragraphs, percent, pixel, pixels, pound, pounds, px, sec, second, seconds, secs, sentence, sentences, star, stars, tb, time, times, token, tokens, usd, week, weeks, word, words, year, years, yr, yrs.

Stop words (end the noun-head search): a, about, after, an, and, are, as, at, be, before, between, but, by, can, do, does, each, for, from, had, has, have, how, i, if, in, into, is, it, its, may, must, no, not, of, on, only, or, over, per, should, so, than, that, the, then, these, they, this, those, to, under, was, we, were, what, when, where, which, who, will, with, within, would, you, your.

Request verbs (bare): list, extract, get, return, give, find, scrape, show, provide, collect, fetch, retrieve, pull, grab, select, pick, identify, name, choose, output, generate, suggest, recommend, gather, include.

Rules version 2; rules sha256 (RULES_VERSION, PATTERNS, UNITS, STOP_WORDS, NOT_PLURAL, IRREGULAR_PLURAL, VERBS, NUMBER_WORDS): `beff03d2e371cdf16a711900b8ebc9f2bc1c6547d44f62b4389814616450219e`.

## Counts per pattern

Rows: share of all rows with at least one kept match of the pattern. Distinct: the same over distinct prompt texts. k columns: kept matches in all rows, by k. Number words: kept matches in distinct prompts whose k is written as a word ("top three").

| Pattern | Rows | % rows | Distinct prompts | % distinct | k=1 | k=3 | k=5 | other k | number words |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| top | 193 | 0.21 | 69 | 0.17 | 0 | 84 | 39 | 73 | 2 |
| up_to | 88 | 0.09 | 64 | 0.15 | 10 | 25 | 26 | 47 | 2 |
| at_least | 41 | 0.04 | 12 | 0.03 | 0 | 12 | 0 | 30 | 3 |
| at_most | 56 | 0.06 | 24 | 0.06 | 0 | 5 | 20 | 38 | 0 |
| exactly | 63 | 0.07 | 43 | 0.10 | 56 | 0 | 11 | 6 | 43 |
| first_k | 89 | 0.09 | 50 | 0.12 | 0 | 46 | 39 | 13 | 6 |
| bare | 127 | 0.14 | 56 | 0.13 | 60 | 19 | 11 | 40 | 20 |
| **any** | **606** | **0.65** | **289** | **0.7** | 126 | 191 | 146 | 247 | |
| any of the six asked types | 517 | 0.55 | 239 | 0.58 | | | | | |

A row can match several patterns, so the pattern rows add up to more than the any row. Rows with a kept k = 1: 112; k = 3: 181; k = 5: 136; other k: 221.

## Dropped candidates (distinct prompts)

Candidates the patterns found but `accept()` dropped, by reason. These are the nearby inputs: percentages, units, ranges and the like.

| Pattern | percent | decimal | range | glued | unit | of | no_head |
|---|---:|---:|---:|---:|---:|---:|---:|
| top | 0 | 0 | 0 | 0 | 0 | 0 | 8 |
| up_to | 3 | 2 | 0 | 0 | 1 | 0 | 0 |
| at_least | 0 | 5 | 6 | 0 | 32 | 1 | 24 |
| at_most | 0 | 0 | 2 | 0 | 23 | 0 | 2 |
| exactly | 0 | 0 | 0 | 0 | 16 | 27 | 8 |
| first_k | 0 | 0 | 6 | 0 | 95 | 0 | 30 |
| bare | 0 | 2 | 4 | 0 | 0 | 4 | 81 |

Two dropped examples per reason:

| Reason | Pattern | Prompt around the match |
|---|---|---|
| percent | up_to | ... up to ₹5 lakhs<p>• You can borrow **up to 90**% of your deposit amount at low fixed deposit ... |
| percent | up_to | ... SAP, IBM Maximo, and Oracle systems, delivering **up to 40**% higher workforce productivity, $3M cost savings per facility, ... |
| decimal | at_least | ... platforms that are USB-C to USB-C, and **at least 1**,5 meter in long. Search from Amazon |
| decimal | bare | ... every three months with a sizable amount.<p>• **Get 0**.5% higher interest for senior citizens with IDFC FIRST ... |
| range | at_least | ... many relevant moving companies as possible, with **a minimum of 20**-30 if available. Include both well-known large companies and ... |
| range | at_most | ... and concrete - Avoid marketing language - **Maximum 2**-3 sentences per point - If unclear, answer with ... |
| unit | at_least | ... "prerequisite_type": "Experience", "key": "experience", "value": 4, "reason": "**Minimum of 4** years of professional, full-time experience (post-undergraduate or military) ... |
| unit | first_k | ... Finance, VP Finance, FP&A, Finance Controller) in **last 3** months. \nPain Point: Founders getting buried in finance ... |
| of | exactly | ... placeholder values.', 'heating': '[REQUIRED FORMAT] Must be **EXACTLY one** of these values: central, underfloor, heat_pump, electric, gas, ... |
| of | exactly | ... placeholder values.', 'energy_label': '[REQUIRED FORMAT] Must be **EXACTLY one** of these values: A+++, A++, A+, A, B, ... |
| no_head | first_k | Show **first 2** link of products |
| no_head | bare | ... Series B, Growth). - Their industry focus (**choose one**: AI, Deep Tech, SaaS, Consumer), Healthcare, FinTech). - ... |

## 20 random matches for the owner's check

Drawn with seed 20261101 across all patterns from the 186 kept matches with a distinct pattern and context (of 359 kept matches in distinct prompt texts; near-identical prompts share a context and are drawn once). Match: the anchor, k and the noun head as written. Context: about 15 words around the match (match in bold). Not judged here; the authors judge whether each is a top-k style count wording.

| # | Pattern | k | Match | Context |
|---:|---|---:|---|---|
| 1 | up_to | 5 | up to 5 key specifications | ... (Produktbeschreibung) - Technical data (Technische Daten) - **up to 5** key specifications - Key features (Eigenschaften) - up ... |
| 2 | up_to | 8 | up to 8 products | ... If Druckluft: compressors, regulators, maintenance units Extract **up to 8** products with detailed information. Include German technical terms ... |
| 3 | bare | 10 | Extract 10 publicly available datasets | **Extract 10** publicly available datasets related to the population, including ... |
| 4 | top | 20 | top 20 universities | ... user query: CIO from GCC graduated from **top 20** universities Make sure the you extract all the ... |
| 5 | top | 5 | top 5 keywords | ... or service). 2/ Identify the company_name and **top 5** keywords. 3/ Given the following categories: ['Books & ... |
| 6 | bare | 1 | retrieve one main | ... the body content in three sentences, and **retrieve one** main image, if any. |
| 7 | exactly | 1 | exactly one JSON | ... strings or [] for lists - Output **exactly one** JSON object - no commentary, no extra keys ... |
| 8 | up_to | 7 | up to 7 search results | ... web page (from the initial set of **up to 7** search results) that you analyzed for this entry. ... |
| 9 | top | 20 | top 20 entities | ... tags, include all GPE entities, and the **top 20** entities from the other categories.: |
| 10 | bare | 1 | extract one quote | ... comments, no explanations. Goal: From this page, **extract one** quote where the user genuinely recommends the book ... |
| 11 | top | 5 | top 5 categories | ... with the same scoring B/ Return the **top 5** categories with the highest scoring 3/ Describe the ... |
| 12 | up_to | 25 | up to 25 products | ... For each product you find (aim for **up to 25** products), extract: 1. **Product Identity:** - Full product ... |
| 13 | top | 3 | Top 3 | ... (exactly 'Clarivate') - cluster (exactly 'Competitor - **Top 3**') OUTPUT RULES: - LIST page => include multiple ... |
| 14 | first_k | 5 | first 5 bullets | ... NOT write NA. Fields: title, price, rating, **first 5** bullets under 'About this item'. |
| 15 | bare | 2 | list 2 jobs | Please **list 2** jobs with their titles |
| 16 | first_k | 3 | last 3 reviews | ... and the different types of accommodation.Get the **last 3** reviews, a description of the property, the urls ... |
| 17 | top | 3 | Top 3 | ... (exactly 'Anaqua') - cluster (exactly 'Competitor - **Top 3**') OUTPUT RULES: - LIST page => include multiple ... |
| 18 | at_least | 4 | A minimum of four research courses | ... statistics courses, depending on your background* * **A minimum of four** research courses * A minimum of 9 content ... |
| 19 | top | 5 | Top 5 emerging markets | ... invest in warehouse properties for passive income" "**Top 5** emerging markets for medical office building investments" "Luxury ... |
| 20 | top | 5 | top 5 categories | ... with the same scoring B/ Return the **top 5** categories with the highest scoring 3/ List up ... |

## 5 examples per pattern

| Pattern | k | Context |
|---|---:|---|
| top | 3 | ... (exactly 'Anaqua') - cluster (exactly 'Competitor - **Top 3**') OUTPUT RULES: - LIST page => include multiple ... |
| top | 5 | ... with the same scoring B/ Return the **top 5** categories with the highest scoring 3/ Include a ... |
| top | 20 | ... tags, include all GPE entities, and the **top 20** entities from the other categories.: |
| top | 10 | ... of investing in luxury real estate properties" "**Top 10** cities for affordable real estate investments right now" ... |
| top | 3 | ... digital initiatives. CEO/C-suite mentions operational efficiency in **top 3** strategic priorities. Regulatory audit findings requiring immediate operational ... |
| up_to | 8 | ... = Gross price EXTRACTION INSTRUCTIONS: - Extract **up to 8** individual products - Focus on actual products, not ... |
| up_to | 7 | ... web page (from the initial set of **up to 7** search results) that you analyzed for this entry. ... |
| up_to | 5 | ... (Produktbeschreibung) - Technical data (Technische Daten) - **up to 5** key specifications - Key features (Eigenschaften) - up ... |
| up_to | 8 | ... If Druckluft: compressors, regulators, maintenance units Extract **up to 8** products with detailed information. Include German technical terms ... |
| up_to | 10 | ... to the skills_outcome list. You may include **up to 10** skills. There may be one or multiple outcome ... |
| at_least | 20 | List **at least 20** photos, with each image containing the image URL, ... |
| at_least | 3 | ... these requirements: 1. cheaper than 15000dkk, 2. **At least 3** rooms. 3. Energimærke must be A or B. ... |
| at_least | 2 | ... Verification standard: - Cross-check all information with **at least 2** credible sources before inclusion - If timing information ... |
| at_least | 4 | ... statistics courses, depending on your background* * **A minimum of four** research courses * A minimum of 9 content ... |
| at_least | 2 | ... Verification standard: - Cross-check all information with **at least 2** credible sources before inclusion - Verify the event ... |
| at_most | 7 | ... step 2. Therefore, the array must contain **at most 7** elements.** Each element in this array must be ... |
| at_most | 7 | ... the exact output format (there will be **at most 7** entries in the 'results' array): {"results":[{"url":"https://example.com/page1","bed_count":183},{"url":"https://example.com/page2","bed_count":null}]} |
| at_most | 100 | ... a product, include it. There should be **a maximum of 100** unique products in total. |
| at_most | 3 | ... step 2. Therefore, the array must contain **at most 3** elements.** Each element in this array must be ... |
| at_most | 2 | ... OR "Get reviews for the hyundai creta" (**not more than 2** different review links). 6. For tasks where NUMBER ... |
| exactly | 5 | ... based on the information you extract. Extract **exactly 5** major topics/articles/news that have the most impact. If ... |
| exactly | 1 | Extract **exactly one** person's details and company information from the imprint ... |
| exactly | 1 | ... Ensure that each customer is linked to **exactly one** FIS service and one location. - Avoid duplicate ... |
| exactly | 1 | ... strings or [] for lists - Output **exactly one** JSON object - no commentary, no extra keys ... |
| exactly | 5 | ... based on the information you provide. Extract **exactly 5** major topics/articles/news that have the most impact. If ... |
| first_k | 3 | ... page with multiple items. Extract data from **first 3** items that are available in stock, and have ... |
| first_k | 5 | ... on webpage containing list of items scrap **first 5** items that are in-stock. |
| first_k | 20 | ... History (Example): http://capitol.texas.gov/BillLookup/History.aspx?LegSess=89R&Bill=SB765 For each of the **first 20** bills, extract: - **Basic Details:** - Bill Number ... |
| first_k | 3 | ... page with multiple items. Extract data from **first 3** items that are available in stock, and have ... |
| first_k | 5 | ... product name, price, description, FAQ section, and **first 5** reviews. } |
| bare | 3 | ... (a Vehicle Detail Page). 1. **VDP Indicators:** **Identify 3** generic keywords that can be found only in ... |
| bare | 2 | ... nba games are on 19th November 2024? **Give 2** channels for each country US, CA, and UK. ... |
| bare | 3 | **Find me the 3** best bibimbap spots in Paris and list the ... |
| bare | 3 | ... (a Vehicle Detail Page). 1. **VDP Indicators:** **Identify 3** generic keywords that can be found only in ... |
| bare | 3 | **Extract 3** publicly available datasets related to Electric Vehicles, including ... |

## minItems in the dataset's schemas

Same walker and array classes as `schema_prevalence.py` (open arrays: not fixed-length, not tuples).

| Measure | Rows | % rows | Distinct schemas | % distinct |
|---|---:|---:|---:|---:|
| any array | 84,697 | 90.4 | 22,447 | 88.19 |
| open list of strings/objects, minItems >= 1 | 32 | 0.03 | 16 | 0.06 |
| open array, minItems >= 2 | 11 | 0.01 | 7 | 0.03 |
| open list of strings/objects, minItems >= 2 | 11 | 0.01 | 7 | 0.03 |
| open array, minItems >= 3 | 11 | 0.01 | 7 | 0.03 |
| open array with a maxItems | 28 | 0.03 | 8 | 0.03 |

Schemas that did not parse: 0 rows, 0 distinct.

## Rule changes after looking at matches

| Date | Change | Before | After |
|---|---|---|---|
| 2026-11-01 | first_k no longer counts with nothing after k; only top k does. Found in the first run's matches: 'move forward to the next one.' The first rules are at commit 3342830 (rules sha256 fbe8ef7d58c1). | rows: any 633 (0.68%), asked types 517 (0.55%), first_k 116, k=1 139, k=3 181, k=5 136 | rows: any 606 (0.65%), asked types 517 (0.55%), first_k 89, k=1 112, k=3 181, k=5 136 (other types unchanged) |

## Caveats

- The rows are extraction events from opt-in telemetry of one library (ScrapeGraphAI), Q2-Q3 2025; the release keeps at most 5 rows per schema, and prompts repeat across rows (41,538 distinct texts in 93,695 rows).
- English patterns only; prompts in other languages count as having no count wording.
- A kept match is a pattern match. Some will be false positives (for example a count inside a field description); the random matches above are for a person to judge that.
- A count in the prompt and a minItems in the schema are different things: the first is prose the model reads, the second is a keyword a decoder can enforce.
