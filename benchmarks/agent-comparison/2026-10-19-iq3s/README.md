# Qwen IQ3_S agent evaluation vs Q4 Flash-Next and GLM 5.3

## Results

All three deployments used the same 24-task agent suite, three repetitions per task, and the same deterministic grader. Each model completed 72 episodes. The IQ3_S evaluation ran on October 19, 2026; Qwen Q4_K_M and GLM Maya-M were evaluated on October 16. The task set, task ordering seed, sampling defaults, and final grader were held constant.

| Model | Complete task success | Role-weighted score | Tasks passed 3/3 | Successful median | Successful p95 | Successful tasks/hour | Tool schema valid |
|---|---:|---:|---:|---:|---:|---:|---:|
| Qwen Flash-Next Uncensored Q4_K_M | 69/72 · 95.8% | 96.7% | 21/24 | 20.25 s | 42.38 s | 161.6 | 399/407 · 98.0% |
| GLM-5.3 Flash Maya-M | 69/72 · 95.8% | 95.8% | 22/24 | 21.19 s | 48.59 s | 141.3 | 325/328 · 99.1% |
| Qwen Flash-Next GSQ-RCO IQ3_S | 66/72 · 91.7% | 90.0% | 20/24 | 16.79 s | 38.55 s | 169.5 | 458/459 · 99.8% |

Successful-task throughput uses total elapsed time for all 72 episodes, including failed episodes. Median and p95 completion times use successful episodes only.

**Observed result:** IQ3_S completed successful tasks fastest by these measures, while it passed three fewer episodes than either reference configuration. Its role-weighted score was 6.7 percentage points below Qwen Q4 and 5.8 points below GLM.

This is a local workload comparison, not an official benchmark. The three result rows describe deployed configurations and do not isolate model quality or speed. In particular, IQ3_S used only the two V100 GPUs while the two October 16 baselines used all four GPUs. Q4 and IQ3_S also came from different Flash-Next checkpoint sources, so their score difference cannot be assigned to quantization alone.

## Paired comparison and uncertainty

The comparisons use the same task and trial identifiers. A task-cluster bootstrap resampled the 24 authored tasks within categories; the intervals describe uncertainty for this small custom suite and are not official benchmark confidence intervals.

| Pair | IQ3_S-only passes | Reference-only passes | Both pass | Both fail | Weighted-score difference, IQ3_S minus reference | 95% task-cluster interval |
|---|---:|---:|---:|---:|---:|---:|
| IQ3_S vs Qwen Q4_K_M | 3 | 6 | 63 | 0 | −6.7 pp | −15.4 to 0.0 pp |
| IQ3_S vs GLM-5.3 Maya-M | 2 | 5 | 64 | 1 | −5.8 pp | −14.2 to 0.0 pp |

Both intervals reach zero. The sample suggests lower IQ3_S success on this suite, but it does not establish a general or causal model-quality difference.

## IQ3_S configuration measured

| Setting | Evaluated value |
|---|---|
| Checkpoint | ISTA-DASLab Qwen3.8-Flash-Next GSQ-RCO, IQ3_S |
| GGUF files | 83.62 GB decimal / 77.88 GiB combined; separate vision encoder excluded |
| Engine | Niko1221/Strata 0.1.43.1, commit a0116b2 |
| Context and KV cache | 262,144 tokens; INT8 KV |
| GPU placement | Physical CUDA indices 2 and 3: two 32 GiB Tesla V100 cards |
| Other GPUs | RTX 3090 and RTX 3060 were unused for this evaluation |
| Expert cache | Engine reported 24,346 slots out of 24,576 profiled pairs (99.1%); reported cache size 47,478 MiB |
| Primary cache | Engine reported 12,800 primary slots |
| VRAM reserve | 700 MiB per GPU |
| Prefill and layer split | Automatic |
| MTP and vision | MTP enabled with speculation; BF16 vision encoder enabled. The benchmark tasks were text-only. |

The 99.1% figure is the engine-reported expert cache-slot count divided by the profiled pair count. It is not a guarantee that 99.1% of the model's weight bytes remained resident continuously. RTX 3090 was intentionally left idle, as requested for this run.

