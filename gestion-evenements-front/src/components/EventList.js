// Liste des événements avec affichage des nouveaux champs
// - Boutons modifier / supprimer
// - Mise en forme simple et lisible

import api from "../api/api";

export default function EventList({ events, onEdit, refresh }) {
  const handleDelete = async (id) => {
    if (window.confirm("Supprimer cet événement ?")) {
      await api.delete(`/events/${id}`);
      refresh();
    }
  };

  return (
    <div>
      <h3>📅 Liste des événements</h3>

      {events.length === 0 ? (
        <p>Aucun événement trouvé.</p>
      ) : (
        <ul style={{ paddingLeft: 0, listStyle: "none" }}>
          {events.map((ev) => (
            <li
              key={ev.id}
              style={{
                marginBottom: 12,
                paddingBottom: 10,
                borderBottom: "1px solid #ddd",
              }}
            >
              <div style={{ fontWeight: "bold" }}>
                {ev.titre} — {ev.localisation}
              </div>

              <div>
                🕒 {ev.date ? new Date(ev.date).toLocaleString() : "—"} • ⏳{" "}
                {ev.duree_jours} j • 👥 {ev.nombre_places} places
              </div>

              <div>
                🎯 Importance: {ev.niveau_importance} • ⚙️ Exigeance: {ev.niveau_exigeance}
              </div>

              <div>👨‍🏫 Formateur: {ev.formateur}</div>

              <div style={{ marginTop: 6 }}>
                <em>Description :</em>{" "}
                {ev.description && ev.description.trim().length > 0
                  ? ev.description
                  : "Aucune description fournie."}
              </div>

              <div style={{ marginTop: 8 }}>
                <button onClick={() => onEdit(ev)} style={{ marginRight: 8 }}>
                  ✏️ Modifier
                </button>
                <button onClick={() => handleDelete(ev.id)}>🗑️ Supprimer</button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
