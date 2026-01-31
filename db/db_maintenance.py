import sqlite3

conn = sqlite3.connect("receipts.db")
cur = conn.cursor()

cur.execute("")

conn.commit()

conn.close()
