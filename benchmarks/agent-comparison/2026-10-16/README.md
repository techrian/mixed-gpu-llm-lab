# Local assistant agent comparison — 2026-10-16

| Metric | Qwen Q4_K_M / Strata 0.1.43.1 | GLM Maya-M / Project Maya 1.1.11 |
| --- | ---: | ---: |
| Complete success | 69/72 · 95.8% | 69/72 · 95.8% |
| Role-weighted success | 96.7% | 95.8% |
| Tasks passed all three times | 21/24 | 22/24 |
| Successful completions/hour | 161.6 | 141.3 |
| Successful median / p95 | 20.25 / 42.38 s | 21.19 / 48.59 s |

**67 common successful episodes:** Qwen/GLM geometric mean time ratio 0.870, paired task-cluster bootstrap 95% interval [0.806, 0.943].
The weighted success difference is +0.83 percentage points for Qwen, interval [−0.83, +3.33] points. A quality winner is not established.

[Excel workbook](AgentBenchmark_Qwen38_vs_GLM53.xlsx) · [statistics](summary_stats.json) · [per-episode results](results.jsonl) · [task definitions](task-manifest.json) · [all traces and artifacts](runs)

## Purpose and workload

Measure whether a local assistant actually completes requested actions in an environment already prepared for it.
The focus is day-to-day agent work, with a small maintenance component. The suite is inspired by BFCL, tau-bench and Terminal-Bench;
it is not an official run of those benchmarks. Hermes-style native tool use is evaluated in a controlled loop; the Hermes application itself is not invoked.

| Category | Weight | Four tasks |
| --- | ---: | --- |
| Tool contracts | 15% | exact reminder, independent status calls, dependent routing, avoiding irrelevant tools |
| Business workflows | 25% | partial refund, timezone/calendar scheduling, bounded purchasing, pagination and deduplication |
| Files and evidence | 20% | CSV reconciliation, SQLite export, current-source quotation, scoped configuration edit |
| Recovery and verification | 20% | timeout after commit, concurrent version conflict, intact backup selection, service repair and restart |
| Context and instruction | 15% | retrieved-instruction injection, necessary clarification, long approved-setting handoff, long shipping history |
| Small maintenance | 5% | Python timezone fix, JavaScript stable deduplication, existing CLI operation, retry policy fix |

Three independent conversations per task, each reset to the same initial fixture. The same shuffled task/repetition order is used for both systems.
Business APIs are deterministic local state machines. Files, SQLite and Python/Node execution are real; terminal actions run in a Docker container
with no network, a read-only root, no capabilities, 512 MiB memory, two CPUs and only the task workspace mounted.
The image runs tools as UID/GID 1000; workspaces must be writable by that identity.

The common budget is **12 LLM turns, 4096 completion tokens per turn, 180 seconds per episode**. Server defaults are temperature 1.0,
top_p 0.95, top_k 20 and min_p 0.0; no generation seed is fixed. An early unique session tag prevents reuse of a prior task's full prompt.
Within-episode prefix reuse is allowed. Native model reasoning and deployment optimizations are retained; effective reasoning settings are detailed below.

## Reasoning settings and token limits

Both models had thinking enabled. The [executed request builder](snapshots/executed-runner.py.txt) sent `max_tokens: 4096` and `tool_choice: auto`
without `reasoning_effort`, a thinking override or a reasoning-token budget. Server and model-template defaults therefore applied:

- **Qwen: `xhigh`.** The [recorded configuration](snapshots/qwen-benchmark-config.json) omits `reasoning_effort` and `reasoning_budget_tokens`.
  The loaded pack's `tokenizer/chat_template.jinja` resolves an omitted effort with `reasoning_effort|default('xhigh')`, its highest supported level.
  There was no separate reasoning-token cap; reasoning shared the request's 4096-token generation limit with answer text and tool calls.
- **GLM: `high`.** The [recorded configuration](snapshots/glm-benchmark-config.json) sets `reasoning_effort: high`, also confirmed by the
  [saved health response](snapshots/glm-health.json). GLM supports `low`, `high` and `max`; this benchmark did not use `max`.
  The pinned Maya server defaults `thinking_budget` to 32768 tokens, then clamps it to leave a quarter of `max_tokens`, with a 1024-token reserve floor,
  for the answer. With `max_tokens: 4096`, the effective reasoning cap was `min(32768, 4096 - 1024) = 3072` tokens.

### Audit of all recorded requests

The table below aggregates every `trace` entry in `runs/{qwen,glm}/*/trajectory.json`, excluding the unscored warm-up.
Completion counts come from `response.usage.completion_tokens`; output-limit endings come from `response.finish_reason == "length"`.

