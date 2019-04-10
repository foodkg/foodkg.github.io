import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import data
from data import Recipe, Ingredient, Tag
from rdflib import Dataset
from rdflib import URIRef, Literal

r1 = Recipe()
r1.title = "Foo"

i1_1 = Ingredient()
i1_1.name = "Foo_1"

t1 = Tag("Baz")

r1.ingredients.append(i1_1)
r1.tags.append(t1)

r1.add_prov("wasDerivedFrom", URIRef("http://recipes.com/r/Foo"))
r1.add_pub_info("wasAttributedTo", Literal("Jeff the Data Guy"))
summed = Dataset()

for quad in r1.__publish__():
    summed.add(quad)

summed.namespace_manager.bind("np", data.NP, True)
summed.namespace_manager.bind("recipe-kb", data.BASE, True)
summed.namespace_manager.bind("prov", data.PROV, True)


print(summed.serialize(format="trig").decode("utf-8"))

u1 = data.USDAEntry(12345, "CHEESE,SERIOUSLY SPICY", [])

l1 = data.Linkage(data.IngredientName(i1_1.name), u1)

summed = Dataset()

for quad in l1.__publish__():
    summed.add(quad)

summed.namespace_manager.bind("np", data.NP, True)
summed.namespace_manager.bind("recipe-kb", data.BASE, True)
summed.namespace_manager.bind("prov", data.PROV, True)

print(summed.serialize(format="trig").decode("utf-8"))
