import React, { useEffect, useRef, useState } from 'react';
import './App.css';

interface Engine {
  id: string;
  healthy: boolean;
  load: number;
  languages: string[];
  quality: string[];
}

interface AudioMetrics {
  lufs?: number | null;        // integrated loudness (I)
  lra?: number | null;         // loudness range (optional if backend sends it)
  true_peak?: number | null;   // dBTP (optional)
  clip_pct?: number | null;    // 0..100 (% of clipped samples or flag)
  dc_offset?: number | null;   // %FS (e.g., 0.2 means 0.2%)
  head_ms?: number | null;     // leading silence in ms
  tail_ms?: number | null;     // trailing silence in ms
}

interface TTSItem {
  id: string;
  engine: string;
  url: string;        // wav url
  metrics?: AudioMetrics; // additive, optional
}

interface TTSResponse {
  items: TTSItem[];
  // existing fields...
}

interface Job {
  id: string;
  status: string;
  progress: number;
  engine?: string;
  result_b64_wav?: string;
  error?: string;
  metrics?: AudioMetrics;  // New: audio metrics
}

interface TTSItem {
  id: string;
  engine: string;
  url: string;        // wav url
  metrics?: AudioMetrics; // additive, optional
}

interface BlindABTest {
  session_id: string;
  trial_id: string;
  items: TTSItem[];
  shuffled: boolean;
}

