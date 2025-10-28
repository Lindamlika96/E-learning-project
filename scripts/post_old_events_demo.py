"""Poste un événement vieux de 15 jours vers l'API (demo)."""
# Usage: python scripts/post_old_events_demo.py

import requests
from datetime import datetime, timedelta, timezone
import os
import json

API_URL = "http://127.0.0.1:8000/api/analytics/events"

def make_old_event():
    old_date = (datetime.now(timezone.utc) - timedelta(days=15)).isoformat()
    payload = {
        "event_type": "pdf_open",
        "user_id": 1,
        "course_id": 1,
        "timestamp": old_date,
        "metadata": {"page_number": 1, "duration_seconds": 30},
    }
    return payload

def post_event(url=API_URL):
    payload = make_old_event()
    try:
        r = requests.post(url, json=payload, timeout=5)
        print("Status:", r.status_code, r.text)
    except Exception as e:
        print("Erreur HTTP:", e)

if __name__ == "__main__":
    post_event()
    print("OK")
