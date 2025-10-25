import React from "react";
import UploadPDF from "./UploadPDF";
import ShowQuiz from "./ShowQuiz";
import Sidebar from "./components/Sidebar";

function App() {
  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      {/* Barre latérale */}
      <Sidebar />

      {/* Contenu principal */}
      <div style={{ flexGrow: 1, padding: "20px" }}>
        <h1 style={{ textAlign: "center", color: "#007bff" }}>SmartQuiz 🎓</h1>

        {/* Section Upload */}
        <section style={{ marginBottom: "50px" }}>
          <UploadPDF />
        </section>

        <hr />

        {/* Section Affichage du quiz */}
        <section>
          <ShowQuiz />
        </section>
      </div>
    </div>
  );
}

export default App;
