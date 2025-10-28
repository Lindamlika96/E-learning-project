from typing import List
from fastapi import APIRouter
from database.session import get_connection
from datetime import datetime

router = APIRouter()

@router.get("/students/at-risk")
def get_students_at_risk():
    """Retourne la liste des étudiants à risque d'abandon."""
    with get_connection() as conn:
        students = conn.execute("""
            SELECT 
                student_id,
                student_name,
                course_id,
                course_name,
                abandon_score,
                predicted_at,
                status
            FROM students_at_risk
            ORDER BY abandon_score DESC
        """).fetchall()
        
        return [
            {
                "student_id": student["student_id"],
                "student_name": student["student_name"],
                "course_id": student["course_id"],
                "course_name": student["course_name"],
                "abandon_score": student["abandon_score"],
                "predicted_at": student["predicted_at"],
                "status": student["status"]
            }
            for student in students
        ]