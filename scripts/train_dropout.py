# scripts/train_dropout.py
# Entraîne sur data/features.csv, évalue sur data/features_test.csv,
# avec validation croisée et analyse des features.

import os
import json
import joblib
import logging
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_validate, train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("train")

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FEATURES_TRAIN = os.path.join(DATA_DIR, "features.csv")
FEATURES_TEST = os.path.join(DATA_DIR, "features_test.csv")
MODEL_PATH = os.path.join(DATA_DIR, "model_dropout.joblib")
METRICS_PATH = os.path.join(DATA_DIR, "metrics.json")
MANIFEST_PATH = os.path.join(DATA_DIR, "model_manifest.json")
PLOTS_DIR = os.path.join(DATA_DIR, "plots")

RANDOM_STATE = 42  # reproductibilité

# Features minimales (une seule métrique de chaque type)
BEHAVIOR_FEATURES = [
    "time_spent_hours",        # Temps total uniquement
    "num_sessions_last7"       # Activité récente uniquement
]

def load_features(path):
    """Charge et prépare les données."""
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    return df

def build_label(df: pd.DataFrame) -> np.ndarray:
    """
    Construit le label dropout basé uniquement sur l'activité récente :
    - Peu ou pas de sessions récentes ET
    - Peu de temps total passé
    """
    # Seuils basés sur les quantiles (plus robuste que la médiane)
    low_activity = df["num_sessions_last7"] <= df["num_sessions_last7"].quantile(0.25)  # Q1
    low_time = df["time_spent_hours"] <= df["time_spent_hours"].quantile(0.25)  # Q1
    
    # Label = peu actif ET peu de temps total
    return (low_activity & low_time).astype(int).values

def plot_feature_importance(model, feature_names, output_dir):
    """Sauvegarde un plot des importances des features."""
    os.makedirs(output_dir, exist_ok=True)
    
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    else:
        importances = np.abs(model.coef_[0])
    
    indices = np.argsort(importances)[::-1]
    
    plt.figure(figsize=(10, 6))
    plt.title("Feature Importances")
    plt.bar(range(len(importances)), importances[indices])
    plt.xticks(range(len(importances)), [feature_names[i] for i in indices], rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "feature_importance.png"))
    plt.close()

def plot_confusion_matrix(y_true, y_pred, output_dir):
    """Sauvegarde la matrice de confusion."""
    os.makedirs(output_dir, exist_ok=True)
    
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.title("Confusion Matrix")
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "confusion_matrix.png"))
    plt.close()

def main():
    # 1. Charger les données
    df_train = load_features(FEATURES_TRAIN)
    if df_train is None or df_train.empty:
        raise SystemExit(f"Train features introuvable ou vide: {FEATURES_TRAIN}")

    # 2. Préparer X/y
    X = df_train[BEHAVIOR_FEATURES].copy()
    y = build_label(df_train)
    
    # Split train/validation pour évaluation finale
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    # 3. Pipeline avec régression logistique fortement régularisée
    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(
            C=0.1,                    # Forte régularisation L2
            class_weight="balanced",   # Gérer le déséquilibre
            random_state=RANDOM_STATE
        ))
    ])

    # 4. Cross-validation
    cv_results = cross_validate(
        model, X_train, y_train,
        cv=5,
        scoring=["accuracy", "roc_auc"],
        return_train_score=True
    )

    # 5. Fit final sur tout train
    model.fit(X_train, y_train)

    # 6. Prédictions validation
    y_pred_val = model.predict(X_val)
    val_acc = accuracy_score(y_val, y_pred_val)
    val_auc = roc_auc_score(y_val, model.predict_proba(X_val)[:, 1])

    # 7. Test si disponible
    test_metrics = None
    if os.path.exists(FEATURES_TEST):
        df_test = load_features(FEATURES_TEST)
        if df_test is not None and not df_test.empty:
            X_test = df_test[BEHAVIOR_FEATURES].copy()
            y_test = build_label(df_test)
            y_pred_test = model.predict(X_test)
            test_metrics = {
                "accuracy": float(accuracy_score(y_test, y_pred_test)),
                "roc_auc": float(roc_auc_score(y_test, model.predict_proba(X_test)[:, 1]))
            }

    # 8. Métriques complètes
    metrics = {
        "random_state": RANDOM_STATE,
        "feature_columns": BEHAVIOR_FEATURES,
        "cv_results": {
            "train_accuracy_mean": float(cv_results["train_accuracy"].mean()),
            "train_accuracy_std": float(cv_results["train_accuracy"].std()),
            "val_accuracy_mean": float(cv_results["test_accuracy"].mean()),
            "val_accuracy_std": float(cv_results["test_accuracy"].std()),
            "train_roc_auc_mean": float(cv_results["train_roc_auc"].mean()),
            "train_roc_auc_std": float(cv_results["train_roc_auc"].std()),
            "val_roc_auc_mean": float(cv_results["test_roc_auc"].mean()),
            "val_roc_auc_std": float(cv_results["test_roc_auc"].std())
        },
        "holdout_validation": {
            "accuracy": float(val_acc),
            "roc_auc": float(val_auc),
            "classification_report": classification_report(y_val, y_pred_val, output_dict=True)
        },
        "test": test_metrics
    }

    # 9. Sauvegardes
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Model
    joblib.dump(model, MODEL_PATH)
    
    # Metrics
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    # Manifest
    manifest = {
        "model_path": MODEL_PATH,
        "metrics_path": METRICS_PATH,
        "feature_columns": BEHAVIOR_FEATURES,
        "random_state": RANDOM_STATE,
        "label_definition": "stalled & (low_activity | low_progress)"
    }
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    # 10. Visualisations
    plot_feature_importance(model[-1], BEHAVIOR_FEATURES, PLOTS_DIR)
    plot_confusion_matrix(y_val, y_pred_val, PLOTS_DIR)

    # Log des résultats
    logger.info("CV Results:")
    logger.info("Train Accuracy: %.3f ± %.3f", 
                metrics["cv_results"]["train_accuracy_mean"],
                metrics["cv_results"]["train_accuracy_std"])
    logger.info("Val Accuracy: %.3f ± %.3f",
                metrics["cv_results"]["val_accuracy_mean"],
                metrics["cv_results"]["val_accuracy_std"])
    logger.info("Train ROC-AUC: %.3f ± %.3f",
                metrics["cv_results"]["train_roc_auc_mean"],
                metrics["cv_results"]["train_roc_auc_std"])
    logger.info("Val ROC-AUC: %.3f ± %.3f",
                metrics["cv_results"]["val_roc_auc_mean"],
                metrics["cv_results"]["val_roc_auc_std"])
    
    logger.info("\nHoldout Validation:")
    logger.info("Accuracy: %.3f", metrics["holdout_validation"]["accuracy"])
    logger.info("ROC-AUC: %.3f", metrics["holdout_validation"]["roc_auc"])
    
    if test_metrics:
        logger.info("\nTest Set:")
        logger.info("Accuracy: %.3f", test_metrics["accuracy"])
        logger.info("ROC-AUC: %.3f", test_metrics["roc_auc"])

    logger.info("\nModèle et métriques sauvegardés:")
    logger.info("- Model: %s", MODEL_PATH)
    logger.info("- Metrics: %s", METRICS_PATH)
    logger.info("- Plots: %s", PLOTS_DIR)

if __name__ == "__main__":
    main()
