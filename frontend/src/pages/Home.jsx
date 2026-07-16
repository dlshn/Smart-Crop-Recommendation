import React, { useEffect, useState } from "react";
import RecommendationForm from "../components/RecommendationForm.jsx";
import ResultCard from "../components/ResultCard.jsx";
import { getCropName } from "../translations";
import { fetchDistricts, fetchCrops, fetchRecommendations } from "../api.js";

export default function Home() {
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
    <div className="space-y-6">
      <header>
        <div className="flex flex-col items-start justify-between gap-6 rounded-none border border-leaf/15 bg-white p-7 shadow-soft transition-shadow duration-300 hover:shadow-lg md:flex-row md:items-center">
          <div>
            <p className="mb-2 text-xs font-bold uppercase tracking-[0.16em] text-wheat">Your district. Your season. Your best crop.</p>
            <h1 className="m-0 mb-3 text-[2rem] font-bold leading-tight tracking-tight text-ink">Smart Crop Recommendation for Sri Lankan Farmers</h1>
            <p className="m-0 max-w-full leading-relaxed text-ink/60">
              A simple tool built around one goal: helping you choose the crop most likely to succeed and sell well, right where you farm.

            </p>
          </div>
          {/* <div className="flex flex-wrap gap-3">
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
          </div> */}
        </div>
      </header>

      {metaError && (
        <div className="rounded-2xl border border-rose-300 bg-rose-50 px-4 py-3 text-sm text-rose-700">
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

      {error && <div className="rounded-2xl border border-rose-300 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div>}

      {results && (
        <section className="rounded-none border border-leaf/15 bg-white p-7 shadow-soft transition-shadow duration-300 hover:shadow-lg">
          <div className="mb-6 flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
            <div>
              <h2 className="flex items-center gap-2 text-xl font-semibold text-ink">
                <span className="inline-block h-5 w-1.5 rounded-full bg-leaf" />
                Recommended profitable crops for <b>{district}</b>
              </h2>
              {/* <p className="mt-1 text-sm text-ink/60">Mean predicted harvest price: LKR {meanPrice}</p> */}
            </div>
            <div className="whitespace-nowrap rounded-full border border-leaf/20 bg-leaf/10 px-3 py-2 text-sm text-leaf">
              Ranked by predicted gain
            </div>
          </div>
          {results.length === 0 ? (
            <p className="text-sm text-ink/60">No crops matched for this district, month, and selection. Try widening your candidate crop list.</p>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {results.map((r, i) => (
                <ResultCard key={r.crop} result={r} rank={i + 1} lang={lang} />
              ))}
            </div>
          )}
        </section>
      )}

      {longTerm && longTerm.length > 0 && (
        <section className="rounded-none border border-leaf/15 bg-white p-7 shadow-soft transition-shadow duration-300 hover:shadow-lg">
          <h2 className="mb-5 flex items-center gap-2 text-xl font-semibold text-ink">
            <span className="inline-block h-5 w-1.5 rounded-full bg-leaf" />
            Long-term crop recommendations
          </h2>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {longTerm.map((item) => (
              <div className="rounded-[20px] border border-leaf/10 bg-cream p-4 transition-transform duration-200 hover:-translate-y-0.5" key={item.crop}>
                <div className="mb-3 flex items-center justify-between">
                  <div className="text-sm font-semibold text-leaf">Long-term</div>
                  <div className="rounded-full bg-leaf/10 px-2.5 py-1 text-xs text-leaf">{item.category}</div>
                </div>
                <h3 className="text-lg font-semibold text-ink">
                  {lang === "si" ? `${getCropName(item.crop, "si")} (${item.crop})` : item.crop}
                </h3>
                {/* <p className="mt-2 text-sm leading-6 text-ink/60">{item.notes}</p> */}
                <div className="mt-4 grid grid-cols-1 gap-3">
                  {/* <div className="rounded-xl border border-leaf/10 bg-white p-3">
                    <div className="text-[11px] uppercase tracking-[0.2em] text-ink/40">Harvest days</div>
                    <div className="mt-1 text-sm font-semibold text-ink/80">{item.harvestDays}</div>
                  </div> */}
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
    </div>
  );
}
