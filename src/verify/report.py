import csv
import json
from functools import reduce
from tqdm import tqdm

file = open("report.txt", "w")

def show(text = ""):
    print(text)
    file.write(text + "\n")

print("Loading config...")

config = json.load(open("config.json"))

do_usda = config["usda"]
do_foodon = config["foodon"]
do_recipes = config["recipes"]
do_links = config["links"]

print("Loading files...")

if do_usda:
    print("Loading USDA data...")
    usda_nutrdef = list(csv.reader(open("data/NUTR_DEF.txt", encoding="latin-1")))
    usda_fooddes = list(csv.reader(open("data/FOOD_DES.txt", encoding="latin-1")))
    usda_csv = list(csv.reader(open("data/usda-pairs.csv")))

if do_foodon:
    print("Loading FoodOn data...")
    foodon_csv = list(csv.reader(open("data/foodon-pairs.csv")))

if do_recipes:
    print("Loading Recipe1M data...")
    layer1 = json.load(open("data/layer1.json"))
    det_ingrs = json.load(open("data/det_ingrs.json"))

if do_links:
    print("Loading linkage data...")
    usda_links = open("data/usda-links.trig").readlines()
    foodon_links = open("data/foodon-links.trig").readlines()

print("All data loaded.")
print()

print("Processing...")

if do_usda:
    print("Doing USDA...")

    usda_entities = len(usda_fooddes)
    usda_nutr_count = len(usda_nutrdef)
    usda_entities_used = len(usda_csv) - 1

if do_foodon:
    print("Doing foodon...")

    foodon_entities = len(foodon_csv) - 1



print("Doing recipe1m...")

if do_recipes:
    recipe1m_recipes = len(layer1)
    recipe1m_ings = 0

    recipe1m_ings_uniq_set = set()

    print("Processing the layer1 file...")
    for recipe in tqdm(layer1):
        recipe1m_ings += len(recipe["ingredients"])
        for ing in recipe["ingredients"]:
            recipe1m_ings_uniq_set.add(ing["text"])

    recipe1m_ings_uniq = len(recipe1m_ings_uniq_set)

    recipe1m_ings_valid = 0
    recipe1m_ings_resolved_set = set()

    print("Processing the det_ingrs file...")
    for recipe in tqdm(det_ingrs):
        for i in range(len(recipe["valid"])):

            if recipe["valid"][i]:
                recipe1m_ings_valid += 1
                recipe1m_ings_resolved_set.add(recipe["ingredients"][i]["text"])

    recipe1m_ings_resolved = len(recipe1m_ings_resolved_set)

if do_links:
    print("Doing links...")

    usda_link_count = 0

    for line in usda_links:
        if "owl:equivalentClass" in line:
            usda_link_count += 1

    foodon_link_count = 0

    for line in foodon_links:
        if "owl:equivalentClass" in line:
            foodon_link_count += 1
            

print("Done processing.")
print()

if do_usda:
    show("USDA: ")

    show("Number of USDA entities: {0}".format(usda_entities))
    show("Number of USDA nutrient types: {0}".format(usda_nutr_count))
    show("Number of USDA entities considered: {0}".format(usda_entities_used))

if do_foodon:
    show()
    show("FoodOn: ")

    show("Number of FoodOn entities considered: {0}".format(foodon_entities))

if do_recipes:
    show()
    show("Recipes: ")

    show("Number of recipes: {0}".format(recipe1m_recipes))
    show("Number of ingredients: {0}".format(recipe1m_ings))
    show("Number of valid ingredients: {0}".format(recipe1m_ings_valid))
    show("Percentage of valid ingredients: {0:.2f}%".format(100 * recipe1m_ings_valid/ recipe1m_ings))
    show("Number of unique ingredients: {0}".format(recipe1m_ings_uniq))
    show("Number of resolved ingredient names: {0}".format(recipe1m_ings_resolved))

if do_links:
    show()
    show("Linkages:")

    show("Number of USDA links made: {0}".format(usda_link_count))
    show("Number of FoodOn links made: {0}".format(foodon_link_count))

if do_recipes and do_links:
    show()
    show("Additional linkage stats: ")

    show("Percentage ingredients linked to USDA: {0:.2f}%".format(100 * usda_link_count / recipe1m_ings_resolved))
    show("Percentage ingredients linked to FoodOn: {0:.2f}%".format(100 * foodon_link_count / recipe1m_ings_resolved))
