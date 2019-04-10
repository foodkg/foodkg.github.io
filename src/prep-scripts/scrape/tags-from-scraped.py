import json
import re
import os
import argparse

from collections import Counter
from html.parser import HTMLParser

class GeniusParser(HTMLParser):
    """Read json-ld data from a GeniusKitchen webpage."""

    def __init__(self):
        """Set up the parser."""
        super(GeniusParser, self).__init__()
        self.armed = False
        self.result = {}

    def handle_starttag(self, tag, attrs):
        """Detect when we have reached the json-ld block."""
        if tag == "script":
            for item in attrs:
                if item[0] == "type" and item[1] == "application/ld+json":
                    self.armed = True

    def handle_data(self, data):
        """Store the json-ld block for later retrieval."""
        if self.armed:
            self.result = json.loads(data)
            self.armed = False

prog = re.compile("content=\"(.*?)\"")

def read_file(filename):
    text = open(filename, "r").readlines()
    for line in text:
        if "sailthru" in line:
            string = prog.search(line).group(1)
            tags = string.split(",")
            return tags

    print("Nothing in " + filename)
    return []

tags = {}
filtered = [
    "time-to-make",
    "low-in-something",
    "course",
    "preparation",
    "main-ingredient",
    "dietary",
    "equipment",
    "technique"
]

def run(args):
    counter = Counter()
    for (dirpath, dirnames, filenames) in os.walk(args.cachedir):
        for file in filenames:
            tags[file] = list(filter(lambda x: x not in filtered, read_file(args.cachedir + "/" + file)))

    with open(args.output, "w") as file:
        json.dump(tags, file)

parser = argparse.ArgumentParser("Reads Genius Kitchen tags from downloaded webpages")

parser.add_argument("cachedir", help="Directory containing cached pages")
parser.add_argument("output", help="Where to write the resulting tags")

run(parser.parse_args())
