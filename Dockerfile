# ---- base image to inherit from ----
FROM python:3.11-slim-bookworm as base

# Install Install xmlsec1 dependencies required for xmlsec (for SAML)
# Needs to be kept before the `pip install`
RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get install -y \
        pkg-config \
        gcc \
        xmlsec1 \
        libxml2-dev \
        libxmlsec1-dev \
        libxmlsec1-openssl && \
    rm -rf /var/lib/apt/lists/*

# We want the most up-to-date stable pip release
RUN pip install --upgrade pip

# ---- back-end builder image ----
FROM base as back-builder

WORKDIR /builder

# Copy required python dependencies
COPY ./src/satosa /builder

RUN mkdir /install && \
  pip install --prefix=/install .

# ---- Core application image ----
FROM base as core

ENV PYTHONUNBUFFERED=1

# Install required system libs
RUN apt-get update && \
    apt-get install -y \
      gettext && \
  rm -rf /var/lib/apt/lists/*

# Copy entrypoint
COPY ./docker/files/usr/local/bin/entrypoint /usr/local/bin/entrypoint

# Give the "root" group the same permissions as the "root" user on /etc/passwd
# to allow a user belonging to the root group to add new users; typically the
# docker user (see entrypoint).
RUN chmod g=u /etc/passwd

# Copy installed python dependencies
COPY --from=back-builder /install /usr/local

# Copy oidc2fer application (see .dockerignore)
COPY ./src/satosa /app/

WORKDIR /app

# We wrap commands run in this container by the following entrypoint that
# creates a user on-the-fly with the container user ID (see USER) and root group
# ID.
ENTRYPOINT [ "/usr/local/bin/entrypoint" ]

# ---- Production image ----
FROM core as production

# Gunicorn
RUN mkdir -p /usr/local/etc/gunicorn
COPY docker/files/usr/local/etc/gunicorn/satosa.py /usr/local/etc/gunicorn/satosa.py

# Un-privileged user running the application
ARG DOCKER_USER
USER ${DOCKER_USER}

# The default command runs gunicorn WSGI server in satosa's main module
CMD ["gunicorn", "-c", "/usr/local/etc/gunicorn/satosa.py", "satosa.wsgi:app"]

# ---- Development image ----
FROM production as development

# Switch back to the root user to install development dependencies
USER root:root

# Uninstall oidc2fer and re-install it in editable mode along with development
# dependencies
RUN pip uninstall -y oidc2fer
RUN pip install -e .[dev]

# Restore the un-privileged user running the application
ARG DOCKER_USER
USER ${DOCKER_USER}
