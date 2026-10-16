# Recorded hardware

Measured on October 16, 2026. GPU indices are physical `nvidia-smi` indices.

| Index | GPU | VRAM | Compute capability | Observed PCIe link | Engine CUDA index |
| --- | --- | ---: | --- | --- | ---: |
| 0 | RTX 3090 | 24 GiB | 8.6 | Gen4 x16 | 1 |
| 1 | RTX 3060 | 12 GiB | 8.6 | Gen4 x1 | 2 |
| 2 | Tesla PG500-216 / V100 | 32 GiB | 7.0 | Gen3 x4 | 0 |
| 3 | Tesla PG500-216 / V100 | 32 GiB | 7.0 | Gen3 x4 | 3 |

- AMD Ryzen 7 9700X, 8 physical cores / 16 logical CPUs.
- 64 GB class RAM; Linux reported 64,933,089,280 bytes, about 60.5 GiB.
- Ubuntu 24.04.5 LTS, kernel 7.0.0-38-generic, NVIDIA driver 580.178.04, CUDA 12.8.
- 100 GiB aggregate VRAM. Aggregate capacity does not remove per-GPU allocation constraints.
- Both configurations remap devices in order `[2,0,1,3]`. Engine CUDA2 is the RTX 3060; physical GPU 2 is a V100.
- The vision encoder uses physical GPU 2. The output head and MTP use the final V100, physical GPU 3.
- Linux swap remains enabled globally; the measured server cgroups use `MemorySwapMax=0`.

The observed PCIe links are captured in [system-info.json](../benchmarks/agent-comparison/2026-10-16/snapshots/system-info.json).
No PCIe rewire or hardware change was made between these two measured deployments.
Power limits, clocks and thermal effects were not controlled as experimental factors. One host and a fixed model order limit generalization.
