# Installation and restoration

These instructions target an NVIDIA PC with Ubuntu 24.04 and CUDA 12.8. They record the working
configuration and dependency sources; the complete procedure has not been rerun on a fresh PC.
Changing the model, GPUs, or PCIe connections can change memory usage and performance.

## 1. Source and Python environment

Required tools are Git, Python 3.12 with venv support, a C/C++ compiler, and CUDA 12.8.
The recorded PC used NVIDIA driver `580.178.04` and GCC 13. Install any missing system tools
through the operating system's package manager.

```bash
git clone https://github.com/Niko1221/Strata.git "$HOME/Strata"
git -C "$HOME/Strata" checkout --detach a0116b2782a5b82622358c04a06496485d12b2d6
python3 -m venv "$HOME/Strata/.venv"
"$HOME/Strata/.venv/bin/python" -m pip install -r "$HOME/Strata/requirements.txt"
```

Observed Python package versions are listed in `snapshots/python-packages.txt`.
Also refer to the pinned upstream
[AI_SETUP.md](https://github.com/Niko1221/Strata/blob/a0116b2782a5b82622358c04a06496485d12b2d6/docs/AI_SETUP.md) and
[OLDER_GPUS.md](https://github.com/Niko1221/Strata/blob/a0116b2782a5b82622358c04a06496485d12b2d6/docs/OLDER_GPUS.md).

## 2. Build the CUDA engine and vision encoder

From this Qwen profile directory:

```bash
bash scripts/build.sh "$HOME/Strata"
```

V100 uses `sm70`; the RTX 3090 and 3060 use `sm86`. This build uses CUDA 12.8,
`STRATA_EXPERIMENTAL_SM60=ON`, and `CMAKE_CUDA_ARCHITECTURES=70;86`.
Upstream classifies the V100 path as experimental. CUDA 13 cannot replace CUDA 12.8 for this build.

The helper obtains upstream's pinned llama.cpp source and places the engine and vision executable
in `engine-cuda12/`. Upstream reuses an existing llama.cpp source directory, so use a fresh,
separate Strata checkout for reproduction. Set `STRATA_CUDA_ROOT` or `STRATA_BUILD_JOBS` to change
the CUDA path or build parallelism. This script builds without running the upstream test suite.

## 3. Model files

Place these files from
[orcarouter/Qwen3.8-Flash-Next-Uncensored-GGUF](https://huggingface.co/orcarouter/Qwen3.8-Flash-Next-Uncensored-GGUF)
in the same directory. This repository does not download them automatically.

| File | Recorded local size in bytes |
| --- | ---: |
| `Qwen3.8-Flash-Next-Uncensored-Q4_K_M-00001-of-00003.gguf` | 44598509600 |
| `Qwen3.8-Flash-Next-Uncensored-Q4_K_M-00002-of-00003.gguf` | 44693535520 |
| `Qwen3.8-Flash-Next-Uncensored-Q4_K_M-00003-of-00003.gguf` | 29858677824 |
| `mmproj-Qwen3.8-Flash-Next-Uncensored-F16.gguf` | 907543296 |

The three GGUF shards total approximately 119.15 GB. Their filenames and sizes were recorded;
full local SHA-256 hashes and the original Hugging Face revision were not recorded. Matching
filenames alone do not establish identical model bytes.

The recorded `--mtp` directory is `Strata-data/mtp/rt`, prepared from the original Qwen checkpoint
in the next step. The separate local `Qwen3.8-Flash-Next-Uncensored-MTP-draft.gguf` file is unused
by this configuration.

## 4. Prepare the native pack and MTP

The following paths are examples. Reuse an existing valid pack and MTP directory when available.
Fetching MTP downloads approximately 5 GB from the original Qwen checkpoint.

```bash
cd "$HOME/Strata"
export STRATA_GGUF_PY="$PWD/third_party/llama.cpp/gguf-py"
model_file="$HOME/llm/gguf/qwen-flashnext-uncensored/Qwen3.8-Flash-Next-Uncensored-Q4_K_M-00001-of-00003.gguf"
data_dir="$HOME/Strata-data"
.venv/bin/python tools/iq_pack.py --gguf "$model_file" \
  --out "$data_dir/packs/orca-q4_k_m" --compat-bf16
.venv/bin/python tools/mtp_fetch.py fetch --out "$data_dir/mtp"
.venv/bin/python tools/mtp_pack.py --src "$data_dir/mtp" --experts q2_0 \
  --out "$data_dir/mtp/mtp-q2_0.gguf"
.venv/bin/python tools/mtp_rt.py --gguf "$data_dir/mtp/mtp-q2_0.gguf" \
  --out "$data_dir/mtp/rt"
cp data/draft_vocab.bin "$data_dir/mtp/rt/draft_vocab.bin"
```

`--compat-bf16` rounds small non-native projections to BF16 while preserving the stored expert
and PLE table bytes. The recorded pack creation output is in `snapshots/pack-build.txt`.
The upstream MTP checkpoint revision is recorded in `snapshots/environment.json`.

## 5. Configure and start

Return to this setup repository's root. Copy `config/paths.example.json` to
`config/paths.local.json`, then edit the actual paths, `host`, and `port`. Resolve any existing
server using the same port before starting.

```bash
python3 scripts/render_config.py
python3 scripts/run.py
```

The generated configuration is `runtime/strata.json`; the engine log is `runtime/strata.log`.
The default host is `127.0.0.1`, with no API key. Once loaded, `/health` should report
`service: strata`, `loaded: true`, `images: true`, and `max_context: 262144`.
The default OpenAI-compatible base URL is `http://127.0.0.1:8080/v1`.

The recorded PC used `MemorySwapMax=0` on a **transient user `strata.service`**. A transient
service does not register automatic startup after reboot. The persistent service example below
is optional; exporting this repository did not change the existing service.

## 6. Optional persistent user service with swap blocked

Stop or otherwise resolve an existing Strata or other model server using the same port first.
Check that the paths in `systemd/qwen3.8_flash_next_strata.service` match this repository's clone location.

```bash
mkdir -p "$HOME/.config/systemd/user"
cp systemd/qwen3.8_flash_next_strata.service "$HOME/.config/systemd/user/qwen3.8_flash_next_strata.service"
systemctl --user daemon-reload
systemctl --user enable --now qwen3.8_flash_next_strata.service
systemctl --user show qwen3.8_flash_next_strata.service -p ActiveState -p MemorySwapMax -p MemorySwapCurrent
```

`MemorySwapMax=0` applies to this service's Python server, engine, and vision child processes.
System-wide swap remains enabled. Starting before login may require a separate user linger setting.
Physical RAM for PLE and the expert RAM complement is still required.

## 7. Existing benchmark scripts

Each comparison directory under `benchmarks/` contains the scripts used for that measurement.
Their base URL now comes from `STRATA_BASE_URL`. New output is written under
`benchmarks/new-runs/` to keep it separate from the recorded results.

```bash
STRATA_BASE_URL=http://127.0.0.1:8080 \
  python3 ../../benchmarks/throughput/prefill-4096-vs-6144-reserve256-20261015/bench_defaults.py G001
```

The scripts do not change the server's prefill setting. After changing settings, restart the
server yourself and record the matching conditions. The defaults script records the final
6144/256 metadata, so use it with that configuration or update its metadata first.
Because scripts select the latest request from `/metrics`, avoid other API traffic during a run.
These benchmarks were not rerun while exporting this repository.
