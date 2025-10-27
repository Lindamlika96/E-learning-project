"""Modèle ORM Event avec champs adaptés au module IA."""

from enum import Enum  # enums Python pour valeurs contrôlées
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SAEnum
from database.db import Base


# --- Énumérations métier (stockées comme TEXT avec contrainte CHECK en SQLite) ---

class VilleTunisie(str, Enum):
    """7 plus grandes villes pour la localisation."""
    TUNIS = "Tunis"
    SFAX = "Sfax"
    SOUSSE = "Sousse"
    KAIROUAN = "Kairouan"
    BIZERTE = "Bizerte"
    GABES = "Gabès"
    ARIANA = "Ariana"


class Importance(str, Enum):
    """Niveau d'importance de l'événement."""
    TRES_PEU = "Très peu"
    PEU = "Peu"
    MOYEN = "Moyen"
    IMPORTANT = "Important"
    TRES_IMPORTANT = "Très important"
    EXTRAORDINAIRE = "Événement extraordinaire"


class Exigeance(str, Enum):
    """Niveau d’exigeance de l’événement."""
    TRES_PEU = "Très peu"
    PEU = "Peu"
    MOYEN = "Moyen"
    IMPORTANT = "Important"
    TRES_IMPORTANT = "Très important"
    EXTRAORDINAIRE = "Extraordinaire"


class Formateur(str, Enum):
    """Type de formateur/intervenant."""
    ELEVE_UNIV = "Élève Université"
    ETUDIANT_BENEVOLE = "Étudiant bénévole"
    PROF_UNIV = "Professeur Université"
    EXPERT = "Expert"
    PDG = "PDG"


class Event(Base):
    """Table 'events' pour la gestion d'événements.

    Champs adaptés à un futur module de ML.
    """

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)  # identifiant unique
    titre = Column(String(200), nullable=False, index=True)  # nom de l'événement
    description = Column(Text, nullable=True)  # détails de l'événement
    localisation = Column(  # ville parmi 7 options
        SAEnum(VilleTunisie, name="ville_tunisie"),
        nullable=False,
    )
    date = Column(DateTime, nullable=False)  # date/heure de l'événement
    duree_jours = Column(Integer, nullable=False)  # durée en jours (int >= 1)
    nombre_places = Column(Integer, nullable=False)  # capacité totale
    niveau_importance = Column(  # importance qualitative
        SAEnum(Importance, name="importance_enum"),
        nullable=False,
    )
    niveau_exigeance = Column(  # exigeance qualitative
        SAEnum(Exigeance, name="exigeance_enum"),
        nullable=False,
    )
    formateur = Column(  # type d'intervenant
        SAEnum(Formateur, name="formateur_enum"),
        nullable=False,
    )
