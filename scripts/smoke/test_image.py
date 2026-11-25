"""Runs the image built by setup_image.py: shows the user it runs as, then runs `rayohx info`.

The `id` output is printed so you can see by eye that the user is not uid 0; it does not fail on it.
`rayohx info` runs on the first line of test_links.txt and fails if the command exits with an error.

Usage: ``python scripts/smoke/test_image.py``
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
IMAGE = "rayohx:local-test"


def docker(*args: str) -> int:
    return subprocess.run(["docker", *args], check=False).returncode


def main() -> None:
    probe = subprocess.run(["docker", "image", "inspect", IMAGE], capture_output=True, check=False)
    if probe.returncode != 0:
        sys.exit("Run setup_image.py first")
    url = (HERE / "test_links.txt").read_text(encoding="utf-8").splitlines()[0].strip()

    print("user:")
    if docker("run", "--rm", "--entrypoint", "id", IMAGE) != 0:
        sys.exit("id failed")

    print(f"inspecting: {url}")
    code = docker("run", "--rm", IMAGE, "info", url)
    if code != 0:
        sys.exit(f"rayohx info failed (exit {code})")


if __name__ == "__main__":
    main()
