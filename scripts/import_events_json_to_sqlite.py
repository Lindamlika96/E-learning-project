"""Importe data/events.json dans la table 'events' du app.db."""
# Usage: python scripts/import_events_json_to_sqlite.py

import os
import json
import sqlite3
import logging
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = os.path.join("data", "app.db")
EVENTS_JSON = os.path.join("data", "events.json")


def ensure_db_dir():
    """Crée le dossier data si nécessaire."""
    os.makedirs("data", exist_ok=True)


def import_events(json_path: str = EVENTS_JSON, db_path: str = DB_PATH) -> None:
    """Lit events.json et insère les événements dans events table."""
    ensure_db_dir()
    if not os.path.exists(json_path):
        logger.error("Fichier events.json introuvable: %s", json_path)
        return

    with open(json_path, "r", encoding="utf-8") as f:
        events = json.load(f)

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                user_id INTEGER,
                course_id INTEGER,
                timestamp TEXT,
                metadata TEXT
            )"""
        )
        for e in events:
            cur.execute(
                "INSERT INTO events (event_type, user_id, course_id, timestamp, metadata) VALUES (?,?,?,?,?)",
                (
                    e.get("event_type"),
                    e.get("user_id"),
                    e.get("course_id"),
                    e.get("timestamp"),
                    json.dumps(e.get("metadata", {})),
                ),
            )
        conn.commit()
    logger.info("Import events.json -> %s OK", db_path)


if __name__ == "__main__":
    import_events()
    print("OK")
