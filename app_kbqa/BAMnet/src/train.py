import timeit
import argparse
import numpy as np

from core.bamnet.bamnet import BAMnetAgent
from core.build_data.build_all import build
from core.build_data.utils import vectorize_data
from core.utils.utils import *
from core.config import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-config', '--config', required=True, type=str, help='path to the config file')
    cfg = vars(parser.parse_args())
    opt = get_config(cfg['config'])
    print_config(opt)

    # Ensure data is built
    build(opt['data_dir'], opt['kb_path'])
    train_vec = load_json(os.path.join(opt['data_dir'], opt['train_data']))
    valid_vec = load_json(os.path.join(opt['data_dir'], opt['valid_data']))

    vocab2id = load_json(os.path.join(opt['data_dir'], 'vocab2id.json'))

    train_queries, train_raw_queries, train_query_mentions, train_memories, _, train_gold_ans_inds, _, _, _ = train_vec
    train_queries, train_query_words, train_query_lengths, train_memories = vectorize_data(train_queries, train_query_mentions, \
                                        train_memories, max_query_size=opt['query_size'], \
                                        max_ans_path_bow_size=opt['ans_path_bow_size'], \
                                        vocab2id=vocab2id)

    valid_queries, valid_raw_queries, valid_query_mentions, valid_memories, valid_cand_labels, valid_gold_ans_inds, valid_gold_ans_labels, _, _ = valid_vec
    valid_queries, valid_query_words, valid_query_lengths, valid_memories = vectorize_data(valid_queries, valid_query_mentions, \
                                        valid_memories, max_query_size=opt['query_size'], \
                                        max_ans_path_bow_size=opt['ans_path_bow_size'], \
                                        vocab2id=vocab2id)

    start = timeit.default_timer()

    model = BAMnetAgent(opt, STOPWORDS, vocab2id)
    model.train([train_memories, train_queries, train_query_words, train_raw_queries, train_query_mentions, train_query_lengths], train_gold_ans_inds, \
        [valid_memories, valid_queries, valid_query_words, valid_raw_queries, valid_query_mentions, valid_query_lengths], \
        valid_gold_ans_inds, valid_cand_labels, valid_gold_ans_labels)

    print('Runtime: %ss' % (timeit.default_timer() - start))
