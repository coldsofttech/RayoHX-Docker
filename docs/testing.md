# Testing

How the image is tested.

## Where tests live

```text
tests/
  integration/
    conftest.py    fixtures: the docker command, the image under test, and a runner
    test_image.py  checks on the built image
```

The image tests drive the `docker` command, so they are integration tests. Everything in `tests/integration/` is marked `integration` automatically, so a normal `pytest` run leaves it out; run it with `-m integration`. They are skipped when Docker is not available. There are no unit tests, because the repository holds a `Dockerfile` and no application code.

## What is checked

- The command runs: `--version` and `download --help` exit with 0.
- The image runs as an unprivileged user (uid `10001`), and `/output` and `/workspace` are writable.
- `RAYOHX_WORKSPACE` is set to `/workspace`.
- A failure is a short `Error:` message with exit code 1 and no traceback.
- FFmpeg and pip are absent from the image.
- The OCI label (title, source, license and version) and the entry point are set.

## Running

```bash
uv run --no-project --with pytest pytest -m integration                      # builds rayohx:test first, then runs the checks
RAYOHX_IMAGE=rayohx uv run --no-project --with pytest pytest -m integration  # test an image you already built
uv run --no-project --with mypy --with pytest mypy                           # type-check the tests
docker image ls rayohx --format '{{.Size}}'  # keep an eye on the size
```

The first run builds the image from the `Dockerfile` in the repository root (`rayohx:test`), which installs `rayohx-cli` from PyPI, so it needs network access. Set `RAYOHX_IMAGE` to reuse an image you already built. CI lets the tests build it themselves.

## Fixtures

| Fixture | What it gives you |
| --- | --- |
| `docker` | The path of the `docker` command; the test is skipped when Docker is missing or not running |
| `image` | The image under test: `RAYOHX_IMAGE` if set, otherwise `rayohx:test` built from the repository root |
| `run` | Runs the image: `run("--version")`, or `run("-c", "touch /output/x", entrypoint="sh")` to replace the entry point |

The fixtures are local to this repository. The tests do not depend on the shared `rayohx-pytest` plugin that the Python repositories use; they need only `pytest`.

## In CI

`ci.yml` runs on every pull request and push to `main`:

| Job | What it does |
| --- | --- |
| `ci` | Runs the pre-commit hooks |
| `lint` | Lints the `Dockerfile` with hadolint |
| `type-check` | Type-checks the tests with mypy |
| `int-tests` | Builds the image and runs the image tests |
| `build` | Builds the image without pushing it |

`security.yml` scans the `Dockerfile` with Semgrep and Trivy, and the built image with Trivy once a week; see [security](security.md#supply-chain).

## Smoke test

The [smoke test](../scripts/smoke/README.md) builds the image and runs `rayohx info` from it against a real stream. It is a manual check that needs Docker and network access, separate from the pytest suite.

## Writing tests

- Use the `run` fixture to run the image, and assert on the exit code, `stdout` and `stderr`.
- Keep each check small, and do not rely on one test having run before another.
- Never put real tokens or cookies in a test; use obvious fake values.
- A new behaviour of the image (a folder, a variable, the user) needs a test here and a line in the [Docker guide](docker.md).
