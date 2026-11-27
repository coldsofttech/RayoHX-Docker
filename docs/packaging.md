# Packaging and releasing

How the RayoHX image is built and released to the GitHub Container Registry (GHCR) and Docker Hub. The image installs the published [`rayohx-cli`](https://pypi.org/project/rayohx-cli/) package from PyPI, which depends on the `rayohx` library, so those versions must be released before the image can use them. They are released from their own repositories: [RayoHX](https://github.com/coldsofttech/RayoHX) for the library and [RayoHX-CLI](https://github.com/coldsofttech/RayoHX-CLI) for the command (see its [packaging and releasing](https://github.com/coldsofttech/RayoHX-CLI/blob/main/docs/packaging.md)).

## What is built

| Where | What you get | Built with |
| --- | --- | --- |
| Any machine with Docker | the `rayohx` image, for your platform | `docker build -t rayohx .` |
| A release (tag `v<version>`) | `ghcr.io/<owner>/rayohx` and `docker.io/coldsoft/rayohx`, `linux/amd64` and `linux/arm64` | `release.yml` |

The image has no installer and nothing on PyPI. The image name is `rayohx`; it is set in `release.yml` (`IMAGE_NAME`). The order of releases is the library, then the command, then the image.

## Building locally

Build from the repository root:

```bash
docker build -t rayohx .
docker build --build-arg VERSION="$(cat VERSION)" -t rayohx:"$(cat VERSION)" .
```

| Build argument | Default | Meaning |
| --- | --- | --- |
| `PYTHON_VERSION` | `3.15` | The Python version of the base image |
| `VERSION` | `0.0.0` | Written to the `org.opencontainers.image.version` label. A release passes the contents of the `VERSION` file; pass it yourself for a local build, or the label stays `0.0.0` |

The build context holds only `requirements.txt` (`Dockerfile.dockerignore` leaves out everything else), which pins the `rayohx-cli` version installed from PyPI. To build from local checkouts of the library and the command instead of PyPI, see [development](development.md#working-with-local-checkouts).

### Changing the command line version

The image is pinned to one `rayohx-cli` version in `requirements.txt`, so a new command line release reaches the image only when the pin moves. Dependabot watches that file and opens a pull request when a new version is on PyPI:

1. Release `rayohx-cli` to PyPI first, from [RayoHX-CLI](https://github.com/coldsofttech/RayoHX-CLI). The wheels are compiled, so the version needs one for the image's Python (3.15 by default) and for both platforms. Until then, the pull request's image build fails.
2. On Dependabot's pull request, check that CI passes (the image builds and the image tests in [testing](testing.md) pass), and add an `[Unreleased]` entry to `CHANGELOG.md` saying which command line version the image now has.
3. Merge it, then release the image as described below. A merged pin does not publish anything, and it does not change `VERSION`.

To move the pin yourself, edit the version in `requirements.txt`.

## Checks on every change

`ci.yml` runs on every pull request and push to `main`. It runs the pre-commit hooks, lints the `Dockerfile` with hadolint, type-checks the tests, builds the image, and runs the image tests; see [testing](testing.md). Nothing is published.

## Releasing

Publishing a GitHub release runs `release.yml`, and the tag decides the image tags. This repository releases one thing, the image, so the only tag is `v<version>`. The image version lives in one place, the `VERSION` file at the repository root, like `__version__` in the Python repositories. The tag must equal `v` plus that version, for example `v0.2.0` for `0.2.0`, or the release stops before anything is built. The version is written to the image's `org.opencontainers.image.version` label. It is separate from `RAYOHX_CLI_VERSION`, the version of the command inside the image.

| Tag | Releases | Environment |
| --- | --- | --- |
| `v<version>` | the image on GHCR and Docker Hub, for `linux/amd64` and `linux/arm64` | `docker` |

Both publish jobs run in the `docker` environment (Settings > Environments), so each waits for a reviewer if you set required reviewers there.

### Publishing is switched on by a variable

The registries are off until a repository variable turns them on (Settings > Secrets and variables > Actions > Variables):

| Variable | Effect |
| --- | --- |
| `PUBLISH_GHCR` | `true` publishes to GHCR as `ghcr.io/<owner>/rayohx` |
| `DOCKERHUB_USERNAME` | when set, also publishes to Docker Hub as `docker.io/<username>/rayohx` (needs the `DOCKERHUB_TOKEN` secret too) |

With a variable unset, its job is skipped, so a release run does nothing for that registry. `DOCKERHUB_USERNAME` must be a repository variable, not an environment variable, because the job's `if:` is checked before the environment loads. The Docker Hub namespace is the username unless `DOCKERHUB_NAMESPACE` in `release.yml` says otherwise.

### Making a release

1. Release the command line first if the image needs a newer one: the image installs `rayohx-cli` from PyPI, so that version must already be there. Move the pin as described [above](#changing-the-command-line-version).
2. Set the new version in the `VERSION` file, and move the `[Unreleased]` entries in `CHANGELOG.md` under a `## [x.y.z]` heading, in a pull request, and merge it.
3. Publish a GitHub release tagged `v<version>`, for example `v0.2.0`. Mark it as a pre-release if it should not become `latest`.
4. `release.yml` does the rest. The check runs once, and the rest runs for each registry that is switched on:

| Step | Result |
| --- | --- |
| Check | the tag must be `v` plus the contents of `VERSION`, or the release stops here. The version it read is what the builds use |
| Set up | QEMU and Buildx, then a login: GHCR with the workflow's own token, Docker Hub with `DOCKERHUB_TOKEN` |
| Name | the tags from the release tag: `<version>` and `<major>.<minor>`, plus `latest` unless the release is a pre-release |
| Build and push | both platforms in one multi-platform image, built with `VERSION` from the file (so the label matches) and provenance attached |

Release notes are written on the GitHub release by hand (or with its "Generate release notes" button); `.github/release.yml` groups the generated ones into features, bug fixes and other changes.

To check a release, run `--version` from each registry you published to:

```bash
docker run --rm ghcr.io/<owner>/rayohx:<version> --version
docker run --rm coldsoft/rayohx:<version> --version
```

### One-time set-up

1. Create the `docker` environment (Settings > Environments) and add the people who must approve a release as required reviewers. Without reviewers, the jobs publish as soon as the release is published.
2. For GHCR, set the `PUBLISH_GHCR` variable to `true`. Pushing uses the workflow's own `GITHUB_TOKEN` with `packages: write`, so no secret is stored. After the first push, make the package public in the package settings if anyone should be able to pull it without signing in.
3. For Docker Hub, create an account and an access token, then set the variable and the secret:
   - On [Docker Hub](https://hub.docker.com), go to Account settings > Personal access tokens and create a token with **Read & Write** access. It is shown only once.
   - Set the `DOCKERHUB_USERNAME` repository variable to the account name (`coldsoft`).
   - Add the token as the `DOCKERHUB_TOKEN` secret. Putting it under the `docker` environment's secrets keeps it away from jobs that do not use that environment.
   - The `coldsoft/rayohx` repository is created by the first push. Create it first if you want to set its description and make sure it is public.

### If a release fails

- **The push to GHCR was refused:** the workflow needs `packages: write`, and an existing package may need this repository added under its package settings.
- **The push to Docker Hub was refused or the login failed:** the token is missing, expired or read-only, or `DOCKERHUB_USERNAME` is not the account that owns the repository. Create a new Read & Write token and update the secret.
- **A GitHub action could not be resolved:** this is usually a short GitHub outage. Re-run the failed job.
- **The tag does not match `VERSION`:** delete the release and the tag, fix `VERSION` in a pull request, and publish again.
- **The build fails on one platform:** reproduce with `docker buildx build --platform linux/arm64 .`, fix it in a pull request, and publish a new release. A pushed tag is not overwritten silently, so use a new version.
- **The build cannot find `rayohx-cli`:** the version pinned in `requirements.txt` is not on PyPI, or has no wheel for the image's Python and platform. Release the command line first, or lower the pin.
- **Nothing was published:** check that `PUBLISH_GHCR` is `true` or `DOCKERHUB_USERNAME` is set, and that the tag starts with `v`. Otherwise the job is skipped.
- **`latest` points at a pre-release:** pre-releases never move `latest`; if it moved, check the release was marked as a pre-release before it was published.
