"""Schémas Pydantic pour validation/IO des événements (v2)."""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

# Réutilise les mêmes Enums que le modèle pour cohérence
from models.event import VilleTunisie, Importance, Exigeance, Formateur


class EventBase(BaseModel):
    """Champs communs pour création/lecture d'un événement."""

    titre: str = Field(min_length=1, max_length=200)  # nom de l’événement
    description: Optional[str] = None  # détails (optionnel)
    localisation: VilleTunisie  # ville (enum 7 villes)
    date: datetime  # date/heure ISO 8601
    duree_jours: int = Field(ge=1)  # durée en jours >= 1
    nombre_places: int = Field(ge=1)  # nb de places >= 1
    niveau_importance: Importance  # enum Importance
    niveau_exigeance: Exigeance  # enum Exigeance
    formateur: Formateur  # enum Formateur


class EventCreate(EventBase):
    """Payload de création (identique à EventBase)."""
    pass


class EventUpdate(BaseModel):
    """Mise à jour partielle (tous champs optionnels)."""

    titre: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    localisation: Optional[VilleTunisie] = None
    date: Optional[datetime] = None
    duree_jours: Optional[int] = Field(default=None, ge=1)
    nombre_places: Optional[int] = Field(default=None, ge=1)
    niveau_importance: Optional[Importance] = None
    niveau_exigeance: Optional[Exigeance] = None
    formateur: Optional[Formateur] = None


class EventOut(EventBase):
    """Représentation renvoyée par l'API (inclut l'id)."""

    id: int  # identifiant DB
    # Pydantic v2: conversion ORM -> schema
    model_config = {"from_attributes": True}
