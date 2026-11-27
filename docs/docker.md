# Docker

The image runs the same `rayohx` command as the Python package, for headless use on servers and in pipelines. It holds no second downloader: the image installs the published `rayohx-cli` package from PyPI, which brings the `rayohx` library.

- **Small:** a slim Python base with only the command and its dependencies. FFmpeg is not included, because joining audio and video is built in. If you need FFmpeg for an unusual codec, build your own image on top of this one and install it (see the [Python guide](https://github.com/coldsofttech/RayoHX/blob/main/docs/guides/python.md)).
- **Non-root:** it runs as user `rayohx` (uid and gid `10001`), with no shell login.
- **Platforms:** `linux/amd64` and `linux/arm64`.

## Where to get it

The image is published to the GitHub Container Registry as `ghcr.io/coldsofttech/rayohx`. It can also be published to Docker Hub as `coldsoft/rayohx`, when the maintainer turns that on. The two registries get the same tags: the version (`X.Y.Z`, `X.Y`) and `latest`, which a pre-release does not move. The examples below use GHCR; swap in the Docker Hub name if you pull from there.

## Running

```bash
docker run --rm ghcr.io/coldsofttech/rayohx info https://example.com/master.m3u8

docker run --rm \
  -v "$PWD/downloads:/output" \
  -v rayohx-work:/workspace \
  ghcr.io/coldsofttech/rayohx download https://example.com/master.m3u8 -o /output/movie.mp4
```

The image's entry point is `rayohx`, so everything after the image name is a normal command; see the [command line guide](https://github.com/coldsofttech/RayoHX-CLI/blob/main/docs/guides/cli.md). Results go to stdout and messages to stderr, so `--json` output can be piped. Without a terminal, progress is printed as a line every 10%.

## Folders

| Folder | Purpose |
| --- | --- |
| `/output` | The working directory. A download without `-o` is saved here. Mount a folder to keep the files. |
| `/workspace` | Where partial downloads and resume state are kept (`RAYOHX_WORKSPACE`). Mount a folder or a named volume to resume after the container is removed. |

Files are written as uid `10001`. When you mount a host folder, make it writable for that user, or run the container as your own user instead:

```bash
docker run --rm --user "$(id -u):$(id -g)" -v "$PWD/downloads:/output" ghcr.io/coldsofttech/rayohx download URL
```

With `--user`, also mount a writable `/workspace`, since the built-in one belongs to uid `10001`.

## Settings

Every option can be set with a `RAYOHX_` environment variable, for example `-e RAYOHX_QUALITY=720p -e RAYOHX_CONCURRENCY=8`; see [settings](https://github.com/coldsofttech/RayoHX-CLI/blob/main/docs/guides/cli/settings.md). The image sets `RAYOHX_WORKSPACE=/workspace` and `NO_COLOR=1`. Command line options win over the environment.

Pass secrets as files, not on the command line: mount a file and use `-H @/run/secrets/headers`, so they do not appear in the process list or shell history. Do not bake them into an image.

Exit codes are those of the command: `0` success, `1` failure, `2` invalid usage or settings, `130` cancelled. To cancel cleanly and keep what a resume needs, send an interrupt: `docker kill --signal INT <container>`.

## Building

The image installs `rayohx-cli` from PyPI, so the build needs network access and nothing from this repository except the `Dockerfile`:

```bash
docker build -t rayohx .
docker build --build-arg PYTHON_VERSION=3.15 -t rayohx:py315 .
```

`Dockerfile.dockerignore` leaves out the whole build context except `requirements.txt`. The `rayohx-cli` version is pinned there, and Dependabot proposes new versions; see [packaging](packaging.md#changing-the-command-line-version) for how to move it.

## Publishing

The [CI workflow](../.github/workflows/ci.yml) lints the `Dockerfile`, builds the image and checks it on every change; nothing is published. To publish, create a GitHub release tagged `v<version>`: the [Release workflow](../.github/workflows/release.yml) builds both platforms and pushes the version tags (and `latest`, unless the release is a pre-release) with provenance. Each registry is off until its repository variable is set:

| Registry | Image | Turned on by |
| --- | --- | --- |
| GitHub Container Registry | `ghcr.io/<owner>/rayohx` | `PUBLISH_GHCR` set to `true` |
| Docker Hub | `docker.io/coldsoft/rayohx` | `DOCKERHUB_USERNAME` (`coldsoft`), with the `DOCKERHUB_TOKEN` secret |

Both publish jobs run in the `docker` environment, so its protection rules and secrets apply to each. See [packaging and releasing](packaging.md#releasing) for the steps and the one-time set-up, and [testing](testing.md) for what the checks cover.
