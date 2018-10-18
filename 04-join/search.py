import sqlite3
import sys
import json

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        if not row[idx] is None:
            d[col[0]] = row[idx]
    return d

def get_composer_info(cur, row):
    d = {}
    d["Print Number"] = row[1]
    
    d["Composer"] = []
    composers = cur.execute("SELECT name, born, died FROM score_author INNER JOIN person ON \
                            score_author.composer = person.id WHERE score_author.score = (?)", (row[2],))
    for c in composers:
        d["Composer"].append(dict_factory(cur, c))
    
    if not row[4] is None:
        d["Title"] = row[4]
    
    if not row[5] is None:
        d["Genre"] = row[5]
        
    if not row[6] is None:
        d["Key"] = row[6]
        
    if not row[7] is None:
        d["Composition Year"] = row[7]
        
    if not row[8] is None:
        d["Edition"] = row[8]
        
    editors = cur.execute("SELECT name, born, died FROM edition_author INNER JOIN person ON \
                            edition_author.editor = person.id WHERE edition_author.edition = (?)", (row[3],))
    d["Editor"] = []
    for e in editors:
        d["Editor"].append(dict_factory(cur, e))
        
    voices = cur.execute("SELECT range, voice.name FROM voice INNER JOIN score ON \
                            voice.score = score.id WHERE score.id = (?) ORDER BY number", (row[2],))
    d["Voices"] = []
    for v in voices:
        d["Voices"].append(dict_factory(cur, v))
    
    if not row[9] is None:
        d["Partiture"] = row[9]
        
    if not row[10] is None:
        d["Incipit"] = row[10]
    return d

conn = sqlite3.connect("scorelib.dat")
cur = conn.cursor()

name = sys.argv[1]
query = "%" + name + "%"
cur.execute("SELECT person.name, print.id, score.id, edition.id, score.name, score.genre, score.key, score.year, \
            edition.name, partiture, incipit FROM \
            print INNER JOIN edition ON print.edition = edition.id \
            INNER JOIN score ON \
            edition.score = score.id INNER JOIN score_author ON score.id = score_author.score \
            INNER JOIN person ON score_author.composer = person.id WHERE person.name like (?)", (query,))

authors = cur.fetchall()
dict = {}
for a in authors:
    if not a[0] in dict:
        dict[a[0]] = []
    dict[a[0]].append(get_composer_info(cur, a))
    
print(json.dumps(dict, indent = 4, ensure_ascii = False))
