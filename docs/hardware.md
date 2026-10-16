# Recorded hardware

Measured on October 16, 2026. GPU indices are physical `nvidia-smi` indices.

## Host platform

| Component | Recorded specification |
| --- | --- |
| CPU | Ryzen 7 9700X; one socket, 8 physical cores / 16 logical CPUs, x86-64 |
| System RAM | 64 GB DDR5 class; Linux reported 64,933,089,280 bytes, or 60.474 GiB |
| Motherboard chipset and socket | B850, AM5 |
| Storage | One NVMe SSD, 2,000,398,934,016 bytes; 2 TB capacity class |
| Operating system | Ubuntu 24.04.5 LTS; kernel 7.0.0-38-generic |
| GPU software | NVIDIA driver 580.178.04; CUDA toolkit 12.8 |

The chipset was identified from the local DMI board identifier and checked against its published specification.
The [AM5 platform reference](https://www.amd.com/en/products/processors/chipsets/am5.html) documents B850 and DDR5 support.
Board brand/model, component-partner brands and serial numbers are omitted from the [curated specification snapshot](hardware-specs.json).
RAM module count, configured data rate, timings and channel population were not captured; the platform's supported rates do not establish the installed memory's operating rate.

## Compute GPUs and PCIe links

| Index | GPU | VRAM | Compute capability | Observed PCIe link | Engine CUDA index |
| --- | --- | ---: | --- | --- | ---: |
| 0 | RTX 3090 | 24 GiB | 8.6 | Gen4 x16 | 1 |
| 1 | RTX 3060 | 12 GiB | 8.6 | Gen4 x1 | 2 |
| 2 | Tesla PG500-216 / V100 | 32 GiB | 7.0 | Gen3 x4 | 0 |
| 3 | Tesla PG500-216 / V100 | 32 GiB | 7.0 | Gen3 x4 | 3 |

- 100 GiB aggregate VRAM. Aggregate capacity does not remove per-GPU allocation constraints.
- Both configurations remap devices in order `[2,0,1,3]`. Engine CUDA2 is the RTX 3060; physical GPU 2 is a V100.
- The vision encoder uses physical GPU 2. The output head and MTP use the final V100, physical GPU 3.
- Linux swap remains enabled globally; the measured server cgroups use `MemorySwapMax=0`.

The observed PCIe links are captured in [system-info.json](../benchmarks/agent-comparison/2026-10-16/snapshots/system-info.json).
No PCIe rewire or hardware change was made between these two measured deployments.
Power limits, clocks and thermal effects were not controlled as experimental factors. One host and a fixed model order limit generalization.

Earlier [GLM GPU-order and MTP placement trials](../benchmarks/throughput/glm-maya-m-20261016/README.md#3-move-the-rtx-3060-away-from-the-last-stage)
measured `[0,2,3,1]`, `[0,2,1,3]`, `[2,0,1,3]` and `[2,3,1,0]` on this topology.
The retained order favored mean decode rate; a different order had the shorter mean total time.
Automatic layer/expert placement changed with order, and no PCIe link-width comparison was performed.
