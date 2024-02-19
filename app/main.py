import logging
import os
import sys
import time
import json
import csv

import json_logging
from confluent_kafka import Producer
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer


def setup_logging():
    ENABLE_JSON_LOGGING = os.environ.get("ENABLE_JSON_LOGGING", "true")
    json_logging_enabled = False if ENABLE_JSON_LOGGING == "false" else True
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    logger = logging.getLogger(__name__)
    logger.setLevel(LOG_LEVEL)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    json_logging.init_non_web(enable_json=json_logging_enabled)
    return logger


def load_avro_schema_from_file(schema_file_path):
    # Open the JSON schema file and load the schema as a dictionary
    with open(schema_file_path, 'r') as schema_file:
        schema = schema_file.read()
    return schema


TOPIC = os.environ.get("TOPIC")
TOPIC_WITH_SCHEMA = os.environ.get("TOPIC_WITH_SCHEMA")
BOOTSTRAP_SERVER = os.environ.get("BOOTSTRAP_SERVER")
SCHEMA_REGISTRY_URL = os.environ.get("SCHEMA_REGISTRY_URL")

_logger = setup_logging()

script_dir = os.path.realpath(os.path.dirname(__file__))
avro_schema = load_avro_schema_from_file(os.path.join(script_dir, 'schema.avsc'))

config = {'bootstrap.servers': BOOTSTRAP_SERVER}

_logger.info("Starting producer with config: %s", config)

producer = Producer(config)

avro_config = {**config,
               'schema.registry.url': SCHEMA_REGISTRY_URL
               }

_logger.info("Starting avro producer with config: %s", avro_config)

avro_producer = AvroProducer(avro_config, default_value_schema=avro_schema)

with open(os.path.join(script_dir, 'dataset.csv')) as file:
    reader = csv.DictReader(file, delimiter=",")
    for row in reader:
        producer.produce(TOPIC, value=json.dumps(row))
        time.sleep(5)
