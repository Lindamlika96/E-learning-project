"""Application FastAPI principale pour la gestion d'événements."""  # doc module

from fastapi import FastAPI  # import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # import CORS
from database.db import Base, engine  # Base ORM et moteur DB
from routes.events import router as events_router  # router événements
from routes.ml import router as ml_router

# Crée les tables au démarrage si absentes (SQLite)
Base.metadata.create_all(bind=engine)

# Instanciation de l’application FastAPI
app = FastAPI(title="Gestion d'événements API", version="0.1.0")

# --- ✅ Configuration CORS ---
origins = [
    "http://localhost:3000",      # React local
    "http://127.0.0.1:3000",      # autre variante locale
    "http://localhost:5173",      # si tu utilises Vite plus tard
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,             # domaines autorisés
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Monter le sous-routeur des événements
app.include_router(events_router)
app.include_router(ml_router)

@app.get("/", tags=["health"])
def health():
    """Vérifie l'état du service.

    Returns
    -------
    dict
        Statut du service et nom.
    """
    return {"status": "ok", "service": "gestion-evenements"}
