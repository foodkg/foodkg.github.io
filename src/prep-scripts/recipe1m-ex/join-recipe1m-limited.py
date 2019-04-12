"""Combines recipe1m data with external information.

This script combines the following sets of data:

- recipe1m's original dataset (layer1.json)
- recipe1m's fixed ingredients (det_ingrs.json)

For each recipe1m id (a ten-digit hex string) that has tag data, a recipe is produced

"""

import csv
import json

import os
import sys

from tqdm import tqdm

import argparse

sys.path.insert(
    0, os.path.abspath(os.path.join(os.getcwd(), "../ingredient-lib"))
)

from inglib.parse import parse_ingredient_no_name

def run(args):
    print("Loading json files...")

    recipe1m_arr = json.load(open(args.layer1, "r", encoding="latin-1"))
    det_ingrs_arr = json.load(open(args.det_ingrs, "r", encoding="latin-1"))

    recipe1m = {}
    det_ingrs = {}

    print("Parsing recipe1m entries")

    for item in tqdm(recipe1m_arr):
        recipe1m[item["id"]] = item

    for item in tqdm(det_ingrs_arr):
        det_ingrs[item["id"]] = item

    results = []

    count = 0

    print("Processing...")

    for id in tqdm(recipe1m):
        recipe = {}
        recipe["id"] = id
        recipe["title"] = recipe1m[id]["title"]
        recipe["url"] = recipe1m[id]["url"]

        valids = det_ingrs[id]["valid"]
        names = det_ingrs[id]["ingredients"]
        ingredients = recipe1m[id]["ingredients"]
        ings = []

        for valid, name, ing in zip(valids, names, ingredients):
            if valid:
                quantity, unit = parse_ingredient_no_name(ing["text"])
                ings.append({
                    "unit": unit,
                    "quantity": quantity,
                    "name": name["text"]
                })

        recipe["ingredients"] = ings
        recipe["instructions"] = list(map(lambda x: x["text"], recipe1m[id]["instructions"]))
        recipe["tags"] = []

        results.append(recipe)

    json.dump(results, open(args.output, "w"))

parser = argparse.ArgumentParser(description="Joins recipe1m recipes with parsed ingredient names")

parser.add_argument("layer1", help="layer1.json file from the Recipe1M dataset")
parser.add_argument("det_ingrs", help="det_ingrs.json file from the Recipe1M dataset")
parser.add_argument("output", help="Where to write the resulting enhanced data")

run(parser.parse_args())
