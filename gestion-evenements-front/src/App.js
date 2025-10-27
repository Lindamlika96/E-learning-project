import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LayoutStatic from "./pages/LayoutStatic";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/evenement" element={<LayoutStatic />} />
      </Routes>
    </Router>
  );
}
