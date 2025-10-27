// src/api/api.js
// Configuration centrale d'Axios

import axios from "axios";

// Crée une instance Axios avec l’URL du backend FastAPI
const api = axios.create({
  baseURL: "http://127.0.0.1:8000", // URL backend
});

export default api;
