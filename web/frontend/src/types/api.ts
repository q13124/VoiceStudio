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
