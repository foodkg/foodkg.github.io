from module import Module
import inspect
import sys
import os
import re
import tqdm

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../ingredient-lib"))
)

from inglib import parse, resolve

import data


class _Processor(Module):
    """Transforms the contents of Recipe objects."""


class Nop(_Processor):
    """Does nothing."""

    name = "nop"

    def run(self, streams):
        pass


class Extract(_Processor):
    """Retrieves objects from other objects.

    It iterates over lists if a name is suffixed with []."""

    name = "extract"

    def __init__(self, input, output, path, unique):
        self.input = input
        self.output = output
        self.path = path
        self.unique = unique

    @classmethod
    def _init_parser(cls):
        super()._init_parser()
        cls._parser.add_argument("input", help="The stream to read")
        cls._parser.add_argument("output", help="The stream to write")
        cls._parser.add_argument("path", help="The path to follow", nargs="+")
        cls._parser.add_argument("++unique", help="If true, runs the results through a set", action="store_true", default=False)

    @classmethod
    def _extract(cls, object, path):
        if len(path) == 0:
            return [object]
        else:
            head = path[0]

            # get several things at the same level in a list
            if len(head.split(",")) > 1:
                result = []
                for field in head.split(","):
                    result += cls._extract(object, [field])
                return [result]

            if len(head.split(">")) > 1:
                result = []
                layers = head.split(">")
                result = cls._extract(object, layers)
                return [result]

            if "[]" in head:
                result = []
                head = head[:-2]
                for item in getattr(object, head):
                    result += cls._extract(item, path[1:])
                return result
            else:
                item = getattr(object, head)
                return cls._extract(item, path[1:])

    def run(self, streams):
        input = streams[self.input]
        streams[self.output] = []
        output = streams[self.output]
        seen = set()

        if self.unique:
            for object in tqdm.tqdm(input):
                extracted = Extract._extract(object, self.path)
                for item in extracted:
                    if item not in seen:
                        seen.add(item)
                        output.append(item)
        else:
            for object in tqdm.tqdm(input):
                output += Extract._extract(object, self.path)


        yield "Produced {0} objects".format(len(output))


class ResolveNames(_Processor):
    """Resolves names against a set of mappings."""

    name = "resolve"

    def __init__(self, entities, mappings, linkages, splitters):
        super().__init__()
        self.entities = entities
        self.mappings = mappings
        self.linkages = linkages
        self.splitters = splitters
        self.cache = {}

    @classmethod
    def _init_parser(cls):
        super()._init_parser()
        cls._parser.add_argument(
            "entities", help="The entities to resolve.", default="names", nargs="?"
        )
        cls._parser.add_argument(
            "mappings",
            help="Mappings between names and entities.",
            default="mappings",
            nargs="?",
        )
        cls._parser.add_argument(
            "linkages",
            help="Output stream containing the linkages.",
            default="linkages",
            nargs="?",
        )
        cls._parser.add_argument(
            "splitters",
            help="Characters to tokenize the inputs with",
            default=" ",
            nargs="?",
        )

    def run(self, streams):
        entities = streams[self.entities]
        mappings = streams[self.mappings]
        streams[self.linkages] = []
        linkages = streams[self.linkages]

        names_to_ents = {}
        mapNames = []
        mapEnts = []

        yield "Reading mappings"

        for row in tqdm.tqdm(mappings):
            name = list(
                filter(None, re.split("[" + self.splitters + "]", row[0].lower()))
            )
            entity = row[1]
            mapNames.append(name)
            mapEnts.append(entity)

        yield "Starting resolution"

        resolver = resolve.Resolver(mapNames, mapEnts)

        for entity in tqdm.tqdm(entities):
            name = entity.__str__().lower().strip()
            if name not in names_to_ents:
                names_to_ents[name] = set()

            names_to_ents[name].add(entity)

            if name not in self.cache:
                self.cache[name] = resolver.resolve(name.split(" "))

        yield "Writing results"

        for name in tqdm.tqdm(self.cache):
            if self.cache[name]:
                for entity in names_to_ents[name]:
                    left = entity
                    right = self.cache[name]
                    linkages.append(data.Linkage(left, right))


class GuessRecipeTags(_Processor):
    """Assigns tags to recipes based on common ingredients and the title."""

    name = "guess-tags"

    def __init__(self, recipes, tags):
        self.recipes = recipes
        self.tags = tags
        self.cache = {}

    @classmethod
    def _init_parser(cls):
        cls._parser.add_argument("recipes", help="The recipes to tag")
        cls._parser.add_argument(
            "tags", help="A list of [ingredient, weight, tag] lists."
        )

    def run(self, streams):
        recipes = streams[self.recipes]
        tags = streams[self.tags]

        # the name to look for
        names = []
        # the resulting tag and weight
        pairs = []
        # how to match
        rules = []

        tag_names = set()

        for tag in tags:
            names.append(tag[0].lower().strip())
            pairs.append((float(tag[1]), tag[2]))
            tag_names.add(tag[2])
            rules.append(tag[3])

        for recipe in tqdm.tqdm(recipes):
            weights = {}
            tags = set()

            for tag in tag_names:
                weights[tag] = 0

            for ing in recipe.ingredients:
                ing_name = ing.name.lower().strip()

                if ing_name not in self.cache:
                    self.cache[ing_name] = None
                    for i in range(len(names)):
                        name = names[i]
                        if rules[i] == "exact":
                            if name == ing_name:
                                self.cache[ing_name] = pairs[i]
                                break
                        if rules[i] == "substring":
                            if name in ing_name:
                                self.cache[ing_name] = pairs[i]
                                break
                        if rules[i] == "fuzzy":
                            ing_tokens = ing_name.split(" ")
                            name_tokens = name.split(" ")
                            score = resolve.cosine_match(ing_tokens, name_tokens)
                            if score > 0:
                                self.cache[ing_name] = pairs[i]
                                break

                if self.cache[ing_name]:
                    pair = self.cache[ing_name]
                    weights[pair[1]] += pair[0]

            for tag in weights:
                score = weights[tag]
                if score >= 1:
                    tags.add(tag)

            for tag in tag_names:
                if tag in recipe.title.lower():
                    tags.add(tag)

            recipe.tags = list(tags)


class BundleNanopub(_Processor):
    """Collects everything from a datastream and bundles it for a nanopub."""

    name = "bundle"

    def __init__(self, source, dest):
        self.source = source
        self.dest = dest

    @classmethod

    def _init_parser(cls):
        cls._parser.add_argument(
            "source", help="Datastream to read from"
        )
        cls._parser.add_argument(
            "dest", help="Datastream to write the bundle to"
        )

    def run(self, streams):
        source = streams[self.source]
        streams[self.dest] = []
        dest = streams[self.dest]

        bundle = data.NanopubBundle()

        for item in source:
            bundle.add(item)

        dest.append(bundle)


__all__ = []
_locals = dict(locals())  # pylint: disable=invalid-name
processors = {}  # pylint: disable=invalid-name


def _setup():
    classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    for _, obj in classes:
        if issubclass(obj, _Processor) and obj != _Processor:
            __all__.append(obj.__name__)
            processors[obj.name] = obj


_setup()
