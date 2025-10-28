"""Routes et utilitaires pour ingestion d'événements (events)."""

import json
import sqlite3
import os
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, Any, List
from datetime import datetime
import logging
from database.session import get_connection, init_db

router = APIRouter(prefix="/events", tags=["events"])
logger = logging.getLogger(__name__)


class EventIn(BaseModel):
    event_type: str
    user_id: int = Field(default=1)  # Utilisateur par défaut
    course_id: int
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Event(EventIn):
    id: int

@router.post("", status_code=201, response_model=Dict[str, Any])
def post_event(event: EventIn):
    """Insère un événement dans la table events."""
    try:
        with get_connection() as conn:
            cur = conn.execute(
                """INSERT INTO events 
                   (event_type, user_id, course_id, timestamp, metadata)
                   VALUES (?, ?, ?, ?, ?)""",
                (event.event_type,
                 event.user_id,
                 event.course_id,
                 event.timestamp.isoformat(),
                 json.dumps(event.metadata))
            )
            conn.commit()
            return {"status": "created", "id": cur.lastrowid}
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erreur d'intégrité: {str(e)}"
        )
    except Exception as e:
        logger.exception("Erreur insertion événement")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne lors de l'insertion: {str(e)}"
        )

@router.get("", response_model=List[Event])
def list_events(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: int = Query(1),  # Utilisateur par défaut
    course_id: int = None
):
    """Liste les événements avec pagination."""
    try:
        query = """SELECT id, event_type, user_id, course_id, timestamp, metadata
                  FROM events WHERE user_id = ?"""
        params = [user_id]
        
        if course_id is not None:
            query += " AND course_id = ?"
            params.append(course_id)
            
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with get_connection() as conn:
            cur = conn.execute(query, params)
            events = cur.fetchall()
            return [
                Event(
                    id=e["id"],
                    event_type=e["event_type"],
                    user_id=e["user_id"],
                    course_id=e["course_id"],
                    timestamp=datetime.fromisoformat(e["timestamp"]),
                    metadata=json.loads(e["metadata"])
                )
                for e in events
            ]
    except Exception as e:
        logger.exception("Erreur lecture événements")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la lecture des événements: {str(e)}"
        )


@router.post("/analytics/events", status_code=201)
def post_event(event: EventIn):
    """Insère un événement dans la table events."""
    try:
        with get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO events (event_type, user_id, course_id, timestamp, metadata) VALUES (?,?,?,?,?)",
                (
                    event.event_type,
                    event.user_id,
                    event.course_id,
                    event.timestamp.isoformat(),
                    json.dumps(event.metadata, ensure_ascii=False),
                ),
            )
            conn.commit()
            inserted_id = cur.lastrowid
        logger.info("Événement inséré ID=%s type=%s", inserted_id, event.event_type)
        return {"status": "created", "id": inserted_id}
    except Exception as e:
        logger.exception("Erreur insertion événement")
        raise HTTPException(status_code=500, detail="Erreur interne lors de l'insertion")


if __name__ == "__main__":
    import sys
    db_path = sys.argv[1] if len(sys.argv) > 1 else "data/app.db"
    recreate = "--recreate" in sys.argv
    init_db(db_path, recreate)
    print(f"OK - Database initialisée: {db_path} (recreate={recreate})")
