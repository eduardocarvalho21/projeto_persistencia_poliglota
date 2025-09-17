import sqlite3
from typing import List, Dict

DB_PATH = "data.sqlite"

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa o banco criando tabelas via schema.sql"""
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript(open("schema.sql").read())  
    conn.commit()
    conn.close()

def insert_country(name: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO country(name) VALUES(?)", (name,))
    conn.commit()
    conn.close()

def insert_state(name: str, country_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO state(name, country_id) VALUES(?,?)", (name, country_id))
    conn.commit()
    conn.close()

def insert_city(name: str, state_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO city(name, state_id) VALUES(?, ?)", (name, state_id))
    conn.commit()
    conn.close()

def get_cities_by_state(state_id: int) -> List[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM city WHERE state_id = ?", (state_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_states_by_country(country_id: int) -> List[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM state WHERE country_id = ?", (country_id,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

def get_countries() -> List[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM country")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows