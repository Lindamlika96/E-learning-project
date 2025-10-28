"""Migre un fichier JSONL d'événements (data/events.jsonl) vers app.db/events."""
# Usage: python scripts/migrate_events_jsonl_to_sqlite.py --jsonl data/events.jsonl

import os
import json
import sqlite3
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = os.path.join("data", "app.db")


def ensure_db_dir():
    os.makedirs("data", exist_ok=True)


def migrate(jsonl_path: str, db_path: str = DB_PATH) -> None:
    """Lit un JSONL et insère chaque objet dans la table events."""
    ensure_db_dir()
    if not os.path.exists(jsonl_path):
        logger.error("Fichier JSONL introuvable: %s", jsonl_path)
        return

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
        inserted = 0
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    logger.warning("Ligne JSON invalide - skip")
                    continue
                cur.execute(
                    "INSERT INTO events (event_type, user_id, course_id, timestamp, metadata) VALUES (?,?,?,?,?)",
                    (
                        obj.get("event_type"),
                        obj.get("user_id"),
                        obj.get("course_id"),
                        obj.get("timestamp"),
                        json.dumps(obj.get("metadata", {})),
                    ),
                )
                inserted += 1
        conn.commit()
    logger.info("Migré %d événements -> %s", inserted, db_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--jsonl", default=os.path.join("data", "events.jsonl"), help="Chemin fichier JSONL")
    args = parser.parse_args()
    migrate(args.jsonl)
    print("OK")
