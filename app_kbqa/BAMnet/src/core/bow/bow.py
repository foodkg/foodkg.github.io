'''
Created on Mar, 2019

@author: hugo

'''
import os
import numpy as np

import torch
import torch.backends.cudnn as cudnn

from .modules import BOWnet
from ..bamnet.utils import to_cuda, next_batch
from ..utils.utils import load_ndarray
from ..utils.metrics import *
from .. import config


CTX_BOW_INDEX = -5
def get_text_overlap(raw_query, query_mentions, ctx_ent_names, vocab2id, ctx_stops, query):
    def longest_common_substring(s1, s2):
       m = [[0] * (1 + len(s2)) for i in range(1 + len(s1))]
       longest, x_longest = 0, 0
       for x in range(1, 1 + len(s1)):
           for y in range(1, 1 + len(s2)):
               if s1[x - 1] == s2[y - 1]:
                   m[x][y] = m[x - 1][y - 1] + 1
                   if m[x][y] > longest:
                       longest = m[x][y]
                       x_longest = x
               else:
                   m[x][y] = 0
       return s1[x_longest - longest: x_longest]

    sub_seq = longest_common_substring(raw_query, ctx_ent_names)
    if len(set(sub_seq) - ctx_stops) == 0:
        return []

    men_type = None
    for men, type_ in query_mentions:
        if type_.lower() in config.constraint_mention_types:
            if '_'.join(sub_seq) in '_'.join(men):
                men_type = '__{}__'.format(type_.lower())
                break

    if men_type:
        return [vocab2id[men_type] if men_type in vocab2id else config.RESERVED_TOKENS['UNK']]
    else:
        return [vocab2id[x] if x in vocab2id else config.RESERVED_TOKENS['UNK'] for x in sub_seq]

