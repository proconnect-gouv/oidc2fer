# ---- base image to inherit from ----
FROM python:3.14.3-slim-trixie AS common

# Install xmlsec1 dependencies required for xmlsec (for SAML)
RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get -y upgrade && \
    apt-get install -qy --no-install-recommends xmlsec1 && \
    rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.11.21 /uv /usr/local/bin/uv

ENV PYTHONUNBUFFERED=1
# Keep uv's venv inside the project so it is easy to mount over in dev
ENV UV_PROJECT_ENVIRONMENT=/app/.venv
# Make the venv's binaries available on PATH so we don't need `uv run` at runtime
ENV PATH="/app/.venv/bin:$PATH"

# Give the "root" group the same permissions AS the "root" user on /etc/passwd
# to allow a user belonging to the root group to add new users; typically the
# docker user (see entrypoint).
RUN chmod g=u /etc/passwd

# We wrap commands run in this container by the following entrypoint that
# creates a user on-the-fly with the container user ID (see USER) and root group
# ID.
COPY ./docker/files/usr/local/bin/entrypoint /usr/local/bin/entrypoint
ENTRYPOINT [ "/usr/local/bin/entrypoint" ]

# Un-privileged user running the application
ARG DOCKER_USER

# Gunicorn
RUN mkdir -p /usr/local/etc/gunicorn
COPY docker/files/usr/local/etc/gunicorn/satosa.py /usr/local/etc/gunicorn/satosa.py

# The default command runs gunicorn WSGI server in satosa's main module
CMD ["gunicorn", "-c", "/usr/local/etc/gunicorn/satosa.py"]

# ---- Development image ----
FROM common AS development

# Install curl (for healthchecks)
RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && apt-get install -qy curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Playwright browsers (webkit only)
ENV PLAYWRIGHT_BROWSERS_PATH=/pw-browsers
# playwright version hardcoded here to avoid depending on pyproject.toml
RUN uv tool run playwright@1.60.0 install --with-deps webkit

# Copy lock file and project metadata first to cache the install layer
COPY pyproject.toml README.md LICENSE uv.lock .python-version .pylintrc ./

# Install all dependencies including dev group
RUN uv sync --locked --group dev --no-install-project

# Copy the rest of the project (satosa runtime config, tests)
COPY src/ src/
COPY satosa/ satosa/
COPY tests/ tests/

# Run uv sync again installing project
RUN uv sync --locked --group dev

RUN chown -R ${DOCKER_USER} /app

# Switch to unprivileged user
USER ${DOCKER_USER}

# ---- Production image (keep last so it is the default target) ----
FROM common AS production

WORKDIR /app

# Copy lock file and project metadata first to cache the install layer
COPY pyproject.toml README.md LICENSE uv.lock .python-version ./
COPY src/ src/

# Install only production dependencies (no dev group)
RUN uv sync --locked --no-group dev

# Copy SATOSA runtime config
COPY satosa/ satosa/

# Switch to unprivileged user
USER ${DOCKER_USER}
