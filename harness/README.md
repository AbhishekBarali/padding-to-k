# harness: running models on the frozen data

The why and the order of work are in `../PLAN/RUN-PLAN.md`. This page is only the commands.

| File | What it does |
|---|---|
| `../configs/models.yaml` | Every model: pinned revision, role (pilot, main, reserve, Bedrock), thinking setting, vLLM flags |
| `serve.py` | Starts the pinned vLLM Docker server for one model and records how it ran (`runs/servers/`) |
| `enforce_test.py` | About 20 requests that prove minItems / maxItems really reach the model on this engine |
| `bedrock_probe.py` | Settles Bedrock's undocumented points for one model (maxItems, schema in prompt, repeats) |
| `retry_arm.py` | Plans the re-ask arm: short min_k_shown replies sent back once with a validation error |
| `full_study_queue.py` | The full study as one ordered queue (`list`, `run --section gpu/together/bedrock`) |
| `run.py` | `plan` a run (expected count, shuffled order), `go` (append-only, resumable), `status` |
| `score_counts.py` | The count outcome (no matcher needed), the pilot stop rules, the dose contrast |
| `repeat_check.py` | Same prompts sent twice: identical share and over-count flips |
| `stop_rule_sim.py` | How the stop rule behaves, by simulation (for the preregistration) |
| `telemetry.sh` | GPU log every 5 seconds during a run |
| `common.py` | Shared: prompt rendering through `data/build.py`, parse ladder, placeholder and duplicate rules |
| `tests/test_common.py` | Tests for the parse and count rules; add your own hard cases at the bottom |

## Setup on the GPU machine

```bash
git clone <repo> pad-to-k && cd pad-to-k
python3 -m venv .venv && . .venv/bin/activate
pip install -r data/requirements.txt -r harness/requirements.txt
(cd data && python build.py && python build.py check)    # rebuilds data/local/ (review text), about 1 minute
python harness/tests/test_common.py
docker pull vllm/vllm-openai:v0.31.0
export HF_HOME=/path/with/400GB/free/hf                   # model weights live here
```

## One model, start to finish

```bash
python harness/serve.py up qwen3.5-9b --hf-home "$HF_HOME"          # prints the docker command, waits for /health
python harness/enforce_test.py --model qwen3.5-9b --base-url http://127.0.0.1:8000/v1
#   read runs/enforce/qwen3.5-9b-*/report.md AND raw.jsonl before going on
python harness/run.py plan --model qwen3.5-9b --scope pilot          # writes runs/<date>_qwen3.5-9b_pilot/
harness/telemetry.sh runs/<run_id>/gpu.csv & TPID=$!
python harness/run.py go runs/<run_id> --base-url http://127.0.0.1:8000/v1 --server-info runs/servers/<file>.json
kill $TPID
python harness/run.py status runs/<run_id>                           # expected vs actual
python harness/serve.py down qwen3.5-9b                              # keeps the server log
```

`go` can be stopped and started again at any time; it only sends what has no result yet. A local run
must name its server record (`--server-info`). A wrong key, model id or region (HTTP 401, 403, 404)
stops the run with nothing recorded; ten failed results in a row at the start stop it too (circuit
breaker). Either way, fix the cause and, for the circuit breaker, plan a new run id.

## Side tests

```bash
# thinking side test: two same-weights pairs, each run with request seeds 1, 2 and 3 (vendor sampling in
# models.yaml); thinking replies can take many minutes, so give go a long client timeout
for M in qwen3.5-9b-think qwen3.5-9b-nothink gemma-4-31b-think gemma-4-31b-sampled; do
  python harness/run.py plan --model $M --scope pilot --request-seed 1 --run-id <date>_${M}_pilot_s1    # and 2, 3
done
python harness/run.py go runs/<run_id> --base-url http://127.0.0.1:8000/v1 --server-info <file> --timeout 3600
python harness/run.py plan --model qwen3.5-9b-sampled --scope pilot --request-seed 1 --run-id s1   # and 2, 3
python harness/run.py plan --model qwen3.5-9b --scope dev                     # reserve documents, scorer tuning
python harness/run.py plan --model qwen3.5-9b --repeat-of runs/<full run> --run-id <full run>-repeat
python harness/repeat_check.py runs/<full run> runs/<full run>-repeat
```

Thinking and reasoning runs do not ask for token ids (`teacher_forced.py` does not read them), which keeps
`raw.jsonl` under GitHub's 100 MB file limit at pilot scale; a full-run thinking folder will need splitting.

## Bedrock (prompt-side conditions only)

```bash
export AWS_BEARER_TOKEN_BEDROCK=<Bedrock API key>        # never commit it, never paste it into a file in the repo
python harness/bedrock_probe.py qwen.qwen3-235b-a22b-2507-v1:0 --region us-east-1
python harness/enforce_test.py --model bedrock-qwen3-235b \
    --base-url https://bedrock-runtime.us-east-1.amazonaws.com/openai/v1 --api-key-env AWS_BEARER_TOKEN_BEDROCK
#   E02/E03/E07/E08/E10/E11 are expected to return HTTP 400 on Bedrock (minItems above 1 is not supported)
python harness/run.py plan --model bedrock-qwen3-235b --scope pilot
python harness/run.py go runs/<run_id> --base-url https://bedrock-runtime.us-east-1.amazonaws.com/openai/v1 \
    --api-key-env AWS_BEARER_TOKEN_BEDROCK --workers 16
```

