import csv
import json
import requests
from flask import jsonify
from flask_restful import Resource
from io import StringIO

from api.common.utils import file_response


ENCODING = 'utf-8'
MAPPINGS_URL = 'http://127.0.0.1:8080'
MAX_YEAR = 2018
MIN_YEAR = 2012


class NodeHistory(Resource):
    @staticmethod
    def get_neighbour(source_year, target_year, node_id):
        content = requests.get('{}/plf_mappings/plf{}_to_plf{}.json'.format(
            MAPPINGS_URL,
            source_year,
            target_year
        )).content.decode(ENCODING)

        mapping = json.loads(content)

        r = mapping[node_id][0]

        content = requests.get('{}/plf_flat_by_code/plf_{}_flat.json'.format(
            MAPPINGS_URL,
            target_year
        )).content.decode(ENCODING)

        print('content {}'.format(target_year))

        if content:
            flat_plf = json.loads(content)
            key = '-'.join(r['codes'])
            info = flat_plf[key]
            r['ae'] = info['ae']
            r['cp'] = info['cp']

        return r

    @staticmethod
    def get(year, node_id):
        """Returns CSV list of available database schemas."""

        print('Was called with {} {}'.format(year, node_id))

        node_id_history = dict()

        # Fetch following years
        for y in range(year, MAX_YEAR):
            node_id_history[y+1] = NodeHistory.get_neighbour(y, y+1, node_id)

        # Fetch previous years
        for y in range(year, MIN_YEAR, -1):
            node_id_history[y-1] = NodeHistory.get_neighbour(y, y-1, node_id)

        return jsonify(node_id_history)
