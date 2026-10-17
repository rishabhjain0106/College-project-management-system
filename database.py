# database.py
import mysql.connector
import credentials as crds

DB_CONFIG = {
    "host": crds.DB_HOST,
    "user": crds.DB_USER,
    "password": crds.DB_PASS,
    "database": crds.DB_NAME
}

def get_conn():
    return mysql.connector.connect(**DB_CONFIG)

def fetch_one(query, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    row = cur.fetchone()
    conn.close()
    return row

def fetch_all(query, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def execute(query, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    conn.close()
