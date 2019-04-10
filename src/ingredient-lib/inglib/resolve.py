import numpy as np
import csv
import math
import nltk
from more_itertools import unique_everseen
from joblib import Parallel, delayed
import json
import random

def _weight_of(word, list, order):
    """Assumes word is in list"""
    pos = 0
    for x in range(len(list)):
        if list[x] == word:
            pos = x
            break
    if order == "ascending":
        return x+1
    elif order == "descending":
        return len(list) - x

def weighted_cosine_match(a, b):
    """Cosine match w/ weights based on order """
    a_list = list(unique_everseen(a))
    b_list = list(unique_everseen(b))

    domain = list(unique_everseen(a_list + b_list))

    a_vec = [_weight_of(word, a_list, "descending") if word in a_list else 0 for word in domain]
    b_vec = [_weight_of(word, b_list, "ascending") if word in b_list else 0 for word in domain]

    product = sum(x*y for x,y in zip(a_vec, b_vec))

    a_mag = math.sqrt(sum(x*x for x in a_vec))
    b_mag = math.sqrt(sum(x*x for x in b_vec))

    return product / (a_mag * b_mag)

def cosine_match(a, b):
    """Return the value of cos(theta) for two word lists."""
    a_set = set(a)
    b_set = set(b)

    domain = a_set.union(b_set)

    ordered_domain = list(domain)

    a_vec = [1 if word in a_set else 0 for word in ordered_domain]
    b_vec = [1 if word in b_set else 0 for word in ordered_domain]

    product = sum(x*y for x,y in zip(a_vec, b_vec))

    a_mag = math.sqrt(sum(x*x for x in a_vec))
    b_mag = math.sqrt(sum(x*x for x in b_vec))

    return product / (a_mag * b_mag)

class Resolver:
    def __init__(self, names, entities, test_func=cosine_match):
        self.names = names
        self.entities = entities
        self.test_func = test_func

    def _find_match(self, tokens):
        max = 0
        index = -1

        for ind, item in enumerate(self.names):
            val = self.test_func(tokens, item)
            if val > max:
                max = val
                index = ind

        return index

    def resolve(self, tokens):
        """Returns the corresponding link for the best match of the tokens

        Input should be a list of individual string tokens."""
        index = self._find_match(tokens)
        if index != -1:
            return self.entities[index]
        else:
            return None
