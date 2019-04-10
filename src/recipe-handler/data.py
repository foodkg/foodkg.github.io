import inspect
import sys

from datetime import datetime

from codecs import encode

from urllib.parse import quote

from rdflib import Graph, ConjunctiveGraph
from rdflib import URIRef, BNode, Literal
from rdflib import Namespace
from rdflib.namespace import RDF, RDFS, XSD, OWL

import hashlib
import secrets

SEP = "/"

BASE = Namespace("http://idea.rpi.edu/heals/kb/")
NP = Namespace("http://www.nanopub.org/nschema#")
PROV = Namespace("http://www.w3.org/ns/prov#")

NOCONTEXT = BASE["noContext"]

TYPES = lambda x: BASE["types" + SEP + x]


def litquote(text):
    fixed = text.replace("'", "\\'")
    fixed = fixed.replace('"', '\\"')
    fixed = fixed.replace("\n", "\\n")
    fixed = fixed.replace("\r", "\\r")
    return Literal(fixed)


class _Data:
    """Base class for data objects. Does nothing right now, though."""

    def __rdf__(self, c):
        return []

    def __uri__(self):
        raise NotImplementedError

    def __array__(self):
        raise NotImplementedError


class _Nanopub(_Data):
    """Base class for objects that can turn into a nanopublication."""

    def __init__(self):
        self.provenance = []
        self.pub_info = []
        self._pubid = secrets.token_hex(16)

    def add_prov(self, predicate, object):
        self.provenance.append((predicate, object))

    def add_pub_info(self, predicate, object):
        self.pub_info.append((predicate, object))

    def __publish__(self):
        id = self.__pubid__()
        id_prefix = "pub-" + id

        head_uri = BASE["head-" + id]
        assertions_uri = BASE["assertions-" + id]
        provenance_uri = BASE["provenance-" + id]
        pub_info_uri = BASE["pubInfo-" + id]

        graph = []

        c = head_uri

        s = BASE[id_prefix]
        p = RDF.type
        o = NP.Nanopublication

        graph.append((s, p, o, c))

        p = NP.hasAssertion
        o = assertions_uri

        graph.append((s, p, o, c))

        p = NP.hasProvenance
        o = provenance_uri

        graph.append((s, p, o, c))

        p = NP.hasPublicationInfo
        o = pub_info_uri

        graph.append((s, p, o, c))

        for item in self.__rdf__(assertions_uri):
            graph.append(item)

        c = provenance_uri

        for claim in self.provenance:
            s = assertions_uri
            p = PROV[claim[0]]
            o = claim[1]
            graph.append((s, p, o, c))

        c = pub_info_uri

        s = BASE[id_prefix]
        p = PROV.generatedAtTime
        o = Literal(
            datetime.now().replace(microsecond=0).isoformat(), datatype=XSD.dateTime
        )

        graph.append((s, p, o, c))

        p = PROV.wasGeneratedBy
        o = Literal("recipe-handler")

        graph.append((s, p, o, c))

        for claim in self.pub_info:
            s = BASE[id_prefix]
            p = PROV[claim[0]]
            o = claim[1]
            graph.append((s, p, o, c))

        return graph

    def __pubid__(self):
        return self._pubid


class NanopubBundle(_Nanopub):
    """Ties together many resources into one nanopublication."""

    def __init__(self):
        super().__init__()
        self.items = []

    def add(self, item):
        self.items.append(item)

    def __rdf__(self, c):
        quads = []

        for item in self.items:
            quads += item.__rdf__(c)

        return quads

class Recipe(_Nanopub):
    """An instance of a recipe."""

    RECIPE = lambda x: BASE["recipe" + SEP + x]
    USES = BASE["uses"]
    TAGGED = BASE["tagged"]

    def __init__(self):
        super().__init__()
        self.title = ""
        self.ingredients = []
        self.steps = []
        self.tags = []

    def __str__(self):
        res = ""
        res += self.title + "\n"
        res += "{0} ingredients".format(len(self.ingredients)) + "\n"
        res += "{0} steps".format(len(self.ingredients)) + "\n"

        return res

    def __rdf__(self, c):
        """Constructs the recipe's own RDF triples."""
        triples = []

        s = self.__uri__()
        p = RDF.type
        o = BASE["recipe"]
        triples.append((s, p, o, c))

        s = self.__uri__()
        p = RDFS["label"]
        o = litquote(self.title)
        triples.append((s, p, o, c))

        for ing in self.ingredients:
            s = self.__uri__()
            p = Recipe.USES
            o = ing.__uri__(self.__uri__())
            triples.append((s, p, o, c))

            triples += ing.__rdf__(self.__uri__(), c)

        for tag in self.tags:
            s = self.__uri__()
            p = Recipe.TAGGED
            o = tag.__uri__()
            triples.append((s, p, o, c))

            triples += tag.__rdf__(c)

        return triples

    def __uri__(self):
        digest = self.__binhash__()
        tag = encode(digest, "hex").decode("utf-8")[0:8]
        return Recipe.RECIPE(tag + "-" + quote(self.title))

    def __array__(self):
        items = []
        items.append(self.title)
        for ing in self.ingredients:
            items += ing.__array__()
        return items

    def __pubid__(self):
        m = hashlib.sha1()
        m.update(self.title.encode("utf-8"))
        return m.hexdigest()

    def __binhash__(self):
        m = hashlib.sha1()
        m.update(self.title.encode("utf-8"))

        for ing in self.ingredients:
            m.update(ing.__binhash__())

        for tag in self.tags:
            m.update(tag.__binhash__())

        for step in self.steps:
            m.update(step.encode("utf-8"))

        return m.digest()


