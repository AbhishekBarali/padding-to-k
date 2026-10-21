# Full study: projected hosted cost and GPU time

Written by `python analysis/full_study_estimate.py`. Every number below comes from the cost test of
18 Oct (`runs/costtest_2026-10-18_*`), the pilot runs of 15 Oct (branch `pilot-runs`) and the prices in
`configs/models.yaml` (read from aws.amazon.com/bedrock/pricing and docs.together.ai on 18 Oct). The
queue that runs it all is `harness/full_study_queue.py`.

## Bedrock (credits, cap 300 USD; a model is dropped only if the total passes 280 USD)

Full run per model: 22,320 sends (the five prompt-side conditions and min_k_shown_fewer_ok on all 558 documents) plus the 300-prompt repeat check. Flex tier on every model (one request each on 18 Oct came back with `service_tier: flex`, and so did all 50 of each cost test); DeepSeek v3.2 is counted at the Standard price because the pricing page lists no Flex price for it. gpt-oss reports no reasoning count: its reasoning is the <reasoning> block at the start of the content, billed in its completion tokens.

| Model | Test replies | Prompt tokens / request | Completion tokens / request | of which reasoning | Price in / out (USD per M) | Tier | Projected USD | --max-usd (full + repeat) |
|---|---|---|---|---|---|---|---|---|
| bedrock-kimi-k3 | 50 | 536 | 64 | 0 | 1.65 / 8.25 | flex | 32.01 | 64 + 1 |
| bedrock-deepseek-v3.2 | 50 | 534 | 76 | 0 | 0.62 / 1.85 | standard | 10.68 | 22 + 0.5 |
| bedrock-qwen3-235b | 50 | 535 | 71 | 0 | 0.11 / 0.44 | flex | 2.04 | 5 + 0.5 |
| bedrock-mistral-large-3 | 50 | 542 | 84 | 0 | 0.25 / 0.75 | flex | 4.49 | 9 + 0.5 |
| bedrock-ministral-3-14b | 50 | 542 | 115 | 0 | 0.1 / 0.1 | flex | 1.49 | 3 + 0.5 |
| bedrock-gpt-oss-20b | 50 | 585 | 206 | 0 | 0.035 / 0.15 | flex | 1.16 | 3 + 0.5 |
| bedrock-gpt-oss-120b | 50 | 585 | 216 | 0 | 0.075 / 0.3 | flex | 2.46 | 5 + 0.5 |
| bedrock-kimi-k3-think (pilot documents) | 50 | 603 | 1690 | 1607 | 1.65 / 8.25 | flex | 35.86 | 72 |
| bedrock-kimi-k3, re-ask arm (about 383 replies) | 50 | | | | | flex | 0.58 | 1.5 |
| bedrock-ministral-3-14b, re-ask arm (about 287 replies) | 50 | | | | | flex | 0.02 | 0.5 |

Seven models, full run and repeat check: **54.32 USD**. Kimi K3 with thinking on would cost 337.94 USD on every prompt-side request (392.86 USD in all, past 280), so it runs on the pilot documents: 35.86 USD. With the re-ask arm (0.60 USD): **Bedrock total 90.78 USD** of the 300 USD cap, plus 0.88 USD already spent on the cost test. No model is dropped.

Caps: each job stops at about twice its projection; the caps add up to 189.00 USD, so with the 0.88 USD spent even every job running to its cap stays under 300 USD. The test used only none and min_k_shown; the five prose wordings ask for the same lists, so their replies should be of the same length, and a 1.5x margin on every row would still keep the total at 136 USD.

## Together (cash, 50 USD in total, 3.64 USD spent by the pilot)

Full run per model: 25,668 sends (every condition, min_k_enforced and min_k_escape included: both models force the count in the 14 Oct engine test) plus the repeat check.

| Model | Prompt / completion tokens per request (pilot) | Price in / out | Projected USD | --max-usd (full + repeat) |
|---|---|---|---|---|
| together-deepseek-v4.1-flash | 539 / 67 (`2026-10-15_together-deepseek-v4.1-flash_pilot`) | 0.3 / 1.2 | 6.29 | 13 + 0.5 |
| together-qwen3.5-9b | 582 / 60 (`2026-10-15_together-qwen3.5-9b_pilot`) | 0.17 / 0.25 | 2.96 | 6 + 0.5 |

Together total 9.25 USD; with the pilot's 3.64 USD, **12.89 USD of 50**. Caps add up to 20.00 USD (23.64 with the pilot).

## GPU queue (one RTX PRO 6000)

