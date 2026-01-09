import sqlite3
import pandas as pd

# --- DATABASE CONFIGURATION ---
DB_FILE = "training_log.db"

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    # This allows us to access columns by name
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database and creates the 'workouts' table if it doesn't exist."""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercicio TEXT NOT NULL,
            serie INTEGER,
            repeticoes INTEGER,
            carga TEXT,
            data_registro TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_workout(exercicio, serie, repeticoes, carga, data):
    """Saves a single workout entry into the database."""
    conn = get_db_connection()
    conn.execute("INSERT INTO workouts (exercicio, serie, repeticoes, carga, data_registro) VALUES (?, ?, ?, ?, ?)",
              (exercicio, serie, repeticoes, carga, data))
    conn.commit()
    conn.close()

def load_workouts():
    """Loads all workout entries from the database into a pandas DataFrame."""
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT exercicio, serie, repeticoes, carga, data_registro FROM workouts ORDER BY data_registro", conn)
    conn.close()
    return df
