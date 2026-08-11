import sqlite3
from typing import Optional
from repository import TaskRepository

DB_FILE = "tasks.db"


class SQLiteTaskRepository(TaskRepository):
    def __init__(self):
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT 0
            )
        """)

        cursor.execute("SELECT COUNT(*) FROM tasks")
        count = cursor.fetchone()[0]

        if count == 0:
            cursor.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                [
                    ("Buy groceries", False),
                    ("Finish assignment", False),
                    ("Read a book", True),
                ]
            )

        conn.commit()
        conn.close()

    def get_all(self) -> list[dict]:
        conn = self._get_connection()
        rows = conn.execute("SELECT * FROM tasks").fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_by_id(self, task_id: int) -> Optional[dict]:
        conn = self._get_connection()
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def create(self, title: str) -> dict:
        conn = self._get_connection()
        cursor = conn.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (title, False)
        )
        conn.commit()
        new_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (new_id,)).fetchone()
        conn.close()
        return dict(row)

    def update(self, task_id: int, title: Optional[str], done: Optional[bool]) -> Optional[dict]:
        conn = self._get_connection()
        existing = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()

        if existing is None:
            conn.close()
            return None

        new_title = title if title is not None else existing["title"]
        new_done = done if done is not None else bool(existing["done"])

        conn.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (new_title, new_done, task_id)
        )
        conn.commit()

        updated = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        conn.close()
        return dict(updated)

    def delete(self, task_id: int) -> bool:
        conn = self._get_connection()
        existing = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()

        if existing is None:
            conn.close()
            return False

        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        return True