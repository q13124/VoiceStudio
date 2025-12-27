# VoiceStudio Quantum+ API Documentation

Complete API documentation for VoiceStudio Quantum+ backend.

## Documentation Files

### 📚 Main Documentation

- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API reference with all endpoints
- **[ENDPOINTS.md](ENDPOINTS.md)** - Detailed list of all 133+ API endpoints
- **[API_USAGE_GUIDE.md](API_USAGE_GUIDE.md)** - Usage guide with code examples
- **[ERROR_CODES.md](ERROR_CODES.md)** - Complete error code reference

### 🔧 Interactive Documentation

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

---

## Quick Start

### 1. Health Check

```bash
curl http://localhost:8000/api/health
```

### 2. Create Voice Profile

```bash
curl -X POST http://localhost:8000/api/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Voice",
    "language": "en"
  }'
```

### 3. Synthesize Voice

```bash
curl -X POST http://localhost:8000/api/voice/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, world!",
    "voice_profile_id": "profile-123",
    "language": "en"
  }'
```

---

## Documentation Structure

### API_REFERENCE.md
- Overview and features
- Base URL and authentication
- Request/response formats
- Error handling
- Rate limiting
- Endpoint categories
- WebSocket events

### ENDPOINTS.md
- Complete list of all endpoints
- Organized by category
- Request/response examples
- Parameter descriptions

### API_USAGE_GUIDE.md
- Getting started guide
- Code examples (Python, JavaScript, cURL)
- Error handling examples
- Best practices
- Rate limiting guide
- WebSocket usage
- Complete workflow examples

### ERROR_CODES.md
- All error codes
- Error response format
- Recovery suggestions
- Error handling best practices
- Complete error code list

---

## API Features

### Voice Cloning
- Multiple engines (XTTS v2, Chatterbox TTS, Tortoise TTS, OpenVoice, RVC, and more)
- Quality metrics (MOS score, similarity, naturalness, SNR)
- Multi-pass synthesis
- Artifact removal
- Prosody control

### Audio Processing
- 17+ audio effects
- Mastering rack
- EQ module
- Style transfer
- Voice mixer

### Project Management
- Projects, tracks, clips
- Timeline management
- Voice profile management

### Training
- Custom voice model training
- Parameter optimization
- Progress monitoring
- Checkpoint management

### Batch Processing
- Queue-based batch synthesis
- Job management
- Progress tracking

### Quality Features
- A/B testing
- Engine recommendation
- Quality benchmarking
- Quality dashboard

---

## Getting Help

### Documentation
- Check the [API_REFERENCE.md](API_REFERENCE.md) for endpoint details
- See [API_USAGE_GUIDE.md](API_USAGE_GUIDE.md) for code examples
- Review [ERROR_CODES.md](ERROR_CODES.md) for error handling

### Interactive Docs
- Use Swagger UI at `/docs` for interactive testing
- Use ReDoc at `/redoc` for formatted documentation

### Support
- Check error messages and recovery suggestions
- Review request/response examples
- Verify endpoint paths and parameters

---

## Version Information

**Current API Version:** 1.0  
**Last Updated:** 2025-01-28

---

## Contributing

To keep documentation up to date:

1. Update endpoint documentation when adding new endpoints
2. Add code examples for new features
3. Document error codes for new error scenarios
4. Update usage guides with new workflows

---

**For the most up-to-date information, see the interactive documentation at `/docs`**

