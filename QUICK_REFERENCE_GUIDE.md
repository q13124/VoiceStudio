# VoiceStudio Ultimate - Quick Reference Guide

## 🚀 Getting Started

### Run Health Check
```bash
python tools/system_health_validator.py
```

### Start Development Mode
```bash
python tools/voicestudio_launcher.py --mode dev
```

### Start Production Mode
```bash
python tools/voicestudio_launcher.py --mode prod
```

---

## 📋 Priority Implementation Order

### Week 1-2: Foundation (CRITICAL)
1. **Multi-Reference Fusion** (3 days) → 40% quality boost
2. **Quality Scoring** (2 days) → Objective metrics
3. **Engine Router** (4 days) → Smart selection
4. **Audio Mastering** (3 days) → Professional output
5. **Batch Processing** (2 days) → 10x throughput

### Week 3-4: Intelligence
6. **Prosody Transfer** (1 week) → Natural speech
7. **Emotion Control** (1 week) → Expressive voices
8. **A/B Testing** (3 days) → Data-driven optimization

### Week 5-6: UI/UX
9. **React Dashboard** (1 week) → Modern interface
10. **Voice Profile Manager** (1 week) → Better UX

---

## 🏗️ Architecture Fixes

### 1. Consolidate Dependencies
```bash
# Merge all requirements into pyproject.toml
pip install -e ".[all]"
```

### 2. Unify Configurations
```bash
# Merge 10+ configs into 3 files
python tools/migrate_configs.py
```

### 3. Add Database Migrations
```bash
# Initialize Alembic
alembic init db/alembic
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

### 4. Implement Service Discovery
```bash
# Start Consul (optional)
consul agent -dev
```

---

## 🎯 Key Features to Implement

### Multi-Reference Fusion
```python
# workers/ops/voice_fusion.py
from resemblyzer import VoiceEncoder

def fuse_references(audio_files: List[str]) -> np.ndarray:
    encoder = VoiceEncoder()
    embeddings = [encoder.embed_utterance(load(f)) for f in audio_files]
    weights = [calculate_quality(f) for f in audio_files]
    return np.average(embeddings, weights=weights, axis=0)
```

### Quality Scoring
```python
# workers/ops/quality_scorer.py
def score_similarity(reference: Audio, generated: Audio) -> float:
    encoder = VoiceEncoder()
    ref_emb = encoder.embed_utterance(reference)
    gen_emb = encoder.embed_utterance(generated)
    return cosine_similarity(ref_emb, gen_emb) * 100  # 0-100
```

### Engine Router
```python
# workers/ops/engine_router.py
def select_engine(language: str, quality: str) -> str:
    if language in ["ja", "zh"]: return "cosyvoice2"
    if quality == "fast": return "xtts"
    if quality == "quality": return "openvoice"
    return "xtts"
```

### Audio Mastering
```python
# workers/ops/audio_master.py
import pyloudnorm as pyln

def master_audio(audio: np.ndarray, sr: int) -> np.ndarray:
    meter = pyln.Meter(sr)
    loudness = meter.integrated_loudness(audio)
    normalized = pyln.normalize.loudness(audio, loudness, -16.0)
    return apply_eq(apply_compression(normalized))
```

---

## 🔧 Configuration

### Main Config (config/voicestudio.config.json)
```json
{
  "programdata": "C:/ProgramData/VoiceStudio",
  "service_port": 5188,
  "ui": {"theme": "dark", "language": "en-US"},
  "logging": {"level": "Information", "json": true}
}
```

### Engines Config (config/engines.config.json)
```json
{
  "routing_policy": {
    "prefer": {"en": "xtts", "ja": "cosyvoice2"},
    "fallback": ["xtts", "openvoice", "cosyvoice2"]
  }
}
```

---

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run with Coverage
```bash
pytest --cov=. --cov-report=html
```

### Run Health Check
```bash
python tools/system_health_validator.py
```

---

## 📊 Monitoring

### Check Service Status
```bash
curl http://127.0.0.1:5188/health
```

### View Metrics
```bash
curl http://127.0.0.1:5188/metrics
```

### Check Engine Status
```bash
curl http://127.0.0.1:5188/engines
```

---

## 🎨 UI/UX Components

### Dashboard
- Service status grid
- Active jobs queue
- Performance metrics
- Quick actions

### Voice Cloning Interface
- Drag-drop audio upload
- Engine selector
- Quality settings
- Real-time progress

### Voice Profile Manager
- Profile gallery
- Search and filter
- Preview playback
- Community marketplace

---

## 🔐 Security

### API Authentication
```bash
# Get API key from logs or database
curl -H "X-API-Key: YOUR_KEY" http://127.0.0.1:5188/metrics
```

### JWT Tokens
```bash
# Login
curl -H "X-API-Key: YOUR_KEY" http://127.0.0.1:5188/auth/login

