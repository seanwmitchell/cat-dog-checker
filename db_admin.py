# Libraries to import for database access

import json
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

with open('/etc/config.json') as config_file:
    config = json.load(config_file)
db_username = config.get('DB_USERNAME')
db_password = config.get('DB_PASSWORD')

print(db_username)
print(db_password)


def db_check():

    # a function to check if we have the database established already. If no, call the setup functions.

    # try:
    #     conn = psycopg2.connect("dbname=cat_dog_checker user=" + db_username + " password=" + db_password)
    #     conn.close()
    # except:
    create_database()
    create_table()

def create_database():

    # a function to initially establish the database

    conn = psycopg2.connect("dbname=cat_dog_checker user=postgres password=")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute(sql.SQL("CREATE DATABASE cat_dog_checker\
            ").format(sql.Identifier('cat_dog_checker')))
    conn.close()
    print("***** database setup.")

def create_table():

    # a function to create the table in the new db

    conn = psycopg2.connect("dbname=cat_dog_checker user=postgres password=")
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