import sqlite3
import sys
import os
from scorelib import *

os.remove(sys.argv[2])

conn = sqlite3.connect(sys.argv[2])
cur = conn.cursor()

cur.execute("create table person ( id integer primary key not null, \
                                  born integer, died integer, \
                                  name varchar not null )")
cur.execute("create table score ( id integer primary key not null, \
                                 name varchar, \
                                 genre varchar, \
                                 key varchar, \
                                 incipit varchar, \
                                 year integer )")
cur.execute("create table voice ( id integer primary key not null, \
                                 number integer not null, \
                                 score integer references score( id ) not null, \
                                 range varchar, \
                                 name varchar )")
cur.execute("create table edition ( id integer primary key not null, \
                                   score integer references score( id ) not null, \
                                   name varchar, \
                                   year integer )")
cur.execute("create table score_author( id integer primary key not null, \
                                       score integer references score( id ) not null, \
                                       composer integer references person( id ) not null )")
cur.execute("create table edition_author( id integer primary key not null, \
                                         edition integer references edition( id ) not null, \
                                         editor integer references person( id ) not null )")
cur.execute("create table print ( id integer primary key not null, \
                                 partiture char(1) default 'N' not null, \
                                 edition integer references edition( id ) )")

load(sys.argv[1], conn, cur)

cur.execute("INSERT INTO person VALUES (?, ?, ?, ?)", (None, None, 1956, "Wolfgang amadeus"))
cur.execute("SELECT id, born, died FROM person WHERE name = (?)", ('Wolfgang amadeus',))
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
