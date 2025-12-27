# Governor + Learners Preservation
## Critical: Do Not Modify During Migration

**Purpose:** Ensure Governor (overseer) and 3 learners remain exactly as agreed during migration.

---

## 🎯 Governor (Overseer)

**Role:** Decides engine selection, explores/records A/B tests, applies reward-model guidance.

**Location:** Preserved in `app/core/runtime/governor.py` (or equivalent)

**Responsibilities:**
- Engine selection decisions
- A/B test exploration and recording
- Reward model guidance application
- Orchestration of learners

**Critical Rules:**
- ✅ **DO NOT** modify Governor logic during migration
- ✅ **DO NOT** change Governor's interface with Engine Router
- ✅ **DO** update paths from `C:\VoiceStudio` to `E:\VoiceStudio`
- ✅ **DO** ensure Governor hooks to Engine Router via `EngineHook`

---

## 🧠 Learners (3)

### Learner 1: Quality Scoring (ABX+MOS)

**Role:** Quality scoring using ABX tests and Mean Opinion Score (MOS)

**Location:** Preserved in `app/core/learners/quality_scorer.py` (or equivalent)

**Responsibilities:**
- ABX test execution
- MOS calculation
- Quality metric aggregation
- Dataset scoring

**Dataset Paths:**
- **Old:** `C:\VoiceStudio\datasets\quality\`
- **New:** `E:\VoiceStudio\library\quality\`

### Learner 2: Prosody/Style Tuning

**Role:** Prosody and style parameter tuning

**Location:** Preserved in `app/core/learners/prosody_tuner.py` (or equivalent)

**Responsibilities:**
- Prosody parameter optimization
- Style transfer learning
- Voice characteristic tuning
- Parameter space exploration

**Dataset Paths:**
- **Old:** `C:\VoiceStudio\datasets\prosody\`
- **New:** `E:\VoiceStudio\library\prosody\`

### Learner 3: Dataset Curator

**Role:** Dataset curation and management

**Location:** Preserved in `app/core/learners/dataset_curator.py` (or equivalent)

**Responsibilities:**
- Dataset collection and organization
- Quality filtering
- Metadata management
- Training data preparation

**Dataset Paths:**
- **Old:** `C:\VoiceStudio\datasets\curated\`
- **New:** `E:\VoiceStudio\library\curated\`

---

## 📁 Dataset Path Migration

### Old Structure (C:\VoiceStudio)
```
C:\VoiceStudio\
├── datasets\
│   ├── quality\
│   ├── prosody\
│   └── curated\
└── models\
    └── (learning models)
```

### New Structure (E:\VoiceStudio)
```
E:\VoiceStudio\
├── library\              # Learning datasets
│   ├── quality\
│   ├── prosody\
│   └── curated\
└── models\               # Shared models (via %PROGRAMDATA%)
    └── (learning models)
```

### Path Updates Required

**In Governor/Learners code:**
- `C:\VoiceStudio\datasets\` → `E:\VoiceStudio\library\`
- `C:\VoiceStudio\models\` → `E:\VoiceStudio\models\` (or `%PROGRAMDATA%\VoiceStudio\models\`)

**Migration script will:**
- Find all references to old paths
- Update to new paths
- Preserve Governor + learners logic unchanged

---

## 🔗 Integration Points

### Governor → Engine Router

```python
from app.core.runtime import hook

# Governor uses EngineHook for engine access
engine = hook.get_engine("xtts_v2")
default_engine = hook.get_default_engine("tts")
task_engine = hook.get_engine_for_task("tts")
```

### Learners → Datasets

```python
# Quality Scorer
quality_dataset = Path("E:\\VoiceStudio\\library\\quality")

# Prosody Tuner
prosody_dataset = Path("E:\\VoiceStudio\\library\\prosody")

# Dataset Curator
curated_dataset = Path("E:\\VoiceStudio\\library\\curated")
```

### Governor → Learners

```python
# Governor orchestrates learners
from app.core.learners import quality_scorer, prosody_tuner, dataset_curator

# Quality scoring
score = quality_scorer.evaluate(audio_sample)

# Prosody tuning
params = prosody_tuner.optimize(reference_audio)

# Dataset curation
curated = dataset_curator.curate(raw_dataset)
```

---

## ✅ Preservation Checklist

After migration, verify:

- [ ] Governor file exists and logic unchanged
- [ ] All 3 learners exist and logic unchanged
- [ ] Dataset paths updated to `E:\VoiceStudio\library\`
- [ ] Model paths updated to `E:\VoiceStudio\models\` or `%PROGRAMDATA%\VoiceStudio\models\`
- [ ] Governor hooks to Engine Router via `EngineHook`
- [ ] Learners can access their datasets
- [ ] A/B test recording works
- [ ] Reward model guidance applies
- [ ] No hardcoded `C:\VoiceStudio` paths remain

---

## 🚨 Critical Rules

1. **DO NOT** modify Governor decision logic
2. **DO NOT** change learner algorithms
3. **DO** update paths only
4. **DO** preserve all interfaces
5. **DO** maintain A/B test recording
6. **DO** keep reward model integration

---

**Governor + learners are preserved exactly as agreed. Only paths are updated during migration.**

