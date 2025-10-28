import os
import pandas as pd

ROOT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(ROOT, ".."))

RAW_TRAIN = os.path.join(ROOT, "data", "ml", "train.csv")
RAW_TEST  = os.path.join(ROOT, "data", "ml", "test.csv")
FTR_TRAIN = os.path.join(ROOT, "data", "features.csv")
FTR_TEST  = os.path.join(ROOT, "data", "features_test.csv")

def pick_keys(df, options):
    for ks in options:
        if all(k in df.columns for k in ks):
            return ks
    return None

def check_raw():
    print("\n==== RAW (data/ml/*.csv) ====")
    if not (os.path.exists(RAW_TRAIN) and os.path.exists(RAW_TEST)):
        print("[SKIP] Fichiers bruts introuvables:", RAW_TRAIN, RAW_TEST)
        return

    train = pd.read_csv(RAW_TRAIN, low_memory=False)
    test  = pd.read_csv(RAW_TEST,  low_memory=False)

    print("train shape:", train.shape, " | test shape:", test.shape)

    key_cols_options = [
        ["enroll_id"],
        ["username","course_id","session_id"],
        ["username","course_id"],
    ]
    k_train = pick_keys(train, key_cols_options)
    k_test  = pick_keys(test,  key_cols_options)
    print("Keys train:", k_train, "| Keys test:", k_test)

    if not k_train or not k_test:
        print("[ALERTE] Impossible d’identifier une clé commune.")
        print("Colonnes train (début):", list(train.columns)[:12], "...")
        print("Colonnes test  (début):", list(test.columns)[:12],  "...")
    else:
        s_train = set(map(tuple, train[k_train].astype(str).values))
        s_test  = set(map(tuple,  test[k_test].astype(str).values))
        inter   = s_train & s_test
        print(f"Overlap (train ∩ test) sur clés {k_train}: {len(inter)}")
        print(f"Ratio overlap côté test : {len(inter) / max(1,len(s_test)):.4f}")
        print(f"Ratio overlap côté train: {len(inter) / max(1,len(s_train)):.4f}")

    # Distribution du label s'il existe
    for name, df in [("train",train),("test",test)]:
        if "truth" in df.columns:
            print(f"\ntruth distribution [{name}]:")
            print(df["truth"].value_counts(dropna=False))

def check_features():
    print("\n==== FEATURES (data/features*.csv) ====")
    if not (os.path.exists(FTR_TRAIN) and os.path.exists(FTR_TEST)):
        print("[SKIP] Fichiers features introuvables:", FTR_TRAIN, FTR_TEST)
        return

    ftr  = pd.read_csv(FTR_TRAIN)
    ftrT = pd.read_csv(FTR_TEST)
    print("features.csv shape:", ftr.shape, " | features_test.csv shape:", ftrT.shape)

    must_cols = {"user_id","course_id"}
    if not must_cols.issubset(ftr.columns) or not must_cols.issubset(ftrT.columns):
        print("[ERREUR] Les features doivent contenir user_id et course_id.")
        print("Cols features:", list(ftr.columns))
        print("Cols features_test:", list(ftrT.columns))
        return

    s_train = set(map(tuple, ftr[["user_id","course_id"]].astype(str).values))
    s_test  = set(map(tuple, ftrT[["user_id","course_id"]].astype(str).values))
    inter   = s_train & s_test

    print(f"Overlap (features ∩ features_test) sur (user_id,course_id): {len(inter)}")
    print(f"Ratio overlap côté features_test: {len(inter) / max(1,len(s_test)):.4f}")
    print(f"Ratio overlap côté features:      {len(inter) / max(1,len(s_train)):.4f}")

if __name__ == "__main__":
    check_raw()
    check_features()
    print("\n[OK] Vérifications terminées.")
