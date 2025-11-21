# ---- base image to inherit from ----
FROM python:3.11.12-slim-bookworm AS common

# Install xmlsec1 dependencies required for xmlsec (for SAML)
# Needs to be kept before the `pip install`
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -qy --no-install-recommends xmlsec1 && \
    rm -rf /var/lib/apt/lists/*

# We want the most up-to-date stable pip release
RUN pip install --upgrade pip

ENV PYTHONUNBUFFERED=1

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
RUN apt-get update && apt-get install -qy curl

# Playwright browsers
ENV PLAYWRIGHT_BROWSERS_PATH=/pw-browsers
RUN pip install playwright
RUN playwright install --with-deps webkit

# Test root CA
COPY env.d/development/certs/mkcert-root-ca.pem /usr/local/share/ca-certificates/mkcert-root-ca.crt
RUN update-ca-certificates

WORKDIR /app

# Copy project file to list dependencies
COPY ./src/satosa/pyproject.toml /app/

# Create empty module directory to please pip install --editable
# (without this, the oidc2fer module will not be importable because
#  pip --editable scans the directory to create its "links")
RUN mkdir -p /app/oidc2fer

# Install oidc2fer in editable mode along with development dependencies
RUN pip install --editable .[dev]

# Copy oidc2fer sources (see .dockerignore)
COPY ./src/satosa /app/

# Switch to unprivileged user
USER ${DOCKER_USER}

# ---- Production image (keep last so it is the default target) ----
FROM common AS production

# Copy oidc2fer application (see .dockerignore)
COPY ./src/satosa /app/

WORKDIR /app

RUN pip install .

# Switch to unprivileged user
USER ${DOCKER_USER}
