# app/courses_api.py
import os, sqlite3
from fastapi import APIRouter, HTTPException
from typing import List
from models.course import Course

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "app.db")
router = APIRouter(prefix="/courses", tags=["courses"])

def get_conn():
    try:
        if not os.path.exists(DB_PATH):
            raise HTTPException(status_code=500, detail="Database file not found")
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

@router.get("", response_model=List[Course])
def list_courses():
    try:
        with get_conn() as conn:
            cur = conn.execute("""
                SELECT 
                    course_id, title, category, level, tutor, total_pages,
                    COALESCE(description, '') as description,
                    COALESCE(file_path, '') as file_path
                FROM courses 
                ORDER BY course_id
            """)
            courses = [dict(r) for r in cur.fetchall()]
            return [Course.model_validate(course) for course in courses]
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing courses: {str(e)}")

@router.get("/{course_id}", response_model=Course)
def get_course(course_id: int):
    try:
        with get_conn() as conn:
            cur = conn.execute("""
                SELECT 
                    course_id, title, category, level, tutor, total_pages,
                    COALESCE(description, '') as description,
                    COALESCE(file_path, '') as file_path
                FROM courses 
                WHERE course_id=?
            """, (course_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail=f"Course {course_id} not found")
            return Course.model_validate(dict(row))
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database query error: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid course data: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing course: {str(e)}")
