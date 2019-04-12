'''
Created on Oct, 2017

@author: hugo

'''
import argparse

from core.build_data.foodkg.build_data import*
from core.utils.utils import *
from core.build_data import utils as build_utils


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-data_dir', '--data_dir', required=True, type=str, help='path to the data dir')
    parser.add_argument('-kb_path', '--kb_path', required=True, type=str, help='path to the kb path')
    parser.add_argument('-out_dir', '--out_dir', required=True, type=str, help='path to the output dir')
    parser.add_argument('-dtype', '--data_type', default='all_qa', type=str, help='data type')
    parser.add_argument('-min_freq', '--min_freq', default=1, type=int, help='min word vocab freq')
    args = parser.parse_args()

    train_data = load_ndjson(os.path.join(args.data_dir, 'train_qas.json'))
    valid_data = load_ndjson(os.path.join(args.data_dir, 'valid_qas.json'))
    test_data = load_ndjson(os.path.join(args.data_dir, 'test_qas.json'))
    kb = load_ndjson(args.kb_path, return_type='dict')

    if not (os.path.exists(os.path.join(args.out_dir, 'entity2id.json')) and \
        os.path.exists(os.path.join(args.out_dir, 'entityType2id.json')) and \
        os.path.exists(os.path.join(args.out_dir, 'relation2id.json')) and \
        os.path.exists(os.path.join(args.out_dir, 'vocab2id.json'))):

        used_kbkeys = set()
        for each in train_data + valid_data:
            if isinstance(each['topicKey'], list):
                used_kbkeys.update(each['topicKey'])
            else:
                used_kbkeys.add(each['topicKey'])
        print('# of used_kbkeys: {}'.format(len(used_kbkeys)))

        entity2id, entityType2id, relation2id, vocab2id = build_vocab(train_data + valid_data, kb, used_kbkeys, min_freq=args.min_freq)
        dump_json(entity2id, os.path.join(args.out_dir, 'entity2id.json'))
        dump_json(entityType2id, os.path.join(args.out_dir, 'entityType2id.json'))
        dump_json(relation2id, os.path.join(args.out_dir, 'relation2id.json'))
        dump_json(vocab2id, os.path.join(args.out_dir, 'vocab2id.json'))
    else:
        entity2id = load_json(os.path.join(args.out_dir, 'entity2id.json'))
        entityType2id = load_json(os.path.join(args.out_dir, 'entityType2id.json'))
        relation2id = load_json(os.path.join(args.out_dir, 'relation2id.json'))
        vocab2id = load_json(os.path.join(args.out_dir, 'vocab2id.json'))
        print('Using pre-built vocabs stored in %s' % args.out_dir)

    train_vec = build_all_data(train_data, kb, entity2id, entityType2id, relation2id, vocab2id)
    valid_vec = build_all_data(valid_data, kb, entity2id, entityType2id, relation2id, vocab2id)
    test_vec = build_all_data(test_data, kb, entity2id, entityType2id, relation2id, vocab2id)
    dump_json(train_vec, os.path.join(args.out_dir, 'train_vec.json'))
    dump_json(valid_vec, os.path.join(args.out_dir, 'valid_vec.json'))
    dump_json(test_vec, os.path.join(args.out_dir, 'test_vec.json'))
    print('Saved data to {}'.format(os.path.join(args.out_dir, 'train(valid, or test)_vec.json')))

    # Mark the data as built.
    build_utils.mark_done(args.out_dir)
