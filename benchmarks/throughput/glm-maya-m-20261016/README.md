# GLM Maya-M: prefill, context and GPU-order tuning

Measurements and a later follow-up from October 16, 2026 on the [mixed RTX 3090 / RTX 3060 / dual V100 host](../../../docs/hardware.md).
These trials explain the later agent benchmark's **prefill 2048 and physical GPU order `[2,0,1,3]`**.
The model is GLM5.3 Flash Maya-M with mixed quantization, including IQ2_S experts, served by Project Maya.

[Unique request CSV](unique-runs.csv) · [recomputed comparisons](comparison-summary.json) · [source provenance and duplicate mapping](source-records.json) · [publication hashes](publication-manifest.json)

## Measurement conditions and reading the data

- One long synthetic request at a time: a repeated archive paragraph, followed by a request for numbered observations.
  The original request construction is retained as [archival runner text](context262k-prefill6144/bench.py.txt).
- Maya counted 59434–59438 prompt tokens, depending on the leading run label. The same prompt pattern counted about 61679 tokens in the Qwen trials.
- Every measured request generated 512 tokens, ended at that output limit, and reported zero reused prompt tokens.
  These are throughput measurements; generated answer quality was not scored.
- FP16 KV; context ceiling 262144 for the main prefill and GPU-order comparisons. The first two trials used a 131072 ceiling.
- Requests omitted sampling fields. The recorded effective defaults were temperature 1.0, top_p 0.95, top_k 20 and min_p 0.0; reasoning effort was high.
  The earliest before-config predates explicitly recording all sampling defaults; use the request records and later snapshots for the measured settings.
- The F16 vision encoder remained on physical GPU 2, although these requests contained text only. MTP remained enabled.
  The last GPU also held the output head and MTP; changing order moved base layers as well as MTP.
- Each row is an arithmetic mean of the saved per-request rates or wall times, rather than a pooled token/time rate.
  Displayed values are rounded; older saved summaries sometimes differ in their last digit because they round earlier.

There are **21 unique measured requests** and **27 per-request JSON files**. Six files are byte-identical baseline copies reused in later comparisons.
Those copies are not extra repetitions. The CSV deduplicates by file hash, since labels such as `M001` also appear in genuinely different context trials.
Raw request records and the original seven `summary.json` files are copied byte for byte. The follow-up summary and metadata replace a private baseline path.
Config templates and archived Python text also replace private home paths and bind addresses.
The `.py.txt` files preserve the executed protocol, including historical service/config mutations; they are archival records, not current launch helpers.

## 1. First set prefill to 6144, then increase the context ceiling

Both stages used physical GPU order `[0,2,3,1]` and two sequential runs.

| Context ceiling | Prefill | Prompt tokens/run | Mean prompt tok/s | Mean decode tok/s | Mean total request time | Records |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 131072 | 6144 | 59434 | 821.10 | 38.85 | 85.995 s | [M001](initial-context131k-prefill6144/M001.json), [M002](initial-context131k-prefill6144/M002.json) |
| 262144 | 6144 | 59434 | 821.70 | 38.85 | 85.993 s | [M001](context262k-prefill6144/M001.json), [M002](context262k-prefill6144/M002.json) |

For this approximately 59.4K-token request, the two-run means were very close. The larger context ceiling was retained.
These measurements did not fill either context window and do not measure a full 262144-token prefill.

## 2. Compare prefill 4096, 6144 and 8192, then add 2048

Physical GPU order was still `[0,2,3,1]`: RTX 3090, V100, V100, RTX 3060. Each value has two measured requests.
The chronology was 6144 at 262144 context, then fresh 4096 and 8192 measurements, then fresh 2048 measurements.
Earlier results were reused to build the combined comparison; this was not a randomized four-value sweep.

