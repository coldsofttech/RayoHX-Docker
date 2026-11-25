# Development

How to work on this repository, the RayoHX Docker image. For how the image is built, see [architecture](architecture.md); for running it, see the [Docker guide](docker.md). The pull request process is in the [contributing guide](../CONTRIBUTING.md); tests are described in [testing](testing.md), packaging in [packaging](packaging.md) and releases in [releasing](releasing.md).

## Build and run

The image installs `rayohx-cli` from PyPI, so a build needs network access and nothing else from the repository:

```bash
docker build -t rayohx .
docker build --build-arg RAYOHX_CLI_VERSION=0.1.0 -t rayohx .
docker build --build-arg PYTHON_VERSION=3.13 -t rayohx:py313 .

docker run --rm rayohx --version
docker run --rm rayohx info https://example.com/master.m3u8
```

## Checks

Run only what your change touches:

```bash
uv run --no-project --with pytest pytest -m integration   # build the image and check it
uv run --no-project --with mypy --with pytest mypy        # type-check the tests
docker image ls rayohx --format '{{.Size}}'               # keep an eye on the size
```

What the tests check, the fixtures and the smoke test of the image are in [testing](testing.md). CI runs the same checks (`ci.yml`), plus pre-commit and hadolint. Behaviour changes to the command itself belong in the [RayoHX-CLI](https://github.com/coldsofttech/RayoHX-CLI) repository, not here.

## Rules to keep

- **One downloader.** Do not add a second implementation to the image. If the image needs something the command does not do, change the command.
- **Stay non-root.** The runtime stage must end with `USER 10001:10001` (the `rayohx` user, by number), and the image must not run as uid 0.
- **Keep it small.** No compilers, pip, package caches or FFmpeg in the runtime stage. Add a package only with a reason in the comment.
- **No secrets in the image.** Never put headers, cookies, tokens or credentials in a `Dockerfile`, build argument or `ENV`. Users pass them at run time (see [security](security.md)).
- **Keep the build context empty.** The image copies nothing in; if a build ever needs a file, allow only that file in `Dockerfile.dockerignore`.
- **Explain exceptions.** A `# nosemgrep`, a Trivy ignore or an entry in `.hadolint.yaml` needs a reason in a comment.

## Changing the image

1. Edit `Dockerfile`, keeping the two stages and the comments at the top current.
2. Build it and run the checks above, on both `amd64` and, if you changed the base or added a package, `arm64` (`docker buildx build --platform linux/arm64 .`).
3. If the change is visible to users (a folder, variable, user or tag), update the [Docker guide](docker.md), `README.md` and the `[Unreleased]` section of `CHANGELOG.md`.
