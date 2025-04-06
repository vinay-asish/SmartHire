import sqlite3

# === DB Setup ===
DB_PATH = "recruitment.db"

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# === Create candidates table ===
c.execute("""
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    cv_path TEXT,
    parsed_data TEXT,
    match_score REAL,
    reasoning TEXT,
    jd_id INTEGER
)
""")

conn.commit()
conn.close()

print("✅ Candidates table created successfully.")