function App() {
  const [engines, setEngines] = useState<Engine[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [wsConnected, setWsConnected] = useState(false);
  const [text, setText] = useState('Hello VoiceStudio!');
  const [language, setLanguage] = useState('en');
  const [quality, setQuality] = useState('balanced');
  const [mode, setMode] = useState<'sync' | 'async'>('sync');
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [audioMetrics, setAudioMetrics] = useState<AudioMetrics | null>(null);  // New: store audio metrics
  const [blindTest, setBlindTest] = useState<BlindABTest | null>(null);
  const [ratings, setRatings] = useState({ a: 3, b: 3, winner: 'tie' });
  const [summary, setSummary] = useState<any>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const baseUrl = 'http://127.0.0.1:5090';

  // Audio quality badge component
  const AudioQualityBadges = ({ metrics }: { metrics?: AudioMetrics }) => {
    if (!metrics) return null;

    const getBadgeColor = (value: number, thresholds: { good: number; warning: number }) => {
      if (value <= thresholds.good) return '#22c55e'; // green
      if (value <= thresholds.warning) return '#f59e0b'; // yellow
      return '#ef4444'; // red
    };

    const formatValue = (value: number | undefined, unit: string, decimals: number = 1) => {
      if (value === undefined || value === null) return null;
      return `${value.toFixed(decimals)}${unit}`;
    };

    return (
      <div className="audio-quality-badges">
        {metrics.lufs !== undefined && (
          <span
            className="quality-badge"
            style={{
              backgroundColor: getBadgeColor(Math.abs(metrics.lufs), { good: 16, warning: 20 }),
              color: 'white',
              padding: '2px 6px',
              borderRadius: '4px',
              fontSize: '12px',
              margin: '2px'
            }}
            title={`LUFS: ${metrics.lufs.toFixed(1)} dB`}
          >
            LUFS: {formatValue(metrics.lufs, 'dB')}
          </span>
        )}

        {metrics.clipping_percent !== undefined && (
          <span
            className="quality-badge"
            style={{
              backgroundColor: getBadgeColor(100 - metrics.clipping_percent, { good: 99, warning: 95 }),
              color: 'white',
              padding: '2px 6px',
              borderRadius: '4px',
              fontSize: '12px',
              margin: '2px'
            }}
            title={`Clipping: ${metrics.clipping_percent.toFixed(2)}%`}
          >
            Clip: {formatValue(metrics.clipping_percent, '%', 2)}
          </span>
        )}

        {metrics.dc_offset !== undefined && (
          <span
            className="quality-badge"
            style={{
              backgroundColor: getBadgeColor(100 + metrics.dc_offset, { good: 60, warning: 40 }),
              color: 'white',
              padding: '2px 6px',
              borderRadius: '4px',
              fontSize: '12px',
              margin: '2px'
            }}
            title={`DC Offset: ${metrics.dc_offset.toFixed(1)} dB`}
          >
            DC: {formatValue(metrics.dc_offset, 'dB')}
          </span>
        )}

        {metrics.head_silence_ms !== undefined && (
          <span
            className="quality-badge"
            style={{
              backgroundColor: getBadgeColor(150 - metrics.head_silence_ms, { good: 100, warning: 50 }),
              color: 'white',
              padding: '2px 6px',
              borderRadius: '4px',
              fontSize: '12px',
              margin: '2px'
            }}
            title={`Head Silence: ${metrics.head_silence_ms.toFixed(0)} ms`}
          >
            Head: {formatValue(metrics.head_silence_ms, 'ms', 0)}
          </span>
        )}

        {metrics.tail_silence_ms !== undefined && (
          <span
            className="quality-badge"
            style={{
              backgroundColor: getBadgeColor(150 - metrics.tail_silence_ms, { good: 100, warning: 50 }),
              color: 'white',
              padding: '2px 6px',
              borderRadius: '4px',
              fontSize: '12px',
              margin: '2px'
            }}
            title={`Tail Silence: ${metrics.tail_silence_ms.toFixed(0)} ms`}
          >
            Tail: {formatValue(metrics.tail_silence_ms, 'ms', 0)}
          </span>
        )}
      </div>
    );
  };

  // WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      const ws = new WebSocket(`ws://127.0.0.1:5090/ws`);

      ws.onopen = () => {
        setWsConnected(true);
        wsRef.current = ws;
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'job') {
          handleJobUpdate(data);
        }
      };

      ws.onclose = () => {
        setWsConnected(false);
        wsRef.current = null;
        setTimeout(connectWebSocket, 3000);
      };

      ws.onerror = () => {
        setWsConnected(false);
      };
    };

    connectWebSocket();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const handleJobUpdate = (data: any) => {
    setJobs(prev => {
      const existing = prev.find(j => j.id === data.id);
      if (existing) {
        return prev.map(j => j.id === data.id ? { ...j, ...data } : j);
      } else {
        return [...prev, { id: data.id, status: data.phase, progress: data.progress || 0 }];
      }
    });
  };

  const fetchEngines = async () => {
    try {
      const response = await fetch(`${baseUrl}/health`);
      const data = await response.json();
      setEngines(Object.entries(data.engines).map(([id, info]: [string, any]) => ({
        id,
        ...info
      })));
    } catch (error) {
      console.error('Failed to fetch engines:', error);
    }
  };

  const generateTTS = async () => {
    try {
      const response = await fetch(`${baseUrl}/tts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text,
          language,
          quality,
          mode,
          voice_profile: {},
          params: { sample_rate: 22050 }
        })
      });

      const data = await response.json();

      if (mode === 'sync' && data.result_b64_wav) {
        const audioBlob = new Blob([Uint8Array.from(atob(data.result_b64_wav), c => c.charCodeAt(0))], { type: 'audio/wav' });
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
        setAudioMetrics(data.metrics || null);  // Store audio metrics
      }
    } catch (error) {
      console.error('TTS generation failed:', error);
    }
  };

  const startBlindABTest = async () => {
    try {
      const response = await fetch(`${baseUrl}/abtest/blind`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text,
          language,
          quality
        })
      });

      const data = await response.json();
      setBlindTest(data);
    } catch (error) {
      console.error('Blind A/B test failed:', error);
    }
  };

  const submitRating = async () => {
    if (!blindTest) return;

    try {
      await fetch(`${baseUrl}/abtest/submit_rating`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: blindTest.session_id,
          trial_id: blindTest.trial_id,
          rating_a: ratings.a,
          rating_b: ratings.b,
          winner: ratings.winner
        })
      });

      setBlindTest(null);
      fetchSummary();
    } catch (error) {
      console.error('Rating submission failed:', error);
    }
  };

  const fetchSummary = async () => {
    try {
      const response = await fetch(`${baseUrl}/abtest/summary`);
      const data = await response.json();
      setSummary(data);
    } catch (error) {
      console.error('Failed to fetch summary:', error);
    }
  };

  const uploadReference = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${baseUrl}/upload_ref`, {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      console.log('Upload successful:', data);
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  const generateDiagnostics = async () => {
    try {
      const response = await fetch(`${baseUrl}/diagnostics/bundle`, { method: 'POST' });
      const data = await response.json();
      console.log('Diagnostics bundle created:', data.file);
    } catch (error) {
      console.error('Diagnostics generation failed:', error);
    }
  };

  useEffect(() => {
    fetchEngines();
    fetchSummary();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>VoiceStudio Router Dashboard</h1>
        <div className="status">
          <span className={`ws-status ${wsConnected ? 'connected' : 'disconnected'}`}>
            WebSocket: {wsConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </header>

      <main className="App-main">
        {/* Engine Status */}
        <section className="engines-section">
          <h2>Engine Status</h2>
          <button onClick={fetchEngines}>Refresh</button>
          <div className="engines-grid">
            {engines.map(engine => (
              <div key={engine.id} className={`engine-card ${engine.healthy ? 'healthy' : 'unhealthy'}`}>
                <h3>{engine.id}</h3>
                <p>Status: {engine.healthy ? 'Healthy' : 'Unhealthy'}</p>
                <p>Load: {(engine.load * 100).toFixed(1)}%</p>
                <p>Languages: {engine.languages.join(', ')}</p>
                <p>Quality: {engine.quality.join(', ')}</p>
              </div>
            ))}
          </div>
        </section>

        {/* TTS Generation */}
        <section className="tts-section">
          <h2>Text-to-Speech</h2>
          <div className="tts-controls">
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Enter text to synthesize..."
              rows={3}
            />
            <div className="controls-row">
              <select value={language} onChange={(e) => setLanguage(e.target.value)}>
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
                <option value="de">German</option>
                <option value="it">Italian</option>
                <option value="pt">Portuguese</option>
                <option value="zh">Chinese</option>
                <option value="ja">Japanese</option>
              </select>
              <select value={quality} onChange={(e) => setQuality(e.target.value)}>
                <option value="fast">Fast</option>
                <option value="balanced">Balanced</option>
                <option value="quality">Quality</option>
              </select>
              <select value={mode} onChange={(e) => setMode(e.target.value as 'sync' | 'async')}>
                <option value="sync">Sync</option>
                <option value="async">Async</option>
              </select>
              <button onClick={generateTTS}>Generate</button>
            </div>
          </div>

          {audioUrl && (
            <div className="audio-player">
              <audio ref={audioRef} controls src={audioUrl} />
              <AudioQualityBadges metrics={audioMetrics} />
            </div>
          )}
        </section>

        {/* Job Queue */}
        {jobs.length > 0 && (
          <section className="jobs-section">
            <h2>Job Queue</h2>
            <div className="jobs-list">
              {jobs.map(job => (
                <div key={job.id} className="job-item">
                  <span>Job {job.id}</span>
                  <span>Status: {job.status}</span>
                  <span>Progress: {(job.progress * 100).toFixed(1)}%</span>
                  {job.engine && <span>Engine: {job.engine}</span>}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Blind A/B Testing */}
        <section className="abtest-section">
          <h2>Blind A/B Testing</h2>
          {!blindTest ? (
            <div>
              <button onClick={startBlindABTest}>Start Blind A/B Test</button>
            </div>
          ) : (
            <div className="abtest-interface">
              <h3>Trial {blindTest.trial_id}</h3>
              <div className="audio-comparison">
                {blindTest.items.map((item, index) => (
                  <div key={item.id} className="audio-clip">
                    <h4>Sample {String.fromCharCode(65 + index)}</h4>
                    <audio controls src={item.url} />
                    <AudioQualityBadges metrics={item.metrics} />
                    <div className="rating">
                      <label>Rating (1-5):</label>
                      <input
                        type="range"
                        min="1"
                        max="5"
                        value={ratings[String.fromCharCode(97 + index) as 'a' | 'b']}
                        onChange={(e) => setRatings(prev => ({
                          ...prev,
                          [String.fromCharCode(97 + index)]: parseInt(e.target.value)
                        }))}
                      />
                      <span>{ratings[String.fromCharCode(97 + index) as 'a' | 'b']}</span>
                    </div>
                  </div>
                ))}
              </div>
              <div className="winner-selection">
                <label>Winner:</label>
                <select value={ratings.winner} onChange={(e) => setRatings(prev => ({ ...prev, winner: e.target.value }))}>
                  <option value="A">A</option>
                  <option value="B">B</option>
                  <option value="tie">Tie</option>
                </select>
              </div>
              <button onClick={submitRating}>Submit Rating</button>
            </div>
          )}
        </section>

        {/* Summary */}
        {summary && (
          <section className="summary-section">
            <h2>Test Summary</h2>
            <button onClick={fetchSummary}>Refresh Summary</button>
            <div className="summary-grid">
              {Object.entries(summary.totals).map(([engine, stats]: [string, any]) => (
                <div key={engine} className="summary-card">
                  <h3>{engine}</h3>
                  <p>Wins: {stats.wins}</p>
                  <p>Losses: {stats.losses}</p>
                  <p>Ties: {stats.ties}</p>
                  <p>Mean Rating: {stats.mean_rating?.toFixed(2) || 'N/A'}</p>
                  <p>Samples: {stats.n}</p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Tools */}
        <section className="tools-section">
          <h2>Tools</h2>
          <div className="tools-grid">
            <div className="tool-card">
              <h3>Upload Reference</h3>
              <input
                type="file"
                accept="audio/*"
                onChange={(e) => e.target.files?.[0] && uploadReference(e.target.files[0])}
              />
            </div>
            <div className="tool-card">
              <h3>Diagnostics</h3>
              <button onClick={generateDiagnostics}>Generate Bundle</button>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
