// Page qui orchestre le CRUD : charge la liste, gère POST/PUT, sélection d'édition — version UI soignée

import { useEffect, useMemo, useState } from "react";
import api from "../api/api";
import EventForm from "../components/EventForm";
import EventList from "../components/EventList";

export default function Home() {
  const [events, setEvents] = useState([]); // liste des événements
  const [selectedEvent, setSelectedEvent] = useState(null); // item en édition
  const [lastPrediction, setLastPrediction] = useState(null); // { proba, label }
  const [predictLoading, setPredictLoading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null); // { title, message, tone }

  // Palette (adaptée à ta charte : violet/indigo)
  const theme = useMemo(
    () => ({
      primary: "#8c52ff",
      primaryDark: "#5e17eb",
      accent: "#cea4ff",
      soft: "#f6f4ff",
      success: "#15b097",
      danger: "#dc3545",
      text: "#0f1221",
      border: "#e7e2fa",
    }),
    []
  );

  // Récupération de tous les événements
  const fetchEvents = async () => {
    try {
      setLoading(true);
      const res = await api.get("/events/");
      setEvents(res.data ?? []);
    } catch (e) {
      console.error(e);
      showToast({
        title: "Erreur",
        message: "Impossible de charger les événements.",
        tone: "danger",
      });
    } finally {
      setLoading(false);
    }
  };

  // Chargement initial
  useEffect(() => {
    fetchEvents();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Création/Mise à jour
  const handleSubmit = async (data) => {
    try {
      if (selectedEvent) {
        await api.put(`/events/${selectedEvent.id}`,(data));
        showToast({ title: "Événement mis à jour", message: `${data?.name ?? "Événement"} enregistré.` });
      } else {
        await api.post("/events/", (data));
        showToast({ title: "Événement créé", message: `${data?.name ?? "Nouvel événement"} ajouté.` });
      }
      setSelectedEvent(null); // reset mode édition
      fetchEvents(); // rechargement de la liste
    } catch (e) {
      console.error(e);
      showToast({ title: "Échec", message: "Sauvegarde impossible.", tone: "danger" });
    }
  };

  // 🔮 Prédiction (envoie les mêmes champs que le POST/PUT)
  const handlePredict = async (data) => {
    try {
      setPredictLoading(true);
      const res = await api.post("/ml/predict", data);
      const p = res?.data?.success_probability;
      const label = !!res?.data?.predicted_label;
      const payload = { proba: Number(p ?? 0), label };
      setLastPrediction(payload);
      showToast({
        title: "Prédiction prête",
        message: `Probabilité de succès : ${((payload.proba || 0) * 100).toFixed(1)}% — ${payload.label ? "Succès" : "Échec"}`,
        tone: payload.label ? "success" : "danger",
      });
    } catch (e) {
      console.error(e);
      showToast({ title: "Erreur ML", message: "Vérifie le backend / logs.", tone: "danger" });
    } finally {
      setPredictLoading(false);
    }
  };

  const showToast = ({ title, message, tone = "neutral" }) => {
    setToast({ id: Date.now(), title, message, tone });
    // Disparition auto après 3.5s
    setTimeout(() => setToast(null), 3500);
  };

  return (
    <div className="app-wrap">
      <StyleBlock theme={theme} />

      <header className="hero">
        <div className="hero__badge">🎟️</div>
        <div className="hero__text">
          <h1>Gestion d'Événements</h1>
          <p>Crée, édite, prédis le succès et pilote la liste en un clin d'œil.</p>
        </div>
      </header>

      <section className="grid">
        <div className="card">
          <div className="card__header">
            <h2>{selectedEvent ? "Modifier un événement" : "Nouvel événement"}</h2>
            {predictLoading && <Spinner label="Prédiction en cours…" />}
          </div>

          {lastPrediction && (
            <PredictionBadge prediction={lastPrediction} />
          )}

          <EventForm
            onSubmit={handleSubmit}
            onPredict={handlePredict}
            selectedEvent={selectedEvent}
            onCancel={() => setSelectedEvent(null)}
          />
        </div>

        <div className="card">
          <div className="card__header">
            <h2>Liste des événements</h2>
            <small className="muted">{events.length} élément(s)</small>
          </div>

          {loading ? (
            <ListSkeleton />
          ) : events.length === 0 ? (
            <EmptyState onRefresh={fetchEvents} />
          ) : (
            <EventList events={events} onEdit={setSelectedEvent} refresh={fetchEvents} />
          )}
        </div>
      </section>

      {toast && <Toast {...toast} />}
    </div>
  );
}

/*** Composants UI ***/
function PredictionBadge({ prediction }) {
  const pct = Math.max(0, Math.min(100, (prediction.proba || 0) * 100));
  const isSuccess = !!prediction.label;
  return (
    <div className={`pill ${isSuccess ? "pill--success" : "pill--danger"}`}>
      <strong>{isSuccess ? "Succès probable" : "Risque d'échec"}</strong>
      <span className="pill__value">{pct.toFixed(1)}%</span>
      <div className="progress">
        <div className="progress__bar" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

function Spinner({ label }) {
  return (
    <div className="spinner">
      <span className="spinner__dot" />
      {label && <span className="spinner__label">{label}</span>}
    </div>
  );
}

function EmptyState({ onRefresh }) {
  return (
    <div className="empty">
      <div className="empty__icon">🗓️</div>
      <h3>Aucun événement</h3>
      <p>Ajoute un premier événement ou recharge la liste.</p>
      <button className="btn" onClick={onRefresh}>Recharger</button>
    </div>
  );
}

function ListSkeleton() {
  return (
    <div className="skeleton-list">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="skeleton-item">
          <div className="sk sk--avatar" />
          <div className="sk sk--line" />
          <div className="sk sk--line sk--short" />
        </div>
      ))}
    </div>
  );
}

function Toast({ title, message, tone }) {
  return (
    <div className={`toast toast--${tone}`} role="status" aria-live="polite">
      <div className="toast__title">{title}</div>
      <div className="toast__msg">{message}</div>
    </div>
  );
}

/** Styles locaux, sans dépendances **/
function StyleBlock({ theme }) {
  return (
    <style>{`
      :root{
        --c-primary:${theme.primary};
        --c-primary-dark:${theme.primaryDark};
        --c-accent:${theme.accent};
        --c-soft:${theme.soft};
        --c-text:${theme.text};
        --c-success:${theme.success};
        --c-danger:${theme.danger};
        --c-border:${theme.border};
        --radius:16px;
      }
      *{box-sizing:border-box}
      .app-wrap{padding:24px; color:var(--c-text); background:linear-gradient(180deg,var(--c-soft),#fff)}

      .hero{display:flex; gap:16px; align-items:center; padding:18px 20px; border:1px solid var(--c-border); border-radius:var(--radius);
            background:linear-gradient(135deg,var(--c-accent),#fff); box-shadow:0 8px 24px rgba(92,65,196,.12)}
      .hero__badge{font-size:28px; width:56px; height:56px; display:grid; place-items:center; border-radius:14px; background:var(--c-primary); color:#fff}
      .hero__text h1{margin:0; font-size:28px; letter-spacing:.2px}
      .hero__text p{margin:4px 0 0; opacity:.75}

      .grid{display:grid; grid-template-columns:1fr; gap:20px; margin-top:20px}
      @media(min-width:980px){ .grid{ grid-template-columns: 1.1fr .9fr; } }

      .card{background:#fff; border:1px solid var(--c-border); border-radius:var(--radius); padding:18px; box-shadow:0 8px 24px rgba(15,18,33,.06)}
      .card__header{display:flex; align-items:center; justify-content:space-between; margin-bottom:12px}
      .muted{opacity:.65}

      .pill{display:flex; align-items:center; gap:10px; margin:10px 0 14px; padding:10px 12px; border-radius:999px; border:1px solid var(--c-border); background:var(--c-soft)}
      .pill--success{border-color:rgba(21,176,151,.25); background:linear-gradient(180deg,#f0fffb,#ffffff)}
      .pill--danger{border-color:rgba(220,53,69,.25); background:linear-gradient(180deg,#fff5f6,#ffffff)}
      .pill__value{font-weight:700}
      .progress{position:relative; height:8px; border-radius:999px; background:#f1eefc; overflow:hidden; flex:1}
      .progress__bar{position:absolute; inset:0 0 0 0; width:0; background:linear-gradient(90deg,var(--c-primary),var(--c-primary-dark)); transition:width .6s ease}

      .spinner{display:inline-flex; align-items:center; gap:10px}
      .spinner__dot{width:10px;height:10px;border-radius:999px; background:var(--c-primary); animation:pulse .9s infinite alternate}
      .spinner__label{font-size:12px; opacity:.7}
      @keyframes pulse{ to{ transform:scale(1.6); opacity:.6 } }

      .empty{display:grid; place-items:center; text-align:center; gap:8px; padding:32px; border:2px dashed var(--c-border); border-radius:var(--radius); background:#fcfbff}
      .empty__icon{font-size:34px}
      .btn{padding:8px 14px; border-radius:10px; border:1px solid var(--c-border); background:var(--c-primary); color:#fff; cursor:pointer}
      .btn:hover{filter:brightness(.95)}

      .skeleton-list{display:grid; gap:12px}
      .skeleton-item{display:grid; grid-template-columns:40px 1fr 120px; align-items:center; gap:10px}
      .sk{background:#f3f0ff; border-radius:10px; height:12px; animation:shimmer 1.2s infinite linear}
      .sk--avatar{width:40px;height:40px;border-radius:12px}
      .sk--line{height:12px}
      .sk--short{width:70%}
      @keyframes shimmer{ 0%{opacity:.6} 50%{opacity:1} 100%{opacity:.6} }

      .toast{position:fixed; right:18px; top:18px; min-width:280px; max-width:380px; padding:12px 14px; border-radius:12px; border:1px solid var(--c-border); background:#fff; box-shadow:0 14px 40px rgba(15,18,33,.18); animation:slideIn .22s ease}
      .toast--success{border-color:rgba(21,176,151,.35)}
      .toast--danger{border-color:rgba(220,53,69,.35)}
      .toast__title{font-weight:700; margin-bottom:4px}
      .toast__msg{opacity:.85}
      @keyframes slideIn{ from{ opacity:0; transform:translateY(-8px) } to{ opacity:1; transform:translateY(0) } }
    `}</style>
  );
}
