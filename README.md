# An OIDC Gateway to the french SAML education federation (RENATER)

As of today, this project is **not yet ready for production**. Expect breaking changes.

## Getting started

### Prerequisite

Make sure you have a recent version of Docker and [Docker
Compose](https://docs.docker.com/compose/install) installed on your laptop:

```bash
$ docker -v
  Docker version 20.10.2, build 2291f61

$ docker compose -v
  docker compose version 1.27.4, build 40524192
```

> ⚠️ You may need to run the following commands with `sudo` but this can be
> avoided by assigning your user to the `docker` group.

### Project bootstrap

The easiest way to start working on the project is to use GNU Make:

```bash
$ make bootstrap
```

This command builds the `app-dev` container, installs dependencies, and sets up
the development services.  It's a good idea to use this command each time
you are pulling code from the project repository to avoid dependency-related or
migration-related issues.

Your Docker services should now be up and running 🎉

Note that if you need to run them afterward, you can use the eponym Make rule:

```bash
$ make run
```

Finally, you can check all available Make rules using:

```bash
$ make help
```

## Creating a release

1. Update `CHANGELOG.md` to change the `Unreleased` header to the new version
number and date.
2. Commit and push to `main`.
3. Create a `vX.Y.Z` tag from `main` and push it.

## Contributing

This project is intended to be community-driven, so please, do not hesitate to
get in touch if you have any question related to our implementation or design
decisions.

## License

This work is released under the MIT License (see [LICENSE](./LICENSE)).

