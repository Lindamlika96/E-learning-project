"""Modèle Course pour structure logique"""
from pydantic import BaseModel

class Course(BaseModel):
    course_id: int
    title: str
    category: str
    level: str
    tutor: str
    total_pages: int
    description: str
    file_path: str
