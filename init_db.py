import sqlite3

conn = sqlite3.connect("database.db")

conn.execute("""
CREATE TABLE applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    job_title TEXT NOT NULL,
    job_link TEXT,
    location TEXT, 
    applied_date TEXT,
    status TEXT,
    notes TEXT
)
""")

conn.commit()
conn.close()

print("Database initialized.")
