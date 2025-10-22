import React, { useEffect, useMemo, useState } from "react";

// Minimal, dependency‑free dashboard preview that talks to:
//   GET  /health, /engines
//   POST /tts  { text, language, quality, mode: "sync" }
// Drop-in ready for Vite (React + TS). Also works in the canvas preview.

// ---------- Types ----------
interface EngineInfo {
  healthy: boolean;
  load: number; // 0..1
  languages: string[];
  quality: ("fast" | "balanced" | "quality")[];
}

interface HealthResponse {
  ok: boolean;
  engines: Record<string, EngineInfo>;
}

interface TTSResponse {
  engine: string;
  tried_order: string[];
  result_b64_wav?: string;
  job_id?: string;
}

// ---------- Helpers ----------
const pct = (x: number) => `${Math.round(x * 100)}%`;
const cls = (...parts: Array<string | false | undefined>) => parts.filter(Boolean).join(" ");

function Bar({ value }: { value: number }) {
  return (
    <div className="h-2 w-full rounded bg-gray-200 overflow-hidden">
      <div
        className="h-2 bg-blue-500"
        style={{ width: pct(Math.max(0, Math.min(1, value))) }}
      />
    </div>
  );
}

function Pill({ children, tone = "default" as "default" | "good" | "bad" | "warn" }) {
  const map: Record<string, string> = {
    default: "bg-gray-100 text-gray-700",
    good: "bg-green-100 text-green-800",
    bad: "bg-red-100 text-red-800",
    warn: "bg-amber-100 text-amber-800",
  };
  return (
    <span className={cls("px-2 py-0.5 rounded text-xs font-medium", map[tone])}>{children}</span>
  );
}

// ---------- Engine Status Grid ----------
function EngineStatusGrid({ baseUrl }: { baseUrl: string }) {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const r = await fetch(`${baseUrl}/health`);
      if (!r.ok) throw new Error(`/health -> ${r.status}`);
      const js = (await r.json()) as HealthResponse;
      setHealth(js);
    } catch (e: any) {
      setError(e.message || String(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const id = setInterval(load, 5000);
    return () => clearInterval(id);
  }, [baseUrl]);

  const engines = useMemo(() => Object.entries(health?.engines || {}), [health]);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Engines</h2>
        <button onClick={load} className="px-3 py-1.5 text-sm rounded bg-gray-900 text-white disabled:opacity-60" disabled={loading}>
          {loading ? "Refreshing…" : "Refresh"}
        </button>
      </div>

      {error && <div className="text-sm text-red-700 bg-red-50 border border-red-200 rounded p-2">{error}</div>}

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
        {engines.map(([id, info]) => (
          <div key={id} className="border rounded-lg p-3 bg-white shadow-sm">
            <div className="flex items-center justify-between gap-2">
              <div className="font-medium">{id}</div>
              {info.healthy ? <Pill tone="good">Healthy</Pill> : <Pill tone="bad">Down</Pill>}
            </div>
            <div className="mt-2 text-xs text-gray-600">Load</div>
            <Bar value={info.load} />
            <div className="mt-2 text-xs text-gray-600">Languages</div>
            <div className="mt-1 flex flex-wrap gap-1">
              {info.languages.slice(0, 12).map((l) => (
                <Pill key={l}>{l}</Pill>
              ))}
            </div>
            <div className="mt-2 text-xs text-gray-600">Tiers</div>
            <div className="mt-1 flex gap-1">
              {info.quality.map((q) => (
                <Pill key={q}>{q}</Pill>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ---------- TTS Demo ----------
function TTSDemo({ baseUrl }: { baseUrl: string }) {
  const [text, setText] = useState("Hello from VoiceStudio Router");
  const [language, setLanguage] = useState("en");
  const [quality, setQuality] = useState<"fast" | "balanced" | "quality">("balanced");
  const [busy, setBusy] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [result, setResult] = useState<TTSResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);

  async function run() {
    setBusy(true);
    setErr(null);
    setAudioUrl(null);
    try {
      const r = await fetch(`${baseUrl}/tts`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ text, language, quality, voice_profile: {}, params: { sample_rate: 22050 }, mode: "sync" }),
      });
      if (!r.ok) throw new Error(`/tts -> ${r.status}`);
      const js = (await r.json()) as TTSResponse;
      setResult(js);
      if (js.result_b64_wav) {
        const b = atob(js.result_b64_wav);
        const arr = new Uint8Array(b.length);
        for (let i = 0; i < b.length; i++) arr[i] = b.charCodeAt(i);
        const url = URL.createObjectURL(new Blob([arr], { type: "audio/wav" }));
        setAudioUrl(url);
      }
    } catch (e: any) {
      setErr(e.message || String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">Quick TTS</h2>

      <div className="grid gap-3 md:grid-cols-2">
        <div className="space-y-2">
          <label className="text-sm font-medium">Text</label>
          <textarea className="w-full border rounded p-2 min-h-[96px]" value={text} onChange={(e) => setText(e.target.value)} />
        </div>
        <div className="grid gap-2 content-start">
          <label className="text-sm font-medium">Language</label>
          <input className="border rounded p-2" value={language} onChange={(e) => setLanguage(e.target.value)} />
          <label className="text-sm font-medium mt-2">Quality</label>
          <select className="border rounded p-2" value={quality} onChange={(e) => setQuality(e.target.value as any)}>
            <option value="fast">fast</option>
            <option value="balanced">balanced</option>
            <option value="quality">quality</option>
          </select>
          <button onClick={run} disabled={busy} className="mt-3 px-3 py-2 rounded bg-blue-600 text-white disabled:opacity-60">
            {busy ? "Generating…" : "Generate"}
          </button>
        </div>
      </div>

      {err && <div className="text-sm text-red-700 bg-red-50 border border-red-200 rounded p-2">{err}</div>}

      {result && (
        <div className="border rounded p-3 bg-white">
          <div className="text-sm text-gray-700">Engine: <b>{result.engine}</b></div>
          <div className="text-xs text-gray-500 mt-1">Tried: {result.tried_order?.join(" → ")}</div>
          {audioUrl && (
            <div className="mt-3">
              <audio controls src={audioUrl} className="w-full" />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ---------- App Shell ----------
export default function App() {
  const [baseUrl, setBaseUrl] = useState("http://127.0.0.1:5090");

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <div className="max-w-6xl mx-auto p-4 md:p-8 space-y-6">
        <header className="flex items-center justify-between">
          <h1 className="text-2xl md:text-3xl font-bold">VoiceStudio — Router Dashboard</h1>
          <div className="flex items-center gap-2">
            <input
              className="border rounded px-2 py-1 text-sm w-[260px]"
              value={baseUrl}
              onChange={(e) => setBaseUrl(e.target.value)}
              title="Router base URL"
            />
            <Pill>Base: {baseUrl}</Pill>
          </div>
        </header>

        <EngineStatusGrid baseUrl={baseUrl} />

        <div className="grid lg:grid-cols-2 gap-6">
          <TTSDemo baseUrl={baseUrl} />
          <div className="space-y-3">
            <h2 className="text-lg font-semibold">Queue (placeholder)</h2>
            <div className="border rounded-lg p-3 bg-white text-sm text-gray-600">
              WebSocket progress will appear here once async jobs are enabled.
            </div>
          </div>
        </div>

        <footer className="pt-6 text-xs text-gray-500">
          Router endpoints: <code>/health</code>, <code>/engines</code>, <code>/tts</code>, <code>/abtest</code>
        </footer>
      </div>
    </div>
  );
}
