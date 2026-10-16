# Mixed GPU LLM Lab

## Measured agent results — October 16, 2026

**24 tasks × 3 repetitions × 2 deployed systems = 144 measured episodes**, on the same RTX 3090 + RTX 3060 + dual V100 PC.

| Metric | Qwen3.8 Flash Next Uncensored Q4_K_M | GLM5.3 Flash Maya-M |
| --- | ---: | ---: |
| Complete task success | **69/72 · 95.8%** | **69/72 · 95.8%** |
| Assistant-role weighted score | 96.7% | 95.8% |
| Tasks passed in all three repetitions | 21/24 | **22/24** |
| Successful completions/hour, failed time included | **161.6** | 141.3 |
| Successful-episode median | **20.25 s** | 21.19 s |
| Successful-episode p95 | **42.38 s** | 48.59 s |
| Native tool argument/schema validity | 98.0% · 399/407 | **99.1% · 325/328** |
| Mean tool calls per episode | 5.65 | **4.56** |

**On the 67 matched episodes both systems completed successfully, Qwen's geometric mean completion time was 13.0% shorter.**
The Qwen/GLM time ratio was **0.870**, with a paired task-cluster bootstrap 95% interval of **0.806–0.943**.

[**Excel workbook — 14 sheets**](benchmarks/agent-comparison/2026-10-16/AgentBenchmark_Qwen38_vs_GLM53.xlsx) ·
[Method, categories and failures](benchmarks/agent-comparison/2026-10-16/README.md) ·
[Machine-readable statistics](benchmarks/agent-comparison/2026-10-16/summary_stats.json) ·
[Complete execution records](benchmarks/agent-comparison/2026-10-16/runs)

## What the results show

- **Overall completion accuracy was equal in this suite.** The role-weighted point estimate favored Qwen by 0.83 percentage points, but its 95% interval was −0.83 to +3.33 points. This workload does not establish a quality winner.
- **Qwen completed the matched successful work sooner.** Useful throughput was 14.4% higher when time spent on failures was included. These are full task times: reasoning, tool calls, tool execution, retries and the final response.
- **GLM used fewer tool calls and produced valid tool arguments more consistently.** It also passed all three repetitions on one more task. Extra calls can include legitimate verification, recovery or redundant work; the complete traces show which occurred.
- **Workload matters.** In the context/instruction category, mean episode times were 22.8 s for Qwen and 41.0 s for GLM. GLM had lower mean times in files/evidence and small maintenance work. Category-level results are below and in the workbook.

These observations describe two actual deployment stacks, including different quantizations, prefill sizes, KV residency and MTP implementations.
They do not isolate base-model intelligence or establish a universal ranking. Use the task definitions, failures, settings and traces to decide which tradeoffs fit your work.

### Reasoning settings and observed token use

**Both models had thinking enabled. Qwen used its chat template's default `xhigh`; GLM used the configured `high`.**
The benchmark requests omitted reasoning-effort overrides. Qwen's highest template level is `xhigh`; GLM also offers `max`, which was not measured here.
These level names are specific to each model and do not imply equal reasoning work.

| Setting or observation | Qwen | GLM |
| --- | ---: | ---: |
| Effective reasoning effort | `xhigh`, template default | `high`, server default |
| Total generation limit per request | 4096 tokens | 4096 tokens |
| Separate reasoning-token cap | None within the total generation limit | 3072 tokens, leaving 1024 for the answer |
| Measured LLM requests across 72 episodes | 400 | 336 |
| Largest total completion in one request | 1435 tokens | 772 tokens |
| Requests ending at the output-token limit | 0 | 0 |

Completion counts include reasoning, answer text and generated tool calls; they are not reasoning-only counts.
**GLM's reasoning cap was never reached:** even its largest total completion, 772 tokens, was below the 3072-token reasoning cap.
The saved records therefore provide no evidence that this cap cut GLM's reasoning short in this suite.

