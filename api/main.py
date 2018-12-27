import csv
import json
import os
import requests
from flask import jsonify, send_file
from flask_restful import Resource
from io import StringIO


ROOT_NAMES = ['PLF', 'REC']
SOURCE_INFO = {
    'PLF': {
        'folder': 'plf',
        'min_year': 2016,
        'max_year': 2019,
    },
    'Recettes': {
        'folder': 'recettes',
        'min_year': 2018,
        'max_year': 2019,
    }
}


class NodeHistory(Resource):
    @staticmethod
    def get_neighbour(source, source_year, target_year, node_id):
        if node_id in ['PLF', 'REC']:
            return {
                'codes': [node_id],
                'distance': 0.0,
                'libelles': [node_id]
            }

        filename = './resources/mappings/{}/{}_to_{}.json'.format(
            SOURCE_INFO[source]['folder'],
            source_year,
            target_year
        )

        if os.path.exists(filename):
            with open(filename, 'r') as mapping_file:
                content = mapping_file.read()

            mapping = json.loads(content)

            if node_id in mapping:
                r = mapping[node_id][0]
            else:
                r = dict({
                    'distance': None,
                    'codes': [],
                    'libelles': [],
                    'error': 'Not found'
                })
        else:
            r = dict({
                'distance': None,
                'codes': [],
                'libelles': [],
                'error': 'Not found'
            })

        return r

    @staticmethod
    def get_node_data(source, year, node):
        filename = './resources/flat/{}/{}.json'.format(
            SOURCE_INFO[source]['folder'],
            year
        )

        if os.path.exists(filename):
            with open(filename, 'r') as flat_file:
                content = flat_file.read()

            if content:
                flat_plf = json.loads(content)
                key = node['code']

                if key in flat_plf:
                    info = flat_plf[key]
                    node['data'] = info
                else:
                    node['data'] = dict()
        else:
            node['data'] = dict()

    @staticmethod
    def get(source, year, node_id):
        """Returns CSV list of available database schemas."""

        node_id_history = {}
        node_id_history[year] = {
            'code': node_id,
            'selected': True,
        }

        if node_id not in ROOT_NAMES:
            # Fetch following years' codes
            for y in range(year, SOURCE_INFO[source]['max_year']):
                node_id_history[y+1] = NodeHistory.get_neighbour(source, y, y+1, node_id)

            # Fetch previous years' codes
            for y in range(year, SOURCE_INFO[source]['min_year'], -1):
                node_id_history[y-1] = NodeHistory.get_neighbour(source, y, y-1, node_id)
        else:
            for y in range(SOURCE_INFO[source]['min_year'], SOURCE_INFO[source]['max_year']+1):
                if y != year:
                    node_id_history[y] = {
                        'code': node_id,
                    }

        # Fetch ae and cp for each year if possible
        for y in node_id_history:
            NodeHistory.get_node_data(source, y, node_id_history[y])

        print(node_id_history)
        return jsonify(node_id_history)

class FileHandler(Resource):
    @staticmethod
    def get(source, year):
        return send_file('./resources/hierarchy/{}/{}.json'.format(
            SOURCE_INFO[source]['folder'],
            year
        ))
