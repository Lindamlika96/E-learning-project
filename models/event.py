"""Modèle Event pour structure logique"""
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

class Event(BaseModel):
    event_type: str
    user_id: int
    course_id: int
    timestamp: datetime
    metadata: Dict[str, Any]