The comparison retains each deployment's reasoning settings. The effect of raising GLM from `high` to `max` on success and completion time remains unmeasured.
A comparison of both models at their highest reasoning settings would require a separate run with sufficient, matching generation and reasoning budgets.
See the [reasoning audit and evidence](benchmarks/agent-comparison/2026-10-16/README.md#reasoning-settings-and-token-limits) for the budget calculation and request records.

### Category results

Each category contains four tasks, repeated three times per system. Times include all attempts.

| Category | Role weight | Qwen passes | GLM passes | Qwen mean time | GLM mean time |
| --- | ---: | ---: | ---: | ---: | ---: |
| Tool contracts | 15% | 11/12 | 10/12 | 9.23 s | 10.70 s |
| Business workflows | 25% | 12/12 | 12/12 | 22.68 s | 26.43 s |
| Files and evidence | 20% | 11/12 | 11/12 | 29.47 s | 25.74 s |
| Recovery and verification | 20% | 12/12 | 12/12 | 19.03 s | 21.41 s |
| Context and instruction | 15% | 12/12 | 12/12 | 22.82 s | 41.03 s |
| Small maintenance tasks | 5% | 11/12 | 12/12 | 24.87 s | 21.18 s |

### Scope and limitations

This is a **custom, controlled OpenAI-native agent loop inspired by Hermes-style use**. The live Hermes gateway, persistent memory and skills were not run.
Business APIs and knowledge pages are deterministic fixtures; files, SQLite and Python/Node execution are real isolated tasks.
Each task exposes 3–8 tools and has a 180-second, 12-turn budget. There is no commercial LLM judge.

The Korean wording of one quote task (D03) admits two interpretations. The frozen target is one quote for 100 units; both models produced a 100-quote list in one repetition.
Excluding that item, both systems scored **67/69 · 97.1%**. The workbook reports this sensitivity separately.
Other strict failures were bare-JSON formatting (Qwen once, GLM twice) and an empty final API response after correct code changes (Qwen once).
All 144 saved episodes were audited with the same final grader; [grading corrections and original verdicts](benchmarks/agent-comparison/2026-10-16/grading-audit.json) are retained.

Three repeats of 24 authored tasks are a limited sample. Image understanding, real accounts, browser/GUI work, a production-sized tool catalog, maximum-context saturation and long unattended operation were not evaluated.
GLM ran before Qwen on one host; model order was not counterbalanced. These are not official BFCL, tau-bench, Terminal-Bench or Hermes leaderboard scores.

## Recorded deployments

| Setting | Qwen profile | GLM profile |
| --- | --- | --- |
| Model | OrcaRouter Qwen3.8 Flash Next Uncensored, Q4_K_M | Peasant Smith GLM5.3 Flash Maya-M, mixed quantization with IQ2_S experts |
| Engine | [Niko1221/Strata](https://github.com/Niko1221/Strata), 0.1.43.1, `a0116b2` | [mw00/project-maya](https://github.com/mw00/project-maya), 1.1.11, `362671a` |
| Context ceiling | 262144 | 262144 |
| Prefill chunk | 6144 | 2048 |
| KV | FP16, GPU-resident configuration | FP16, streaming with 32768 resident positions |
| GPU order, physical indices | `[2,0,1,3]` | `[2,0,1,3]` |
| Base-layer ranges, half-open | `[0,16) / [16,29) / [29,33) / [33,48)` | `[0,16) / [16,27) / [27,31) / [31,45)` observed auto split |
| Experts | All 24576 cache slots; prefill borrows slots with RAM backing | 10102 VRAM slots including slack; remaining experts in pinned RAM, disk eviction off |
| MTP | Qwen native draft, `--spec 4 --spec-min-p 0.5` | GLM MTP, enabled |
| Reasoning effort | `xhigh`, chat-template default | `high`, configured server default |
| Vision | F16 encoder on physical GPU 2 | F16 encoder on physical GPU 2 |
| Process swap | `MemorySwapMax=0` | `MemorySwapMax=0` |

Both used API defaults temperature 1.0, top_p 0.95, top_k 20 and min_p 0.0. Reasoning settings and observed token use are detailed above.
Vision was loaded during measurement, but the agent tasks were text-only. MTP ran on the last V100 in both recorded layouts.

## Configuration and reproduction

- [Qwen settings, build and restoration](models/qwen3.8-flash-next/README.md)
- [GLM Maya-M settings, build and restoration](models/glm5.3-flash-maya/README.md)
- [Hardware and physical GPU/CUDA mapping](docs/hardware.md)
- [Persistent services and manual model switching](docs/services.md)
- [Upstream community PR and hardware report](docs/upstream-contributions.md)
- [Agent task definitions, scoring and reproduction](benchmarks/agent-comparison/2026-10-16/README.md)
- [Earlier Qwen prefill/decode throughput experiments](benchmarks/throughput/README.md)
- [Upstream sources and licenses](THIRD_PARTY_NOTICES.md)

This repository publishes configurations, helper scripts, measurements and reproducible task fixtures.
Engine source and model weights are obtained from their upstream projects. Clean installation using the exported helpers has not been exercised end to end.
Generated runtime configurations and local paths are ignored by Git. The example API bind address is `127.0.0.1`.

The original Qwen-only repository is preserved at tag **`qwen38-baseline-20261015`**. Its history remains in this repository.
