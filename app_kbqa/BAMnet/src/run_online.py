import os
import argparse
from collections import defaultdict

from core.kbqa import KBQA
from core.utils.utils import load_ndjson, get_config
from core.utils.metrics import calc_avg_f1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-config', '--config', required=True, type=str, help='path to the config file')

    cfg = vars(parser.parse_args())
    config = get_config(cfg['config'])

    # 1) Load testing data
    data = load_ndjson(os.path.join(config['data_dir'], config['test_raw_data']))

    # 2) Load pretrained KBQA model
    kbqa = KBQA.from_pretrained(config)

    # 3) Prediction
    gold = defaultdict(list)
    system_output = defaultdict(list)
    for each in data:
        question = each['qText']
        question_type = each['qType']
        topic_entities = each['topicKey']

        # Call the KBQA answer function to fetch answers
        answer_list, answer_id_list, rel_path_list, err_code, err_msg = kbqa.answer(question, question_type, topic_entities)

        gold[question_type].append(each['answers'])
        system_output[question_type].append(answer_list)
        # print('System output: {}, {}, {}'.format(answer_list, err_code, err_msg))
        # print('Ground-truth answer: {}'.format(each['answers']))


    # 4) Evaluation
    overall_count, overall_recall, overall_precision, overall_f1 = 0, 0, 0, 0
    for question_type in gold:
        count, avg_recall, avg_precision, avg_f1 = calc_avg_f1(gold[question_type], system_output[question_type], verbose=False)
        print('\nQuestion type: {}\n Recall: {}\n Precision: {}\n F1: {}'.format(question_type, avg_recall, avg_precision, avg_f1))
        overall_count += count
        overall_recall += count * avg_recall
        overall_precision += count * avg_precision
        overall_f1 += count * avg_f1

    print('\nQuestion type: {}\n Recall: {}\n Precision: {}\n F1: {}\n'.format('overall', \
        overall_recall / overall_count, overall_precision / overall_count, overall_f1 / overall_count))
