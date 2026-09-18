import React from "react";

function todayIsoDate() {
  const now = new Date();
  const yyyy = now.getFullYear();
  const mm = String(now.getMonth() + 1).padStart(2, "0");
  const dd = String(now.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

export default function RecommendationForm({
  districts, crops, district, setDistrict, plantingDate, setPlantingDate,
  selectedCrops, setSelectedCrops, lang, setLang, onSubmit, loading,
}) {
  const toggleCrop = (crop) => {
    setSelectedCrops((prev) =>
      prev.includes(crop) ? prev.filter((c) => c !== crop) : [...prev, crop]
    );
  };

  return (
    <form
      className="rounded-none border border-leaf/15 bg-white p-7 shadow-soft transition-shadow duration-300 hover:shadow-lg"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit();
      }}
    >
      <h2 className="mb-5 flex items-center gap-2 text-xl font-semibold text-ink">
        <span className="inline-block h-5 w-1.5 rounded-full bg-leaf" />
        {lang === "si" ? "ඔබේ නිර්දේශය ලබාගන්න " : "Build your recommendation"}
      </h2>

      <div className="grid gap-4 md:grid-cols-3">
        <label className="flex flex-col gap-2 text-sm text-ink/60">
          <span className="text-ink/70">{lang === "si" ? "දිස්ත්‍රික්කය" : "District / දිස්ත්‍රික්කය"}</span>
          <select
            className="rounded-2xl border border-leaf/15 bg-cream px-3 py-2.5 text-ink outline-none transition-colors focus:border-leaf focus:ring-2 focus:ring-leaf/20"
            value={district}
            onChange={(e) => setDistrict(e.target.value)}
          >
            {districts.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-2 text-sm text-ink/60">
          <span className="text-ink/70">{lang === "si" ? "සිටුවන දිනය" : "Planting date / සිටුවන දිනය"}</span>
          <input
            type="date"
            className="rounded-2xl border border-leaf/15 bg-cream px-3 py-2.5 text-ink outline-none transition-colors focus:border-leaf focus:ring-2 focus:ring-leaf/20"
            value={plantingDate}
            min={todayIsoDate()}
            onChange={(e) => setPlantingDate(e.target.value)}
          />
        </label>

        <label className="flex flex-col gap-2 text-sm text-ink/60">
          <span className="text-ink/70">{lang === "si" ? "භාෂාව" : "Language / භාෂාව"}</span>
          <select
            className="rounded-2xl border border-leaf/15 bg-cream px-3 py-2.5 text-ink outline-none transition-colors focus:border-leaf focus:ring-2 focus:ring-leaf/20"
            value={lang}
            onChange={(e) => setLang(e.target.value)}
          >
            <option value="en">English</option>
            <option value="si">සිංහල</option>
          </select>
        </label>
      </div>

      <div className="mt-7">
        <span className="text-sm font-medium text-ink/70">
          {lang === "si" ? "අපේක්ෂිත බෝග (සියලු බෝග බලාපොරොත්තු වන්නේ නම් හිස්ව තබන්න)" : "Candidate crops (leave empty to consider all crops)"}
        </span>
        <p className="mt-1 text-sm text-ink/40">
          {lang === "si"
            ? "සාපේක්ෂා කිරීමට කුඩා බෝග කිහිපයක් තෝරන්න හෝ පුළුල් දර්ශනයක් සඳහා තේරීම හිස්ව තබන්න."
            : "Choose a few crops to compare or leave the selection open for a broader view."}
        </p>
        <div className="mt-3 flex flex-wrap gap-2">
          {crops.map((c) => (
            <button
              type="button"
              key={c}
              className={`rounded-xl  border px-3 py-2 text-sm transition ${selectedCrops.includes(c)
                ? "border-leaf bg-leaf text-white shadow-sm"
                : "border-leaf/15 bg-cream text-ink/70 hover:border-leaf/40 hover:text-leaf"}`}
              onClick={() => toggleCrop(c)}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      <button
        type="submit"
        className="mt-7 rounded-full bg-leaf px-5 py-2.5 font-semibold text-white shadow-sm transition hover:-translate-y-0.5 hover:bg-leaf-dark hover:shadow-md disabled:cursor-not-allowed disabled:translate-y-0 disabled:opacity-70 disabled:shadow-none"
        disabled={loading}
      >
        {loading
          ? lang === "si" ? "රැදීසිටින්න  ..." : "Analyzing your options..."
          : lang === "si" ? "නිර්දේශ ලබාදෙන්න" : "Generate Recommendations"}
      </button>
    </form>
  );
}
