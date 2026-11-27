"""Builds the RayoHX image from local ``rayohx`` and ``rayohx-cli`` checkouts, without a release.

It builds a wheel of each checkout into ``.local/wheels``, writes ``.local/Dockerfile`` (the
committed Dockerfile with its PyPI install swapped for those wheels), and builds that as
``rayohx:local-test``, the image the smoke tests use. The committed Dockerfile is never changed.
The checkouts come from ``RAYOHX_PATH`` (default ``../RayoHX/packages/core``) and
``RAYOHX_CLI_PATH`` (default ``../RayoHX-CLI``).

Usage: ``python scripts/dev/local.py``
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / ".local"
WHEELS = LOCAL / "wheels"
IMAGE = "rayohx:local-test"

DEFAULT_CORE_PATH = "../RayoHX/packages/core"
CORE_PATH_ENV = "RAYOHX_PATH"
DEFAULT_CLI_PATH = "../RayoHX-CLI"
CLI_PATH_ENV = "RAYOHX_CLI_PATH"

RELEASE_INSTALL = "/opt/venv/bin/pip install --no-compile -r /requirements.txt"
LOCAL_INSTALL = "/opt/venv/bin/pip install --no-compile /wheels/*.whl"
WHEELS_COPY = "COPY .local/wheels /wheels\n\n"
RUN_ANCHOR = "RUN python -m venv /opt/venv"


def local_dockerfile(text: str) -> str | None:
    """The Dockerfile text installing the local wheels, or ``None`` if the install line is gone."""
    if RELEASE_INSTALL not in text or RUN_ANCHOR not in text:
        return None
    text = text.replace(RELEASE_INSTALL, LOCAL_INSTALL, 1)
    return text.replace(RUN_ANCHOR, WHEELS_COPY + RUN_ANCHOR, 1)


def checkout(env: str, default: str) -> Path:
    """The checkout path from ``env``, or ``default`` relative to this repository."""
    return (ROOT / os.environ.get(env, default)).resolve()


def main() -> int:
    """Build the wheels and the local image, and return the exit code."""
    import shutil
    import subprocess

    uv = shutil.which("uv")
    docker = shutil.which("docker")
    if uv is None or docker is None:
        print("uv and docker must both be on PATH.")
        return 1

    dockerfile = local_dockerfile((ROOT / "Dockerfile").read_text(encoding="utf-8"))
    if dockerfile is None:
        print("The Dockerfile's PyPI install line changed; update scripts/dev/local.py.")
        return 1

    shutil.rmtree(WHEELS, ignore_errors=True)
    WHEELS.mkdir(parents=True)
    for env, default in ((CORE_PATH_ENV, DEFAULT_CORE_PATH), (CLI_PATH_ENV, DEFAULT_CLI_PATH)):
        source = checkout(env, default)
        if not (source / "pyproject.toml").is_file():
            print(f"No pyproject.toml in {source}; set {env}.")
            return 1
        build = [uv, "build", "--wheel", "--out-dir", str(WHEELS), str(source)]
        if subprocess.run(build, check=False).returncode != 0:
            print(f"Building {source.name} failed.")
            return 1

    (LOCAL / "Dockerfile").write_text(dockerfile, encoding="utf-8", newline="\n")
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    command = [
        docker, "build", "-t", IMAGE, "--build-arg", f"VERSION={version}-local",
        "-f", str(LOCAL / "Dockerfile"), str(ROOT),
    ]  # fmt: skip
    if subprocess.run(command, check=False).returncode != 0:
        print("docker build failed.")
        return 1
    print(f"Built {IMAGE} from local sources; run scripts/smoke/test_image.py against it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
