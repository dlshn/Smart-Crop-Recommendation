import React from "react";

export default function GrowingPeriodRainfallChart({ breakdown }) {
  if (!Array.isArray(breakdown) || breakdown.length === 0) return null;

  const width = 220;
  const height = 90;
  const paddingTop = 14;
  const paddingBottom = 16;
  const chartHeight = height - paddingTop - paddingBottom;

  const maxValue = Math.max(...breakdown.map((b) => b.rainfall), 1);
  const barGap = 4;
  const n = breakdown.length;
  const barWidth = width / n - barGap;

  return (
    <div>
      <div className="mb-1 text-[11px] uppercase tracking-[0.2em] text-ink/40">Rainfall within growing period</div>
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full" role="img" aria-label="Rainfall forecast over the growing period">
        {breakdown.map((b, i) => {
          const x = i * (barWidth + barGap) + barGap / 2;
          const barHeight = (b.rainfall / maxValue) * chartHeight;
          const y = paddingTop + (chartHeight - barHeight);
          return (
            <g key={b.label + "-" + i}>
              <text
                x={x + barWidth / 2}
                y={Math.max(y - 3, 9)}
                textAnchor="middle"
                fontSize="8"
                className="fill-ink/60 font-semibold"
              >
                {Math.round(b.rainfall)}
              </text>
              <rect x={x} y={y} width={Math.max(barWidth, 1)} height={Math.max(barHeight, 1)} rx="2" className="fill-leaf/60">
                <title>{`${b.label}: ${b.rainfall} mm`}</title>
              </rect>
              <text
                x={x + barWidth / 2}
                y={height - 4}
                textAnchor="middle"
                fontSize="8"
                className="fill-ink/40"
              >
                {b.label.split(" ")[0]}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
