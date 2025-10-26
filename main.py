from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from crud import router as crud_router
from utils.email_verification import send_code


# ⚠️ Importation protégée du router auth
try:
    from auth import router as auth_router
    print("✅ auth_router importé avec succès")
    auth_router_loaded = True
except Exception as e:
    print("⚠️ Erreur lors de l'import de auth_router :", e)
    auth_router_loaded = False

app = FastAPI()

# 🔓 Autoriser les requêtes du frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ← adapte si ton frontend est ailleurs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📦 Création des tables
print("📦 Création des tables SQLAlchemy...")
Base.metadata.create_all(bind=engine)
print("✅ Tables créées")

# 📡 Inclusion des routes
print("📡 Inclusion du routeur CRUD sur /admin")
app.include_router(crud_router, prefix="/admin", tags=["Users"])  # ✅ corrigé

if auth_router_loaded:
    print("📡 Inclusion du routeur AUTH")
    app.include_router(auth_router, tags=["Auth"])

@app.get("/")
def read_root():
    print("👋 Route / appelée")
    return {"message": "Bienvenue sur l'API utilisateur 🎉"}

# 🧪 Test manuel d'envoi d'email
@app.get("/debug-email")
def debug_email():
    print("📤 Envoi manuel de test à daoudwissal2000@gmail.com")
    send_code("daoudwissal2000@gmail.com", "999999")
    return {"message": "✅ Email test envoyé"}
