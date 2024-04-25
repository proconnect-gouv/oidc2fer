bind = ["0.0.0.0:8000"]
name = "satosa"
python_path = "/app"

# Run
graceful_timeout = 90
timeout = 90

# Logging
# Using '-' for the access log file makes gunicorn log accesses to stdout
accesslog = "-"
# Using '-' for the error log file makes gunicorn log errors to stderr
errorlog = "-"
loglevel = "info"
