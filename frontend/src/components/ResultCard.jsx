import React from "react";
import { getCropName } from "../translations";

export default function ResultCard({ result, rank, lang }) {
  const cropDisplay =
    lang === "si"
      ? `${getCropName(result.crop, "si")} (${result.crop})`
      : result.crop;
  const zoneMatch = result && result.zoneMatch ? String(result.zoneMatch) : "Unknown";
  const zoneClass = zoneMatch.toLowerCase();
  const zoneName = result && result.zone ? result.zone : "-";

  const rainfall = typeof result?.predictedRainfallMm === "number" ? result.predictedRainfallMm : null;
  const price = typeof result?.predictedPriceLkr === "number" ? result.predictedPriceLkr : null;

  const risk = typeof result?.riskScore === "number" ? result.riskScore : 0;
  const finalScore = typeof result?.finalScore === "number" ? result.finalScore : 0;

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

        <span className={`inline-flex rounded-full px-3 py-1 text-xs font-medium ${zoneClass === "suitable" ? "bg-leaf/15 text-leaf" : zoneClass === "marginal" ? "bg-amber-100 text-amber-700" : "bg-ink/5 text-ink/40"}`}>
          {zoneMatch} for {zoneName} Zone
        </span>

        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-2xl border border-leaf/10 bg-cream p-3">
            <div className="text-[11px] uppercase tracking-[0.2em] text-ink/40">Rainfall</div>
            <div className="mt-1 text-sm font-semibold text-ink/80">{rainfall !== null ? `${rainfall} mm` : "N/A"}</div>
            <div className="mt-1 text-xs text-ink/40">{result?.rainfallBand ?? result?.rainfallRange ?? "-"}</div>
          </div>
          <div className="rounded-2xl border border-leaf/10 bg-cream p-3">
            <div className="text-[11px] uppercase tracking-[0.2em] text-ink/40">Price</div>
            <div className="mt-1 text-sm font-semibold text-ink/80">{price !== null ? `LKR ${price}` : "N/A"}</div>
          </div>
          <div className="rounded-2xl border border-leaf/10 bg-cream p-3 col-span-2">
            <div className="text-[11px] uppercase tracking-[0.2em] text-ink/40">Soil</div>
            <div className="mt-1 text-sm font-semibold text-ink/80">{Array.isArray(result?.suitableSoilTypes) && result.suitableSoilTypes.length > 0 ? result.suitableSoilTypes.join(", ") : "-"}</div>
          </div>
          <div className="rounded-2xl border border-leaf/10 bg-cream p-3">
            <div className="text-[11px] uppercase tracking-[0.2em] text-ink/40">Risk</div>
            <div className="mt-1 text-sm font-semibold text-ink/80">{risk.toFixed(2)}</div>
          </div>
          <div className="rounded-2xl border border-leaf/20 bg-leaf/10 p-3">
            <div className="text-[11px] uppercase tracking-[0.2em] text-leaf">Score</div>
            <div className="mt-1 text-sm font-semibold text-leaf">{finalScore.toFixed(2)}</div>
          </div>
        </div>
      </div>
    </div>
  );
}