| Observation | Qwen | GLM |
| --- | ---: | ---: |
| Measured episodes | 72 | 72 |
| Measured LLM requests | 400 | 336 |
| Largest total completion per request | 1435 tokens | 772 tokens |
| Requests with 3072 or more total completion tokens | 0 | 0 |
| Requests ending at the output-token limit | 0 | 0 |

These are total generated tokens, including reasoning, answer text and native tool calls. They do not measure reasoning tokens separately.
The largest completions are Qwen [D01-r2, turn 7](runs/qwen/D01-r2/trajectory.json) and GLM [D01-r1, turn 3](runs/glm/D01-r1/trajectory.json).
All recorded requests ended with `tool_calls` or `stop`.

**GLM never reached its 3072-token reasoning cap:** its largest total completion was only 772 tokens.
The records provide no evidence that this cap cut its reasoning short or caused its failures in this suite. A cap could matter on a workload that reaches it.

Reasoning effort remains a separate comparison variable. Qwen `xhigh` and GLM `high` are model-specific instructions, not a common measure of reasoning work.
Raising GLM to `max` could change reasoning, success and completion time; that effect was not measured.
The published results compare the recorded deployments. Comparing both at their highest reasoning settings would require a separate run with sufficient,
matching generation and reasoning budgets; equal token allowances would still not imply equal computation across models.

## Timing and success

Wall time runs from the first model request to the final answer, API error or budget stop. It includes reasoning, native tool generation,
tool execution and retries. Fixture preparation, model loading and deterministic hidden grading are excluded. Each model receives an unscored tool warm-up.
GLM ran first, then Qwen, with no concurrent model evaluation; model order was not counterbalanced.

Strict success requires every task-specific final-state and protected-state check, required verification, and a nonempty final response.
Native call schema validity measures names, JSON and declared types; final-state checks separately enforce semantic correctness.
Tool error counts include intentional timeout/version faults and failed visible commands, so inspect their context.

Successful completions/hour = successes × 3600 / wall time of **all** attempts. Successful-only medians and p95 are also shown.
Matched speed uses only the same task/repetition pairs both systems passed. Quality and speed intervals use 10000 stratified paired task-cluster resamples;
each task keeps its three repetitions together. Small authored workloads limit generalization.

## Failures, ambiguity and grading audit

- Qwen: T02-r1 returned fenced JSON; D03-r1 created 100 quotations; M04-r3 passed its code/state checks but the final API content was empty.
- GLM: T02-r1 and T02-r3 returned extra formatting/prose; D03-r3 created 100 quotations.
- D03's Korean wording `100개 견적` admits an alternate scope interpretation. The frozen target is a single quotation for quantity 100.
  The workbook flags this ambiguity. Excluding D03, both score 67/69 (97.1%).

### Paired outcomes where only one model succeeded

Pairing the same task and repetition gives **67 pairs where both passed, 2 where only Qwen passed, 2 where only GLM passed,
and 1 where both failed**. The four pairs with different verdicts involve three task types; D03 appears in both directions on different repetitions.

| Episode | Qwen | GLM | Complete request/response traces |
| --- | --- | --- | --- |
| T02-r3 | Pass: returned only the required JSON object | Fail: correct JSON values wrapped in a Markdown code fence | [Qwen](runs/qwen/T02-r3/trajectory.json) · [GLM](runs/glm/T02-r3/trajectory.json) |
| D03-r3 | Pass: one quote for 100 units, USD 1350 | Fail: 100 quote objects for quantities 1–100 | [Qwen](runs/qwen/D03-r3/trajectory.json) · [GLM](runs/glm/D03-r3/trajectory.json) |
| D03-r1 | Fail: 100 quote objects for quantities 1–100 | Pass: one quote for 100 units, USD 1350 | [Qwen](runs/qwen/D03-r1/trajectory.json) · [GLM](runs/glm/D03-r1/trajectory.json) |
| M04-r3 | Fail: code and verification checks passed; final API content was empty | Pass: code, verification and final response passed | [Qwen](runs/qwen/M04-r3/trajectory.json) · [GLM](runs/glm/M04-r3/trajectory.json) |

**T02 — exact output format.** The request was to query `api`, `billing` and `worker`, then return exactly a JSON object with
`unhealthy` and `healthy_count`. Both models queried all three services and obtained the correct values. In repetition 3,
Qwen returned `{"unhealthy": ["billing"], "healthy_count": 2}` directly; GLM surrounded the same object with a Markdown code fence.
That failed the explicit JSON-only contract. In repetition 1, [Qwen](runs/qwen/T02-r1/trajectory.json) and
[GLM](runs/glm/T02-r1/trajectory.json) both used code fences, accounting for the one pair both failed.

