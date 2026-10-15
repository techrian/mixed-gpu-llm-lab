# Sources and licenses

- **Strata**: https://github.com/Niko1221/Strata, MIT,
  copyright (c) 2026 Niko1221 and the Strata contributors.
  Recorded source commit: `a0116b2782a5b82622358c04a06496485d12b2d6`.
  Engine flags, configuration format and model preparation commands come from this project.
  Its license is preserved in [third_party/Strata-LICENSE](third_party/Strata-LICENSE).
- **llama.cpp / ggml / mtmd**: https://github.com/ggml-org/llama.cpp,
  dependency pinned by Strata to `3cf03257f219afbe7334045ff7c6a06ac68c627d`.
  Source and binaries are obtained by the build process, not redistributed here.
- **Qwen3.8-Flash-Next-Uncensored-GGUF**:
  https://huggingface.co/orcarouter/Qwen3.8-Flash-Next-Uncensored-GGUF.
  Model files are not included; refer to the model distributor for their license and provenance.
- **MTP tensors**: original https://huggingface.co/Qwen/Qwen3.8-Flash-Next,
  prepared using Strata's pinned fetch/pack tools. Not included in this repository.

The MIT license for this setup repository does not relicense any model weights or upstream dependency.
The recorded benchmark scripts were written locally for these measurements; their only publication changes
are a configurable base URL and output directory. Timing JSON is preserved without rewriting measurements.
