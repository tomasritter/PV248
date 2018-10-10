import re
import sys

class Print:
    def __init__(self, edition, print_id, partiture):
        self.edition = edition
        self.print_id = print_id
        self.partiture = partiture

    def format(self):
        s = "Print Number: " + str(self.print_id) + "\n"
        s += "Composer: "
        # Go through each compsoer in the list
        for i in range(len(self.edition.composition.authors)):
            c = self.edition.composition.authors[i]
            # Add name to the output string
            s += c.name
            # Add year of birth/death if present
            if not c.born is None or not c.died is None:
                s += " (" + (str(c.born) if not c.born is None else "")
                s += "--" + (str(c.died) if not c.died is None else "") + ")"
            # Add "; " behind all names except for the last one
            if i != len(self.edition.composition.authors) - 1:
                s += "; "
        s += "\n"
        s += "Title: " + (self.edition.composition.name or "") + "\n"
        s += "Genre: " + (self.edition.composition.genre or "") + "\n"
        s += "Key: " + (self.edition.composition.key or "") + "\n"
        s += "Composition Year: " + (str(self.edition.composition.year) if not self.edition.composition.year is None else "") + "\n"
        s += "Edition: " + (self.edition.name or "") + "\n"
        s += "Editor: "
        for i in range(len(self.edition.authors)):
            c = self.edition.authors[i]
            s += c.name
            # Add ", " behind all names except for the last one
            if i != len(self.edition.authors) - 1:
                s += ", "
        s += "\n"
        # Add voices to the output string
        for i in range(len(self.edition.composition.voices)):
            v = self.edition.composition.voices[i]
            # Uses index + 1 to get the original order of Voice lines
            s += "Voice " + str(i + 1) + ": "
            if v.range is None: 
                s += v.name or ""
            elif v.name is None:
                s += v.range
            else:
                s += v.range + ", " + v.name
            s += "\n"
        s += "Partiture: " + ("yes" if self.partiture else "no") + "\n"
        s += "Incipit: " + (self.edition.composition.incipit if not self.edition.composition.incipit is None else "") + "\n"
        print(s)
        
    def composition(self):
        return self.edition.composition

class Edition:
    def __init__(self, composition, authors, name):
        self.composition = composition
        self.authors = authors
        self.name = name

class Composition:
    def __init__(self, name, incipit, key, genre, year, voices, authors):
        self.name = name
        self.incipit = incipit
        self.key = key
        self.genre = genre
        self.year = year
        self.voices = voices
        self.authors = authors

class Voice:
    def __init__(self, name, range):
        self.name = name
        self.range = range

class Person:
    def __init__(self, name, born, died):
        self.name = name
        self.born = born
        self.died = died

def get_authors(composers):
    authors = []
    if composers is None:
        return authors
    s = re.split(r"; ", composers)
    for a in s:
        # If there is not a "(" symbol, there is no year of birth/death
        if a.find("(") == -1:
            authors.append(Person(a, None, None))
        else:
            # Match name an everything in the brackets
            m = re.match(r"(.*) \((.*)\)", a)
            name = m.group(1)
            # Try to match numbers around "--" symbols
            m1 = re.match(r"(\d*)--?(\d*)", m.group(2))
            if m1 is None:
                authors.append(Person(name, None, None))
                continue
            # Use matched numbers only if there are 4 digits
            born = int(m1.group(1)) if len(m1.group(1)) == 4 else None
            died = int(m1.group(2)) if len(m1.group(2)) == 4 else None
            authors.append(Person(name, born, died))
    return authors

def get_voices(dict):
    voices = []
    k = 1
    while True:
        # Go through all the listed voices
        if ("Voice " + str(k)) in dict:
            v = dict["Voice " + str(k)]
            # Empty case
            if v is None or v == "": 
                voices.append(Voice(None, None))
            # If there is range, add id
            elif "--" in v:
                # Some lines of Voice were seperated by ";", instead use ","
                v = v.replace('; ', ', ')
                m = v.split(", ", 1)
                voices.append(Voice(m[1] if len(m) != 1 else None, m[0]))
            else:
                voices.append(Voice(v or None, None))
            # Increase the number of the voice
            k += 1
        else: 
            break
    return voices

def get_editors(editors_string):
    editors = []
    if editors_string is None:
        return editors
    # Strip ',' and ' ' symbols from the right 
    editors_string = editors_string.rstrip(", ")
    # Split on comma
    s = re.split(r", ", editors_string)
    skip = False
    for i in range(len(s)):
        # Skip only when else statement has executed in the iteration before
        if skip:
            skip = False
            continue
        # If split contains ' ', it's a full name an will be used as such
        if s[i].find(" ") != -1:
            editors.append(Person(s[i], None, None))
        else:
            # If split doesn't contain ' ', then try to get next split as part of the name
            editors.append(Person(s[i] + ((", " + s[i + 1]) if i + 1 < len(s) else ""), None, None))
            skip = True
    return editors


def get_year(comp_year):
    if comp_year is None:
        return None
    m = re.match(r"\d\d\d\d", comp_year)
    return int(m.group(0)) if m is not None else None

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
    for line in open(filename, 'r'):
        m = r.match(line)
        if m is None:
            continue
        dict[m.group(1)] = m.group(2) or None
        # If incipit has been parsed, we know we are at the endo of a "block"
        if m.group(1) == "Incipit":
            prints.append(get_print(dict))
            dict = {}
    return prints
