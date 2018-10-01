import sys
import re
from .scorelib import *

def get_authors(composers):
    r = re.compile(r"(.*) (\((.*)--(.*)\))?")
    authors = []
    s = re.split(r"; ", composers)
    for a in s:
        m = r.match(a)
        name = m.group(1)
        born = m.group(3) or None
        died = m.group(4) or None
        authors.append(Person(name, born, died))
    return authors

def get_voices(dict):
    r = re.compile(r"(([^ ,]*)--([^ ,]*)), (.*)")
    voices = []
    for k, v in dict:
        if k.startswith("Voice"):


def get_print(dict):
    printId = int(dict["Print Number"])
    authors = get_authors(dict["Composer"])
    name = dict["Title"]
    incipit = dict["Incipit"]
    key = dict["Key"]
    genre = dict["Genre"]
    partiture = True if "yes" in dict["Partiture"] else False
    name = dict["Edition"] or None
    voices = get_voices(dict)

    return print;

def load(filename):
    r = re.compile(r"(.*?): (.*)")
    prints = []
    data = {}
    for line in open(sys.argv[1], 'r'):
        if line == "":
            continue
        m = r.match(line)
        dict[m.group(1)] = m.group(2) or None
        if m.group(1) == "Incipit":
            prints.append(get_print(dict))
            dict = {}
    return prints


prints = load(sys.argv[1])

for p in prints:
    print("VALUE")