The IQ3_S GGUF size is the sum of its two downloaded GGUF files. The comparison sizes and configurations are detailed in the [October 16 report](../2026-10-16/README.md).

## Task results

IQ3_S failed six of 72 episodes:

| Task | Required work | IQ3_S result |
|---|---|---:|
| W03 | Purchase within inventory constraints while preserving inventory and verifying the order | 1/3 |
| D04 | Make a scoped configuration change, preserve the validator, and run verification | 2/3 |
| T02 | Query three services and return the required structured health result | 1/3 |
| D03 | Use current source documents, cite/read the correct sources, and produce the requested quote | 2/3 |

The two reference models both passed W03 and D04 in all three trials. T02 was a shared weakness: Qwen Q4 passed 2/3 and GLM passed 1/3. All three passed 2/3 on D03, each failing once. IQ3_S passed all repeats for the other 20 tasks.

See [per-task comparison](task-comparison.csv), [category results](category-comparison.csv), and [all IQ3_S episode records](runs/iq3s/). Each episode directory contains its score, trajectory, and task workspace artifacts.

## Category results

| Category | Weight | Qwen Q4 passes | GLM passes | IQ3_S passes |
|---|---:|---:|---:|---:|
| Tool contracts | 15% | 11/12 | 10/12 | 10/12 |
| Business workflows | 25% | 12/12 | 12/12 | 10/12 |
| Files and evidence | 20% | 11/12 | 11/12 | 10/12 |
| Recovery and verification | 20% | 12/12 | 12/12 | 12/12 |
| Context and instruction | 15% | 12/12 | 12/12 | 12/12 |
| Maintenance | 5% | 11/12 | 12/12 | 12/12 |

The [machine-readable category CSV](category-comparison.csv) and [task CSV](task-comparison.csv) preserve the counts and failed trials. Time-by-category results for the October 16 pair are in the earlier report; IQ3_S category means are available in its episode records.

## Protocol and limits

- 24 tasks across tool contracts, business workflows, files/evidence, recovery/verification, context/instruction, and maintenance; each repeated three times.
- Same frozen task suite and task ordering seed 20261016. The exact suite SHA-256 is 3be3622f90af51eb067eb387e2746e03d3d2f5780c5759d95de10e77fbde024f; the task manifest and suite source are retained here and in the October 16 benchmark folder.
- Sampling used each server's defaults: temperature 1.0, top-p 0.95, top-k 20, min-p 0.0. No fixed generation seed was set.
- Each task had a 12-turn limit, 4,096 maximum output tokens per turn, and a 180-second wall-time budget.
- The harness used an OpenAI-native tool loop inspired by Hermes-style agent use. The live Hermes gateway, persistent memory, and skills were not run.
- Scoring checked final environment state, protected state, and explicit verification deterministically. No LLM judge was used.
- Business tools and reference pages were deterministic fixtures. File, SQLite, and Python/Node tasks ran in isolated task workspaces.

Three repetitions of 24 authored tasks provide a limited sample. This suite did not test image understanding, real accounts, browser/GUI workflows, maximum-context saturation, or long unattended operation. Task scores are not BFCL, tau-bench, Terminal-Bench, or Hermes leaderboard results.

## Artifacts

- [Three-model comparison workbook](AgentBenchmark_Three_Model_Comparison.xlsx)
- [Aggregate IQ3_S results](iq3s-results.json) and [paired statistics](comparison.json)
- [Task manifest](task-manifest.json), [execution plan](plan.json), and [grader validation](validation.json)
- [Deployment record](deployment.json), [benchmark metadata](metadata.json), [example model identifier](snapshots/iq3s-model.json), [runner](runner.py), and [Python requirements](requirements.txt)
- [Publication manifest with file hashes](publication-manifest.json)

To repeat the run, install the listed Python requirements and start the same model server first. Set STRATA_BASE_URL to its local address and STRATA_IQ3S_CONFIG to a local JSON file containing the served model_name, then run python runner.py. The server must expose OpenAI-compatible chat completions plus health and metrics endpoints. Set AGENT_BENCH_OUTPUT to a fresh output directory to keep the published records untouched. The runner only sends requests to the already-running server; it does not start or stop a service.

The exported episode paths are repository-relative. Machine-local home paths and the private bind address were removed from the published traces.
