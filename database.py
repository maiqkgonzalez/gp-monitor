import sqlite3
import logging

def create_table():
    """Creates the records table."""
    with sqlite3.connect("users_gp.db") as conn:
        cursor = conn.cursor()
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            users INTEGER,
            firewall TEXT NOT NULL,
            gateway TEXT,
            status TEXT NOT NULL
        );
        '''
        cursor.execute(create_table_query)
        conn.commit()

def insert_batch_records(records_list: list):
    """Inserts all records from the firewall list into the DB using a single connection."""
    try:
        with sqlite3.connect("users_gp.db") as conn:
            cursor = conn.cursor()
            insert_query = '''
            INSERT INTO records (firewall, gateway, users, timestamp, status)
            VALUES (?, ?, ?, ?, ?);
            '''
            
            # Prepare a list of tuples for executemany
            values = [
                (r['firewall'], r['gateway'], r['users'], r['timestamp'], r['status']) 
                for r in records_list
            ]
            
            cursor.executemany(insert_query, values)
            conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")

if __name__ == "__main__":
    create_table()
    print("DB created")