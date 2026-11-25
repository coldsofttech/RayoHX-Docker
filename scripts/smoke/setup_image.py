"""Builds the RayoHX Docker image from the Dockerfile in the repository root as rayohx:local-test.

The image installs the published rayohx-cli package from PyPI; pass ``--cli-version`` to choose
the version instead of the Dockerfile's default.

Usage: ``python scripts/smoke/setup_image.py [--cli-version 0.1.0]``
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMAGE = "rayohx:local-test"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cli-version", help="rayohx-cli version to install, for example 0.1.0")
    args = parser.parse_args()

    command = ["docker", "build", "-t", IMAGE, "--build-arg", "VERSION=0.0.0-local"]
    if args.cli_version:
        command += ["--build-arg", f"RAYOHX_CLI_VERSION={args.cli_version}"]
    if subprocess.run([*command, str(ROOT)], check=False).returncode != 0:
        sys.exit("docker build failed")
    subprocess.run(["docker", "image", "ls", IMAGE], check=True)


if __name__ == "__main__":
    main()
