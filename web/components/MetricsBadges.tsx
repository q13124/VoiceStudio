import React from "react";

// Types for audio metrics
export interface AudioMetrics {
  lufs?: number | null;        // integrated loudness (I)
  lra?: number | null;         // loudness range (optional if backend sends it)
  true_peak?: number | null;   // dBTP (optional)
  clip_pct?: number | null;    // 0..100 (% of clipped samples or flag)
  dc_offset?: number | null;   // %FS (e.g., 0.2 means 0.2%)
  head_ms?: number | null;     // leading silence in ms
  tail_ms?: number | null;     // trailing silence in ms
}

export interface TTSItem {
  id: string;
  engine: string;
  url: string;        // wav url
  metrics?: AudioMetrics; // additive, optional
}

export interface TTSResponse {
  items: TTSItem[];
  engine: string;
  tried_order: string[];
  result_b64_wav?: string;
  job_id?: string;
}

// A/B Testing Types
export type EngineStats = {
  engine: string;
  n_items: number;
  wins: number;
  win_rate: number;            // 0..1
  win_rate_ci95_low?: number | null;
  win_rate_ci95_high?: number | null;
  mean_score?: number | null;  // 0..5
  median_lufs?: number | null;
  clip_hit_rate?: number | null; // 0..1
};

export type ABSummaryResponse = {
  sessionId: string;
  engines: EngineStats[];
  total_items: number;
};

// Metrics thresholds configuration
export const MetricsThresholds = {
  // LUFS target for speech mastering; UI only shows pass/warn (no hard fail)
  lufs: { target: -23.0, warnDelta: 3.0 },        // warn if |I - target| > 3 dB

  clip_pct: { warn: 0.1, fail: 1.0 },             // % clipped samples
  dc_offset: { warn: 0.5, fail: 1.0 },            // %FS
  head_ms: { warn: 120, fail: 250 },              // ms of leading silence
  tail_ms: { warn: 150, fail: 300 },              // ms of trailing silence
};

type BadgeTone = "ok" | "warn" | "fail";

function toneClass(tone: BadgeTone) {
  switch (tone) {
    case "ok": return "bg-green-100 text-green-800 ring-green-300";
    case "warn": return "bg-amber-100 text-amber-800 ring-amber-300";
    case "fail": return "bg-red-100 text-red-800 ring-red-300";
  }
}

