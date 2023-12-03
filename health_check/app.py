import connexion
from connexion import NoContent
from datetime import datetime
import logging.config
import yaml
import json
from apscheduler.schedulers.background import BackgroundScheduler
import requests
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

services = ['Receiver', 'Storage', 'Processing', 'Audit']
health_check_endpoint = '/health'
poll_interval = 20
timeout = 5
port = 8120

status_data = {
    'Receiver': 'Unknown',
    'Storage': 'Unknown',
    'Processing': 'Unknown',
    'Audit': 'Unknown',
    'last_update': None
}

def health_check():
    for service in services:
        logger.info(f"Attempting to get health check from {service} service.")
        try:
            response = requests.get(f'http://sbajustin.eastus.cloudapp.azure.com:{port}/{service}{health_check_endpoint}', timeout=timeout)
            if response.status_code == 200:
                status_data[service] = 'Running'
            else:
                status_data[service] = 'Down'
        except requests.RequestException:
            status_data[service] = 'Down'
        logging.info(f"{service} service status updated: {status_data[service]}")

    # Update the last_update timestamp after checking all services
    status_data['last_update'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')

    save_to_json(status_data, "health_check_data.json")

    # Construct the response in the required format
    response_data = {
        service.lower(): status
        for service, status in status_data.items() if service != 'last_update'
    }
    response_data['last_update'] = status_data['last_update']

    return response_data, 200


def health_check_service():
    while True:
        # Poll the health_check endpoint of each service
        for service in services:
            try:
                response = requests.get(f'http://sbajustin.eastus.cloudapp.azure.com:{port}/health/{service}')
                logger.info(f"Health check for {service}: {response.status_code}")
            except requests.RequestException as e:
                logger.error(f"Error during health check for {service}: {str(e)}")

        time.sleep(poll_interval)

def save_to_json(data, filename):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(health_check,
                  'interval',
                  seconds=app_config['scheduler']['period_sec'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml", base_path="/health_check", strict_validation=True,
            validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=port, use_reloader=False)
