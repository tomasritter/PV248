import sqlite3
import sys


conn = sqlite3.connect(sys.argv[2])
cur = conn.cursor()

conn.execute("create table person ( id integer primary key not null, born integer, died integer, name varchar not null )")
conn.execute("INSERT INTO table person VALUES (?, ?, ?, ?)", (1, 1954, 1956, "Wolfgang amadeus"))
conn.commit()
conn.close()

