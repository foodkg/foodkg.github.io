import argparse
import os
import json
import random
import ssl
from SPARQLWrapper import SPARQLWrapper, JSON

from config.data_config import *
from utils.io_utils import *


def fetch_all_tags(sparql):
    query = '''
    PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
    SELECT DISTINCT ?tag {
        ?r recipe-kb:tagged ?tag .
    }'''

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    tags = [x['tag']['value'] for x in results['results']['bindings']]
    return tags

def fetch_all_dishes(sparql, tag):
    query = '''
        PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
        SELECT DISTINCT ?r ?name {{
            ?r recipe-kb:tagged {} .
            ?r rdfs:label ?name .
        }}'''.format(tag)

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    dishes = [(x['r']['value'], x['name']['value']) for x in results['results']['bindings']]
    return dishes

def fetch_all_ingredients(sparql, dish):
    query = '''PREFIX recipe-kb: <http://idea.rpi.edu/heals/kb/>
        SELECT ?in {{
            {} recipe-kb:uses ?ii .
            ?ii recipe-kb:ing_name ?in
        }}
    '''.format(dish)

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    ingredients = [x['in']['value'] for x in results['results']['bindings']]
    return ingredients


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', required=True, type=str, help='path to the output dir')
    opt = vars(parser.parse_args())

    ssl._create_default_https_context = ssl._create_unverified_context
    sparql = SPARQLWrapper(USE_ENDPOINT_URL)

    f_kg = open(os.path.join(opt['output'], 'recipe_kg.json'), 'w')
    all_tags = fetch_all_tags(sparql)
    for tag in all_tags:
        tag_name = ' '.join(tag.split('/')[-1].split('%20'))
        if len(tag_name) == 0:
            continue
        graph = {'uri': tag, 'name': [tag_name], 'alias': [], 'type': ['tag'], 'neighbors': {}}
        dishes = fetch_all_dishes(sparql, '<{}>'.format(tag))
        graph['neighbors']['tagged_dishes'] = []
        for dish, dish_name in dishes:
            dish_graph = {dish: {'name': [dish_name], 'uri': dish, 'alias': [], 'type': ['dish_recipe'], 'neighbors': {}}}
            dish_graph[dish]['neighbors']['contains_ingredients'] = []
            ingredients = fetch_all_ingredients(sparql, '<{}>'.format(dish))
            for ingredient in ingredients:
                ingredient_name = ' '.join(ingredient.split('/')[-1].split('%20'))
                ingredient_graph = {ingredient: {'name': [ingredient_name], 'uri': ingredient, 'alias': [], 'type': ['ingredient']}}
                dish_graph[dish]['neighbors']['contains_ingredients'].append(ingredient_graph)
            graph['neighbors']['tagged_dishes'].append(dish_graph)
        f_kg.write(json.dumps({tag: graph}) + '\n')
        f_kg.flush()
    f_kg.close()
