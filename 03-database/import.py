import sqlite3
import sys
import os

os.remove(sys.argv[2])

conn = sqlite3.connect(sys.argv[2])
cur = conn.cursor()

cur.execute("create table person ( id integer primary key not null, born integer, died integer, name varchar not null )")
cur.execute("INSERT INTO person VALUES (?, ?, ?, ?)", (None, None, 1956, "Wolfgang amadeus"))
conn.commit()
cur.execute("SELECT id, born, died, name FROM person WHERE name = (?)", ('Wolfgang amadeus',))
user = cur.fetchone()

if user is None:
    cur.execute("INSERT INTO person VALUES (?, ?, ?, ?)", (None, 1954, 1956, "Wolfgang amadeus"))
else:
    if user[1] is None:
        cur.execute("UPDATE person SET born = (?) WHERE id = (?)", (1954, user[0]))
    if user[2] is None:
        cur.execute("UPDATE person SET died = (?) WHERE id = (?)", (1956, user[0]))
conn.commit()
conn.close()
