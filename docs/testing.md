# Testing

How the image is tested. The behaviour of the command and the engine is tested in their own repositories: see the [RayoHX-CLI testing](https://github.com/coldsofttech/RayoHX-CLI/blob/main/docs/testing.md) and the [RayoHX testing](https://github.com/coldsofttech/RayoHX/blob/main/docs/testing.md) docs. The tests here check only what this repository adds: the image around the command.

## Where tests live

```text
tests/
  integration/
    conftest.py    fixtures: the docker command, the image under test, and a runner
    test_image.py  checks on the built image
scripts/smoke/     a manual check that builds the image and runs a real stream
pytest.ini         pytest settings: strict markers, and integration tests left out by default
mypy.ini           type-checking settings for the tests
```

The image tests drive the `docker` command, so they are integration tests. Everything in `tests/integration/` is marked `integration` automatically, so a normal `pytest` run leaves it out; run it with `-m integration`. They are skipped when Docker is not available. There are no unit tests, because the repository holds a `Dockerfile` and no application code, and so no coverage minimum, unlike the Python repositories.

## What is checked

- The command runs: `--version` and `download --help` exit with 0.
- The image runs as an unprivileged user (uid `10001`), and `/output` and `/workspace` are writable.
- `RAYOHX_WORKSPACE` is set to `/workspace`.
- A failure is a short `Error:` message with exit code 1 and no traceback.
- FFmpeg and pip are not on the path.
- The user, entry point, volumes and OCI labels (the license among them) are set.

## Running

```bash
uv run --no-project --with pytest pytest -m integration                      # builds rayohx:test first, then runs the checks
RAYOHX_IMAGE=rayohx uv run --no-project --with pytest pytest -m integration  # test an image you already built
uv run --no-project --with mypy --with pytest mypy                           # type-check the tests
docker image ls rayohx --format '{{.Size}}'  # keep an eye on the size
```

The first run builds the image from the `Dockerfile` in the repository root (`rayohx:test`), which installs `rayohx-cli` from PyPI, so it needs network access. Set `RAYOHX_IMAGE` to reuse an image you already built, such as one from `python scripts/dev/local.py` (`rayohx:local-test`, built from local checkouts of the library and the command; see [development](development.md#working-with-local-checkouts)). CI lets the tests build it themselves.

## Fixtures

| Fixture | What it gives you |
| --- | --- |
| `docker` | The path of the `docker` command; the test is skipped when Docker is missing or not running |
| `image` | The image under test: `RAYOHX_IMAGE` if set, otherwise `rayohx:test` built from the repository root |
| `run` | Runs the image: `run("--version")`, or `run("-c", "touch /output/x", entrypoint="sh")` to replace the entry point |

The fixtures are local to this repository. The tests do not depend on the shared `rayohx-pytest` plugin, the one in [RayoHX](https://github.com/coldsofttech/RayoHX) (`packages/pytest`) that the Python repositories use for local servers, certificates and test media; they need only `pytest`.

## In CI

`ci.yml` runs on every pull request and push to `main`:

| Job | What it does |
| --- | --- |
| `ci` | Runs the pre-commit hooks |
| `lint` | Lints the `Dockerfile` with hadolint |
| `type-check` | Type-checks the tests with mypy |
| `int-tests` | Builds the image and runs the image tests |
| `build` | Builds the image without pushing it |

`security.yml` scans the `Dockerfile` and the workflows with Semgrep, the `Dockerfile` with Trivy, and the built image with Trivy once a week; see [security](security.md#supply-chain). `dependency-review.yml` checks the dependencies a pull request changes. Nothing in CI publishes an image; that happens only from a release, see [packaging and releasing](packaging.md#releasing).

## Smoke test

The [smoke test](../scripts/smoke/README.md) builds the image and runs `rayohx info` from it against a real stream. It is a manual check that needs Docker and network access, separate from the pytest suite, and the same idea as the smoke test of the compiled build in the [RayoHX](https://github.com/coldsofttech/RayoHX/blob/main/docs/development.md#smoke-test-the-compiled-build) and [RayoHX-CLI](https://github.com/coldsofttech/RayoHX-CLI/blob/main/docs/packaging.md#checking-a-build) repositories. The stream it uses is the first line of `scripts/smoke/test_links.txt`.

## Writing tests

- Use the `run` fixture to run the image, and assert on the exit code, `stdout` and `stderr`.
- Keep each check small, and do not rely on one test having run before another.
- Never put real tokens or cookies in a test; use obvious fake values.
- A new behaviour of the image (a folder, a variable, the user) needs a test here and a line in the [Docker guide](docker.md). A change to what the command does belongs in [RayoHX-CLI](https://github.com/coldsofttech/RayoHX-CLI), with its tests.
