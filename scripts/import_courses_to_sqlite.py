"""Importe data/courses.json dans une table SQLite 'courses'."""
# Usage: python scripts/import_courses_to_sqlite.py

import os
import json
import sqlite3
import logging
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = os.path.join("data", "app.db")
COURSES_JSON = os.path.join("data", "courses.json")


def ensure_db_dir():
    """Crée le dossier data si nécessaire."""
    os.makedirs("data", exist_ok=True)


def import_courses(json_path: str = COURSES_JSON, db_path: str = DB_PATH) -> None:
    """Lit courses.json et les insère dans la table courses (créée si absente)."""
    ensure_db_dir()
    if not os.path.exists(json_path):
        logger.error("Fichier courses.json introuvable: %s", json_path)
        return

    with open(json_path, "r", encoding="utf-8") as f:
        courses = json.load(f)

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS courses (
                course_id INTEGER PRIMARY KEY,
                title TEXT,
                category TEXT,
                level TEXT,
                tutor TEXT,
                total_pages INTEGER,
                description TEXT,
                file_path TEXT
            )"""
        )
        # Insert or replace
        for c in courses:
            cur.execute(
                "INSERT OR REPLACE INTO courses VALUES (?,?,?,?,?,?,?,?)",
                (
                    c.get("course_id"),
                    c.get("title"),
                    c.get("category"),
                    c.get("level"),
                    c.get("tutor"),
                    c.get("total_pages"),
                    c.get("description"),
                    c.get("file_path"),
                ),
            )
        conn.commit()
    logger.info("Import courses.json -> %s OK", db_path)


if __name__ == "__main__":
    import_courses()
    print("OK")
