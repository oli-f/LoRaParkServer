#!/usr/bin/env python

import os
import yaml

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('LoRaPark')

from citysense import Citysense
from rest import Rest
from sensors import Sensors
from rules import Rules

logger.info('Loading config...')
with open('config.yaml') as yaml_file:
	config = yaml.load(yaml_file, Loader=yaml.FullLoader)
logger.info('Done')

logger.info('Loading sensors module...')
sensors = Sensors(config['sensors'])
logger.info('Done')

logger.info('Starting rules module...')
rules = Rules(config['rules'])
logger.info('Done')

logger.info('Loading citysense module...')
citysense = Citysense(config['citysense'], sensors)
logger.info('Done')

#req = citysense.get_endpoint('weatherstation', id='davis-013d4d',start='2021-02-16T13:56:56.994Z')
#print(req)

#req = citysense.get_endpoint('hochwasser', id=['ultrasonic1', 'ultrasonic2'], start='2021-02-16T13:56:56.994Z')
#print(req)

#citysense.register_sensor('weather_station', 'davis-013d4d')
#citysense.register_sensor('co2', 'elsysco2-045184')
#citysense.register_sensor('co2', 'elsysco2-048e67')

logger.info('Registering sensors')
for sensor in sensors.get_domains():
	for domain in sensor['domains']:
		citysense.register_sensor(domain, sensor['id'])
logger.info('Done')

logger.info('Pulling initial citysense...')
citysense.pull_registered_sensors()
logger.info('Done')

logger.info('Starting rest API...')
rest = Rest(config['rest'], sensors, rules)
rest.run(host='0.0.0.0')

logger.info('Shutting down...')
citysense.disable_token_timer()
citysense.disable_sensor_timer()
logger.info('Done')
