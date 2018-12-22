import csv
import json
import requests
from flask import jsonify
from flask_restful import Resource
from io import StringIO

from api.common.utils import file_response


ENCODING = 'utf-8'
MAPPINGS_URL = 'http://127.0.0.1:8080'
MAX_YEAR = 2019
MIN_YEAR = 2016


class NodeHistory(Resource):
    @staticmethod
    def get_neighbour(source_year, target_year, node_id):
        if node_id in ['PLF', 'REC']:
            return {
                'codes': [node_id],
                'distance': 0.0,
                'libelles': [node_id]
            }

        content = requests.get('{}/plf_mappings/plf_{}_to_plf_{}.json'.format(
            MAPPINGS_URL,
            source_year,
            target_year
        )).content.decode(ENCODING)

        mapping = json.loads(content)

        r = mapping[node_id][0]

        return r

    @staticmethod
    def get_node_information(year, node):
        content = requests.get('{}/plf_flat_by_code/plf_{}_flat.json'.format(
            MAPPINGS_URL,
            year
        )).content.decode(ENCODING)

        print('content {}'.format(year))

        if content:
            flat_plf = json.loads(content)
            key = '-'.join(node['codes'])
            print(key)

            if key in flat_plf:
                info = flat_plf[key]
                node['ae'] = info['ae']
                node['cp'] = info['cp']
            else:
                node['ae'] = 0
                node['cp'] = 0

    @staticmethod
    def get(year, node_id):
        """Returns CSV list of available database schemas."""

        print('Was called with {} {}'.format(year, node_id))

        node_id_history = {}
        node_id_history[year] = {
            'codes': node_id.split('-')
        }

        # Fetch following years' codes
        for y in range(year, MAX_YEAR):
            node_id_history[y+1] = NodeHistory.get_neighbour(y, y+1, node_id)

        # Fetch previous years' codes
        for y in range(year, MIN_YEAR, -1):
            node_id_history[y-1] = NodeHistory.get_neighbour(y, y-1, node_id)

        # Fetch ae and cp for each year if possible
        for y in node_id_history:
            NodeHistory.get_node_information(y, node_id_history[y])

        return jsonify(node_id_history)
