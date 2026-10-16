#!/usr/bin/env bash
# Build the recorded upstream commit for V100 (sm70) and RTX 30 (sm86).
set -euo pipefail
strata_dir=$(realpath "${1:?Usage: build.sh /path/to/Strata}")
cuda_root=${STRATA_CUDA_ROOT:-/usr/local/cuda-12.8}
build_jobs=${STRATA_BUILD_JOBS:-8}
pinned=a0116b2782a5b82622358c04a06496485d12b2d6
if [[ $(git -C "$strata_dir" rev-parse HEAD) != "$pinned" ]]; then
  printf '%s\n' 'Use the Strata commit pinned in snapshots/environment.json.' >&2
  exit 1
fi
if ! git -C "$strata_dir" diff --quiet HEAD --; then
  printf '%s\n' 'The Strata source has tracked changes; use a clean checkout.' >&2
  exit 1
fi
if [[ ! -x "$cuda_root/bin/nvcc" || ! -x "$strata_dir/.venv/bin/python" ]]; then
  printf '%s\n' 'Install CUDA 12.8 and the Strata Python environment first; see docs/REPRODUCE.md.' >&2
  exit 1
fi
export PATH="$strata_dir/.venv/bin:$cuda_root/bin:$PATH"
export LD_LIBRARY_PATH="$cuda_root/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
cd "$strata_dir"
# Upstream gets ggml/gguf-py/mtmd from its pinned llama.cpp archive.
.venv/bin/python - <<'PY'
import setup
setup.get_llama_cpp()
PY
cmake -S . -B build-cuda12 -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DSTRATA_ENABLE_CUDA=ON -DSTRATA_BUILD_TESTS=OFF \
  -DSTRATA_EXPERIMENTAL_SM60=ON \
  '-DCMAKE_CUDA_ARCHITECTURES=70;86' \
  "-DCMAKE_CUDA_COMPILER=$cuda_root/bin/nvcc" \
  "-DCUDAToolkit_ROOT=$cuda_root" \
  "-DSTRATA_GGML_DIR=$strata_dir/third_party/llama.cpp"
cmake --build build-cuda12 --target strata -j "$build_jobs"
cmake -S tools/vision -B build-vision-cuda12 -G Ninja \
  -DCMAKE_BUILD_TYPE=Release -DSTRATA_VISION_CUDA=ON -DSTRATA_PORTABLE=OFF \
  '-DCMAKE_CUDA_ARCHITECTURES=70;86' \
  "-DCMAKE_CUDA_COMPILER=$cuda_root/bin/nvcc" \
  "-DCUDAToolkit_ROOT=$cuda_root" \
  "-DLLAMA_DIR=$strata_dir/third_party/llama.cpp"
cmake --build build-vision-cuda12 --target strata-vision -j "$build_jobs"
install -d engine-cuda12
install -m 755 build-cuda12/strata engine-cuda12/strata
install -m 755 build-vision-cuda12/bin/strata-vision engine-cuda12/strata-vision
# Match setup.py's build stamp so a later setup can identify the local engine.
.venv/bin/python - "$cuda_root" <<'PY'
import json
import sys
from pathlib import Path
import setup
cuda = Path(sys.argv[1])
stamp = {
    "source": "local", "version": setup.source_version(), "archs": [70, 86],
    "vision": "gpu", "toolkit": 12,
    "cuda_dirs": [str(cuda / "bin"), str(cuda / "lib64")],
    "src": setup.source_hash(setup.ENGINE_SOURCES),
    "vision_src": setup.source_hash(setup.VISION_SOURCES),
}
Path("engine-cuda12/BUILD.json").write_text(json.dumps(stamp, indent=2) + "\n")
PY
