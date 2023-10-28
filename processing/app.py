import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import yaml
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler
import json
import requests



with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def populate_stats():
    """ Periodically update stats """
    logger.info("Start Periodic Processing")

    total_bullet_efficiency_readings = 0
    highest_gun_cost = 0
    lowest_gun_cost = 0
    highest_round_end_magazine_count = 0
    lowest_round_end_magazine_count = 0
    total_ability_efficiency_readings = 0
    highest_ability_cost=  0
    lowest_ability_cost = 0
    highest_round_end_ability_count = 0
    lowest_round_end_ability_count = 0

    try:
        with open(app_config['datastore']['filename'], 'r') as f:
            data=json.load(f)
    
    except:
        data = {
            "total_bullet_efficiency_readings": 0,
            "highest_gun_cost": 0,
            "lowest_gun_cost": 0,
            "highest_round_end_magazine_count": 0,
            "lowest_round_end_magazine_count": 0,
            "total_ability_efficiency_readings": 0,
            "highest_ability_cost": 0,
            "lowest_ability_cost": 0,
            "highest_round_end_ability_count": 0,
            "lowest_round_end_ability_count": 0,
            "total_readings": 0,
            "last_updated": "2023-10-10T09:30:15.448Z"
        }
        with open(app_config['datastore']['filename'], 'w') as f:
            json.dump(data, f, indent=4)
    
    param = {
        "timestamp": data['last_updated']
    }

    bullet_efficiency_query = requests.get(app_config['eventstore1']['url'], params=param)
    ability_efficiency_query = requests.get(app_config['eventstore2']['url'], params=param)


    if bullet_efficiency_query.status_code == 200:
        content_json = bullet_efficiency_query.json()
        total_bullet_efficiency_readings = len(content_json)

        highest_gun_cost = data['highest_gun_cost']
        lowest_gun_cost = data['lowest_gun_cost']
        highest_round_end_magazine_count = data['highest_round_end_magazine_count']
        lowest_round_end_magazine_count = data['lowest_round_end_magazine_count']

        for request_dick in content_json:
            print('i made it')
            if request_dick['gun_cost'] > highest_gun_cost:
                highest_gun_cost = request_dick['gun_cost']

            if request_dick['gun_cost'] < lowest_gun_cost:
                lowest_gun_cost = request_dick['gun_cost']

            if request_dick['round_end_magazine_count'] > highest_round_end_magazine_count:
                highest_round_end_magazine_count = request_dick['round_end_magazine_count']

            if request_dick['round_end_magazine_count'] < lowest_round_end_magazine_count:
                lowest_round_end_magazine_count = request_dick['round_end_magazine_count']
        
        logger.info(f'Amount of bullet efficiency data: {len(content_json)}')
    else:
        logger.error("Did not get a 200 response code.")

    if ability_efficiency_query.status_code == 200:
        content_json = ability_efficiency_query.json()
        total_ability_efficiency_readings = len(content_json)

        highest_ability_cost = data['highest_ability_cost']
        lowest_ability_cost = data['lowest_ability_cost']
        highest_round_end_ability_count = data['highest_round_end_ability_count']
        lowest_round_end_ability_count = data['lowest_round_end_ability_count']

        for request_dick in content_json:
            if request_dick['ability_cost'] > highest_ability_cost:
                highest_ability_cost = request_dick['ability_cost']
            
            if request_dick['ability_cost'] < lowest_ability_cost:
                lowest_ability_cost = request_dick['ability_cost']

            if request_dick['round_end_ability_count'] > highest_round_end_ability_count:
                highest_round_end_ability_count = request_dick['round_end_ability_count']
            
            if request_dick['round_end_ability_count'] < lowest_round_end_ability_count:
                lowest_round_end_ability_count = request_dick['round_end_ability_count']

            logger.info(f"Amount of ability efficiency data: {len(content_json)}")
        else:
            logger.info("Did not get a 200 response code")
    
    current_datetime = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

    data['total_bullet_efficiency_readings'] += total_bullet_efficiency_readings
    data['highest_gun_cost'] = highest_gun_cost
    data['lowest_gun_cost'] = lowest_gun_cost
    data['highest_round_end_magazine_count'] = highest_round_end_magazine_count
    data['lowest_round_end_magazine_count'] = lowest_round_end_magazine_count
    data['total_ability_efficiency_readings'] += total_ability_efficiency_readings
    data['highest_ability_cost'] = highest_ability_cost
    data['lowest_ability_cost'] = lowest_ability_cost
    data['highest_round_end_ability_count'] = highest_round_end_ability_count
    data['lowest_round_end_ability_count'] = lowest_round_end_ability_count
    data['total_readings'] = total_bullet_efficiency_readings + total_ability_efficiency_readings
    data['last_updated'] = current_datetime

    logger.debug(data)

    with open(app_config['datastore']['filename'], 'w') as f:
        json.dump(data, f, indent=4)

    logger.info('Processing period has ended.')


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                  'interval',
                  seconds=app_config['scheduler']['period_sec'])
    sched.start()

def get_stats():
    logger.info("Get request for stats has started")
    
    try:
        with open(app_config['datastore']['filename'], 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        logging.error('Stats file not found')
        return "No such stats exist", 404
    
    logging.debug(dict(data))
    logging.info("Get request completed")
    return dict(data), 200

app = connexion.FlaskApp(__name__, specification_dir='')

app.add_api("openapi.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    # run our standalone event server
    init_scheduler()
    app.run(port=8100, use_reloader=False)