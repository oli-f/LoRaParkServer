from collections import defaultdict
import yaml
import os

import logging
logger = logging.getLogger('LoRaPark-sensors')

class Sensors:
	_models = dict()
	_sensors = defaultdict(dict)

	def __init__(self, config):
		self._config = config

		logger.info('Loading sensors config...')
		with open(config['sensors_file']) as yaml_file:
			sensors = yaml.load(yaml_file, Loader=yaml.FullLoader)
			self._sensors = defaultdict(dict, {sensor['id']: defaultdict(dict, sensor) for sensor in sensors})
		logger.info('Done.')

		logger.info('Loading models...')
		for file in os.listdir(config['model_directory']):
			if file.endswith('.yaml'):
				with open(os.path.join(config['model_directory'], file)) as yaml_file:
					self._models[file.removesuffix('.yaml')] = yaml.load(yaml_file, Loader=yaml.FullLoader)
		logger.info('Done.')

	def set(self, domain, id, data):
		self._sensors[id]['values'][domain] = data

	def get_ids(self):
		return list(self._sensors.keys())
	
	def get_domains(self):
		return [{'id': sensor['id'], 'domains': sensor['domains']} for sensor in self._sensors.values()]

	def get_sensors(self, ids=None):
		if ids == None:
			ids = self.get_ids()

		return [self.get_sensor(id) for id in ids]

	def get_sensor(self, id):
		if not id in self._sensors:
			return None
		
		return self._sensors[id]

	def get_sensor_description(self, id):
		sensor =	self.get_sensor(id)
		return {k: sensor[k] for k in sensor if k in ['id', 'name', 'location', 'description', 'domains']}
	
	def get_sensors_description(self, ids=None):
		if ids == None:
			ids = self.get_ids()

		return [self.get_sensor_description(id) for id in ids]

	def get_sensor_values(self, id):
		sensor =	self.get_sensor(id)

		if not sensor:
			return None

		return sensor['values']
	
	def get_sensors_values(self, ids=None):
		if ids == None:
			ids = self.get_ids()

		return [self.get_sensor_values(id) for id in ids]

	def get_sensor_domain(self, id, domain):
		sensor = self.get_sensor_values(id)

		if not sensor:
			return None

		return sensor.get(domain, dict())

	def get_sensor_details(self, id, lang='en'):
		model = self._models.get(lang, dict())
		domains =	self.get_sensor_values(id)

		if not domains:
			return None
		
		def generate():
			for domain, values in domains.items():
				if domain in model:
					domain_model = model.get(domain)
					metrics = domain_model.get('metrics', dict())

					for key, value in values.items():
						if key in metrics.keys():
							metric = metrics.get(key, dict())

							yield {
								'name': (domain_model.get('name', domain) + ': ' if len(domains) > 1 else '') + metric.get('name', key),
								'value': value,
								'unit': metric.get('unit', ''),
								'timestamp': values['timestamp']
							}
				else:
					for key, value in values.items():
						yield {
							'name': domain + ': ' + key,
							'value': value,
							'unit': '',
							'timestamp': values['timestamp']
						}
		return list(generate())
	
	def get_sensors_details(self, ids=None):
		if ids == None:
			ids = self.get_ids()

		return [self.get_sensor_details(id) for id in ids]