# Getting Started with VoiceStudio Quantum+

Welcome to VoiceStudio Quantum+, a professional voice cloning and audio production studio. This guide will help you get up and running quickly.

## What is VoiceStudio?

VoiceStudio Quantum+ is a professional DAW-grade voice cloning studio that allows you to:
- Clone voices from reference audio
- Synthesize speech with multiple state-of-the-art engines
- Edit audio in a multi-track timeline
- Apply professional effects and mixing
- Train custom voice models
- Analyze audio quality with comprehensive metrics

## System Requirements

### Minimum Requirements
- **OS:** Windows 10 (version 1903 or later) or Windows 11
- **RAM:** 8 GB (16 GB recommended)
- **Storage:** 5 GB free space (more for models and projects)
- **GPU:** DirectX 11 compatible (NVIDIA GPU recommended for faster processing)
- **.NET:** .NET 8 Runtime (included in installer)
- **Python:** Python 3.10+ (included in installer)

### Recommended Requirements
- **OS:** Windows 11
- **RAM:** 32 GB or more
- **Storage:** 50+ GB SSD (for models and projects)
- **GPU:** NVIDIA GPU with 8+ GB VRAM (for faster voice synthesis)
- **CPU:** Multi-core processor (6+ cores recommended)

## Installation

### Step 1: Download the Installer

1. Download the latest VoiceStudio installer from the releases page (URL will be provided at release time)
2. The installer file will be named `VoiceStudio-Setup-vX.X.X.exe`

### Step 2: Run the Installer

1. Double-click the installer file
2. If Windows SmartScreen appears, click "More info" then "Run anyway" (the app is not yet code-signed)
3. Follow the installation wizard:
   - Accept the license agreement
   - Choose installation directory (default: `C:\Program Files\VoiceStudio`)
   - Select components to install (all recommended)
   - Click "Install"

### Step 3: Install Additional Libraries (Optional but Recommended)

VoiceStudio includes advanced audio quality features that require additional Python libraries. These are optional but highly recommended for the best experience:

1. **Open Command Prompt or PowerShell** as Administrator
2. **Navigate to VoiceStudio installation directory:**
   ```powershell
   cd "C:\Program Files\VoiceStudio"
   ```
3. **Activate the Python virtual environment:**
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
4. **Install additional libraries:**
   ```powershell
   pip install -r requirements_missing_libraries.txt
   ```

**Note:** Some libraries may require:
- C++ compiler (for fairseq, pyworld)
- CUDA toolkit (for GPU acceleration)
- Additional system dependencies

If installation fails for specific libraries, you can skip them - VoiceStudio will work with reduced functionality. See the Troubleshooting guide for more information.

**Libraries included:**
- Audio quality enhancement (voicefixer, deepfilternet, essentia-tensorflow)
- Quality metrics (pesq, pystoi)
- RVC engine dependencies (fairseq, faiss, pyworld, parselmouth)
- Performance monitoring (py-cpuinfo, GPUtil, nvidia-ml-py)
- And more (see `requirements_missing_libraries.txt` for complete list)

### Step 4: First Launch

1. Launch VoiceStudio from the Start Menu
2. The welcome dialog will appear on first launch
3. Review the welcome information and choose whether to show it on startup

## First Launch Walkthrough

### 1. Main Window Overview

When VoiceStudio opens, you'll see:

- **Top Bar:** Menu, toolbar with transport controls, and performance HUD
- **Left Panel:** Voice Profiles panel (default)
- **Center Panel:** Timeline editor (default)
- **Right Panel:** Effects & Mixer panel (default)
- **Bottom Panel:** Macros & Automation panel (default)
- **Status Bar:** System status, job progress, and metrics

### 2. Check Backend Connection

1. Look at the **Diagnostics** panel (accessible from the navigation rail)
2. Check the "Backend Status" - it should show "Connected"
3. If not connected, ensure the backend is running (it should start automatically)

### 3. Verify Engines

1. Go to **Diagnostics** panel
2. Check "Available Engines" - you should see:
   - XTTS v2 (Coqui TTS)
   - Chatterbox TTS (Resemble AI)
   - Tortoise TTS
   - Whisper (for transcription)

## Basic Setup

### Setting Up Voice Profiles

1. **Open Profiles Panel** (left panel by default)
2. **Create a Profile:**
   - Click the "+" button or "New Profile"
   - Enter a name (e.g., "My Voice")
   - Select language (default: English)
   - Optionally add tags
   - Click "Create"