| Prefill | Mean prompt tok/s | Mean prompt time | Mean decode tok/s | Mean total request time | Reported VRAM slots | Reported RAM slots |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **2048** | **911.05** | **65.291 s** | 40.45 | **78.108 s** | 10180 | 3857 |
| 4096 | 881.60 | 67.435 s | 40.30 | 80.312 s | 10180 | 4069 |
| 6144 | 821.70 | 72.340 s | 38.85 | 85.993 s | 10180 | 4180 |
| 8192 | 744.15 | 79.885 s | 39.10 | 93.361 s | 10178 | 4306 |

**2048 was selected because it had the highest mean prompt throughput and shortest mean request time in this comparison.**
Its mean request time was about 2.7% shorter than 4096. The 8192 setting loaded and completed both requests, but ran slowest.
Thus, fitting a larger prefill chunk in memory did not predict a throughput gain on this machine.

VRAM slots were unchanged from 2048 through 6144 and decreased by only two at 8192. The recorded slot counts do not support attributing
2048's improvement to a large increase in VRAM expert residency. RAM-slot accounting also includes the runtime's allocation behavior;
slot totals alone are not exact counts of distinct experts or model-residency percentages. These trials did not isolate a single cause of the slowdown.

The [combined comparison directory](prefill-2048-4096-6144-8192) retains all eight records. Its `P6144-R1/R2` files are copies of the earlier
`M001/M002` context-262144 measurements, and its 4096/8192 files are copies from the [preceding comparison](prefill-4096-6144-8192).
The [source mapping](source-records.json) identifies every duplicate.

## 3. Move the RTX 3060 away from the last stage

The GPU-order trials used prefill 2048, context 262144, FP16 KV, 59437 prompt tokens and 512 generated tokens.
Physical indices are **0 = RTX 3090, 1 = RTX 3060, 2 = vision V100, 3 = the other V100**.

| Physical GPU order | MTP/output GPU | Runs | Mean prompt tok/s | Mean decode tok/s | Mean total request time | Reported VRAM slots |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `[0,2,3,1]` | RTX 3060 | 2 | 911.05 | 40.45 | 78.108 s | 10180 |
| `[0,2,1,3]` | V100, physical 3 | 2 | **955.40** | 44.65 | **73.925 s** | 10171 |
| **`[2,0,1,3]` — retained** | **V100, physical 3** | **3** | 937.97 | **45.33** | 74.979 s | 10102 |
| `[2,3,1,0]` — reverted | RTX 3090 | 3 | 945.90 | 39.87 | 76.106 s | 10106 |

Moving from `[0,2,3,1]` to `[0,2,1,3]` moved the RTX 3060 to the third stage and placed the output head/MTP on the final V100.
The mean decode rate increased by about 10.4% and mean request time fell by about 5.4%. The baseline was reused from the 2048 prefill trial.
See [both new requests, the recorded decision and before-config](gpu-order-3090-first-v100-last).

## 4. Put the vision V100 first and keep the final V100 for MTP

The next candidate was `[2,0,1,3]`: vision V100, RTX 3090, RTX 3060, final V100 with MTP.
Three candidate requests were compared with the two preceding `[0,2,1,3]` requests.

**The selection criterion was mean decode rate.** It increased from 44.65 to 45.33 tok/s, about 1.5%, so this order was retained.
Mean prompt throughput decreased about 1.8%, and mean total request time increased about 1.4%.
Consequently, the retained order had the highest observed mean decode rate, while `[0,2,1,3]` had the shortest observed mean total time.
The small difference and unequal two-/three-run samples leave substantial uncertainty about repeatability.

The [three raw records](gpu-order-v100-first), including their full `gpu_map` fields, and the original decision summary are published.
The archived runner also retains a [report-construction error](gpu-order-v100-first/failure.txt): it referenced `summary` while constructing that variable.
All three inference records had already been saved. That reporting error is separate from an inference failure; the recorded final summary and later config snapshots show the retained order.

## 5. Try MTP on the RTX 3090, then restore the previous order

