FROM python:3.14

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

HEALTHCHECK --start-period=30s --start-interval=1s CMD curl --fail http://localhost:5000/healthz

CMD ["python", "app.py"]
