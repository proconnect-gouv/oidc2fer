FROM python:3.14.3-slim-trixie

COPY --from=ghcr.io/astral-sh/uv:0.11.21 /uv /usr/local/bin/uv

COPY requirements.txt /app/requirements.txt

WORKDIR /app

RUN uv pip install --system -r requirements.txt

COPY . /app/

HEALTHCHECK --start-period=30s --start-interval=1s CMD curl --fail http://localhost:5000/healthz

CMD ["python", "app.py"]
