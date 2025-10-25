# app/api_events.py
from fastapi import APIRouter
from pydantic import BaseModel
from pathlib import Path
import json
from datetime import datetime

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

DATA_DIR = Path("data")
EVENTS_FILE = DATA_DIR / "events.jsonl"

class Event(BaseModel):
    user_id: int
    course_id: int
    event_type: str           # ex: "page_view" | "time_spent" | "quiz_submit"...
    value: float | int | str | None = None
    ts: str | None = None     # ISO datetime

@router.post("/events")
def post_events(events: list[Event]):
    DATA_DIR.mkdir(exist_ok=True)
    EVENTS_FILE.touch(exist_ok=True)
    with open(EVENTS_FILE, "a", encoding="utf-8") as f:
        for ev in events:
            data = ev.dict()
            data["ts"] = data["ts"] or datetime.utcnow().isoformat()
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
    return {"status": "ok", "count": len(events)}
