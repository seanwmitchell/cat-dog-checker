# Libraries to import for database access

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def db_check():

    # a function to check if we have the database established already. If no, call the setup functions.

    try:
        conn = psycopg2.connect("dbname=cat_dog_checker user=seanm password=")
        conn.close()
    except:
        create_database()
        create_table()

    print("***** DB Check done")

def create_database():

    # a function to initially establish the database

    conn = psycopg2.connect("dbname=postgres user=seanm password=")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(sql.SQL("CREATE DATABASE cat_dog_checker\
            ").format(sql.Identifier('cat_dog_checker')))
    conn.close()
    print("***** database setup.")

def create_table():

    # a function to create the table in the new db

    conn = psycopg2.connect("dbname=cat_dog_checker user=seanm password=")
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(sql.SQL("""CREATE TABLE uploads_table(
            upload_id SERIAL PRIMARY KEY,
            file_name VARCHAR(255),
            label VARCHAR(255),
            confidence FLOAT(1),
            correct BOOLEAN,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );"""))
    conn.close()
    print("***** table setup.")