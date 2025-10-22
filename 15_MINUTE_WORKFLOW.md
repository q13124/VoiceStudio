# 15-Minute Daily Workflow

## ⚡ Ultra-Fast Execution

**Goal**: Ship one feature per day in 15 minutes.

---

## 🎯 The 15-Minute Breakdown

### 0-2 min: ChatGPT Plans
```
"VoiceStudio Day [X]: [FEATURE]
Generate minimal code only. No explanations."
```

### 2-5 min: Cursor Executes
```
Ctrl+K: "Execute: [paste]"
Ctrl+Enter: Accept
```

### 5-10 min: Quick Test
```bash
python test_feature.py
```

### 10-12 min: ChatGPT Review (critical only)
```
"Quick review: [paste]. Critical issues only."
```

### 12-15 min: Cursor Fixes
```
Ctrl+L: "Fix: [paste]"
```

**Done.**

---

## 📋 Minimal ChatGPT Prompt

```
VoiceStudio Day [X]: [FEATURE]

Output ONLY:
1. File path
2. Complete code
3. Test command

No explanations.
```

### Example Output
```
File: workers/ops/voice_fusion.py

from resemblyzer import VoiceEncoder
import numpy as np

class VoiceFusion:
    def fuse(self, files):
        embs = [VoiceEncoder().embed_utterance(load(f)) for f in files]
        return np.mean(embs, axis=0)

Test: python -c "from workers.ops.voice_fusion import VoiceFusion; print('OK')"
```

---

## ⚡ Speed Optimizations

### 1. Skip Tests During Build
Build Week 1-3, test Week 4
**Saves 5 min/day**

### 2. Batch Reviews
Review Friday instead of daily
**Saves 2 min/day**

### 3. Auto-Accept Cursor
Don't review during development
**Saves 3 min/day**

---

## 📅 30-Day Plan (15 min/day)

**Week 1**: Foundation (75 min total)
**Week 2**: Features (75 min total)
**Week 3**: Advanced (75 min total)
**Week 4**: Polish (75 min total)

**Total: 5 hours over 30 days**

---

## 🚀 Daily Routine

### 9:00-9:02: ChatGPT
```
"Day [X]: [FEATURE]. Code only."
```

### 9:02-9:05: Cursor
```
Ctrl+K: [paste]
Ctrl+Enter
```

### 9:05-9:10: Test
```bash
python -c "import module; print('OK')"
```

### 9:10-9:15: Commit
```bash
git add . && git commit -m "Day [X]" && git push
```

**Done. 15 minutes.**

---

## 💡 The Secret

**ChatGPT outputs minimal executable code.**
**Cursor implements instantly.**
**You ship without review.**
**Test everything Week 4.**

**5 hours total = Professional voice cloner.**
