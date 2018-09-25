import sys
import re

def get_print(dict):
    
    return print;

def load(filename):
    r = re.compile(r"(.*): (.*)")
    prints = []
    data = {}
    for line in open(sys.argv[1], 'r'):
        if line == "":
            prints.append(get_print(dict))
        m = r.match(line)
        data[m.group(1)] = m.group(2)

    return prints


prints = load(sys.argv[1])

for p in prints:
    print("VALUE")