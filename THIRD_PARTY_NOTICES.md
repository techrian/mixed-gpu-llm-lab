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

- **Project Maya**: https://github.com/mw00/project-maya, MIT,
  copyright (c) 2026 Peasant Smith and the Project Maya contributors, and the Strata contributors.
  Recorded source commit: `362671aee624183ce3630fb1fd4c1aa431a5a451` (1.1.11), tracked source unmodified.
  The license is preserved in [third_party/Project-Maya-LICENSE](third_party/Project-Maya-LICENSE).
  The current GLM agent comparison used this engine.
- **GLM-5.3-Flash Maya-M**: https://huggingface.co/peasantsmith/GLM-5.3-Flash-Maya-GGUF,
  derived from https://huggingface.co/zai-org/GLM-5.3-Flash. Weights and vision artifacts are not redistributed.
- **Strata-GLM**: https://github.com/isichan-ai/Strata-GLM was consulted and used in earlier local experiments.
  The published October 16 GLM comparison uses Project Maya; these results are attributed to that measured stack.
- **Evaluation methodology references**: BFCL (https://gorilla.cs.berkeley.edu/blogs/13_bfcl_v3_multi_turn.html),
  tau2-bench (https://github.com/sierra-research/tau2-bench), Terminal-Bench (https://www.tbench.ai/),
  and Hermes Agent (https://github.com/NousResearch/hermes-agent). The local suite is custom; no official dataset
  or leaderboard score is claimed. Task fixtures and the local harness are authored for this report.

The MIT license for this setup repository does not relicense any model weights or upstream dependency.
The recorded benchmark scripts were written locally for these measurements; their only publication changes
are a configurable base URL and output directory. Timing JSON is preserved without rewriting measurements.
