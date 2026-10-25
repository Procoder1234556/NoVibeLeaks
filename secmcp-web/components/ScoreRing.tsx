"use client";

type ScoreRingProps = {
  score: number;
  grade: string;
  size?: number;
};

function ringColor(grade: string): string {
  if (grade === "A") return "#34d399";
  if (grade === "B") return "#2dd4bf";
  if (grade === "C") return "#fbbf24";
  return "#f87171";
}

export function ScoreRing({ score, grade, size = 140 }: ScoreRingProps) {
  const stroke = 10;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.max(0, Math.min(100, score));
  const offset = circumference - (clamped / 100) * circumference;
  const color = ringColor(grade);

  return (
    <div
      className="relative inline-flex items-center justify-center"
      style={{ width: size, height: size }}
      role="img"
      aria-label={`Security score ${clamped} out of 100, grade ${grade}`}
    >
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#1e293b"
          strokeWidth={stroke}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-[stroke-dashoffset] duration-700 ease-out"
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-3xl font-bold tabular-nums text-white">{clamped}</span>
        <span className="text-xs font-medium uppercase tracking-wide text-slate-400">
          {grade}
        </span>
      </div>
    </div>
  );
}
