import sqlite3
import hashlib

def hash_password(password):
    """Hashes the password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def db_connect():
    """Creates a connection to the SQLite database."""
    return sqlite3.connect('training_data.db')

def create_tables():
    """Creates the necessary tables if they don't exist."""
    conn = db_connect()
    cursor = conn.cursor()
    # Tabela de usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    # Tabela de treinos (exemplo)
    # Cada registro de treino terá um user_id para vincular ao usuário
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            exercise TEXT NOT NULL,
            weight REAL NOT NULL,
            reps INTEGER NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, password):
    """Adds a new user to the database."""
    conn = db_connect()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                       (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError: # Ocorre se o username já existir
        return False
    finally:
        conn.close()

def check_user(username, password):
    """Checks if a user exists and the password is correct."""
    conn = db_connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    user_record = cursor.fetchone()
    conn.close()
    if user_record and user_record[1] == hash_password(password):
        return user_record[0] # Retorna o user_id
    return None

def save_workout(user_id, exercise, weight, reps, date):
    """Saves a new workout for a specific user."""
    conn = db_connect()
    cursor = conn.cursor()
    # A tabela 'workouts' agora espera user_id, exercise, weight, reps, date
    cursor.execute(
        "INSERT INTO workouts (user_id, exercise, weight, reps, date) VALUES (?, ?, ?, ?, ?)",
        (user_id, exercise, weight, reps, str(date)) # Garante que a data seja salva como texto
    )
    conn.commit()
    conn.close()

def load_workouts(user_id):
    """Loads all workouts for a specific user from the database."""
    import pandas as pd
    conn = db_connect()
    # Seleciona apenas os treinos do usuário logado
    query = "SELECT exercise, weight, reps, date FROM workouts WHERE user_id = ? ORDER BY date DESC, id DESC"
    # O pd.read_sql_query é uma forma eficiente de carregar dados em um DataFrame
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return df