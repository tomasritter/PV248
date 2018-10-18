import re
import sys
import sqlite3

# Each class has a method add_to_db, which returns id of itself in the database

class Print:
    def __init__(self, edition, print_id, partiture):
        self.edition = edition
        self.print_id = print_id
        self.partiture = partiture
        
    def composition(self):
        return self.edition.composition
    
    def add_to_db(self, conn, cur):
        edition_id = self.edition.add_to_db(conn, cur)
        cur.execute("INSERT INTO print VALUES (?, ?, ?)", 
                    (self.print_id, 'Y' if self.partiture else 'N', edition_id))

class Edition:
    def __init__(self, composition, authors, name):
        self.composition = composition
        self.authors = authors
        self.name = name
            
    def add_to_db(self, conn, cur):
        composition_id = self.composition.add_to_db(conn, cur)
        # checking for duplicates
        cur.execute("SELECT id, name FROM edition WHERE score = (?)", (composition_id, ))
        editions = cur.fetchall()
        # nothing found, create a new edition
        if not editions:
            return self.add_edition_to_db(conn, cur, composition_id)
        
        for e in editions:
            # Check whether the edition has the same name and authors
            if self.name == e[1] and self.same_authors(conn, cur, e[0]):
                # It does, return id of edition already in db
                return e[0]
        return self.add_edition_to_db(conn, cur, composition_id)

    #Adds edition and its authors to db    
    def add_edition_to_db(self, conn, cur, composition_id):
        cur.execute("INSERT INTO edition VALUES (?, ?, ?, ?)", 
                    (None, composition_id, self.name, None))
        edition_id = cur.lastrowid
        for author in self.authors:
            person_id = author.add_to_db(conn, cur)
            cur.execute("INSERT INTO edition_author VALUES (?, ?, ?)", (None, edition_id, person_id))
        return edition_id
    
    # Duplicated code except for the sql query, I think it's better to have
    # logic for editors and composers seperated
    def same_authors(self, conn, cur, edition_id):
        cur.execute("SELECT name FROM edition_author INNER JOIN person ON \
                    edition_author.editor = person.id WHERE edition = (?)", (edition_id, ))
        # Get all authors as list
        authors_names = [i[0] for i in cur.fetchall()]
        # Compare length
        if len(authors_names) != len(self.authors):
            return False
        self_authors_names = []
        # Get all names of authors in self
        for a in self.authors:
            self_authors_names.append(a.name)
        # Return whether the lists are equal
        return sorted(self_authors_names) == sorted(authors_names)

class Composition:
    def __init__(self, name, incipit, key, genre, year, voices, authors):
        self.name = name
        self.incipit = incipit
        self.key = key
        self.genre = genre
        self.year = year
        self.voices = voices
        self.authors = authors

    def add_to_db(self, conn, cur):
        cur.execute("SELECT id, name, genre, key, incipit, year FROM score WHERE name = (?)", (self.name,))
        score = cur.fetchone()
        # Check whether the score with the same name is the same in all other things,
        # If at least one is different, create new entry in database
        # Else return value already in db
        if score is None or\
            score[2] != self.genre or score[3] != self.key or \
            score[4] != self.incipit or score[5] != self.year or \
            not self.same_authors(conn, cur, score[0]) or \
            not self.same_voices(conn, cur, score[0]):
            return self.add_composition_to_db(conn, cur)
        else:
            return score[0]
    
    def add_composition_to_db(self, conn, cur):
        cur.execute("INSERT INTO score VALUES (?, ?, ?, ?, ?, ?)", 
                        (None, self.name, self.genre, self.key, self.incipit, self.year))
        composition_id = cur.lastrowid
        for author in self.authors:
            person_id = author.add_to_db(conn, cur)
            cur.execute("INSERT INTO score_author VALUES (?, ?, ?)", (None, composition_id, person_id))
        for index, voice in enumerate(self.voices, start=1):
            voice.add_to_db(conn, cur, index, composition_id)
        return composition_id
    
    def same_authors(self, conn, cur, score_id):
        cur.execute("SELECT name FROM score_author INNER JOIN person ON \
                    score_author.composer = person.id WHERE score = (?)", (score_id, ))
        # Compare length
        authors_names = [i[0] for i in cur.fetchall()]
        # Compare length
        if len(authors_names) != len(self.authors):
            return False
        self_authors_names = []
        # Get all names of authors in self
        for a in self.authors:
            self_authors_names.append(a.name)
        # Return whether the lists are equal
        return sorted(self_authors_names) == sorted(authors_names)
        
    def same_voices(self, conn, cur, score_id):
        cur.execute("SELECT number, range, name FROM voice WHERE score = (?) ORDER BY number", (score_id, ))
        voices = cur.fetchall()
        if len(voices) != len(self.voices):
            return False
        for i in range(0, len(voices)):
            if voices[i][1] != self.voices[i].range or voices[i][2] != self.voices[i].name:
                return False
        return True
                

