import argparse
import os
from collections import defaultdict
import numpy as np

from utils.io_utils import *
from config.data_config import *


def add_qas_id(all_qas, dtype, seed=1234):
    width = len(str(len(all_qas))) + 1
    np.random.seed(seed)
    np.random.shuffle(all_qas)
    for i, qas in enumerate(all_qas):
        qas['qId'] = '{}-qas-{}-'.format(qas['qType'], dtype) + ('{0:0%sd}' % width).format(i)

def generate_simple_qas(kg, kg_keys, simple_qas_templates, p=0.1, seed=1234):
    all_qas = []
    for ent_key in kg_keys:
        subject_name = kg[ent_key]['name'][0]
        neighbors = kg[ent_key]['neighbors']
        for attr in neighbors:
            if np.random.binomial(1, p, 1)[0] == 0:
                continue
            qas_template = np.random.choice(simple_qas_templates)
            qas_str = qas_template.format(s=subject_name, p=attr)
            qas = {}
            val = list(neighbors[attr][0].values())[0]['name']
            qas['answers'] = [str(x) for x in val]
            qas['entities'] = [(subject_name, 'ingredient')]
            qas['topicKey'] = [subject_name]
            qas['rel_path'] = [attr]
            qas['qText'] = qas_str
            qas['qType'] = 'simple'
            all_qas.append(qas)
    return all_qas

def generate_comparision_qas(kg, kg_keys, comparision_qas_templates, p=0.1, seed=1234):
    pred_dict = defaultdict(list)
    for ent_key in kg_keys:
        subject_name = kg[ent_key]['name'][0]
        neighbors = kg[ent_key]['neighbors']
        for attr in neighbors:
            if np.random.binomial(1, p, 1)[0] == 0:
                continue
            val = list(neighbors[attr][0].values())[0]['name'][0]
            pred_dict[attr].append((subject_name, val))

    all_qas = []
    for attr in pred_dict:
        try:
            float(pred_dict[attr][0][1])
        except:
            continue
        np.random.shuffle(pred_dict[attr])
        for j in range(0, len(pred_dict[attr]) - 1, 2):
            s1, o1 = pred_dict[attr][j]
            s2, o2 = pred_dict[attr][j + 1]
            try:
                o1 = float(o1)
                o2 = float(o2)
            except:
                pass

            if o1 == o2:
                continue
            idx = np.random.choice(len(comparision_qas_templates))
            is_more, qas_template = comparision_qas_templates[idx]
            qas_str = qas_template.format(s1=s1, s2=s2, p=attr)
            qas = {}
            qas['answers'] = [s1 if o1 > o2 else s2] if is_more else [s1 if o1 < o2 else s2]
            qas['intermediate_answers'] = [[str(o1)], [str(o2)]]
            qas['entities'] = [(s1, 'ingredient'), (s2, 'ingredient')]
            qas['topicKey'] = [s1, s2]
            qas['rel_path'] = [attr]
            qas['qText'] = qas_str
            qas['is_more'] = is_more
            qas['qType'] = 'comparison'
            all_qas.append(qas)
    return all_qas

def generate_constraint_qas(kg, kg_keys, constraint_qas_templates, num_qas_per_tag=5, seed=1234):
    all_qas = []
    for tag in kg_keys:
        if len(kg[tag]['neighbors']) == 0:
            continue

        tag_name = kg[tag]['name'][0]
        if len(tag_name) == 0:
            continue

        dish_ingredient_map = {}
        all_ingredient_names = set()
        for dish_graph in kg[tag]['neighbors']['tagged_dishes']:
            dish_graph = list(dish_graph.values())[0]
            dish_name = dish_graph['name'][0]
            ingredient_names = []
            for ingredient_graph in dish_graph['neighbors']['contains_ingredients']:
                in_name = list(ingredient_graph.values())[0]['name'][0]
                ingredient_names.append(in_name)
                all_ingredient_names.add(in_name)
            dish_ingredient_map[dish_name] = ingredient_names

        for _ in range(num_qas_per_tag):
            qas_template = np.random.choice(constraint_qas_templates)
            count = np.random.choice(range(1, 5))
            if count > len(all_ingredient_names):
                continue

            sampled_ingredients = np.random.choice(list(all_ingredient_names), count, replace=False)
            qas_str = qas_template.format(tag=tag_name, in_list=', '.join(sampled_ingredients))
            qas = {}
            qas['entities'] = [(tag_name, 'tag')]
            qas['topicKey'] = [tag]
            qas['rel_path'] = ['tagged_dishes']
            qas['qText'] = qas_str
            qas['qType'] = 'constraint'
            qas['answers'] = []
            for dish_name in dish_ingredient_map:
                if len(set(sampled_ingredients).intersection(dish_ingredient_map[dish_name])) == len(sampled_ingredients):
                    qas['answers'].append(dish_name)
            if len(qas['answers']) == 0:
                continue

            all_qas.append(qas)
    return all_qas


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-usda', '--usda', type=str, help='path to the usda data')
    parser.add_argument('-recipe', '--recipe', type=str, help='path to the recipe data')
    parser.add_argument('-o', '--output', required=True, type=str, help='path to the output dir')
    parser.add_argument('-split_ratio', '--split_ratio', nargs=3, type=float, default=[0.5, 0.2, 0.3], help='split ratio')

    opt = vars(parser.parse_args())

    train_ratio, valid_ratio, test_ratio = opt['split_ratio']
    assert sum(opt['split_ratio']) == 1

    np.random.seed(1234)
    # USDA data
    usda_kg = load_ndjson(opt['usda'], return_type='dict')
    usda_keys = list(usda_kg.keys())

    # Recipe data
    recipe_kg = load_ndjson(opt['recipe'], return_type='dict')
    recipe_keys = list(recipe_kg.keys())


    # USDA simple questions
    simple_qas = generate_simple_qas(usda_kg, usda_keys, SIMPLE_QAS_TEMPLATES, p=0.1)

    # USDA comparison questions
    comparision_qas = generate_comparision_qas(usda_kg, usda_keys, COMPARISION_QAS_TEMPLATES, p=0.1)

    # Recipe constraint questions
    constraint_qas = generate_constraint_qas(recipe_kg, recipe_keys, CONSTRAINT_QAS_TEMPLATES, num_qas_per_tag=40)

    qas = simple_qas + comparision_qas + constraint_qas


    train_size = int(len(qas) * train_ratio)
    valid_size = int(len(qas) * valid_ratio)
    test_size = len(qas) - train_size - valid_size

    np.random.shuffle(qas)


    train_qas = qas[:train_size]
    valid_qas = qas[train_size:train_size + valid_size]
    test_qas = qas[-test_size:]

    add_qas_id(train_qas, 'train')
    add_qas_id(valid_qas, 'valid')
    add_qas_id(test_qas, 'test')

    print('{} simple questions'.format(len(simple_qas)))
    print('{} comparison questions'.format(len(comparision_qas)))
    print('{} constraint questions'.format(len(constraint_qas)))

    dump_ndjson(train_qas, os.path.join(opt['output'], 'train_qas.json'))
    dump_ndjson(valid_qas, os.path.join(opt['output'], 'valid_qas.json'))
    dump_ndjson(test_qas, os.path.join(opt['output'], 'test_qas.json'))
    print('Generated totally {} qas, training size: {}, validation size: {}, test size: {}'.format(train_size + valid_size + test_size, train_size, valid_size, test_size))
    print('Saved qas to {}'.format(opt['output']))
