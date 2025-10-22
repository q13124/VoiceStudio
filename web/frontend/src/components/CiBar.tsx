import React from "react";

export function CiBar({
  point, lo, hi,
}: { point: number; lo?: number | null; hi?: number | null }) {
  const clamp = (v: number) => Math.max(0, Math.min(1, v));
  const p = clamp(point);
  const l = clamp(lo ?? p);
  const h = clamp(hi ?? p);
  const pct = (v: number) => `${(v * 100).toFixed(3)}%`;

  return (
    <div className="relative h-2 w-48 rounded bg-zinc-200">
      <div className="absolute top-0 bottom-0 bg-zinc-400/60" style={{ left: pct(l), right: pct(1 - h) }} />
      <div className="absolute top-[-2px] h-[10px] w-[1%] rounded-sm bg-zinc-900" style={{ left: pct(Math.min(0.99, p)) }} />
    </div>
  );
}
