import sys
import os
from shutil import rmtree

if len(sys.argv) < 2:
    print("Usage: rm.py path [path ...]")

for path in sys.argv[1:]:
    try:
        rmtree(path)
    except OSError:
        try:
            os.remove(path)
        except OSError:
            pass
