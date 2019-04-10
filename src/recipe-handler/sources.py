import inspect
import json
import csv
import tqdm
import sys
import os

import rdflib

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../recipeformats"))
)

import data
from data import Recipe, Ingredient, RawIngredient, USDAEntry, Tag
from module import Module

import mxp


class _Source(Module):
    """Provides objects, given a source of data."""

    def run(self):
        raise NotImplementedError


class Recipe1M(_Source):
    """Extracts Recipe objects from the Recipe1M data set."""

    name = "recipe1m"

    def __init__(self, file, datastream):
        self.file = file
        self.datastream = datastream
        pass

    @classmethod
    def _init_parser(cls):
        super()._init_parser()
        cls._parser.add_argument(
            "file", help="The name of the recipe1m layer_1 json file"
        )
        cls._parser.add_argument(
            "datastream", help="The name of the resulting list of recipes"
        )

    def run(self, streams):
        streams[self.datastream] = []

        with open(self.file, "rb") as file:
            yield "Loading json file"
            data = json.load(file)
            yield "Parsing records"

            for recipe_data in tqdm.tqdm(data):
                recipe = Recipe()
                recipe.title = recipe_data["title"]
                recipe.ingredients = [
                    RawIngredient(x["text"]) for x in recipe_data["ingredients"]
                ]
                recipe.steps = [x["text"] for x in recipe_data["instructions"]]
                streams[self.datastream].append(recipe)
                recipe.add_prov("wasDerivedFrom", rdflib.URIRef(recipe_data["url"]))


class Recipe1MExtended(_Source):
    """Reads our own augmented recipe1m data."""

    name = "recipe1m-ex"

    def __init__(self, file, datastream):
        self.file = file
        self.datastream = datastream
        pass

    @classmethod
    def _init_parser(cls):
        super()._init_parser()
        cls._parser.add_argument(
            "file", help="The name of the augmented recipe1m json file"
        )
        cls._parser.add_argument(
            "datastream", help="The name of the resulting list of recipes"
        )

    def run(self, streams):
        streams[self.datastream] = []

        with open(self.file, "rb") as file:

            yield "Loading json file"
            records = json.load(file)
            yield "Parsing records"

            for recipe_data in tqdm.tqdm(records):
                recipe = Recipe()
                recipe.title = recipe_data["title"]
                recipe.ingredients = []

                for item in recipe_data["ingredients"]:
                    ing = Ingredient()
                    ing.name = data.IngredientName(item["name"])
                    ing.unit = item["unit"]
                    ing.quantity = item["quantity"]
                    
                    recipe.ingredients.append(ing)

                recipe.steps = recipe_data["instructions"]

                for item in recipe_data["tags"]:
                    recipe.tags.append(Tag(item))

                url = recipe_data["url"]
                url = url.replace("{", "%7B")
                url = url.replace("}", "%7D")
                url = url.replace("^", "%5E")
                recipe.add_prov("wasDerivedFrom", rdflib.URIRef(url))

                streams[self.datastream].append(recipe)


class MasterCookOld(_Source):
    """Reads Mastercook 1-4 archives."""

    name = "mxp"

    def __init__(self, file, datastream):
        self.file = file
        self.datastream = datastream

    @classmethod
    def _init_parser(cls):
        super()._init_parser()
        cls._parser.add_argument("file", help="The name of the mxp file")
        cls._parser.add_argument(
            "datastream", help="The name of the resulting list of list of recipes"
        )

    def run(self, streams):
        streams[self.datastream] = []
        recipes = streams[self.datastream]

        yield "Reading file"

        with open(self.file, "r", encoding="latin-1") as file:
            data = file.readlines()

        yield "Parsing recipes"

        mxp_recipes = mxp.parse_recipes(data)

        for mxp_recipe in tqdm.tqdm(mxp_recipes):
            recipe = Recipe()
            recipe.title = mxp_recipe.title

            # * is used to denote a regional tag, apparently
            for mxp_tag in mxp_recipe.categories:
                recipe.tags.append(Tag(mxp_tag.replace("*", "")))

            for mxp_ing in mxp_recipe.ingredients:
                ing = Ingredient()
                ing.name = IngredientName(mxp_ing.ingredient)
                ing.quantity = mxp_ing.amount
                ing.unit = mxp_ing.measure
                ing.comment = mxp_ing.preparation_method
                recipe.ingredients.append(ing)

            recipes.append(recipe)
        yield "Read {0} recipes".format(len(recipes))


class CSV(_Source):
    """Reads a CSV file as a list of lists of strings."""

    name = "csv"

    def __init__(self, file, datastream):
        self.file = file
        self.datastream = datastream

    @classmethod
    def _init_parser(cls):
        super()._init_parser()
        cls._parser.add_argument("file", help="The name of the csv file")
        cls._parser.add_argument(
            "datastream", help="The name of the resulting list of list of strings"
        )

    def run(self, streams):
        streams[self.datastream] = []

        with open(self.file, "r", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=",")
            for row in tqdm.tqdm(reader):
                streams[self.datastream].append(row)


class TypedCSV(_Source):
    """Reads a CSV file as a list of lists of typed objects.

    Types are given by the first row."""

    name = "typed-csv"

    _extra_types = {"str": str, "int": int, "float": float}

    def __init__(self, file, datastream):
        self.file = file
        self.datastream = datastream

    @classmethod
    def _init_parser(cls):
        super()._init_parser()
        cls._parser.add_argument("file", help="The name of the csv file")
        cls._parser.add_argument(
            "datastream", help="The name of the resulting list of lists of objects"
        )

    def run(self, streams):
        streams[self.datastream] = []

        with open(self.file, "r", encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=",")
            type_row = reader.__next__()
            types = []
            for item in type_row:
                if item in data.datatypes:
                    types.append(data.datatypes[item])
                elif item in TypedCSV._extra_types:
                    types.append(TypedCSV._extra_types[item])
            for items in tqdm.tqdm(reader):
                row = []
                for item, item_type in zip(items, types):
                    row.append(item_type(item))
                streams[self.datastream].append(row)


class USDA(_Source):
    """Reads a CSV file as a series of USDA entries."""

    name = "usda"

    def __init__(self, file, datastream):
        self.file = file
        self.datastream = datastream

    @classmethod
    def _init_parser(cls):
        super()._init_parser()
        cls._parser.add_argument("file", help="The name of the USDA csv file" "")
        cls._parser.add_argument(
            "datastream", help="The name of the resulting list of USDA entries"
        )

    def run(self, streams):
        streams[self.datastream] = []
        entries = streams[self.datastream]

        with open(self.file, "r") as file:
            reader = csv.reader(file, delimiter=",")
            reader.__next__()
            for row in tqdm.tqdm(reader):
                id = row[0]
                desc = row[1]
                attributes = {}

                entry = USDAEntry(id, desc, row)

                entries.append(entry)
        yield "Read {0} USDA entries".format(len(entries))


__all__ = []
_locals = dict(locals())  # pylint: disable=invalid-name
sources = {}  # pylint: disable=invalid-name


def _setup():
    classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    for _, obj in classes:
        if issubclass(obj, _Source) and obj != _Source:
            __all__.append(obj.__name__)
            sources[obj.name] = obj


_setup()
