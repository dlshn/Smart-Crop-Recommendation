import React from "react";

const STEPS = [
  {
    title: "District suitability",
    body: "Candidate crops are filtered by whether they genuinely grow in the selected district, based on Sri Lanka's Wet / Intermediate / Dry agro-climatic zone classification.",
  },
  {
    title: "Price prediction",
    body: "A Random Forest model predicts each surviving crop's market price at harvest time, trained separately per crop on 5 years of district-level price data.",
  },
  {
    title: "Profitability filter",
    body: "Only crops whose predicted price is above their OWN historical average price move forward — each crop is judged against its own baseline, not a shared threshold.",
  },
  {
    title: "Rainfall check",
    body: "Expected rainfall across the growing period is estimated so the result includes a plain-language rainfall outlook, not just a number.",
  },
];

const STACK = [
  { label: "Frontend", value: "React + Vite, Tailwind CSS" },
  { label: "Backend API", value: "Node.js + Express, MongoDB" },
  { label: "ML Service", value: "Python + FastAPI, scikit-learn" },
  { label: "Data", value: "5 years of district-level price & weather records" },
];

export default function About() {
  return (
    <div className="space-y-6">
      <header className="rounded-not border border-leaf/15 bg-white p-7 shadow-soft">
        <p className="mb-2 text-xs font-bold uppercase tracking-[0.16em] text-wheat">About the project</p>
        <h1 className="m-0 mb-3 text-[2rem] font-bold leading-tight tracking-tight text-ink">
          Built to close the gap between data and planting decisions
        </h1>
        <p className="m-0 max-w-2xl leading-relaxed text-ink/60">
          Most crop decisions in Sri Lanka are still made on tradition and intuition rather
          than data. This project brings district suitability, rainfall patterns, and market
          price forecasting together into one recommendation, so a farmer can weigh a real,
          district-specific outlook before choosing what to plant.
        </p>
      </header>

      <section className="rounded-not border border-leaf/15 bg-white p-7 shadow-soft">
        <h2 className="mb-5 flex items-center gap-2 text-xl font-semibold text-ink">
          <span className="inline-block h-5 w-1.5 rounded-full bg-leaf" />
          How a recommendation is built
        </h2>
        <div className="grid gap-4 md:grid-cols-2">
          {STEPS.map((step, i) => (
            <div
              key={step.title}
              className="rounded-[20px] border border-leaf/10 bg-cream p-4 transition-transform duration-200 hover:-translate-y-0.5"
            >
              <div className="mb-2 flex items-center gap-2">
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-leaf/15 text-xs font-bold text-leaf">
                  {i + 1}
                </span>
                <h3 className="text-sm font-semibold text-ink">{step.title}</h3>
              </div>
              <p className="text-sm leading-6 text-ink/60">{step.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="rounded-not border border-leaf/15 bg-white p-7 shadow-soft">
        <h2 className="mb-5 flex items-center gap-2 text-xl font-semibold text-ink">
          <span className="inline-block h-5 w-1.5 rounded-full bg-leaf" />
          Two kinds of recommendations
        </h2>
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-[20px] border border-leaf/10 bg-cream p-4">
            <div className="mb-2 text-sm font-semibold text-leaf">Short-term crops</div>
            <p className="text-sm leading-6 text-ink/60">
              Fast-cycle vegetables run through the full pipeline: district
              suitability, price prediction, the profitability filter, and a
              rainfall outlook — ranked and narrowed to the top 3.
            </p>
          </div>
          <div className="rounded-[20px] border border-leaf/10 bg-cream p-4">
            <div className="mb-2 text-sm font-semibold text-leaf">Long-term crops</div>
            <p className="text-sm leading-6 text-ink/60">
              Perennial fruit trees and vines are listed by district
              suitability alone — a single-season price/rainfall forecast
              doesn't meaningfully apply to a multi-year crop.
            </p>
          </div>
        </div>
      </section>

      {/* <section className="rounded-[24px] border border-leaf/15 bg-white p-7 shadow-soft">
        <h2 className="mb-5 flex items-center gap-2 text-xl font-semibold text-ink">
          <span className="inline-block h-5 w-1.5 rounded-full bg-leaf" />
          Built with
        </h2>
        <div className="grid gap-3 sm:grid-cols-2">
          {STACK.map((item) => (
            <div key={item.label} className="flex items-center justify-between rounded-xl border border-leaf/10 bg-cream px-4 py-3">
              <span className="text-xs font-semibold uppercase tracking-[0.15em] text-ink/40">{item.label}</span>
              <span className="text-sm font-semibold text-ink/80">{item.value}</span>
            </div>
          ))}
        </div>
        <div className="mt-5 flex flex-wrap gap-2">
          <span className="rounded-full border border-leaf/15 bg-cream px-3 py-1 text-sm text-ink/70">District-aware</span>
          <span className="rounded-full border border-leaf/15 bg-cream px-3 py-1 text-sm text-ink/70">Soil-aware</span>
          <span className="rounded-full border border-leaf/15 bg-cream px-3 py-1 text-sm text-ink/70">Price-aware</span>
          <span className="rounded-full border border-leaf/15 bg-cream px-3 py-1 text-sm text-ink/70">Rainfall-aware</span>
        </div>
      </section> */}
    </div>
  );
}
