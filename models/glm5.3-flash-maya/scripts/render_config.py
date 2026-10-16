#!/usr/bin/env python3
"""Render the recorded Maya settings without changing an existing installation."""
import argparse
import json
import shlex
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]


def render(value, replacements):
    if isinstance(value, str):
        return Template(value).substitute(replacements)
    if isinstance(value, list):
        return [render(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: render(item, replacements) for key, item in value.items()}
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paths", type=Path, default=ROOT / "config/paths.local.json")
    parser.add_argument("--output", type=Path, default=ROOT / "runtime/maya.json")
    args = parser.parse_args()
    if not args.paths.is_file():
        parser.error("Copy config/paths.example.json to config/paths.local.json and edit it first.")
    paths = json.loads(args.paths.read_text())
    replacements = {}
    for key in ("maya_dir", "model_dir", "cuda_root"):
        if not isinstance(paths.get(key), str) or not paths[key].strip():
            parser.error(f"Missing path: {key}")
        replacements[key.upper()] = str(Path(paths[key]).expanduser().resolve())
    output = args.output.expanduser().resolve()
    replacements["RUNTIME_DIR"] = str(output.parent)
    replacements["BIND_HOST"] = paths.get("host", "127.0.0.1")
    config = render(json.loads((ROOT / "config/maya.template.json").read_text()), replacements)
    vision_gpu = int(paths.get("vision_gpu", 2))
    if vision_gpu < 0:
        parser.error("vision_gpu must be a physical NVIDIA index >= 0")
    output.parent.mkdir(parents=True, exist_ok=True)
    vision = Path(replacements["MAYA_DIR"]) / "build-vision/bin/strata-vision"
    wrapper = output.parent / "vision-on-v100.sh"
    wrapper.write_text("#!/bin/sh\nexport CUDA_VISIBLE_DEVICES=" + str(vision_gpu) + "\nexec " + shlex.quote(str(vision)) + ' "$@"\n')
    wrapper.chmod(0o700)
    config["port"] = int(paths.get("port", 8080))
    if not 1 <= config["port"] <= 65535:
        parser.error("port must be between 1 and 65535")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    output.chmod(0o600)
    print(f"Configuration written: {output}")


if __name__ == "__main__":
    main()
