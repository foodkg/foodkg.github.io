import sys
from urllib.request import urlretrieve

urlretrieve(sys.argv[1], filename=sys.argv[2])