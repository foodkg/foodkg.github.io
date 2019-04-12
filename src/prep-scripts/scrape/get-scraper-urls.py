"""Extracts pairs of IDs and URLs to be scraped.

This script requires the following source files:

- recipe1m's recipe data (layer1.json)

For each recipe, an object containing the ten-digit hex identifier
and the URL the recipe came from is generated."""

import argparse
import json
import sys
from tqdm import tqdm

def run(args):
    print("Loading recipe1m data...")

    pairs = []
    data = json.load(open(args.layer1))

    print("Extracting data...")

    for recipe in tqdm(data):
        pairs.append({
            "id": recipe["id"],
            "url": recipe["url"]
        })

    print("Dumping results...")

    json.dump(pairs, open(args.out, "w"))

parser = argparse.ArgumentParser(description="Extracts pairs of URLs and IDs from the Recipe1M dataset so that their sources can be scraped.")

parser.add_argument("layer1", help="layer1.json from the Recipe1M dataset")
parser.add_argument("out", help="What to name the file containing the URLs")

run(parser.parse_args())
