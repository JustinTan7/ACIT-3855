import connexion
from connexion import NoContent
from datetime import datetime
import logging.config
import yaml
import datetime
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from flask_cors import CORS, cross_origin
import os

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

hostname = app_config['events']['hostname']

def get_bullet_efficiency_stats(index):
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)

    logger.info("Retrieving bullet efficiency at index %d" % index)

    message_count = 0

    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)

            if msg['type'] == 'bullet_efficiency':
                if message_count == index:
                    return { "message": msg }, 200
                else:
                    message_count += 1

    except:
        logger.error("No more messages found")

    logger.error("Could not find bullet efficiency at index %d" % index)
    return { "message": "Not found"}, 404

def get_ability_efficiency_stats(index):
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config['events']['topic'])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)

    logger.info("Retrieving ability efficiency at index %d" % index)

    message_count = 0

    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] == 'ability_efficiency':
                if message_count == index:
                    return { "message": msg }, 200
                else:
                    message_count += 1

    except:
        logger.error("No more messages found")

    logger.error("Could not find ability efficiency at index %d" % index)
    return { "message": "Not found"}, 404

app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'

app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110, use_reloader=False)