"""Modèle Enrollment pour gérer les inscriptions aux cours"""
from pydantic import BaseModel
from datetime import datetime

class Enrollment(BaseModel):
    id: int
    student_id: int
    course_id: int
    enrolled_at: datetime
    last_activity: datetime
    completion_percent: float
    time_spent_hours: float
    pages_viewed: int
    
    class Config:
        from_attributes = True