# Use token
curl -H "Authorization: Bearer TOKEN" http://127.0.0.1:5188/discovery
```

---

## 📈 Performance Optimization

### Enable GPU
```python
import torch
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
```

### Enable Caching
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def load_model(engine: str):
    # Model loaded once and cached
    pass
```

### Batch Processing
```python
def process_batch(requests: List[Request]) -> List[Audio]:
    grouped = group_by_engine(requests)
    return [engine.batch_infer(reqs) for engine, reqs in grouped.items()]
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :5188
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5188 | xargs kill -9
```

### Import Errors
```bash
pip install -e ".[all]"
```

### GPU Not Detected
```bash
# Check CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Install CUDA version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Config Errors
```bash
# Validate config
python -c "from common.config_schema import VoiceStudioConfig; VoiceStudioConfig.parse_file('config/voicestudio.yaml')"
```

---

## 📚 Documentation

### Architecture
- `VoiceStudio_Architecture_Documentation.md`
- `FRAMEWORK_INTEGRITY_ANALYSIS.md`

### Features
- `ADVANCED_VOICE_CLONING_RECOMMENDATIONS.md`
- `IMPLEMENTATION_PRIORITIES.md`

### UI/UX
- `UI_UX_MODERNIZATION_SPEC.md`

### Strategy
- `CHATGPT_STRATEGIC_RECOMMENDATIONS.md`

---

## 🎯 Success Metrics

### Quality
- Voice similarity: >85% (target >90%)
- Audio quality: >3.5 PESQ (target >4.0)
- User ratings: >4.0/5 (target >4.5/5)

### Performance
- Latency: <3s (target <2s)
- Throughput: 100 req/min (target 200)
- GPU utilization: >70% (target >85%)

### Business
- User satisfaction: >4.5/5
- Return rate: >50% (target >70%)
- Feature discovery: >60%

---

## 🔄 Common Commands

### Development
```bash
# Start dev server
python tools/voicestudio_launcher.py --mode dev

# Run tests
pytest tests/ -v

# Check health
python tools/system_health_validator.py

# Format code
black .
ruff check .
```

### Deployment
```bash
# Build installer
cd installer/VoiceStudio.Bootstrapper
.\build-remote.ps1

# Build Docker
docker-compose build

# Deploy
docker-compose up -d
```

### Maintenance
```bash
# Update dependencies
pip install -U -e ".[all]"

# Run migrations
alembic upgrade head

# Clear cache
rm -rf __pycache__ .mypy_cache .pytest_cache

# Backup database
cp voicestudio.db voicestudio.db.backup
```

---

## 🆘 Quick Fixes

### Service Won't Start
1. Check port availability
2. Verify config files exist
3. Check Python version (>=3.9)
4. Run health validator

### Poor Voice Quality
1. Use 3+ reference samples
2. Check audio quality (SNR)
3. Try different engine
4. Enable audio mastering

### Slow Performance
1. Enable GPU if available
2. Use batch processing
3. Enable model caching
4. Reduce quality for speed

### Import Errors
1. Check Python version
2. Reinstall dependencies
3. Check for conflicts
4. Use virtual environment

---

## 📞 Support

### Documentation
- `/docs/` - Full documentation
- `README.md` - Project overview
- `HEALTH_REPORT.md` - System status

### Tools
- `tools/system_health_validator.py` - Health checks
- `tools/voicestudio_launcher.py` - Unified launcher
- `tools/migrate_configs.py` - Config migration

### Logs
- `logs/` - Application logs
- `voicestudio.db` - Database
- `HEALTH_REPORT.md` - Health report

---

## 🎓 Best Practices

### Voice Cloning
- Use 3-10 reference samples
- Each sample 5-30 seconds
- Clear audio, no background noise
- Different sentences per sample
- Same speaker, different contexts

### Configuration
- Use environment variables
- Validate with schema
- Version control configs
- Document changes

### Development
- Write tests first
- Use type hints
- Follow PEP 8
- Document code
- Review before commit

### Deployment
- Test in staging first
- Use health checks
- Monitor metrics
- Have rollback plan
- Document changes

---

**This guide provides quick access to all essential VoiceStudio operations and best practices.**
