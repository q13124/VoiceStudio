# VoiceStudio Quantum+ API Code Examples

Code examples for using the VoiceStudio API in various languages.

## Table of Contents

1. [Python Examples](#python-examples)
2. [C# Examples](#c-examples)
3. [cURL Examples](#curl-examples)
4. [JavaScript Examples](#javascript-examples)
5. [Quality Improvement Features](#quality-improvement-features)

---

## Python Examples

### Basic Setup

```python
import requests
import json

BASE_URL = "http://localhost:8000/api"

def make_request(method, endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    response = requests.request(method, url, json=data)
    response.raise_for_status()
    return response.json()
```

### Voice Profiles

#### Create Profile

```python
def create_profile(name, language="en"):
    data = {
        "name": name,
        "language": language,
        "tags": []
    }
    return make_request("POST", "/profiles", data)

# Usage
profile = create_profile("My Voice", "en")
print(f"Created profile: {profile['id']}")
```

#### List Profiles

```python
def list_profiles():
    return make_request("GET", "/profiles")

# Usage
profiles = list_profiles()
for profile in profiles:
    print(f"{profile['name']}: {profile['id']}")
```

#### Get Profile

```python
def get_profile(profile_id):
    return make_request("GET", f"/profiles/{profile_id}")

# Usage
profile = get_profile("profile-123")
print(profile)
```

### Voice Synthesis

#### Synthesize Speech

```python
def synthesize(profile_id, text, engine="chatterbox", language="en"):
    data = {
        "engine": engine,
        "profile_id": profile_id,
        "text": text,
        "language": language,
        "enhance_quality": True
    }
    return make_request("POST", "/voice/synthesize", data)

# Usage
result = synthesize("profile-123", "Hello, world!", "chatterbox")
print(f"Audio ID: {result['audio_id']}")
print(f"MOS Score: {result['quality_metrics']['mos_score']}")
print(f"Similarity: {result['quality_metrics']['similarity']}")
```

#### Analyze Audio Quality

```python
def analyze_quality(audio_id, reference_audio_id=None):
    data = {
        "audio_id": audio_id,
        "reference_audio_id": reference_audio_id
    }
    return make_request("POST", "/voice/analyze", data)

# Usage
metrics = analyze_quality("audio-123", "ref-123")
print(f"Quality metrics: {metrics['quality_metrics']}")
```

### Projects

#### Create Project

```python
def create_project(name, description=None):
    data = {
        "name": name,
        "description": description
    }
    return make_request("POST", "/projects", data)

# Usage
project = create_project("My Project", "Test project")
print(f"Created project: {project['id']}")
```

#### List Projects

```python
def list_projects():
    return make_request("GET", "/projects")

# Usage
projects = list_projects()
for project in projects:
    print(f"{project['name']}: {project['id']}")
```

### Batch Processing

#### Create Batch Job

```python
def create_batch_job(name, project_id, profile_id, engine, texts):
    data = {
        "name": name,
        "project_id": project_id,
        "voice_profile_id": profile_id,
        "engine_id": engine,
        "texts": texts,
        "language": "en"
    }
    return make_request("POST", "/batch/jobs", data)

# Usage
job = create_batch_job(
    "Batch Job 1",
    "project-123",
    "profile-123",
    "chatterbox",
    ["Text 1", "Text 2", "Text 3"]
)
print(f"Created batch job: {job['id']}")
```

#### Start Batch Job

```python
def start_batch_job(job_id):
    return make_request("POST", f"/batch/jobs/{job_id}/start")

# Usage
start_batch_job("batch-123")
```

#### Get Batch Job Status

```python
def get_batch_job(job_id):
    return make_request("GET", f"/batch/jobs/{job_id}")

# Usage
job = get_batch_job("batch-123")
print(f"Status: {job['status']}, Progress: {job['progress']}")
```

### WebSocket (Python)

```python
import asyncio
import websockets
import json

async def listen_events():
    uri = "ws://localhost:8000/ws/realtime?topics=meters,training"
    
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            if data["topic"] == "meters":
                print(f"Meters: {data['payload']}")
            elif data["topic"] == "training":
                print(f"Training: {data['payload']}")

# Usage
asyncio.run(listen_events())
```

---

## C# Examples

### Basic Setup

```csharp
using System;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

public class VoiceStudioClient
{
    private readonly HttpClient _client;
    private readonly string _baseUrl;

    public VoiceStudioClient(string baseUrl = "http://localhost:8000/api")
    {
        _baseUrl = baseUrl;
        _client = new HttpClient();
        _client.BaseAddress = new Uri(baseUrl);
    }

    private async Task<T> MakeRequestAsync<T>(HttpMethod method, string endpoint, object data = null)
    {
        var request = new HttpRequestMessage(method, endpoint);
        
        if (data != null)
        {
            var json = JsonSerializer.Serialize(data);
            request.Content = new StringContent(json, Encoding.UTF8, "application/json");
        }

        var response = await _client.SendAsync(request);
        response.EnsureSuccessStatusCode();
        
        var content = await response.Content.ReadAsStringAsync();
        return JsonSerializer.Deserialize<T>(content);
    }
}
```

### Voice Profiles

#### Create Profile

```csharp
public async Task<VoiceProfile> CreateProfileAsync(string name, string language = "en")
{
    var data = new
    {
        name = name,
        language = language,
        tags = new string[] { }
    };
    
    return await MakeRequestAsync<VoiceProfile>("POST", "/profiles", data);
}

// Usage
var client = new VoiceStudioClient();
var profile = await client.CreateProfileAsync("My Voice", "en");
Console.WriteLine($"Created profile: {profile.Id}");
```

#### List Profiles

```csharp
public async Task<List<VoiceProfile>> ListProfilesAsync()
{
    return await MakeRequestAsync<List<VoiceProfile>>("GET", "/profiles");
}

// Usage
var profiles = await client.ListProfilesAsync();
foreach (var profile in profiles)
{
    Console.WriteLine($"{profile.Name}: {profile.Id}");
}
```

### Voice Synthesis

#### Synthesize Speech

```csharp
public async Task<VoiceSynthesizeResponse> SynthesizeAsync(
    string profileId, 
    string text, 
    string engine = "chatterbox",
    string language = "en")
{
    var data = new
    {
        engine = engine,
        profile_id = profileId,
        text = text,
        language = language,
        enhance_quality = true
    };
    
    return await MakeRequestAsync<VoiceSynthesizeResponse>("POST", "/voice/synthesize", data);
}

// Usage
var result = await client.SynthesizeAsync("profile-123", "Hello, world!", "chatterbox");
Console.WriteLine($"Audio ID: {result.AudioId}");
Console.WriteLine($"MOS Score: {result.QualityMetrics.MosScore}");
```

### Projects

#### Create Project

```csharp
public async Task<Project> CreateProjectAsync(string name, string description = null)
{
    var data = new
    {
        name = name,
        description = description
    };
    
    return await MakeRequestAsync<Project>("POST", "/projects", data);
}

// Usage
var project = await client.CreateProjectAsync("My Project", "Test project");
Console.WriteLine($"Created project: {project.Id}");
```

### WebSocket (C#)

```csharp
using System;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

public class WebSocketClient
{
    private ClientWebSocket _ws;
    
    public async Task ConnectAsync(string topics = "meters,training")
    {
        _ws = new ClientWebSocket();
        var uri = new Uri($"ws://localhost:8000/ws/realtime?topics={topics}");
        await _ws.ConnectAsync(uri, CancellationToken.None);
        
        _ = Task.Run(ReceiveLoop);
    }
    
    private async Task ReceiveLoop()
    {
        var buffer = new byte[4096];
        
        while (_ws.State == WebSocketState.Open)
        {
            var result = await _ws.ReceiveAsync(
                new ArraySegment<byte>(buffer), 
                CancellationToken.None
            );
            
            if (result.MessageType == WebSocketMessageType.Text)
            {
                var message = Encoding.UTF8.GetString(buffer, 0, result.Count);
                var data = JsonSerializer.Deserialize<WebSocketEvent>(message);
                HandleEvent(data);
            }
        }
    }
    
    private void HandleEvent(WebSocketEvent data)
    {
        switch (data.Topic)
        {
            case "meters":
                Console.WriteLine($"Meters: {data.Payload}");
                break;
            case "training":
                Console.WriteLine($"Training: {data.Payload}");
                break;
        }
    }
}
```

---

## cURL Examples

### Voice Profiles

#### Create Profile

```bash
curl -X POST http://localhost:8000/api/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Voice",
    "language": "en",
    "tags": []
  }'
```

#### List Profiles

```bash
curl http://localhost:8000/api/profiles
```

#### Get Profile

```bash
curl http://localhost:8000/api/profiles/profile-123
```

### Voice Synthesis

#### Synthesize Speech

```bash
curl -X POST http://localhost:8000/api/voice/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "engine": "chatterbox",
    "profile_id": "profile-123",
    "text": "Hello, world!",
    "language": "en",
    "enhance_quality": true
  }'
```

#### Analyze Quality

```bash
curl -X POST http://localhost:8000/api/voice/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "audio_id": "audio-123",
    "reference_audio_id": "ref-123"
  }'
```

### Projects

#### Create Project

```bash
curl -X POST http://localhost:8000/api/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Project",
    "description": "Test project"
  }'
```

#### List Projects

```bash
curl http://localhost:8000/api/projects
```

### Batch Processing

#### Create Batch Job

```bash
curl -X POST http://localhost:8000/api/batch/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Batch Job 1",
    "project_id": "project-123",
    "voice_profile_id": "profile-123",
    "engine_id": "chatterbox",
    "texts": ["Text 1", "Text 2", "Text 3"],
    "language": "en"
  }'
```

#### Start Batch Job

```bash
curl -X POST http://localhost:8000/api/batch/jobs/batch-123/start
```

#### Get Batch Job Status

```bash
curl http://localhost:8000/api/batch/jobs/batch-123
```

### Transcription

#### Transcribe Audio

```bash
curl -X POST http://localhost:8000/api/transcribe/ \
  -H "Content-Type: application/json" \
  -d '{
    "audio_id": "audio-123",
    "engine": "whisper",
    "language": "en",
    "word_timestamps": true
  }'
```

### Audio Analysis

#### Get Waveform Data

```bash
curl "http://localhost:8000/api/audio/waveform?audio_id=audio-123&width=1000"
```

#### Get Spectrogram Data

```bash
curl "http://localhost:8000/api/audio/spectrogram?audio_id=audio-123&width=1000&height=256"
```

---

## JavaScript Examples

### Basic Setup

```javascript
const BASE_URL = 'http://localhost:8000/api';

async function makeRequest(method, endpoint, data = null) {
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
  };
  
  if (data) {
    options.body = JSON.stringify(data);
  }
  
  const response = await fetch(`${BASE_URL}${endpoint}`, options);
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return await response.json();
}
```

### Voice Profiles

#### Create Profile

```javascript
async function createProfile(name, language = 'en') {
  const data = {
    name,
    language,
    tags: []
  };
  
  return await makeRequest('POST', '/profiles', data);
}

// Usage
const profile = await createProfile('My Voice', 'en');
console.log(`Created profile: ${profile.id}`);
```

#### List Profiles

```javascript
async function listProfiles() {
  return await makeRequest('GET', '/profiles');
}

// Usage
const profiles = await listProfiles();
profiles.forEach(profile => {
  console.log(`${profile.name}: ${profile.id}`);
});
```

### Voice Synthesis

#### Synthesize Speech

```javascript
async function synthesize(profileId, text, engine = 'chatterbox', language = 'en') {
  const data = {
    engine,
    profile_id: profileId,
    text,
    language,
    enhance_quality: true
  };
  
  return await makeRequest('POST', '/voice/synthesize', data);
}

// Usage
const result = await synthesize('profile-123', 'Hello, world!', 'chatterbox');
console.log(`Audio ID: ${result.audio_id}`);
console.log(`MOS Score: ${result.quality_metrics.mos_score}`);
```

### WebSocket (JavaScript)

```javascript
class VoiceStudioWebSocket {
  constructor(topics = []) {
    const topicParam = topics.length > 0 
      ? `?topics=${topics.join(',')}` 
      : '';
    this.ws = new WebSocket(`ws://localhost:8000/ws/realtime${topicParam}`);
    
    this.ws.onopen = () => {
      console.log('Connected');
    };
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleEvent(data);
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    this.ws.onclose = () => {
      console.log('Disconnected');
    };
  }
  
  handleEvent(data) {
    switch (data.topic) {
      case 'meters':
        this.onMetersUpdate(data.payload);
        break;
      case 'training':
        this.onTrainingUpdate(data.payload);
        break;
      case 'batch':
        this.onBatchUpdate(data.payload);
        break;
    }
  }
  
  onMetersUpdate(payload) {
    console.log('Meters update:', payload);
    // Update UI with meter data
  }
  
  onTrainingUpdate(payload) {
    console.log('Training update:', payload);
    // Update training progress UI
  }
  
  onBatchUpdate(payload) {
    console.log('Batch update:', payload);
    // Update batch progress UI
  }
}

// Usage
const ws = new VoiceStudioWebSocket(['meters', 'training']);
```

### Complete Example: Synthesize and Analyze

```javascript
async function synthesizeAndAnalyze(profileId, text) {
  try {
    // Step 1: Synthesize
    console.log('Synthesizing...');
    const synthesis = await synthesize(profileId, text, 'chatterbox');
    console.log(`Synthesized: ${synthesis.audio_id}`);
    console.log(`Quality: MOS=${synthesis.quality_metrics.mos_score}`);
    
    // Step 2: Analyze
    console.log('Analyzing...');
    const analysis = await makeRequest('POST', '/voice/analyze', {
      audio_id: synthesis.audio_id
    });
    console.log(`Analysis complete:`, analysis.quality_metrics);
    
    return {
      audio_id: synthesis.audio_id,
      metrics: analysis.quality_metrics
    };
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}

// Usage
synthesizeAndAnalyze('profile-123', 'Hello, world!')
  .then(result => {
    console.log('Complete:', result);
  })
  .catch(error => {
    console.error('Failed:', error);
  });
```

---

## Quality Improvement Features

Complete working examples for all quality improvement features (IDEA 61-70).

### Python Examples

All Python examples are located in `examples/quality_features/`:

#### Quality Improvement Features (IDEA 61-70)

1. **[Multi-Pass Synthesis](examples/quality_features/multipass_synthesis.py)** - Generate high-quality voice synthesis with quality refinement
2. **[Reference Audio Pre-Processing](examples/quality_features/reference_preprocessing.py)** - Pre-process reference audio for optimal cloning
3. **[Artifact Removal](examples/quality_features/artifact_removal.py)** - Detect and remove audio artifacts
4. **[Voice Characteristic Analysis](examples/quality_features/voice_characteristics.py)** - Analyze voice characteristics for preservation
5. **[Prosody Control](examples/quality_features/prosody_control.py)** - Control prosody and intonation for natural speech
6. **[Face Enhancement](examples/quality_features/face_enhancement.py)** - Enhance face quality in images and videos
7. **[Temporal Consistency](examples/quality_features/temporal_consistency.py)** - Enhance temporal consistency for video deepfakes
8. **[Training Data Optimization](examples/quality_features/training_optimization.py)** - Optimize training data for better cloning
9. **[Post-Processing Pipeline](examples/quality_features/post_processing.py)** - Apply multi-stage post-processing enhancement

#### Quality Testing & Comparison Features (IDEA 46, 47, 49, 52)

10. **[A/B Testing](examples/quality_features/ab_testing.py)** - Compare two synthesis configurations side-by-side
11. **[Engine Recommendation](examples/quality_features/engine_recommendation.py)** - Get AI-powered engine recommendations based on quality requirements
12. **[Quality Benchmarking](examples/quality_features/quality_benchmarking.py)** - Test multiple engines with the same input and compare quality metrics
13. **[Quality Dashboard](examples/quality_features/quality_dashboard.py)** - Get visual overview of quality metrics, trends, and insights

### JavaScript Examples

**[Real-Time Quality Preview](examples/quality_features/realtime_quality_preview.js)** - WebSocket client for real-time quality updates during synthesis and processing

### Quick Example: Multi-Pass Synthesis

```python
from examples.quality_features.multipass_synthesis import synthesize_multipass

# Perform multi-pass synthesis with quality refinement
result = synthesize_multipass(
    profile_id="profile-123",
    text="Hello, world!",
    engine="chatterbox",
    max_passes=3
)

print(f"Best quality audio: {result['audio_url']}")
```

### Quick Example: Artifact Removal

```python
from examples.quality_features.artifact_removal import remove_artifacts_workflow

# Detect and remove artifacts
result = remove_artifacts_workflow("audio-123")

if result.get('repaired_audio_id'):
    print(f"Repaired audio: {result['repaired_audio_url']}")
```

### Quick Example: Real-Time Quality Preview

```javascript
import QualityPreviewClient from './examples/quality_features/realtime_quality_preview.js';

const client = new QualityPreviewClient();
client.connect();

// Quality updates will be received automatically during synthesis
```

### Quick Example: A/B Testing

```python
from examples.quality_features.ab_testing import run_ab_test

# Compare two engines side-by-side
result = run_ab_test(
    profile_id="profile-123",
    text="Hello, this is a test.",
    engine_a="xtts",
    engine_b="tortoise"
)

print(f"Winner: Sample {result['comparison']['overall_winner']}")
```

### Quick Example: Engine Recommendation

```python
from examples.quality_features.engine_recommendation import get_engine_recommendation

# Get engine recommendation for high quality
result = get_engine_recommendation(
    target_tier="high",
    min_mos_score=4.0
)

print(f"Recommended: {result['recommended_engine']}")
```

### Quick Example: Quality Benchmarking

```python
from examples.quality_features.quality_benchmarking import run_benchmark

# Benchmark all engines
result = run_benchmark(
    profile_id="profile-123",
    test_text="This is a benchmark test.",
    engines=["xtts", "chatterbox", "tortoise"]
)

# Find best engine
best = max(result['results'], key=lambda x: x['quality_metrics']['mos_score'])
print(f"Best engine: {best['engine']}")
```

### Quick Example: Quality Dashboard

```python
from examples.quality_features.quality_dashboard import get_quality_dashboard

# Get dashboard for last 30 days
dashboard = get_quality_dashboard(days=30)

print(f"Average MOS: {dashboard['overview']['average_mos_score']:.2f}")
print(f"Total Syntheses: {dashboard['overview']['total_syntheses']}")
```

For complete examples with error handling and workflows, see the individual example files in `examples/quality_features/`.

---

## Error Handling

### Python

```python
import requests

def safe_request(method, endpoint, data=None):
    try:
        url = f"{BASE_URL}{endpoint}"
        response = requests.request(method, url, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"Resource not found: {endpoint}")
        elif e.response.status_code == 400:
            print(f"Bad request: {e.response.text}")
        else:
            print(f"HTTP error: {e}")
        raise
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        raise
```

### JavaScript

```javascript
async function safeRequest(method, endpoint, data = null) {
  try {
    const options = {
      method,
      headers: { 'Content-Type': 'application/json' },
    };
    
    if (data) {
      options.body = JSON.stringify(data);
    }
    
    const response = await fetch(`${BASE_URL}${endpoint}`, options);
    
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error(`Resource not found: ${endpoint}`);
      } else if (response.status === 400) {
        const error = await response.json();
        throw new Error(`Bad request: ${error.detail}`);
      } else {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    }
    
    return await response.json();
  } catch (error) {
    console.error('Request error:', error);
    throw error;
  }
}
```

---

## Best Practices

1. **Error Handling:**
   - Always handle HTTP errors
   - Check response status codes
   - Provide user-friendly error messages

2. **Rate Limiting:**
   - Implement retry logic with exponential backoff
   - Respect rate limits (if implemented)

3. **WebSocket:**
   - Implement reconnection logic
   - Handle disconnections gracefully
   - Subscribe only to needed topics

4. **Performance:**
   - Use batch endpoints for multiple operations
   - Cache frequently accessed data
   - Use WebSocket for real-time updates

---

**For more information:**
- [API Reference](API_REFERENCE.md)
- [Endpoints List](ENDPOINTS.md)
- [WebSocket Events](WEBSOCKET_EVENTS.md)

