import argparse
import os
import json
import random
import ssl
import urllib.parse
import requests

from utils.io_utils import *
from config.data_config import *


def fetch_usda_data():
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/sparql-results+json"}
    query = {"query": USDA_SPARQL_QUERY}
    response = requests.post(USE_ENDPOINT_URL, data=urllib.parse.urlencode(query), headers=headers)
    results = json.loads(response.content)['results']['bindings']
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', required=True, type=str, help='path to the output dir')
    opt = vars(parser.parse_args())

    ssl._create_default_https_context = ssl._create_unverified_context


    results = fetch_usda_data()
    f_ent = open(os.path.join(opt['output'], 'usda_entities.json'), 'w')
    f_kg = open(os.path.join(opt['output'], 'usda_subgraphs.json'), 'w')

    for each in results:
        food_uri = each['food_V']['value']
        food_label = each['description']['value']
        graph = {'uri': food_uri, 'name': [food_label], 'alias': [], 'type': ['ingredient'], 'neighbors':{}}
        for attr, val in each.items():
            if attr.split('_')[-1] == 'E' or attr in {'id', 'food_V', 'description'}:
                continue

            datatype = val['datatype'].split('#')[-1]
            if datatype == 'integer':
                val_type = ['num']
            elif datatype == 'float':
                val_type = ['num']
            else:
                val_type = []

            value_graph = {'attr_val': {'name': [val['value']], 'uri': each['%s_E'%attr]['value'], 'alias': [], 'type': val_type}}
            graph['neighbors'][attr] = [value_graph]

        f_ent.write(json.dumps({'id': food_uri, 'name': food_label}) + '\n')
        f_kg.write(json.dumps({food_label: graph}) + '\n')

    f_ent.close()
    f_kg.close()
