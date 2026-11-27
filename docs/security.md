# Security

How the RayoHX image protects secrets and the machine it runs on. To report a vulnerability, see [SECURITY.md](../SECURITY.md). The image runs the published `rayohx-cli` command, so it has the protections of the command and the engine as well: the [CLI security notes](https://github.com/coldsofttech/RayoHX-CLI/blob/main/docs/security.md) cover secrets, redaction, connections and what the command shows, and the [core security notes](https://github.com/coldsofttech/RayoHX/blob/main/docs/security.md) cover the download engine (redaction, input checks, credentials per host, working folder, file names, untrusted media). This page covers what the image adds. A problem in the command or the engine is fixed in those repositories, and reaches the image through a new `rayohx-cli` release.

## The image

- **Not root.** It runs as `rayohx` (uid and gid `10001`) with no home folder and no login shell. CI fails if the image runs as uid 0.
- **Minimal runtime.** The final stage holds only a slim Python base and the installed packages: no compilers, no sources and no FFmpeg. The build tools `setuptools` and `wheel` are removed, so there is less to exploit and less to patch.
- **Patched base.** The `Dockerfile` upgrades only `zlib1g` and pip, so a fix is in the image even when the base image is older than the fix. Each of these steps names the advisory it covers in a comment, and is dropped once the base image catches up.
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

- **Scanned.** [`security.yml`](../.github/workflows/security.yml) checks the `Dockerfile` and the workflows with Semgrep, and the `Dockerfile` with Trivy, on every run, and scans the built image for vulnerable OS and Python packages on the weekly and manual runs. High and critical findings fail the run and appear in the Security tab. Dependencies are also covered by dependency review on pull requests.
- **Linted.** `ci.yml` lints the `Dockerfile` with hadolint, and the pre-commit hooks lint the workflows with actionlint.
- **Secret scanning.** The pre-commit hooks run gitleaks before a commit.
- **Updates.** Dependabot proposes updates to the base image, the GitHub Actions and the `rayohx-cli` version pinned in `requirements.txt`, with a 7-day cooldown. Each is a pull request you review and merge; see [packaging](packaging.md#changing-the-command-line-version). The command's own dependencies are locked and audited in [RayoHX-CLI](https://github.com/coldsofttech/RayoHX-CLI/blob/main/docs/security.md#supply-chain).
- **Published carefully.** A release is pushed to GHCR only when `PUBLISH_GHCR` is `true`, and to Docker Hub only when `DOCKERHUB_USERNAME` is set. Both jobs run in the `docker` environment, so if you set reviewers they wait for approval. GHCR uses the workflow's own token with no stored secret; Docker Hub uses a Read & Write access token kept as the `DOCKERHUB_TOKEN` secret, never the account password. The image carries build provenance. See [packaging and releasing](packaging.md#releasing).
- **Pin what you run.** Pull a version tag (or its digest) instead of `latest` in anything that matters, so an update is a decision you make.
- **Rebuild for fixes.** The base image receives security updates. Pull a new release, or rebuild yours, regularly.

## Not included

The image does not scan or sign what you download, and the tags are not signed beyond provenance. Only download from sources you trust.
