import React, { useEffect, useMemo, useRef, useState } from "react";

// Router Dashboard — React Preview (with A/B test + WebSocket progress + Async button)
// Talks to:
//   GET  /health, /engines
//   POST /tts        { text, language, quality, mode: "sync" }
//   POST /abtest     { text, language, quality, engines? }
//   POST /tts_async  { text, language, quality, voice_profile, params }
//   GET  /jobs/:id
// And listens (optionally) to WebSocket progress at ws://<host>:<port>/ws

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

interface ABTestResponse {
  candidates: string[];
  results: Record<string, string>; // engine_id -> b64 wav
}

interface JobStatus {
  id: string;
  status: "queued" | "running" | "done" | "error";
  progress: number;
  engine?: string;
  result_b64_wav?: string;
  error?: string;
}

// ---------- Helpers ----------
const pct = (x: number) => `${Math.round(x * 100)}%`;
const cls = (...parts: Array<string | false | undefined>) => parts.filter(Boolean).join(" ");

function Bar({ value }: { value: number }) {
  return (
    <div className="h-2 w-full rounded bg-gray-200 overflow-hidden">
      <div className="h-2 bg-blue-500" style={{ width: pct(Math.max(0, Math.min(1, value))) }} />
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
  return <span className={cls("px-2 py-0.5 rounded text-xs font-medium", map[tone])}>{children}</span>;
}

function b64ToAudioUrl(b64: string) {
  const b = atob(b64);
  const arr = new Uint8Array(b.length);
  for (let i = 0; i < b.length; i++) arr[i] = b.charCodeAt(i);
  return URL.createObjectURL(new Blob([arr], { type: "audio/wav" }));
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

// ---------- TTS Demo (Sync + Async) ----------
function TTSDemo({ baseUrl }: { baseUrl: string }) {
  const [text, setText] = useState("Hello from VoiceStudio Router");
  const [language, setLanguage] = useState("en");
  const [quality, setQuality] = useState<"fast" | "balanced" | "quality">("balanced");
  const [busy, setBusy] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [result, setResult] = useState<TTSResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);

  const [jobId, setJobId] = useState<string | null>(null);
  const [job, setJob] = useState<JobStatus | null>(null);
  const pollRef = useRef<number | null>(null);

  async function runSync() {
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
      if (js.result_b64_wav) setAudioUrl(b64ToAudioUrl(js.result_b64_wav));
    } catch (e: any) {
      setErr(e.message || String(e));
    } finally {
      setBusy(false);
    }
  }

  async function runAsync() {
    setBusy(true);
    setErr(null);
    setAudioUrl(null);
    setJob(null);
    setJobId(null);
    try {
      const r = await fetch(`${baseUrl}/tts`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ text, language, quality, voice_profile: {}, params: { sample_rate: 22050 }, mode: "async" }),
      });
      if (!r.ok) throw new Error(`/tts -> ${r.status}`);
      const js = (await r.json()) as { job_id: string };
      setJobId(js.job_id);
      // Start polling status every 500ms
      if (pollRef.current) window.clearInterval(pollRef.current);
      pollRef.current = window.setInterval(async () => {
        try {
          const s = await fetch(`${baseUrl}/jobs/${js.job_id}`);
          if (!s.ok) throw new Error(`/jobs/${js.job_id} -> ${s.status}`);
          const st = (await s.json()) as JobStatus;
          setJob(st);
          if (st.status === "done") {
            if (pollRef.current) window.clearInterval(pollRef.current);
            if (st.result_b64_wav) setAudioUrl(b64ToAudioUrl(st.result_b64_wav));
            setBusy(false);
          }
          if (st.status === "error") {
            if (pollRef.current) window.clearInterval(pollRef.current);
            setErr(st.error || "Job failed");
            setBusy(false);
          }
        } catch (e: any) {
          if (pollRef.current) window.clearInterval(pollRef.current);
          setErr(e.message || String(e));
          setBusy(false);
        }
      }, 500);
    } catch (e: any) {
      setErr(e.message || String(e));
      setBusy(false);
    }
  }

  useEffect(() => () => { if (pollRef.current) window.clearInterval(pollRef.current); }, []);

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
          <div className="flex gap-2 mt-3">
            <button onClick={runSync} disabled={busy} className="px-3 py-2 rounded bg-blue-600 text-white disabled:opacity-60">
              {busy ? "Generating…" : "Generate (sync)"}
            </button>
            <button onClick={runAsync} disabled={busy} className="px-3 py-2 rounded bg-indigo-600 text-white disabled:opacity-60">
              {busy ? "Submitting…" : "Generate (async)"}
            </button>
          </div>
        </div>
      </div>

      {jobId && (
        <div className="text-xs text-gray-600">Job: <b>{jobId}</b> · Status: <b>{job?.status || "queued"}</b> · Progress: {pct(job?.progress || 0)}</div>
      )}

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

      {!result && audioUrl && (
        <div className="border rounded p-3 bg-white">
          <div className="text-sm text-gray-700">Async result</div>
          <div className="text-xs text-gray-500 mt-1">From job: {jobId}</div>
          <div className="mt-3">
            <audio controls src={audioUrl} className="w-full" />
          </div>
        </div>
      )}
    </div>
  );
}

