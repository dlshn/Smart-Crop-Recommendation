import React, { useEffect, useState } from "react";
import RecommendationForm from "./components/RecommendationForm.jsx";
import ResultCard from "./components/ResultCard.jsx";
import { fetchDistricts, fetchCrops, fetchRecommendations } from "./api.js";

export default function App() {
  const [districts, setDistricts] = useState([]);
  const [crops, setCrops] = useState([]);
  const [district, setDistrict] = useState("");
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [selectedCrops, setSelectedCrops] = useState([]);
  const [lang, setLang] = useState("en");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [metaError, setMetaError] = useState(null);

  useEffect(() => {
    Promise.all([fetchDistricts(), fetchCrops()])
      .then(([d, c]) => {
        setDistricts(d);
        setCrops(c);
        setDistrict(d[0] || "");
      })
      .catch((err) => setMetaError(err.message));
  }, []);

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchRecommendations({
        district, month, crops: selectedCrops, topN: 3,
      });
      setResults(data.results);
    } catch (err) {
      setError(err.message);
      setResults(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🌾 AI-Powered Smart Crop Recommendation System</h1>
        <p className="subtitle">For Sri Lankan Farmers — CS/2020/051</p>
      </header>

      {metaError && (
        <div className="error-banner">
          Could not reach the backend API ({metaError}). Make sure the
          Express server is running on port 5000.
        </div>
      )}

      {districts.length > 0 && crops.length > 0 && (
        <RecommendationForm
          districts={districts}
          crops={crops}
          district={district}
          setDistrict={setDistrict}
          month={month}
          setMonth={setMonth}
          selectedCrops={selectedCrops}
          setSelectedCrops={setSelectedCrops}
          lang={lang}
          setLang={setLang}
          onSubmit={handleSubmit}
          loading={loading}
        />
      )}

      {error && <div className="error-banner">{error}</div>}

      {results && (
        <section className="results">
          <h2>
            Top {results.length} Recommended Crops for {district}
            {results[0] ? ` (${results[0].zone} Zone)` : ""}
          </h2>
          <div className="results-grid">
            {results.map((r, i) => (
              <ResultCard key={r.crop} result={r} rank={i + 1} lang={lang} />
            ))}
          </div>
        </section>
      )}

      <footer className="app-footer">
        Models: Random Forest Regressors trained on 5 years of district-level
        rainfall and market price data (2020–2024). Suitability includes
        agro-climatic zone matching; risk reflects historical rainfall/price
        variability.
      </footer>
    </div>
  );
}
