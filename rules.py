from collections import defaultdict
import json
import os

import logging
logger = logging.getLogger('LoRaPark-rules')

class Rules:
	_rules = dict()

	def __init__(self, config):
		self._config = config

		logger.info('Loading rules...')
		for file in os.listdir(config['rules_directory']):
			if file.endswith('.json'):
				with open(os.path.join(config['rules_directory'], file)) as json_file:
					rule = json.load(json_file)
					id = file.removesuffix('.json')
					rule['id'] = id
					self._rules[id] = rule
		logger.info('Done.')

	def get_ids(self):
		return list(self._rules.keys())
	
	def get_rules(self, ids=None):
		if ids == None:
			ids = self.get_ids()

		return [self.get_rule(id) for id in ids]

	def get_rule(self, id):
		if not id in self._rules:
			return None
		
		return self._rules[id]

	def get_rule_description(self, id):
		rule = self.get_rule(id)

		if not rule:
			return None

		return {k: rule[k] for k in rule if k in ['id', 'name', 'description']}
	
	def get_rules_description(self, ids=None):
		if ids == None:
			ids = self.get_ids()

		return [self.get_rule_description(id) for id in ids]
