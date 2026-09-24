import os
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor

# قراءة رابط الاتصال بالسحابة من متغيرات البيئة في Streamlit Secrets
def get_connection():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        # رابط افتراضي للتطوير المحلي إن لم تتوفر الأسرار السحابية
        raise ValueError("DATABASE_URL environment variable is not set!")
    return psycopg2.connect(database_url, cursor_factory=RealDictCursor)

def init_db():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # جدول الذاكرة التكيفية للمضاعفات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS adaptive_memory (
                source TEXT,
                target TEXT,
                multiplier REAL,
                PRIMARY KEY (source, target)
            )
        ''')
        
        # جدول سجل الأحداث والتدقيق المؤسسي (Audit Trail)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_history (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                model_version TEXT,
                scenario TEXT,
                expected_damage REAL,
                observed_damage REAL,
                confidence INTEGER
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database initialization note: {e}")

def save_memory_to_db(memory):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        for (source, target), mult in memory.items():
            cursor.execute('''
                INSERT INTO adaptive_memory (source, target, multiplier)
                VALUES (%s, %s, %s)
                ON CONFLICT (source, target) 
                DO UPDATE SET multiplier = EXCLUDED.multiplier
            ''', (source, target, float(mult)))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error saving memory: {e}")

def load_memory_from_db(graph):
    memory = {(u, v): 1.0 for u, v in graph.edges()}
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT source, target, multiplier FROM adaptive_memory')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        for row in rows:
            source, target, mult = row['source'], row['target'], row['multiplier']
            if graph.has_edge(source, target):
                memory[(source, target)] = float(mult)
    except Exception as e:
        print(f"Could not load from cloud DB, using default memory: {e}")
    return memory

def log_event_to_db(record):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO event_history (model_version, scenario, expected_damage, observed_damage, confidence)
            VALUES (%s, %s, %s, %s, %s)
        ''', (
            record.get("Model"),
            record.get("Scenario"),
            record.get("Predicted Expected Damage"),
            record.get("Observed Damage"),
            record.get("Confidence (%)")
        ))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error logging event: {e}")

def get_event_history_df():
    try:
        conn = get_connection()
        df = pd.read_sql_query("SELECT * FROM event_history ORDER BY timestamp DESC", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame(columns=["id", "timestamp", "model_version", "scenario", "expected_damage", "observed_damage", "confidence"])
        
