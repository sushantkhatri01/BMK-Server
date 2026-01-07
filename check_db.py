import sqlite3
import os

# Check what's in the Access DB
print("Checking databases...")
print("OMGBMK.accdb exists:", os.path.exists(r"Z:\OMRGBMK\OMGBMK.accdb"))
print("bmk.db exists:", os.path.exists(r"Z:\OMRGBMK\bmk.db"))

# Try to read bmk.db to see structure
conn = sqlite3.connect(r"Z:\OMRGBMK\bmk.db")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in bmk.db:", tables)
conn.close()
