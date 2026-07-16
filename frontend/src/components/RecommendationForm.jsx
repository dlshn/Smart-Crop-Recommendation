import React from "react";

const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

export default function RecommendationForm({
  districts, crops, district, setDistrict, month, setMonth,
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
        Build your recommendation
      </h2>

      <div className="grid gap-4 md:grid-cols-3">
        <label className="flex flex-col gap-2 text-sm text-ink/60">
          <span className="text-ink/70">District</span>
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
          <span className="text-ink/70">Month</span>
          <select
            className="rounded-2xl border border-leaf/15 bg-cream px-3 py-2.5 text-ink outline-none transition-colors focus:border-leaf focus:ring-2 focus:ring-leaf/20"
            value={month}
            onChange={(e) => setMonth(Number(e.target.value))}
          >
            {MONTHS.map((m, i) => (
              <option key={m} value={i + 1}>{m}</option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-2 text-sm text-ink/60">
          <span className="text-ink/70">Language / භාෂාව</span>
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
          Candidate crops (leave empty to consider all crops)
        </span>
        <p className="mt-1 text-sm text-ink/40">Choose a few crops to compare or leave the selection open for a broader view.</p>
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
        {loading ? "Analyzing your options..." : "Generate Recommendations"}
      </button>
    </form>
  );
}
