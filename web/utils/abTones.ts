import { ABThresholds as T } from "../config/abThresholds";

export function toneWinRate(x?: number | null): "ok" | "warn" | "fail" {
  if (x == null) return "warn";
  if (x >= T.winRate.good) return "ok";
  if (x >= T.winRate.warn) return "warn";
  return "fail";
}

export function toneClipRate(x?: number | null): "ok" | "warn" | "fail" {
  if (x == null) return "warn";
  if (x <= T.clipHit.good) return "ok";
  if (x <= T.clipHit.warn) return "warn";
  return "fail";
}

export function toneClass(t: "ok" | "warn" | "fail"): string {
  switch (t) {
    case "ok":   return "bg-green-100 text-green-800 ring-green-300";
    case "warn": return "bg-amber-100 text-amber-800 ring-amber-300";
    default:     return "bg-red-100 text-red-800 ring-red-300";
  }
}
