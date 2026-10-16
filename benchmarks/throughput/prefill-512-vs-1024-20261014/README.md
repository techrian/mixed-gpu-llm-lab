# Strata prefill 512 vs 1024 benchmark

Date: 2026-10-14 (Asia/Seoul)

## Method

Used the same synthetic prompt (61,679 tokens) and a 512-token generation limit for two requests at each setting. Each prompt had a distinct leading run label to prevent prompt-prefix reuse; all four requests report 0 cached/reused tokens. The model, 256K context, FP16 KV cache, GPU order/split, and speculative decoding settings stayed the same. Measurements are from Strata `/metrics`.

The 512-token generation limit was reached while the model was still producing internal reasoning tokens, so the benchmark measures token generation throughput rather than answer quality.

## Results

| Prefill | Prompt time (runs; mean) | Prompt throughput (runs; mean) | Decode rate (runs; mean) | Total request (runs; mean) |
|---|---:|---:|---:|---:|
| 512 | 69.063, 69.080; **69.071 s** | 893.1, 892.9; **893.0 tok/s** | 72.0, 70.6; **71.3 tok/s** | 76.220, 76.374; **76.297 s** |
| 1024 | 49.061, 48.988; **49.025 s** | 1,257.2, 1,259.1; **1,258.1 tok/s** | 73.1, 69.8; **71.5 tok/s** | 56.118, 56.371; **56.245 s** |

At 1024, prompt throughput rose about **40.9%** and prompt time fell about **29.0%**. Decode rate was effectively unchanged (**+0.2%** across these two-run averages). Total request time fell about **26.3%**, mostly from the shorter prefill.

## VRAM and cache

Both settings reported 24,576 expert slots (76,800 MiB cache) and about 1.0 GiB free VRAM on the primary CUDA device after loading. The prompt arena reported by `/metrics` increased from 756 MiB at 512 to 1,670 MiB at 1024.

Startup logs show the per-stage prompt buffers growing from 0.37 GiB to about 0.81 GiB on CUDA2 and CUDA3. Borrowed prompt buffers grew from about 0.37 GiB to 0.81–0.82 GiB on CUDA0 and CUDA1; the borrowed slots keep their experts in RAM. The reported total expert-slot count did not change.

CUDA ordinals follow the configured GPU order `[2,0,1,3]`: CUDA0 is physical GPU2 (V100), CUDA1 is physical GPU0 (RTX 3090), CUDA2 is physical GPU1 (RTX 3060), and CUDA3 is physical GPU3 (V100).

## Files

- `A001.json`, `A002.json`: prefill 512 runs
- `B001.json`, `B002.json`: prefill 1024 runs
- `config.before.template.json`: pre-change configuration with private paths and host replaced; raw runtime log omitted
- `bench.py`: repeatable API benchmark

## Repository export

Private paths and bind addresses in configuration snapshots were replaced with template variables. Benchmark scripts now read `STRATA_BASE_URL` (default `http://127.0.0.1:8080`) and save new results under ignored `benchmarks/new-runs/`, or `STRATA_BENCH_OUTPUT_DIR`. These edits do not change the synthetic prompt, API payload, or recorded timing JSON. No new inference was run during export.
