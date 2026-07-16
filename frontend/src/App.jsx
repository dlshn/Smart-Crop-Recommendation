import React, { useEffect, useState } from "react";
import RecommendationForm from "./components/RecommendationForm.jsx";
import ResultCard from "./components/ResultCard.jsx";
import { getCropName } from "./translations";
import { fetchDistricts, fetchCrops, fetchRecommendations } from "./api.js";

export default function App() {
  const [districts, setDistricts] = useState([]);
  const [crops, setCrops] = useState([]);
  const [district, setDistrict] = useState("");
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [selectedCrops, setSelectedCrops] = useState([]);
  const [lang, setLang] = useState("en");
  const [results, setResults] = useState(null);
  const [longTerm, setLongTerm] = useState(null);
  const [meanPrice, setMeanPrice] = useState(null);
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
        district,
        month,
        crops: selectedCrops,
        lang,
      });
      setResults(data.recommendations);
      setLongTerm(data.longTermCrops);
      setMeanPrice(data.meanPrice);
    } catch (err) {
      setError(err.message);
      setResults(null);
      setLongTerm(null);
      setMeanPrice(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-[1100px] px-5 pb-16 pt-5">
      <nav className="sticky top-4 z-10 mb-6 flex items-center justify-between rounded-full border border-leaf/15 bg-white/85 px-5 py-3.5 shadow-soft backdrop-blur-md">
        <div className="text-[1.05rem] font-bold tracking-wide text-leaf">🌾 SmartCrop</div>
        <div className="flex gap-5 text-sm font-semibold">
          <a href="#recommend" className="text-ink/60 transition-colors hover:text-leaf">Recommend</a>
          <a href="#about" className="text-ink/60 transition-colors hover:text-leaf">About</a>
          <a href="#results" className="text-ink/60 transition-colors hover:text-leaf">Results</a>
        </div>
      </nav>

      <main className="space-y-6">
        <header>
          <div className="flex flex-col items-start justify-between gap-6 rounded-3xl border border-leaf/15 bg-white p-7 shadow-soft transition-shadow duration-300 hover:shadow-lg md:flex-row md:items-center">
            <div>
              <p className="mb-2 text-xs font-bold uppercase tracking-[0.16em] text-wheat">Modern field insight dashboard</p>
              <h1 className="m-0 mb-3 text-[2rem] font-bold leading-tight tracking-tight text-ink">Smart Crop Recommendation for Sri Lankan Farmers</h1>
              <p className="m-0 max-w-xl leading-relaxed text-ink/60">
                A focused planning workspace that combines local suitability, rainfall insight,
                and price forecasting into a clearer decision flow.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <div className="min-w-[104px] rounded-xl border border-leaf/20 bg-leaf/10 px-4 py-3 text-center transition-transform duration-200 hover:-translate-y-0.5">
                <strong className="block text-xl text-leaf">37</strong>
                <span className="text-xs text-ink/50">Crops</span>
              </div>
              <div className="min-w-[104px] rounded-xl border border-leaf/20 bg-leaf/10 px-4 py-3 text-center transition-transform duration-200 hover:-translate-y-0.5">
                <strong className="block text-xl text-leaf">25</strong>
                <span className="text-xs text-ink/50">Districts</span>
              </div>
              <div className="min-w-[104px] rounded-xl border border-leaf/20 bg-leaf/10 px-4 py-3 text-center transition-transform duration-200 hover:-translate-y-0.5">
                <strong className="block text-xl text-leaf">ML</strong>
                <span className="text-xs text-ink/50">Price & Rainfall</span>
              </div>
            </div>
          </div>
        </header>

        {metaError && (
          <div className="rounded-2xl border border-rose-300 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            Could not reach the backend API ({metaError}). Make sure the
            Express server is running on port 5000.
          </div>
        )}

        <section id="about" className="rounded-[24px] border border-leaf/15 bg-white p-7 shadow-soft transition-shadow duration-300 hover:shadow-lg">
          <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
            <div className="max-w-2xl">
              <h2 className="flex items-center gap-2 text-xl font-semibold text-ink">
                <span className="inline-block h-5 w-1.5 rounded-full bg-leaf" />
                About this system
              </h2>
              <p className="mt-3 text-sm leading-7 text-ink/60">
                This project combines crop metadata, district suitability rules, and ML-based price and rainfall
                prediction to help farmers make more confident planting decisions.
              </p>
            </div>
            <div className="whitespace-nowrap rounded-full border border-leaf/20 bg-leaf/10 px-3 py-2 text-sm font-semibold text-leaf">
              Built for practical field use
            </div>
          </div>
          <div className="mt-5 flex flex-wrap gap-2">
            <span className="rounded-full border border-leaf/15 bg-cream px-3 py-1 text-sm text-ink/70">District-aware</span>
            <span className="rounded-full border border-leaf/15 bg-cream px-3 py-1 text-sm text-ink/70">Soil-aware</span>
            <span className="rounded-full border border-leaf/15 bg-cream px-3 py-1 text-sm text-ink/70">Price-aware</span>
            <span className="rounded-full border border-leaf/15 bg-cream px-3 py-1 text-sm text-ink/70">Rainfall-aware</span>
          </div>
        </section>

        {districts.length > 0 && crops.length > 0 && (
          <div id="recommend">
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
          </div>
        )}

        {error && <div className="rounded-2xl border border-rose-300 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div>}

        {results && (
          <section id="results" className="rounded-[24px] border border-leaf/15 bg-white p-7 shadow-soft transition-shadow duration-300 hover:shadow-lg">
            <div className="mb-6 flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
              <div>
                <h2 className="flex items-center gap-2 text-xl font-semibold text-ink">
                  <span className="inline-block h-5 w-1.5 rounded-full bg-leaf" />
                  Recommended profitable crops for {district}
                </h2>
                <p className="mt-1 text-sm text-ink/60">Mean predicted harvest price: LKR {meanPrice}</p>
              </div>
              <div className="whitespace-nowrap rounded-full border border-leaf/20 bg-leaf/10 px-3 py-2 text-sm text-leaf">
                Ranked by predicted gain
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {results.map((r, i) => (
                <ResultCard key={r.crop} result={r} rank={i + 1} lang={lang} />
              ))}
            </div>
          </section>
        )}

        {longTerm && longTerm.length > 0 && (
          <section className="rounded-[24px] border border-leaf/15 bg-white p-7 shadow-soft transition-shadow duration-300 hover:shadow-lg">
            <h2 className="mb-5 flex items-center gap-2 text-xl font-semibold text-ink">
              <span className="inline-block h-5 w-1.5 rounded-full bg-leaf" />
              Long-term crop recommendations
            </h2>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {longTerm.map((item) => (
                <div className="rounded-[20px] border border-leaf/10 bg-cream p-4 transition-transform duration-200 hover:-translate-y-0.5" key={item.crop}>
                  <div className="mb-3 flex items-center justify-between">
                    <div className="text-sm font-semibold text-leaf">Long-term</div>
                    <div className="rounded-full bg-leaf/10 px-2.5 py-1 text-xs text-leaf">Planning</div>
                  </div>
                  <h3 className="text-lg font-semibold text-ink">
                    {lang === "si" ? `${getCropName(item.crop, "si")} (${item.crop})` : item.crop}
                  </h3>
                  <p className="mt-2 text-sm leading-6 text-ink/60">{item.notes}</p>
                  <div className="mt-4 grid grid-cols-2 gap-3">
                    <div className="rounded-xl border border-leaf/10 bg-white p-3">
                      <div className="text-[11px] uppercase tracking-[0.2em] text-ink/40">Harvest days</div>
                      <div className="mt-1 text-sm font-semibold text-ink/80">{item.harvestDays}</div>
                    </div>
                    <div className="rounded-xl border border-leaf/10 bg-white p-3">
                      <div className="text-[11px] uppercase tracking-[0.2em] text-ink/40">Soil</div>
                      <div className="mt-1 text-sm font-semibold text-ink/80">{item.suitableSoilTypes.join(", ")}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}
      </main>

      <footer className="mt-10 border-t border-leaf/10 pt-5 text-sm text-ink/50">
        Models: Random Forest Regressors trained on 5 years of district-level
        rainfall and market price data (2020–2024). Suitability includes
        agro-climatic zone matching; risk reflects historical rainfall/price
        variability.
      </footer>
    </div>
  );
}
