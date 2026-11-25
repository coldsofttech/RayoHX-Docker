# Releasing

How a release of the RayoHX image is made. This repository releases one thing, the image on GitHub Container Registry (GHCR), so the only tag is `v<version>`. For what the image contains and how to build it, see [packaging](packaging.md).

## How it works

Publishing a GitHub release runs `release.yml`, and the tag decides the image tags. The job that pushes runs in the `docker` environment (Settings > Environments), so it waits for a reviewer if you set required reviewers there.

| Tag | Releases | Environment |
| --- | --- | --- |
| `v<version>` | the image `ghcr.io/<owner>/rayohx`, for `linux/amd64` and `linux/arm64` | `docker` |

There is no version file in this repository: the image version is the tag. The tag is written to the image's `org.opencontainers.image.version` label.

## Publishing is switched on by a variable

The registries are off until a repository variable turns them on (Settings > Secrets and variables > Actions > Variables):

| Variable | Effect |
| --- | --- |
| `PUBLISH_GHCR` | `true` publishes to GHCR |
| `DOCKERHUB_USERNAME` | when set, also publishes to Docker Hub (needs the `DOCKERHUB_TOKEN` secret too) |

With a variable unset, its job is skipped, so a release run does nothing for that registry.

## Making a release

1. Release the command line first if the image needs a newer one: the image installs `rayohx-cli` from PyPI, so that version must already be there. Move the pin as described in [packaging](packaging.md#changing-the-command-line-version).
2. Move the `[Unreleased]` entries in `CHANGELOG.md` under a `## [x.y.z]` heading, in a pull request, and merge it.
3. Publish a GitHub release tagged `v<version>`, for example `v0.2.0`. Mark it as a pre-release if it should not become `latest`.
4. `release.yml` does the rest:

| Step | Result |
| --- | --- |
| Set up | QEMU and Buildx, then a login to GHCR with the workflow's own token |
| Name | the tags from the release tag: `<version>` and `<major>.<minor>`, plus `latest` unless the release is a pre-release |
| Build and push | both platforms in one multi-platform image, built with `VERSION=<version>` and provenance attached |

Release notes are written on the GitHub release by hand (or with its "Generate release notes" button); `.github/release.yml` groups the generated ones into features, bug fixes and other changes.

To check a release: `docker run --rm ghcr.io/<owner>/rayohx:<version> --version`.

## One-time set-up

1. Set the `PUBLISH_GHCR` variable to `true`.
2. Create the `docker` environment (Settings > Environments) and add the people who must approve a release as required reviewers. Without reviewers, the job publishes as soon as the release is published.
3. After the first push, make the package public in the package settings if anyone should be able to pull it without signing in.

Pushing uses the workflow's own `GITHUB_TOKEN` with `packages: write`, so no secret is stored.

## If a release fails

- **The push was refused:** the workflow needs `packages: write`, and an existing package may need this repository added under its package settings.
- **The build fails on one platform:** reproduce with `docker buildx build --platform linux/arm64 .`, fix it in a pull request, and publish a new release. A pushed tag is not overwritten silently, so use a new version.
- **The build cannot find `rayohx-cli`:** the pinned `RAYOHX_CLI_VERSION` is not on PyPI, or has no wheel for the image's Python and platform. Release the command line first, or lower the pin.
- **Nothing was published:** check that `PUBLISH_GHCR` is `true`. When it is not, the `publish-ghcr` job is skipped.
- **`latest` points at a pre-release:** pre-releases never move `latest`; if it moved, check the release was marked as a pre-release before it was published.
