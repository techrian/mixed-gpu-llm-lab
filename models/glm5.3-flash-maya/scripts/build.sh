#!/usr/bin/env bash
set -euo pipefail
maya_dir=$(realpath "${1:?Usage: build.sh /path/to/project-maya}")
cuda_root=${MAYA_CUDA_ROOT:-/usr/local/cuda-12.8}
build_jobs=${MAYA_BUILD_JOBS:-8}
pinned=362671aee624183ce3630fb1fd4c1aa431a5a451
if [[ $(git -C "$maya_dir" rev-parse HEAD) != "$pinned" ]]; then
  printf '%s\n' 'Use the Maya source commit pinned in this profile.' >&2
  exit 1
fi
if ! git -C "$maya_dir" diff --quiet HEAD --; then
  printf '%s\n' 'Use a clean separate source checkout.' >&2
  exit 1
fi
export PATH="$maya_dir/.venv/bin:$cuda_root/bin:$PATH"
export LD_LIBRARY_PATH="$cuda_root/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
cd "$maya_dir"
.venv/bin/python -c 'import setup; setup.get_llama_cpp()'
# The recorded main cache used native; 70;86 names this machine's two architectures explicitly.
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DSTRATA_ENABLE_CUDA=ON -DSTRATA_BUILD_TESTS=OFF \
  -DSTRATA_NATIVE_EXPERTS=ON -DSTRATA_PREFILL_MMQ=OFF \
  '-DCMAKE_CUDA_ARCHITECTURES=70;86' \
  "-DCMAKE_CUDA_COMPILER=$cuda_root/bin/nvcc" "-DCUDAToolkit_ROOT=$cuda_root" \
  "-DSTRATA_GGML_DIR=$maya_dir/third_party/llama.cpp"
cmake --build build --target strata -j "$build_jobs"
cmake -S tools/vision -B build-vision -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DSTRATA_VISION_CUDA=ON -DSTRATA_PORTABLE=OFF '-DCMAKE_CUDA_ARCHITECTURES=70;86' \
  "-DCMAKE_CUDA_COMPILER=$cuda_root/bin/nvcc" "-DCUDAToolkit_ROOT=$cuda_root" \
  "-DLLAMA_DIR=$maya_dir/third_party/llama.cpp"
cmake --build build-vision --target strata-vision -j "$build_jobs"
