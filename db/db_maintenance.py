import sqlite3

conn = sqlite3.connect("receipts.db")
cur = conn.cursor()

cur.execute("DELETE FROM receipts  WHERE ID IN (28 ,29);")

conn.commit()

conn.close()
