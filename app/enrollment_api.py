# app/enrollments_api.py
import os, sqlite3
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "app.db")
router = APIRouter()

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

class EnrollmentIn(BaseModel):
    user_id: int
    course_id: str

@router.post("/enrollments")
def create_enrollment(payload: EnrollmentIn):
    with get_conn() as conn:
        # vérifier existence user/course
        u = conn.execute("SELECT 1 FROM users WHERE id=?", (payload.user_id,)).fetchone()
        c = conn.execute("SELECT 1 FROM courses WHERE course_id=?", (payload.course_id,)).fetchone()
        if not u or not c:
            raise HTTPException(status_code=400, detail="user_id ou course_id inexistant")
        try:
            conn.execute(
                "INSERT OR IGNORE INTO enrollments(user_id, course_id, enrolled_at) VALUES(?,?,?)",
                (payload.user_id, payload.course_id, datetime.now(timezone.utc).isoformat())
            )
            conn.commit()
        except sqlite3.IntegrityError as e:
            raise HTTPException(status_code=400, detail=str(e))
    return {"status": "ok"}

@router.get("/enrollments")
def list_enrollments(user_id: Optional[int] = None):
    q = """
        SELECT 
            e.id, 
            e.user_id, 
            e.course_id, 
            e.enrolled_at,
            c.title as course_title,
            COALESCE(
                (SELECT COUNT(*) FROM events 
                WHERE enrollment_id = e.id AND event_type = 'page_view'), 
                0
            ) as pages_viewed,
            COALESCE(
                (SELECT MAX(timestamp) FROM events 
                WHERE enrollment_id = e.id), 
                e.enrolled_at
            ) as last_activity
        FROM enrollments e
        JOIN courses c ON e.course_id = c.course_id
    """
    args: List = []
    if user_id is not None:
        q += " WHERE e.user_id=?"
        args.append(user_id)
    q += " ORDER BY e.id DESC"
    with get_conn() as conn:
        rows = conn.execute(q, tuple(args)).fetchall()
        return [dict(r) for r in rows]

@router.post("/enrollments/{enrollment_id}/events")
def track_event(enrollment_id: int, event_type: str, metadata: dict):
    """Enregistre un événement d'interaction et met à jour les statistiques"""
    with get_conn() as conn:
        # Vérifier que l'inscription existe
        enroll = conn.execute(
            "SELECT 1 FROM enrollments WHERE id=?", 
            (enrollment_id,)
        ).fetchone()
        if not enroll:
            raise HTTPException(status_code=404, detail="Inscription non trouvée")
        
        # Enregistrer l'événement
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """
            INSERT INTO events (enrollment_id, event_type, timestamp, metadata)
            VALUES (?, ?, ?, ?)
            """,
            (enrollment_id, event_type, now, str(metadata))
        )
        
        # Mettre à jour les statistiques d'inscription
        conn.execute(
            "UPDATE enrollments SET last_activity = ? WHERE id = ?",
            (now, enrollment_id)
        )
        
        conn.commit()
        return {"status": "success", "message": "Événement enregistré"}
