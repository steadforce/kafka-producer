FROM python:3.10-alpine

ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache build-base librdkafka-dev && \
    mkdir /install

COPY requirements.txt ./requirements.txt
RUN pip install -U pip setuptools wheel && pip install --no-warn-script-location -r ./requirements.txt

COPY app/ /src/app/
COPY dataset/ /src/app/
WORKDIR /src

ENV ENABLE_JSON_LOGGING true
ENV PYTHONPATH /src/app
ENV LOG_LEVEL INFO

ENV TOPIC "test"
ENV TOPIC_WITH_SCHEMA "test"
ENV BOOTSTRAP_SERVER "test"
ENV SCHEMA_REGISTRY_URL "test"

CMD ["python", "app/main.py"]