import React, { useState } from "react";
import axios from "axios";

function UploadPDF() {
  const [file, setFile] = useState(null);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleUpload = async () => {
    if (!file) {
      alert("Veuillez choisir un fichier PDF.");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("http://127.0.0.1:8000/upload-pdf/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setData(res.data);
    } catch (error) {
      console.error(error);
      alert("Erreur lors du traitement du fichier !");
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: "30px", fontFamily: "Poppins, sans-serif" }}>
      <h2 style={{ color: "#007bff", marginBottom: "20px" }}>
        📘 Uploader un fichier PDF de cours
      </h2>

      <input type="file" onChange={handleFileChange} accept="application/pdf" />
      <button
        onClick={handleUpload}
        style={{
          marginLeft: "10px",
          padding: "6px 12px",
          backgroundColor: "#007bff",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer",
        }}
      >
        {loading ? "Analyse en cours..." : "Uploader"}
      </button>

      {data && (
        <div style={{ marginTop: "30px", textAlign: "left" }}>
          <h3>🧠 Résultat :</h3>
          <h4 style={{ color: "#555" }}>{data.structured_data.course_title}</h4>

          {data.structured_data.chapters.map((chapter, i) => (
            <div key={i} style={{ marginBottom: "20px" }}>
              <h5 style={{ color: "#333" }}>📖 {chapter.chapter}</h5>
              {chapter.sections.map((section, j) => (
                <div key={j} style={{ marginLeft: "20px" }}>
                  <strong>🔹 {section.title}</strong>
                  <p style={{ marginLeft: "10px", color: "#555" }}>{section.content}</p>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default UploadPDF;
