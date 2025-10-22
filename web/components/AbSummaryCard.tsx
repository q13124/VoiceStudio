import React from "react";
import { ABSummaryResponse } from "../types/api";
import { CiBar } from "./CiBar";
import { toneWinRate, toneClipRate, toneClass } from "../lib/scoreColor";

const pct = (x?: number | null) => (x == null ? "–" : `${(x * 100).toFixed(1)}%`);

export function AbSummaryCard({ data }: { data: ABSummaryResponse }) {
  const rows = [...data.engines].sort((a, b) =>
    b.win_rate !== a.win_rate ? b.win_rate - a.win_rate : (b.mean_score ?? 0) - (a.mean_score ?? 0)
  );

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white shadow-sm">
      <div className="flex items-center justify-between px-4 py-3">
        <div>
          <h3 className="text-sm font-semibold text-zinc-900">A/B Results</h3>
          <p className="text-xs text-zinc-500">Session {data.sessionId} • {data.total_items} samples</p>
        </div>
      </div>

      <div className="divide-y divide-zinc-100">
        {rows.map(e => {
          const wrTone = toneWinRate(e.win_rate);
          const chTone = toneClipRate(e.clip_hit_rate ?? undefined);
          return (
            <div key={e.engine} className="px-4 py-3">
              <div className="grid grid-cols-[1fr,auto] items-center gap-3">
                <div className="min-w-0">
                  <div className="truncate text-sm font-medium text-zinc-900">{e.engine}</div>
                  <div className="mt-0.5 text-xs text-zinc-500">{e.n_items} items • {e.wins} wins</div>
                  <div className="mt-2 flex items-center gap-2">
                    <CiBar point={e.win_rate} lo={e.win_rate_ci95_low} hi={e.win_rate_ci95_high} />
                    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset ${toneClass(wrTone)}`}>
                      WR {pct(e.win_rate)}
                    </span>
                  </div>
                </div>

                <div className="flex flex-col items-end gap-1">
                  <span className="inline-flex items-center rounded-full bg-zinc-100 px-2 py-0.5 text-xs font-medium ring-1 ring-inset ring-zinc-200">
                    μ {e.mean_score != null ? e.mean_score.toFixed(2) : "–"}
                  </span>
                  <span className="inline-flex items-center rounded-full bg-zinc-100 px-2 py-0.5 text-xs font-medium ring-1 ring-inset ring-zinc-200">
                    LUFS {e.median_lufs != null ? e.median_lufs.toFixed(1) : "–"}
                  </span>
                  <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset ${toneClass(chTone)}`}>
                    clip {pct(e.clip_hit_rate ?? null)}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="px-4 py-3 text-xs text-zinc-500">
        WR = win rate, CI = Wilson 95% interval. LUFS/clip are objective; scores are user ratings.
      </div>
    </div>
  );
}