| Job | Model | Sends | Requests / s | Hours | Hours if half as fast | Rate from |
|---|---|---|---|---|---|---|
| full grid + repeat check | qwen3.5-0.8b | 25,968 | 20 | 0.36 | 0.72 | scaled: taken as qwen3.5-9b (its own engine-test speed is 4x; the harness, not the GPU, is the limit there) |
| full grid + repeat check | qwen3.5-2b | 25,968 | 20 | 0.36 | 0.72 | scaled: as qwen3.5-0.8b |
| full grid + repeat check | qwen3.5-9b | 25,968 | 20 | 0.36 | 0.72 | measured: 2026-10-15_qwen3.5-9b_robustness, 840 in 0.7 min |
| full grid + repeat check | qwen3.5-27b | 25,968 | 6.3 | 1.14 | 2.29 | scaled: 23 / 73 of qwen3.5-9b (engine test) |
| full grid + repeat check | gemma-4-31b | 25,968 | 3.4 | 2.12 | 4.24 | measured: 2026-10-15_gemma-4-31b_robustness, 840 in 4.1 min |
| full grid + repeat check | olmo-3.1-32b | 25,968 | 3.4 | 2.12 | 4.24 | scaled: same engine-test speed as gemma-4-31b (10 tokens/s) |
| full grid + repeat check | ministral-3-14b | 25,968 | 6.1 | 1.18 | 2.37 | measured: 2026-10-15_ministral-3-14b_robustness, 840 in 2.3 min |
| full grid + repeat check | gpt-oss-20b | 25,968 | 10.8 | 0.67 | 1.34 | scaled: 135 / 73 of qwen3.5-9b, times 60 / 206 for its longer replies |
| dev set | qwen3.5-0.8b | 2,184 | 20 | 0.03 | 0.06 | scaled: taken as qwen3.5-9b (its own engine-test speed is 4x; the harness, not the GPU, is the limit there) |
| dev set | qwen3.5-2b | 2,184 | 20 | 0.03 | 0.06 | scaled: as qwen3.5-0.8b |
| dev set | qwen3.5-27b | 2,184 | 6.3 | 0.10 | 0.19 | scaled: 23 / 73 of qwen3.5-9b (engine test) |
| dev set | olmo-3.1-32b | 2,184 | 3.4 | 0.18 | 0.36 | scaled: same engine-test speed as gemma-4-31b (10 tokens/s) |
| dev set | gpt-oss-20b | 2,184 | 10.8 | 0.06 | 0.11 | scaled: 135 / 73 of qwen3.5-9b, times 60 / 206 for its longer replies |
| thinking pair, all documents, 3 seeds | qwen3.5-9b-think | 11,718 | 0.387 | 8.41 | 16.82 | measured: 2026-10-15_qwen3.5-9b-think_pilot_s1, 420 in about 18 min |
| thinking pair, all documents, 3 seeds | qwen3.5-9b-nothink | 11,718 | 17.5 | 0.19 | 0.37 | measured: 2026-10-15_qwen3.5-9b-nothink_pilot_s1, 420 in 0.4 min |
| thinking pair, pilot documents, 3 seeds | qwen3.5-9b-think-pp0 | 1,260 | 0.387 | 0.90 | 1.81 | taken as qwen3.5-9b-think (not measured; without the penalty it may think longer) |
| thinking pair, pilot documents, 3 seeds | qwen3.5-9b-nothink-pp0 | 1,260 | 17.5 | 0.02 | 0.04 | taken as qwen3.5-9b-nothink |
| thinking pair, all documents, 1 seed | gemma-4-31b-think | 3,906 | 0.0775 | 14.00 | 28.00 | measured: 2026-10-15_gemma-4-31b-think_pilot_s1, 420 in 90.3 min |
| thinking pair, all documents, 1 seed | gemma-4-31b-sampled | 3,906 | 3 | 0.36 | 0.72 | measured: 2026-10-15_gemma-4-31b-sampled_pilot_s1, 420 in 2.4 min |

Generation 32.6 h (slow column 65.2 h), server start-ups 1.6 h (22 starts at their measured seconds_to_healthy), and about 1 h for the re-ask arm and restarts. The teacher-forced pass is not in the queue (it runs with the mechanism figure).

**GPU total: about 35 hours (68 if every rate is half as fast).** The thinking-on arms are most of it: Gemma 4 31B thinking 14.0 h, Qwen3.5-9B thinking 8.4 h for its three seeds. Its presence-penalty-0 rerun runs on the pilot documents only, so it adds about 1 h, but it may think longer without the penalty, so that row is the least certain.
