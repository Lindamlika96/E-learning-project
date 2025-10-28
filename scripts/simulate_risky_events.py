"""
Génère des événements à risque pour tester le système de notification.
"""
import os
import json
from datetime import datetime, timedelta
import random

# Configuration
N_EVENTS = 10  # Nombre d'événements à générer
USER_ID = 1    # ID utilisateur par défaut
COURSE_ID = 1  # ID cours par défaut

# Chemins
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DB_PATH = os.path.join(DATA_DIR, "app.db")

def generate_risky_event():
    """Génère un événement avec des métriques à risque."""
    now = datetime.now()
    
    # Générer un timestamp dans les dernières 24h
    event_time = now - timedelta(
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )
    
    # Métriques indiquant un risque:
    # - Temps passé très court
    # - Peu de pages vues
    event = {
        "event_type": "page_view",
        "user_id": USER_ID,
        "course_id": COURSE_ID,
        "timestamp": event_time.isoformat(),
        "metadata": json.dumps({
            "url": f"/course/{COURSE_ID}/page/{random.randint(1,3)}"
        }),
        "time_spent": random.randint(10, 60),  # 10-60 secondes
        "page_number": random.randint(1, 3)     # Premières pages seulement
    }
    return event

def main():
    """Génère et insère les événements dans la base."""
    import sqlite3
    
    # Connexion BD
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Vérifier/créer utilisateur si besoin
    cur.execute("""
        INSERT OR IGNORE INTO users (id, email, name)
        VALUES (?, ?, ?)
    """, (USER_ID, "dorsariahi6@gmail.com", "Test User"))
    
    # Vérifier/créer cours si besoin
    cur.execute("""
        INSERT OR IGNORE INTO courses (id, title, description)
        VALUES (?, ?, ?)
    """, (COURSE_ID, "Cours Test", "Cours pour test notifications"))
    
    # Vérifier/créer inscription si besoin
    cur.execute("""
        INSERT OR IGNORE INTO enrollments (user_id, course_id)
        VALUES (?, ?)
    """, (USER_ID, COURSE_ID))
    
    # Générer et insérer les événements
    for _ in range(N_EVENTS):
        event = generate_risky_event()
        cur.execute("""
            INSERT INTO events (
                event_type, user_id, course_id, timestamp,
                metadata, time_spent, page_number
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event["event_type"],
            event["user_id"],
            event["course_id"],
            event["timestamp"],
            event["metadata"],
            event["time_spent"],
            event["page_number"]
        ))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
    print(f"{N_EVENTS} événements à risque générés avec succès!")