import sqlite3

conn = sqlite3.connect("receipts.db")
cur = conn.cursor()

cur.execute("DELETE FROM receipts  WHERE ID IN (18 ,19 ,20 ,21 ,22 ,23 ,24 ,25);")

conn.commit()

conn.close()
