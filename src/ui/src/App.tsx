import { Routes, Route } from "react-router-dom";
import AppHeader from "./components/AppHeader";
import DemandsPage from "./pages/DemandsPage";
import MatchResultsPage from "./pages/MatchResultsPage";

export default function App() {
  return (
    <div className="app-shell">
      <AppHeader />
      <Routes>
        <Route path="/" element={<DemandsPage />} />
        <Route path="/demands/:demandId/matches" element={<MatchResultsPage />} />
      </Routes>
    </div>
  );
}
