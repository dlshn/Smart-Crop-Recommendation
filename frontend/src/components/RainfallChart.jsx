import React from "react";
import { t } from "../translations";

export default function RainfallChart({ trend, district, lang = "en" }) {
  if (!Array.isArray(trend) || trend.length === 0) return null;

  const width = 640;
  const height = 240;
  const paddingLeft = 40;
  const paddingBottom = 30;
  const paddingTop = 12;
  const chartWidth = width - paddingLeft - 12;
  const chartHeight = height - paddingTop - paddingBottom;

  const maxValue = Math.max(...trend.map((t) => t.upper ?? t.rainfall), 1);
  const barGap = 6;
  const n = trend.length;
  const barWidth = chartWidth / n - barGap;

  const yTicks = 4;
  const tickValues = Array.from({ length: yTicks + 1 }, (_, i) => Math.round((maxValue / yTicks) * i));

  const yFor = (v) => paddingTop + chartHeight - (v / maxValue) * chartHeight;

  return (
    <div className="rounded-2xl border border-leaf/10 bg-cream p-4">
      <div className="mb-2 flex items-center justify-between">
        <div className="text-[11px] uppercase tracking-[0.2em] text-ink/40">
          {t("rainfallForecastTitle", lang)} <span className="font-bold text-ink/70">{district}</span>
        </div>
        <div className="text-[11px] text-ink/40">mm / 30-day period</div>
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full" role="img" aria-label={`Forecast rainfall for the next 12 months in ${district}`}>
        {tickValues.map((v, i) => {
          const y = yFor(v);
          return (
            <g key={v + "-" + i}>
              <line x1={paddingLeft} y1={y} x2={width - 8} y2={y} stroke="currentColor" className="text-leaf/10" strokeWidth="1" />
              <text x={paddingLeft - 6} y={y + 3} textAnchor="end" fontSize="10" className="fill-ink/40">
                {v}
              </text>
            </g>
          );
        })}

        {trend.map((t, i) => {
          const x = paddingLeft + i * (barWidth + barGap) + barGap / 2;
          const barHeight = (t.rainfall / maxValue) * chartHeight;
          const y = paddingTop + chartHeight - barHeight;
          const isFirst = i === 0;

          const hasBand = typeof t.lower === "number" && typeof t.upper === "number" && t.upper > t.lower;
          const bandY = hasBand ? yFor(t.upper) : null;
          const bandHeight = hasBand ? yFor(t.lower) - yFor(t.upper) : 0;

          return (
            <g key={t.label + "-" + i}>
              {hasBand && (
                <rect
                  x={x}
                  y={bandY}
                  width={barWidth}
                  height={Math.max(bandHeight, 0)}
                  rx="3"
                  className="fill-leaf/10"
                />
              )}
              <rect
                x={x}
                y={y}
                width={barWidth}
                height={Math.max(barHeight, 1)}
                rx="3"
                className={isFirst ? "fill-leaf" : "fill-leaf/50"}
              >
                <title>
                  {`${t.label}: ${t.rainfall} mm`}
                  {hasBand ? ` (range ${t.lower}-${t.upper} mm)` : ""}
                </title>
              </rect>
              <text
                x={x + barWidth / 2}
                y={height - paddingBottom + 14}
                textAnchor="middle"
                fontSize="9"
                className={isFirst ? "fill-leaf font-semibold" : "fill-ink/50"}
              >
                {t.label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