class Voice:
    def __init__(self, name, range):
        self.name = name
        self.range = range

    def add_to_db(self, conn, cur, index, composition_id):
        cur.execute("INSERT INTO voice VALUES (?, ?, ?, ?, ?)", 
                    (None, index, composition_id, self.range, self.name)) 

class Person:
    def __init__(self, name, born, died):
        self.name = name
        self.born = born
        self.died = died

    def add_to_db(self, conn, cur):
        cur.execute("SELECT id, born, died FROM person WHERE name = (?)", (self.name,))
        person = cur.fetchone()
        # If no person of the same name found, insert it
        if person is None:
            cur.execute("INSERT INTO person VALUES (?, ?, ?, ?)", (None, self.born, self.died, self.name))
            return cur.lastrowid
        else:
            # Check whether new born or died data could be used to update the db
            if person[1] is None:
                cur.execute("UPDATE person SET born = (?) WHERE id = (?)", (self.born, person[0]))
            if person[2] is None:
                cur.execute("UPDATE person SET died = (?) WHERE id = (?)", (self.died, person[0]))
            return person[0]
        

def get_authors(composers):
    authors = []
    if composers is None:
        return authors
    s = re.split(r"; ", composers)
    for a in s:
        # If there is not a "(" symbol, there is no year of birth/death
        if a.find("(") == -1:
            authors.append(Person(a.rstrip(), None, None))
        else:
            # Match name an everything in the brackets
            m = re.match(r"(.*) \((.*)\)", a)
            name = m.group(1).rstrip()
            # Try to match numbers around "--" symbols
            m1 = re.match(r"(\d*)--?(\d*)", m.group(2))
            # If nothing matched within the brackets
            if m1 is None:
                born_match = re.match(r"\*(\d*)", m.group(2))
                died_match = re.match(r"\+(\d*)", m.group(2))
                born = int(born_match.group(1)) if not born_match is None and len(born_match.group(1)) == 4 else None
                died = int(died_match.group(1)) if not died_match is None and len(died_match.group(1)) == 4 else None
                authors.append(Person(name, born, died))
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
    
    # Remove possible brackets and right whitespace
    for i in range(len(s)):
        ss = s[i].split("(")[0]
        s[i] = ss.rstrip()
        
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

def add_to_db(dict, conn, curr):
    printId = int(dict["Print Number"])
    authors = get_authors(dict["Composer"])
    title = dict["Title"] if "Title" in dict else None
    title = title if title is None else title.rstrip()
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
    
    p.add_to_db(conn, curr)

    
def load(filename, conn, cur):
    r = re.compile(r"(.*)?: *(.*)")
    dict = {}
    for line in open(filename, 'r'):
        m = r.match(line)
        if m is None:
            continue
        dict[m.group(1)] = m.group(2).rstrip() or None
        # If incipit has been parsed, we know we are at the endo of a "block"
        if m.group(1) == "Incipit":
            add_to_db(dict, conn, cur)
            dict = {}
