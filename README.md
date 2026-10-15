# Strata Qwen3.8 mixed GPU setup

Configuration and recorded benchmarks for **Qwen3.8-Flash-Next-Uncensored Q4_K_M** on an
RTX 3090 24 GiB, RTX 3060 12 GiB, and two V100 32 GiB GPUs. This snapshot was taken from
the running setup on October 15, 2026.

The inference engine is [Niko1221/Strata](https://github.com/Niko1221/Strata).
This repository contains configuration templates, helper scripts, build and restoration instructions,
and existing benchmark results. The upstream inference source is unmodified.

## Recorded configuration

| Setting | Value |
| --- | --- |
| Model | `orcarouter/Qwen3.8-Flash-Next-Uncensored-GGUF`, `Q4_K_M`, 3 shards |
| Strata | `0.1.43.1`, commit `a0116b2782a5b82622358c04a06496485d12b2d6` |
| Context | `262144` tokens (256 Ki tokens) |
| KV cache | `fp16`, placed on GPUs in the recorded setup |
| Prefill chunk | `6144` |
| VRAM reserve | `256 MiB` configured per GPU |
| Expert cache | `auto`; recorded total `24576` slots / `76800 MiB` |
| PLE | `--ple-io ram`, locked in system RAM |
| Expert RAM budget | `--resident-budget-gib 16` |
| Speculative decoding | `--spec 4 --spec-min-p 0.5`, upstream Qwen MTP `q2_0`, CJK draft vocabulary |
| Vision | F16 mmproj on **physical GPU 2 (V100)** |
| API sampling defaults | temperature `1.0`, top_p `0.95`, top_k `20`, min_p `0.0` |
| Process swap | systemd cgroup `MemorySwapMax=0` |

The `24576` slots cover all experts. During prefill, some expert slots lend their VRAM to temporary
buffers and the corresponding experts are backed by RAM copies. All experts therefore do not remain
in VRAM simultaneously throughout prefill. The recorded 6144 startup reported `2648` borrowed slots
and an `8.05 GiB` page-locked RAM complement.

## GPU numbering and layer placement

`gpu: [2, 0, 1, 3]`, `gpu_order: as_given`, `layer_split: 16,29,33`.
Layer indices start at zero.

| Physical nvidia-smi index | GPU | VRAM | Engine CUDA index | Layers |
| --- | --- | ---: | --- | --- |
| 0 | RTX 3090 | 24 GiB | CUDA1 | 16–28 (13 layers) |
| 1 | RTX 3060 | 12 GiB | CUDA2 | 29–32 (4 layers) |
| 2 | V100 / Tesla PG500-216 | 32 GiB | CUDA0 | 0–15 (16 layers) |
| 3 | V100 / Tesla PG500-216 | 32 GiB | CUDA3 | 33–47 (15 layers), output head / MTP |

The vision process interprets `vision.cuda_device: 2` as **physical GPU 2**. The main engine's CUDA2
is the RTX 3060 because its device order is remapped. On another PC, check `nvidia-smi` and adjust
`gpu` and `vision.cuda_device` in the template. The RTX 3060 uses PCIe 4.0 x1 according to the
owner's hardware report. This layer placement has not been compared against every alternative.

## Restore configuration with an existing installation

```bash
git clone https://github.com/techrian/strata-qwen38-mixed-gpu-setup.git
cd strata-qwen38-mixed-gpu-setup
cp config/paths.example.json config/paths.local.json
# Edit Strata, Strata-data, model and CUDA paths, plus the bind address.
python3 scripts/render_config.py
# Run after stopping any previous server that uses the same port.
python3 scripts/run.py
```

`config/paths.local.json` and the generated `runtime/` directory are ignored by Git.
The example binds to `127.0.0.1:8080` without an API key. Set the desired address in the local path
file; the launcher uses the configured host and does not add an API key.

This snapshot comes from a working server. Exporting it did not restart the model or run new
performance measurements. See the [reproduction guide](docs/REPRODUCE.md) for installation on a
new PC. The complete installation and server launch through the new helper scripts have not been
exercised separately.

## Recorded performance

Measured on a Ryzen 7 9700X, 64 GB class RAM (about 60.5 GiB visible to Linux), Ubuntu 24.04,
and 100 GiB total VRAM. Requests used the same 61,679-token synthetic prompt shape, a 512-token
output limit, and zero prompt cache reuse.

| Configuration | Runs | Mean prompt throughput | Mean decode rate | Mean request time |
| --- | ---: | ---: | ---: | ---: |
| Prefill 512 / reserve 700 | 2 | 893.0 tok/s | 71.3 tok/s | 76.297 s |
| Prefill 1024 / reserve 700 | 2 | 1258.1 tok/s | 71.5 tok/s | 56.245 s |
| Prefill 2048 / reserve 256 | 2 | 1663.3 tok/s | 72.6 tok/s | 44.181 s |
| Prefill 4096 / reserve 256 | 2 | 2066.3 tok/s | 73.7 tok/s | 36.845 s |
| Prefill 6144 / reserve 256, initial | 2 | 2202.4 tok/s | 70.8 tok/s | 35.293 s |
| Prefill 8192 / reserve 256 | 2 | 1969.3 tok/s | 69.8 tok/s | 38.707 s |
| **Final 6144, API defaults, swap blocked (F010–F012)** | **3** | **2212.0 tok/s** | **69.7 tok/s** | **35.280 s** |

The initial comparisons specified temperature `0.7` in the request; the final runs omitted sampling
fields and used the defaults above. The 1024-to-2048 comparison also changed the VRAM reserve.
These rows do not constitute one experiment with all other conditions held constant.
The output limit was reached during internal reasoning, so these are throughput measurements,
not answer-quality results. Values are derived from the existing JSON; see
[measurement files and conditions](benchmarks/README.md).

## Contents

- `config/`: recorded engine and vision settings with machine paths separated out.
- `scripts/`: configuration rendering, server launch, and CUDA build helpers.
- `systemd/`: optional user service example with swap blocked.
- `snapshots/`: environment, build metadata, and selected startup lines with private details removed.
- `benchmarks/`: existing October 14–15 JSON, scripts, and comparison notes.

Model weights, MTP artifacts, prepared packs, engine binaries, virtual environments, and GitHub
credentials are excluded. Model files remain subject to their distributor's license.
Upstream attribution and license information are in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
