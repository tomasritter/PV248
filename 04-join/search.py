import sqlite3
import sys
import json

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        if not row[idx] is None:
            d[col[0]] = row[idx]
    return d

def add_value_to_dict(dict, key, value):
    if not value is None:
        dict[key] = value
        
def add_values_to_dict_list(dict, key, values, cur):
    dict[key] = []
    for v in values:
        dict[key].append(dict_factory(cur, v))
        

def get_composer_info(cur, row):
    d = {}
    d["Print Number"] = row[1]

    composers = cur.execute("SELECT name, born, died FROM score_author INNER JOIN person ON \
                            score_author.composer = person.id WHERE score_author.score = (?)", (row[2],))
    add_values_to_dict_list(d, "Composer", composers, cur)
    
    add_value_to_dict(d, "Title", row[4])

    add_value_to_dict(d, "Genre", row[5])

    add_value_to_dict(d, "Key", row[6])
        
    add_value_to_dict(d, "Composition Year", row[7])
    
    add_value_to_dict(d, "Edition", row[8])
        
    editors = cur.execute("SELECT name, born, died FROM edition_author INNER JOIN person ON \
                            edition_author.editor = person.id WHERE edition_author.edition = (?)", (row[3],))
    add_values_to_dict_list(d, "Editor", editors, cur)
        
    voices = cur.execute("SELECT range, voice.name FROM voice INNER JOIN score ON \
                            voice.score = score.id WHERE score.id = (?) ORDER BY number", (row[2],))
    add_values_to_dict_list(d, "Voices", voices, cur)
    
    add_value_to_dict(d, "Partiture", row[9])
     
    add_value_to_dict(d, "Incipit", row[10])
    return d

conn = sqlite3.connect("scorelib.dat")
cur = conn.cursor()

query = "%" + sys.argv[1] + "%"
cur.execute("SELECT person.name, print.id, score.id, edition.id, score.name, \
            score.genre, score.key, score.year, edition.name, partiture, incipit FROM \
            print INNER JOIN edition ON print.edition = edition.id INNER JOIN score ON \
            edition.score = score.id INNER JOIN score_author ON score.id = score_author.score \
            INNER JOIN person ON score_author.composer = person.id WHERE person.name like (?)", (query,))

authors = cur.fetchall()
dict = {}
for a in authors:
    if not a[0] in dict:
        dict[a[0]] = []
    dict[a[0]].append(get_composer_info(cur, a))
    
print(json.dumps(dict, indent = 4, ensure_ascii = False))
