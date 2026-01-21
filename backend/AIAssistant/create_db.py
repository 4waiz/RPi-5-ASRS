import sqlite3

# Connect (or create if not exists) database file
conn = sqlite3.connect("factory_parts.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    object TEXT NOT NULL,
    quantity INTEGER NOT NULL
)
""")

# Insert dummy data
data = [
    ("red body", 10),
    ("blue body", 15),
    ("green body", 8),
    ("drilled chassis", 5),
    ("chassis", 12),
    ("wheels", 40)
]

cursor.executemany("INSERT INTO inventory (object, quantity) VALUES (?, ?)", data)

conn.commit()
conn.close()

print("✅ Database created and filled with dummy data.")
