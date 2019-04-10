import zipfile
import sys

file = zipfile.ZipFile(sys.argv[1])
file.extractall(sys.argv[2])
file.close()