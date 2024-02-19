FROM python:3.12-alpine

ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache build-base=0.5-r3 librdkafka-dev=2.3.0-r1 && \
    mkdir /install

WORKDIR /src
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -U pip==24.0 setuptools==69.1.0 wheel==0.42.0 && pip install --no-cache-dir --no-warn-script-location -r ./requirements.txt

COPY app/ app/
COPY dataset/ app/

ENV ENABLE_JSON_LOGGING true
ENV PYTHONPATH /src/app
ENV LOG_LEVEL INFO
ENV PRODUCE_INTERVAL 0.1

CMD ["python", "app/main.py"]