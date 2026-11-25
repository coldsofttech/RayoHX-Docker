# The RayoHX command line as a small, non-root image. It runs the same `rayohx` command as the
# Python package; there is no second downloader in here.
#
#   docker run --rm -v "$PWD/downloads:/output" -v rayohx-work:/workspace \
#       ghcr.io/coldsofttech/rayohx download https://example.com/master.m3u8 -o /output/movie.mp4
#
# Muxing is built in, so FFmpeg is not installed. See docs/docker.md.
#
# The image installs the published rayohx-cli package from PyPI (which brings the rayohx library),
# so the build context holds nothing. Choose the version with RAYOHX_CLI_VERSION:
#
#   docker build -t rayohx .
#   docker build --build-arg RAYOHX_CLI_VERSION=0.1.0 -t rayohx .

ARG PYTHON_VERSION=3.15

# --- build: put the command line and its dependencies in a virtual environment ----------------
FROM python:${PYTHON_VERSION}-slim AS build

ARG RAYOHX_CLI_VERSION=0.1.0

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-compile "rayohx-cli==${RAYOHX_CLI_VERSION}" \
    && /opt/venv/bin/pip uninstall --yes pip

# --- run: the same base without compilers or pip -----------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS runtime

ARG VERSION=0.0.0
LABEL org.opencontainers.image.title="RayoHX" \
      org.opencontainers.image.description="HLS download engine and command line" \
      org.opencontainers.image.source="https://github.com/coldsofttech/RayoHX-Docker" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.version="${VERSION}"

# Take the patched zlib (CVE-2026-85091) even when the base image is older than the fix; this is the
# only package upgraded, and the package lists are removed again to keep the image small.
RUN apt-get update \
    && apt-get install --yes --no-install-recommends --only-upgrade zlib1g \
    && rm -rf /var/lib/apt/lists/*

# The base image's own pip bundles an older msgpack (CVE-2026-114613); a current pip carries the fix.
# setuptools and wheel are build tools the command never uses, so they are removed (CVE-2025-47273).
RUN python -m pip install --no-cache-dir --disable-pip-version-check --upgrade pip \
    && python -m pip uninstall --yes setuptools wheel

# A fixed, unprivileged user, so files written to a mounted folder have a predictable owner.
RUN groupadd --system --gid 10001 rayohx \
    && useradd --system --uid 10001 --gid rayohx --no-create-home --shell /usr/sbin/nologin rayohx \
    && mkdir /output /workspace \
    && chown rayohx:rayohx /output /workspace

COPY --from=build /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    RAYOHX_WORKSPACE=/workspace \
    NO_COLOR=1

USER 10001:10001
WORKDIR /output
VOLUME ["/output", "/workspace"]

ENTRYPOINT ["rayohx"]
CMD ["--help"]
