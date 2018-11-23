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
    def get_index(source_year, target_year, index, future=True):
        content = requests.get('{}/plf_mappings/plf{}_to_plf{}.csv'.format(
            MAPPINGS_URL,
            source_year,
            target_year
        )).content.decode(ENCODING)

        for row in csv.reader(StringIO(content), delimiter=';'):
            source_index, target_index, distance = row
            source_index = int(source_index)
            target_index = int(target_index)
            distance = float(distance)

            if future:
                if source_index == index:
                    return(target_index)
            else:
                if target_index == index:
                    return(source_index)

        return None

    @staticmethod
    def get(year, node_id):
        """Returns CSV list of available database schemas."""

        print('Was called with {} {}'.format(year, node_id))

        node_id_history = {}
        for current_year in range(MIN_YEAR, MAX_YEAR+1):
            node_id_history[current_year] = {'index': None}
        node_id_history[year] = {'index': node_id}

        # Fetch mapping in the future
        for current_year in range(year, MAX_YEAR):
            print(current_year, current_year+1)
            next_index = NodeHistory.get_index(current_year, current_year+1, node_id_history[current_year]['index'], future=True)
            if next_index:
                node_id_history[current_year+1]['index'] = next_index
            else:
                break

        # Fetch mapping in the past
        for current_year in list(reversed(range(MIN_YEAR, year))):
            print(current_year, current_year+1)
            next_index = NodeHistory.get_index(current_year, current_year+1, node_id_history[current_year+1]['index'], future=False)
            if next_index:
                node_id_history[current_year]['index'] = next_index
            else:
                break

        # Add names
        for current_year in node_id_history:
            content = requests.get('{}/plf_all_nodes/plf{}.csv'.format(
                MAPPINGS_URL,
                current_year
            )).content.decode(ENCODING)

            for row_index, row in enumerate(csv.reader(StringIO(content), delimiter=';')):
                if row_index == 0:
                    continue
                node_index = int(row[0])
                if node_index == node_id_history[current_year]['index']:
                    node_id_history[current_year]['type_mission'] = row[1]
                    node_id_history[current_year]['mission'] = row[3]
                    node_id_history[current_year]['programme'] = row[5]
                    node_id_history[current_year]['action'] = row[7]
                    node_id_history[current_year]['sous-action'] = row[9]

        return jsonify(node_id_history)
