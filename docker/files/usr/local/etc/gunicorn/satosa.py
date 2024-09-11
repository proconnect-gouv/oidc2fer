import datetime
import logging
import os
import sys

import json_log_formatter


class RequestJSONFormatter(json_log_formatter.JSONFormatter):
    """
    Converts Gunicorn request log records to JSON.

    See https://docs.gunicorn.org/en/stable/settings.html#access-log-format
    """

    def json_record(
        self,
        message: str,
        extra: dict[str, str | int | float],
        record: logging.LogRecord,
    ) -> dict[str, str | int | float]:
        # Convert the log record to a JSON object.

        response_time = datetime.datetime.strptime(
            record.args["t"], "[%d/%b/%Y:%H:%M:%S %z]"
        )
        url = record.args["U"]
        if record.args["q"]:
            url += f"?{record.args['q']}"

        return {
            "remote_ip": record.args["h"],
            "method": record.args["m"],
            "path": url,
            "status": str(record.args["s"]),
            "time": response_time.isoformat(),
            "user_agent": record.args["a"],
            "referer": record.args["f"],
            "duration_in_ms": record.args["M"],
            "poppid": record.process,
        }


class DefaultJSONFormatter(json_log_formatter.JSONFormatter):
    """
    Formats a log record as JSON, adding level and pid.
    """

    def json_record(
        self,
        message: str,
        extra: dict[str, str | int | float],
        record: logging.LogRecord,
    ) -> dict[str, str | int | float]:
        payload: dict[str, str | int | float] = super().json_record(
            message, extra, record
        )
        payload["level"] = record.levelname
        payload["pid"] = record.process
        return payload


bind = ["0.0.0.0:8000"]
name = "satosa"
python_path = "/app"
wsgi_app = "oidc2fer.wsgi:app"

# Run
graceful_timeout = 90
timeout = 90

# Logging
# Using '-' for the access log file makes gunicorn log accesses to stdout
accesslog = "-"
# Using '-' for the error log file makes gunicorn log errors to stderr
errorlog = "-"
loglevel = os.environ.get("LOG_LEVEL", "INFO")

logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": True,
    "root": {"level": loglevel.upper(), "handlers": ["json_error"]},
    "loggers": {
        # The gunicorn.error and gunicorn.access loggers are preconfigured with
        # a handler and propagate=False, we need to override this with the
        # default values (no handlers and propagate=True)
        "gunicorn.error": {
            "level": "INFO",
            "handlers": ["json_error"],
            "propagate": False,
            "qualname": "gunicorn.error",
        },
        "gunicorn.access": {
            "level": "INFO",
            "handlers": ["json_request"],
            "propagate": False,
            "qualname": "gunicorn.access",
        },
    },
    "formatters": {
        "json_request": {
            "()": RequestJSONFormatter,
        },
        "json_error": {
            "()": DefaultJSONFormatter,
        },
    },
    "handlers": {
        "json_request": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "json_request",
        },
        "json_error": {
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
            "formatter": "json_error",
        },
    },
}
