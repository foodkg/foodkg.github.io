import csv
import sys

import rdflib
import rdflib.util

if len(sys.argv) != 3:
    print("Usage: extract-labels.py source_rdf output")

g = rdflib.Graph()
g.parse(sys.argv[1], rdflib.util.guess_format(sys.argv[1]))

pairs = []

for pair in g.subject_objects(rdflib.RDFS["label"]):
    pairs.append([pair[1].__str__(), pair[0].__str__()])

f = open(sys.argv[2], "w")
w = csv.writer(f)

w.writerow(["str", "Resource"])
for pair in pairs:
    w.writerow(pair)
