# Mixed GPU LLM Lab

## Test hardware

| Component | Recorded specification |
| --- | --- |
| CPU | Ryzen 7 9700X, 8 physical cores / 16 threads |
| System RAM | 64 GB DDR5 class; 60.47 GiB visible to Linux |
| Motherboard platform | B850 chipset, socket AM5 |
| Compute GPUs | RTX 3090 24 GiB + RTX 3060 12 GiB + 2 × V100 32 GiB; **100 GiB total VRAM** |
| GPU PCIe links | RTX 3090: Gen4 x16; RTX 3060: Gen4 x1; each V100: Gen3 x4 |
| Storage | 2 TB class NVMe SSD |
| Runtime | Ubuntu 24.04.5 LTS, CUDA 12.8, NVIDIA driver 580.178.04 |

[Hardware details and GPU numbering](docs/hardware.md) · [curated specification snapshot](docs/hardware-specs.json).
RAM module count, configured data rate and timings were not captured. Board and component-partner brands are omitted.

## Measured agent results — October 16 and 19, 2026

**24 tasks × 3 repetitions × 3 deployed configurations = 216 measured episodes** on the same RTX 3090 + RTX 3060 + dual V100 PC. The Qwen Q4 and GLM runs were measured October 16 using all four GPUs; the IQ3_S run was measured October 19 using only the two V100 GPUs. All three used the same task suite and final grader.

| Metric | Qwen3.8 Flash-Next Uncensored Q4_K_M | GLM-5.3 Flash Maya-M | Qwen3.8 Flash-Next GSQ-RCO IQ3_S |
| --- | ---: | ---: | ---: |
| Recorded model GGUF files, vision encoder excluded | 119.15 GB (110.97 GiB) | 116.00 GB (108.04 GiB) | 83.62 GB (77.88 GiB) |
| Complete task success | **69/72 · 95.8%** | **69/72 · 95.8%** | 66/72 · 91.7% |
| Assistant-role weighted score | **96.7%** | 95.8% | 90.0% |
| Tasks passed in all three repetitions | 21/24 | **22/24** | 20/24 |
| Successful tasks/hour, failed time included | 161.6 | 141.3 | **169.5** |
| Successful-episode median | 20.25 s | 21.19 s | **16.79 s** |
| Successful-episode p95 | 42.38 s | 48.59 s | **38.55 s** |
| Native tool argument/schema validity | 98.0% · 399/407 | 99.1% · 325/328 | **99.8% · 458/459** |
| Mean tool calls per episode | 5.65 | **4.56** | 6.38 |

The separate vision encoders were 0.91 GB for both Qwen configurations and 1.13 GB for GLM. GGUF size is not a measure of required runtime memory.

In the original Qwen Q4 vs GLM comparison, both passed 67 matched episodes; Qwen's geometric mean completion time on those pairs was 13.0% shorter (time ratio 0.870, paired task-cluster bootstrap 95% interval 0.806–0.943). The IQ3_S results and three-model workbook are linked below.

[**Three-model Excel comparison**](benchmarks/agent-comparison/2026-10-19-iq3s/AgentBenchmark_Three_Model_Comparison.xlsx) ·
[Three-model findings, task failures and configuration](benchmarks/agent-comparison/2026-10-19-iq3s/README.md) ·
[Machine-readable three-model statistics](benchmarks/agent-comparison/2026-10-19-iq3s/comparison.json) ·
[IQ3_S execution records](benchmarks/agent-comparison/2026-10-19-iq3s/runs/iq3s) ·
[Original Qwen/GLM report and workbook](benchmarks/agent-comparison/2026-10-16/README.md)

## What the results show

- **Qwen Q4 and GLM had equal strict success** at 69/72 episodes. Their role-weighted point estimates differed by 0.83 percentage points, with an interval spanning no difference; this suite does not establish a quality winner between them.
- **IQ3_S passed 66/72 episodes.** Its role-weighted score was 6.7 points below Qwen Q4 and 5.8 points below GLM. Paired task-cluster bootstrap intervals reach zero, so this small suite gives suggestive rather than conclusive evidence of lower task success.
- **IQ3_S had the fastest observed successful-task throughput and median completion time.** It ran on two V100 GPUs only; the Q4 and GLM baselines used all four GPUs. These timing results describe the deployed setups and do not isolate model-only speed.
- **The IQ3_S and Q4 checkpoints are not a controlled quantization pair.** Qwen Q4 came from ORCArouter's Uncensored checkpoint, while IQ3_S came from ISTA-DASLab's GSQ-RCO checkpoint. The score difference cannot be attributed to quantization alone.
- **Tool use varied by metric.** IQ3_S had the highest valid tool-call schema rate, while it averaged more calls per episode than Qwen Q4 or GLM. The saved traces show task execution, verification and errors.

