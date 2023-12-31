import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from ability_efficiency import AbilityEfficiency
from bullet_efficiency import BulletEfficiency
import datetime
import yaml
import logging.config
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from sqlalchemy import and_
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

user = app_config['datastore']['user']
password = app_config['datastore']['password']
hostname = app_config['datastore']['hostname']
port = app_config['datastore']['port']
db = app_config['datastore']['db']


DB_ENGINE = create_engine(f"mysql+pymysql://{user}:{password}@{hostname}:{port}/{db}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)



def report_bullet_efficiency(body):
    """ Receives a bullet efficiency reading """

    logger.info(f'Connecting to DB. Hostname: {hostname}, Port: {port}')
    
    session = DB_SESSION()


    be = BulletEfficiency(body['player_id'],
                          body['gun_id'],
                          body['round_start_magazine_count'],
                          body['round_end_magazine_count'],
                          body['gun_cost'],
                          body['trace_id'])

    session.add(be)
    
    session.commit()
    session.close()

  
    logger.debug(f'Stored event bullet_efficiency request with a trace id of {body["trace_id"]}')

    return NoContent, 201


def report_ability_efficiency(body):
    """ Receives an ability efficiency reading """

    session = DB_SESSION()

    ae = AbilityEfficiency(body['player_id'],
                           body['agent_id'],
                           body['round_start_ability_count'],
                           body['round_end_ability_count'],
                           body['ability_cost'],
                           body['trace_id'])

    session.add(ae)

    session.commit()
    session.close()

    logger.debug(f'Stored event ability efficiency request with a trace id of {body["trace_id"]}')

    return NoContent, 201

def get_bullet_efficiency(start_timestamp, end_timestamp):
    """ Gets new bullet efficiency readings after the timestamp """

    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ", )
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ", )
                                                    
    readings = session.query(BulletEfficiency).filter(and_(BulletEfficiency.date_created >= start_timestamp_datetime, BulletEfficiency.date_created < end_timestamp_datetime))

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for Bullet Efficiency readings after %s returns %d results" %
                (start_timestamp, len(results_list)))

    return results_list, 200


def get_ability_efficiency(start_timestamp, end_timestamp):
    """ Gets new bullet efficiency readings after the timestamp """

    session = DB_SESSION()

    start_timestamp_datetime = datetime.datetime.strptime(start_timestamp, "%Y-%m-%dT%H:%M:%SZ", )
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ", )
                                                    
    readings = session.query(AbilityEfficiency).filter(and_(AbilityEfficiency.date_created >= start_timestamp_datetime, AbilityEfficiency.date_created < end_timestamp_datetime))

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())

    session.close()

    logger.info("Query for Ability Efficiency readings after %s returns %d results" %
                (start_timestamp, len(results_list)))

    return results_list, 200

def process_messages():
    """ Process event messages """
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
            break
        except Exception as e:
            logger.error(f"Connection to Kafka failed {e}.")
            current_retry += 1
            time.sleep(retry_sleep_interval)

    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)
    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)

        payload = msg["payload"]
        session = DB_SESSION()

        if msg["type"] == "bullet_efficiency":
            bullet = BulletEfficiency(payload['player_id'],
                                      payload['gun_id'],
                                      payload['round_start_magazine_count'],
                                      payload['round_end_magazine_count'],
                                      payload['gun_cost'],
                                      payload['trace_id'])
            session.add(bullet)
    
            session.commit()
            session.close()

        elif msg["type"] == "ability_efficiency":
            ability = AbilityEfficiency(payload['player_id'],
                           payload['agent_id'],
                           payload['round_start_ability_count'],
                           payload['round_end_ability_count'],
                           payload['ability_cost'],
                           payload['trace_id'])

            session.add(ability)

            session.commit()
            session.close()

        consumer.commit_offsets()
    
def health_check():
    return 200

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", base_path="/storage", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)