# scripts/prepare_ml_dataset.py
# Prépare data/features.csv (train) et data/features_test.csv (test) à partir des CSV bruts (Kaggle).
# ZÉRO FUITE : toutes les features sont calculées à un instant d'observation T_obs (par défaut 14 jours
# après la première activité par (user_id, course_id)). Le label final reste en dehors de ce script.
#
# Usage typique :
#   python scripts/prepare_ml_dataset.py \
#     --train data/ml/train.csv --test data/ml/test.csv \
#     --out data/features.csv --out_test data/features_test.csv \
#     --courses data/courses.json \
#     --tobs-days 14
#
# Options :
#   --tobs-days N            : T_obs = min(time) + N jours (par groupe user_id,course_id). [def=14]
#   --tobs-date YYYY-MM-DD   : T_obs = date fixe (UTC) pour tous (ignore --tobs-days).
#   --no-extras              : n’ajoute pas les features dérivées (progress_velocity, pages_per_session, stalled).

import argparse
import os
import json
from datetime import timezone
import pandas as pd
import numpy as np

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DEFAULT_TOTAL_PAGES = 10  # fallback si courses.json absent

CONTENT_ACTIONS = {
    "action_click_courseware",
    "action_click_progress",
    "action_load_video",
    "action_play_video",
    "action_pause_video",
    "action_stop_video",
    "action_seek_video",
    "action_click_about",
    "action_click_info",
}
ANNOTATION_ACTIONS = {"action_create_comment", "action_create_thread"}
EVENT_CONTENT_ACTIONS = {"pdf_open", "page_view", "click_courseware", "play_video", "load_video"}

# Colonnes de base attendues par le script d’entraînement
CANONICAL_COLUMNS = [
    "user_id",
    "course_id",
    "percent_complete",
    "time_spent_hours",
    "pages_viewed",
    "num_sessions_last7",
    "annotations_count",
    "days_since_last_activity",
]

# Colonnes dérivées (extras) — utiles pour ta logique “effort vs progrès”
EXTRA_COLUMNS = [
    "progress_velocity",   # percent_complete / (time_spent_hours + eps)
    "pages_per_session",   # pages_viewed / (num_sessions_last7 + 1)
    "stalled",             # 1{days_since_last_activity >= 7}
]

# ---------- utilitaires ----------

def _norm_id(x: pd.Series, lower=True, none_placeholder="unknown"):
    s = x.astype(str).str.strip()
    if lower:
        s = s.str.lower()
    return s.replace({"": none_placeholder, "nan": none_placeholder, "none": none_placeholder})

def _safe_first_scalar(x, default=0):
    if isinstance(x, pd.Series):
        return x.iloc[0] if len(x) else default
    if isinstance(x, (np.ndarray, list, tuple)):
        return x[0] if len(x) else default
    return x if x is not None else default

def load_course_pages(courses_json_path):
    pages = {}
    if courses_json_path and os.path.exists(courses_json_path):
        try:
            with open(courses_json_path, "r", encoding="utf-8") as f:
                arr = json.load(f)
            for c in arr:
                try:
                    pages[int(c.get("course_id"))] = int(c.get("total_pages", DEFAULT_TOTAL_PAGES))
                except Exception:
                    pass
        except Exception:
            pass
    return pages

def detect_format(df: pd.DataFrame):
    cols = set(df.columns.str.lower())
    if any(c for c in cols if c.startswith("action_")) and "avg_nactions_per_session" in cols:
        return "agg"
    if "action" in cols and "time" in cols:
        return "event"
    if "unique_session_count" in cols:
        return "agg"
    return "unknown"

def _tobs_from_group(group_time: pd.Series, days: int, fixed_date: pd.Timestamp | None):
    """
    Retourne T_obs (timestamp UTC) pour un groupe :
      - si fixed_date fourni → cette date (UTC)
      - sinon → min(time) + days
    """
    if fixed_date is not None:
        return fixed_date
    tmin = pd.to_datetime(group_time, utc=True, errors="coerce").min()
    if pd.isna(tmin):
        # si pas de temps valide, on prend "now" UTC et ajoute days (purement défensif)
        return pd.Timestamp.now(tz=timezone.utc) + pd.Timedelta(days=days)
    return tmin + pd.Timedelta(days=days)

