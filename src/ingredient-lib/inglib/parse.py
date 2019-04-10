import nltk
import json
import re
import webcolors
from collections import Counter
import random

try:
    nltk.data.find("corpora/wordnet")
except:
    nltk.download("wordnet")

seen = Counter()

counts = [
    "one",
    "two",
    "three",
    "four",
    "a few",
    "around",
    "about",
    "roughly"
]

def read_count(ingredient):
    lead = ingredient.split(" ")[0]
    for count in counts:
        if count == lead:
            return count, ingredient[len(count) + 1 :].strip()
    return "", ingredient

def read_quantity(ingredient, unitless=False):
    # tagged = nltk.pos_tag(nltk.word_tokenize(ingredient))

    match = re.match("[0-9\-/. ]+", ingredient)
    if match == None:
        return "", ingredient.strip()
    start, end = match.start(0), match.end(0)

    text = ingredient[start:end]

    return text, ingredient[end:].strip()

def fix_quantity(quantity):
    # common error: loss of / marks
    # solution!

    return re.sub("([1-9])([0-9]+)", "\\1/\\2", quantity)

units = [
    "cup",
    "teaspoon",
    "cups",
    "tablespoon",
    "lb",
    "can",
    "ounce",
    "ounces",
    "package",
    "medium",
    "cans",
    "slice",
    "pinch",
    "dash",
    "clove",
    "jar",
    "ounce",
    "box",
    "whole",
    "container",
    "bunch",
    "head",
    "pint",
    "inch",
    "stalk",
    "bag",
    "envelope",
    "liter",
    "litre",
    "c.",
    "tbsp",
    "tbsp.",
    "tbs",
    "tbs.",
    "tsp",
    "gram",
    "grams",
    "g.",
    "ml",
    "lbs",
    "lbs.",
    "gallon",
    "gal.",
    "quart",
    "q.",
    "qt.",
    "qts."
    ]


def read_unit(ingredient):
    lead = ingredient.split(" ")[0].lower()
    for unit in units:
        if unit + "s" == lead:
            return lead, ingredient[len(lead) :].strip()
        if unit + "es" == lead:
            return lead, ingredient[len(lead) :].strip()
        if unit == lead:
            return lead, ingredient[len(lead) :].strip()
    return "", ingredient

# performing nltk analysis is very expensive
# shortcut time!

def read_name(ingredient, high_quality):

    if high_quality:
        parts = ingredient.split(",")

        kept = []

        for part in parts:
            count = 0
            tagged = nltk.pos_tag(nltk.word_tokenize(part))
            for tag in tagged:
                if "NN" in tag[1]:
                    count += 1
            if count > 0:
                kept.append(part)

        if len(kept) == 0:
            return ""

        ingredient = kept[0]

        tagged = nltk.pos_tag(nltk.word_tokenize(ingredient))

        # remove anything after a conjunction

        for x in range(len(tagged)):
            if tagged[x][1] == "CC":
                tagged = tagged[0:x]
                break

        tagged = list(
            filter(
                lambda x: (("RB" not in x[1] and x[1] != "JJ" and x[1][0] != "V"))
                or x[0].lower() in webcolors.CSS3_NAMES_TO_HEX,
                tagged,
            )
        )

        words = list(map(lambda x: x[0], tagged))

        p = nltk.PorterStemmer()
        w = nltk.WordNetLemmatizer()

        words = map(lambda x: w.lemmatize(x), words)
        return " ".join(words)
    else:
        return ingredient.split(",")[0]


def parse_ingredient_no_name(ingredient):
    ingredient = re.sub("\(.*?\)", "", ingredient)
    ingredient = ingredient.replace('"', "")
    count, rest = read_count(ingredient)
    quantity, rest = read_quantity(rest)
    unit, rest = read_unit(rest)

    if unit:
        quantity = fix_quantity(quantity)

    return quantity.strip(), unit.strip()


def parse_ingredient(ingredient, high_quality=False):
    ingredient = re.sub("\(.*?\)", "", ingredient)
    ingredient = ingredient.replace('"', "")
    count, rest = read_count(ingredient)
    quantity, rest = read_quantity(rest)
    unit, rest = read_unit(rest)
    name = read_name(rest, high_quality)

    if unit:
        quantity = fix_quantity(quantity)

    return quantity.strip(), unit.strip(), name.strip()
