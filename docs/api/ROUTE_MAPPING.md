# VoiceStudio API Route Mapping

This document clarifies the distinction between similar API routes and provides guidance
on when to use each endpoint. Created as part of GAP-B06 to address route overlap concerns.

## Audio Visualization Routes

### Quick vs. Advanced Operations

VoiceStudio provides two tiers of audio visualization APIs:

1. **Quick endpoints** (`/api/audio/*`) - Optimized for single-file, real-time operations
2. **Advanced endpoints** (`/api/waveform/*`, `/api/spectrogram/*`) - Full-featured with caching and configuration

### Waveform Routes

| Use Case | Endpoint | Features | Best For |
|----------|----------|----------|----------|
| Quick waveform | `GET /api/audio/waveform` | Fast generation, minimal config | Files < 1 min, real-time preview |
| Configured waveform | `GET /api/waveform/data/{audio_id}` | Custom zoom, channels, RMS/peak | Detailed editing, multi-channel |
| Waveform settings | `GET/PUT /api/waveform/config/{audio_id}` | Persistent display settings | User preferences |
| Signal analysis | `GET /api/waveform/analysis/{audio_id}` | Peak, RMS, crest factor, DC offset | Quality assessment |
| A/B comparison | `POST /api/waveform/compare` | Compare two waveforms | Before/after editing |

### Spectrogram Routes

| Use Case | Endpoint | Features | Best For |
|----------|----------|----------|----------|
| Quick spectrogram | `GET /api/audio/spectrogram` | Fast generation, defaults | Preview, real-time |
| Custom spectrogram | `GET /api/spectrogram/data/{audio_id}` | Custom FFT, color, range | Detailed analysis |
| Spectrogram settings | `GET/PUT /api/spectrogram/config/{audio_id}` | Persistent settings | User preferences |
| Frequency analysis | `GET /api/spectrogram/analyze/{audio_id}` | Dominant frequencies, harmonics | Audio forensics |
| Multi-file overlay | `POST /api/spectrogram/overlay` | Compare spectrograms | A/B testing |

### Audio Level Routes

| Use Case | Endpoint | Features | Best For |
|----------|----------|----------|----------|
| Level meters | `GET /api/audio/meters` | Peak, RMS, LUFS | Real-time monitoring |
| Loudness curve | `GET /api/audio/loudness` | Time-series LUFS | Loudness normalization |

## Plugin Routes

| Use Case | Endpoint | Features | Best For |
|----------|----------|----------|----------|
| Plugin management | `/api/plugins/*` | Install, enable, configure | Local plugin lifecycle |
| Plugin gallery | `/api/plugin-gallery/*` | Browse, search, download | Discovering new plugins |

## Assistant Routes

| Use Case | Endpoint | Features | Best For |
|----------|----------|----------|----------|
| Chat assistant | `/api/assistant/*` | Conversations, history | General AI chat |
| Action execution | `/api/assistant/run/*` | Execute registered actions | Automation |
| Production assistant | `/api/assistant/production/*` | Audio production guidance | Production workflows |

## Version Prefixes

Routes are available under multiple version prefixes:

- `/api/v1/*` - Legacy (deprecated, sunset 2026-06-30)
- `/api/v2/*` - Current stable
- `/api/*` - Alias to current stable

## Deprecation Schedule

| Endpoint | Deprecation Date | Replacement |
|----------|------------------|-------------|
| `/api/v1/*` | 2026-06-30 | `/api/v2/*` |

## Adding New Routes

When adding new routes:

1. Check this document for existing similar functionality
2. If functionality overlaps, extend the existing route instead
3. Document the new route here with use cases
4. Run the route validator at startup to detect conflicts

## See Also

- `backend/api/route_validator.py` - Route conflict detection
- `backend/api/routes/*.py` - Route implementations
- `docs/api/openapi.json` - OpenAPI specification
