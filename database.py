import sqlite3
import pandas as pd

DB_NAME = "shock_sim_mvp.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS adaptive_memory (
            source TEXT,
            target TEXT,
            multiplier REAL,
            PRIMARY KEY (source, target)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            model_version TEXT,
            scenario TEXT,
            expected_damage REAL,
            observed_damage REAL,
            confidence INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def save_memory_to_db(memory):
    conn = get_connection()
    cursor = conn.cursor()
    for (source, target), mult in memory.items():
        cursor.execute('''
            INSERT OR REPLACE INTO adaptive_memory (source, target, multiplier)
            VALUES (?, ?, ?)
        ''', (source, target, float(mult)))
    conn.commit()
    conn.close()

def load_memory_from_db(graph):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT source, target, multiplier FROM adaptive_memory')
    rows = cursor.fetchall()
    conn.close()
    
    memory = {(u, v): 1.0 for u, v in graph.edges()}
    for source, target, mult in rows:
        if graph.has_edge(source, target):
            memory[(source, target)] = float(mult)
    return memory

def log_event_to_db(record):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO event_history (model_version, scenario, expected_damage, observed_damage, confidence)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        record.get("Model"),
        record.get("Scenario"),
        record.get("Predicted Expected Damage"),
        record.get("Observed Damage"),
        record.get("Confidence (%)")
    ))
    conn.commit()
    conn.close()

def get_event_history_df():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM event_history ORDER BY timestamp DESC", conn)
    conn.close()
    return df
    
