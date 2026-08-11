import os
import psycopg2
import psycopg2.extras
from typing import Optional
from dotenv import load_dotenv
from repository import TaskRepository

load_dotenv()  # reads variables from .env into the environment

DATABASE_URL = os.getenv("DATABASE_URL")


class PostgresTaskRepository(TaskRepository):
    def __init__(self):
        self._init_db()

    def _get_connection(self):
        conn = psycopg2.connect(DATABASE_URL)
        return conn

    def _init_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT FALSE
            )
        """)

        cursor.execute("SELECT COUNT(*) FROM tasks")
        count = cursor.fetchone()[0]

        if count == 0:
            cursor.executemany(
                "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                [
                    ("Buy groceries", False),
                    ("Finish assignment", False),
                    ("Read a book", True),
                ]
            )

        conn.commit()
        cursor.close()
        conn.close()

    def get_all(self) -> list[dict]:
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM tasks ORDER BY id")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [dict(row) for row in rows]

    def get_by_id(self, task_id: int) -> Optional[dict]:
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return dict(row) if row else None

    def create(self, title: str) -> dict:
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *",
            (title, False)
        )
        new_row = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        return dict(new_row)

    def update(self, task_id: int, title: Optional[str], done: Optional[bool]) -> Optional[dict]:
        conn = self._get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
        existing = cursor.fetchone()

        if existing is None:
            cursor.close()
            conn.close()
            return None

        new_title = title if title is not None else existing["title"]
        new_done = done if done is not None else existing["done"]

        cursor.execute(
            "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING *",
            (new_title, new_done, task_id)
        )
        updated = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        return dict(updated)

    def delete(self, task_id: int) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
        existing = cursor.fetchone()

        if existing is None:
            cursor.close()
            conn.close()
            return False

        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return True