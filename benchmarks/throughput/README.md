# Recorded benchmark results

This directory contains the Qwen Strata measurements from October 14–15 and the GLM Maya-M tuning sequence from October 16, 2026.
It explains the retained prefill values and publishes the earlier GPU-order attempts on the same mixed GPU PC.

- [Qwen prefill and later repeat results](#qwen-prefill-and-later-repeat-results): 22 unique requests, prefill 512–8192.
- [GLM Maya-M prefill, context, GPU-order and MTP trials](glm-maya-m-20261016/README.md): 21 unique requests across eight collections, including the later 1024 follow-up.
- [Main results and configuration rationale](../../README.md#why-these-prefill-values-and-gpu-order-were-chosen).

Timing JSON is copied byte for byte. Private paths and addresses are replaced in configuration snapshots and archival scripts.
The Qwen scripts accept a configurable URL and output directory. GLM's original runners are archived as text, with their historical mutations and errors retained.
The original history was exported from existing records without repeating its measurements.
The later 1024 follow-up added exactly three new inference requests at the owner's request; the old measurements and agent suite were retained.

## Qwen prefill and later repeat results

The initial sweep used two requests per value, temperature 0.7 and the reserves below. Later rows show separate repeats and sampling/swap conditions.
8192 was measured before 6144; the initial rows are sorted by chunk size.

| Requests | Prefill | Reserve MiB | Runs | Mean prompt tok/s | Mean decode tok/s | Mean total time |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A001–A002 | 512 | 700 | 2 | 892.98 | 71.30 | 76.297 s |
| B001–B002 | 1024 | 700 | 2 | 1258.12 | 71.45 | 56.245 s |
| C001–C002 | 2048 | 256 | 2 | 1663.32 | 72.60 | 44.181 s |
| D001–D002 | 4096 | 256 | 2 | 2066.34 | 73.65 | 36.845 s |
| F001–F002, initial | **6144** | 256 | 2 | 2202.38 | 70.75 | 35.293 s |
| E001–E002 | 8192 | 256 | 2 | 1969.25 | 69.75 | 38.707 s |
| F003–F004, repeat | 6144 | 256 | 2 | 2217.39 | 72.40 | 34.920 s |
| F005–F006, configured sampling defaults | 6144 | 256 | 2 | 2206.48 | 70.40 | 35.281 s |
| F007–F009, defaults and swap blocked | 6144 | 256 | 3 | 2207.57 | 70.53 | 35.254 s |
| F010–F012, defaults, swap blocked, service restarted | **6144** | **256** | **3** | **2212.05** | **69.70** | **35.280 s** |

6144 had the shortest mean request time in the initial sweep, while 4096 had a higher mean decode rate.
8192 completed both requests but had lower prompt throughput and longer total time than 6144. The later repeats retained 6144.
The 1024-to-2048 comparison also changed the reserve, and later groups changed sampling or swap policy; these are separate conditions.
Rates and times are arithmetic means of the saved per-request values, rounded for display. Older prose tables sometimes round the last digit differently.

### Conditions

- Ryzen 7 9700X, 64 GB class system RAM, RTX 3090 + RTX 3060 + two V100 32 GiB cards.
- Q4_K_M GGUF, Strata 0.1.43.1, 262144-token context, FP16 KV, GPU order `[2,0,1,3]`,
  layer boundaries `16,29,33`, PLE in RAM, F16 vision encoder on physical GPU 2.
- Synthetic repeated archive paragraph, 61,679 prompt tokens, 512-token generation limit.
- Each run changes the leading label; the recorded requests report zero reused/cached prompt tokens.
  Check the metric rather than assuming a new label always prevents all cache reuse.
- All generated tokens reached the limit during internal reasoning. This is throughput data,
  not answer-quality evaluation or a full 256K-context measurement.
- `prompt_tok_s = prompt_tokens / (prompt_ms / 1000)`; decoding rate is taken from Strata metrics.
- Existing scripts read `/metrics` after a non-streaming completion and select its newest request;
  concurrent client traffic can invalidate that association.
- Decode rate varies with speculative draft acceptance, sampling and run conditions.
  The small samples do not establish a universal optimum or a reliable improvement from disabling swap.

### Run groups

| JSON labels | Prefill | Reserve MiB | Sampling request | Service swap cap |
| --- | ---: | ---: | --- | --- |
| A001–A002 | 512 | 700 | temperature 0.7; other fields omitted | not blocked |
| B001–B002 | 1024 | 700 | temperature 0.7; other fields omitted | not blocked |
| C001–C002 | 2048 | 256 | temperature 0.7; other fields omitted | not blocked |
| D001–D002 | 4096 | 256 | temperature 0.7; other fields omitted | not blocked |
| E001–E002 | 8192 | 256 | temperature 0.7; other fields omitted | not blocked |
| F001–F004 | 6144 | 256 | temperature 0.7; other fields omitted | not blocked |
| F005–F006 | 6144 | 256 | all sampling fields omitted; configured defaults | not blocked |
| F007–F009 | 6144 | 256 | all sampling fields omitted; configured defaults | `MemorySwapMax=0` |
| F010–F012 | 6144 | 256 | all sampling fields omitted; configured defaults | `MemorySwapMax=0`, service restarted |

Configured final defaults are temperature 1.0, top_p 0.95, top_k 20, min_p 0.0.
The 1024→2048 comparison changes both prefill and reserve. Rows with different sampling or swap
conditions should be reported separately. Reserve 700 for A/B comes from the saved configuration;
those earliest JSON records do not contain `config_reserve_mib`.

The CSV [summary.csv](summary.csv) lists the 22 unique measured requests, excluding duplicate
`baseline-*.json` files. Each comparison directory retains its baseline copies so the original
comparison can still be reviewed. Small last-digit differences in older prose tables are rounding.

## GLM tuning and hardware dependence

[The GLM report](glm-maya-m-20261016/README.md) includes the two-/three-run averages, complete records and a chronological explanation:

1. Start with prefill 6144 at context 131072, then retain context 262144 after measuring both ceilings with a roughly 59.4K-token prompt.
2. Compare prefill 4096/6144/8192, then add 2048. The 2048 setting had the highest mean prompt throughput and shortest total time in that comparison.
3. Change physical order from `[0,2,3,1]` to `[0,2,1,3]`, moving MTP/output from the RTX 3060 to a V100.
4. Retain `[2,0,1,3]` for its slightly higher mean decode rate, while documenting its longer mean total time than `[0,2,1,3]`.
5. Try `[2,3,1,0]` with MTP/output on the RTX 3090; restore the preceding order after the mean decode rate decreased.
6. After the agent comparison, measure 1024 exactly three times at the final `[2,0,1,3]` order. Against the historical same-order 2048 baseline,
   mean prompt throughput was 830.30 versus 937.97 tok/s, decode 46.17 versus 45.33 tok/s, and total time 83.246 versus 74.979 s.
   The configuration was restored to 2048. [Follow-up records and method](glm-maya-m-20261016/followup-prefill1024-final-order/README.md).

The GLM order comparisons reused earlier baselines; the prefill sweep preceded the final order selection.
These experiments did not cover every prefill/order combination or repeat the agent-quality suite for every candidate.
The RTX 3060's Gen4 x1 link, the V100s' Gen3 x4 links, automatic layer placement, resident vision encoder and runtime cache behavior are part of this machine's configuration.
Link width and individual placement effects were not isolated. The published choices can differ from those on another host or workload.

## Repeating a measurement

For Qwen, see [the reproduction guide](../../models/qwen3.8-flash-next/docs/REPRODUCE.md#7-existing-benchmark-scripts).
The scripts send inference requests and do not change the server configuration. Their positional
prefill/reserve arguments are labels for the recorded metadata; the running server must match them.
The `bench_defaults.py` variant has the recorded final 6144/256 values in its metadata.

Publication changes to the copied scripts:

1. Read `STRATA_BASE_URL`, defaulting to `http://127.0.0.1:8080`.
2. Save under ignored `benchmarks/new-runs/<comparison>/` by default, or `STRATA_BENCH_OUTPUT_DIR`.

Prompt text, API request fields and metric selection are otherwise unchanged. No generated response
text, user chat history, raw runtime logs, model weights or authentication information is included.

The multi-model repository migration moved these scripts one directory deeper; their default output path was adjusted to remain under ignored `benchmarks/new-runs/`. Recorded timing JSON is unchanged.
