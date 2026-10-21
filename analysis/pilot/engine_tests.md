# Engine test, one row per model and stack (from runs/enforce/)

minItems 3 / 5 met under the grammar (E02, E03; entries returned in brackets); maxItems respected (E04 to
E06); reasoning seen on replies sent with a grammar / without one; identical repeats of a study request (E14).

| stack | model | in study | >= 3 | >= 5 | max | reasoning, grammar | reasoning, none | repeats | folder | note |
|---|---|---|---|---|---|---|---|---|---|---|
| GPU | Qwen3.5-0.8B | yes | yes (3) | yes (5) | yes | 0/19 | 0/3 | 5/5 | `qwen3.5-0.8b-20261014T144126Z` |  |
| GPU | Qwen3.5-2B | yes | yes (61) | yes (61) | yes | 0/19 | 0/3 | 5/5 | `qwen3.5-2b-20261014T153302Z` | rerun after the parse-ladder fix |
| GPU | Qwen3.5-9B | yes | yes (3) | yes (5) | yes | 0/19 | 0/3 | 4/5 | `qwen3.5-9b-20261014T153000Z` | the xgrammar control of the llguidance test |
| GPU | Qwen3.5-27B | yes | yes (3) | yes (5) | yes | 0/19 | 0/3 | 5/5 | `qwen3.5-27b-20261014T145016Z` |  |
| GPU | Gemma 4 31B | yes | yes (3) | yes (5) | yes | 0/19 | 0/3 | 5/5 | `gemma-4-31b-20261014T143023Z` | as configured, with the reasoning parser |
| GPU | Ministral 3 14B | yes | yes (3) | yes (5) | yes | 0/19 | 0/3 | 5/5 | `ministral-3-14b-20261014T141128Z` |  |
| GPU | OLMo 3.1 32B | yes | yes (3) | yes (5) | yes | 0/19 | 0/3 | 5/5 | `olmo-3.1-32b-20261014T181319Z` | with the template copy, from models.yaml |
| GPU | gpt-oss-20b | yes | yes (3) | yes (5) | yes | 18/18 | 3/3 | 0/5 | `gpt-oss-20b-20261014T181628Z` | batch invariance off, from models.yaml |
| GPU | gpt-oss-120b | no | no (1) | no (1) | no: E06 | 19/19 | 3/3 | 0/5 | `gpt-oss-120b-20261014T162209Z` | out |
| GPU | Qwen3.5-9B, thinking | yes | yes (3) | yes (5) | yes | 19/19 | 3/3 | 0/5 | `qwen3.5-9b-think-20261014T190852Z` | card sampling, 81,920 tokens |
| GPU | Gemma 4 31B, thinking | yes | timeout | timeout | yes | 16/16 | 3/3 | 0/5 | `gemma-4-31b-think-20261014T191647Z` | card sampling, 81,920 tokens |
| Together | Qwen3.5-9B | yes | yes (3) | yes (16) | no: E06 | 0/17 | 0/2 | 0/5 | `together-qwen3.5-9b-20261014T185700Z` | re-test under the tightened rules |
| Together | DeepSeek V4.1 Flash | yes | yes (3) | yes (16) | yes | 0/19 | 0/3 | 1/5 | `together-deepseek-v4.1-flash-20261014T173556Z` | forced comparison |
| Together | Kimi K3 | yes | yes (3) | no (1) | no: E06 | 0/19 | 0/3 | 5/5 | `together-kimi-k3-20261014T134950Z` | prompt-side conditions only |
| Together | GLM-5.3, thinking | yes | yes (3) | yes (5) | yes | 1/19 | 3/3 | 0/5 | `together-glm-5.3-think-20261014T173600Z` | prompt-side conditions only |
| Together | GLM-5.3 | no | yes (3) | no (None) | yes | 2/19 | 3/3 | 0/5 | `together-glm-5.3-20261014T134943Z` | out: thinking not reliably off |
| Together | DeepSeek V4 Pro | no | yes (38) | yes (16) | yes | 0/19 | 3/3 | 0/5 | `together-deepseek-v4-pro-20261014T135156Z` | out |
| Together | DeepSeek V4 Pro, thinking | no | HTTP 429 | no (0) | yes | 0/18 | 2/2 | 1/5 | `together-deepseek-v4-pro-think-20261014T173602Z` | out |
| Together | Llama 3.3 70B | no | yes (3) | yes (5) | yes | 0/18 | 0/3 | 5/5 | `together-llama-3.3-70b-20261014T135410Z` | fallback, not used |
| Together | Muse Glimmer 30B | no | no (None) | no (None) | no: E05, E06 | 4/19 | 0/3 | 5/5 | `together-muse-glimmer-30b-20261014T173554Z` | out |
| Together | gpt-oss-120b | no | no (1) | yes (5) | yes | 19/19 | 3/3 | 0/5 | `together-gpt-oss-120b-20261014T173558Z` | out |
| Together | Qwen3.5-9B, thinking | no | HTTP 503 | no (0) | no: E05, E06 | 17/17 | 1/1 | 0/5 | `together-qwen3.5-9b-think-20261014T173604Z` | out |

Not tested: Qwen3.5-397B, Gemma 4 31B and Nemotron 3 Ultra on Together answer HTTP 400 (not serverless; `runs/enforce/together-*-20261014T1354*Z`).
