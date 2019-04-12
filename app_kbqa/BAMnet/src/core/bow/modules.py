'''
Created on Mar, 2019

@author: hugo

'''
import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F

from ..bamnet.utils import to_cuda


INF = 1e20
VERY_SMALL_NUMBER = 1e-10
class BOWnet(nn.Module):
    def __init__(self, vocab_size, vocab_embed_size, pre_w2v=None, use_cuda=True):
        super(BOWnet, self).__init__()
        self.use_cuda = use_cuda
        self.que_enc = BOWEncoder(vocab_size, vocab_embed_size, init_word_embed=pre_w2v, use_cuda=use_cuda)

        self.ans_enc = AnsEncoder(vocab_size=vocab_size, \
                        vocab_embed_size=vocab_embed_size, \
                        shared_embed=self.que_enc.embed, \
                        use_cuda=use_cuda)

    def forward(self, memories, queries, query_lengths, query_words, ctx_mask=None):
        # Question encoder
        q_r = self.que_enc(queries, query_lengths)

        ans_mask = create_mask(memories[0], memories[2].size(1), self.use_cuda)
        _, _, _, x_type_bow, x_types, x_type_bow_len, x_path_bow, x_paths, x_path_bow_len, x_ctx_ent, x_ctx_ent_len, x_ctx_ent_num, _, _, _, _ = memories
        ans_key = self.ans_enc(x_type_bow, x_types, x_type_bow_len, x_path_bow, x_paths, x_path_bow_len, x_ctx_ent, x_ctx_ent_len, x_ctx_ent_num)


        ans_key = torch.cat([each.unsqueeze(2) for each in ans_key], 2)

        mid_score = self.scoring(ans_key.sum(2), q_r, mask=ans_mask)
        mem_hop_scores = [mid_score]
        return mem_hop_scores

    def scoring(self, ans_r, q_r, mask=None):
        # ans_r = ans_r.div(ans_r.norm(p=2, dim=-1, keepdim=True).expand_as(ans_r))
        # q_r = q_r.div(q_r.norm(p=2, dim=-1, keepdim=True).expand_as(q_r))
        score = torch.bmm(ans_r, q_r.unsqueeze(2)).squeeze(2)
        if mask is not None:
            score = mask * score - (1 - mask) * INF # Make dummy candidates have large negative scores
        return score


class AnsEncoder(nn.Module):
    """Answer Encoder"""
    def __init__(self, vocab_size=None, vocab_embed_size=None, shared_embed=None, use_cuda=True):
        super(AnsEncoder, self).__init__()
        # Cannot have embed and vocab_size set as None at the same time.
        self.use_cuda = use_cuda
        self.embed = shared_embed if shared_embed is not None else nn.Embedding(vocab_size, vocab_embed_size, padding_idx=0)
        self.vocab_embed_size = self.embed.weight.data.size(1)
        self.bow_enc = BOWEncoder(vocab_size, vocab_embed_size, shared_embed=shared_embed, use_cuda=use_cuda)

    def forward(self, x_type_bow, x_types, x_type_bow_len, x_path_bow, x_paths, x_path_bow_len, x_ctx_ents, x_ctx_ent_len, x_ctx_ent_num):
        '''
        x_types: answer type
        x_paths: answer path, i.e., bow of relation
        x_ctx_ents: answer context, i.e., bow of entity words, (batch_size, num_cands, num_ctx, L)
        '''
        ans_type_bow = (self.bow_enc(x_type_bow.view(-1, x_type_bow.size(-1)), x_type_bow_len.view(-1))).view(x_type_bow.size(0), x_type_bow.size(1), -1)
        ans_path_bow = (self.bow_enc(x_path_bow.view(-1, x_path_bow.size(-1)), x_path_bow_len.view(-1))).view(x_path_bow.size(0), x_path_bow.size(1), -1)

        # Avg over ctx
        ctx_num_mask = create_mask(x_ctx_ent_num.view(-1), x_ctx_ents.size(2), self.use_cuda).view(x_ctx_ent_num.shape + (-1,))
        ans_ctx_ent = (self.bow_enc(x_ctx_ents.view(-1, x_ctx_ents.size(-1)), x_ctx_ent_len.view(-1))).view(x_ctx_ents.size(0), x_ctx_ents.size(1), x_ctx_ents.size(2), -1)
        ans_ctx_ent = ctx_num_mask.unsqueeze(-1) * ans_ctx_ent
        ans_ctx_ent = torch.sum(ans_ctx_ent, dim=2) / torch.clamp(x_ctx_ent_num.float().unsqueeze(-1), min=VERY_SMALL_NUMBER)
        return [ans_type_bow, ans_path_bow, ans_ctx_ent]

class BOWEncoder(nn.Module):
    """Question Encoder"""
    def __init__(self, vocab_size, embed_size, shared_embed=None, init_word_embed=None, use_cuda=True):
        super(BOWEncoder, self).__init__()
        self.use_cuda = use_cuda
        self.embed = shared_embed if shared_embed is not None else nn.Embedding(vocab_size, embed_size, padding_idx=0)
        if shared_embed is None:
            self.init_weights(init_word_embed)

    def init_weights(self, init_word_embed):
        if init_word_embed is not None:
            print('[ Using pretrained word embeddings ]')
            self.embed.weight.data.copy_(torch.from_numpy(init_word_embed))
        else:
            self.embed.weight.data.uniform_(-0.08, 0.08)

    def forward(self, x, x_len):
        """x: [batch_size, max_length]
           x_len: [batch_size]
        """
        x_mask = create_mask(x_len, x.size(1), self.use_cuda)
        x = self.embed(x)
        avg_x = torch.sum(x * x_mask.unsqueeze(-1), dim=1) / torch.clamp(torch.sum(x_mask, dim=-1, keepdim=True), min=VERY_SMALL_NUMBER)
        return avg_x

def create_mask(x, N, use_cuda=True):
    x = x.data
    mask = np.zeros((x.size(0), N))
    for i in range(x.size(0)):
        mask[i, :x[i]] = 1
    return to_cuda(torch.Tensor(mask), use_cuda)
