# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.11] - 2025-11-24
- remove setuptools, wheel and pip from production Docker image

## [1.0.10] - 2025-11-21
- rename helmfile.yaml for compatibility with helmfile 1.x

## [1.0.9] - 2025-10-03
- map SAML entity IDs to SIRET (#34)
- include ACR claim in ID token only if requested (#32)

## [1.0.8] - 2025-09-10
- fix secrets submodule path following move to `proconnect-gouv` organization
- update other references to `numerique-gouv` organization
- publish Docker images at ghcr.io/proconnect-gouv/oidc2fer

## [1.0.7] - 2025-05-07
- remove unused APT dependencies
- upgrade to gunicorn 23.0.0

## [1.0.6] - 2025-03-11
- upgrade to SATOSA 8.5.1
- allow faculty, staff, employee, researcher, teacher affiliations

## [1.0.5] - 2025-03-06
- add allowlist for URL paths to nginx ingress
- allow customizing log levels per logger

## [1.0.4] - 2024-09-11
- serve static files

## [1.0.3] - 2024-09-02
- set SAML signing algorithm to use SHA256 for compatibility with AccessCheck

## [1.0.2] - 2024-07-22
- check the scope of returned eduPersonPrincipalNames
- require "employee" value in eduPersonAffiliation

## [1.0.1] - 2024-06-04
- enable JSON logging and LOG_LEVEL environment variable
- add production configuration

## [1.0.0] - 2024-05-16
- add Helm chart for deployment
- provide Docker images on https://hub.docker.com/r/lasuite/oidc2fer
- install SATOSA
