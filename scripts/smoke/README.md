# Smoke test for the image

A manual check that the image builds and runs. It is separate from the pytest suite in `tests/`.

## What you need

- Python 3.11 or newer, to run the scripts.
- Docker, running.
- Network access, to install `rayohx-cli` from PyPI while building and to reach the test stream.

## Steps

Run these from the repository root. They work on Windows, Linux and macOS.

```sh
python scripts/smoke/setup_image.py   # builds rayohx:local-test
python scripts/smoke/test_image.py    # shows the user the container runs as, then runs `rayohx info`
```

### `setup_image.py`

Builds the `Dockerfile` in the repository root as `rayohx:local-test`, with `VERSION=<contents of the VERSION file>-local`. It installs the `rayohx-cli` version pinned in `requirements.txt`; edit that file to try another version.

### `test_image.py`

Prints the output of `id` from inside the container, so you can see by eye that it is not uid 0. It
does not fail on it. It then runs `rayohx info` on the **first line** of `test_links.txt` and fails
if the command exits with an error. It stops with "Run setup_image.py first" when the image is
missing.

To try another stream, put its URL on the first line of `test_links.txt`; any further lines are
ignored. The file is kept in the repository, so use a stream you are allowed to share.

## Files

| File | What it is |
|---|---|
| `setup_image.py` | Builds the image |
| `test_image.py` | Runs the image and `rayohx info` |
| `test_links.txt` | Test stream addresses; the first line is used |
