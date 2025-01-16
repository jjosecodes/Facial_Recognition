import sqlite3

# database connection
conn = sqlite3.connect('database/attendance.db')
cursor = conn.cursor()

# Create a table for attendance logs
cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
''')
conn.commit()
conn.close()
