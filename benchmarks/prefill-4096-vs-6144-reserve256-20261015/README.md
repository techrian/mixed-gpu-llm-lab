# Strata prefill 4096 vs 6144, reserve 256 MiB

Date: 2026-10-15 (Asia/Seoul)

## Method

Compared two runs at each prefill value, keeping `--vram-reserve-mib 256` constant. Each request used the same 61,679-token synthetic prompt and 512-token generation limit, with zero cached/reused prompt tokens. The model, 256K context, FP16 KV cache, GPU split/order, and speculative decoding settings were unchanged. Timings came from Strata `/metrics`.

The 512-token output limit was reached while the model was producing internal reasoning tokens, so this measures raw token generation throughput rather than answer quality.

## Results

| Prefill | Prompt time (runs; mean) | Prompt throughput (runs; mean) | Decode rate (runs; mean) | Total request (runs; mean) |
|---|---:|---:|---:|---:|
| 4096 | 29.915, 29.785; **29.850 s** | 2,061.8, 2,070.8; **2,066.3 tok/s** | 73.8, 73.5; **73.7 tok/s** | 36.900, 36.789; **36.845 s** |
| 6144 | 28.146, 27.866; **28.006 s** | 2,191.0, 2,213.0; **2,202.4 tok/s** | 72.4, 69.1; **70.8 tok/s** | 35.265, 35.320; **35.293 s** |

At 6144, prompt throughput rose about **6.6%**, prompt time fell about **6.2%**, and total request time fell about **4.2%**. Decode rate was about **3.9% lower** across these two runs.

## 6144 repeat

Repeated the 6144 setting twice with the same 61,679-token prompt shape and 512-token output limit. Both requests read the full prompt with no reuse and reached the 512-token limit.

| Run | Prompt time | Prompt throughput | Decode rate | Total request | Drafts accepted / offered |
|---|---:|---:|---:|---:|---:|
| F003 | 27.771 s | 2,221.0 tok/s | 72.2 tok/s | 34.900 s | 232 / 315 |
| F004 | 27.861 s | 2,213.8 tok/s | 72.6 tok/s | 34.940 s | 248 / 351 |
| **Mean** | **27.816 s** | **2,217.4 tok/s** | **72.4 tok/s** | **34.920 s** | **480 / 666** |

The repeat's 72.4 tok/s decode mean is above the first 6144 pair's 70.8 tok/s. Across all four 6144 runs, decode averages **71.6 tok/s**, so the original 3.9% drop versus 4096 is not stable; the four-run average is about **2.8% lower** than 4096's 73.7 tok/s. Both 6144 repeats completed exactly 512 tokens.

## 6144 with API sampling defaults

After setting the server config to `temperature=1.0`, `top_p=0.95`, `top_k=20`, `min_p=0.0`, sent two requests with all four sampling fields omitted. Both read 61,679 prompt tokens with no reuse and reached the 512-token output limit.

| Run | Prompt time | Prompt throughput | Decode rate | Total request | Drafts accepted / offered |
|---|---:|---:|---:|---:|---:|
| F005 | 28.058 s | 2,198.3 tok/s | 68.1 tok/s | 35.628 s | 229 / 376 |
| F006 | 27.850 s | 2,214.7 tok/s | 72.7 tok/s | 34.933 s | 254 / 361 |
| **Mean** | **27.954 s** | **2,206.5 tok/s** | **70.4 tok/s** | **35.281 s** | **483 / 737** |

## 6144 with Strata service swap disabled

Applied `MemorySwapMax=0` to the Strata service cgroup and restarted the model so pages swapped by the old process were released. The service cgroup reported `memory.swap.max=0` and `memory.swap.current=0` before and after the three requests. The host's swap remains enabled for other processes. Requests omitted the sampling fields and used the same configured defaults as the previous section.

| Run | Prompt time | Prompt throughput | Decode rate | Total request | Drafts accepted / offered |
|---|---:|---:|---:|---:|---:|
| F007 | 28.060 s | 2,198.1 tok/s | 68.1 tok/s | 35.622 s | 225 / 367 |
| F008 | 27.881 s | 2,212.2 tok/s | 68.4 tok/s | 35.405 s | 237 / 380 |
| F009 | 27.879 s | 2,212.4 tok/s | 75.1 tok/s | 34.735 s | 271 / 383 |
| **Mean** | **27.940 s** | **2,207.6 tok/s** | **70.5 tok/s** | **35.254 s** | **733 / 1,130** |

Compared with the two preceding swap-allowed runs using the same API defaults (70.4 tok/s decode mean), the three no-swap runs averaged 70.5 tok/s. This small sample shows no measurable speed change; the per-run decode spread was 68.1–75.1 tok/s.

### Repeat no-swap set

Repeated after restarting Strata with `MemorySwapMax=0`. Each request used 61,679 prompt tokens, generated 512 tokens, reused no cached prompt tokens, and omitted sampling fields so the configured API defaults applied. The Strata cgroup remained capped at zero swap; after the last request, both cgroup `memory.swap.current` and engine `VmSwap` were zero.

| Run | Prompt time | Prompt throughput | Decode rate | Total request | Drafts accepted / offered |
|---|---:|---:|---:|---:|---:|
| F010 | 27.982 s | 2,204.3 tok/s | 72.3 tok/s | 35.110 s | 244 / 347 |
| F011 | 27.829 s | 2,216.4 tok/s | 66.2 tok/s | 35.598 s | 219 / 365 |
| F012 | 27.840 s | 2,215.5 tok/s | 70.6 tok/s | 35.132 s | 240 / 366 |
| **Mean** | **27.883 s** | **2,212.0 tok/s** | **69.7 tok/s** | **35.280 s** | **703 / 1,078** |

## VRAM and cache

Startup confirmed the requested 6144-token chunk (`ring 96 slots at chunk 6144`). Both settings reported 24,576 expert slots. Free VRAM on the primary CUDA device was 1,027 MiB at 4096 and 1,021 MiB at 6144. The reported prompt arena grew from 5,951 MiB to 8,245 MiB.

At 6144, CUDA2 owns 2.68 GiB of prompt buffers; CUDA0, CUDA1, and CUDA3 each lend about 2.68 GiB from their cache slots. The 2,648 borrowed slots keep their experts in RAM (8.05 GiB total resident expert RAM for this path).

## Files

- `F001.json`, `F002.json`: prefill 6144 runs
- `F003.json`, `F004.json`: repeated prefill 6144 runs
- `F005.json`, `F006.json`: prefill 6144 with API sampling defaults omitted from requests
- `F007.json`–`F009.json`: prefill 6144 with the Strata service cgroup swap limit set to zero
- `F010.json`–`F012.json`: repeated prefill 6144 runs after restarting Strata with the swap limit set to zero
- `baseline-4096-256-001.json`, `baseline-4096-256-002.json`: prefill 4096 runs
- `config.before.template.json`: configuration before this change
- `bench.py`: repeatable API benchmark (`bench.py LABEL PREFILL RESERVE_MIB`)
- `bench_defaults.py`: API benchmark that omits sampling fields to exercise the configured defaults

## Repository export

Private paths and bind addresses in configuration snapshots were replaced with template variables. Benchmark scripts now read `STRATA_BASE_URL` (default `http://127.0.0.1:8080`) and save new results under ignored `benchmarks/new-runs/`, or `STRATA_BENCH_OUTPUT_DIR`. These edits do not change the synthetic prompt, API payload, or recorded timing JSON. No new inference was run during export.