def _clip_to_tobs(df_group: pd.DataFrame, tobs: pd.Timestamp) -> pd.DataFrame:
    """Filtre les lignes à time <= T_obs (time doit être datetime UTC)."""
    if "time" not in df_group.columns:
        return df_group.iloc[0:0]  # pas de temps → pas mesurable à T_obs
    return df_group.loc[df_group["time"] <= tobs]

def _finalize_rows(rows: list[dict], include_extras: bool) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if df.empty:
        # Garantit les colonnes
        for c in CANONICAL_COLUMNS:
            if c not in df.columns:
                df[c] = []
        if include_extras:
            for c in EXTRA_COLUMNS:
                df[c] = []
        return df

    # sécurité colonnes canoniques
    for c in CANONICAL_COLUMNS:
        if c not in df.columns:
            df[c] = 0

    # extras
    if include_extras:
        eps = 1e-3
        if "progress_velocity" not in df.columns:
            df["progress_velocity"] = (df["percent_complete"] / (df["time_spent_hours"] + eps)).fillna(0.0)
        if "pages_per_session" not in df.columns:
            df["pages_per_session"] = (df["pages_viewed"] / (df["num_sessions_last7"] + 1.0)).fillna(0.0)
        if "stalled" not in df.columns:
            df["stalled"] = (df["days_since_last_activity"] >= 7).astype(int)

    # réordonne : clés, canoniques puis extras
    ordered = CANONICAL_COLUMNS + ([c for c in EXTRA_COLUMNS if c in df.columns] if include_extras else [])
    return df[ordered]

def _consolidate_features(df_out: pd.DataFrame) -> pd.DataFrame:
    """Dernière passe anti-doublons sur (user_id, course_id) avec des règles stables."""
    if df_out.empty:
        return df_out

    df_out["user_id"] = _norm_id(df_out["user_id"])
    df_out["course_id"] = _norm_id(df_out["course_id"])

    agg_rules = {
        "percent_complete": "max",
        "time_spent_hours": "sum",
        "pages_viewed": "sum",
        "num_sessions_last7": "sum",
        "annotations_count": "sum",
        "days_since_last_activity": "min",
    }
    # si extras présents, définir des règles raisonnables
    if "progress_velocity" in df_out.columns:
        agg_rules["progress_velocity"] = "mean"
    if "pages_per_session" in df_out.columns:
        agg_rules["pages_per_session"] = "mean"
    if "stalled" in df_out.columns:
        agg_rules["stalled"] = "max"

    df_grp = df_out.groupby(["user_id", "course_id"], as_index=False).agg(agg_rules)
    # réordonne
    ordered = [c for c in CANONICAL_COLUMNS if c in df_grp.columns] + [c for c in EXTRA_COLUMNS if c in df_grp.columns]
    return df_grp[ordered]

# ---------- préparation depuis formats ----------

def prepare_from_event(df: pd.DataFrame, course_pages, tobs_days: int, fixed_date: pd.Timestamp | None, include_extras: bool):
    df = df.rename(columns=str.lower)

    # clés
    if "username" in df.columns and "user_id" not in df.columns:
        df = df.rename(columns={"username": "user_id"})
    if "user_id" not in df.columns:
        raise ValueError("Colonne user_id/username absente du CSV événementiel.")
    if "course_id" not in df.columns:
        raise ValueError("Colonne course_id absente du CSV événementiel.")
    if "time" not in df.columns:
        raise ValueError("Colonne time absente du CSV événementiel.")

    # normalisation
    df["user_id"] = _norm_id(df["user_id"])
    df["course_id"] = _norm_id(df["course_id"])
    df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce")

    rows = []
    for (uid, cid), group in df.groupby(["user_id", "course_id"], dropna=False):
        # T_obs par groupe
        tobs = _tobs_from_group(group["time"], tobs_days, fixed_date)
        g = _clip_to_tobs(group, tobs)
        if g.empty:
            # rien avant T_obs → zéro activité observée
            pages_viewed = 0
            time_spent_secs = 0.0
            last_ts = pd.NaT
            num_sessions_last7 = 0
            annotations = 0
        else:
            # pages vues = actions de contenu jusqu’à T_obs
            pages_viewed = int(g["action"].isin(EVENT_CONTENT_ACTIONS).sum())

            # temps passé
            if "time_difference" in g.columns:
                time_spent_secs = float(g["time_difference"].fillna(0).astype(float).sum())
            else:
                if "session_id" in g.columns:
                    time_spent_secs = int(g["session_id"].nunique()) * 5 * 60
                else:
                    time_spent_secs = len(g) * 15  # simple fallback

            last_ts = g["time"].max()
            last7 = tobs - pd.Timedelta(days=7)
            if "session_id" in g.columns:
                num_sessions_last7 = int(g.loc[g["time"] >= last7, "session_id"].nunique())
            else:
                num_sessions_last7 = int((g["time"] >= last7).sum())

            annotations = int(g["action"].isin({"create_comment", "create_thread"}).sum())

        time_spent_hours = time_spent_secs / 3600.0
        days_since_last_activity = int((tobs - last_ts).days) if pd.notnull(last_ts) else 9999  # loin dans le passé ⇒ “pas d’activité”

        # progression (%)
        try:
            cid_int = int(str(cid)) if str(cid).isdigit() else None
        except Exception:
            cid_int = None
        total_pages = course_pages.get(cid_int, DEFAULT_TOTAL_PAGES)
        percent_complete = min(100.0, (pages_viewed / total_pages * 100.0)) if total_pages > 0 else 0.0

        row = {
            "user_id": uid,
            "course_id": cid,
            "percent_complete": round(percent_complete, 2),
            "time_spent_hours": round(time_spent_hours, 3),
            "pages_viewed": int(pages_viewed),
            "num_sessions_last7": int(num_sessions_last7),
            "annotations_count": int(annotations),
            "days_since_last_activity": int(days_since_last_activity),
        }

        # extras calculés plus tard dans _finalize_rows (pour cohérence)
        rows.append(row)

    df_out = _finalize_rows(rows, include_extras=include_extras)
    return df_out

