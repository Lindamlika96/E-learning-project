"""Routes FastAPI pour CRUD des événements avec nouveaux champs."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.db import get_db
from models.event import Event  # modèle ORM
from models.schemas import EventCreate, EventUpdate, EventOut  # schémas IO

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=EventOut, status_code=status.HTTP_201_CREATED)
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    """Crée un événement avec validation Pydantic."""
    # Les champs (titre, localisation, etc.) sont validés par EventCreate
    ev = Event(**payload.model_dump())
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev


@router.get("/", response_model=List[EventOut])
def list_events(db: Session = Depends(get_db)):
    """Liste tous les événements (tri par date croissante)."""
    return db.query(Event).order_by(Event.date.asc()).all()


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Récupère un événement par identifiant."""
    ev = db.get(Event, event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    return ev


@router.put("/{event_id}", response_model=EventOut)
def update_event(event_id: int, payload: EventUpdate, db: Session = Depends(get_db)):
    """Met à jour un événement (partiel ou complet)."""
    ev = db.get(Event, event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")

    # Applique uniquement les champs fournis (exclude_unset)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(ev, field, value)

    db.commit()
    db.refresh(ev)
    return ev


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: int, db: Session = Depends(get_db)):
    """Supprime un événement par identifiant."""
    ev = db.get(Event, event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(ev)
    db.commit()
    return None  # 204 No Content
