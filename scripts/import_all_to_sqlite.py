#!/usr/bin/env python3
"""
Import des données dans SQLite.
Usage: import_all_to_sqlite.py --db data/app.db --train data/ml/train.csv --test data/ml/test.csv --courses data/courses.json
"""

import os
import json
import sqlite3
import logging
import argparse
import pandas as pd
from datetime import datetime
from app.events_db import init_db, get_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("import")

def parse_args():
    parser = argparse.ArgumentParser(description="Import données dans SQLite")
    parser.add_argument("--db", required=True, help="Chemin vers la base SQLite")
    parser.add_argument("--train", required=True, help="Chemin vers train.csv")
    parser.add_argument("--test", required=True, help="Chemin vers test.csv")
    parser.add_argument("--courses", required=True, help="Chemin vers courses.json")
    return parser.parse_args()

def import_users_from_events(db_path: str, events_df: pd.DataFrame) -> int:
    """Crée les utilisateurs à partir des événements."""
    users = events_df[["username"]].drop_duplicates()
    users["email"] = users["username"].apply(lambda x: f"user{x}@example.com")
    users["name"] = users["username"].apply(lambda x: f"User {x}")
    
    n = 0
    with get_connection(db_path) as conn:
        for _, user in users.iterrows():
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO users(id, email, name) VALUES(?,?,?)",
                    (int(user["username"]), user["email"], user["name"])
                )
                n += 1
            except sqlite3.IntegrityError as e:
                logger.warning(f"Skip user {user['username']}: {e}")
        conn.commit()
    return n

def import_courses(db_path: str, courses_path: str) -> int:
    """Importe les cours depuis le JSON."""
    if not os.path.exists(courses_path):
        logger.error(f"Fichier courses introuvable: {courses_path}")
        return 0
        
    with open(courses_path, "r", encoding="utf-8") as f:
        courses = json.load(f)
        
    n = 0
    with get_connection(db_path) as conn:
        for course in courses:
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO courses(id, title, description) VALUES(?,?,?)",
                    (
                        int(course.get("id")),
                        course.get("title", "Sans titre"),
                        course.get("description", "")
                    )
                )
                n += 1
            except sqlite3.IntegrityError as e:
                logger.warning(f"Skip course {course.get('id')}: {e}")
        conn.commit()
    return n

def import_events(db_path: str, events_df: pd.DataFrame, source: str) -> int:
    """Importe les événements depuis un DataFrame."""
    n = 0
    with get_connection(db_path) as conn:
        for _, event in events_df.iterrows():
            try:
                # Calculer le type d'événement à partir des colonnes action_*
                action_cols = [col for col in event.index if col.startswith('action_')]
                active_actions = [col.replace('action_', '') for col in action_cols if event[col] > 0]
                event_type = active_actions[0] if active_actions else "page_view"
                
                # Convertir les colonnes en types appropriés
                metadata = {
                    "source": source,
                    "session_id": str(event.get("session_id", "")),
                    "truth": int(event.get("truth", 0)),
                    "unique_session_count": int(event.get("unique_session_count", 0)),
                    "avg_nActions_per_session": float(event.get("avg_nActions_per_session", 0))
                }
                
                # Ajouter toutes les actions dans metadata
                for col in action_cols:
                    metadata[col] = int(event.get(col, 0))
                
                conn.execute("""
                    INSERT INTO events(
                        event_type, user_id, course_id, timestamp,
                        metadata, time_spent
                    ) VALUES(?,?,?,?,?,?)
                """, (
                    event_type,
                    int(event["username"]),  # username est notre user_id
                    int(event["course_id"]),
                    event.get("timestamp", datetime.now().isoformat()),
                    json.dumps(metadata),
                    int(event.get("time_difference", 0))  # time_difference comme time_spent
                ))
                n += 1
            except sqlite3.IntegrityError as e:
                logger.warning(f"Skip event user={event['username']} course={event['course_id']}: {e}")
                
        conn.commit()
    return n

def import_enrollments(db_path: str, events_df: pd.DataFrame) -> int:
    """Crée les inscriptions à partir des événements."""
    enrollments = events_df[["username", "course_id"]].drop_duplicates()
    
    n = 0
    with get_connection(db_path) as conn:
        for _, enroll in enrollments.iterrows():
            try:
                conn.execute("""
                    INSERT OR IGNORE INTO enrollments(user_id, course_id)
                    VALUES(?,?)
                """, (int(enroll["username"]), int(enroll["course_id"])))
                n += 1
            except sqlite3.IntegrityError as e:
                logger.warning(f"Skip enrollment user={enroll['username']} course={enroll['course_id']}: {e}")
        conn.commit()
    return n

def main():
    args = parse_args()
    
    # 1. Initialiser la DB
    init_db(args.db, recreate=True)
    logger.info(f"Schema initialisé: {args.db}")
    
    # 2. Charger les données
    train_df = pd.read_csv(args.train)
    test_df = pd.read_csv(args.test)
    logger.info(f"Données chargées: train={len(train_df)} test={len(test_df)} lignes")
    
    # 3. Importer dans l'ordre pour respecter les FK
    n_users = import_users_from_events(args.db, pd.concat([train_df, test_df]))
    logger.info(f"Users importés: {n_users}")
    
    n_courses = import_courses(args.db, args.courses)
    logger.info(f"Courses importés: {n_courses}")
    
    n_enrollments = import_enrollments(args.db, pd.concat([train_df, test_df]))
    logger.info(f"Enrollments créés: {n_enrollments}")
    
    n_train = import_events(args.db, train_df, "train")
    n_test = import_events(args.db, test_df, "test")
    logger.info(f"Events importés: train={n_train} test={n_test}")

if __name__ == "__main__":
    main()
