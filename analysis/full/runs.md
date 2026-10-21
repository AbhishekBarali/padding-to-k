# Run folders scored

One row per run folder. Rows = covered request ids (the `none` answer covers k = 1, 3, 5). Missing = transport failures and requests never answered: left out of every pair, never outputs.

| run | kind | model | rows | ok | missing |
|---|---|---|---|---|---|
| fs_bedrock-deepseek-v3.2_full | full | bedrock-deepseek-v3.2 | 23436 | 23436 | 0 |
| fs_bedrock-deepseek-v3.2_full-repeat | repeat | bedrock-deepseek-v3.2 | 300 | 300 | 0 |
| fs_bedrock-gpt-oss-120b_full | full | bedrock-gpt-oss-120b | 23436 | 23436 | 0 |
| fs_bedrock-gpt-oss-120b_full-repeat | repeat | bedrock-gpt-oss-120b | 300 | 300 | 0 |
| fs_bedrock-gpt-oss-20b_full | full | bedrock-gpt-oss-20b | 23436 | 23436 | 0 |
| fs_bedrock-gpt-oss-20b_full-repeat | repeat | bedrock-gpt-oss-20b | 300 | 300 | 0 |
| fs_bedrock-kimi-k3-think_pilot | think | bedrock-kimi-k3-think | 2520 | 2520 | 0 |
| fs_bedrock-kimi-k3_full | full | bedrock-kimi-k3 | 23436 | 23436 | 0 |
| fs_bedrock-kimi-k3_full-reask1 | reask | bedrock-kimi-k3 | 510 | 510 | 0 |
| fs_bedrock-kimi-k3_full-repeat | repeat | bedrock-kimi-k3 | 300 | 300 | 0 |
| fs_bedrock-ministral-3-14b_full | full | bedrock-ministral-3-14b | 23436 | 23436 | 0 |
| fs_bedrock-ministral-3-14b_full-reask1 | reask | bedrock-ministral-3-14b | 410 | 410 | 0 |
| fs_bedrock-ministral-3-14b_full-repeat | repeat | bedrock-ministral-3-14b | 300 | 300 | 0 |
| fs_bedrock-mistral-large-3_full | full | bedrock-mistral-large-3 | 23436 | 23436 | 0 |
| fs_bedrock-mistral-large-3_full-repeat | repeat | bedrock-mistral-large-3 | 300 | 300 | 0 |
| fs_bedrock-qwen3-235b_full | full | bedrock-qwen3-235b | 23436 | 23436 | 0 |
| fs_bedrock-qwen3-235b_full-repeat | repeat | bedrock-qwen3-235b | 300 | 300 | 0 |
| fs_gemma-4-31b-sampled_think-filters_s1 | think | gemma-4-31b-sampled | 4464 | 4464 | 0 |
| fs_gemma-4-31b-think_think-filters_s1 | think | gemma-4-31b-think | 4464 | 4463 | 1 |
| fs_gemma-4-31b_full | full | gemma-4-31b | 26784 | 26784 | 0 |
| fs_gemma-4-31b_full-reask1 | reask | gemma-4-31b | 429 | 429 | 0 |
| fs_gemma-4-31b_full-repeat | repeat | gemma-4-31b | 300 | 300 | 0 |
| fs_gpt-oss-20b_dev | dev | gpt-oss-20b | 2799 | 2799 | 0 |
| fs_gpt-oss-20b_full | full | gpt-oss-20b | 26784 | 26778 | 6 |
| fs_gpt-oss-20b_full-repeat | repeat | gpt-oss-20b | 300 | 300 | 0 |
| fs_ministral-3-14b_full | full | ministral-3-14b | 26784 | 26784 | 0 |
| fs_ministral-3-14b_full-reask1 | reask | ministral-3-14b | 425 | 425 | 0 |
| fs_ministral-3-14b_full-repeat | repeat | ministral-3-14b | 300 | 300 | 0 |
| fs_olmo-3.1-32b_dev | dev | olmo-3.1-32b | 2799 | 2799 | 0 |
| fs_olmo-3.1-32b_full | full | olmo-3.1-32b | 26784 | 26784 | 0 |
| fs_olmo-3.1-32b_full-repeat | repeat | olmo-3.1-32b | 300 | 300 | 0 |
| fs_qwen3.5-0.8b_dev | dev | qwen3.5-0.8b | 2799 | 2799 | 0 |
| fs_qwen3.5-0.8b_full | full | qwen3.5-0.8b | 26784 | 26783 | 1 |
| fs_qwen3.5-0.8b_full-repeat | repeat | qwen3.5-0.8b | 300 | 300 | 0 |
| fs_qwen3.5-27b_dev | dev | qwen3.5-27b | 2799 | 2799 | 0 |
| fs_qwen3.5-27b_full | full | qwen3.5-27b | 26784 | 26784 | 0 |
| fs_qwen3.5-27b_full-repeat | repeat | qwen3.5-27b | 300 | 300 | 0 |
| fs_qwen3.5-2b_dev | dev | qwen3.5-2b | 2799 | 2795 | 4 |
| fs_qwen3.5-2b_full | full | qwen3.5-2b | 26784 | 26781 | 3 |
| fs_qwen3.5-2b_full-repeat | repeat | qwen3.5-2b | 300 | 300 | 0 |
| fs_qwen3.5-9b-nothink-pp0_think-filters_s1 | think | qwen3.5-9b-nothink-pp0 | 480 | 480 | 0 |
| fs_qwen3.5-9b-nothink-pp0_think-filters_s2 | think | qwen3.5-9b-nothink-pp0 | 480 | 480 | 0 |
| fs_qwen3.5-9b-nothink-pp0_think-filters_s3 | think | qwen3.5-9b-nothink-pp0 | 480 | 480 | 0 |
| fs_qwen3.5-9b-nothink_think-filters_s1 | think | qwen3.5-9b-nothink | 4464 | 4464 | 0 |
| fs_qwen3.5-9b-nothink_think-filters_s2 | think | qwen3.5-9b-nothink | 4464 | 4464 | 0 |
| fs_qwen3.5-9b-nothink_think-filters_s3 | think | qwen3.5-9b-nothink | 4464 | 4464 | 0 |
| fs_qwen3.5-9b-think-pp0_think-filters_s1 | think | qwen3.5-9b-think-pp0 | 480 | 480 | 0 |
| fs_qwen3.5-9b-think-pp0_think-filters_s2 | think | qwen3.5-9b-think-pp0 | 480 | 480 | 0 |
| fs_qwen3.5-9b-think-pp0_think-filters_s3 | think | qwen3.5-9b-think-pp0 | 480 | 480 | 0 |
| fs_qwen3.5-9b-think_think-filters_s1 | think | qwen3.5-9b-think | 4464 | 4464 | 0 |
| fs_qwen3.5-9b-think_think-filters_s2 | think | qwen3.5-9b-think | 4464 | 4464 | 0 |
| fs_qwen3.5-9b-think_think-filters_s3 | think | qwen3.5-9b-think | 4464 | 4464 | 0 |
| fs_qwen3.5-9b_full | full | qwen3.5-9b | 26784 | 26784 | 0 |
| fs_qwen3.5-9b_full-reask1 | reask | qwen3.5-9b | 678 | 678 | 0 |
| fs_qwen3.5-9b_full-repeat | repeat | qwen3.5-9b | 300 | 300 | 0 |
| fs_together-deepseek-v4.1-flash_full | full | together-deepseek-v4.1-flash | 26784 | 26784 | 0 |
| fs_together-deepseek-v4.1-flash_full-repeat | repeat | together-deepseek-v4.1-flash | 300 | 300 | 0 |
| fs_together-qwen3.5-9b_full | full | together-qwen3.5-9b | 26784 | 26784 | 0 |
| fs_together-qwen3.5-9b_full-repeat | repeat | together-qwen3.5-9b | 300 | 300 | 0 |

Thinking-pair runs not present yet: none
