import React from "react";
import { getCropName } from "../translations";

export default function ResultCard({ result, rank, lang }) {
  const cropDisplay =
    lang === "si"
      ? `${getCropName(result.crop, "si")} (${result.crop})`
      : result.crop;

  const price = typeof result?.predictedPriceLkr === "number" ? result.predictedPriceLkr : null;
  const soils =
    Array.isArray(result?.suitableSoilTypes) && result.suitableSoilTypes.length > 0
      ? result.suitableSoilTypes.join(", ")
      : "-";

  return (
    <div className="relative rounded-[22px] border border-leaf/10 bg-white p-4 shadow-soft transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg">
      <div className="absolute -left-2 -top-2 flex h-8 w-8 items-center justify-center rounded-full bg-leaf text-sm font-semibold text-white shadow-sm">
        #{rank}
      </div>
      <div className="space-y-3">
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-lg font-semibold text-ink">{cropDisplay || result?.crop || "Unknown crop"}</h3>
          <span className="text-lg">🌿</span>
        </div>

        <div className="rounded-2xl border border-leaf/10 bg-cream p-3">
          <div className="text-[11px] uppercase tracking-[0.2em] text-ink/40">Predicted price</div>
          <div className="mt-1 text-sm font-semibold text-ink/80">{price !== null ? `LKR ${price}` : "N/A"}</div>
        </div>

        <div className="rounded-2xl border border-leaf/10 bg-cream p-3">
          <div className="text-[11px] uppercase tracking-[0.2em] text-ink/40">Suitable soil type</div>
          <div className="mt-1 text-sm font-semibold text-ink/80">{soils}</div>
        </div>

        <div className="rounded-2xl border border-leaf/10 bg-cream p-3">
          <div className="text-[11px] uppercase tracking-[0.2em] text-ink/40">Rainfall idea within growing period</div>
          <div className="mt-1 text-sm font-semibold text-ink/80">{result?.rainfallIdea ?? "-"}</div>
        </div>
      </div>
    </div>
  );
}