3. **Add Reference Audio:**
   - Click on the profile card
   - Click "Upload Reference Audio"
   - Select a WAV file (recommended: 5-30 seconds, clear speech)
   - Wait for upload and analysis

4. **Preview the Profile:**
   - Click "Preview" button
   - Enter test text
   - Click "Synthesize"
   - Listen to the generated audio

### Configuring Engines

1. **Select Default Engine:**
   - Go to **Settings** (accessible from menu or command palette)
   - Navigate to "Engines"
   - Choose your preferred default engine:
     - **XTTS v2:** Good balance of quality and speed (14 languages)
     - **Chatterbox TTS:** Highest quality, state-of-the-art (23 languages, emotion control)
     - **Tortoise TTS:** Ultra-realistic HQ mode (slower but highest quality)

2. **Engine Settings:**
   - Adjust quality mode (Fast/Standard/High/Ultra)
   - Configure quality enhancement options
   - Set default language

## Quick Start Tutorial

### Tutorial 1: Create Your First Voice Clone

1. **Prepare Reference Audio:**
   - Record or select 10-30 seconds of clear speech
   - Save as WAV file (16-bit, 44.1 kHz recommended)
   - Ensure minimal background noise

2. **Create Voice Profile:**
   - Open Profiles panel
   - Click "New Profile"
   - Name it "First Clone"
   - Upload your reference audio

3. **Synthesize Speech:**
   - Select the profile
   - Click "Preview" or go to Timeline
   - Enter text: "Hello, this is my first voice clone!"
   - Select engine (try Chatterbox for best quality)
   - Click "Synthesize"
   - Wait for generation (10-30 seconds depending on engine)

4. **Listen and Evaluate:**
   - Play the generated audio
   - Check quality metrics:
     - **MOS Score:** Should be ≥ 4.0 (out of 5.0)
     - **Similarity:** Should be ≥ 0.85 (out of 1.0)
     - **Naturalness:** Should be ≥ 0.80 (out of 1.0)

5. **Add to Timeline:**
   - Click "Add to Timeline"
   - The audio clip appears in the timeline
   - You can now edit, apply effects, or mix it

### Tutorial 2: Basic Timeline Editing

1. **Add Audio to Timeline:**
   - After synthesizing, click "Add to Timeline"
   - Or drag audio files directly to the timeline

2. **Navigate Timeline:**
   - Use mouse wheel to zoom in/out
   - Click and drag to scrub through timeline
   - Use transport controls (Play/Pause/Stop) at the top

3. **Edit Clips:**
   - Click on a clip to select it
   - Drag edges to trim
   - Drag clip to move position
   - Right-click for more options (split, delete, etc.)

4. **Playback:**
   - Press Spacebar or click Play button
   - Use timeline scrubber to jump to any position
   - Adjust playback speed if needed

## Common Workflows

### Workflow 1: Synthesizing Speech

**Complete workflow for creating voice synthesis:**

1. **Select Voice Profile:**
   - Open Profiles panel (left panel)
   - Click on a profile card to select it
   - Verify profile has reference audio uploaded

2. **Enter Text:**
   - Go to Voice Synthesis panel or Timeline
   - Enter text in the text input field
   - Use SSML tags for advanced control (optional)

3. **Choose Engine and Settings:**
   - Select engine from dropdown:
     - **XTTS v2:** Fast, good quality (14 languages)
     - **Chatterbox TTS:** Highest quality, emotion control (23 languages)
     - **Tortoise TTS:** Ultra-realistic HQ mode (slower)
   - Choose quality mode: Fast/Standard/High/Ultra
   - Adjust emotion (if using Chatterbox)

4. **Synthesize:**
   - Click "Synthesize" button
   - Wait for generation (10-60 seconds depending on engine)
   - Progress indicator shows status

5. **Review Quality Metrics:**
   - Check MOS Score (target: ≥ 4.0)
   - Check Similarity (target: ≥ 0.85)
   - Check Naturalness (target: ≥ 0.80)
   - Listen to preview

6. **Add to Timeline or Export:**
   - Click "Add to Timeline" to add to project
   - Or click "Export" to save as audio file
   - Or click "Synthesize Again" to regenerate

### Workflow 2: Applying Effects

**Complete workflow for applying audio effects:**

1. **Select Audio Clip:**
   - Open Timeline panel (center panel)
   - Click on an audio clip to select it
   - Clip highlights when selected

2. **Open Effects Panel:**
   - Open Effects & Mixer panel (right panel)
   - Click "Effects" tab
   - View available effects list

