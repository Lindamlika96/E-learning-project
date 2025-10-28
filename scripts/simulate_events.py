"""Simule l'envoi d'événements depuis data/events.json vers l'API."""
# Usage: python scripts/simulate_events.py --url http://127.0.0.1:8000/api/analytics/events

import os
import json
import argparse
import time
import requests

EVENTS_JSON = os.path.join("data", "events.json")

def load_events(path=EVENTS_JSON):
    if not os.path.exists(path):
        print("events.json introuvable:", path)
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def simulate(url: str, delay: float = 0.1):
    events = load_events()
    for e in events:
        try:
            r = requests.post(url, json=e, timeout=5)
            print("POST", r.status_code, e.get("event_type"))
        except Exception as ex:
            print("Erreur:", ex)
        time.sleep(delay)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--url", default="http://127.0.0.1:8000/api/analytics/events")
    p.add_argument("--delay", type=float, default=0.05)
    args = p.parse_args()
    simulate(args.url, args.delay)
    print("OK")
