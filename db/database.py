# database.py
import os
import sqlite3
from typing import Optional, List, Dict

class ReceiptDatabase:
    def __init__(self, db_name="receipts.db"):
        """
        Initialize the database connection and create tables if they don't exist 
        Parameters:
            db_name: SQLite database file name
        """
        self.db_name = db_name
        self.create_tables()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        """
        for creating the necessary tables if they don't exist
        1. receipts: for storing receipt metadata
        2. items: for storing products associated with receipts
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # receipts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_name TEXT,
                receipt_number TEXT,
                date TEXT,
                currency TEXT,
                taxes TEXT,
                total_amount TEXT,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                receipt_id INTEGER NOT NULL,
                item_name TEXT,
                quantity TEXT,
                FOREIGN KEY (receipt_id) REFERENCES receipts(id) ON DELETE CASCADE
            )
        ''')

        conn.commit()
        conn.close()
        print("Tables created successfully.")

    def save_receipt(self, data: dict, image_path: Optional[str] = None) -> int:
        """
        Save receipt and its items to the database
        
        Parameters:
            data: OCR extracted data
        
        Returns:
            receipt_id
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # 1. insert receipt metadata
            cursor.execute('''
                INSERT INTO receipts 
                (store_name, receipt_number, date, currency, taxes, total_amount, image_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('store_name'),      # might be None
                data.get('receipt_number'),  # might be None
                data.get('date'),            # might be None
                data.get('currency'),        # might be None
                data.get('taxes'),           # might be None
                data.get('total_amount'),    # might be None
                image_path
            ))

            # 2. get the inserted receipt id
            receipt_id = cursor.lastrowid

            # 3. insert items associated with the receipt if exist
            items = data.get('items', [])
            if items:
                for item in items:
                    cursor.execute('''
                        INSERT INTO items (receipt_id, item_name, quantity)
                        VALUES (?, ?, ?)
                    ''', (
                        receipt_id,
                        item.get('item_name'),
                        item.get('quantity')
                    ))

            conn.commit()
            print(f"saved with id: {receipt_id}")
            return receipt_id

        except Exception as e:
            conn.rollback()
            print(f"error in {e}")
            raise e
        finally:
            conn.close()


    def update_receipt_image(self, receipt_id: int, image_path: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE receipts SET image_path = ? WHERE id = ?",
            (image_path, receipt_id)
        )
        conn.commit()
        conn.close()

    def save_uploaded_image(self, file_bytes: bytes, receipt_id: int) -> str:
        folder = "receipt_images"
        os.makedirs(folder, exist_ok=True) 
        path = os.path.join(folder, f"receipt_{receipt_id}.png")
        with open(path, "wb") as f:
            f.write(file_bytes)
        return path
    
    def get_all_receipts(self) -> List[Dict]:
        """
        retrieve all receipts metadata
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, store_name, receipt_number, date, 
                   currency, taxes, total_amount, created_at
            FROM receipts
            ORDER BY created_at DESC
        ''')
        

        rows = cursor.fetchall()
        conn.close()

        # convert to list of dicts
        receipts = []
        for row in rows:
            receipts.append({
                'id': row[0],
                'store_name': row[1],
                'receipt_number': row[2],
                'date': row[3],
                'currency': row[4],
                'taxes': row[5],
                'total_amount': row[6],
                'created_at': row[7]
            })

        return receipts

    def get_receipt_by_id(self, receipt_id: int) -> Dict:
        """
        get receipt by id with its items        
        Parameters:
            receipt_id
        
        Returns:
            receipt data with items
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # 1.get receipt  data
        cursor.execute('''
            SELECT id, store_name, receipt_number, date,
                   currency, taxes, total_amount, created_at
            FROM receipts
            WHERE id = ?
        ''', (receipt_id,))

        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        receipt = {
            'id': row[0],
            'store_name': row[1],
            'receipt_number': row[2],
            'date': row[3],
            'currency': row[4],
            'taxes': row[5],
            'total_amount': row[6],
            'created_at': row[7],
            'items': []
        }

        # 2.get items associated with the receipt
        cursor.execute('''
            SELECT item_name, quantity
            FROM items
            WHERE receipt_id = ?
        ''', (receipt_id,))

        items = cursor.fetchall()
        receipt['items'] = [
            {'item_name': item[0], 'quantity': item[1]}
            for item in items
        ]

        conn.close()
        return receipt

    def delete_receipt(self, receipt_id: int):
        """
        delete receipt by id will also delete its items due to foreign key constraint        
        Parameters:
            receipt_id
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM receipts WHERE id = ?', (receipt_id,))

        conn.commit()
        conn.close()
        print(f"✅ deleted  {receipt_id}")

    def search_receipts(self, search_term: str) -> List[Dict]:
        """
        search receipts by store name, receipt number, or date
        
        Parameters:
            search_term: term to search for in receipts fields 
        
        Returns:
            list of matching receipts
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        search_pattern = f"%{search_term}%"

        cursor.execute('''
            SELECT id, store_name, receipt_number, date,
                   currency, taxes, total_amount, created_at
            FROM receipts
            WHERE store_name LIKE ? 
               OR receipt_number LIKE ?
               OR date LIKE ?
            ORDER BY created_at DESC
        ''', (search_pattern, search_pattern, search_pattern))

        rows = cursor.fetchall()
        conn.close()

        receipts = []
        for row in rows:
            receipts.append({
                'id': row[0],
                'store_name': row[1],
                'receipt_number': row[2],
                'date': row[3],
                'currency': row[4],
                'taxes': row[5],
                'total_amount': row[6],
                'created_at': row[7]
            })

        return receipts

    def get_statistics(self) -> Dict:
        """
        get basic statistics about receipts
        
        Returns:
            dictionary with total_receipts and total_amount
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # total receipts
        cursor.execute('SELECT COUNT(*) FROM receipts')
        total_receipts = cursor.fetchone()[0]

        #total amount
        cursor.execute('''
            SELECT SUM(CAST(total_amount AS REAL))
            FROM receipts
            WHERE total_amount IS NOT NULL 
              AND total_amount != ''
        ''')

        total_amount = cursor.fetchone()[0] or 0

        conn.close()

        return {
            'total_receipts': total_receipts,
            'total_amount': round(total_amount, 2)
        }


# #for testing purposes
# if __name__ == "__main__":
#   #intialize the database
#     db = ReceiptDatabase()

#     # save a sample receipt
#     sample_data = {
#         "store_name": "كارفور",
#         "receipt_number": "12345",
#         "date": "25/01/2026",
#         "currency": "JOD",
#         "taxes": "2.50",
#         "total_amount": "50.00",
#         "items": [
#             {"item_name": "حليب", "quantity": "2"},
#             {"item_name": "خبز", "quantity": "1"}
#         ]
#     }

#     receipt_id = db.save_receipt(sample_data)
#     print(f" saved receipt with ID: {receipt_id}")

#     # retrieve all receipts
#     all_receipts = db.get_all_receipts()
#     print(f" retrieved {len(all_receipts)} receipts")

#   #statistics
#     stats = db.get_statistics()
#     print(f"statistics: {stats}")
