"""Checks on the built command line image: it runs, stays unprivileged and keeps its folders."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable

Run = Callable[..., subprocess.CompletedProcess[str]]


def test_version_runs(run: Run) -> None:
    result = run("--version")
    assert result.returncode == 0
    assert result.stdout.strip()


def test_download_help_runs(run: Run) -> None:
    assert run("download", "--help").returncode == 0


def test_runs_as_unprivileged_user(run: Run) -> None:
    result = run("-u", entrypoint="id")
    assert result.returncode == 0
    assert result.stdout.strip() == "10001"


def test_output_and_workspace_are_writable(run: Run) -> None:
    result = run("-c", "touch /output/x /workspace/x", entrypoint="sh")
    assert result.returncode == 0, result.stderr


def test_workspace_environment(run: Run) -> None:
    result = run("RAYOHX_WORKSPACE", entrypoint="printenv")
    assert result.stdout.strip() == "/workspace"


def test_failure_is_a_message_not_a_traceback(run: Run) -> None:
    result = run("info", "http://127.0.0.1:1/none.m3u8", "--retries", "0")
    assert result.returncode == 1
    assert result.stderr.startswith("Error:") or "\nError:" in result.stderr
    assert "Traceback" not in result.stderr


def test_no_ffmpeg_or_pip(run: Run) -> None:
    result = run("-c", "command -v ffmpeg pip", entrypoint="sh")
    assert result.stdout.strip() == ""


def test_image_metadata(docker: str, image: str) -> None:
    inspected = subprocess.run(
        [docker, "image", "inspect", image], capture_output=True, text=True, check=True
    )
    config = json.loads(inspected.stdout)[0]["Config"]
    assert config["User"] == "10001:10001"
    assert config["Entrypoint"] == ["rayohx"]
    assert config["Labels"]["org.opencontainers.image.licenses"] == "Apache-2.0"
    assert set(config["Volumes"]) == {"/output", "/workspace"}
