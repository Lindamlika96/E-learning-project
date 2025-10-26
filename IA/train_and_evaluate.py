import pandas as pd
import joblib, json
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from imblearn.over_sampling import SMOTE
from feature_builder import build_features

# Charger dataset
df = pd.read_csv("emails_dataset.csv", encoding="utf-8")

# Construire X et y
data, labels = [], []
for _, row in df.iterrows():
    feats = build_features(
        username=row["username"],
        email=row["email"],
        full_name=row["full_name"],
        time_to_submit_ms=row["time_to_submit_ms"]
    )
    data.append(feats)
    labels.append(row["label"])

X = pd.DataFrame(data)
y = labels

# Split train/test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

# Appliquer SMOTE pour équilibrer les classes
sm = SMOTE(random_state=42)
X_train_bal, y_train_bal = sm.fit_resample(X_train, y_train)

print(f"Avant SMOTE : {pd.Series(y_train).value_counts().to_dict()}")
print(f"Après SMOTE : {pd.Series(y_train_bal).value_counts().to_dict()}")

# Définir les modèles
models = {
    "LogisticRegression_balanced": LogisticRegression(max_iter=1000, class_weight="balanced"),
    "RandomForest_balanced": RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced"),
    "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric="logloss", random_state=42)
}

results = {}

# Entraînement et évaluation
for name, model in models.items():
    print(f"\n=== {name} ===")

    # Entraînement avec données équilibrées
    model.fit(X_train_bal, y_train_bal)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    # Rapport
    print(classification_report(y_test, y_pred))

    # Matrice de confusion
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
    plt.title(f"Matrice de confusion - {name}")
    plt.xlabel("Prédit")
    plt.ylabel("Réel")
    plt.show()

    # ROC
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    roc_auc = auc(fpr, tpr)
    plt.plot(fpr, tpr, label=f"{name} (AUC = {roc_auc:.2f})")

    results[name] = {"model": model, "auc": roc_auc}

# Comparer toutes les courbes ROC
plt.plot([0, 1], [0, 1], "k--")
plt.xlabel("Taux de faux positifs")
plt.ylabel("Taux de vrais positifs")
plt.title("Courbes ROC comparées (après équilibrage)")
plt.legend(loc="lower right")
plt.show()

# Choisir le meilleur modèle
best_model_name = max(results, key=lambda k: results[k]["auc"])
best_model = results[best_model_name]["model"]

print(f"\n✅ Meilleur modèle après équilibrage : {best_model_name} (AUC={results[best_model_name]['auc']:.2f})")

# Sauvegarde du meilleur modèle
joblib.dump(best_model, "signup_risk_model.joblib")

# Sauvegarde des seuils
thresholds = {"T_REVIEW": 0.4, "T_BLOCK": 0.8}
with open("signup_risk_thresholds.json", "w") as f:
    json.dump(thresholds, f)

print("📦 Modèle équilibré sauvegardé dans signup_risk_model.joblib")
