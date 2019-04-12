import argparse
import os
from collections import defaultdict
import math
import numpy as np

from utils.io_utils import *
from config.data_config import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-recipe', '--recipe', type=str, help='path to the recipe data')
    parser.add_argument('-o', '--output', required=True, type=str, help='path to the output file')
    parser.add_argument('-max_dish_count_per_tag', '--max_dish_count_per_tag', default=2000, type=int, help='max num of dishes per tag')

    opt = vars(parser.parse_args())

    # Recipe data
    recipe_kg = load_ndjson(opt['recipe'], return_type='dict')

    tag_count_dish = defaultdict(int)
    dish_count_tag = defaultdict(int)
    for tag in recipe_kg:
        if len(recipe_kg[tag]['neighbors']) == 0:
            continue

        tag_count_dish[tag] = len(recipe_kg[tag]['neighbors']['tagged_dishes'])
        for dish_graph in recipe_kg[tag]['neighbors']['tagged_dishes']:
            dish_graph = list(dish_graph.values())[0]
            dish_name = dish_graph['name'][0]
            dish_count_tag[dish_name] += 1


    print('Total tag num: {}'.format(len(tag_count_dish)))
    print('Total dish num: {}'.format(len(dish_count_tag)))

    np.random.seed(1234)
    max_dish_count_per_tag = opt['max_dish_count_per_tag']
    for tag in recipe_kg.copy():
        if len(recipe_kg[tag]['neighbors']) == 0:
            continue

        if len(recipe_kg[tag]['neighbors']['tagged_dishes']) > max_dish_count_per_tag:
            np.random.shuffle(recipe_kg[tag]['neighbors']['tagged_dishes'])
            recipe_kg[tag]['neighbors']['tagged_dishes'] = recipe_kg[tag]['neighbors']['tagged_dishes'][:max_dish_count_per_tag]

    with open(opt['output'], 'w') as fout:
        for tag, graph in recipe_kg.items():
            fout.write(json.dumps({tag: graph}) + '\n')
