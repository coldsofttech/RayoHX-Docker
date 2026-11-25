# Packaging

How the RayoHX image is built. The image installs the published [`rayohx-cli`](https://pypi.org/project/rayohx-cli/) package from PyPI, so that version must be released before the image can use it. For how a release is made and published to GitHub Container Registry (GHCR), see [releasing](releasing.md).

## What is built

| Where | What you get | Built with |
| --- | --- | --- |
| Any machine with Docker | the `rayohx` image, for your platform | `docker build -t rayohx .` |
| A release (tag `v<version>`) | `ghcr.io/<owner>/rayohx`, `linux/amd64` and `linux/arm64` | `release.yml` |

The image has no installer and nothing on PyPI. The image name is `rayohx`; it is set in `release.yml` (`IMAGE_NAME`).

## Building locally

Build from the repository root:

```bash
docker build -t rayohx .
docker build --build-arg RAYOHX_CLI_VERSION=0.1.0 --build-arg VERSION=0.1.0 -t rayohx:0.1.0 .
```

| Build argument | Default | Meaning |
| --- | --- | --- |
| `PYTHON_VERSION` | `3.15` | The Python version of the base image |
| `RAYOHX_CLI_VERSION` | `0.1.0` | The `rayohx-cli` version installed from PyPI |
| `VERSION` | `0.0.0` | Written to the `org.opencontainers.image.version` label |

The build context is empty (`Dockerfile.dockerignore` is `*`), because the image copies nothing in.

### Changing the command line version

The image is pinned to one `rayohx-cli` version, so a new command line release reaches the image only when you move the pin:

1. Release `rayohx-cli` to PyPI first. The wheels are compiled, so the version needs one for the image's Python (3.15 by default) and for both platforms.
2. Change the default of `RAYOHX_CLI_VERSION` in the `Dockerfile`, and add an `[Unreleased]` entry to `CHANGELOG.md` saying which command line version the image now has.
3. Build and run the checks in [testing](testing.md), then release the image as described in [releasing](releasing.md).

Dependabot cannot bump a build-argument default, so this step is by hand.

## Checks on every change

`ci.yml` runs on every pull request and push to `main`. It runs the pre-commit hooks, lints the `Dockerfile` with hadolint, type-checks the tests, builds the image, and runs the image tests; see [testing](testing.md). Nothing is published.