3. **Add Effect:**
   - Click "Add Effect" button
   - Choose effect type from list:
     - **Normalize:** Adjust volume levels
     - **Denoise:** Remove background noise
     - **EQ:** Equalize frequency response
     - **Compressor:** Dynamic range compression
     - **Reverb:** Add reverb/echo
     - **And 12+ more effects**

4. **Configure Effect:**
   - Effect panel opens with parameters
   - Adjust sliders/knobs for desired sound
   - Use presets for quick setup
   - Click "Preview" to hear changes

5. **Apply Effect:**
   - Click "Apply" to process audio
   - Wait for processing (usually < 5 seconds)
   - Effect appears in effects chain
   - Can add multiple effects in sequence

6. **Manage Effects:**
   - Reorder effects by dragging
   - Enable/disable effects with toggle
   - Remove effects with delete button
   - Save effect chains as presets

### Workflow 3: Using the Mixer

**Complete workflow for mixing audio:**

1. **Open Mixer Panel:**
   - Open Effects & Mixer panel (right panel)
   - Click "Mixer" tab
   - View mixer interface with tracks

2. **Adjust Track Levels:**
   - Each track has a fader (volume slider)
   - Drag fader up/down to adjust volume
   - Use mouse wheel for fine adjustment
   - View level meters for visual feedback

3. **Pan Tracks:**
   - Each track has a pan knob
   - Drag left for left channel, right for right channel
   - Center position is balanced stereo

4. **Use Sends/Returns:**
   - Sends route track audio to effects
   - Returns bring processed audio back
   - Create reverb/delay sends for depth
   - Adjust send levels for effect amount

5. **Master Bus:**
   - Master bus controls overall output
   - Adjust master fader for final volume
   - Apply master effects (limiter, EQ)
   - Monitor master levels to prevent clipping

6. **Save Mix Settings:**
   - Mix settings saved with project
   - Can save mixer presets
   - Recall presets for different projects

### Workflow 4: Batch Processing

**Complete workflow for batch synthesis:**

1. **Open Batch Processing Panel:**
   - Click Batch Processing in navigation rail
   - Or use Command Palette (Ctrl+P) → "Batch Processing"

2. **Create Batch Job:**
   - Click "New Batch Job" button
   - Enter job name (e.g., "Chapter 1 Narration")
   - Select voice profile from dropdown

3. **Add Text Entries:**
   - Click "Add Entry" button
   - Enter text for each entry
   - Or import from text file (one line per entry)
   - Can add hundreds of entries

4. **Configure Settings:**
   - Select engine (applies to all entries)
   - Choose quality mode
   - Set output format (WAV, MP3, etc.)
   - Choose output directory

5. **Start Batch Job:**
   - Click "Start Batch" button
   - Job appears in queue
   - Progress shown in real-time
   - Can pause/resume/cancel job

6. **Monitor Progress:**
   - View progress bar for overall job
   - See individual entry status
   - View quality metrics for each entry
   - Download completed files

### Workflow 5: Creating a Complete Project

**End-to-end workflow for a complete voice project:**

1. **Create New Project:**
   - File → New Project (Ctrl+N)
   - Enter project name
   - Choose save location
   - Project opens with empty timeline

2. **Set Up Voice Profile:**
   - Create or select voice profile
   - Upload reference audio
   - Pre-process reference audio (recommended)
   - Verify profile quality score

3. **Synthesize Audio:**
   - Enter script text
   - Synthesize with chosen engine
   - Review quality metrics
   - Add to timeline

4. **Edit Timeline:**
   - Arrange clips on timeline
   - Trim clips to desired length
   - Add markers for important points
   - Adjust clip positions

5. **Apply Effects:**
   - Select clips
   - Add effects (normalize, denoise, etc.)
   - Adjust effect parameters
   - Preview and apply

6. **Mix Audio:**
   - Open mixer panel
   - Adjust track levels
   - Pan tracks as needed
   - Apply master effects

7. **Export Final Audio:**
   - File → Export (Ctrl+E)
   - Choose export format (WAV, MP3, etc.)
   - Set quality settings
   - Click "Export"
   - Save to desired location

### Workflow 6: Training a Custom Voice Model

**Complete workflow for training custom models:**

1. **Prepare Training Data:**
   - Collect 30+ minutes of clean audio
   - Ensure consistent speaker
   - Remove background noise
   - Split into 5-30 second clips

2. **Create Training Dataset:**
   - Go to Training panel
   - Click "New Dataset"
   - Upload audio files
   - Verify dataset quality

