# Security

How the RayoHX image protects secrets and the machine it runs on. To report a vulnerability, see [SECURITY.md](../SECURITY.md). The protections of the download engine itself (redaction, input checks, credentials per host, file names, untrusted media) are in the [core security notes](https://github.com/coldsofttech/RayoHX/blob/main/packages/core/docs/security.md), and those of the command are in the [CLI security notes](https://github.com/coldsofttech/RayoHX-CLI/blob/main/docs/security.md).

## The image

- **Not root.** It runs as `rayohx` (uid and gid `10001`) with no home folder and no login shell. CI fails if the image runs as uid 0.
- **Minimal runtime.** The final stage holds only a slim Python base and the installed packages: no compilers, no pip, no sources and no FFmpeg. There is less to exploit and less to patch.
- **No secrets baked in.** The image holds no tokens, headers or cookies. Never add them with `ENV`, `ARG` or `COPY` when you build on top of it, because they stay in the image layers.
- **Two folders only.** It writes to `/output` and `/workspace`. Mount only what you need, and mount nothing else you would mind it changing.

## Secrets you give it

- **Use files.** Mount a file and pass `-H @/run/secrets/headers` (or `--cookie @file`), so the secret does not appear in the process list, `docker inspect` or shell history. Do not put a token in the URL or in `-e`.
- **Environment variables are visible.** `-e RAYOHX_PROXY=...` shows in `docker inspect` and to anyone who can read the container's configuration. Use a file or your orchestrator's secret store for anything sensitive.
- **Redaction applies.** Secrets are hidden in messages, errors and logs inside the container, as on any other install. The result goes to stdout and messages to stderr.

## Running it safely

- **Drop what you do not need.** For example: `--read-only` with `/output`, `/workspace` and a `--tmpfs /tmp` mounted, `--cap-drop ALL` and `--security-opt no-new-privileges`.
- **Run as your own user** with `--user "$(id -u):$(id -g)"` if you want files owned by you, and mount a writable `/workspace` as well.
- **Limit resources** with `--memory` and `--cpus` when running unattended downloads from sources you do not control.
- **Control the network.** The container reaches whatever the host can. Use `--network` or firewall rules to restrict it, and `--proxy` (or `RAYOHX_PROXY`) only when you mean to. Certificates are checked; avoid `--insecure`.
- **Untrusted media.** The command does not sandbox what it downloads. The container isolates it from your host, which is a reason to prefer it for sources you do not trust, but keep the downloaded files out of sensitive folders.

## Supply chain

- **Scanned.** [`security.yml`](../.github/workflows/security.yml) checks the `Dockerfile` with Semgrep and Trivy on every run, and scans the built image for vulnerable OS and Python packages on the weekly and manual runs. High and critical findings fail the run and appear in the Security tab. Dependencies are also covered by dependency review on pull requests.
- **Updates.** Dependabot proposes updates to the base image and to the GitHub Actions, with a 7-day cooldown. The `rayohx-cli` version is a pin in the `Dockerfile`, moved on purpose; see [packaging](packaging.md#changing-the-command-line-version).
- **Published carefully.** A release is pushed only when `PUBLISH_GHCR` is `true` and, if you set reviewers, after approval of the `docker` environment, using the workflow's own token with no stored secret. The image carries build provenance. See [releasing](releasing.md).
- **Pin what you run.** Pull a version tag (or its digest) instead of `latest` in anything that matters, so an update is a decision you make.
- **Rebuild for fixes.** The base image receives security updates. Pull a new release, or rebuild yours, regularly.

## Not included

The image does not scan or sign what you download, and the tags are not signed beyond provenance. Only download from sources you trust.
