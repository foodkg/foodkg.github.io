import os
import hashlib
import json
import sys
import requests

from urllib.parse import urlparse

if len(sys.argv) < 2:
    print("Usage: scraper.py url_json_file [start] [end]")
    sys.exit(64)

def scrape(url, id, filepath):

    if not os.path.exists(filepath):
        os.makedirs(filepath)

    if os.path.isfile(filepath + id):
        return None

    try:
        r = requests.get(url)
        print(r.status_code)
        print(r)
        if not r.ok:
            save(filepath, id, "")
        else:
            save(filepath, id, r.text)
    except Exception as e:
        print("Exception raised!")
        print(e)
        save(filepath, id, "")

def save(filepath, hex, response):
    with open(filepath + hex, "w") as file:
        file.write(response)

futures = []

items = json.load(open(sys.argv[1]))
cachedir = sys.argv[2] + "/"

if len(sys.argv) > 3:
    start = int(sys.argv[3])
else:
    start = 0

if len(sys.argv) > 4:
    end = int(sys.argv[4])
else:
    end = len(items)

items = items[start:end]

milestone = 0
for index, item in enumerate(items):
    scrape(item["url"], item["id"], cachedir)

    if index - milestone > len(items) // 100:
        print("Progress: {0:.2f}%".format((index / len(items) * 100)))
        milestone = index