3. **Configure Training:**
   - Select base model (XTTS v2 recommended)
   - Set training parameters:
     - Epochs: 50-100 (recommended)
     - Learning rate: 0.0001 (default)
     - Batch size: 4-8 (based on VRAM)
   - Enable quality optimization

4. **Start Training:**
   - Click "Start Training"
   - Monitor progress in real-time
   - View loss curves
   - Training takes 1-4 hours

5. **Evaluate Model:**
   - Test with sample text
   - Compare with original voice
   - Check quality metrics
   - Adjust if needed

6. **Use Trained Model:**
   - Model appears in engine list
   - Use like any other engine
   - Create profile with trained model
   - Synthesize with custom voice

## Quality Features Quick Start

VoiceStudio Quantum+ includes 9 advanced quality improvement features (IDEA 61-70) that significantly enhance voice cloning, deepfake, and post-processing quality. This quick start guide will help you get started with these powerful features.

### What Are Quality Features?

Quality features are advanced algorithms that:
- **Improve voice synthesis quality** through multi-pass refinement
- **Optimize reference audio** for better cloning
- **Remove artifacts** (clicks, pops, distortion) from audio
- **Preserve voice characteristics** during cloning
- **Control prosody** for natural speech
- **Enhance face quality** in images and videos
- **Improve temporal consistency** in videos
- **Optimize training data** for better models
- **Apply comprehensive post-processing** pipelines

### Quick Start: Essential Quality Features

#### 1. Pre-Process Reference Audio (Start Here!)

**Why:** Optimizing reference audio before cloning dramatically improves results.

**How:**
1. Create or select a voice profile
2. Upload reference audio
3. Enable **"Pre-Process Reference Audio"** in upload dialog
4. Or right-click profile → **"Pre-Process Reference Audio"**
5. Review analysis and use processed audio

**Time:** 5-10 minutes  
**Impact:** High - Improves all subsequent cloning

#### 2. Multi-Pass Synthesis (Maximum Quality)

**Why:** Generates the highest quality voice synthesis by refining through multiple passes.

**How:**
1. Select voice profile
2. Click **"Synthesize"**
3. Select **"Multi-Pass"** mode
4. Set passes: **3-5** (recommended)
5. Choose focus preset:
   - **Naturalness Focus:** For natural speech
   - **Similarity Focus:** For matching reference
   - **Artifact Focus:** For reducing artifacts
6. Enable **"Adaptive Stopping"**
7. Click **"Synthesize"**

**Time:** 3-10x normal synthesis time  
**Impact:** Very High - Best quality possible

#### 3. Remove Artifacts (Quick Cleanup)

**Why:** Removes clicks, pops, distortion, and other artifacts from audio.

**How:**
1. Select synthesized audio
2. Right-click → **"Remove Artifacts"**
3. Click **"Preview"** to analyze first
4. Review detected artifacts
5. Select repair preset: **"Comprehensive"**
6. Click **"Apply"**

**Time:** 10-30 seconds  
**Impact:** High - Clean, professional audio

#### 4. Post-Processing Pipeline (Final Polish)

**Why:** Applies comprehensive multi-stage enhancement for final production quality.

**How:**
1. Select audio, image, or video
2. Right-click → **"Post-Process"**
3. For audio, select stages:
   - **Denoise** (recommended)
   - **Normalize** (recommended)
   - **Enhance** (recommended)
   - **Repair** (recommended)
4. Enable **"Optimize Order"**
5. Click **"Preview"** first
6. Click **"Apply"** if satisfied

**Time:** 30 seconds - 5 minutes  
**Impact:** High - Production-ready quality

### Recommended Workflow for Maximum Quality

**Step 1: Pre-Process Reference Audio**
- Always pre-process reference audio before creating profiles
- This sets the foundation for high-quality cloning

**Step 2: Multi-Pass Synthesis**
- Use multi-pass synthesis for final production audio
- Start with 3 passes, increase if needed
- Use naturalness focus for most cases

**Step 3: Remove Artifacts**
- Always check for artifacts after synthesis
- Use preview mode first
- Apply comprehensive removal if artifacts found

**Step 4: Post-Processing**
- Apply post-processing pipeline for final polish
- Use all recommended stages
- Preview before applying

**Result:** Maximum quality voice synthesis ready for production.

### When to Use Each Feature

