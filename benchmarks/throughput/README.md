# Recorded benchmark results

These are the existing 2026-10-14/15 Qwen Strata measurements, exported without rerunning inference.
Timing JSON is copied byte for byte. Machine paths and addresses are removed from configuration
snapshots, and the copied scripts accept a configurable URL and output directory.

## Conditions

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

## Run groups

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

## Repeating a measurement

See [the reproduction guide](../../models/qwen3.8-flash-next/docs/REPRODUCE.md#7-existing-benchmark-scripts).
The scripts send inference requests and do not change the server configuration. Their positional
prefill/reserve arguments are labels for the recorded metadata; the running server must match them.
The `bench_defaults.py` variant has the recorded final 6144/256 values in its metadata.

Publication changes to the copied scripts:

1. Read `STRATA_BASE_URL`, defaulting to `http://127.0.0.1:8080`.
2. Save under ignored `benchmarks/new-runs/<comparison>/` by default, or `STRATA_BENCH_OUTPUT_DIR`.

Prompt text, API request fields and metric selection are otherwise unchanged. No generated response
text, user chat history, raw runtime logs, model weights or authentication information is included.

The multi-model repository migration moved these scripts one directory deeper; their default output path was adjusted to remain under ignored `benchmarks/new-runs/`. Recorded timing JSON is unchanged.
