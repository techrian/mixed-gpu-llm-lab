# GLM5.3 Flash Maya-M on mixed NVIDIA GPUs

Recorded working deployment on October 16, 2026. The engine is [Project Maya](https://github.com/mw00/project-maya), version 1.1.11,
commit `362671aee624183ce3630fb1fd4c1aa431a5a451`. Its tracked source tree was clean.
The model is [peasantsmith/GLM-5.3-Flash-Maya-GGUF](https://huggingface.co/peasantsmith/GLM-5.3-Flash-Maya-GGUF), **Maya-M**,
three shards with IQ2_S expert tensors and mixed higher-precision tensors. Files total 116,003,563,168 bytes.

## Settings and observed placement

| Setting | Value |
| --- | --- |
| Context | 262144 |
| Prefill | 2048 |
| KV | FP16; `--kv-streaming on`, 32768 resident positions |
| Physical GPU order | `[2,0,1,3]`: V100, RTX3090, RTX3060, V100 |
| Layer split | Automatic; observed half-open ranges `[0,16)`, `[16,27)`, `[27,31)`, `[31,45)` |
| MTP | Enabled; draft block 45 and output head on physical GPU 3 |
| Vision | F16 mmproj, resident on physical GPU 2; wrapper sets its own physical CUDA visibility |
| Expert tiers | 10102 VRAM slots including slack, 82.4 GiB reported; 32.3 GiB pinned RAM tier reported |
| RAM policy | `STRATA_GLM_RAM_GB=48`, `STRATA_GLM_RAM_RESIDENT=1`; disk evictions off |
| CPU/PCIe decision | Runtime reported 5 CPU threads, PCIe share 0.00; RAM experts use the CPU lane |
| API defaults | temperature 1.0, top_p 0.95, top_k 20, min_p 0.0, reasoning effort high |
| Swap | Server cgroup `MemorySwapMax=0` |

Slot totals contain allocator slack and MTP allocation. Dividing slots by model experts is not a precise expert-residency percentage.
The [runtime snapshot](snapshots/runtime.json) records the engine's actual map and units. Automatic placement can change with available memory.
The [main comparison](../../README.md) and [agent report](../../benchmarks/agent-comparison/2026-10-16/README.md) contain the measured outcomes.

## Why prefill 2048 and this GPU order

The [published tuning history](../../benchmarks/throughput/glm-maya-m-20261016/README.md) includes 21 unique throughput requests, including the later 1024 follow-up.
With the earlier `[0,2,3,1]` order, two requests per prefill value gave mean total times of 78.108 s at 2048,
80.312 s at 4096, 85.993 s at 6144 and 93.361 s at 8192. The shortest mean time and highest mean prompt throughput selected 2048.

Later order trials retained `[2,0,1,3]` based on its mean decode rate, 45.33 tok/s versus 44.65 for `[0,2,1,3]`.
Its mean total time was slightly longer, 74.979 s versus 73.925 s. Putting the RTX 3090 last with MTP, `[2,3,1,0]`,
reduced mean decode rate to 39.87 tok/s and was reverted. The raw GPU maps show that base-layer and expert allocations also changed.

These small sequential samples reflect the mixed PCIe topology and a roughly 59.4K-token synthetic prompt with 512 generated tokens.
The prefill sweep preceded the order trials; every prefill/order combination and agent-task outcome was not measured.
The report distinguishes each selection criterion and retains the unsuccessful attempt alongside the chosen configuration.

A later [three-request 1024 follow-up](../../benchmarks/throughput/glm-maya-m-20261016/followup-prefill1024-final-order/README.md), at the final `[2,0,1,3]` order,
averaged 830.30 prompt tok/s, 46.17 decode tok/s and 83.246 s total. The historical same-order 2048 baseline averaged 937.97,
45.33 and 74.979 respectively. The slightly higher decode mean at 1024 accompanied a longer total time; the profile was restored to 2048.
This follow-up added exactly three inference requests and did not repeat the agent-quality suite or create a fresh 2048 baseline.

## Prepare a separate installation

Use CUDA 12.8 for the V100 and RTX30 combination. The helper records the relevant build flags; it does not run a fresh benchmark or change an existing service.

```bash
git clone https://github.com/mw00/project-maya.git "$HOME/project-maya"
git -C "$HOME/project-maya" checkout --detach 362671aee624183ce3630fb1fd4c1aa431a5a451
python3 -m venv "$HOME/project-maya/.venv"
"$HOME/project-maya/.venv/bin/python" -m pip install \
  numpy jinja2 regex pyyaml tqdm requests cmake ninja pillow psutil
# From this profile directory:
bash scripts/build.sh "$HOME/project-maya"
```

The observed main build cache used `CMAKE_CUDA_ARCHITECTURES=native`; the helper explicitly targets `70;86` for these two architectures.
The vision build used `70;86`. The dependency pin is llama.cpp `3cf03257f219afbe7334045ff7c6a06ac68c627d`.
See [build metadata](snapshots/build.json). The exported helper has not been exercised as a full clean installation.

## Model and pack

Download these Maya-M shards from the model repository into one directory. The pinned Maya setup knows their published hashes;
the recorded local filenames and sizes are in [model-files.json](snapshots/model-files.json).

```text
GLM-5.3-Flash-Maya-M-IQ2_S-00001-of-00003.gguf
GLM-5.3-Flash-Maya-M-IQ2_S-00002-of-00003.gguf
GLM-5.3-Flash-Maya-M-IQ2_S-00003-of-00003.gguf
```

Keep `pack/` next to the shards: the GLM engine locates expert tensors relative to that directory.
The equivalent pack command used by the pinned installer is:

```bash
cd "$HOME/project-maya"
export STRATA_GGUF_PY="$PWD/third_party/llama.cpp/gguf-py"
model_dir="$HOME/Maya-data/models/Maya-M"
.venv/bin/python tools/iq_pack.py \
  --gguf "$model_dir/GLM-5.3-Flash-Maya-M-IQ2_S-00001-of-00003.gguf" \
  --out "$model_dir/pack" --compat-bf16
```

Vision also needs `vision/mmproj-GLM-5.3-Flash-F16.gguf` and `vision/GLM-5.3-Flash-vocab.gguf` from the Maya setup's vision preparation.
The recorded configuration uses the upstream learned `data/expert-profile-glm.bin`. MTP is in the GLM model; this profile does not use a separate Qwen draft pack.
For complete model/vision download preparation, refer to the [pinned Maya setup](https://github.com/mw00/project-maya/blob/362671aee624183ce3630fb1fd4c1aa431a5a451/docs/SETUP.md).

## Render and start

From this profile directory:

```bash
cp config/paths.example.json config/paths.local.json
# Edit installation, model and CUDA paths; verify physical GPU indices.
python3 scripts/render_config.py
python3 scripts/run.py
```

The renderer creates `runtime/maya.json` and an executable vision wrapper. The example binds to `127.0.0.1:8080` without an API key.
Run one model at a time on this hardware; the two profile examples share the same API port and GPUs.
For swap blocking, adapt the optional [user service](systemd/glm5.3_maya_strata.service) to your clone location.
The measured installation used a transient user unit; exporting this profile does not replace it or enable boot startup.

Model weights, packs, learned profile binaries, vision files and engine binaries are not included.
Project Maya's [MIT license](../../third_party/Project-Maya-LICENSE) and [source attribution](../../THIRD_PARTY_NOTICES.md) are preserved.
