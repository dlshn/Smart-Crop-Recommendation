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
      className="rec-form"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit();
      }}
    >
      <div className="form-row">
        <label>
          District
          <select value={district} onChange={(e) => setDistrict(e.target.value)}>
            {districts.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
        </label>

        <label>
          Month
          <select value={month} onChange={(e) => setMonth(Number(e.target.value))}>
            {MONTHS.map((m, i) => (
              <option key={m} value={i + 1}>{m}</option>
            ))}
          </select>
        </label>

        <label>
          Language / භාෂාව
          <select value={lang} onChange={(e) => setLang(e.target.value)}>
            <option value="en">English</option>
            <option value="si">සිංහල</option>
          </select>
        </label>
      </div>

      <div className="crop-picker">
        <span className="crop-picker-label">
          Candidate crops (leave empty to consider all {crops.length})
        </span>
        <div className="crop-chips">
          {crops.map((c) => (
            <button
              type="button"
              key={c}
              className={`chip ${selectedCrops.includes(c) ? "chip-selected" : ""}`}
              onClick={() => toggleCrop(c)}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      <button type="submit" className="submit-btn" disabled={loading}>
        {loading ? "Analyzing..." : "Get Recommendations"}
      </button>
    </form>
  );
}
