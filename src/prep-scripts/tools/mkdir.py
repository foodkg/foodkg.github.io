import os
import sys

if len(sys.argv) < 2:
    print("Usage: mkdir.py dir [dir ...]")
try:
    for directory in sys.argv[1:]:
        os.makedirs(directory)
except OSError:
    pass
