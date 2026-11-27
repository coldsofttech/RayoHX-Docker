# Development

How to work on this repository, the RayoHX Docker image. For how the image is built, see [architecture](architecture.md); for running it, see the [Docker guide](docker.md). The pull request process is in the [contributing guide](../CONTRIBUTING.md); tests are described in [testing](testing.md), packaging and releases in [packaging and releasing](packaging.md).

This repository only packages the command as an image. The logic lives elsewhere: the `rayohx` library in [RayoHX](https://github.com/coldsofttech/RayoHX) and the `rayohx` command in [RayoHX-CLI](https://github.com/coldsofttech/RayoHX-CLI). A change to how the command behaves belongs in those repositories, not here.

## Layout

```text
Dockerfile                the two-stage build
Dockerfile.dockerignore   leaves out the build context except requirements.txt
requirements.txt          the pinned rayohx-cli version the image installs
VERSION                   the image version; a release tag must be "v" plus this
tests/integration/        the image tests (they drive the docker command)
scripts/smoke/            a manual check that builds and runs the image
scripts/dev/              local.py, which builds the image from local checkouts
brand/                    the logo and social preview image
docs/                     repository documentation
.github/workflows/        ci, security, dependency review and release
```

The changelog is the root `CHANGELOG.md`.

## Tooling

| Purpose | Tool |
| --- | --- |
| Build and run | Docker, with Buildx for multi-platform builds |
| Dockerfile lint | hadolint (`.hadolint.yaml`) |
| Image tests | pytest, run through [uv](https://docs.astral.sh/uv/) |
| Type checking | mypy, over the tests |
| Other checks | pre-commit: file hygiene, gitleaks, Markdown lint and actionlint |

## Build and run

The image installs `rayohx-cli` from PyPI, so a build needs network access and nothing else from the repository:

```bash
docker build -t rayohx .
docker build --build-arg PYTHON_VERSION=3.15 -t rayohx:py315 .

docker run --rm rayohx --version
docker run --rm rayohx info https://example.com/master.m3u8
```

## Working with local checkouts

To try the image against changes you have not released, build it from local copies of the library and the command:

```bash
python scripts/dev/local.py
```

It builds a wheel of each checkout into `.local/wheels`, writes `.local/Dockerfile` (the committed one with its PyPI install swapped for those wheels) and builds it as `rayohx:local-test`, the image the smoke tests use. The committed `Dockerfile` is never changed. The checkouts are taken from `RAYOHX_PATH` (default `../RayoHX/packages/core`) and `RAYOHX_CLI_PATH` (default `../RayoHX-CLI`). `.local/` is git-ignored.

## Checks

Run only what your change touches:

```bash
uv run --no-project --with pytest pytest -m integration   # build the image and check it
uv run --no-project --with mypy --with pytest mypy        # type-check the tests
docker image ls rayohx --format '{{.Size}}'               # keep an eye on the size
pre-commit run --all-files                                # file hygiene, hadolint, Markdown and workflow lint
```

The integration tests are marked `integration` and left out of the default run, because they need Docker and build the image. What the tests check, the fixtures and the smoke test of the image are in [testing](testing.md). CI (`ci.yml`) runs the same checks, plus pre-commit and hadolint. The other workflows are `security.yml`, `dependency-review.yml` and `release.yml`.

## Rules to keep

- **One downloader.** Do not add a second implementation to the image. If the image needs something the command does not do, change the command in [RayoHX-CLI](https://github.com/coldsofttech/RayoHX-CLI).
- **Stay non-root.** The runtime stage must end with `USER 10001:10001` (the `rayohx` user, by number), and the image must not run as uid 0.
- **Keep it small.** No compilers, package caches or FFmpeg in the runtime stage, and no build tools such as `setuptools` or `wheel`. Add a package only with a reason in the comment.
- **No secrets in the image.** Never put headers, cookies, tokens or credentials in a `Dockerfile`, build argument or `ENV`. Users pass them at run time (see [security](security.md)).
- **Keep the build context small.** The image copies in only `requirements.txt`; if a build ever needs another file, allow only that file in `Dockerfile.dockerignore`.
- **Keep publishing off by default.** The release workflow publishes to GHCR (`ghcr.io/coldsofttech/rayohx`) and Docker Hub (`coldsoft/rayohx`) only when the maintainer sets the variables, and both jobs run in the `docker` environment. Do not publish or tag a release yourself.
- **Explain exceptions.** A `# nosemgrep`, a Trivy ignore or an entry in `.hadolint.yaml` needs a reason in a comment. A pinned fix for a base image advisory names the advisory in the `Dockerfile`.

## Changing the image

1. Edit `Dockerfile`, keeping the two stages and the comments at the top current.
2. Build it and run the checks above, on both `amd64` and, if you changed the base or added a package, `arm64` (`docker buildx build --platform linux/arm64 .`).
3. If the change is visible to users (a folder, variable, user or tag), update the [Docker guide](docker.md), `README.md` and the `[Unreleased]` section of `CHANGELOG.md`.
