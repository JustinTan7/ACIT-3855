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


logger = logging.getLogger('basicLogger')

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

def report_bullet_efficiency(body):
    body["trace_id"] = str(uuid.uuid4())

    logger.info(f"Received bullet efficiency event with a trace id of: {body['trace_id']}")

    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()
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

    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()
    msg = { "type": "ability_efficiency",
            "datetime" :
                datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S"),
            "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f"Returned ability efficiency event with a trace id of: {body['trace_id']}")

    return NoContent, 201



app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)



if __name__ == "__main__":
    app.run(port=8080)