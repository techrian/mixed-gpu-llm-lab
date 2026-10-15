# Strata prefill 4096 vs 8192, reserve 256 MiB

Date: 2026-10-15 (Asia/Seoul)

## Method

Compared two runs at each prefill value, holding `--vram-reserve-mib 256` constant. Each request used the same 61,679-token synthetic prompt and 512-token generation limit, with zero cached/reused tokens. Other model, context, KV, GPU split/order, and speculative decoding settings were unchanged.

The 512-token output limit was reached while the model was still producing internal reasoning tokens, so this measures raw generation throughput rather than answer quality.

## Results

| Prefill | Prompt time (mean) | Prompt throughput (mean) | Decode rate (mean) | Total request (mean) |
|---|---:|---:|---:|---:|
| 4096 | 29.850 s | 2066.3 tok/s | 73.7 tok/s | 36.844 s |
| 8192 | 31.321 s | 1969.3 tok/s | 69.8 tok/s | 38.707 s |

At 8192, prompt throughput changed by -4.7%, prompt time by +4.9%, decode rate by -5.3%, and total request time by +5.1%.

## Memory

Both settings reported 24,576 expert slots. Startup confirmed the requested 8192-token chunk (`ring 96 slots at chunk 8192`), but it required about 3.43 GiB of prompt buffers per GPU stage, with 4,517 slots borrowed and backed by 13.73 GiB of resident RAM experts. The prior 4096 run borrowed 1,915 slots and reported a 5,951 MiB prompt arena; 8192 reported a 14,062 MiB arena.

## Files

- `E001.json`, `E002.json`: prefill 8192 runs
- `baseline-4096-256-001.json`, `baseline-4096-256-002.json`: prefill 4096 runs
- `config.before.template.json`: configuration before this test
- `bench.py`: repeatable API benchmark

## Repository export

Private paths and bind addresses in configuration snapshots were replaced with template variables. Benchmark scripts now read `STRATA_BASE_URL` (default `http://127.0.0.1:8080`) and save new results under ignored `benchmarks/new-runs/`, or `STRATA_BENCH_OUTPUT_DIR`. These edits do not change the synthetic prompt, API payload, or recorded timing JSON. No new inference was run during export.
