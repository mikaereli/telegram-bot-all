import sqlite3
from typing import List, Set, Tuple
from config import DATABASE_PATH


class Database:
    def __init__(self):
        self.db_file = DATABASE_PATH
        self.init_database()
        print(f"Database initialized at {self.db_file}")

    def init_database(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                group_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_members (
                user_id INTEGER NOT NULL,
                group_id INTEGER NOT NULL,
                username TEXT,
                first_name TEXT,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES groups (group_id),
                PRIMARY KEY (user_id, group_id)
            )
        ''')

        conn.commit()
        conn.close()

    def add_group(self, group_id: int, name: str) -> bool:
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO groups (group_id, name)
                VALUES (?, ?)
            ''', (group_id, name))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding group: {e}")
            return False

    def register_user(self, group_id: int, user_id: int, username: str, first_name: str):
        """Register or update a user in a group"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO group_members (user_id, group_id, username, first_name, last_seen)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, group_id, username, first_name))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error registering user {user_id}: {e}")

    def get_group_users(self, group_id: int) -> List[dict]:
        """Get all users for a group"""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row  
        cursor = conn.cursor()

        cursor.execute('''
            SELECT user_id, username, first_name FROM group_members
            WHERE group_id = ?
        ''', (group_id,))

        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users

    # Legacy methods below might be removed or updated if needed
    def remove_member(self, group_id: int, user_id: int) -> bool:
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            cursor.execute('''
                DELETE FROM group_members
                WHERE group_id = ? AND user_id = ?
            ''', (group_id, user_id))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error removing member: {e}")
            return False