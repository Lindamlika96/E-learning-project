# app/api_courses.py
from fastapi import APIRouter, HTTPException, UploadFile, File
from pathlib import Path
import json
from typing import List, Any

router = APIRouter(prefix="/api/courses", tags=["courses"])
DATA_DIR = Path("data")
COURSES_FILE = DATA_DIR / "courses.json"

@router.get("/", response_model=List[Any])
def list_courses():
    if not COURSES_FILE.exists():
        return []
    with open(COURSES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@router.get("/{course_id}")
def get_course(course_id: int):
    if not COURSES_FILE.exists():
        raise HTTPException(status_code=404, detail="Aucun cours disponible")
    with open(COURSES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    for c in data:
        if c.get("id") == course_id:
            return c
    raise HTTPException(status_code=404, detail="Cours non trouvé")

@router.post("/load-json")
def load_courses_from_json(courses: List[dict]):
    """Remplace le fichier courses.json par le payload fourni (liste d'objets)."""
    DATA_DIR.mkdir(exist_ok=True)
    with open(COURSES_FILE, "w", encoding="utf-8") as f:
        json.dump(courses, f, ensure_ascii=False, indent=2)
    return {"status": "ok", "count": len(courses)}

@router.post("/upload-file")
async def upload_courses_file(file: UploadFile = File(...)):
    """Upload d'un fichier courses.json via form-data."""
    DATA_DIR.mkdir(exist_ok=True)
    content = json.loads(await file.read())
    with open(COURSES_FILE, "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    return {"status": "ok", "count": len(content)}