The candidate `[2,3,1,0]` kept the vision V100 first and the RTX 3060 third, moved the second V100 to stage two,
and put the RTX 3090 last with the output head/MTP. It was compared with the preceding three `[2,0,1,3]` requests.

Mean decode rate fell from **45.33 to 39.87 tok/s**, about **12.1%**, while mean total request time increased about 1.5%.
The order was restored to `[2,0,1,3]`. Putting MTP on the faster GPU did not improve this complete placement on this workload.

This was a whole-placement change, not an isolated measurement of MTP execution speed. The recorded base-layer ranges changed too:

| Order | Physical 2 | Second stage | Physical 1 | Last stage |
| --- | --- | --- | --- | --- |
| `[2,0,1,3]` | V100: `[0,16)` | RTX 3090: `[16,27)` | RTX 3060: `[27,31)` | V100: `[31,45)`, MTP |
| `[2,3,1,0]` | V100: `[0,16)` | V100: `[16,31)` | RTX 3060: `[31,35)` | RTX 3090: `[35,45)`, MTP |

Ranges are zero-based and half-open. See the [candidate request maps](mtp-on-3090) and the [recorded rollback decision](mtp-on-3090/summary.json).
The maps also show that layer distribution and expert-pool allocation changed with GPU order.

## 6. Follow up with prefill 1024 on the final order

After the original tuning and agent comparison, prefill 1024 was measured **exactly three times** with `[2,0,1,3]`, context 262144,
FP16 KV and the retained MTP, vision and sampling settings. The comparison reused the three earlier 2048 requests from section 4;
it added no warm-up or fresh 2048 requests. The service's request counter increased from zero to three.

| Prefill | Evidence | Runs | Mean prompt tok/s | Mean decode tok/s | Mean total request time |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1024 | New follow-up | 3 | 830.30 | 46.17 | 83.246 s |
| 2048 | Historical same-order baseline | 3 | 937.97 | 45.33 | 74.979 s |

1024 had about **11.5% lower prompt throughput**, **1.8% higher decode rate** and **11.0% longer mean total time** than that historical baseline.
All runs used 59437 prompt tokens, generated 512 tokens and reported zero reused prompt tokens. The slower first 1024 request is included in the mean.
The GLM config was restored to 2048, and the originally active Qwen service was restored with boot enablement unchanged.
The [follow-up directory](followup-prefill1024-final-order/README.md) includes individual rates, runtime allocation counters,
the actual engine command, config snapshots, source/binary fingerprints and restoration evidence.

These measurements were taken at different times, with no counterbalancing of cache warmth, clocks or order.
The 1024 follow-up belongs with the final-order 2048 baseline; adding it to section 2's earlier `[0,2,3,1]` sweep would change two factors at once.
The original agent-quality suite still uses its recorded prefill 2048 deployment.

## What applies to another machine

This host combines a **PCIe Gen4 x16 RTX 3090, Gen4 x1 RTX 3060 and two Gen3 x4 V100s**. The vision encoder also consumes memory on one V100.
The experiments document the complete model/runtime/placement on that topology. They do not isolate the effect of the RTX 3060 link width,
GPU architecture, expert-cache behavior, MTP placement or CPU scheduling individually. No PCIe rewiring comparison was measured.

The samples are small and sequential. Historical baselines were reused, order was not counterbalanced, and expert-cache warmth,
clocks, power and temperature were not controlled as experimental factors. Zero prompt-cache reuse does not mean a cold expert cache.
The prefill sweep preceded the final GPU-order selection; all prefill values were not retested for every later order.
The retained combination is therefore the recorded choice from this sequence, with its selection criteria and tradeoffs documented.

The later agent comparison used the retained settings, but the tuning trials did not run that 24-task suite for every candidate.
Other prompt lengths, output lengths, hardware links, engine versions or latency priorities can lead to different choices.
Use the [current profile](../../../models/glm5.3-flash-maya/README.md) for restoration, and these historical records to choose which alternatives to measure on your own machine.
