import React, { useEffect, useState } from "react";
import "./Sidebar.css";

function Sidebar() {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  // Appel à l’API FastAPI
  useEffect(() => {
fetch("http://127.0.0.1:8000/api/courses/")
      .then((res) => res.json())
      .then((data) => {
        setCourses(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Erreur lors du chargement des cours :", error);
        setLoading(false);
      });
  }, []);

  return (
    <div className="sidebar">
      <h2 className="sidebar-title">📚 Cours</h2>

      {loading ? (
        <p>Chargement...</p>
      ) : courses.length === 0 ? (
        <p>Aucun cours disponible</p>
      ) : (
        <ul className="course-list">
          {courses.map((course) => (
            <li key={course.id} className="course-item">
              {course.title}
              <br />
              <button className="go-quiz-btn">Go to Quiz ➡️</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default Sidebar;