function badge(label: string, value: string, tone: BadgeTone, title?: string) {
  return (
    <span
      key={label}
      title={title ?? label}
      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset ${toneClass(tone)}`}
    >
      <span className="opacity-70">{label}</span>
      <span className="font-semibold">{value}</span>
    </span>
  );
}

export function MetricsBadges({ m }: { m?: AudioMetrics }) {
  if (!m) return null;
  const nodes: React.ReactNode[] = [];

  // LUFS (I)
  if (typeof m.lufs === "number") {
    const delta = Math.abs(m.lufs - MetricsThresholds.lufs.target);
    const tone: BadgeTone = delta > MetricsThresholds.lufs.warnDelta ? "warn" : "ok";
    nodes.push(badge("LUFS", `${m.lufs.toFixed(1)}`, tone, `Target ${MetricsThresholds.lufs.target} ±${MetricsThresholds.lufs.warnDelta} dB`));
  }

  // Clipping %
  if (typeof m.clip_pct === "number") {
    const tone: BadgeTone = m.clip_pct >= MetricsThresholds.clip_pct.fail ? "fail" :
                            m.clip_pct >= MetricsThresholds.clip_pct.warn ? "warn" : "ok";
    nodes.push(badge("clip", `${m.clip_pct.toFixed(2)}%`, tone, `Warn ≥${MetricsThresholds.clip_pct.warn}% · Fail ≥${MetricsThresholds.clip_pct.fail}%`));
  }

  // DC offset %
  if (typeof m.dc_offset === "number") {
    const tone: BadgeTone = m.dc_offset >= MetricsThresholds.dc_offset.fail ? "fail" :
                            m.dc_offset >= MetricsThresholds.dc_offset.warn ? "warn" : "ok";
    nodes.push(badge("DC", `${m.dc_offset.toFixed(2)}%`, tone, `Warn ≥${MetricsThresholds.dc_offset.warn}%FS · Fail ≥${MetricsThresholds.dc_offset.fail}%FS`));
  }

  // Head silence ms
  if (typeof m.head_ms === "number") {
    const tone: BadgeTone = m.head_ms >= MetricsThresholds.head_ms.fail ? "fail" :
                            m.head_ms >= MetricsThresholds.head_ms.warn ? "warn" : "ok";
    nodes.push(badge("head", `${m.head_ms}ms`, tone, `Warn ≥${MetricsThresholds.head_ms.warn}ms · Fail ≥${MetricsThresholds.head_ms.fail}ms`));
  }

  // Tail silence ms
  if (typeof m.tail_ms === "number") {
    const tone: BadgeTone = m.tail_ms >= MetricsThresholds.tail_ms.fail ? "fail" :
                            m.tail_ms >= MetricsThresholds.tail_ms.warn ? "warn" : "ok";
    nodes.push(badge("tail", `${m.tail_ms}ms`, tone, `Warn ≥${MetricsThresholds.tail_ms.warn}ms · Fail ≥${MetricsThresholds.tail_ms.fail}ms`));
  }

  // Optional extras if backend supplies them:
  if (typeof m.true_peak === "number") {
    // True peak > -1 dBTP warn, > -0.1 fail (suggested)
    const tone: BadgeTone = m.true_peak > -0.1 ? "fail" : (m.true_peak > -1.0 ? "warn" : "ok");
    nodes.push(badge("TP", `${m.true_peak.toFixed(1)} dBTP`, tone, "Warn > -1.0 dBTP · Fail > -0.1 dBTP"));
  }
  if (typeof m.lra === "number") {
    // LRA guidance (speech often 5–15 dB, purely informational)
    nodes.push(badge("LRA", `${m.lra.toFixed(1)} dB`, "ok", "Informational loudness range"));
  }

  if (!nodes.length) return null;
  return (
    <div className="mt-2 flex flex-wrap gap-1.5">
      {nodes}
    </div>
  );
}

type ClipCardProps = {
  item: TTSItem;
  onPlay?: () => void;
  onSelect?: () => void;
  onRate?: (rating: number) => void;
  isPlaying?: boolean;
  isSelected?: boolean;
};

export function ClipCard({ item, onPlay, onSelect, onRate, isPlaying = false, isSelected = false }: ClipCardProps) {
  return (
    <div className={`rounded-2xl border p-3 shadow-sm transition-all ${
      isSelected 
        ? 'border-blue-300 bg-blue-50' 
        : 'border-zinc-200 bg-white hover:border-zinc-300'
    }`}>
      <div className="flex items-center justify-between gap-2">
        <div className="min-w-0">
          <div className="truncate text-sm font-semibold text-zinc-900">
            {item.engine.toUpperCase()} Engine
          </div>
          <div className="mt-1 text-xs text-zinc-500">
            ID: {item.id}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={onPlay}
            className={`rounded-full p-2 transition-colors ${
              isPlaying 
                ? 'bg-red-100 text-red-600 hover:bg-red-200' 
                : 'bg-green-100 text-green-600 hover:bg-green-200'
            }`}
            title={isPlaying ? 'Stop' : 'Play'}
          >
            {isPlaying ? '⏹' : '▶'}
          </button>
          <button
            onClick={onSelect}
            className={`rounded-full p-2 transition-colors ${
              isSelected 
                ? 'bg-blue-100 text-blue-600' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
            title="Select this clip"
          >
            ✓
          </button>
        </div>
      </div>

      {/* Audio metrics badges */}
      <MetricsBadges m={item.metrics} />

      {/* Audio player controls */}
      <div className="mt-3">
        <div className="flex items-center gap-2">
          <audio 
            src={item.url} 
            controls 
            className="flex-1"
            onPlay={() => onPlay?.()}
            onPause={() => onPlay?.()}
          />
          <div className="flex gap-1">
            {[1, 2, 3, 4, 5].map((rating) => (
              <button
                key={rating}
                onClick={() => onRate?.(rating)}
                className="text-lg hover:text-yellow-500 transition-colors"
                title={`Rate ${rating} stars`}
              >
                ⭐
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}