Bedrock models list only the conditions Bedrock can serve (`conditions:` in models.yaml), so their
pilot is 300 sends, not 420 (no enforced cell). Since 18 Oct they all run on the Flex tier
(`extra_body: {service_tier: flex}`); Qwen3 235B is served from us-east-2 (`base_url` in models.yaml), so
leave `--base-url` out for it.

## Spending stop, and the full-study line-up

Every hosted model has a `price` in models.yaml. `go --max-usd N` adds up each reply's cost from its usage
and stops sending once the run has cost N USD (earlier sessions count); the requests not sent stay planned,
and `go` with a higher cap carries on (exit code 3 when it stops). `run.py spend runs/<a> runs/<b> ...`
prints the cost so far of several runs, for a cap shared by several models. The full-study line-up and the
caps are the `full_study` block at the end of models.yaml; `python analysis/full_study_estimate.py` projects
its hosted cost and GPU hours from the cost test (`runs/costtest_2026-10-18_*`) and the pilot, and
`python analysis/full_study_estimate.py check` checks the caps.

```bash
python harness/full_study_queue.py list                       # every job, in order, with its commands
python harness/full_study_queue.py run --section bedrock      # one section; --from N to resume, --dry-run to print
```

## Re-ask arm (Instructor-style, exploratory)

```bash
python harness/retry_arm.py plan runs/<finished run>       # min_k_shown replies with fewer than k entries
python harness/run.py go runs/<finished run>-reask1 ...    # same go options as the run it came from
```

Each short reply goes back once, as a second turn: the model's own reply, then Instructor's JSON-mode
correction ("Correct your JSON ONLY RESPONSE, based on the following errors:") with the error pydantic
raises for a list shorter than its min_length. The replies carry arm `reask1` and `retry_of`. It runs on the
models listed under `retry_arm` in models.yaml (three GPU models, two Bedrock models).

## Together AI (big-model reference)

```bash
set -a; . ~/.padk.env; set +a                             # TOGETHER_API_KEY lives there, never in the repo
python harness/enforce_test.py --model together-kimi-k3 \
    --base-url https://api.together.ai/v1 --api-key-env TOGETHER_API_KEY
#   read the report: E02/E03 decide whether the forced condition counts on Together; raw.jsonl shows
#   whether reasoning really stayed off (no reasoning text, small completion token counts)
python harness/run.py plan --model together-kimi-k3 --scope pilot
python harness/run.py go runs/<run_id> --base-url https://api.together.ai/v1 \
    --api-key-env TOGETHER_API_KEY --workers 4                              # 8 in parallel drew HTTP 429 (14 Oct)
```

Together entries send `max_tokens` (not `max_completion_tokens`) and `reasoning: {enabled: false}`
(`max_tokens_field` and `extra_body` in models.yaml). Before each run, estimate its cost from the
`usage` fields of the last run and the prices in models.yaml; the total budget is about 50 USD.

## Pilot report

```bash
python harness/score_counts.py runs/<pilot run model 1> runs/<model 2> runs/<model 3> --out analysis/pilot
```

## Teacher-forced pass (mechanism figure, RQ7) and its HF check

Reads a finished local run back through the same model without the grammar: at each list boundary, how
likely the model was to close the list; for each entry, the log probability of its own tokens. Writes
`runs/tf_<run_id>_<utc>/` with numbers and offsets only (no text), so review-set outputs are scored too.
It runs inside the pinned vLLM image (it needs the model's tokenizer); details in the script's docstring.

```bash
python harness/serve.py up qwen3.5-9b --hf-home /home/ubuntu/hf --extra=--enable-scale-out --extra=--max-logprobs=1024
IMG=<image_digest from that runs/servers/*.json>
docker run --rm --network host --user "$(id -u):$(id -g)" -v "$PWD":/repo -w /repo -v /home/ubuntu/hf:/hf \
    -e HF_HOME=/hf -e HF_HUB_OFFLINE=1 -e HOME=/tmp --entrypoint python3 "$IMG" \
    harness/teacher_forced.py score --source runs/<run_id> --server-info runs/servers/<that file>.json
python harness/serve.py down qwen3.5-9b
docker run --rm --gpus all --ipc=host --user "$(id -u):$(id -g)" -v "$PWD":/repo -w /repo -v /home/ubuntu/hf:/hf \
    -e HF_HOME=/hf -e HF_HUB_OFFLINE=1 -e HOME=/tmp --entrypoint python3 "$IMG" \
    harness/teacher_forced.py hf-check --scores runs/tf_<run_id>_<utc> --n 200
```

Read `summary.json` first: every line `ok`, `align_max` 0 (the two vLLM outputs agree), every boundary's
token in the class of the model's own choice, and how many outputs were scored on re-tokenized text
(`token_source`). Runs from 15 Oct on keep the generated token ids (`token_ids` in each record), so they are
scored on the exact tokens.

## What never goes into git

`runs/**/raw_restricted.jsonl` (model outputs on the review set quote review text) and `data/local/`.
`.gitignore` already excludes both. Raw outputs of the other sets can be committed gzipped.
