import os
import sqlite3
from typing import Optional, Dict


class ReceiptDatabase:
    def __init__(self, db_name="receipts.db"):
        self.db_name = db_name
        self.create_tables()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    # =========================
    # CREATE TABLES
    # =========================
    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # USERS TABLE
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # RECEIPTS TABLE (user_id)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            store_name TEXT,
            receipt_number TEXT,
            date TEXT,
            currency TEXT,
            taxes TEXT,
            total_amount TEXT,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)

        # Backward-compatible migration for older databases that already have
        # a receipts table without the user_id column.
        cursor.execute("PRAGMA table_info(receipts)")
        receipt_columns = {row[1] for row in cursor.fetchall()}
        if "user_id" not in receipt_columns:
            cursor.execute("ALTER TABLE receipts ADD COLUMN user_id INTEGER")

        # ITEMS TABLE
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            receipt_id INTEGER NOT NULL,
            item_name TEXT,
            quantity TEXT,
            FOREIGN KEY (receipt_id) REFERENCES receipts(id) ON DELETE CASCADE
        )
        """)

        conn.commit()
        conn.close()

    # =========================
    # SAVE RECEIPT
    # =========================
    def save_receipt(self, user_id: int, data: dict, image_path: Optional[str] = None) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # insert receipt
            cursor.execute("""
            INSERT INTO receipts (
                user_id,
                store_name,
                receipt_number,
                date,
                currency,
                taxes,
                total_amount,
                image_path
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                data.get('store_name'),
                data.get('receipt_number'),
                data.get('date'),
                data.get('currency'),
                data.get('taxes'),
                data.get('total_amount'),
                image_path
            ))

            receipt_id = cursor.lastrowid

            # insert items
            items = data.get('items', [])
            for item in items:
                cursor.execute("""
                INSERT INTO items (receipt_id, item_name, quantity)
                VALUES (?, ?, ?)
                """, (
                    receipt_id,
                    item.get('item_name'),
                    item.get('quantity')
                ))

            conn.commit()
            return receipt_id

        except Exception as e:
            conn.rollback()
            raise e

        finally:
            conn.close()

    # =========================
    # GET RECEIPT (SECURE)
    # =========================
    def get_receipt_by_id(self, receipt_id: int, user_id: int) -> Dict:
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT id, store_name, receipt_number, date,
               currency, taxes, total_amount, created_at
        FROM receipts
        WHERE id = ? AND user_id = ?
        """, (receipt_id, user_id))

        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        receipt = {
            "id": row[0],
            "store_name": row[1],
            "receipt_number": row[2],
            "date": row[3],
            "currency": row[4],
            "taxes": row[5],
            "total_amount": row[6],
            "created_at": row[7],
            "items": []
        }

        # get items
        cursor.execute("""
        SELECT item_name, quantity
        FROM items
        WHERE receipt_id = ?
        """, (receipt_id,))

        items = cursor.fetchall()

        receipt["items"] = [
            {"item_name": i[0], "quantity": i[1]}
            for i in items
        ]

        conn.close()
        return receipt

    # =========================
    # IMAGE STORAGE
    # =========================
    def save_uploaded_image(self, file_bytes: bytes, receipt_id: int) -> str:
        folder = "receipt_images"
        os.makedirs(folder, exist_ok=True)

        path = os.path.join(folder, f"receipt_{receipt_id}.png")

        with open(path, "wb") as f:
            f.write(file_bytes)

        return path

    def update_receipt_image(self, receipt_id: int, image_path: str, user_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE receipts
        SET image_path = ?
        WHERE id = ? AND user_id = ?
        """, (image_path, receipt_id, user_id))

        conn.commit()
        conn.close()


    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