def prepare_from_agg(df: pd.DataFrame, course_pages, tobs_days: int, fixed_date: pd.Timestamp | None, include_extras: bool):
    """
    Format agrégé : si une colonne 'time' existe, on la respecte (et on coupe à T_obs).
    Sinon, on fait au mieux sans fuite (on ne connaît pas la chronologie fine) :
      - on utilise uniquement des colonnes “taux” ou “comptes” déjà agrégées,
      - on évite d’inférer des signaux postérieurs à T_obs.
    """
    df = df.rename(columns=str.lower)

    if "username" in df.columns:
        df = df.rename(columns={"username": "user_id"})
    if "enroll_id" in df.columns and "user_id" not in df.columns:
        df = df.rename(columns={"enroll_id": "user_id"})
    if "user_id" not in df.columns:
        raise ValueError("Colonne user_id/username/enroll_id absente du CSV agrégé.")
    if "course_id" not in df.columns:
        raise ValueError("Colonne course_id absente du CSV agrégé.")

    df["user_id"] = _norm_id(df["user_id"])
    df["course_id"] = _norm_id(df["course_id"])

    has_time = "time" in df.columns
    if has_time:
        df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce")

    rows = []
    for (uid, cid), group in df.groupby(["user_id", "course_id"], dropna=False):
        if has_time:
            tobs = _tobs_from_group(group["time"], tobs_days, fixed_date)
            g = _clip_to_tobs(group, tobs)
        else:
            # pas de temps → impossible de couper finement ; on prend la ligne (ou somme) “avant T_obs”
            g = group

        # pages vues via colonnes action_* si dispo
        pages_viewed = 0
        for col in CONTENT_ACTIONS:
            if col in g.columns:
                pages_viewed += int(g[col].fillna(0).astype(float).sum())

        # annotations
        annotations = 0
        for col in ANNOTATION_ACTIONS:
            if col in g.columns:
                annotations += int(g[col].fillna(0).astype(float).sum())

        # temps passé
        if "time_difference" in g.columns:
            time_spent_secs = float(g["time_difference"].fillna(0).astype(float).sum())
        else:
            unique_sessions = _safe_first_scalar(g["unique_session_count"], 0) if "unique_session_count" in g.columns else 0
            avg_actions = float(_safe_first_scalar(g["avg_nactions_per_session"], 0.0)) if "avg_nactions_per_session" in g.columns else 0.0
            time_spent_secs = float(unique_sessions) * float(avg_actions) * 6.0

        time_spent_hours = time_spent_secs / 3600.0

        # activité récente / last7
        if has_time and not g.empty:
            tobs = _tobs_from_group(group["time"], tobs_days, fixed_date)
            last7 = tobs - pd.Timedelta(days=7)
            num_sessions_last7 = int((pd.to_datetime(g["time"], utc=True, errors="coerce") >= last7).sum())
            last_ts = pd.to_datetime(g["time"], utc=True, errors="coerce").max()
            days_since_last_activity = int((tobs - last_ts).days) if pd.notnull(last_ts) else 9999
        else:
            # sans horodatage, on ne sait pas — rester conservateur
            num_sessions_last7 = int(_safe_first_scalar(g["unique_session_count"], 0)) if "unique_session_count" in g.columns else 0
            days_since_last_activity = 9999

        # progression (%)
        try:
            cid_int = int(str(cid)) if str(cid).isdigit() else None
        except Exception:
            cid_int = None
        total_pages = course_pages.get(cid_int, DEFAULT_TOTAL_PAGES)
        percent_complete = min(100.0, (pages_viewed / total_pages * 100.0)) if total_pages > 0 else 0.0

        row = {
            "user_id": uid,
            "course_id": cid,
            "percent_complete": round(percent_complete, 2),
            "time_spent_hours": round(time_spent_hours, 3),
            "pages_viewed": int(pages_viewed),
            "num_sessions_last7": int(num_sessions_last7),
            "annotations_count": int(annotations),
            "days_since_last_activity": int(days_since_last_activity),
        }
        rows.append(row)

    df_out = _finalize_rows(rows, include_extras=include_extras)
    return df_out

