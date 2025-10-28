import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.courses_api import router as courses_router
from app.events_db import router as events_router, init_db

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ProjetAI - E-learning")

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(courses_router, prefix="/api")
app.include_router(events_router, prefix="/api")

@app.on_event("startup")
def startup_event():
    """Initialisation lors du démarrage du serveur"""
    logger.info("Initialisation de la base de données...")
    init_db()
    logger.info("Démarrage de l'application FastAPI réussi.")

@app.get("/")
def root():
    """Endpoint racine de test"""
    return {"message": "Bienvenue sur l'API ProjetAI"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
