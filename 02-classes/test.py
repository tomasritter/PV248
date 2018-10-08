import sys
from scorelib import *

prints = load(sys.argv[1])

for p in prints:
    p.format()