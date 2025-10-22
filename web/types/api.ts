// === A/B Summary types (append) ===
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

// Health Metrics Types
export type HealthFFmpeg = {
  present: boolean;
  version?: string | null;
};

export type HealthPostFx = {
  available: boolean;
  ffmpeg_used_by_default: boolean;
};

export type HealthBuild = {
  version?: string | null;
  git_sha?: string | null;
  build_time_utc?: string | null;
};

export interface HealthMetrics {
  metrics_enabled: boolean;
  ffmpeg: HealthFFmpeg;
  ffprobe: HealthFFmpeg;
  postfx: HealthPostFx;
  openapi_version: string;
  build?: HealthBuild | null;
}

// A/B Testing Thresholds
export const ABThresholds = {
  winRate: { good: 0.65, warn: 0.55 },      // green ≥ 65%, amber ≥ 55%, else red
  clipHit: { good: 0.02, warn: 0.10 },      // green ≤ 2%, amber ≤ 10%, else red
};