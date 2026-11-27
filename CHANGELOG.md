# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.1] - 2026-11-27

### Added

- Releases can also be published to Docker Hub as `coldsoft/rayohx`, after a reviewer approves them.

### Changed

- The image now uses Python 3.15 (it was 3.13).
- The image now installs `rayohx-cli` 0.1.1 by default (it was 0.1.0).
- The image now installs the published `rayohx-cli` package, pinned to one version, instead of building it from source.

### Security

- The image now includes the patched zlib library, fixing a high-severity heap buffer overflow (CVE-2026-85091).
- The image now includes a current pip, which carries the fixes for three high-severity flaws in the libraries it bundles: a memory leak (CVE-2026-114613) and an out-of-bounds read (GHSA-6v7p-g79w-8964) in msgpack, and traffic interception through an HTTPS proxy (CVE-2026-97687) and unbounded memory use (CVE-2026-97689) in urllib3.
- The image no longer contains setuptools, which had a high-severity path traversal flaw (CVE-2025-47273).

## [0.1.0] - 2026-11-21

### Added

- A Docker image that runs the `rayohx` command for `linux/amd64` and `linux/arm64`. It is small, runs as a normal user, and keeps the output and the resume state in two folders you can mount.
- Every option can be set with a `RAYOHX_` environment variable, and secrets can be read from mounted files, so they stay off the command line.
- Releases are published to GitHub Container Registry as a version tag, plus `latest` for full releases, after a reviewer approves them.
- Documentation for the image: how it is built, developed, packaged and secured.

### Security

- The image runs as an unprivileged user, and holds no compilers, pip or FFmpeg, which keeps what can be attacked small.
- The Dockerfile is checked on every change, and the built image is scanned for known vulnerabilities every week.
- Published images carry build provenance.