class RawIngredient(_Data):
    """An unparsed ingredient."""

    def __init__(self, text=""):
        self.text = text

    def __array__(self):
        return [self.text]


class Tag(_Data):
    """A recipe's tag."""

    TAG = lambda x: BASE["tag" + SEP + x]

    def __init__(self, name):
        self.name = name

    def __rdf__(self, c):
        triples = []

        tag_uri = self.__uri__()

        s = tag_uri
        p = RDF.type
        o = BASE["tag"]
        triples.append((s, p, o, NOCONTEXT))

        s = tag_uri
        p = RDFS.label
        o = litquote(self.name)
        triples.append((s, p, o, NOCONTEXT))

        return triples

    def __uri__(self):
        return Tag.TAG(quote(self.name))

    def __array__(self):
        return [self.name]

    def __binhash__(self):
        m = hashlib.sha1()
        m.update(self.name.encode("utf-8"))
        return m.digest()


class Ingredient(_Data):
    """A parsed ingredient."""

    ING = lambda x: BASE["ingredient" + SEP + x]

    def __init__(self):
        self.name = ""
        self.quantity = ""
        self.unit = ""
        self.comment = ""

    def __rdf__(self, owner, c):
        """Uses the owner's URI to get a unique, concrete identifier"""
        triples = []

        ing_uri = self.__uri__(owner)

        s = ing_uri
        p = BASE["ing_name"]
        o = self.name.__uri__()
        triples.append((s, p, o, c))

        triples += self.name.__rdf__(c)

        s = ing_uri
        p = BASE["ing_quantity"]
        o = litquote(self.quantity)
        triples.append((s, p, o, c))

        s = ing_uri
        p = BASE["ing_unit"]
        o = litquote(self.unit)
        triples.append((s, p, o, c))

        s = ing_uri
        p = BASE["ing_comment"]
        o = litquote(self.comment)
        triples.append((s, p, o, c))

        s = ing_uri
        p = RDF.type
        o = BASE["ingredientuse"]
        triples.append((s, p, o, c))

        return triples

    def __uri__(self, owner):
        return URIRef(owner + SEP + "ingredient" + SEP + quote(self.name.__str__()))

    def __array__(self):
        return [self.name]

    def __binhash__(self):
        m = hashlib.sha1()
        m.update(self.name.__binhash__())
        m.update(self.quantity.encode("utf-8"))
        m.update(self.unit.encode("utf-8"))
        m.update(self.comment.encode("utf-8"))
        return m.digest()


class IngredientName(_Data):
    """The name of an ingredient; can be shared by ingredient instances."""

    ING_NAME = lambda x: BASE["ingredientname" + SEP + x]

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if self is other:
            return True
        elif type(self) != type(other):
            return False
        else:
            return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __rdf__(self, c):
        triples = []

        uri = self.__uri__()

        s = uri
        p = RDFS.label
        o = litquote(self.name)
        triples.append((s, p, o, NOCONTEXT))

        s = uri
        p = RDF.type
        o = BASE["ingredientname"]
        triples.append((s, p, o, NOCONTEXT))

        return triples

    def __uri__(self):
        return IngredientName.ING_NAME(quote(self.name))

    def __array__(self):
        return [self.name]

    def __binhash__(self):
        m = hashlib.sha1()
        m.update(self.name.encode("utf-8"))
        return m.digest()


class Linkage(_Nanopub):
    """An equivalence relation between two entities."""

    RELATED = OWL["equivalentClass"]

    def __init__(self, subject, object):
        super().__init__()
        self.subject = subject
        self.object = object
        self.add_prov("wasGeneratedBy", Literal("linker"))

    def __rdf__(self, c):
        """Returns the triple describing the relationship."""
        s = URIRef(self.subject.__uri__())
        p = self.__uri__()
        o = URIRef(self.object.__uri__())
        return [(s, p, o, c)]

    def __uri__(self):
        """Returns the URI for a relationship."""
        return Linkage.RELATED

    def __array__(self):
        return self.subject.__array__() + self.object.__array__()


class Resource(_Data):
    """Any arbitrary RDF resource."""

    def __init__(self, uri):
        self.uri = uri

    def __uri__(self):
        return URIRef(self.uri)

    def __array__(self):
        return [self.uri]


class USDAEntry(_Data):
    """A USDA food id, its description, and a list of qualities."""

    def __init__(self, id, desc, qualities):
        self.id = id
        self.desc = desc
        self.qualities = qualities

    def __uri__(self):
        return Literal(self.id, datatype=XSD.integer)


__all__ = []
_locals = dict(locals())  # pylint: disable=invalid-name
datatypes = {}  # pylint: disable=invalid-name


def _setup():
    classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    for _, obj in classes:
        if issubclass(obj, _Data) and obj != _Data:
            __all__.append(obj.__name__)
            datatypes[obj.__name__] = obj


_setup()
