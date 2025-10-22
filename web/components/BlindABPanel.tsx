import React from "react";
import { postABSummary } from "../api/ab";
import { AbSummaryCard } from "../components/AbSummaryCard";
import { ABSummaryResponse, ABRating } from "../types/api";

export function BlindABPanel({ apiBase, sessionId, ratings }: {
  apiBase: string;
  sessionId: string;
  ratings: ABRating[];
}) {
  const [summary, setSummary] = React.useState<ABSummaryResponse | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [err, setErr] = React.useState<string | null>(null);

  async function finalizeRound() {
    try {
      setLoading(true);
      setErr(null);
      const res = await postABSummary(apiBase, { sessionId, ratings });
      setSummary(res);
    } catch (e: any) {
      setErr(e?.message ?? "Summary failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-3">
      {/* ... your existing candidate list / controls ... */}

      <div className="flex items-center gap-2">
        <button
          onClick={finalizeRound}
          className="rounded-xl bg-zinc-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-zinc-800 disabled:opacity-50"
          disabled={loading || ratings.length === 0}
        >
          {loading ? "Summarizing…" : "Summarize A/B"}
        </button>
        {err && <div className="text-xs text-red-600">{err}</div>}
      </div>

      {summary && <AbSummaryCard data={summary} />}
    </div>
  );
}
