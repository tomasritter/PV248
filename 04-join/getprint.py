import sqlite3
import sys
import json

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        if not row[idx] is None:
            d[col[0]] = row[idx]
    return d

conn = sqlite3.connect("scorelib.dat")
cur = conn.cursor()

id = sys.argv[1]
authors = cur.execute("SELECT person.name, born, died FROM \
            print INNER JOIN edition ON print.edition = edition.id \
            INNER JOIN score ON \
            edition.score = score.id INNER JOIN score_author ON score.id = score_author.score \
            INNER JOIN person ON score_author.composer = person.id WHERE print.id = (?)", (id,))

list = []
for a in authors:
    list.append(dict_factory(cur, a))
    
print(json.dumps(list, indent = 4, ensure_ascii=False))