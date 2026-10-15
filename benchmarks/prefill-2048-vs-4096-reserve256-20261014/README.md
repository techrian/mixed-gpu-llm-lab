# Strata prefill 2048 vs 4096, reserve 256 MiB

Date: 2026-10-14 (Asia/Seoul)

## Method

Compared two runs at each prefill value, keeping `--vram-reserve-mib 256` unchanged. Every request used the same 61,679-token synthetic prompt and 512-token generation limit, with 0 cached/reused prompt tokens. Other model, context, KV, GPU split/order, and speculative decoding settings were unchanged. Timings came from Strata `/metrics`.

The 512-token output limit was reached while the model was producing internal reasoning tokens, so this measures raw token generation throughput rather than answer quality.

## Results

| Prefill | Prompt time (runs; mean) | Prompt throughput (runs; mean) | Decode rate (runs; mean) | Total request (runs; mean) |
|---|---:|---:|---:|---:|
| 2048 | 37.202, 36.962; **37.082 s** | 1,657.9, 1,668.7; **1,663.3 tok/s** | 71.2, 74.0; **72.6 tok/s** | 44.443, 43.919; **44.181 s** |
| 4096 | 29.915, 29.785; **29.850 s** | 2,061.8, 2,070.8; **2,066.3 tok/s** | 73.8, 73.5; **73.7 tok/s** | 36.900, 36.789; **36.845 s** |

At 4096, prompt throughput rose about **24.2%**, prompt time fell about **19.5%**, and total request time fell about **16.6%**. Decode rate was nearly unchanged (+1.4%).

## VRAM and cache

4096 started successfully and the startup log confirms `ring 96 slots at chunk 4096`. Both settings reported 24,576 expert slots and 76,800 MiB of expert cache. Free VRAM on the primary CUDA device was 1,033 MiB at 2048 and 1,027 MiB at 4096. The reported prompt arena grew from 3,655 MiB to 5,951 MiB.

At 4096, CUDA2 owns prompt buffers of 1.94 GiB; CUDA0, CUDA1, and CUDA3 each lend about 1.94 GiB from their cache slots. Those borrowed slots keep their experts in RAM. CUDA ordinals follow configured order `[2,0,1,3]`.

## Files

- `D001.json`, `D002.json`: prefill 4096 runs
- `baseline-2048-256-001.json`, `baseline-2048-256-002.json`: prefill 2048 runs
- `config.before.template.json`: configuration before this change
- `bench.py`: repeatable API benchmark (`bench.py LABEL PREFILL RESERVE_MIB`)

## Repository export

Private paths and bind addresses in configuration snapshots were replaced with template variables. Benchmark scripts now read `STRATA_BASE_URL` (default `http://127.0.0.1:8080`) and save new results under ignored `benchmarks/new-runs/`, or `STRATA_BENCH_OUTPUT_DIR`. These edits do not change the synthetic prompt, API payload, or recorded timing JSON. No new inference was run during export.
