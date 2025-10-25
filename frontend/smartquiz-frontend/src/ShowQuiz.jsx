import React, { useState } from "react";
import axios from "axios";

function ShowQuiz() {
  const [courseId, setCourseId] = useState("");
  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchQuiz = async () => {
    if (!courseId) {
      setError("⚠️ Veuillez entrer un ID de cours.");
      return;
    }

    setError("");
    setLoading(true);

    try {
      const response = await axios.post("http://127.0.0.1:8000/get-quiz/", {
        course_id: parseInt(courseId),
      });
      setQuiz(response.data.quiz);
    } catch (err) {
      setError("Erreur lors du chargement du quiz 😥");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "800px", margin: "40px auto", textAlign: "center" }}>
      <h2>📋 Afficher un quiz</h2>

      <input
        type="number"
        placeholder="Entrez l'ID du cours"
        value={courseId}
        onChange={(e) => setCourseId(e.target.value)}
        style={{ padding: "8px", width: "60%", marginRight: "10px" }}
      />
      <button onClick={fetchQuiz} style={{ padding: "8px 16px" }}>
        Charger le quiz
      </button>

      {loading && <p>⏳ Chargement du quiz...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {quiz && (
        <div style={{ textAlign: "left", marginTop: "30px" }}>
          <h3>{quiz.title}</h3>
          <ol>
            {quiz.questions.map((q, index) => (
              <li key={index}>
                <strong>{q.question_text}</strong>
                <ul>
                  <li>{q.option_a}</li>
                  <li>{q.option_b}</li>
                  <li>{q.option_c}</li>
                  {q.option_d && <li>{q.option_d}</li>}
                </ul>
                <p>✅ Réponse correcte : {q.correct_answer}</p>
                <hr />
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}

export default ShowQuiz;
