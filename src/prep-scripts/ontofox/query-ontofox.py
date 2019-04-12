import sys
import requests

if len(sys.argv) != 3:
    print("Usage: query-ontofox.py [configuration] [outfile]")

files = {
    'file': ('ontofox.txt', open(sys.argv[1], 'rb')),
}

response = requests.post('http://ontofox.hegroup.org/service.php', files=files)

with open(sys.argv[2], "w") as file:
    file.write(response.text)