| Feature | When to Use | Processing Time | Quality Impact |
|---------|-------------|----------------|----------------|
| **Pre-Process Reference** | Before creating profile | 5-10 min | Very High |
| **Multi-Pass Synthesis** | Final production audio | 3-10x normal | Very High |
| **Artifact Removal** | After synthesis | 10-30 sec | High |
| **Voice Analysis** | Verify voice matching | 5-10 sec | Medium |
| **Prosody Control** | Adjust intonation | 5-15 sec | Medium |
| **Face Enhancement** | After image/video generation | 30-60 sec | High |
| **Temporal Consistency** | Video with flickering | 2-5 min | Very High |
| **Training Optimization** | Before model training | 1-5 min | Very High |
| **Post-Processing** | Final polish | 30 sec - 5 min | High |

### Quick Tips

1. **Always Pre-Process Reference Audio**
   - This single step improves all subsequent cloning
   - Takes only 5-10 minutes
   - Dramatically improves quality

2. **Use Multi-Pass for Important Projects**
   - 3-5 passes is usually sufficient
   - Enable adaptive stopping to save time
   - Quality improvement is significant

3. **Preview Before Applying**
   - Always preview artifacts/post-processing before applying
   - Saves time if quality improvement is minimal
   - Helps you understand what will change

4. **Monitor Quality in Real-Time**
   - Quality preview shows progress during processing
   - Helps you make decisions about continuing
   - Provides insights into quality trends

5. **Combine Features Wisely**
   - Pre-process → Multi-pass → Artifact removal → Post-process
   - Don't over-process - use features based on actual needs
   - Each feature adds processing time

### Learning More

- **Detailed Tutorials:** See [Tutorials](TUTORIALS.md) for step-by-step guides (Tutorials 8-17)
- **User Manual:** See [User Manual](USER_MANUAL.md) for complete feature documentation
- **API Reference:** See [API Reference](../api/API_REFERENCE.md) for developer documentation
- **Quick Reference:** See [Quality Features Quick Reference](../api/QUALITY_FEATURES_QUICK_REFERENCE.md) for decision trees and workflows

### Next Steps

1. **Try Pre-Processing:** Start with reference audio pre-processing
2. **Experiment with Multi-Pass:** Try multi-pass synthesis on a test project
3. **Learn Artifact Removal:** Practice removing artifacts from audio
4. **Explore Post-Processing:** Try the post-processing pipeline
5. **Read Tutorials:** Follow detailed tutorials for each feature

---

## Keyboard Shortcuts

### Essential Shortcuts

- **Ctrl+N:** New Project
- **Ctrl+O:** Open Project
- **Ctrl+S:** Save Project
- **Space:** Play/Pause
- **S:** Stop
- **Ctrl+R:** Record
- **Ctrl+Z:** Undo
- **Ctrl+Y:** Redo
- **Ctrl+P:** Command Palette
- **Ctrl+Plus:** Zoom In
- **Ctrl+Minus:** Zoom Out
- **Ctrl+0:** Reset Zoom

### Navigation

- **Tab:** Cycle through panels
- **F1:** Help
- **F5:** Refresh

## Next Steps

Now that you're set up, explore:

1. **[User Manual](USER_MANUAL.md)** - Complete feature documentation
2. **[Tutorials](TUTORIALS.md)** - Step-by-step workflows
3. **[Installation Guide](INSTALLATION.md)** - Detailed installation instructions
4. **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Solutions to common issues

## Getting Help

- **Documentation:** See the `docs/` folder for comprehensive guides
- **Issues:** Report bugs on GitHub Issues
- **Community:** Join our Discord/Forum (if available)

## Tips for Best Results

1. **Reference Audio Quality:**
   - Use clear, high-quality recordings
   - Minimize background noise
   - 10-30 seconds is optimal
   - Multiple speakers for better cloning

2. **Engine Selection:**
   - **Speed:** XTTS v2 or Chatterbox
   - **Quality:** Tortoise (HQ mode) or Chatterbox
   - **Emotion Control:** Chatterbox
   - **Multilingual:** XTTS v2 (14 languages) or Chatterbox (23 languages)

3. **Quality Settings:**
   - Use "High" or "Ultra" for final production
   - Use "Fast" for quick previews
   - Enable quality enhancement for best results
   - **Use Quality Features:** Pre-process reference audio, multi-pass synthesis, artifact removal, and post-processing for maximum quality
   - **Use Quality Features:** Pre-process reference audio, multi-pass synthesis, artifact removal, and post-processing for maximum quality

4. **Performance:**
   - Use GPU acceleration when available
   - Close other applications for faster processing
   - Use batch processing for multiple files

---

**Congratulations!** You're now ready to start creating with VoiceStudio Quantum+. Explore the features and experiment with different engines and settings to find what works best for your projects.

