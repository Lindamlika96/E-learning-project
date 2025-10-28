#!/usr/bin/env python3
"""
Agrège events depuis data/app.db -> data/ml/features.csv
Calcul des features par (user_id, course_id).
"""
import os
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(ROOT, "data")
DB_PATH = os.path.join(DATA_DIR, "app.db")
ML_DIR = os.path.join(DATA_DIR, "ml")
COURSES_JSON = os.path.join(DATA_DIR, "courses.json")
OUTPUT = os.path.join(ML_DIR, "features.csv")

os.makedirs(ML_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)


def load_courses_total_pages() -> Dict[int, int]:
    """Charge total_pages depuis courses.json si présent (fallback 10)."""
    if not os.path.exists(COURSES_JSON):
        return {}
    with open(COURSES_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {int(c["course_id"]): int(c.get("total_pages", 10)) for c in data}


def aggregate_events(db_path: str, output_csv: str) -> None:
    """Lit events depuis SQLite et produit features.csv."""
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM events", conn)
    conn.close()

    if df.empty:
        print("Aucun événement trouvé dans events -> sortie.")
        # write empty CSV with headers
        pd.DataFrame(
            columns=[
                "user_id",
                "course_id",
                "percent_complete",
                "time_spent_hours",
                "pages_viewed",
                "num_sessions_last7",
                "annotations_count",
                "days_since_last_activity",
            ]
        ).to_csv(output_csv, index=False)
        return

    # Parser timestamp en UTC et metadata JSON
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df["metadata"] = df["metadata"].apply(lambda x: json.loads(x) if isinstance(x, str) else (x or {}))

    courses_pages = load_courses_total_pages()
    now_utc = datetime.now(timezone.utc)
    features = []

    # grouper par user_id & course_id
    grouped = df.groupby(["user_id", "course_id"])
    for (user_id, course_id), group in grouped:
        # pages_viewed : compter items metadata contenant page_number
        pages_viewed = sum(1 for md in group["metadata"] if isinstance(md, dict) and md.get("page_number") is not None)
        # time_spent_hours : somme duration_seconds s'il y en a, sinon heuristique 0.25h par event
        duration_sum = sum((md.get("duration_seconds", 0) for md in group["metadata"] if isinstance(md, dict)))
        time_spent_hours = duration_sum / 3600.0 if duration_sum else len(group) * 0.25
        # last activity
        last_ts = group["timestamp"].max()
        days_since_last_activity = int((now_utc - last_ts).days) if pd.notnull(last_ts) else 0
        # sessions last 7 days
        last_7d = now_utc - timedelta(days=7)
        num_sessions_last7 = int(sum(1 for ts in group["timestamp"] if pd.notnull(ts) and ts >= last_7d))
        total_pages = courses_pages.get(int(course_id) if course_id is not None else 0, 10)
        percent_complete = min((pages_viewed / total_pages) * 100.0, 100.0) if total_pages > 0 else 0.0

        features.append(
            {
                "user_id": int(user_id) if user_id is not None else 0,
                "course_id": int(course_id) if course_id is not None else 0,
                "percent_complete": round(percent_complete, 2),
                "time_spent_hours": round(time_spent_hours, 3),
                "pages_viewed": int(pages_viewed),
                "num_sessions_last7": int(num_sessions_last7),
                "annotations_count": 0,
                "days_since_last_activity": int(days_since_last_activity),
            }
        )

    df_out = pd.DataFrame(features)
    df_out.to_csv(output_csv, index=False)
    print(f"Features agrégées dans {output_csv}")


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(ML_DIR, exist_ok=True)
    aggregate_events(DB_PATH, OUTPUT)
    print("OK")
