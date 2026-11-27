"""Builds the RayoHX Docker image from the Dockerfile in the repository root as rayohx:local-test.

The image installs the published rayohx-cli package from PyPI, at the version pinned in
requirements.txt.

Usage: ``python scripts/smoke/setup_image.py``
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMAGE = "rayohx:local-test"


def main() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    command = ["docker", "build", "-t", IMAGE, "--build-arg", f"VERSION={version}-local"]
    if subprocess.run([*command, str(ROOT)], check=False).returncode != 0:
        sys.exit("docker build failed")
    subprocess.run(["docker", "image", "ls", IMAGE], check=True)


if __name__ == "__main__":
    main()
