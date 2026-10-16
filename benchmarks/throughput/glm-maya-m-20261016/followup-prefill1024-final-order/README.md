# Follow-up: prefill 1024 on the final GLM GPU order

Three new sequential requests were measured on October 16, 2026, after the original tuning and agent comparison.
The owner requested exactly three 1024 measurements, with no extra warm-up or fresh 2048 requests.
The reference is the earlier three-request 2048 baseline at the **same final physical GPU order `[2,0,1,3]`**.

## Configuration and protocol

| Setting | Value |
| --- | --- |
| Model | GLM5.3 Flash Maya-M, mixed quantization including IQ2_S experts |
| Runtime | Project Maya 1.1.11; source `362671aee624183ce3630fb1fd4c1aa431a5a451` |
| Changed setting | Prefill 2048 → 1024 for the test, restored to 2048 afterward |
| Context / KV | 262144; FP16, streaming with 32768 resident positions |
| Physical GPU order | `[2,0,1,3]`: vision V100, RTX 3090, RTX 3060, final V100 with output head/MTP |
| Base-layer ranges | `[0,16) / [16,27) / [27,31) / [31,45)`, unchanged from the reference layout |
| API defaults | temperature 1.0, top_p 0.95, top_k 20, min_p 0.0; reasoning effort high |
| Prompt / output | 59437 prompt tokens and 512 generated tokens per request |
| Prompt cache reuse | Zero for all three requests |
| Swap | Service `MemorySwapMax=0`; `MemorySwapCurrent=0` after every request |

The synthetic archive paragraph and generation request follow the earlier protocol. Sampling and thinking overrides were omitted from the API body.
The running engine command explicitly contained `--prefill 1024`; see [engine-command.txt](engine-command.txt).
The service request counter increased from **0 to 3**, with no additional inference requests observed.
The [archival runner](run_test.py.txt) documents the full protocol and restoration steps.

## Individual 1024 measurements

| Run | Prompt time | Prompt tok/s | Decode tok/s | Total request time | Record |
| --- | ---: | ---: | ---: | ---: | --- |
| P1024-R1 | 78.668 s | 755.50 | 41.40 | 91.069 s | [JSON](P1024-R1.json) |
| P1024-R2 | 68.470 s | 868.10 | 48.90 | 79.220 s | [JSON](P1024-R2.json) |
| P1024-R3 | 68.532 s | 867.30 | 48.20 | 79.448 s | [JSON](P1024-R3.json) |
| **Mean** | **71.890 s** | **830.30** | **46.17** | **83.246 s** | |

All three generated 512 tokens, ended at the output limit, and reported zero reused prompt tokens.
The first request was slower than the next two; all three are included in the mean. No first-run exclusion was applied.
These are throughput measurements, with no answer-quality grading.

## Compare with the historical same-order 2048 baseline

The baseline requests are [V021-R1](../gpu-order-v100-first/V021-R1.json), [V021-R2](../gpu-order-v100-first/V021-R2.json)
and [V021-R3](../gpu-order-v100-first/V021-R3.json). They also used 59437 prompt tokens, 512 generated tokens, zero prompt-cache reuse,
the same physical GPU order and the same context/KV settings.

| Setting | Runs | Mean prompt tok/s | Mean decode tok/s | Mean total request time |
| --- | ---: | ---: | ---: | ---: |
| 1024, new follow-up | 3 | 830.30 | 46.17 | 83.246 s |
| 2048, historical reference | 3 | 937.97 | 45.33 | 74.979 s |
| 1024 change relative to reference | | −11.5% | +1.8% | +11.0% |

1024's slightly higher mean decode rate accompanied lower prompt throughput and a longer mean request time for this long-prompt workload.
The GLM profile was restored to 2048. The 24-task agent suite was not rerun; its original results still use the recorded 2048 deployment.

The reference was recorded earlier, rather than measured again in an alternating A/B sequence. Cache warmth, clocks, temperature and
other host activity were not controlled as separate factors. Three requests per setting provide limited evidence about repeatability.
This follow-up should not be inserted into the earlier four-value prefill sweep as a single-factor comparison: that sweep used `[0,2,3,1]`.

Reported VRAM slots were **10103** at 1024 versus **10102** in the reference. Reported RAM slots were **3755** versus **3960**.
These are runtime allocation counters, including slack and prefill backing behavior, rather than exact counts of distinct resident experts.
The new records retain the full GPU maps and engine counters.

## Evidence and restored state

- [Before-config](config.before.template.json) and [test config](config.test.template.json): the only test change was prefill 2048 → 1024.
- [Metadata and fingerprints](metadata.template.json): source commit, engine binary SHA-256 and original config hashes.
- [Recorded comparison](summary.template.json): all per-setting averages, percentage changes and the 0 → 3 request count.
- [Health response](health-before.json) and [service properties during the test](service-during.json).
- [Original service state](services-before.json) and [restoration result](restoration.json).

Both GLM and Qwen configuration files were restored byte for byte. The originally active Qwen service was loaded and serving again;
Qwen remained enabled for boot, and GLM remained registered but disabled for boot and inactive. No service enablement policy changed.
The raw per-request JSON and service/restoration records are byte-identical copies. Template snapshots and archived source replace private paths and the bind address.
The [parent provenance map](../source-records.json) and [publication hashes](../publication-manifest.json) record those transformations.
