import csv
import argparse
import re
from tqdm import tqdm

from csvutil import read_usda, write_typed_list

# we only want prefixes corresponding to useful ingredients


accepted = [
    "01", "02", "04", "05", "06", "07", "09", "10", "11", "12", "13", "15", "16", "17", "20"
]

seen = set()

def run(args):
    data = read_usda(args.food_des)
    result = []
    for row in tqdm(data):
        id = row[0]
        name = ",".join(row[2].split(",")[0:3])
        name = re.sub("\(.*?\)", "", name)
        if name not in seen:
            seen.add(name)
            if id[0:2] in accepted:
                resource = args.prefix + id
                result.append([name, resource])
                if row[4]:
                    for item in row[4].split(","):
                        result.append([item.strip(), resource])

    write_typed_list(args.output, result, ["str", "Resource"])

parser = argparse.ArgumentParser(description="Extracts pairs of [name, id] from the USDA's list of food descriptions")

parser.add_argument("food_des", help="FOOD_DES.txt file")
parser.add_argument("prefix", help="A prefix to turn the USDA IDs into URIs")
parser.add_argument("output", help="Where to write the pairs of names and ids")

run(parser.parse_args())