// ---------- A/B Test Panel ----------
function ABTestPanel({ baseUrl }: { baseUrl: string }) {
  const [text, setText] = useState("A/B test this line with two engines.");
  const [language, setLanguage] = useState("en");
  const [quality, setQuality] = useState<"fast" | "balanced" | "quality">("balanced");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [candidates, setCandidates] = useState<string[]>([]);
  const [audios, setAudios] = useState<Record<string, string>>({});

  async function run() {
    setBusy(true);
    setErr(null);
    setCandidates([]);
    setAudios({});
    try {
      const r = await fetch(`${baseUrl}/abtest`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ text, language, quality }),
      });
      if (!r.ok) throw new Error(`/abtest -> ${r.status}`);
      const js = (await r.json()) as ABTestResponse;
      setCandidates(js.candidates);
      const urls: Record<string, string> = {};
      Object.entries(js.results || {}).forEach(([engine, b64]) => {
        if (b64 && b64.length > 0) urls[engine] = b64ToAudioUrl(b64);
      });
      setAudios(urls);
    } catch (e: any) {
      setErr(e.message || String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">A/B Test</h2>
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
          <button onClick={run} disabled={busy} className="mt-3 px-3 py-2 rounded bg-indigo-600 text-white disabled:opacity-60">
            {busy ? "Comparing…" : "Run A/B"}
          </button>
        </div>
      </div>

      {err && <div className="text-sm text-red-700 bg-red-50 border border-red-200 rounded p-2">{err}</div>}

      {candidates.length > 0 && (
        <div className="border rounded p-3 bg-white">
          <div className="text-sm text-gray-700 mb-2">Candidates: {candidates.join(" · ")}</div>
          <div className="grid md:grid-cols-2 gap-3">
            {candidates.map((e) => (
              <div key={e} className="border rounded p-2">
                <div className="text-sm font-medium">{e}</div>
                {audios[e] ? (
                  <audio controls src={audios[e]} className="w-full mt-2" />
                ) : (
                  <div className="text-xs text-gray-500 mt-2">No audio returned (engine skipped or failed)</div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ---------- WebSocket Progress (UI) ----------
function ProgressPanel({ baseUrl }: { baseUrl: string }) {
  const [messages, setMessages] = useState<string[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const url = baseUrl.replace(/^http/, "ws") + "/ws";
    let ws: WebSocket | null = null;
    try {
      ws = new WebSocket(url);
      wsRef.current = ws;
      ws.onopen = () => setConnected(true);
      ws.onclose = () => setConnected(false);
      ws.onerror = () => setConnected(false);
      ws.onmessage = (ev) => {
        setMessages((m) => [String(ev.data), ...m].slice(0, 100));
      };
    } catch (e) {
      // If no WS backend yet, stay quiet.
    }
    return () => {
      try { ws?.close(); } catch {}
    };
  }, [baseUrl]);

  return (
    <div className="space-y-2">
      <h2 className="text-lg font-semibold">Progress (WebSocket)</h2>
      <div className="text-sm">Status: {connected ? <Pill tone="good">Connected</Pill> : <Pill tone="warn">Not connected</Pill>}</div>
      <div className="border rounded-lg bg-white p-2 h-48 overflow-auto text-xs font-mono">
        {messages.length === 0 ? (
          <div className="text-gray-500">Waiting for progress events…</div>
        ) : (
          messages.map((m, i) => (
            <div key={i} className="py-0.5">{m}</div>
          ))
        )}
      </div>
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
          <ProgressPanel baseUrl={baseUrl} />
        </div>

        <div className="mt-6">
          <ABTestPanel baseUrl={baseUrl} />
        </div>

        <footer className="pt-6 text-xs text-gray-500">
          Router endpoints: <code>/health</code>, <code>/engines</code>, <code>/tts</code>, <code>/jobs/:id</code>, <code>/abtest</code>. WebSocket: <code>/ws</code>
        </footer>
      </div>
    </div>
  );
}
