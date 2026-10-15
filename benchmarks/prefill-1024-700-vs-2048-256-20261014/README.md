# Strata prefill and VRAM reserve comparison

Date: 2026-10-14 (Asia/Seoul)

## Method

Compared the prior 1024/700 run with the requested combined 2048/256 configuration. Each setting was measured twice using the same 61,679-token synthetic prompt and a 512-token generation limit. Each request reported 0 cached/reused tokens. Model, 256K context, FP16 KV cache, GPU order/split, and speculative decoding settings stayed the same. Timings came from Strata `/metrics`.

The 512-token generation limit was reached while the model was still producing internal reasoning tokens, so this measures token generation throughput rather than answer quality.

## Results

| Prefill / reserve | Prompt time (runs; mean) | Prompt throughput (runs; mean) | Decode rate (runs; mean) | Total request (runs; mean) |
|---|---:|---:|---:|---:|
| 1024 / 700 MiB | 49.061, 48.988; **49.025 s** | 1,257.2, 1,259.1; **1,258.1 tok/s** | 73.1, 69.8; **71.5 tok/s** | 56.118, 56.371; **56.245 s** |
| 2048 / 256 MiB | 37.202, 36.962; **37.082 s** | 1,657.9, 1,668.7; **1,663.3 tok/s** | 71.2, 74.0; **72.6 tok/s** | 44.443, 43.919; **44.181 s** |

The combined change increased prompt throughput about **32.2%**, reduced prompt time about **24.4%**, and reduced total request time about **21.5%**. Decode rate changed by about **+1.6%**, which is small across two runs.

Because both prefill and VRAM reserve changed together, this comparison cannot separate the effect of `--prefill 2048` from the effect of `--vram-reserve-mib 256`.

## VRAM and cache

Both configurations reported 24,576 expert slots and 76,800 MiB expert cache. Free VRAM on the primary CUDA device was 1,037 MiB at 1024/700 and 1,033 MiB at 2048/256. `/metrics` reported the prompt arena increasing from 1,670 MiB to 3,655 MiB.

At 2048, the startup log shows a 1.19 GiB prompt buffer owned by CUDA2 and borrowed buffers of about 1.19 GiB each from CUDA0, CUDA1, and CUDA3. The borrowed slots keep their experts in RAM. CUDA ordinals follow GPU order `[2,0,1,3]`: CUDA0 is physical GPU2 (V100), CUDA1 is physical GPU0 (RTX 3090), CUDA2 is physical GPU1 (RTX 3060), and CUDA3 is physical GPU3 (V100).

## Files

- `C001.json`, `C002.json`: 2048/256 runs
- `baseline-1024-700-001.json`, `baseline-1024-700-002.json`: prior 1024/700 runs
- `config.before.template.json`: configuration before this change
- `bench.py`: repeatable API benchmark (`bench.py LABEL PREFILL RESERVE_MIB`)

## Repository export

Private paths and bind addresses in configuration snapshots were replaced with template variables. Benchmark scripts now read `STRATA_BASE_URL` (default `http://127.0.0.1:8080`) and save new results under ignored `benchmarks/new-runs/`, or `STRATA_BENCH_OUTPUT_DIR`. These edits do not change the synthetic prompt, API payload, or recorded timing JSON. No new inference was run during export.
