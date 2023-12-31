import logging
import logging.config
import connexion
from connexion import NoContent
import json
from datetime import datetime
import requests
import yaml
import uuid
from pykafka import KafkaClient
import time
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

max_retries = (app_config["kafka"]["max_retries"])
current_retry = 0
retry_sleep_interval = (app_config["kafka"]["retry_sleep_interval"])
hostname = "%s:%d" % (app_config["events"]["hostname"],
                        app_config["events"]["port"])
while current_retry < max_retries:
    logger.info(f"Connecting to Kafka...\nCurrent retry count: {current_retry + 1}")
    try:
        client = KafkaClient(hosts=hostname)
        topic = client.topics[str.encode(app_config["events"]["topic"])]
        logger.info(f"Successfully connected to Kafka (attempt: {current_retry + 1})")
        producer = topic.get_sync_producer()
        break
    except Exception as e:
        logger.error(f"Connection to Kafka failed {e}.")
        current_retry += 1
        time.sleep(retry_sleep_interval)
        
def report_bullet_efficiency(body):
    body["trace_id"] = str(uuid.uuid4())

    logger.info(f"Received bullet efficiency event with a trace id of: {body['trace_id']}")

    msg = { "type": "bullet_efficiency",
            "datetime" :
                datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S"),
            "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f"Returned bullet efficiency event with a trace id of: {body['trace_id']}")

    return NoContent, 201



def report_ability_efficiency(body):
    body["trace_id"] = str(uuid.uuid4())

    logger.info(f"Received ability efficiency event with a trace id of: {body['trace_id']}")

    msg = { "type": "ability_efficiency",
            "datetime" :
                datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S"),
            "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f"Returned ability efficiency event with a trace id of: {body['trace_id']}")

    return NoContent, 201

def health_check():
    return 200


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", base_path="/receiver", strict_validation=True,
validate_responses=True)



if __name__ == "__main__":
    app.run(port=8080)