# 🎓 Projet IA — Gestion d’Événements (FastAPI + IA + React)

Ce projet fait partie du module **“IA for Software Engineering”** à **ESPRIT (5SAE3)**.  
Il s’agit d’un système complet **Full Stack** (**FastAPI + React**) permettant la **gestion d’événements pédagogiques** avec une intégration **IA** pour prédire la **probabilité de succès** d’un événement.

---

## 🧩 Objectifs du projet

- Créer une **API backend** en **FastAPI** pour gérer un ensemble d’événements (**CRUD complet**).  
- Intégrer un **modèle de Machine Learning** (entraîné avec **Scikit-Learn**) pour **prédire la réussite** d’un événement.  
- Concevoir un **frontend React moderne** (intégré au template **SB Admin**) pour manipuler les données et déclencher les prédictions en un clic.

---

## ⚙️ Architecture du projet

```bash
Projet IA/
├─ gestion-evenements-back/ ← Backend FastAPI + IA
│  ├─ artifacts/ ← modèle ML (.joblib, métriques)
│  ├─ database/db.py ← config SQLAlchemy (SQLite)
│  ├─ models/ ← modèles Pydantic & SQLAlchemy
│  ├─ routes/ ← routes REST & IA
│  ├─ events.db ← base SQLite locale
│  ├─ main.py ← point d’entrée FastAPI
│  └─ requirements.txt ← dépendances backend
│
└─ gestion-evenements-front/ ← Front React (CRA + Bootstrap)
   ├─ public/ ← fichiers statiques / template
   ├─ src/
   │  ├─ api/api.js ← Axios (connexion API)
   │  ├─ components/ ← EventForm / EventList
   │  ├─ pages/ ← Home / LayoutStatic
   │  ├─ App.js ← Routes ("/evenement")
   │  └─ index.js
   └─ package.json

```
## 🧠 Fonctionnalités principales

### 🎟️ Gestion des événements
- Consultation de la liste des événements  
- Ajout, modification et suppression d’un événement  
- Détails : titre, description, durée, formateur, importance, etc.

### 🤖 Prédiction IA
- Prédire la **probabilité de succès** d’un événement via un bouton **“Prédire”**  
- Modèle ML entraîné (**Logistic Regression**, **RandomForest**, **XGBoost**)  
- Endpoint `/ml/predict` disponible via **FastAPI**  
- Probabilité renvoyée : entre 0 et 1 → succès / échec

---

## 🧠 Exemple d’appel IA

### ➤ Requête

```json
POST /ml/predict
{
  "titre": "Atelier Python",
  "description": "Découverte de FastAPI",
  "localisation": "Tunis",
  "date": "2025-11-15T09:00:00",
  "duree_jours": 2,
  "nombre_places": 50,
  "niveau_importance": "Important",
  "niveau_exigeance": "Moyen",
  "formateur": "Professeur Université"
}
#### ➤ Réponse

```json
{
  "success_probability": 0.87,
  "predicted_label": true,
  "used_features": [
    "duree_jours",
    "nombre_places",
    "localisation",
    "niveau_importance",
    "niveau_exigeance",
    "formateur"
  ]
}

### 🖥️ Détails techniques

### 🔹 Backend (FastAPI)
- **Framework :** FastAPI  
- **ORM :** SQLAlchemy  
- **Base de données :** SQLite  
- **ML :** scikit-learn, joblib, xgboost  
- **Endpoints :**
  - `/events/` — CRUD complet  
  - `/ml/predict` — prédiction IA  
- **CORS activé pour :** `http://localhost:3000`

---

### 🔹 Frontend (React)
- **Framework :** React 19  
- **Gestion API :** Axios  
- **Style :** Bootstrap 5 / SB Admin Template  
- **Routes :**
  - `/` → Tableau de bord  
  - `/evenement` → Page principale (formulaire + liste)  
- **Composants :**
  - `EventForm.js` → formulaire CRUD + bouton “Prédire”  
  - `EventList.js` → affichage des événements  
  - `Home.js` → orchestration CRUD + prédiction  
  - `LayoutStatic.js` → intégration du template SB Admin

---

### 🚀 Installation et lancement

### 🧩 Backend

```bash
cd gestion-evenements-back
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

### 📍 Swagger UI
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 📍 Redoc
[http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

### 💻 Frontend

```bash
cd ../gestion-evenements-front
npm install
npm start

## 📍 Front accessible sur
[http://localhost:3000](http://localhost:3000)

## 📍 Page principale
[http://localhost:3000/evenement](http://localhost:3000/evenement)

---

## 🧱 Base de données

**Fichier :** `gestion-evenements-back/events.db`

### Table : `Event`

| Champ | Type | Description |
|-------|------|--------------|
| id | PK | Identifiant unique |
| titre | String | Titre de l’événement |
| description | String | Description |
| localisation | String | Lieu |
| date | DateTime | Date de l’événement |
| duree_jours | Int | Durée |
| nombre_places | Int | Capacité |
| niveau_importance | Enum | Importance |
| niveau_exigeance | Enum | Exigence |
| formateur | String | Nom du formateur |

---

## ⚡ Routes principales

| Méthode | Endpoint | Description |
|----------|-----------|-------------|
| GET | `/events/` | Liste des événements |
| POST | `/events/` | Création d’un événement |
| GET | `/events/{id}` | Récupérer un événement |
| PUT | `/events/{id}` | Modifier un événement |
| DELETE | `/events/{id}` | Supprimer un événement |
| POST | `/ml/predict` | Prédiction IA |

---

## 📦 Technologies utilisées

### 🧰 Backend
- Python 3.12  
- FastAPI  
- SQLAlchemy  
- Pydantic  
- Scikit-learn  
- XGBoost  
- Joblib  
- Uvicorn

### 💻 Frontend
- React 19  
- Axios  
- Bootstrap 5  
- HTML / CSS / JS

---

## 🧠 Outils et bonnes pratiques

- **IDE :** Visual Studio Code  
- **Test API :** Swagger UI / Postman  
- **Git Flow :** branche `evenement`  
- **.gitignore :**
  - `.venv`
  - `node_modules`
  - `events.db`
  - `artifacts/`  
- **Bonne pratique :** aucun fichier > 100 Mo (pour éviter les erreurs GitHub)

---

## 🚀 Améliorations possibles

- Authentification JWT (Admin / Utilisateur)  
- Pagination et recherche d’événements  
- Upload d’affiches ou documents d’événement  
- Tableau de bord analytique (charts)  
- Déploiement sur Render / Railway / Vercel

---

## 👨‍💻 Auteurs

| Nom | Rôle | Description |
|------|------|-------------|
| **Slim-Fady HANAFI** | 🧠 Développeur IA & Full-Stack | Responsable du module “Gestion d’Événements” (FastAPI + React + IA) |
| **Linda MLIKA** | 🎨 UI/UX & Intégration Front | Intégration du template SB Admin + UI de l’application e-learning |

---

## 🏁 Conclusion

Le module **Gestion d’Événements** s’intègre dans un projet e-learning intelligent, combinant :

- Un backend robuste en **FastAPI**  
- Un frontend moderne en **React**  
- Une intelligence artificielle intégrée pour estimer le succès des événements  

> 🔹 **Un projet complet, intelligent et évolutif, démontrant la maîtrise du développement Full Stack & IA.**
