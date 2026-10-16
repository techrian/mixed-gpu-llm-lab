#!/usr/bin/env python3
"""Start Project Maya using the rendered configuration (foreground process)."""
import argparse
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "runtime/maya.json")
    args = parser.parse_args()
    path = args.config.expanduser().resolve()
    if not path.is_file():
        parser.error("Run scripts/render_config.py first.")
    config = json.loads(path.read_text())
    strata = Path(config["cwd"])
    python = strata / ".venv/bin/python"
    server = strata / "maya.py"
    for required in (python, server, Path(config["exe"])):
        if not required.is_file():
            parser.error(f"Missing file: {required}")
    os.chdir(strata)
    os.execv(str(python), [str(python), str(server),
                         "--config", str(path), "--port", str(config["port"])])


if __name__ == "__main__":
    main()
