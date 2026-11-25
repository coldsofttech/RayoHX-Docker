# Architecture

How the RayoHX image is put together. For running it, see the [Docker guide](docker.md); for working on it, see [development](development.md).

## What the image is

The image runs the same `rayohx` command as the Python package. It holds no second downloader: it installs the published `rayohx-cli` package from PyPI, which depends on the `rayohx` library, so the image, the PyPI packages and the installers behave the same way. See the [CLI architecture](https://github.com/coldsofttech/RayoHX-CLI/blob/main/docs/architecture.md) and the [core architecture](https://github.com/coldsofttech/RayoHX/blob/main/packages/core/docs/architecture.md) for how the command and the library work.

## Files

```text
Dockerfile                the two-stage build
Dockerfile.dockerignore   leaves the build context empty, since nothing is copied in
docs/                     this documentation
tests/integration/        the image tests (they drive the docker command); see testing.md
scripts/smoke/            a manual check that builds and runs the image
CHANGELOG.md              changes to the image
README.md                 the image for users
```

The build context holds nothing the image needs: the command is installed from PyPI.

## Stages

| Stage | Purpose |
| --- | --- |
| `build` | A slim Python image where `rayohx-cli` (version `RAYOHX_CLI_VERSION`) and its dependencies are installed into a virtual environment at `/opt/venv`. pip is removed from the environment afterwards. |
| `runtime` | The same slim base with only `/opt/venv` copied in: no compilers, no pip and no sources. |

Splitting the stages keeps the final image small and keeps build tools out of it. The Python version is the `PYTHON_VERSION` build argument (default 3.15), and both stages use the same one so the virtual environment matches its interpreter.

## The runtime image

- **User.** A fixed system user and group `rayohx` (uid and gid `10001`) with no home folder and no login shell, so files written to a mounted folder have a predictable owner.
- **Folders.** `/output` is the working directory and `/workspace` holds partial downloads and resume state (`RAYOHX_WORKSPACE`). Both are declared as volumes and owned by `rayohx`.
- **Entry point.** `ENTRYPOINT ["rayohx"]` with `CMD ["--help"]`, so everything after the image name is a normal command.
- **Environment.** `RAYOHX_WORKSPACE=/workspace` and `NO_COLOR=1` are set. Python output is unbuffered and no bytecode is written. Command line options win over `RAYOHX_` variables.
- **Labels.** The OCI labels (title, description, source, license and `VERSION`) are set so registries show the right details.

## No FFmpeg

Joining audio and video is built into the library, so FFmpeg is not installed. That keeps the image small and removes a large source of vulnerabilities. Someone who needs FFmpeg for an unusual codec builds their own image on top of this one.

## Platforms and releases

The image is built for `linux/amd64` and `linux/arm64`. CI builds your platform only and checks it; a `v<version>` release builds both and pushes to GHCR. See [packaging](packaging.md) for building and [releasing](releasing.md) for publishing, and [testing](testing.md) for how the image is checked.
