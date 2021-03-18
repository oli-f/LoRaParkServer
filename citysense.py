from authlib.integrations.requests_client import OAuth2Session
from oauthlib.oauth2 import LegacyApplicationClient

import requests
from threading import Timer
from collections import defaultdict
import datetime

import logging
logger = logging.getLogger('LoRaPark-citysense')

class BearerAuth(requests.auth.AuthBase):
	def __init__(self, token):
		self.token = token

	def __call__(self, r):
		r.headers['authorization'] = 'Bearer ' + self.token
		return r


class Citysense:
	_registered_sensors = defaultdict(set)
	_token_timer = None
	_sensor_timer = None

	def __init__(self, config, sensors, token_timer=True, sensor_timer=True):
		self._config = config
		self._sensors = sensors

		if token_timer:
			self.enable_token_timer(0)
		else:
			self.refresh_token()

		if sensor_timer:
			self.enable_sensor_timer()

	# self-calling timer for sensor refresh
	def enable_sensor_timer(self):
		self.pull_registered_sensors()

		logger.info("Updating sensor timer...")
		self._sensor_timer = Timer(self._config.get("pull_interval", 60), self.enable_sensor_timer)
		self._sensor_timer.start()

	def disable_sensor_timer(self):
		if self._sensor_timer:
			logger.info("Disabling sensor timer...")
			self._sensor_timer.cancel()

	# self-calling timer for token refresh
	def enable_token_timer(self, timeout):
		logger.info("Refreshing access token...")
		timeout = self.refresh_token()

		logger.info("Updating token timer...")
		self._token_timer = Timer(timeout, self.enable_token_timer)
		self._token_timer.start()

	def disable_token_timer(self):
		if self._token_timer:
			logger.info("Disabling token timer...")
			self._token_timer.cancel()

	def refresh_token(self):
		data = dict(
			grant_type='password',
			username=self._config['username'],
			password=self._config['password']
		)

		#client_id = _config['username']
		#headers = {'Content-Type': 'application/json'}
		#oauth = OAuth2Session(client=LegacyApplicationClient(client_id=client_id))
		#token = oauth.fetch_token(_config['token_url'], username=_config['username'], password=_config['password'], headers=headers)
		#token = oauth.fetch_token(_config['token_url'], json=data, headers=headers)
		# print(token)

		logger.info("Refreshing access token")

		req = requests.post(self._config['token_url'], json=data)
		res = req.json()
		#print('Token: {}'.format(res['access_token']))
		self.auth = BearerAuth(res['access_token'])

		return res['expires_in']

	def _get(self, endpoint, **kwargs):
		return requests.get(self._config['base_url']+endpoint, auth=self.auth, **kwargs)

	# def _post(self, endpoint, **kwargs):
	#	return requests.post(self._config['base_url']+endpoint, auth=self.auth, **kwargs)

	def get_endpoint(self, endpoint, **kwargs):
		return self._get(endpoint, params=kwargs).json()
	
	def get_sensor(self, domain, **kwargs):
		endpoint = self._config['endpoints'][domain]
		return self.get_endpoint(endpoint, **kwargs)

	def register_sensor(self, domain, sensors):
		if type(sensors) is not list: sensors = [ sensors ]

		logger.info("Registering sensors {} to {}".format(sensors, domain))

		self._registered_sensors[domain].update(sensors)

	def unregister_sensor(self, domain, sensors):
		if type(sensors) is not list: sensors = [ sensors ]

		logger.info("Unregistering sensors {} from {}".format(sensors, domain))

		self._registered_sensors[domain].difference_update(sensors)

	def pull_registered_sensors(self, sensors=None, **kwargs): # TODO Timer
		if sensors is None:
			sensors = self._registered_sensors
		elif type(sensors) is str and sensors in self._registered_sensors:
			sensors = self._registered_sensors[sensors]
		elif type(sensors) is list:
			sensors = dict(self._registered_sensors[sensors] for domain in sensors)

		logger.info("Pulling sensors...")

		for domain, sensor_list in sensors.items():
			logger.info("Pulling sensors {} from {}".format(sensor_list, domain))
			data = self.get_sensor(domain, id=sensor_list, count=1, **kwargs)

			for sensor_data in data:
				self._sensors.set(domain=domain, id=sensor_data['id'], data=sensor_data)
