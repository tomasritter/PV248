import sys
import re
from scorelib import *

def get_authors(composers):
    authors = []
    if composers is None:
        return authors
    s = re.split(r"; ", composers)
    for a in s:
        if a.find("(") == -1:
            authors.append(Person(a, None, None))
        else:
            m = re.match(r"(.*) \((.*)\)", a)
            name = m.group(1)
            m1 = re.match(r"(\d*)--?(\d*)", m.group(2))
            if m1 is None:
                authors.append(Person(name, None, None))
                continue
            born = int(m1.group(1)) if len(m1.group(1)) == 4 else None
            died = int(m1.group(2)) if len(m1.group(2)) == 4 else None
            authors.append(Person(name, born, died))
    return authors

def get_voices(dict):
    r = re.compile(r"([^ ,]*--[^ ,]*)[;,]? (.*)?")
    voices = []
    k = 1
    while True:
        if ("Voice " + str(k)) in dict:
            v = dict["Voice " + str(k)]
            if v is None or v == "": 
                voices.append(Voice(None, None))
            elif "--" in v:
                v = v.replace('; ', ', ')
                m = v.split(", ", 1)
                voices.append(Voice(m[1] if len(m) != 1 else None, m[0]))
            else:
                voices.append(Voice(v or None, None))
            k += 1
        else: 
            break
    return voices

def get_editors(editors_string):
    editors = []
    if editors_string is None:
        return editors
    editors_string = editors_string.rstrip(", ")
    s = re.split(r", ", editors_string)
    skip = False
    for i in range(len(s)):
        if skip:
            skip = False
            continue
        if s[i].find(" ") != -1:
            editors.append(Person(s[i], None, None))
        else:
            editors.append(Person(s[i] + ((", " + s[i + 1]) if i + 1 < len(s) else ""), None, None))
            skip = True
    return editors


def get_year(comp_year):
    if comp_year is None:
        return None
    m = re.match(r"\d\d\d\d", comp_year)
    return m.group(0) if m is not None else None

def get_print(dict):
    printId = int(dict["Print Number"])
    authors = get_authors(dict["Composer"])
    title = dict["Title"] if "Title" in dict else None
    incipit = dict["Incipit"] if "Incipit" in dict else None
    key = None
    if "Key" in dict:
        key = None if dict["Key"] is "" else dict["Key"]
    genre = None
    if "Genre" in dict:
        genre = None if dict["Genre"] is "" else dict["Genre"]
    partiture = False
    if "Partiture" in dict and not dict["Partiture"] is None and "yes" in dict["Partiture"]:
            partiture = True
    name = dict["Edition"] or None
    voices = get_voices(dict)
    editors = get_editors(dict["Editor"]) if "Editor" in dict else []
    year = get_year(dict["Composition Year"]) if "Composition Year" in dict else None
    composition = Composition(title, incipit, key, genre, year, voices, authors)
    edition = Edition(composition, editors, name)
    p = Print(edition, printId, partiture)
    return p;

def load(filename):
    r = re.compile(r"(.*)?: ?(.*)")
    prints = []
    dict = {}
    for line in open(sys.argv[1], 'r'):
        m = r.match(line)
        if m is None:
            continue
        dict[m.group(1)] = m.group(2) or None
        if m.group(1) == "Incipit":
            prints.append(get_print(dict))
            dict = {}
    return prints


prints = load(sys.argv[1])

for p in prints:
    print(p.format())