**D03 — ambiguous quote quantity.** The task required reading the current price list and discount policy, preserving the source files,
and writing `quote.json` with the required fields and source paths. The frozen target was a single object: unit price USD 15,
quantity 100, discount 10%, total USD 1350. The Korean phrase `100개 견적` also permits the interpretation "100 quotes".
Qwen took that interpretation in repetition 1; GLM did so in repetition 3. Both generated arrays of 100 quotes for quantities 1–100,
using the current USD 15 price and quantity-based discount rule. The saved checks rejected the array where they expected one quote object.
The source-field check also expected an object and failed on the array; that verdict alone does not establish that a model failed to read the sources.
This ambiguity limits capability comparisons from this item; the D03-excluded result remains 67/69 (97.1%) for both models.

**M04 — successful code change with missing completion report.** The contract was to preserve the retry function's interface,
allow only case-insensitive GET/HEAD requests with status 429 or 503 while `attempt < 3`, run the visible tests and verify edge cases.
In repetition 3, both models passed the hidden behavior checks, actually ran the visible tests, and preserved tests and unrelated files.
Qwen's final API `content` was empty, so it failed the required nonempty completion response. GLM also returned a completion report and passed all checks.
The empty response's cause was not diagnosed; this episode's failed condition is completion reporting, with the code checks recorded as passed.

These cases document output-contract adherence, interpretation of an ambiguous request and end-of-task reporting in the measured deployments.
They do not isolate the effects of base-model architecture, quantization, reasoning effort or serving behavior.

### Grading audit

The original graders rejected some equivalent representations. All 144 saved episodes were audited symmetrically without new inference or timing changes:
equivalent absolute/relative workspace paths, complete authoritative mutation responses where a separate reread was not requested,
financial decimal strings when no JSON numeric type was required, and required fields with additional metadata when extra keys were not forbidden.
Explicit exclusive-key/type contracts remain strict. See [correction rules](grader-correction.json), [changed verdicts](grading-audit.json),
and each episode's `result-original.json` alongside `result.json`.

All 24 known-correct oracle trajectories pass and all 24 unexecuted negatives fail. Partial pilot attempts used to find harness defects are excluded.
The numerical results are the final audited verdicts, not a best-of-three score. The task inputs and expected numerical/state outcomes were held fixed.

## Reproduce the report from saved evidence

From this directory, create a virtual environment and install [requirements.txt](requirements.txt), then:

```bash
python report.py
```

This recalculates statistics and writes the Excel workbook without calling a model. Workbook trajectory links work after cloning or extracting the full evidence directory.
The workbook has Summary, Runs, LLMRequests, ToolCalls, Checks, FailureReview, Categories, TaskResults, PairedRuns, Tasks, Protocol, Configurations, Sources and Statistics sheets.
The blue category weights are editable; changing them recalculates the weighted score, while bootstrap intervals and written interpretation retain the original protocol weights.

For an independent outcome audit with Docker available:

```bash
docker build -t local-agent-bench:20261016 container
python validate_suite.py
python regrade.py
python report.py
```

`regrade.py` checks that the task definitions equal the frozen manifest. Hidden code checks execute outside the model-visible workspace.
Do not edit recorded task artifacts when auditing; use a copy if you want to experiment.

## Run fresh inference

Apply one of the recorded model profiles and start its API yourself. Keep other clients idle. The public adapter uses the same streamed native-call loop,
tool schemas, unique tags, budgets and repetition order; it targets an already running server and leaves service management to the operator.
The final audited grader is used from the start. The original service orchestration is retained as [archival source](snapshots/executed-runner.py.txt).

```bash
# GLM running with its recorded defaults and configuration:
python runner.py --model glm --url http://127.0.0.1:8080 --output ../../new-runs/agent-comparison
# Stop GLM, start Qwen with its recorded configuration, then:
python runner.py --model qwen --url http://127.0.0.1:8080 --output ../../new-runs/agent-comparison
```

This writes new results outside the frozen evidence. Record new engine commits, configurations, runtime placement and host conditions alongside them.
It does not automatically apply the old deployment metadata to a new run. The adapter has not been used for an additional 144-episode inference run during publication.
Task prompts retain their original Korean/English text and fixed evaluation date so a translated task is not silently substituted.

## Publication and limits

Private home paths and bind addresses are replaced by examples. Run paths are relative. Task artifacts are copied byte for byte; numerical metrics and verdicts are unchanged.
Recorded source/config hashes refer to the original local files. [publication-manifest.json](publication-manifest.json) records the exported files and their hashes.
Model weights, prepared packs, engine binaries and virtual environments are excluded.

This evaluates the two quantized deployment stacks, including different KV, prefill and MTP behavior. It does not isolate architecture or quantization quality.
Open-ended final prose is not independently judged. The suite exposes 3–8 tools/task; it does not test production-sized tool discovery, actual Hermes memory/skills,
real accounts, browser/GUI actions, vision, voice, delegation, maximum 262K-context saturation or long-term unattended operation.
One retrieval-injection case is not a broad security rating.

See [model configurations](../../../models), [hardware](../../../docs/hardware.md) and [primary methodology sources](metadata.json).
