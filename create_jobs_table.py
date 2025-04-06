import sqlite3
import pandas as pd

# === Paths ===
DB_PATH = "recruitment.db"
JD_CSV_PATH = "jd_summary_output.csv"  # Path to the CSV file you generated earlier

# === Load JD summaries ===
df = pd.read_csv(JD_CSV_PATH)

if "JD Summary" not in df.columns:
    raise Exception("JD Summary column not found in CSV.")

# === Setup DB connection ===
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# === Create jobs table ===
c.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    summary TEXT
)
""")

# === Insert JD summaries into DB ===
for _, row in df.iterrows():
    c.execute("INSERT INTO jobs (title, summary) VALUES (?, ?)", (row["Job Title"], row["JD Summary"]))

conn.commit()
conn.close()

print("✅ Jobs table created and populated successfully.")
