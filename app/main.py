import itertools
import logging
import os
import random
import sys
import time
import json
import csv

import json_logging
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer


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


def create_key(row: dict) -> str:
    return f"{row["Index"]}-{row["ToolId"]}-{row["Machine"]}"


def manipulate_row(row: dict) -> dict:
    manipulate = random.choices([True, False], [0.1, 0.9], k=1)[0]
    if not manipulate:
        return row
    _logger.info("Message is MANIPULATED!")
    return_empty = random.choices([True, False], [0.1, 0.9], k=1)[0]
    if return_empty:
        return {}
    dict_keys = list(row.keys())
    # numbers of dict keys to manipulate
    number_manipulated_values = random.choices(list(itertools.chain(*[[i] * (len(dict_keys) +1 -i) for i in range(1, len(dict_keys)+1)])), k=1)[0]
    # keys to manipulate
    manipulate_cols = random.sample(dict_keys, k=number_manipulated_values)
    for col in manipulate_cols:
        manipulate_by = random.choices([None, "null", "n.a.", "drop_column"], [0.5, 0.2 ,0.2, 0.1], k=1)[0]
        if manipulate_by == "drop_column":
            del row[col]
        else:
            row[col] = manipulate_by
    return row

TOPIC = os.environ.get("TOPIC")
TOPIC_WITH_SCHEMA = os.environ.get("TOPIC_WITH_SCHEMA")
BOOTSTRAP_SERVER = os.environ.get("BOOTSTRAP_SERVER")
SCHEMA_REGISTRY_URL = os.environ.get("SCHEMA_REGISTRY_URL")

PRODUCE_INTERVAL = float(os.environ.get("PRODUCE_INTERVAL"))

_logger = setup_logging()

script_dir = os.path.realpath(os.path.dirname(__file__))
avro_schema = load_avro_schema_from_file(os.path.join(script_dir, 'schema.avsc'))

schema_registry_conf = {'url': SCHEMA_REGISTRY_URL}
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

avro_serializer = AvroSerializer(schema_registry_client, avro_schema)
producer_conf = {'bootstrap.servers': BOOTSTRAP_SERVER}


_logger.info("Starting producer with config: %s", producer_conf)

producer = Producer(producer_conf)

with open(os.path.join(script_dir, 'dataset.csv')) as file:
    reader = csv.DictReader(file, delimiter=",")
    for row in reader:
        key = create_key(row)
        row = manipulate_row(row)
        producer.produce(TOPIC, key=key, value=json.dumps(row))
        _logger.info("Produced message.")
        time.sleep(PRODUCE_INTERVAL)
    _logger.info("End of stream reached.")
    # Wait for outstanding messages to be delivered
    producer.flush()
    exit(0)

