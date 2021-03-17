import flask

import logging
logger = logging.getLogger('LoRaPark-rest')

class Rest(flask.Flask):
	def __init__(self, config, sensors, rules):
		super().__init__(__name__)
		self._config = config
		self._sensors = sensors
		self._rules = rules

		self.config['DEBUG'] = config.get('debug', False)

		self.add_url_rule('/sensors', 'sensors', self.get_sensors)
		self.add_url_rule('/sensors/raw', 'sensors raw', self.get_sensors_raw)

		self.add_url_rule('/sensor/<id>/raw', 'sensor raw', self.get_sensor_raw)
		self.add_url_rule('/sensor/<id>/details', 'sensor details', self.get_sensor_details)
		self.add_url_rule('/sensor/<id>/details/<lang>', 'sensors details land', self.get_sensor_details)

		self.add_url_rule('/rules', 'rules', self.get_rules)
		self.add_url_rule('/rule/<id>', 'rule', self.get_rule)

	def make_response(self, rv):
		if rv is None or type(rv) in [bool, list, str, dict, tuple]:
			return super(Rest, self).make_response(flask.jsonify(rv))
		else:
			return super(Rest, self).make_response(rv)

	def get_sensors(self):
		return self._sensors.get_sensors_description()
	
	def get_sensors_raw(self):
		ids = flask.request.args.getlist('id')
		return {id: self._sensors.get_sensor_values(id) for id in ids}

	def get_sensor_raw(self, id):
		return self._sensors.get_sensor_values(id)

	def get_sensor_details(self, id, lang='en'):
		return self._sensors.get_sensor_details(id, lang)

	def get_rules(self):
		return self._rules.get_rules_description()

	def get_rule(self, id):
		return self._rules.get_rule(id)
