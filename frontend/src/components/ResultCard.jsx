import React from "react";
import { getCropName } from "../translations";

export default function ResultCard({ result, rank, lang }) {
  const cropDisplay =
    lang === "si"
      ? `${getCropName(result.crop, "si")} (${result.crop})`
      : result.crop;

  return (
    <div className="result-card">
      <div className="result-rank">#{rank}</div>
      <div className="result-body">
        <h3>{cropDisplay}</h3>
        <span className={`badge badge-${result.zoneMatch.toLowerCase()}`}>
          {result.zoneMatch} for {result.zone} Zone
        </span>

        <div className="metric-grid">
          <div className="metric">
            <span className="metric-label">Rainfall</span>
            <span className="metric-value">{result.predictedRainfallMm} mm</span>
            <span className="metric-sub">{result.rainfallBand}</span>
          </div>
          <div className="metric">
            <span className="metric-label">Price</span>
            <span className="metric-value">LKR {result.predictedPriceLkr}</span>
          </div>
          <div className="metric">
            <span className="metric-label">Risk (higher = safer)</span>
            <span className="metric-value">{result.riskScore.toFixed(2)}</span>
          </div>
          <div className="metric metric-highlight">
            <span className="metric-label">Overall Score</span>
            <span className="metric-value">{result.finalScore.toFixed(2)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
