import { ABSummaryResponse } from "../types/api";

export async function postABSummary(
  baseUrl: string,
  payload: { sessionId: string; ratings: any[] }
): Promise<ABSummaryResponse> {
  const r = await fetch(`${baseUrl.replace(/\/$/, "")}/v1/ab/summary`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error(`A/B summary failed: ${r.status}`);
  return r.json();
}
