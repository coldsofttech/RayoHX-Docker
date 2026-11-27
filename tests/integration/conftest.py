"""Fixtures for the image tests: build the image once (or reuse one) and run containers from it."""

from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCKERFILE = REPO_ROOT / "Dockerfile"
DEFAULT_TAG = "rayohx:test"


DOCKER = shutil.which("docker")


def _docker_works() -> bool:
    if DOCKER is None:
        return False
    return subprocess.run([DOCKER, "info"], capture_output=True, check=False).returncode == 0


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Mark every test in this directory as an integration test."""
    for item in items:
        if "integration" in item.path.parts:
            item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="session")
def docker() -> str:
    """The full path of the docker command; the tests skip when it is not usable."""
    if DOCKER is None or not _docker_works():
        pytest.skip("Docker is not available")
    return DOCKER


@pytest.fixture(scope="session")
def image(docker: str) -> str:
    """The image under test.

    Set RAYOHX_IMAGE to test an image that is already built (CI does this); otherwise the image is
    built from the repository root. The tests are skipped when Docker is not available.
    """
    existing = os.environ.get("RAYOHX_IMAGE")
    if existing:
        return existing
    build = subprocess.run(
        [docker, "build", "-f", str(DOCKERFILE), "-t", DEFAULT_TAG, str(REPO_ROOT)],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if build.returncode != 0:
        pytest.fail(f"docker build failed:\n{build.stderr[-2000:]}")
    return DEFAULT_TAG


@pytest.fixture(scope="session")
def run(docker: str, image: str) -> Callable[..., subprocess.CompletedProcess[str]]:
    """Run the image: `run("--version")` or `run("-c", "...", entrypoint="sh")`."""

    def _run(*args: str, entrypoint: str | None = None) -> subprocess.CompletedProcess[str]:
        command = [docker, "run", "--rm"]
        if entrypoint is not None:
            command += ["--entrypoint", entrypoint]
        command += [image, *args]
        return subprocess.run(command, capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=120,
        )

    return _run
