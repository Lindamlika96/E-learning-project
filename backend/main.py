from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.api_courses import router as courses_router
from app.api_events import router as events_router
from app.api_ai import router as ai_router
from app import models

# -------------------------
# INITIALISATION
# -------------------------
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SmartQuiz API")

# CORS : autoriser le frontend à accéder à l'API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en prod, remplace * par ton domaine
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# ROUTE TEST
# -------------------------
@app.get("/")
def read_root():
    return {"message": "✅ SmartQuiz API fonctionne !"}

# -------------------------
# ROUTERS IMPORTÉS
# -------------------------
app.include_router(courses_router)
app.include_router(events_router)
app.include_router(ai_router)
