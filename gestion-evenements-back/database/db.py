"""Configuration SQLAlchemy et utilitaire de session DB."""  # doc module

from sqlalchemy import create_engine  # import moteur SQLAlchemy
from sqlalchemy.orm import sessionmaker, declarative_base  # ORM outils

# DSN SQLite local (changer pour PostgreSQL/MySQL si besoin)             # DSN
SQLALCHEMY_DATABASE_URL = "sqlite:///./events.db"  # fichier SQLite local

# Création du moteur SQLAlchemy                                           # engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,  # URL de connexion
    connect_args={"check_same_thread": False},  # requis pour SQLite + threads
)

# Fabrique de sessions (scopées à la requête)                            # session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # cfg

# Classe de base pour les modèles ORM                                    # Base
Base = declarative_base()  # base des modèles


def get_db():
    """Fournit une session DB par requête FastAPI.

    Yields
    ------
    Session
        Session SQLAlchemy ouverte pour la requête.

    Notes
    -----
    Ferme proprement la session après usage.
    """
    db = SessionLocal()  # ouvre une nouvelle session
    try:
        yield db  # expose la session au dépendant
    finally:
        db.close()  # ferme toujours la session
