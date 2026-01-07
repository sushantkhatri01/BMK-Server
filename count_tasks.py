import sqlite3

conn = sqlite3.connect(r"Z:\OMRGBMK\bmk.db")
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM tasks")
count = cursor.fetchone()[0]
print(f"Tasks in Windows bmk.db: {count}")
conn.close()
