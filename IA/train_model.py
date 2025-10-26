import pandas as pd
import joblib, json
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE
from feature_builder import build_features

# Charger dataset
df = pd.read_csv("IA/emails_dataset.csv", encoding="utf-8")

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

# Rééquilibrage
sm = SMOTE(random_state=42)
X_train_bal, y_train_bal = sm.fit_resample(X_train, y_train)

# Entraînement Logistic Regression équilibrée
model = LogisticRegression(max_iter=1000, class_weight="balanced")
model.fit(X_train_bal, y_train_bal)

# Évaluation
y_pred = model.predict(X_test)
print("\n=== Rapport de classification ===")
print(classification_report(y_test, y_pred))

# Sauvegarde du modèle
joblib.dump(model, "IA/signup_risk_model.joblib")

# Sauvegarde des colonnes
with open("IA/feature_names.json", "w") as f:
    json.dump(list(X.columns), f)

# Sauvegarde des seuils
thresholds = {"T_REVIEW": 0.4, "T_BLOCK": 0.8}
with open("IA/signup_risk_thresholds.json", "w") as f:
    json.dump(thresholds, f)

print("📦 Modèle, features et seuils sauvegardés avec succès !")
