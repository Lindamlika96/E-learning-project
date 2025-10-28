from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.at_risk_api import router as at_risk_router
from app.courses_api import router as courses_router
from app.events_db import router as events_router
from database.session import init_db, seed_courses

app = FastAPI()

# Configuration CORS pour permettre les requêtes du frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL du frontend React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialisation de la base de données et seeding
@app.on_event("startup")
async def startup_event():
    init_db()
    seed_courses()

# Inclure les routers
app.include_router(at_risk_router, prefix="/api", tags=["at-risk"])
app.include_router(courses_router, prefix="/api", tags=["courses"])
app.include_router(events_router, prefix="/api", tags=["events"])

@app.get("/")
async def read_root():
    return {"message": "Backend API is running"}