These observations describe three actual deployment stacks, including different checkpoints, quantizations, GPU allocations, prefill and KV settings. They do not isolate base-model intelligence or establish a universal ranking. Use the task definitions, failures, settings and traces to judge which tradeoffs fit your work.

### Reasoning settings and observed token use

**In the October 16 Qwen Q4/GLM comparison, thinking was enabled. Qwen used its chat template's default `xhigh`; GLM used the configured `high`.**
The benchmark requests omitted reasoning-effort overrides. Qwen's highest template level is `xhigh`; GLM also offers `max`, which was not measured here.
These level names are specific to each model and do not imply equal reasoning work.

| October 16 setting or observation | Qwen Q4 | GLM |
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

For IQ3_S, benchmark requests also omitted reasoning-effort overrides; the runner set a 4096-token output limit per request. Its template effort was not separately audited. The October 16 comparison retains each deployment's reasoning settings. The effect of raising GLM from `high` to `max` on success and completion time remains unmeasured.
A comparison of Qwen Q4 and GLM at their highest reasoning settings would require a separate run with sufficient, matching generation and reasoning budgets.
See the [reasoning audit and evidence](benchmarks/agent-comparison/2026-10-16/README.md#reasoning-settings-and-token-limits) for the budget calculation and request records.

### Where the October 16 Qwen Q4 and GLM runs differed

Of their **72 matching task/repetition pairs**, both models passed 67, only Qwen passed 2, only GLM passed 2, and both failed 1. The four pairs with different outcomes are shown below. IQ3_S failures and matched outcomes are listed separately in the [October 19 three-model report](benchmarks/agent-comparison/2026-10-19-iq3s/README.md).

| Episode | Required work | Qwen | GLM |
| --- | --- | --- | --- |
| T02-r3 | Query three services and return only a JSON object | [Pass](benchmarks/agent-comparison/2026-10-16/runs/qwen/T02-r3/result.json): bare JSON | [Fail](benchmarks/agent-comparison/2026-10-16/runs/glm/T02-r3/result.json): correct values inside a Markdown code fence |
| D03-r3 | Use current prices and discounts for one quote covering 100 units | [Pass](benchmarks/agent-comparison/2026-10-16/runs/qwen/D03-r3/result.json): quantity 100, total USD 1350 | [Fail](benchmarks/agent-comparison/2026-10-16/runs/glm/D03-r3/result.json): generated 100 quotes for quantities 1–100 |
| D03-r1 | Same quote task | [Fail](benchmarks/agent-comparison/2026-10-16/runs/qwen/D03-r1/result.json): generated 100 quotes for quantities 1–100 | [Pass](benchmarks/agent-comparison/2026-10-16/runs/glm/D03-r1/result.json): quantity 100, total USD 1350 |
| M04-r3 | Fix and verify the HTTP retry policy, then report completion | [Fail](benchmarks/agent-comparison/2026-10-16/runs/qwen/M04-r3/result.json): code and verification passed, but final API content was empty | [Pass](benchmarks/agent-comparison/2026-10-16/runs/glm/M04-r3/result.json): code, verification and final response passed |

`r1` and `r3` identify independent repetitions of the same task. D03's Korean phrase `100개 견적` can also be read as "100 quotes";
the frozen target was one quote for 100 units. Each model took the alternate interpretation once.
For M04, Qwen passed the code and execution checks; the failed condition was the missing final response, whose cause was not diagnosed.
The one pair both failed was T02-r1: both returned correct values inside a code fence despite the JSON-only instruction.

These observed differences concern output format, ambiguous instruction interpretation and completion reporting.
See the [paired-case explanations and complete response traces](benchmarks/agent-comparison/2026-10-16/README.md#paired-outcomes-where-only-one-model-succeeded) for the exact requirements and evidence.

### Category results

Each category contains four tasks, repeated three times per system. Mean times include all 12 attempts per model, including failures.

| Category | Role weight | Qwen Q4 passes | GLM passes | IQ3_S passes | Qwen Q4 mean time | GLM mean time | IQ3_S mean time |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Tool contracts | 15% | 11/12 | 10/12 | 10/12 | 9.23 s | 10.70 s | 7.01 s |
| Business workflows | 25% | 12/12 | 12/12 | 10/12 | 22.68 s | 26.43 s | 22.06 s |
| Files and evidence | 20% | 11/12 | 11/12 | 10/12 | 29.47 s | 25.74 s | 24.41 s |
| Recovery and verification | 20% | 12/12 | 12/12 | 12/12 | 19.03 s | 21.41 s | 14.85 s |
| Context and instruction | 15% | 12/12 | 12/12 | 12/12 | 22.82 s | 41.03 s | 23.86 s |
| Small maintenance tasks | 5% | 11/12 | 12/12 | 12/12 | 24.87 s | 21.18 s | 24.65 s |

IQ3_S category means are calculated from the 72 published episode records. The [October 19 report](benchmarks/agent-comparison/2026-10-19-iq3s/README.md) includes task-level counts and traces.

### Scope and limitations

This is a **custom, controlled OpenAI-native agent loop inspired by Hermes-style use**. The live Hermes gateway, persistent memory and skills were not run.
Business APIs and knowledge pages are deterministic fixtures; files, SQLite and Python/Node execution are real isolated tasks.
Each task exposes 3–8 tools and has a 180-second, 12-turn budget. There is no commercial LLM judge.

The Korean wording of one quote task (D03) admits two interpretations. The frozen target is one quote for 100 units; Qwen Q4 and GLM each produced a 100-quote list in one repetition.
For the October 16 Qwen/GLM pair, excluding that item, both systems scored **67/69 · 97.1%**. The workbook reports this sensitivity separately.
Other strict failures were bare-JSON formatting (Qwen once, GLM twice) and an empty final API response after correct code changes (Qwen once).
The 144 October 16 Qwen/GLM episodes and the 72 October 19 IQ3_S episodes use the same final grader hash. The October 16 [grading corrections and original verdicts](benchmarks/agent-comparison/2026-10-16/grading-audit.json) are retained.

Three repeats of 24 authored tasks are a limited sample. Image understanding, real accounts, browser/GUI work, a production-sized tool catalog, maximum-context saturation and long unattended operation were not evaluated.
GLM ran before Qwen on one host; the October 16 pair was not counterbalanced. IQ3_S was measured separately on October 19. These are not official BFCL, tau-bench, Terminal-Bench or Hermes leaderboard scores.

## Recorded deployments

| Setting | Qwen Q4 profile | GLM Maya-M profile | Qwen IQ3_S profile |
| --- | --- | --- | --- |
| Model and source | OrcaRouter Qwen3.8 Flash-Next Uncensored, Q4_K_M | Peasant Smith GLM-5.3 Flash Maya-M, mixed quantization with IQ2_S experts | ISTA-DASLab Qwen3.8 Flash-Next GSQ-RCO, IQ3_S |
| Engine | [Niko1221/Strata](https://github.com/Niko1221/Strata), 0.1.43.1, a0116b2 | [mw00/project-maya](https://github.com/mw00/project-maya), 1.1.11, 362671a | [Niko1221/Strata](https://github.com/Niko1221/Strata), 0.1.43.1, a0116b2 |
| Context ceiling | 262144 | 262144 | 262144 |
| Prefill chunk | 6144 | 2048 | Automatic |
| KV | FP16, GPU-resident configuration | FP16, streaming with 32768 resident positions | INT8 |
| GPU order, physical indices | [2,0,1,3] | [2,0,1,3] | [2,3] |
| Base-layer placement | [0,16) / [16,29) / [29,33) / [33,48) | [0,16) / [16,27) / [27,31) / [31,45), observed auto split | Automatic split across the two V100 GPUs; exact layer ranges not retained |
| Expert cache | 24576 cache slots; prefill borrows slots with RAM backing | 10102 VRAM slots including slack; remaining experts in pinned RAM, disk eviction off | 24346 reported cache slots out of 24576 profiled pairs; 47478 MiB reported cache, including 12800 primary slots |
| MTP | Qwen native draft, spec 4, minimum probability 0.5 | GLM MTP enabled | MTP enabled, spec 4, minimum probability 0.5 |
| Reasoning effort | xhigh, chat-template default | high, configured server default | No request-level override; template default was not separately audited |
| Vision | F16 encoder on physical GPU 2 | F16 encoder on physical GPU 2 | BF16 vision encoder enabled; evaluation tasks were text-only |
| Process swap | MemorySwapMax=0 | MemorySwapMax=0 | MemorySwapMax=0 |

The IQ3_S slot ratio is 24346/24576, about 99.1% of profiled cache slots. It is not a byte-weight residency guarantee. The RTX 3090 and RTX 3060 were unused during that evaluation. See the [deployment record](benchmarks/agent-comparison/2026-10-19-iq3s/deployment.json) for the full IQ3_S snapshot.

All three used API defaults temperature 1.0, top_p 0.95, top_k 20 and min_p 0.0. The reasoning settings and observed token usage for the Qwen Q4/GLM pair are detailed above. Vision was enabled during the evaluations, but agent tasks were text-only. GPU and MTP placement differed by configuration.

## Why these prefill values and GPU order were chosen

The configurations came from earlier throughput trials on this PC. **Prefill is the prompt-processing chunk size; the context ceiling remains 262144.**
The trials used a long synthetic prompt, 512 generated tokens and zero reported prompt-cache reuse. They measure prompt reading, decoding and full request time.
The separate 24-task agent benchmark above measured task completion using the retained configurations.

### Qwen: keep prefill 6144 after trying 512 through 8192

Each initial row below contains two measured requests with 61679 prompt tokens. GPU order was `[2,0,1,3]` throughout these saved Qwen comparisons.
The sequence was 512 → 1024 → 2048 → 4096 → 8192 → 6144; the table is sorted by chunk size.

| Prefill | VRAM reserve/GPU | Mean prompt tok/s | Mean decode tok/s | Mean total request time |
| ---: | ---: | ---: | ---: | ---: |
| 512 | 700 MiB | 892.98 | 71.30 | 76.297 s |
| 1024 | 700 MiB | 1258.12 | 71.45 | 56.245 s |
| 2048 | 256 MiB | 1663.32 | 72.60 | 44.181 s |
| 4096 | 256 MiB | 2066.34 | 73.65 | 36.845 s |
| **6144** | **256 MiB** | **2202.38** | 70.75 | **35.293 s** |
| 8192 | 256 MiB | 1969.25 | 69.75 | 38.707 s |

**6144 had the shortest mean request time in this initial sweep; 8192 completed but was slower.**
4096 had the higher mean decode rate, so the choice favored long-prompt request time rather than decode rate alone.
The 1024-to-2048 step also reduced the VRAM reserve; its improvement cannot be assigned to prefill alone.
All initial rows requested temperature 0.7. Later repeats with the final sampling defaults and swap blocked retained 6144;
the last three requests averaged **2212.05 prompt tok/s, 69.70 decode tok/s and 35.280 s**.
Those later sampling/swap groups are documented separately in the [22-request Qwen history](benchmarks/throughput/README.md#qwen-prefill-and-later-repeat-results).

### GLM Maya-M: reduce prefill from 6144 to 2048

Two requests per value, context 262144, FP16 KV and 59434–59438 prompt tokens. This comparison used the earlier GPU order `[0,2,3,1]`.

| Prefill | Mean prompt tok/s | Mean decode tok/s | Mean total request time |
| ---: | ---: | ---: | ---: |
| **2048** | **911.05** | 40.45 | **78.108 s** |
| 4096 | 881.60 | 40.30 | 80.312 s |
| 6144 | 821.70 | 38.85 | 85.993 s |
| 8192 | 744.15 | 39.10 | 93.361 s |

**2048 had the highest mean prompt throughput and shortest mean request time**, so it was retained.
8192 fit and completed, but ran slowest. Reported VRAM expert slots were 10180 at 2048/4096/6144 and 10178 at 8192;
the observed gain was not accompanied by a large increase in VRAM slots.
The sequence first measured 6144, then 4096/8192, then added 2048, reusing earlier measurements.
See the [raw requests and comparison details](benchmarks/throughput/glm-maya-m-20261016/README.md#2-compare-prefill-4096-6144-and-8192-then-add-2048).

### GLM GPU-order and MTP placement trials

Physical indices: **0 = RTX 3090, 1 = RTX 3060, 2 = vision V100, 3 = the other V100**.
All four rows used prefill 2048, context 262144, 59437 prompt tokens and 512 generated tokens.

| Physical GPU order | Last GPU, with output head/MTP | Runs | Mean prompt tok/s | Mean decode tok/s | Mean total request time |
| --- | --- | ---: | ---: | ---: | ---: |
| `[0,2,3,1]` | RTX 3060 | 2 | 911.05 | 40.45 | 78.108 s |
| `[0,2,1,3]` | V100 | 2 | **955.40** | 44.65 | **73.925 s** |
| **`[2,0,1,3]` — retained** | **V100** | **3** | 937.97 | **45.33** | 74.979 s |
| `[2,3,1,0]` — reverted | RTX 3090 | 3 | 945.90 | 39.87 | 76.106 s |

- Moving the RTX 3060 from the final stage to the third stage, with MTP on the final V100, increased mean decode rate about 10.4% and reduced mean request time about 5.4% in these samples.
- Putting the vision V100 first, `[2,0,1,3]`, was retained using **mean decode rate** as the selection criterion: about 1.5% higher than `[0,2,1,3]`. Its mean request time was about 1.4% longer. The retained order did not minimize total time in this table.
- Putting the RTX 3090 last with MTP, `[2,3,1,0]`, reduced mean decode rate about 12.1% versus the retained order, so it was reverted. This also changed base-layer distribution and expert allocation; it did not isolate MTP execution speed.

These GPU-order measurements are for **GLM Maya-M**. The published Qwen throughput records use the fixed `[2,0,1,3]` order.
The [complete GLM tuning history](benchmarks/throughput/glm-maya-m-20261016/README.md) includes 21 unique requests, reused-baseline provenance,
historical configs, observed layer maps, the context-ceiling trials, a summary-construction error, the rollback decision and the later 1024 follow-up below.

### Follow-up: prefill 1024 on the final GLM order

After the original tuning and agent comparison, **three new 1024 requests** were measured with the final `[2,0,1,3]` order.
Context 262144, FP16 KV, MTP, resident vision and sampling defaults were retained. Each request used 59437 prompt tokens and generated 512 tokens,
with zero prompt-cache reuse. No extra warm-up or fresh 2048 requests were added.

| Prefill and evidence | Runs | Mean prompt tok/s | Mean decode tok/s | Mean total request time |
| --- | ---: | ---: | ---: | ---: |
| 1024, new follow-up | 3 | 830.30 | 46.17 | 83.246 s |
| 2048, historical same-order baseline | 3 | 937.97 | 45.33 | 74.979 s |

Relative to that historical baseline, **1024 had 11.5% lower prompt throughput, 1.8% higher decode rate and 11.0% longer mean total time**.
All three runs, including the slower first request, are retained. This is a small sequential follow-up against earlier measurements, rather than a fresh alternating A/B test.
The GLM configuration was restored to 2048; the original 144-episode agent results used 2048 and were not rerun for this follow-up.
See the [individual requests, comparison and restoration record](benchmarks/throughput/glm-maya-m-20261016/followup-prefill1024-final-order/README.md).

### Hardware and experiment limits

The PCIe links were **Gen4 x16 for the RTX 3090, Gen4 x1 for the RTX 3060, and Gen3 x4 for each V100**.
The vision encoder occupied memory on physical GPU 2. These settings reflect this topology and the tested model/runtime/workload.
The trials did not isolate PCIe link width or prove that a particular card alone caused a bottleneck.

Samples contain only two or three sequential requests, with historical baselines reused and no counterbalancing of order or cache warmth.
The GLM prefill sweep preceded its final GPU-order selection; all prefill values were not tested again for every order.
The agent suite was also not repeated for each tuning candidate. Different hardware, prompt/output lengths or latency priorities can change the preferred settings.

## Configuration and reproduction

- [Qwen settings, build and restoration](models/qwen3.8-flash-next/README.md)
- [GLM Maya-M settings, build and restoration](models/glm5.3-flash-maya/README.md)
- [Hardware and physical GPU/CUDA mapping](docs/hardware.md)
- [Persistent services and manual model switching](docs/services.md)
- [Upstream community PR and hardware report](docs/upstream-contributions.md)
- [Three-model agent results, IQ3_S task traces and deployment](benchmarks/agent-comparison/2026-10-19-iq3s/README.md)
- [Qwen Q4 vs GLM agent task definitions, scoring and reproduction](benchmarks/agent-comparison/2026-10-16/README.md)
- [Prefill, GPU-order and MTP tuning history](benchmarks/throughput/README.md)
- [Upstream sources and licenses](THIRD_PARTY_NOTICES.md)

This repository publishes configurations, helper scripts, measurements and reproducible task fixtures.
Engine source and model weights are obtained from their upstream projects. Clean installation using the exported helpers has not been exercised end to end.
Generated runtime configurations and local paths are ignored by Git. The example API bind address is `127.0.0.1`.

The original Qwen-only repository is preserved at tag **`qwen38-baseline-20261015`**. Its history remains in this repository.
