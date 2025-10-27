// Formulaire d’ajout/modification d’un événement (mise en page améliorée)

import { useEffect, useState } from "react";

const VILLES = ["Tunis", "Sfax", "Sousse", "Kairouan", "Bizerte", "Gabès", "Ariana"];

const IMPORTANCES = [
  "Très peu",
  "Peu",
  "Moyen",
  "Important",
  "Très important",
  "Événement extraordinaire",
];

const EXIGEANCES = [
  "Très peu",
  "Peu",
  "Moyen",
  "Important",
  "Très important",
  "Extraordinaire",
];

const FORMATEURS = [
  "Élève Université",
  "Étudiant bénévole",
  "Professeur Université",
  "Expert",
  "PDG",
];

// Convertit une date ISO en format compatible avec input datetime-local
function toDatetimeLocal(value) {
  if (!value) return "";
  const d = new Date(value);
  if (isNaN(d)) return value.slice(0, 16);
  const pad = (n) => (n < 10 ? `0${n}` : n);
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(
    d.getHours()
  )}:${pad(d.getMinutes())}`;
}

export default function EventForm({ onSubmit, onPredict, selectedEvent, onCancel }) {
  // état du formulaire
  const [formData, setFormData] = useState({
    titre: "",
    description: "",
    localisation: "Tunis",
    date: "",
    duree_jours: 1,
    nombre_places: 1,
    niveau_importance: "Moyen",
    niveau_exigeance: "Moyen",
    formateur: "Expert",
  });

  useEffect(() => {
    if (selectedEvent) {
      setFormData({
        titre: selectedEvent.titre || "",
        description: selectedEvent.description || "",
        localisation: selectedEvent.localisation || "Tunis",
        date: toDatetimeLocal(selectedEvent.date) || "",
        duree_jours: selectedEvent.duree_jours ?? 1,
        nombre_places: selectedEvent.nombre_places ?? 1,
        niveau_importance: selectedEvent.niveau_importance || "Moyen",
        niveau_exigeance: selectedEvent.niveau_exigeance || "Moyen",
        formateur: selectedEvent.formateur || "Expert",
      });
    }
  }, [selectedEvent]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name === "duree_jours" || name === "nombre_places") {
      setFormData((prev) => ({ ...prev, [name]: Number(value) }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
    if (!selectedEvent) {
      setFormData({
        titre: "",
        description: "",
        localisation: "Tunis",
        date: "",
        duree_jours: 1,
        nombre_places: 1,
        niveau_importance: "Moyen",
        niveau_exigeance: "Moyen",
        formateur: "Expert",
      });
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        marginBottom: 20,
        padding: 20,
        backgroundColor: "#f9f9f9",
        borderRadius: 8,
        maxWidth: 500,
      }}
    >
      <h3 style={{ textAlign: "center", fontWeight: "bold", marginBottom: 20 }}>
        📝 {selectedEvent ? "Modifier un événement" : "Ajouter un événement"}
      </h3>

      {/* Titre */}
      <div style={{ marginBottom: 10 }}>
        <label><strong>Titre</strong></label>
        <input
          name="titre"
          value={formData.titre}
          onChange={handleChange}
          placeholder="Titre"
          required
          style={{ width: "100%", padding: 6 }}
        />
      </div>

      {/* Description */}
      <div style={{ marginBottom: 10 }}>
        <label><strong>Description</strong></label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          placeholder="Description"
          rows={3}
          style={{ width: "100%", padding: 6 }}
        />
      </div>

      {/* Localisation */}
      <div style={{ marginBottom: 10 }}>
        <label><strong>Localisation</strong></label>
        <select
          name="localisation"
          value={formData.localisation}
          onChange={handleChange}
          required
          style={{ width: "100%", padding: 6 }}
        >
          {VILLES.map((v) => (
            <option key={v} value={v}>{v}</option>
          ))}
        </select>
      </div>

      {/* Date */}
      <div style={{ marginBottom: 10 }}>
        <label><strong>Date</strong></label>
        <input
          type="datetime-local"
          name="date"
          value={formData.date}
          onChange={handleChange}
          required
          style={{ width: "100%", padding: 6 }}
        />
      </div>

      {/* Durée */}
      <div style={{ marginBottom: 10 }}>
        <label><strong>Durée (jours)</strong></label>
        <input
          type="number"
          name="duree_jours"
          min={1}
          value={formData.duree_jours}
          onChange={handleChange}
          required
          style={{ width: "100%", padding: 6 }}
        />
      </div>

      {/* Nombre de places */}
      <div style={{ marginBottom: 10 }}>
        <label><strong>Nombre de places</strong></label>
        <input
          type="number"
          name="nombre_places"
          min={1}
          value={formData.nombre_places}
          onChange={handleChange}
          required
          style={{ width: "100%", padding: 6 }}
        />
      </div>

      {/* Importance */}
      <div style={{ marginBottom: 10 }}>
        <label><strong>Niveau d’importance</strong></label>
        <select
          name="niveau_importance"
          value={formData.niveau_importance}
          onChange={handleChange}
          required
          style={{ width: "100%", padding: 6 }}
        >
          {IMPORTANCES.map((n) => (
            <option key={n} value={n}>{n}</option>
          ))}
        </select>
      </div>

      {/* Exigeance */}
      <div style={{ marginBottom: 10 }}>
        <label><strong>Niveau d’exigeance</strong></label>
        <select
          name="niveau_exigeance"
          value={formData.niveau_exigeance}
          onChange={handleChange}
          required
          style={{ width: "100%", padding: 6 }}
        >
          {EXIGEANCES.map((n) => (
            <option key={n} value={n}>{n}</option>
          ))}
        </select>
      </div>

      {/* Formateur */}
      <div style={{ marginBottom: 10 }}>
        <label><strong>Formateur</strong></label>
        <select
          name="formateur"
          value={formData.formateur}
          onChange={handleChange}
          required
          style={{ width: "100%", padding: 6 }}
        >
          {FORMATEURS.map((f) => (
            <option key={f} value={f}>{f}</option>
          ))}
        </select>
      </div>

      {/* Boutons */}
      <div style={{ marginTop: 15, display: "flex", gap: 8, justifyContent: "center" }}>
        <button
          type="submit"
          style={{
            backgroundColor: "#1976d2",
            color: "white",
            border: "none",
            padding: "8px 16px",
            borderRadius: 4,
            cursor: "pointer",
          }}
        >
          {selectedEvent ? "Mettre à jour" : "Ajouter"}
        </button>

        {/* Nouveau bouton Prédire */}
        {typeof onPredict === "function" && (
          <button
            type="button"
            onClick={() => onPredict(formData)}
            style={{
              backgroundColor: "#5c6bc0",
              color: "white",
              border: "none",
              padding: "8px 16px",
              borderRadius: 4,
              cursor: "pointer",
            }}
          >
            Prédire
          </button>
        )}

        {selectedEvent && (
          <button
            type="button"
            onClick={onCancel}
            style={{
              backgroundColor: "#999",
              color: "white",
              border: "none",
              padding: "8px 16px",
              borderRadius: 4,
              cursor: "pointer",
            }}
          >
            Annuler
          </button>
        )}
      </div>
    </form>
  );
}
