# Projet AI - E-learning (Gestion des Cours + Prédiction Abandon)

## Description
Mini application FastAPI simulant un e-learning :
- Lecture des cours (`GET /api/courses`)
- Ingestion d’événements (`POST /api/analytics/events`)
- Pipeline IA LogisticRegression → risque d’abandon.

## Étapes d’exécution
```bash
python scripts/import_courses_to_sqlite.py
python scripts/import_events_json_to_sqlite.py
python scripts/aggregate_from_sqlite.py
python scripts/train_dropout.py
python scripts/batch_predict_and_notify.py
