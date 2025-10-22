import React, { useState, useEffect, useRef } from 'react';
import './RouterDashboard.css';

interface Engine {
  healthy: boolean;
  load: number;
  languages: string[];
  quality: string[];
}

interface Engines {
  [key: string]: Engine;
}

interface TTSRequest {
  text: string;
  language: string;
  quality: 'fast' | 'balanced' | 'quality';
  voice_profile: Record<string, any>;
  params: Record<string, any>;
  mode: 'sync' | 'async';
}

interface TTSResponse {
  engine: string;
  tried_order: string[];
  result_b64_wav?: string;
  job_id?: string;
}

interface JobStatus {
  id: string;
  status: string;
  progress: number;
  engine?: string;
  result_b64_wav?: string;
  error?: string;
  started_at: number;
  finished_at?: number;
}

const RouterDashboard: React.FC = () => {
  const [engines, setEngines] = useState<Engines>({});
  const [health, setHealth] = useState<{ ok: boolean; engines: Engines } | null>(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [jobs, setJobs] = useState<JobStatus[]>([]);
  const [request, setRequest] = useState<TTSRequest>({
    text: 'Hello, this is a test of the VoiceStudio router!',
    language: 'en',
    quality: 'balanced',
    voice_profile: {},
    params: { sample_rate: 22050 },
    mode: 'sync'
  });
  const [response, setResponse] = useState<TTSResponse | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadToken, setUploadToken] = useState<string | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  const baseUrl = 'http://127.0.0.1:5090';

  useEffect(() => {
    fetchHealth();
    connectWebSocket();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const fetchHealth = async () => {
    try {
      const response = await fetch(`${baseUrl}/health`);
      const data = await response.json();
      setHealth(data);
      setEngines(data.engines);
    } catch (error) {
      console.error('Failed to fetch health:', error);
    }
  };

  const connectWebSocket = () => {
    const ws = new WebSocket(`ws://127.0.0.1:5090/ws`);
    wsRef.current = ws;

    ws.onopen = () => {
      setWsConnected(true);
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('WebSocket message:', data);
      
      if (data.type === 'job') {
        handleJobUpdate(data);
      }
    };

    ws.onclose = () => {
      setWsConnected(false);
      console.log('WebSocket disconnected');
      // Reconnect after 3 seconds
      setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  };

  const handleJobUpdate = (data: any) => {
    if (data.phase === 'start') {
      setJobs(prev => [...prev, {
        id: data.id,
        status: 'running',
        progress: 0,
        started_at: Date.now()
      }]);
    } else if (data.phase === 'progress') {
      setJobs(prev => prev.map(job => 
        job.id === data.id ? { ...job, progress: data.progress } : job
      ));
    } else if (data.phase === 'done') {
      setJobs(prev => prev.map(job => 
        job.id === data.id ? { 
          ...job, 
          status: 'done', 
          progress: 1, 
          engine: data.engine,
          finished_at: Date.now()
        } : job
      ));
    } else if (data.phase === 'error') {
      setJobs(prev => prev.map(job => 
        job.id === data.id ? { 
          ...job, 
          status: 'error', 
          error: data.error,
          finished_at: Date.now()
        } : job
      ));
    }
  };

  const handleTTSRequest = async () => {
    try {
      const response = await fetch(`${baseUrl}/tts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: TTSResponse = await response.json();
      setResponse(data);

      if (data.result_b64_wav) {
        const audioBlob = new Blob([
          Uint8Array.from(atob(data.result_b64_wav), c => c.charCodeAt(0))
        ], { type: 'audio/wav' });
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
      }
    } catch (error) {
      console.error('TTS request failed:', error);
      alert('TTS request failed: ' + error);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploadedFile(file);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${baseUrl}/upload_ref`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }

      const data = await response.json();
      setUploadToken(data.token);
      
      // Update voice profile with uploaded reference
      setRequest(prev => ({
        ...prev,
        voice_profile: {
          ...prev.voice_profile,
          speaker_wavs: [data.path]
        }
      }));
    } catch (error) {
      console.error('File upload failed:', error);
      alert('File upload failed: ' + error);
    }
  };

  const playAudio = () => {
    if (audioRef.current && audioUrl) {
      audioRef.current.play();
    }
  };

  const downloadDiagnostics = async () => {
    try {
      const response = await fetch(`${baseUrl}/diagnostics/bundle`, {
        method: 'POST'
      });
      const data = await response.json();
      
      const downloadResponse = await fetch(`${baseUrl}/diagnostics/download?file=${data.file}`);
      const blob = await downloadResponse.blob();
      
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = data.file;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Diagnostics download failed:', error);
    }
  };

  return (
    <div className="router-dashboard">
      <header className="dashboard-header">
        <h1>VoiceStudio Router Dashboard</h1>
        <div className="status-indicators">
          <div className={`status-indicator ${health?.ok ? 'healthy' : 'unhealthy'}`}>
            API: {health?.ok ? 'Healthy' : 'Unhealthy'}
          </div>
          <div className={`status-indicator ${wsConnected ? 'connected' : 'disconnected'}`}>
            WebSocket: {wsConnected ? 'Connected' : 'Disconnected'}
          </div>
        </div>
      </header>

      <div className="dashboard-content">
        <div className="engines-panel">
          <h2>Engine Status</h2>
          <div className="engines-grid">
            {Object.entries(engines).map(([id, engine]) => (
              <div key={id} className={`engine-card ${engine.healthy ? 'healthy' : 'unhealthy'}`}>
                <h3>{id.toUpperCase()}</h3>
                <div className="engine-info">
                  <div>Status: {engine.healthy ? 'Healthy' : 'Unhealthy'}</div>
                  <div>Load: {(engine.load * 100).toFixed(1)}%</div>
                  <div>Languages: {engine.languages.join(', ')}</div>
                  <div>Quality: {engine.quality.join(', ')}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="tts-panel">
          <h2>Text-to-Speech</h2>
          <div className="tts-form">
            <div className="form-group">
              <label>Text:</label>
              <textarea
                value={request.text}
                onChange={(e) => setRequest(prev => ({ ...prev, text: e.target.value }))}
                rows={3}
              />
            </div>
            
            <div className="form-row">
              <div className="form-group">
                <label>Language:</label>
                <select
                  value={request.language}
                  onChange={(e) => setRequest(prev => ({ ...prev, language: e.target.value }))}
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                  <option value="it">Italian</option>
                  <option value="pt">Portuguese</option>
                  <option value="zh">Chinese</option>
                  <option value="ja">Japanese</option>
                </select>
              </div>
              
              <div className="form-group">
                <label>Quality:</label>
                <select
                  value={request.quality}
                  onChange={(e) => setRequest(prev => ({ ...prev, quality: e.target.value as any }))}
                >
                  <option value="fast">Fast</option>
                  <option value="balanced">Balanced</option>
                  <option value="quality">Quality</option>
                </select>
              </div>
              
              <div className="form-group">
                <label>Mode:</label>
                <select
                  value={request.mode}
                  onChange={(e) => setRequest(prev => ({ ...prev, mode: e.target.value as any }))}
                >
                  <option value="sync">Sync</option>
                  <option value="async">Async</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>Voice Reference (Optional):</label>
              <input
                type="file"
                accept=".wav,.mp3,.flac,.m4a,.ogg"
                onChange={handleFileUpload}
              />
              {uploadToken && <div className="upload-success">✓ Reference uploaded: {uploadToken}</div>}
            </div>

            <button onClick={handleTTSRequest} className="tts-button">
              Generate Speech
            </button>
          </div>

          {response && (
            <div className="tts-response">
              <h3>Response</h3>
              <div className="response-info">
                <div>Engine: {response.engine}</div>
                <div>Tried Order: {response.tried_order.join(' → ')}</div>
                {response.job_id && <div>Job ID: {response.job_id}</div>}
              </div>
              
              {audioUrl && (
                <div className="audio-player">
                  <audio ref={audioRef} src={audioUrl} controls />
                  <button onClick={playAudio}>Play Audio</button>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="jobs-panel">
          <h2>Active Jobs</h2>
          <div className="jobs-list">
            {jobs.map(job => (
              <div key={job.id} className={`job-item ${job.status}`}>
                <div className="job-header">
                  <span>Job {job.id}</span>
                  <span className="job-status">{job.status}</span>
                </div>
                <div className="job-progress">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill" 
                      style={{ width: `${job.progress * 100}%` }}
                    />
                  </div>
                  <span>{(job.progress * 100).toFixed(1)}%</span>
                </div>
                {job.engine && <div>Engine: {job.engine}</div>}
                {job.error && <div className="job-error">Error: {job.error}</div>}
              </div>
            ))}
          </div>
        </div>

        <div className="tools-panel">
          <h2>Tools</h2>
          <button onClick={fetchHealth} className="tool-button">
            Refresh Health
          </button>
          <button onClick={downloadDiagnostics} className="tool-button">
            Download Diagnostics
          </button>
        </div>
      </div>
    </div>
  );
};

export default RouterDashboard;
