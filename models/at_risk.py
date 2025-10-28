from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class StudentAtRisk(SQLModel, table=True):
    __tablename__ = "students_at_risk"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(index=True)
    student_name: str
    course_id: int = Field(index=True)  # Hash du course_id EDX
    course_name: str
    abandon_score: float = Field(index=True)
    predicted_at: datetime
    status: str  # "À surveiller" ou "Critique"
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "student_id": 1,
                "student_name": "Dorsaf Riahi",
                "course_id": 12345,
                "course_name": "Introduction à FastAPI",
                "abandon_score": 0.72,
                "predicted_at": "2025-10-27T14:01:00",
                "status": "À surveiller"
            }
        }
    }