# ---------- pipeline ----------

def build_features_from_file(path_in: str, out_csv: str, courses_json=None,
                             tobs_days: int = 14, fixed_date_str: str | None = None,
                             include_extras: bool = True):
    print("Lecture:", path_in)
    df = pd.read_csv(path_in)
    fmt = detect_format(df)
    print("Format détecté:", fmt)

    # charge total_pages par course_id (facultatif)
    course_pages = load_course_pages(courses_json) if courses_json else {}

    # date fixe ?
    fixed_date = None
    if fixed_date_str:
        fixed_date = pd.to_datetime(fixed_date_str, utc=True, errors="coerce")
        if pd.isna(fixed_date):
            raise ValueError(f"--tobs-date invalide: {fixed_date_str}. Exemple: 2017-03-01")

    if fmt == "agg":
        df_out = prepare_from_agg(df, course_pages, tobs_days, fixed_date, include_extras)
    elif fmt == "event":
        df_out = prepare_from_event(df, course_pages, tobs_days, fixed_date, include_extras)
    else:
        raise ValueError("Format non reconnu — vérifie les colonnes d'entrée.")

    # sécurité colonnes de base
    for c in CANONICAL_COLUMNS:
        if c not in df_out.columns:
            df_out[c] = 0
    df_out = df_out[[c for c in CANONICAL_COLUMNS if c in df_out.columns] +
                    [c for c in EXTRA_COLUMNS if c in df_out.columns]]

    # consolidation anti-doublons (user_id, course_id)
    df_out = _consolidate_features(df_out)

    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df_out.to_csv(out_csv, index=False)
    print(f"[prepare_ml_dataset] Features écrites -> {out_csv}  (rows={len(df_out)})")
    return df_out

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--train", required=True, help="CSV brut pour le train")
    p.add_argument("--test", required=False, help="CSV brut pour le test")
    p.add_argument("--out", default=os.path.join(DATA_DIR, "features.csv"), help="Chemin sortie features train")
    p.add_argument("--out_test", default=os.path.join(DATA_DIR, "features_test.csv"), help="Chemin sortie features test")
    p.add_argument("--courses", default=os.path.join(DATA_DIR, "courses.json"), help="courses.json (pour total_pages)")
    p.add_argument("--tobs-days", type=int, default=14, help="Fenêtre d'observation en jours après 1ère activité (par groupe)")
    p.add_argument("--tobs-date", type=str, default=None, help="Date fixe UTC (YYYY-MM-DD) pour T_obs; surpasse --tobs-days")
    p.add_argument("--no-extras", action="store_true", help="Désactive les features dérivées (velocity, pages/session, stalled)")
    args = p.parse_args()

    build_features_from_file(
        args.train, args.out,
        courses_json=args.courses,
        tobs_days=args.tobs_days,
        fixed_date_str=args.tobs_date,
        include_extras=(not args.no_extras),
    )
    if args.test:
        build_features_from_file(
            args.test, args.out_test,
            courses_json=args.courses,
            tobs_days=args.tobs_days,
            fixed_date_str=args.tobs_date,
            include_extras=(not args.no_extras),
        )
    print("OK")

if __name__ == "__main__":
    main()
