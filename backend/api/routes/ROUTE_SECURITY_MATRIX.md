# Route Security Matrix

**GAP-CRIT-004**: Documents which routes require authentication and their current status.

## Security Tiers

| Tier | Description | Auth Required |
|------|-------------|---------------|
| **Public** | Health checks, version info, read-only discovery | No |
| **Protected** | User data, synthesis, training, file operations | Yes (when auth enabled) |
| **Admin** | Configuration, backup, system settings | Yes (always) |

## Public Routes (No Auth Required)

These routes are intentionally public:

| Route | File | Reason |
|-------|------|--------|
| `GET /api/health/*` | health.py | Service discovery, monitoring |
| `GET /api/version` | main.py | API version info |
| `GET /api/voice-browser/voices` | voice_browser.py | Voice catalog browsing |
| `GET /api/engines` | engines.py | Engine discovery |
| `GET /` | main.py | Root endpoint |
| `GET /metrics` | metrics.py | Prometheus metrics |

## Protected Routes (Auth When Enabled)

These routes require `Depends(require_auth_if_enabled)`:

### Voice Operations
- `POST /api/voice/synthesize` - voice.py ✓
- `POST /api/voice/clone` - voice.py ✓
- `WS /api/voice/synthesize/stream` - voice.py ✓

### Profile Management
- `POST /api/profiles` - profiles.py ✓
- `PUT /api/profiles/{id}` - profiles.py
- `DELETE /api/profiles/{id}` - profiles.py

### Training
- `POST /api/training/*` - training.py ✓

### Project Management
- `POST /api/projects` - projects.py ✓
- `PUT /api/projects/{id}` - projects.py
- `DELETE /api/projects/{id}` - projects.py

### Timeline/Tracks
- All write operations - timeline.py ✓

### Jobs
- `POST /api/jobs` - jobs.py ✓
- `DELETE /api/jobs/{id}` - jobs.py

## Admin Routes (Always Protected)

These should always require auth even if auth is globally disabled:

### Backup/Restore (GAP-CRIT-004: Auth added 2026-02-11)
- `POST /api/backup` - backup.py ✓
- `POST /api/backup/{id}/restore` - backup.py ✓
- `POST /api/backup/upload` - backup.py ✓
- `DELETE /api/backup/{id}` - backup.py ✓

### Settings (GAP-CRIT-004: Auth added 2026-02-11)
- `POST /api/settings` - settings.py ✓
- `PUT /api/settings/{category}` - settings.py ✓
- `POST /api/settings/reset` - settings.py ✓

### Models (GAP-CRIT-004: Auth added 2026-02-11)
- `POST /api/models` - models.py ✓
- `POST /api/models/import` - models.py ✓
- `PUT /api/models/{engine}/{model_name}/update-checksum` - models.py ✓
- `DELETE /api/models/{engine}/{model_name}` - models.py ✓

### API Keys
- All operations - api_key_manager.py ✓

## Archived Routes (Arch Review Task 1.4)

Moved to `routes/_archived/`: todo_panel, ultimate_dashboard, mcp_dashboard, adr, docs, reward, text_highlighting, script_editor, mix_scene, deepfake_creator.

## Face Swap (Arch Review Task 1.4)

- `POST /api/face-swap/create` - face_swap.py (gated, consent required)
- `GET /api/face-swap/engines` - face_swap.py
- Alias `/api/deepfake-creator/*` for backward compatibility. Gate: `experimental.face_swap` in config/feature_flags.json.

## Implementation Notes

1. Use `Depends(require_auth_if_enabled)` for Protected tier
2. Use `Depends(require_auth_always)` for Admin tier (to be created)
3. Update routes marked "NEEDS AUTH" as part of GAP-CRIT-004
