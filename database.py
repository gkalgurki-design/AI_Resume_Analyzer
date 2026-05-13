import sqlite3

def create_connection():
    conn = sqlite3.connect("resume_analyzer.db")
    return conn

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        predicted_role TEXT,
        ats_score INTEGER,
        skill_match INTEGER,
        detected_skills TEXT
    )
    """)

    conn.commit()
    conn.close()

def add_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (username, password)
    )

    conn.commit()
    conn.close()

def check_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = cursor.fetchone()

    conn.close()
    return user

def user_exists(username):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    )

    user = cursor.fetchone()

    conn.close()
    return user

def save_history(username, predicted_role, ats_score, skill_match, detected_skills):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO history 
    (username, predicted_role, ats_score, skill_match, detected_skills)
    VALUES (?, ?, ?, ?, ?)
    """, (username, predicted_role, ats_score, skill_match, detected_skills))

    conn.commit()
    conn.close()

def get_history(username):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT predicted_role, ats_score, skill_match, detected_skills FROM history WHERE username=?",
        (username,)
    )

    records = cursor.fetchall()

    conn.close()
    return records