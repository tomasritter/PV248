import sys
import re

def get_authors(dict)
    authors = []
    return authors

def get_

def get_print(dict):
    printId = dict["Print Number"]
    print
    return print;

def load(filename):
    r = re.compile(r"(.*?): (.*)")
    prints = []
    data = {}
    for line in open(sys.argv[1], 'r'):
        if line == "":
            prints.append(get_print(dict))
            dict = {}
            continue
        m = r.match(line)
        dict[m.group(1)] = m.group(2) or None

    return prints


prints = load(sys.argv[1])

for p in prints:
    print("VALUE")