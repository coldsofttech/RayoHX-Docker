# RayoHX Docker

[![CI](https://github.com/coldsofttech/RayoHX-Docker/actions/workflows/ci.yml/badge.svg)](https://github.com/coldsofttech/RayoHX-Docker/actions/workflows/ci.yml)
[![Security](https://github.com/coldsofttech/RayoHX-Docker/actions/workflows/security.yml/badge.svg)](https://github.com/coldsofttech/RayoHX-Docker/actions/workflows/security.yml)
[![GHCR](https://img.shields.io/badge/ghcr.io-coldsofttech%2Frayohx-blue?logo=docker&logoColor=white)](https://github.com/coldsofttech/RayoHX-Docker/pkgs/container/rayohx)
[![Platforms](https://img.shields.io/badge/platforms-linux%2Famd64%20%7C%20linux%2Farm64-blue)](docs/docker.md)
[![Non-root](https://img.shields.io/badge/runs%20as-non--root-green)](docs/security.md)
[![Python](https://img.shields.io/badge/base-python%3Aslim-blue?logo=python&logoColor=white)](docs/architecture.md)
[![License](https://img.shields.io/github/license/coldsofttech/RayoHX-Docker)](LICENSE)

Download HLS streams from a container, with nothing to install except Docker.

```sh
docker run --rm -v "$PWD/downloads:/output" ghcr.io/coldsofttech/rayohx download https://example.com/master.m3u8 -o /output/movie.mp4
```

## What is RayoHX?

RayoHX is a tool for saving HLS streams (`.m3u8` links) as ordinary video files. Many websites play
video as a stream made of many small pieces, which is awkward to save by hand. Give RayoHX the
stream's web address and it looks at what the stream offers, lets you choose the quality, audio and
subtitles you want, and puts everything together into a single file you can keep and play anywhere.

RayoHX comes in several forms that share the same engine: a Python library, a command line, a
desktop window for Windows and this Docker image. This repository is the **Docker image**: the
`rayohx` command in a small container, for servers, pipelines and scheduled jobs.

## How it helps

- **Nothing to install**: no Python, no FFmpeg, no dependencies on your machine, only Docker
- **Safe to run anywhere**: the container runs as a normal user, holds no compilers or pip, and
  keeps its files in two folders you choose
- **Fits automation**: results go to stdout and messages to stderr, `--json` output can be piped,
  and every option can be set with a `RAYOHX_` environment variable
- **Secrets stay out of the command line**: read headers and cookies from a mounted file, so they
  never appear in your shell history or the process list
- **Finish what you started**: keep the resume folder between runs and interrupted downloads
  continue where they stopped

## What you can do

- See a stream's qualities, audio and subtitle tracks and encryption before downloading anything
- Choose the quality, audio and subtitles, and save to a file or a folder of segments
- Join separate audio and video into one MP4 without installing FFmpeg
- Download encrypted (AES-128) streams; protected (DRM) and live streams are refused with an
  explanation
- Use proxies, custom headers and cookies when a site needs them
- Run it from a script, a scheduled job or a CI pipeline

## Get the image

```sh
docker pull ghcr.io/coldsofttech/rayohx
```

The image is published for `linux/amd64` and `linux/arm64`, so it runs on Intel and AMD servers
and on Apple silicon and ARM machines. Each release has these tags:

| Tag | Meaning |
| --- | --- |
| `latest` | The newest full release |
| `1.2.3` | That exact release |
| `1.2` | The newest release of that minor version |

Use a version tag, not `latest`, in anything that matters, so an update is a decision you make.
Each image contains one version of the `rayohx` command; see the [changelog](CHANGELOG.md).

## Run it

Look at a stream without downloading it:

```sh
docker run --rm ghcr.io/coldsofttech/rayohx info https://example.com/master.m3u8
```

Download it, keeping the file and the resume state:

```sh
docker run --rm \
  -v "$PWD/downloads:/output" \
  -v rayohx-work:/workspace \
  ghcr.io/coldsofttech/rayohx download https://example.com/master.m3u8 -o /output/movie.mp4
```

Everything after the image name is a normal `rayohx` command, so it works as it does in a terminal.

| Folder | Purpose |
| --- | --- |
| `/output` | Where files are saved. Mount a folder to keep them. |
| `/workspace` | Where partial downloads are kept. Mount a folder or a named volume to resume later. |

The image runs as a normal user (uid `10001`), supports `linux/amd64` and `linux/arm64`, and
carries no FFmpeg, compilers or pip.

Files are written as uid `10001`. To save files as yourself instead, add
`--user "$(id -u):$(id -g)"` and mount a writable `/workspace` too; see the [Docker guide](docs/docker.md).

All the releases are on the [releases page](https://github.com/coldsofttech/RayoHX-Docker/releases), and the
tags are on the [package page](https://github.com/coldsofttech/RayoHX-Docker/pkgs/container/rayohx).

## Build it yourself

```sh
docker build -t rayohx .
```

This installs the published `rayohx-cli` package from PyPI, so the build needs network access. See the
[Docker guide](docs/docker.md#building) for the build arguments.

## Other ways to use RayoHX

| What it is | Where |
| --- | --- |
| The `rayohx` command, installed with Python | [`rayohx-cli`](https://pypi.org/project/rayohx-cli/) |
| Python library, to use RayoHX inside your own programs | [`rayohx`](https://pypi.org/project/rayohx/) |
| Desktop window for Windows | The full setup on the [RayoHX-Installer releases page](https://github.com/coldsofttech/RayoHX-Installer/releases) |

## Learn more

- [Docker guide](docs/docker.md): folders, settings, exit codes, building and publishing
- [Command line guide](https://github.com/coldsofttech/RayoHX-CLI/blob/main/docs/guides/cli.md):
  every option and example
- [Security](docs/security.md): handling secrets and running the container safely
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md) · [Security policy](SECURITY.md) · [Support](SUPPORT.md)
- [Report a problem](https://github.com/coldsofttech/RayoHX-Docker/issues)

## License

Apache-2.0. See [LICENSE](LICENSE).