class BOWnetAgent(object):
    """ Bidirectional attentive memory network agent.
    """
    def __init__(self, opt, ctx_stops, vocab2id):
        self.ctx_stops = ctx_stops
        self.vocab2id = vocab2id
        opt['cuda'] = not opt['no_cuda'] and torch.cuda.is_available()
        if opt['cuda']:
            print('[ Using CUDA ]')
            torch.cuda.set_device(opt['gpu'])
            # It enables benchmark mode in cudnn, which
            # leads to faster runtime when the input sizes do not vary.
            cudnn.benchmark = True

        self.opt = opt
        if self.opt['pre_word2vec']:
            pre_w2v = load_ndarray(self.opt['pre_word2vec'])
        else:
            pre_w2v = None

        self.model = BOWnet(opt['vocab_size'], opt['vocab_embed_size'], pre_w2v=pre_w2v, use_cuda=opt['cuda'])
        if opt['cuda']:
            self.model.cuda()

        # if opt.get('model_file'):
        #     if os.path.isfile(opt['model_file']):
        #         print('Loading existing model parameters from ' + opt['model_file'])
        #         self.load(opt['model_file'])
        #     else:
        #         os.makedirs(os.path.dirname(opt['model_file']), exist_ok=True)
        #         self.save()

        super(BOWnetAgent, self).__init__()

    def predict(self, xs, cand_labels, batch_size=32, margin=1, ys=None, verbose=False, silence=False):
        '''Prediction scores are returned in the verbose mode.
        '''
        if not silence:
            print('Testing size: {}'.format(len(cand_labels)))
        memories, queries, query_words, raw_queries, query_mentions, query_lengths = xs
        gen = next_batch(memories, queries, query_words, raw_queries, query_mentions, query_lengths, cand_labels, batch_size)
        predictions = []
        for batch_xs, batch_cands in gen:
            batch_pred = self.predict_step(batch_xs, batch_cands, margin, verbose=verbose)
            predictions.extend(batch_pred)
        return predictions

    def predict_step(self, xs, cand_labels, margin, verbose=False):
        self.model.train(mode=False)
        with torch.set_grad_enabled(False):
            # Organize inputs for network
            memories, ctx_mask = self.pad_ctx_memory(xs[0], self.opt['ans_ctx_entity_bow_size'], xs[3], xs[4], xs[1])
            memories = [to_cuda(torch.LongTensor(np.array(x)), self.opt['cuda']) for x in zip(*memories)]
            ctx_mask = to_cuda(ctx_mask, self.opt['cuda'])
            queries = to_cuda(torch.LongTensor(xs[1]), self.opt['cuda'])
            query_words = to_cuda(torch.LongTensor(xs[2]), self.opt['cuda'])
            query_lengths = to_cuda(torch.LongTensor(xs[5]), self.opt['cuda'])
            mem_hop_scores = self.model(memories, queries, query_lengths, query_words, ctx_mask=None)

            predictions = self.ranked_predictions(cand_labels, mem_hop_scores[-1].data, margin)
            return predictions

    def pad_ctx_memory(self, memories, ctx_bow_size, raw_queries, query_mentions, queries):
        cand_ans_size = max(max(map(len, list(zip(*memories))[0]), default=0) - 1, 1) # The last element is a dummy candidate
        ctx_bow_size = max(min(max(map(len, (a for x in list(zip(*memories))[CTX_BOW_INDEX] for y in x for a in y)), default=0), ctx_bow_size), 1)

        pad_memories = []
        ctx_mask = []
        for i in range(len(memories)):
            n = len(memories[i][0]) - 1 # The last element is a dummy candidate
            augmented_inds = list(range(n)) + [-1] * (cand_ans_size - n)
            xx = [n] + [np.array(x)[augmented_inds] for x in memories[i][:CTX_BOW_INDEX]]

            ctx_bow = []
            ctx_bow_len = []
            ctx_num = []
            tmp_ctx_mask = np.zeros(cand_ans_size)
            for _, idx in enumerate(augmented_inds):
                tmp_ctx = []
                tmp_ctx_len = []
                for ctx_ent_names in memories[i][CTX_BOW_INDEX][idx]:
                    sub_seq = get_text_overlap(raw_queries[i], query_mentions[i], ctx_ent_names, self.vocab2id, self.ctx_stops, queries[i])
                    if len(sub_seq) > 0:
                        tmp_ctx_mask[_] = 1
                        tmp_ctx.append(sub_seq[:ctx_bow_size] + [config.RESERVED_TOKENS['PAD']] * max(0, ctx_bow_size - len(sub_seq)))
                        tmp_ctx_len.append(max(min(ctx_bow_size, len(sub_seq)), 1))
                ctx_bow.append(tmp_ctx)
                ctx_bow_len.append(tmp_ctx_len)
                ctx_num.append(len(tmp_ctx))

            xx += [ctx_bow, ctx_bow_len, ctx_num]
            xx += [np.array(x)[augmented_inds] for x in memories[i][CTX_BOW_INDEX+1:]]
            pad_memories.append(xx)
            ctx_mask.append(tmp_ctx_mask)

        max_ctx_num = max(max([y for x in pad_memories for y in x[CTX_BOW_INDEX]]), 1)
        for i in range(len(pad_memories)): # Example
            for j in range(len(pad_memories[i][-1])): # Cand
                count = pad_memories[i][CTX_BOW_INDEX][j]
                if count < max_ctx_num:
                    pad_memories[i][CTX_BOW_INDEX - 2][j] += [[config.RESERVED_TOKENS['PAD']] * ctx_bow_size] * (max_ctx_num - count)
                    pad_memories[i][CTX_BOW_INDEX - 1][j] += [1] * (max_ctx_num - count)
        return pad_memories, torch.Tensor(np.array(ctx_mask))

    def ranked_predictions(self, cand_labels, scores, margin):
        _, sorted_inds = scores.sort(descending=True, dim=1)
        return [[(j, scores[i][j]) for j in r if scores[i][j] + margin >= scores[i][r[0]] \
                and cand_labels[i][j] != 'UNK'] \
                if len(cand_labels[i]) > 0 and scores[i][r[0]] > -1e4 else [] \
                for i, r in enumerate(sorted_inds)] # Very large negative ones are dummy candidates

    def save(self, path=None):
        path = self.opt.get('model_file', None) if path is None else path

        if path:
            checkpoint = {}
            checkpoint['bownet'] = self.model.state_dict()
            with open(path, 'wb') as write:
                torch.save(checkpoint, write)
                print('Saved model to {}'.format(path))

    def load(self, path):
        with open(path, 'rb') as read:
            checkpoint = torch.load(read, map_location=lambda storage, loc: storage)
        self.model.load_state_dict(checkpoint['bownet'])
