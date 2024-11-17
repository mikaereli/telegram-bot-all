import sqlite3
from typing import List, Set, Tuple
from config import DATABASE_PATH


class Database:
    def __init__(self):
        self.db_file = DATABASE_PATH
        self.init_database()
        print(f"Database initialized at {self.db_file}")

    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                group_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                group_id INTEGER,
                FOREIGN KEY (group_id) REFERENCES groups (group_id),
                UNIQUE(username, group_id)
            )
        ''')

        conn.commit()
        conn.close()

    def add_group(self, group_id: int, name: str) -> bool:
        """Добавление новой группы"""
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

    def add_members(self, group_id: int, usernames: List[str]) -> Tuple[int, List[str]]:
        """Добавление участников в группу"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        added = 0
        failed = []

        for username in usernames:
            username = username.lstrip('@')
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO members (username, group_id)
                    VALUES (?, ?)
                ''', (username, group_id))
                added += 1
            except Exception as e:
                print(f"Error adding member {username}: {e}")
                failed.append(username)

        conn.commit()
        conn.close()
        return added, failed

    def get_group_members(self, group_id: int) -> Set[str]:
        """Получение всех участников группы"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT username FROM members
            WHERE group_id = ?
        ''', (group_id,))

        members = {row[0] for row in cursor.fetchall()}
        conn.close()
        return members

    def remove_member(self, group_id: int, username: str) -> bool:
        """Удаление участника из группы"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            username = username.lstrip('@')
            cursor.execute('''
                DELETE FROM members
                WHERE group_id = ? AND username = ?
            ''', (group_id, username))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error removing member: {e}")
            return False