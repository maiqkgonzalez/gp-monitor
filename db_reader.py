import sqlite3
from contextlib import contextmanager
import logging

db_name = "users_gp.db"


@contextmanager
def get_db_connection():
    """Returns DB connection"""
    conn = sqlite3.connect(db_name)

    try:
        yield conn
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"Data base error: {e}")
        raise
    finally:
        conn.close()


def get_max_users_per_firewall(
    firewall_list: list, start_date: str, end_date: str
) -> list:
    """
    Returns a list of tuples with each firewall and its maximum number of
    connected users within the given date range.

    Example: [('firewall_1', 100), ('firewall_2', 77)]
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Format dynamic placeholders for the 'WHERE firewall IN ....' clause
        placeholders = ",".join("?" * len(firewall_list))

        query = f"""
        SELECT firewall, MAX(users)
        FROM records
        WHERE firewall IN ({placeholders})
        AND status = ?
        AND timestamp BETWEEN ? AND ?
        GROUP BY firewall;
        """

        # Concatenete lists to pass a single list to 'execute'
        query_values = firewall_list + ["connected", start_date, end_date]

        cursor.execute(query, query_values)

        return cursor.fetchall()


def get_users_overtime(firewall_list: list, start_date: str, end_date: str) -> list:
    """
    Returns the records fon the given firewall list and date range.

    Example: [('2026-03-24 11:57:04', 'firewall_peru', 0), ('2026-03-24 11:57:07', 'firewall_arg', 28), ('2026-03-24 11:57:08', 'firewall_esp', 54)]
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Format dynamic placeholders for the 'WHERE firewall IN ...' clause
        placeholders = ",".join("?" * len(firewall_list))

        query = f"""
        SELECT timestamp, firewall, users
        FROM records
        WHERE firewall in ({placeholders}) 
        AND status = ?
        AND timestamp BETWEEN ? AND ?
        ORDER BY timestamp;
        """

        # Concatenete lists to pass a single list to 'execute'
        query_values = firewall_list + ["connected", start_date, end_date]

        cursor.execute(query, query_values)

        return cursor.fetchall()


# def get_users_overtime_byday(firewall_name, days)

if __name__ == "__main__":
    print(
        get_max_users_per_firewall(
            firewall_list=["firewall_esp", "firewall_arg", "firewall_peru"],
            start_date="2026-03-24 11:56:49",
            end_date="2026-03-25 16:06:19",
        )
    )
    print(" ")
    print(
        get_users_overtime(
            firewall_list=["firewall_arg", "firewall_esp", "firewall_peru"],
            start_date="2026-03-24 11:56:49",
            end_date="2026-03-25 16:06:19",
        )
    )
