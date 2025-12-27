# VoiceStudio Quantum+ User Manual

Complete guide to all features and capabilities of VoiceStudio Quantum+.

## Table of Contents

1. [Introduction](#introduction)
2. [Interface Overview](#interface-overview)
3. [Advanced UI Features](#advanced-ui-features)
4. [Voice Profiles](#voice-profiles)
5. [Voice Synthesis](#voice-synthesis)
6. [Quality Improvement Features](#quality-improvement-features)
7. [Quality Testing & Comparison](#quality-testing--comparison)
8. [Timeline Editing](#timeline-editing)
9. [Effects and Processing](#effects-and-processing)
10. [Mixer](#mixer)
11. [Audio Analysis](#audio-analysis)
12. [Macros and Automation](#macros-and-automation)
13. [Training Module](#training-module)
14. [Batch Processing](#batch-processing)
15. [Transcription](#transcription)
16. [Projects](#projects)
17. [Settings and Preferences](#settings-and-preferences)
18. [Keyboard Shortcuts](#keyboard-shortcuts)
19. [Accessibility](#accessibility)
20. [Performance](#performance)

---

## Performance

VoiceStudio Quantum+ includes comprehensive performance optimization and monitoring. See [PERFORMANCE_GUIDE.md](PERFORMANCE_GUIDE.md) for complete performance documentation.

**Key Features:**
- Startup profiling and optimization
- API performance monitoring
- Memory management and monitoring
- VRAM usage tracking
- Performance tuning settings
- Performance baselines and targets

---

## Accessibility

VoiceStudio Quantum+ includes comprehensive accessibility features. See [ACCESSIBILITY.md](ACCESSIBILITY.md) for complete accessibility documentation.

**Key Features:**
- Screen reader support (Windows Narrator, JAWS, NVDA)
- Full keyboard navigation
- High contrast mode support
- Font scaling support
- Clear focus indicators
- WCAG 2.1 Level AA compliant

---

## Introduction

VoiceStudio Quantum+ is a professional voice cloning and audio production studio. This manual covers all features and workflows.

### Key Features

- **Multiple Voice Cloning Engines:** XTTS v2, Chatterbox TTS, Tortoise TTS
- **Quality Metrics:** MOS score, similarity, naturalness, SNR, artifact detection
- **Quality Improvement Features:** 9 advanced quality enhancement features for voice, image, and video
- **Quality Testing & Comparison:** A/B Testing, Engine Recommendation, Quality Benchmarking, Quality Dashboard
- **Reference Audio Quality Analyzer:** Automatic quality analysis with enhancement suggestions
- **Real-Time Quality Feedback:** Monitor quality metrics during synthesis in real-time
- **Timeline Scrubbing Preview:** Audio previews during timeline scrubbing
- **Panel State Persistence:** Save and restore workspace layouts with profiles
- **Professional Timeline:** Multi-track audio editing
- **Effects Chain:** 17 effect types with full parameter control
- **Professional Mixer:** Faders, pan, sends/returns, sub-groups, master bus
- **Audio Analysis:** Waveform, spectrogram, LUFS, phase analysis
- **Macro System:** Node-based automation editor
- **Training Module:** Train custom voice models with data optimization
- **Batch Processing:** Process multiple files efficiently
- **Global Search:** Search across profiles, projects, audio files, markers, and scripts
- **Context-Sensitive Action Bar:** Quick actions in panel headers
- **Enhanced Drag-and-Drop:** Visual feedback during drag operations
- **Panel Resize Handles:** Resize panels with visual feedback
- **Contextual Right-Click Menus:** Context-appropriate menus for all interactive elements
- **Toast Notifications:** User-friendly notifications for success, errors, warnings, and info
- **Multi-Select System:** Select multiple items with visual indicators and batch operations
- **Undo/Redo Visual Indicator:** Visual feedback for undo/redo operations
- **Recent Projects Quick Access:** Quick access to recently opened projects with pinning support

---

## Interface Overview

### Main Window Layout

VoiceStudio uses a professional DAW-style layout:

```
┌─────────────────────────────────────────────────────────┐
│ Menu Bar | Toolbar | Transport Controls | Performance  │
├──────────┬──────────────────────────────┬──────────────┤
│          │                              │              │
│  Nav     │      Timeline Editor         │   Effects   │
│  Rail    │      (Center Panel)          │   & Mixer   │
│          │                              │   (Right)   │
│          │                              │              │
├──────────┴──────────────────────────────┴──────────────┤
│  Macros & Automation (Bottom Panel)                    │
├─────────────────────────────────────────────────────────┤
│ Status | Job Progress | Metrics | Clock                │
└─────────────────────────────────────────────────────────┘
```

### Panel Regions

- **Left Panel:** Voice Profiles (default)
- **Center Panel:** Timeline Editor (default)
- **Right Panel:** Effects & Mixer (default)
- **Bottom Panel:** Macros & Automation (default)

### Navigation Rail

The left navigation rail provides quick access to:
- Profiles
- Timeline
- Effects/Mixer
- Analyzer
- Macros
- Diagnostics
- Training
- Batch Processing

### Command Palette

Press **Ctrl+P** to open the command palette. Search for any command or feature.

### Panel State Persistence and Workspace Profiles

VoiceStudio remembers your panel layout and selections for each project.

**Workspace Profiles:**
- **Default Profile:** Standard layout for general use
- **Custom Profiles:** Create custom layouts for specific workflows
  - Recording: Optimized for recording workflows
  - Mixing: Optimized for mixing and effects
  - Analysis: Optimized for audio analysis
  - Custom: Your own custom layouts

**Using Workspace Profiles:**
1. Arrange panels as desired
2. Open **Settings > Workspace Profiles**
3. Click **"Save Current Layout"**
4. Enter profile name
5. Layout saved automatically

**Switching Profiles:**
- Select profile from **Settings > Workspace Profiles**
- Or use command palette (Ctrl+P) → "Switch Workspace Profile"
- Layout restores automatically

**Project-Specific Layouts:**
- Each project remembers its own panel layout
- Layouts restore when opening projects
- Panel selections and scroll positions preserved
- Timeline zoom and position remembered

**Best Practices:**
- Create profiles for different workflows
- Use project-specific layouts for consistency
- Switch profiles based on current task

---

## Advanced UI Features

VoiceStudio Quantum+ includes advanced UI features that enhance productivity and user experience.

### Global Search (IDEA 5)

**Purpose:** Quickly find profiles, projects, audio files, markers, and scripts across your entire workspace.

**How to Use:**
1. Press **Ctrl+F** or click the search icon in the toolbar
2. Type your search query (minimum 2 characters)
3. Results appear grouped by type
4. Click a result to navigate to that item

**Search Features:**
- **Type Filters:** Use `type:profile`, `type:project`, `type:audio`, `type:marker`, `type:script` to filter results
- **Exact Phrases:** Use quotes for exact matches: `"my voice"`
- **Preview Snippets:** See context around matches
- **Quick Navigation:** Click result to jump to item

**Search Scope:**
- Voice profiles (name, description, tags)
- Projects (name, description)
- Audio files (filename)
- Timeline markers (name, description)
- Scripts (name, text content)

**Best Practices:**
- Use specific search terms for better results
- Use type filters to narrow results
- Use quotes for exact phrase matching

---

### Context-Sensitive Action Bar (IDEA 2)

**Purpose:** Quick access to relevant actions in panel headers based on current context.

**How It Works:**
- Action bar appears in panel headers
- Actions change based on selection or active context
- Up to 4 actions displayed at once
- Keyboard shortcuts shown in tooltips

**Example Actions:**
- **Timeline Panel:** Split Clip, Delete Clip, Add Track, Mute Track
- **Profiles Panel:** New Profile, Import Profile, Export Profile, Delete Profile
- **Effects Panel:** Add Effect, Remove Effect, Bypass Effect, Edit Effect

**Usage:**
1. Select an item or activate a context
2. Action bar updates automatically
3. Click action button to execute
4. Hover to see keyboard shortcut

**Best Practices:**
- Use keyboard shortcuts for faster access
- Actions are context-aware - they change based on selection
- Disabled actions indicate unavailable operations

---

### Enhanced Drag-and-Drop Visual Feedback (IDEA 4)

**Purpose:** Clear visual feedback during drag-and-drop operations to improve usability.

**Visual Feedback:**
- **Drag Preview:** Semi-transparent preview of item being dragged
- **Drop Target Indicators:** Highlighted areas where you can drop
- **Valid/Invalid Indicators:** Clear indication of valid drop targets
- **Smooth Animations:** GPU-accelerated animations for smooth experience

**How to Use:**
1. Click and hold on an item (profile, audio file, clip, etc.)
2. Drag to desired location
3. Watch for drop target highlighting
4. Drop when target is highlighted
5. Visual feedback confirms successful drop

**Supported Operations:**
- Drag profiles to timeline
- Drag audio files to tracks
- Drag clips between tracks
- Drag effects to effect chain
- Drag markers on timeline

**Best Practices:**
- Look for highlighted drop targets
- Invalid targets won't highlight
- Release mouse button when target is highlighted

---

### Panel Resize Handles (IDEA 9)

**Purpose:** Resize panels to customize your workspace layout.

**How to Use:**
1. Hover over panel edge to see resize handle
2. Cursor changes to resize indicator
3. Click and drag to resize panel
4. Release to set new size

**Resize Directions:**
- **Horizontal:** Resize left/right edges
- **Vertical:** Resize top/bottom edges
- **Both:** Resize corners (if supported)

**Features:**
- Visual feedback on hover
- Cursor changes to indicate direction
- Minimum panel sizes respected
- Smooth resizing with animations

**Best Practices:**
- Resize panels to fit your workflow
- Use minimum sizes to prevent panels from becoming too small
- Save workspace profile after resizing

---

### Contextual Right-Click Menus (IDEA 10)

**Purpose:** Quick access to context-appropriate actions via right-click menus.

**Available Contexts:**
- **Timeline:** Right-click on clips, tracks, or empty area
- **Profiles:** Right-click on profile cards
- **Library:** Right-click on files or folders
- **Effects:** Right-click on effects or channels
- **Tracks:** Right-click on track headers
- **Markers:** Right-click on timeline markers

**Menu Features:**
- Context-appropriate menu items
- Keyboard shortcuts shown in tooltips
- Menu items enabled/disabled based on context
- Separators for logical grouping

**Example Menus:**
- **Timeline Clip:** Edit, Split, Delete, Copy, Properties
- **Profile Card:** Edit, Delete, Export, Duplicate, Properties
- **Audio File:** Play, Add to Timeline, Delete, Properties

**Usage:**
1. Right-click on any interactive element
2. Context menu appears
3. Click menu item to execute
4. Keyboard shortcuts shown in tooltips

**Best Practices:**
- Use right-click for quick access to actions
- Keyboard shortcuts shown in tooltips
- Menus are context-aware

---

### Toast Notification System (IDEA 11)

**Purpose:** User-friendly notifications for important events and feedback.

**Toast Types:**
- **Success (Green):** Successful operations (auto-dismiss after 3 seconds)
- **Error (Red):** Errors and failures (manual dismiss required)
- **Warning (Yellow):** Warnings and cautions (auto-dismiss after 5 seconds)
- **Info (Blue):** Informational messages (auto-dismiss after 5 seconds)
- **Progress:** Long-running operations with progress indicator

**Features:**
- Auto-dismiss for success/info/warning
- Manual dismiss for errors
- Up to 4 toasts visible at once
- Click to view details (for errors)
- Smooth animations

**Usage:**
- Toasts appear automatically for important events
- Click toast to view details (errors)
- Click X to dismiss manually
- Errors require manual dismissal

**Best Practices:**
- Read error toasts for important information
- Success toasts auto-dismiss quickly
- Check progress toasts for long operations

---

### Multi-Select System (IDEA 12)

**Purpose:** Select multiple items for batch operations.

**Selection Methods:**
- **Ctrl+Click:** Add item to selection
- **Shift+Click:** Select range of items
- **Ctrl+A:** Select all items in panel
- **Click:** Clear selection and select single item

**Visual Indicators:**
- Selected items are highlighted
- Selection count badge in panel header
- Visual feedback on selection change

**Batch Operations:**
- **Delete:** Delete all selected items
- **Export:** Export selected items
- **Apply Effects:** Apply effects to selected items
- **Move:** Move selected items
- **Copy:** Copy selected items

**Usage:**
1. Hold **Ctrl** and click items to add to selection
2. Or hold **Shift** and click to select range
3. Selection count appears in panel header
4. Right-click to see batch operations
5. Or use keyboard shortcuts for batch operations

**Best Practices:**
- Use Ctrl+Click for non-contiguous selection
- Use Shift+Click for contiguous ranges
- Check selection count before batch operations
- Batch operations are faster than individual operations

---

### Undo/Redo Visual Indicator (IDEA 15)

**Purpose:** Visual feedback for undo/redo operations with action history.

**Visual Indicator:**
- Shows number of available undo operations
- Shows number of available redo operations
- Tooltip shows next undo/redo action name
- Action history preview available

**Usage:**
- **Ctrl+Z:** Undo last action
- **Ctrl+Y:** Redo last undone action
- Visual indicator shows available operations
- Hover to see action names

**Features:**
- Up to 100 actions in history
- Action names displayed in tooltips
- Visual indicator in status bar or toolbar
- Clear indication of undo/redo availability

**Best Practices:**
- Use undo/redo frequently for experimentation
- Check visual indicator to see available operations
- Action history helps track changes

---

## Voice Profiles

Voice profiles store reference audio and settings for voice cloning.

### Creating a Profile

1. Open **Profiles** panel (left panel)
2. Click **"New Profile"** or the **"+"** button
3. Enter profile name
4. Select language (default: English)
5. Optionally add tags for organization
6. Click **"Create"**

### Adding Reference Audio

1. Select a profile
2. Click **"Upload Reference Audio"**
3. Select WAV file (recommended: 5-30 seconds, clear speech)
4. Wait for upload and analysis

**Reference Audio Quality Analysis:**

After uploading reference audio, VoiceStudio automatically analyzes its quality and provides:
- **Overall Quality Score:** 0.0-1.0 (higher is better)
- **Quality Issues:** Detected problems (noise, clipping, low volume, etc.)
- **Enhancement Suggestions:** Recommendations to improve reference audio
- **Quality Metrics:** SNR, dynamic range, frequency response

**Using Quality Analysis:**
- Review quality score before using profile
- Address quality issues for better cloning results
- Follow enhancement suggestions to improve reference audio
- Re-upload enhanced audio if needed

**Best Practices:**
- Use high-quality recordings (16-bit, 44.1 kHz or higher)
- Minimize background noise
- Use clear, natural speech
- 10-30 seconds is optimal length
- Multiple speakers improve cloning quality
- Review and address quality analysis recommendations

### Profile Properties

Each profile has:
- **Name:** Profile identifier
- **Language:** Primary language (affects synthesis)
- **Emotion:** Optional emotion tag
- **Quality Score:** Calculated quality metric (0.0-1.0)
- **Tags:** Custom tags for organization
- **Reference Audio:** Uploaded reference file

### Previewing Profiles

1. Select a profile
2. Click **"Preview"** button
3. Enter test text
4. Select engine and quality settings
5. Click **"Synthesize"**
6. Listen to generated audio
7. Review quality metrics

### Managing Profiles

- **Edit:** Click profile card, modify properties
- **Delete:** Right-click profile, select "Delete"
- **Duplicate:** Right-click profile, select "Duplicate"
- **Export:** Right-click profile, select "Export" (saves as `.vprofile` file)
- **Import:** Click "Import" button, select `.vprofile` file

---

## Voice Synthesis

Synthesize speech from text using voice profiles.

### Basic Synthesis

1. Select a voice profile
2. Go to **Timeline** or **Profiles** panel
3. Enter text in synthesis text box
4. Select engine:
   - **XTTS v2:** Good balance (14 languages)
   - **Chatterbox TTS:** Highest quality (23 languages, emotion control)
   - **Tortoise TTS:** Ultra-realistic HQ mode
5. Select quality mode:
   - **Fast:** Quick previews
   - **Standard:** Balanced quality/speed
   - **High:** Production quality
   - **Ultra:** Maximum quality (slower)
6. Click **"Synthesize"**
7. Wait for generation (10-60 seconds depending on engine and quality)
8. Review quality metrics
9. Add to timeline or export

### Real-Time Quality Feedback

During synthesis, VoiceStudio provides real-time quality feedback so you can monitor the process and make informed decisions.

**Real-Time Metrics:**
- **Quality Progress:** Track quality improvement during multi-pass synthesis
- **MOS Trend:** See how MOS score changes over time
- **Similarity Tracking:** Monitor similarity to reference voice
- **Artifact Detection:** Real-time artifact detection and removal progress

**Quality Alerts:**
The system automatically alerts you to:
- **Quality Drop:** Sudden decrease in quality metrics
- **Low MOS:** MOS score below acceptable threshold
- **Low Quality:** Overall quality concerns

**Quality Comparison:**
- Compare current synthesis with previous syntheses
- View quality trends over time
- Identify quality improvement patterns
- Use historical data for optimization

**Quality Recommendations:**
Receive real-time suggestions for:
- Parameter adjustments to improve quality
- Stopping synthesis early if quality is sufficient
- Retrying with different settings
- Applying post-processing enhancements

**Using Real-Time Feedback:**
1. Start synthesis operation
2. Monitor real-time quality metrics in the synthesis panel
3. Watch for quality alerts and recommendations
4. Make adjustments based on real-time feedback
5. Review quality history after completion

**Best Practices:**
- Monitor quality trends during long operations
- Stop early if quality plateaus and is acceptable
- Use quality alerts to identify issues early
- Review quality history to optimize future syntheses
- Follow recommendations for parameter adjustments

### Quality Metrics

After synthesis, review:
- **MOS Score (1.0-5.0):** Overall audio quality (≥4.0 is excellent)
- **Similarity (0.0-1.0):** Match to reference voice (≥0.85 is excellent)
- **Naturalness (0.0-1.0):** Speech-like characteristics (≥0.80 is excellent)
- **SNR (dB):** Signal-to-noise ratio (higher is better)
- **Artifacts:** Detection of clicks, pops, distortion

### Engine-Specific Settings

#### XTTS v2
- **Languages:** 14 languages supported
- **Speed:** Fast to moderate
- **Quality:** Good to excellent
- **Best for:** Multilingual projects, balanced quality/speed

#### Chatterbox TTS
- **Languages:** 23 languages supported
- **Speed:** Moderate
- **Quality:** Excellent (state-of-the-art)
- **Emotion Control:** Yes
- **Best for:** Highest quality, emotion control, multilingual

#### Tortoise TTS
- **Languages:** English (primary)
- **Speed:** Slow
- **Quality:** Ultra-realistic (HQ mode)
- **Quality Presets:** ultra_fast, fast, high_quality, ultra_quality
- **Best for:** Maximum quality, English-only projects

### Quality Enhancement

Enable quality enhancement for:
- Automatic denoising
- Normalization
- Artifact removal
- SNR improvement

Available in "High" and "Ultra" quality modes.

### Language Selection

Select language for synthesis:
- Affects pronunciation and prosody
- Some engines support more languages than others
- Default language is set in profile

### Emotion Control (Chatterbox)

When using Chatterbox engine:
1. Select emotion from dropdown
2. Available emotions vary by language
3. Affects prosody and delivery style

---

## Quality Improvement Features

VoiceStudio Quantum+ includes 9 advanced quality improvement features (IDEA 61-70) that significantly enhance voice cloning, deepfake, and post-processing quality. These features help you achieve the highest possible quality for your productions.

### Overview

The quality improvement features are organized into four categories:

1. **Voice Quality Enhancement** - Improve synthesized audio quality
2. **Reference Audio Optimization** - Optimize reference audio for better cloning
3. **Image/Video Quality Enhancement** - Enhance face quality and temporal consistency
4. **Training Data Optimization** - Optimize training datasets

---

### Multi-Pass Synthesis

**Purpose:** Generate the highest quality voice synthesis by performing multiple passes and selecting the best segments.

**When to Use:**
- Final production audio requiring maximum quality
- Important projects where quality is critical
- When standard synthesis quality is insufficient

**How to Use:**

1. **Synthesize with Multi-Pass:**
   - In the Voice Synthesis panel, select "Multi-Pass" mode
   - Choose number of passes (3-10, recommended: 3-5)
   - Select focus preset:
     - **Naturalness Focus:** Prioritizes natural-sounding speech
     - **Similarity Focus:** Prioritizes matching the reference voice
     - **Artifact Focus:** Prioritizes reducing artifacts
   - Enable adaptive stopping (stops early if quality plateaus)

2. **Review Results:**
   - View quality score for each pass
   - Compare passes using the pass comparison view
   - Best quality pass is automatically selected
   - Review improvement tracking to see quality gains per pass

3. **Use Best Quality Audio:**
   - Best pass audio is automatically used
   - Other passes available for comparison
   - Export the best quality audio

**Best Practices:**
- Start with 3 passes, increase if needed
- Use adaptive stopping to save time
- Naturalness focus for emotional content
- Similarity focus for voice matching
- Expect 3-10x longer processing time

---

### Reference Audio Pre-Processing

**Purpose:** Analyze and enhance reference audio to optimize voice cloning quality.

**When to Use:**
- Before creating a voice profile
- When reference audio has quality issues
- To select optimal segments for cloning

**How to Use:**

1. **Access Pre-Processing:**
   - Select a profile in the Profiles panel
   - Click "Pre-Process Reference Audio"
   - Or use the reference audio upload dialog

2. **Configure Settings:**
   - **Auto-Enhance:** Automatically enhance audio (recommended: ON)
   - **Select Optimal Segments:** Choose best segments for cloning (recommended: ON)
   - **Max Segments:** Maximum segments to select (recommended: 5)
   - **Min Segment Duration:** Minimum segment length (recommended: 1.0 seconds)

3. **Review Analysis:**
   - Quality score (1-10)
   - Issues detected (noise, clipping, distortion)
   - Recommendations for improvement
   - Optimal segments selected

4. **Use Processed Audio:**
   - Processed audio is saved automatically
   - Use processed audio for better cloning results
   - Original audio preserved for comparison

**Best Practices:**
- Always pre-process reference audio for best results
- Review recommendations and address issues
- Use optimal segments for better cloning
- Keep original audio as backup

---

### Artifact Removal

**Purpose:** Detect and remove audio artifacts (clicks, pops, distortion, glitches, phase issues) from synthesized audio.

**When to Use:**
- After synthesis when artifacts are detected
- When quality metrics show artifact issues
- For final audio cleanup before production

**How to Use:**

1. **Access Artifact Removal:**
   - Select synthesized audio in timeline or project
   - Right-click and select "Remove Artifacts"
   - Or use the Effects panel → Quality → Artifact Removal

2. **Preview Mode:**
   - Click "Preview" to analyze without applying
   - Review detected artifacts:
     - Artifact types (clicks, pops, distortion, glitches, phase issues)
     - Severity scores (1-10)
     - Time locations
     - Confidence levels

3. **Configure Removal:**
   - Select artifact types to remove
   - Choose repair preset:
     - **Click Removal:** Focus on clicks and pops
     - **Distortion Repair:** Focus on distortion and clipping
     - **Comprehensive:** Remove all artifact types
   - Adjust sensitivity if needed

4. **Apply Removal:**
   - Click "Apply" to remove artifacts
   - Review quality improvement score
   - Compare original and repaired audio
   - Save repaired audio

**Best Practices:**
- Always preview before applying
- Use comprehensive preset for maximum cleanup
- Check quality improvement before saving
- Keep original audio for comparison

---

### Voice Characteristic Analysis

**Purpose:** Analyze voice characteristics (pitch, formants, timbre, prosody) to preserve voice identity during cloning.

**When to Use:**
- Before synthesis to understand reference characteristics
- After synthesis to verify voice preservation
- When voice doesn't match reference closely
- To compare multiple voices

**How to Use:**

1. **Access Analysis:**
   - Select audio in timeline or project
   - Right-click and select "Analyze Voice Characteristics"
   - Or use the Analyzer panel → Voice Characteristics

2. **Configure Analysis:**
   - **Include Pitch:** Analyze pitch characteristics (recommended: ON)
   - **Include Formants:** Analyze formant frequencies (recommended: ON)
   - **Include Timbre:** Analyze spectral characteristics (recommended: ON)
   - **Include Prosody:** Analyze prosody patterns (recommended: ON)
   - **Reference Audio:** Optional reference for comparison

3. **Review Results:**
   - **Pitch Analysis:** Mean pitch, pitch variation
   - **Formants:** F1, F2, F3 frequencies
   - **Spectral:** Centroid, rolloff, MFCC features
   - **Prosody:** Pitch contour, rhythm, stress patterns
   - **Similarity Score:** If reference provided (0.0-1.0)
   - **Preservation Score:** Voice identity preservation (0.0-1.0)
   - **Recommendations:** Suggestions for improvement

4. **Use Analysis:**
   - Use similarity score to verify voice matching
   - Follow recommendations to improve quality
   - Compare characteristics across multiple voices
   - Adjust synthesis parameters based on analysis

**Best Practices:**
- Analyze reference audio first to understand target characteristics
- Compare synthesized audio with reference to verify preservation
- Use similarity score ≥0.85 for good voice matching
- Follow recommendations to improve quality

---

### Prosody Control

**Purpose:** Fine-tune prosody patterns, pitch contours, rhythm, and stress for natural speech synthesis.

**When to Use:**
- When intonation needs adjustment
- For emotional or expressive speech
- To match specific prosody patterns
- For question/statement intonation

**How to Use:**

1. **Access Prosody Control:**
   - Select audio in timeline
   - Right-click and select "Prosody Control"
   - Or use Effects panel → Quality → Prosody Control

2. **Configure Prosody:**
   - **Intonation Pattern:**
     - **Rising:** For questions, uncertainty
     - **Falling:** For statements, certainty
     - **Flat:** For monotone delivery
   - **Pitch Contour:** Custom pitch curve (advanced)
   - **Rhythm Adjustments:** Tempo and beat strength
   - **Stress Markers:** Word-level stress placement
   - **Prosody Template:** Pre-configured patterns

3. **Preview and Apply:**
   - Preview prosody adjustments
   - Review quality improvement
   - Apply prosody control
   - Compare original and processed audio

**Best Practices:**
- Use intonation patterns for questions vs statements
- Apply stress markers for emphasis
- Use prosody templates for consistency
- Preview before applying to verify effect

---

### Face Enhancement

**Purpose:** Enhance face quality in generated images and videos for better deepfake results.

**When to Use:**
- After generating images with faces
- When face quality is suboptimal
- For portrait or close-up images
- For video deepfakes

**How to Use:**

1. **Access Face Enhancement:**
   - Select image or video in project
   - Right-click and select "Enhance Face"
   - Or use Image/Video panel → Quality → Face Enhancement

2. **Configure Enhancement:**
   - **Enhancement Preset:**
     - **Portrait:** For headshots and portraits
     - **Full Body:** For full-body images
     - **Close-Up:** For extreme close-ups
   - **Multi-Stage:** Apply multi-stage enhancement (recommended: ON)
   - **Face-Specific:** Apply face-specific algorithms (recommended: ON)

3. **Review Results:**
   - **Original Analysis:**
     - Resolution score (1-10)
     - Artifact score (lower is better)
     - Alignment score (1-10)
     - Realism score (1-10)
     - Overall quality (1-10)
   - **Enhanced Analysis:** Quality after enhancement
   - **Quality Improvement:** Improvement percentage
   - **Recommendations:** Suggestions for further enhancement

4. **Use Enhanced Media:**
   - Enhanced image/video saved automatically
   - Replace original or keep both
   - Export enhanced media

**Best Practices:**
- Use portrait preset for headshots
- Enable multi-stage for maximum quality
- Review recommendations for guidance
- Use face-specific enhancement for best results

---

### Temporal Consistency

**Purpose:** Enhance temporal consistency in video deepfakes, reducing flickering and jitter.

**When to Use:**
- After generating video deepfakes
- When video has flickering or jitter
- For smooth frame-to-frame transitions
- For professional video production

**How to Use:**

1. **Access Temporal Consistency:**
   - Select video in project
   - Right-click and select "Temporal Consistency"
   - Or use Video panel → Quality → Temporal Consistency

2. **Configure Enhancement:**
   - **Smoothing Strength:** 0.0-1.0 (recommended: 0.5)
     - Lower values: Less smoothing, more detail
     - Higher values: More smoothing, less flicker
   - **Motion Consistency:** Ensure motion consistency (recommended: ON)
   - **Detect Artifacts:** Detect temporal artifacts (recommended: ON)

3. **Review Analysis:**
   - **Frame Stability:** Frame-to-frame stability (0.0-1.0)
   - **Motion Smoothness:** Motion continuity (0.0-1.0)
   - **Flicker Score:** Flickering detection (lower is better)
   - **Jitter Score:** Jitter detection (lower is better)
   - **Overall Consistency:** Overall temporal quality (0.0-1.0)
   - **Artifacts Detected:** Types of temporal artifacts

4. **Apply Enhancement:**
   - Processed video saved automatically
   - Review quality improvement
   - Compare original and processed video
   - Export enhanced video

**Best Practices:**
- Start with smoothing strength 0.5
- Increase if flickering is severe
- Decrease if losing too much detail
- Check motion consistency for natural movement

---

### Training Data Optimization

**Purpose:** Analyze training data quality, diversity, and coverage, and select optimal samples for better model training.

**When to Use:**
- Before starting model training
- When training data quality is uncertain
- To improve training dataset quality
- To reduce training time with better samples

**How to Use:**

1. **Access Optimization:**
   - Open Training panel
   - Select or create a dataset
   - Click "Optimize Dataset"
   - Or use Dataset menu → Optimize

2. **Configure Analysis:**
   - **Analyze Quality:** Analyze audio quality (recommended: ON)
   - **Analyze Diversity:** Analyze data diversity (recommended: ON)
   - **Select Optimal:** Select optimal samples (recommended: ON)
   - **Suggest Augmentation:** Suggest augmentation strategies (recommended: ON)

3. **Review Analysis:**
   - **Quality Score:** Average audio quality (1-10)
   - **Diversity Score:** Data diversity (1-10)
   - **Coverage Score:** Coverage completeness (1-10)
   - **Optimal Samples:** Selected high-quality samples
   - **Recommendations:** Suggestions for improvement
   - **Augmentation Suggestions:** Data augmentation strategies

4. **Use Optimized Dataset:**
   - Optimized dataset created automatically
   - Use optimized dataset for training
   - Original dataset preserved
   - Review quality improvement estimate

**Best Practices:**
- Always optimize training data before training
- Review recommendations and address issues
- Use optimal samples for faster, better training
- Follow augmentation suggestions for diversity

---

### Post-Processing Pipeline

**Purpose:** Apply multi-stage enhancement (denoise, normalize, enhance, repair) with quality tracking for each stage.

**When to Use:**
- For final audio polish
- When multiple enhancements needed
- For comprehensive quality improvement
- Before final export

**How to Use:**

1. **Access Post-Processing:**
   - Select audio, image, or video
   - Right-click and select "Post-Process"
   - Or use Quality menu → Post-Processing Pipeline

2. **Configure Stages:**
   - **For Audio:**
     - **Denoise:** Remove background noise
     - **Normalize:** Normalize audio levels
     - **Enhance:** General audio enhancement
     - **Repair:** Repair artifacts and issues
   - **For Images:**
     - **Upscale:** Increase resolution
     - **Enhance:** General enhancement
     - **Denoise:** Remove noise
   - **For Videos:**
     - **Upscale:** Increase resolution
     - **Temporal Smoothing:** Reduce flicker
     - **Enhance:** General enhancement
   - **Optimize Order:** Automatically optimize stage order (recommended: ON)

3. **Preview Mode:**
   - Enable preview to see results without applying
   - Review quality improvement per stage
   - Check total quality improvement
   - Adjust stages as needed

4. **Apply Post-Processing:**
   - Processed media saved automatically
   - Review stage-by-stage results
   - Check total quality improvement
   - Export processed media

**Best Practices:**
- Preview before applying to verify improvement
- Use optimize order for best results
- Apply stages in recommended order
- Review quality improvement before finalizing

---

### Real-Time Quality Preview

**Purpose:** Monitor quality metrics in real-time during synthesis and processing via WebSocket.

**When to Use:**
- During long synthesis operations
- For multi-pass synthesis progress
- During post-processing
- For quality monitoring

**How to Use:**

1. **Enable Quality Preview:**
   - Quality preview enabled automatically during synthesis
   - Visible in synthesis panel
   - Updates in real-time

2. **Monitor Updates:**
   - **Multi-Pass Synthesis:** See quality per pass
   - **Artifact Removal:** See detection and removal progress
   - **Post-Processing:** See stage-by-stage quality improvements
   - **Voice Analysis:** See analysis progress

3. **Use Information:**
   - Make decisions based on real-time quality
   - Stop processes early if quality is sufficient
   - Adjust parameters based on quality trends

**Best Practices:**
- Monitor quality during long operations
- Use quality trends to optimize parameters
- Stop early if quality plateaus
- Review quality history for insights

---

### Quality Improvement Workflows

#### Workflow 1: Maximum Quality Production

1. **Pre-Process Reference Audio**
   - Pre-process reference for optimal cloning

2. **Multi-Pass Synthesis**
   - Use 3-5 passes with naturalness focus
   - Enable adaptive stopping

3. **Remove Artifacts**
   - Preview artifacts
   - Apply comprehensive removal

4. **Post-Processing**
   - Apply denoise, normalize, enhance stages
   - Review quality improvement

#### Workflow 2: Voice Preservation

1. **Analyze Reference Characteristics**
   - Analyze reference voice characteristics
   - Note key features

2. **Synthesize with Multi-Pass**
   - Use similarity focus preset
   - Verify quality scores

3. **Verify Preservation**
   - Analyze synthesized audio
   - Compare with reference
   - Use prosody control if needed

#### Workflow 3: Video Deepfake Enhancement

1. **Generate Video**
   - Generate initial video

2. **Enhance Face Quality**
   - Apply face enhancement with portrait preset

3. **Improve Temporal Consistency**
   - Apply temporal smoothing
   - Adjust smoothing strength as needed

---

## Quality Testing & Comparison

VoiceStudio Quantum+ includes powerful quality testing and comparison features that help you evaluate, compare, and optimize voice synthesis quality. These features enable data-driven decisions about engine selection, parameter tuning, and quality optimization.

### Overview

The quality testing and comparison features include:

1. **A/B Testing** - Side-by-side comparison of two synthesis configurations
2. **Engine Recommendation** - AI-powered engine selection based on quality requirements
3. **Quality Benchmarking** - Comprehensive testing across multiple engines
4. **Quality Dashboard** - Visual overview of quality metrics and trends

---

### A/B Testing

**Purpose:** Compare two different synthesis configurations side-by-side to determine which produces better quality (IDEA 46).

**When to Use:**
- Comparing different engines for the same voice
- Testing different quality settings
- Evaluating parameter changes
- Choosing between synthesis options
- Quality optimization decisions

**How to Use:**

1. **Open A/B Testing Panel:**
   - Navigate to A/B Testing panel (available in center panel region)
   - Or use Command Palette (Ctrl+P) → "A/B Testing"

2. **Configure Test:**
   - **Select Voice Profile:** Choose the voice profile to test
   - **Enter Test Text:** Enter the text to synthesize for comparison
   - **Sample A Configuration:**
     - **Engine:** Select engine (XTTS v2, Chatterbox TTS, Tortoise TTS)
     - **Emotion (Optional):** Enter emotion if desired
     - **Enhance Quality:** Enable quality enhancement (recommended: ON)
   - **Sample B Configuration:**
     - **Engine:** Select different engine or same engine with different settings
     - **Emotion (Optional):** Enter emotion if desired
     - **Enhance Quality:** Enable quality enhancement (recommended: ON)

3. **Run Test:**
   - Click "Run A/B Test" button
   - Wait for both samples to be synthesized
   - Results appear automatically

4. **Review Results:**
   - **Side-by-Side Comparison:**
     - Sample A and Sample B displayed side-by-side
     - Play buttons for each sample
     - Quality metrics for each sample:
       - **MOS Score:** Mean Opinion Score (0.0-5.0, higher is better)
       - **Similarity:** Voice similarity to reference (0.0-1.0, higher is better)
       - **Naturalness:** Speech naturalness (0.0-1.0, higher is better)
       - **SNR:** Signal-to-Noise Ratio (dB, higher is better)
   - **Comparison Summary:**
     - Overall winner (Sample A or Sample B)
     - Per-metric winners
     - Detailed comparison data

5. **Use Results:**
   - Choose the better sample based on metrics and listening
   - Use winning configuration for production
   - Export preferred sample
   - Save test results for reference

**Best Practices:**
- Test with representative text samples
- Use the same voice profile for fair comparison
- Enable quality enhancement for both samples
- Listen to both samples, not just metrics
- Test multiple text samples for comprehensive evaluation
- Document winning configurations for future reference

---

### Engine Recommendation

**Purpose:** Get AI-powered recommendations for the best engine based on your quality requirements (IDEA 47).

**When to Use:**
- Starting a new project and unsure which engine to use
- Need specific quality requirements (MOS, similarity, naturalness)
- Want to optimize for a specific quality tier
- Comparing engines before synthesis

**How to Use:**

1. **Access Engine Recommendation:**
   - Available in Voice Synthesis panel
   - Or use API endpoint: `GET /api/quality/engine-recommendation`
   - Or use Quality panel → Engine Recommendation

2. **Set Quality Requirements:**
   - **Target Tier:** Select quality tier
     - **Fast:** Quick synthesis, lower quality
     - **Standard:** Balanced quality and speed
     - **High:** High quality, slower synthesis
     - **Ultra:** Maximum quality, slowest synthesis
   - **Minimum MOS Score (Optional):** Set minimum MOS requirement (0.0-5.0)
   - **Minimum Similarity (Optional):** Set minimum similarity requirement (0.0-1.0)
   - **Minimum Naturalness (Optional):** Set minimum naturalness requirement (0.0-1.0)

3. **Get Recommendation:**
   - System analyzes requirements
   - Recommends best engine for your needs
   - Provides reasoning for recommendation

4. **Use Recommendation:**
   - Use recommended engine for synthesis
   - Review reasoning to understand why
   - Adjust requirements if needed
   - Re-run recommendation with different requirements

**Best Practices:**
- Set realistic quality requirements
- Use target tier for general guidance
- Set specific minimums for critical projects
- Review reasoning to understand trade-offs
- Test recommended engine before committing

---

### Quality Benchmarking

**Purpose:** Test multiple engines with the same input and compare quality metrics comprehensively (IDEA 52).

**When to Use:**
- Evaluating all available engines
- Comparing engine performance
- Establishing quality baselines
- Testing new engines
- Quality optimization research

**How to Use:**

1. **Access Quality Benchmarking:**
   - Open Quality Benchmarking panel
   - Or use API endpoint: `POST /api/quality/benchmark`
   - Or use Quality panel → Benchmark

2. **Configure Benchmark:**
   - **Voice Profile or Reference Audio:** Select voice profile or provide reference audio ID
   - **Test Text:** Enter text to synthesize for all engines
   - **Language:** Select language (default: "en")
   - **Engines to Test:** Select specific engines or test all available engines
   - **Enhance Quality:** Enable quality enhancement (recommended: ON)

3. **Run Benchmark:**
   - Click "Run Benchmark" button
   - System synthesizes with each selected engine
   - Quality metrics calculated for each engine
   - Results compiled automatically

4. **Review Results:**
   - **Per-Engine Results:**
     - **Engine Name:** Engine tested
     - **Success Status:** Whether benchmark succeeded
     - **Quality Metrics:**
       - MOS Score
       - Similarity
       - Naturalness
       - SNR
       - Artifacts detected
     - **Performance Metrics:**
       - Synthesis time
       - Initialization time
   - **Summary Statistics:**
     - Total engines tested
     - Successful benchmarks
     - Best engine per metric
     - Average metrics across engines

5. **Use Benchmark Results:**
   - Identify best engine for your needs
   - Compare quality vs performance trade-offs
   - Use results to inform engine selection
   - Export benchmark report
   - Save benchmark for historical comparison

**Best Practices:**
- Use representative test text
- Test all engines for comprehensive comparison
- Enable quality enhancement for fair comparison
- Run benchmarks with same voice profile
- Document benchmark results for reference
- Re-run benchmarks when engines are updated

---

### Quality Dashboard

**Purpose:** Visual overview of quality metrics, trends, and insights across your projects (IDEA 49).

**When to Use:**
- Monitoring overall quality trends
- Identifying quality issues
- Tracking quality improvements
- Project quality analysis
- Quality optimization planning

**How to Use:**

1. **Access Quality Dashboard:**
   - Open Quality Dashboard panel
   - Or use API endpoint: `GET /api/quality/dashboard`
   - Or use Quality panel → Dashboard

2. **Configure Dashboard:**
   - **Project Filter (Optional):** Filter by specific project
   - **Time Range:** Select number of days (default: 30 days)

3. **Review Dashboard:**
   - **Overview:**
     - Total syntheses count
     - Average quality metrics (MOS, similarity, naturalness)
     - Quality tier distribution
   - **Trends:**
     - Quality metrics over time
     - Improvement or degradation trends
     - Date-based quality history
   - **Distribution:**
     - Quality metric distributions
     - Quality score ranges
     - Quality patterns
   - **Alerts:**
     - Quality warnings
     - Low quality detections
     - Recommendations
   - **Insights:**
     - Quality insights
     - Optimization suggestions
     - Best practices

4. **Use Dashboard:**
   - Identify quality trends
   - Address quality alerts
   - Follow optimization insights
   - Track quality improvements
   - Plan quality optimization

**Best Practices:**
- Review dashboard regularly
- Address alerts promptly
- Track trends over time
- Use insights for optimization
- Compare projects for patterns

---

### Quality Testing Workflows

#### Workflow 1: Engine Selection for New Project

1. **Use Engine Recommendation**
   - Set quality requirements
   - Get engine recommendation
   - Review reasoning

2. **Run Quality Benchmark**
   - Test recommended engine
   - Compare with other engines
   - Verify recommendation

3. **Use A/B Testing**
   - Compare top 2 engines
   - Make final decision
   - Document choice

#### Workflow 2: Quality Optimization

1. **Review Quality Dashboard**
   - Check overall quality
   - Identify issues
   - Review trends

2. **Run Benchmark**
   - Test current configuration
   - Compare alternatives
   - Identify improvements

3. **A/B Test Improvements**
   - Test optimized configuration
   - Compare with original
   - Verify improvements

4. **Apply Best Configuration**
   - Use winning configuration
   - Monitor in dashboard
   - Track improvements

---

## Timeline Editing

Professional multi-track timeline for audio editing.

### Timeline Overview

- **Tracks:** Multiple audio tracks
- **Clips:** Audio clips on tracks
- **Playhead:** Current playback position
- **Zoom:** Zoom in/out for detailed editing
- **Time Ruler:** Time scale at top

### Adding Audio to Timeline

**Method 1: From Synthesis**
1. Synthesize audio
2. Click **"Add to Timeline"**
3. Clip appears on selected track

**Method 2: Import File**
1. Drag audio file to timeline
2. Or use **File > Import Audio**
3. Select track for placement

**Method 3: From Library**
1. Open library
2. Drag audio file to timeline
3. Drop on desired track

### Editing Clips

**Select Clip:**
- Click on clip to select
- Selected clip is highlighted

**Move Clip:**
- Drag clip horizontally to change position
- Drag vertically to move between tracks

**Trim Clip:**
- Hover over clip edge
- Drag edge to trim start/end
- Visual feedback shows trim area

**Split Clip:**
- Position playhead at split point
- Right-click clip, select **"Split"**
- Or press **S** key

**Delete Clip:**
- Select clip, press **Delete**
- Or right-click, select **"Delete"**

**Copy/Paste:**
- Select clip, **Ctrl+C** to copy
- **Ctrl+V** to paste at playhead position

### Track Management

**Create Track:**
- Right-click track area, select **"New Track"**
- Or use toolbar button

**Delete Track:**
- Right-click track header, select **"Delete Track"**
- Confirms before deletion

**Rename Track:**
- Double-click track name
- Enter new name

**Track Properties:**
- Volume: Track volume fader
- Pan: Left/right panning
- Mute: Mute track
- Solo: Solo track (mute others)

### Playback Controls

- **Play/Pause:** Spacebar or Play button
- **Stop:** S key or Stop button
- **Record:** Ctrl+R or Record button
- **Loop:** Enable loop mode for region

### Zoom and Navigation

**Zoom:**
- **Ctrl+Plus:** Zoom in
- **Ctrl+Minus:** Zoom out
- **Ctrl+0:** Reset zoom
- Mouse wheel: Zoom in/out
- Zoom slider: Adjust zoom level

**Navigation:**
- Click timeline to move playhead
- Drag playhead to scrub
- Arrow keys: Nudge playhead
- Home/End: Jump to start/end

**Timeline Scrubbing with Audio Preview:**
- **Scrubbing:** Drag playhead to scrub through timeline
- **Audio Preview:** Brief audio preview plays while scrubbing
- **Preview Length:** Configurable preview duration (default: 0.1 seconds)
- **Visual Feedback:** Playhead pulses during preview playback

**Using Scrubbing:**
1. Click and drag playhead on timeline
2. Brief audio preview plays at scrubbed position
3. Release to stop scrubbing
4. Use for precise navigation and editing

**Scrubbing Settings:**
- Enable/disable in **Settings > Timeline > Enable Scrubbing Preview**
- Adjust preview duration in **Settings > Timeline > Preview Duration**
- Preview volume controlled by main audio volume

### Waveform Visualization

- Clips show waveform visualization
- Zoom in to see detail
- Helps with precise editing

### Time Selection

1. Click and drag on timeline ruler
2. Selected region is highlighted
3. Use for:
   - Loop playback
   - Apply effects to region
   - Export selection

---

## Effects and Processing

Apply professional audio effects to clips and tracks.

### Effects Panel

Located in right panel (Effects & Mixer).

### Available Effects

#### 1. Normalize
- **Purpose:** Adjust audio level to target
- **Parameters:**
  - Target Level (dB): -3.0 to 0.0 dB
  - Method: Peak or RMS
- **Use:** Standardize audio levels

#### 2. Denoise
- **Purpose:** Remove background noise
- **Parameters:**
  - Strength: 0.0-1.0
  - Frequency Range: Low/Mid/High/Full
- **Use:** Clean up noisy recordings

#### 3. EQ (Equalizer)
- **Purpose:** Adjust frequency response
- **Parameters:**
  - Frequency bands (Low/Mid/High)
  - Gain per band (-12 to +12 dB)
  - Q factor (bandwidth)
- **Use:** Shape tone and remove unwanted frequencies

#### 4. Compressor
- **Purpose:** Control dynamic range
- **Parameters:**
  - Threshold (dB)
  - Ratio (1:1 to 20:1)
  - Attack (ms)
  - Release (ms)
  - Makeup Gain (dB)
- **Use:** Even out levels, add punch

#### 5. Reverb
- **Purpose:** Add space and depth
- **Parameters:**
  - Room Size: Small/Medium/Large
  - Decay Time (seconds)
  - Wet/Dry Mix (0.0-1.0)
- **Use:** Add ambience, create space

#### 6. Delay
- **Purpose:** Add echo/delay effect
- **Parameters:**
  - Delay Time (ms)
  - Feedback (0.0-1.0)
  - Wet/Dry Mix (0.0-1.0)
- **Use:** Create echo, doubling effects

#### 7. Filter
- **Purpose:** Filter frequencies
- **Parameters:**
  - Type: Low-pass/High-pass/Band-pass/Notch
  - Cutoff Frequency (Hz)
  - Resonance (Q)
- **Use:** Remove frequencies, creative filtering

### Creating Effect Chains

1. Select clip or track
2. Open **Effects** panel
3. Click **"Add Effect"**
4. Choose effect type
5. Adjust parameters
6. Add more effects (they process in order)
7. Click **"Apply"** to process audio
8. Or enable **"Live Preview"** for real-time processing

### Effect Presets

**Save Preset:**
1. Configure effect
2. Click **"Save Preset"**
3. Enter preset name
4. Preset saved for reuse

**Load Preset:**
1. Click **"Load Preset"**
2. Select preset from list
3. Parameters applied

**Manage Presets:**
- Edit, delete, or export presets
- Import presets from files

### Applying Effects

**To Clip:**
- Effects process the clip audio
- Creates new processed version
- Original preserved (can undo)

**To Track:**
- Effects process entire track
- Real-time processing during playback
- Can be automated

**To Selection:**
- Select time region
- Apply effects to selection only
- Useful for targeted processing

---

## Mixer

Professional mixing console with faders, routing, and effects.

### Mixer Panel

Located in right panel (Effects & Mixer), Mixer tab.

### Track Strips

Each track has a strip with:
- **Fader:** Volume control (-∞ to +12 dB)
- **Pan:** Left/right panning (-1.0 to +1.0)
- **Mute:** Mute button
- **Solo:** Solo button
- **Sends:** Send knobs for effect buses
- **VU Meter:** Real-time level meter

### Master Bus

Master bus controls final output:
- **Fader:** Master volume
- **Pan:** Master panning
- **Mute:** Master mute
- **VU Meter:** Master level meter
- **Effects:** Master bus effects

### Sends and Returns

**Sends:**
- Route track audio to effect buses
- Adjust send level per track
- Multiple sends per track

**Returns:**
- Effect bus returns
- Apply effects to return bus
- Control return level and pan

**Creating Send/Return:**
1. Click **"Add Send"** on track
2. Select bus number
3. Adjust send level
4. Click **"Add Return"** for bus
5. Apply effects to return
6. Adjust return level

### Sub-Groups

Group tracks for collective control:
1. Create sub-group
2. Route tracks to sub-group
3. Control sub-group volume/pan/effects
4. Sub-group routes to master

**Use Cases:**
- Drums group
- Vocals group
- Effects group
- Parallel processing

### Mixer Presets

**Save Preset:**
1. Configure mixer (faders, routing, etc.)
2. Click **"Save Preset"**
3. Enter preset name
4. Preset saved

**Load Preset:**
1. Click **"Load Preset"**
2. Select preset
3. Mixer state restored

**Manage Presets:**
- Edit, delete, export presets
- Import presets

### VU Meters

Real-time level meters:
- **Track Meters:** Per-track levels
- **Master Meter:** Final output level
- **Peak Hold:** Shows peak levels
- **LUFS Meter:** Integrated loudness (optional)

**Target Levels:**
- **Peak:** -3.0 dB (avoid clipping)
- **LUFS:** -16.0 LUFS (broadcast), -23.0 LUFS (podcast)

---

## Audio Analysis

Comprehensive audio analysis tools.

### Analyzer Panel

Located in navigation rail, Analyzer tab.

### Analysis Modes

#### 1. Waveform
- Visual waveform display
- Amplitude over time
- Zoom for detail
- Selection analysis

#### 2. Spectral
- Frequency spectrum display
- Spectrogram view
- Frequency analysis
- Identify frequencies

#### 3. Radar Chart
- Multi-dimensional analysis
- Quality metrics visualization
- Compare multiple clips
- Export analysis

#### 4. Loudness
- LUFS (Loudness Units Full Scale)
- Integrated loudness
- Momentary loudness
- Peak levels
- Target compliance

#### 5. Phase
- Phase analysis
- Stereo correlation
- Phase issues detection
- Mono compatibility

### Using Analysis

1. Select audio clip or track
2. Open **Analyzer** panel
3. Choose analysis mode
4. View analysis results
5. Use for:
   - Quality assessment
   - Problem identification
   - Optimization guidance
   - Comparison

### Exporting Analysis

- Export analysis data as JSON
- Export charts as images
- Save analysis reports

---

## Macros and Automation

Node-based macro system for automation.

### Macro Panel

Located in bottom panel (Macros & Automation).

### Creating Macros

1. Click **"New Macro"**
2. Enter macro name
3. Macro editor opens

### Node-Based Editor

**Nodes:**
- Input nodes (audio, parameters)
- Processing nodes (effects, synthesis)
- Output nodes (audio, files)

**Connections:**
- Connect node outputs to inputs
- Visual connection lines
- Port-based system

**Node Types:**
- **Audio Input:** Load audio file
- **Synthesize:** Voice synthesis
- **Effect:** Apply effect
- **Mix:** Mix audio
- **Export:** Save audio
- **Parameter:** Control parameter

### Automation Curves

**Creating Automation:**
1. Select parameter
2. Click **"Add Automation"**
3. Draw curve on timeline
4. Bezier curve support
5. Keyframe editing

**Automation Types:**
- Volume automation
- Pan automation
- Effect parameter automation
- Synthesis parameter automation

### Executing Macros

1. Select macro
2. Click **"Run"**
3. Monitor execution
4. View results
5. Check for errors

### Macro Management

- **Save:** Auto-saves changes
- **Export:** Export macro file
- **Import:** Import macro file
- **Duplicate:** Copy macro
- **Delete:** Remove macro

---

## Training Module

Train custom voice models from your own data.

### Training Panel

Located in navigation rail, Training tab.

### Preparing Training Data

**Dataset Requirements:**
- Audio files: WAV format, 16-bit, 44.1 kHz
- Clear speech, minimal noise
- 10+ minutes total (more is better)
- Optional transcripts (improves quality)

**Dataset Organization:**
- Organize files in folders
- Name files descriptively
- Include metadata if available

### Creating Dataset

1. Open **Training** panel
2. Click **"New Dataset"**
3. Enter dataset name
4. Upload audio files
5. Optionally add transcripts
6. Review dataset

### Training Configuration

**Engine Selection:**
- XTTS v2 (recommended)
- Other engines as available

**Training Parameters:**
- **Epochs:** Number of training iterations
- **Batch Size:** Samples per batch
- **Learning Rate:** Training speed
- **Quality Mode:** Fast/Standard/High

**Advanced Settings:**
- Model architecture options
- Regularization
- Data augmentation

### Starting Training

1. Configure training settings
2. Click **"Start Training"**
3. Monitor progress:
   - Training loss
   - Validation metrics
   - ETA
   - Real-time logs

### Training Progress

- Progress bar shows completion
- Loss graphs show training progress
- Validation metrics show quality
- WebSocket streaming for real-time updates

### Model Export

After training completes:
1. Review training results
2. Click **"Export Model"**
3. Choose export format
4. Save model file
5. Model ready for use

### Model Import

Import trained models:
1. Click **"Import Model"**
2. Select model file
3. Model loaded
4. Available for synthesis

---

## Batch Processing

Process multiple synthesis jobs efficiently.

### Batch Panel

Located in navigation rail, Batch tab.

### Creating Batch Job

1. Open **Batch** panel
2. Click **"New Batch Job"**
3. Enter job name
4. Configure settings:
   - Voice profile
   - Engine
   - Quality mode
   - Language
5. Add text entries:
   - Enter text manually
   - Import from file (TXT, CSV)
   - Paste from clipboard
6. Review job
7. Click **"Start Job"**

### Job Queue

- Jobs queue automatically
- Process one at a time
- Monitor queue status
- Pause/resume queue
- Cancel jobs

### Job Status

**Status Types:**
- **Pending:** Waiting in queue
- **Running:** Currently processing
- **Completed:** Finished successfully
- **Failed:** Error occurred
- **Cancelled:** User cancelled

### Progress Tracking

- Progress bar per job
- Overall progress
- ETA calculation
- Real-time updates via WebSocket

### Job Results

**View Results:**
- Click completed job
- View generated audio files
- Review quality metrics
- Export results

**Export Results:**
- Export all audio files
- Export metadata (CSV)
- Export quality reports

### Managing Jobs

- **Pause:** Pause job (if running)
- **Resume:** Resume paused job
- **Cancel:** Cancel job
- **Delete:** Remove job from list
- **Retry:** Retry failed job

---

## Transcription

Transcribe audio to text using Whisper engine.

### Transcription Panel

Located in navigation rail, Transcription tab.

### Loading Audio

**Methods:**
1. Drag audio file to panel
2. Click **"Load Audio"**, select file
3. Import from timeline clip

**Supported Formats:**
- WAV, MP3, FLAC, M4A
- Any format supported by backend

### Language Selection

1. Select language from dropdown
2. 99+ languages supported
3. Auto-detect option available
4. Affects accuracy

### Transcription Settings

**Model Size:**
- **Tiny:** Fastest, lower accuracy
- **Base:** Fast, good accuracy
- **Small:** Balanced
- **Medium:** Better accuracy
- **Large:** Best accuracy, slower

**Options:**
- **Word Timestamps:** Include word-level timing
- **Diarization:** Identify speakers
- **Translate:** Translate to English

### Starting Transcription

1. Load audio
2. Configure settings
3. Click **"Transcribe"**
4. Wait for processing
5. View results

### Transcription Results

**Display:**
- Full transcript text
- Word timestamps (if enabled)
- Speaker labels (if diarization enabled)
- Confidence scores

**Export:**
- Export as text file
- Export as SRT (subtitles)
- Export as VTT (WebVTT)
- Export as JSON (with timestamps)

### Using Transcripts

- Copy transcript text
- Use for voice synthesis
- Create subtitles
- Edit and refine
- Export for other tools

---

## Projects

Organize your work in projects.

### Creating Projects

1. **File > New Project** or **Ctrl+N**
2. Enter project name
3. Choose location (default: Projects folder)
4. Click **"Create"**

### Project Structure

Projects contain:
- **Audio Files:** Synthesized and imported audio
- **Voice Profiles:** Project-specific profiles
- **Timeline:** Track and clip data
- **Effects:** Effect chains and presets
- **Mixer:** Mixer state and presets
- **Macros:** Project macros
- **Settings:** Project-specific settings

### Opening Projects

1. **File > Open Project** or **Ctrl+O**
2. Select `.voiceproj` file
3. Project loads

### Saving Projects

- **File > Save** or **Ctrl+S:** Save project
- **File > Save As:** Save with new name
- Auto-save: Projects auto-save periodically

### Project Settings

Access via **File > Project Settings**:
- Project name
- Sample rate
- Bit depth
- Time signature
- Tempo (if applicable)

### Closing Projects

- **File > Close Project**
- Prompts to save if unsaved changes
- Returns to empty workspace

---

## Settings and Preferences

Configure VoiceStudio to your preferences.

### Accessing Settings

- **File > Settings** or **Ctrl+,**
- Or via Command Palette (**Ctrl+P**, type "settings")

### General Settings

**Appearance:**
- Theme: Light/Dark/System
- Accent color
- Font size
- UI scale

**Behavior:**
- Auto-save interval
- Undo/redo history size
- Default project location
- Language

### Engine Settings

**Default Engine:**
- Select default synthesis engine
- Engine-specific defaults

**Quality Settings:**
- Default quality mode
- Quality enhancement defaults
- Engine preferences

### Audio Settings

**Playback:**
- Output device
- Sample rate
- Buffer size
- Latency

**Recording:**
- Input device
- Sample rate
- Bit depth
- Monitoring

### Timeline Settings

**Display:**
- Time format
- Zoom defaults
- Snap settings
- Grid display

**Editing:**
- Default track count
- Clip fade in/out
- Crossfade settings

**Audio Preview:**
- Enable preview during scrubbing
- Preview duration (default: 150ms)
- Preview volume (default: 60%)

### Workspace Settings

**Panel State Persistence:**
VoiceStudio can save and restore your workspace layout, including panel positions, sizes, and states.

**Workspace Profiles:**
- **Save Workspace:** Save current panel layout as a profile
- **Load Workspace:** Restore a saved workspace profile
- **Default Profile:** Auto-created profile that saves automatically
- **Custom Profiles:** Create named profiles for different workflows

**What Gets Saved:**
- Panel positions and sizes
- Panel visibility
- Timeline zoom level and scroll position
- Panel-specific settings (e.g., analyzer view, mixer configuration)
- Region states (left, center, right, bottom panels)

**Using Workspace Profiles:**
1. Arrange panels as desired
2. **Save Current Layout:**
   - Settings → Workspace → Save Profile
   - Enter profile name
   - Click Save
3. **Load Saved Profile:**
   - Settings → Workspace → Load Profile
   - Select profile from list
   - Layout restores automatically
4. **Manage Profiles:**
   - View all saved profiles
   - Rename or delete profiles
   - Set default profile

**Project-Specific Layouts:**
- Each project can have its own workspace layout
- Layout saves automatically when project saves
- Layout restores when project opens

**Best Practices:**
- Create profiles for different workflows (editing, mixing, analysis)
- Save layout before making major changes
- Use project-specific layouts for different project types
- Restore default profile to reset layout

### Effects Settings

**Default Effects:**
- Effect chain defaults
- Preset locations
- Effect processing mode

### Mixer Settings

**Default Mixer:**
- Track count
- Bus configuration
- Routing defaults

### Keyboard Shortcuts

**Customize Shortcuts:**
1. Open Settings
2. Go to **Keyboard Shortcuts**
3. Find command
4. Click to assign shortcut
5. Save changes

**Reset Shortcuts:**
- Click **"Reset to Defaults"**
- Restores original shortcuts

### Advanced Settings

**Performance:**
- GPU acceleration
- Thread count
- Memory limits
- Cache settings

**Backend:**
- Backend URL (default: localhost:8000)
- Timeout settings
- Retry settings

**Developer:**
- Debug mode
- Log level
- Telemetry

---

## Keyboard Shortcuts

Complete keyboard shortcut reference. For a detailed cheat sheet, see [KEYBOARD_SHORTCUTS.md](KEYBOARD_SHORTCUTS.md).

### File Operations

- **Ctrl+N:** New Project
- **Ctrl+O:** Open Project
- **Ctrl+S:** Save Project
- **Ctrl+Shift+S:** Save As
- **Ctrl+W:** Close Project
- **Ctrl+Q:** Quit Application

### Edit Operations

- **Ctrl+Z:** Undo
- **Ctrl+Y:** Redo
- **Ctrl+X:** Cut
- **Ctrl+C:** Copy
- **Ctrl+V:** Paste
- **Delete:** Delete Selection
- **Ctrl+A:** Select All
- **Ctrl+Click:** Add to Selection (Multi-Select)
- **Shift+Click:** Select Range (Multi-Select)
- **Ctrl+Click:** Add to Selection (Multi-Select)
- **Shift+Click:** Select Range (Multi-Select)

### Playback

- **Space:** Play/Pause
- **S:** Stop
- **Ctrl+R:** Record
- **Home:** Go to Start
- **End:** Go to End
- **Left Arrow:** Previous
- **Right Arrow:** Next

### Navigation

- **Ctrl+P:** Command Palette
- **Tab:** Cycle Panels
- **F1:** Help
- **F5:** Refresh
- **Ctrl+Tab:** Switch Windows

### Zoom

- **Ctrl+Plus:** Zoom In
- **Ctrl+Minus:** Zoom Out
- **Ctrl+0:** Reset Zoom
- **Ctrl+Mouse Wheel:** Zoom

### Timeline

- **S:** Split Clip (at playhead)
- **M:** Mute Track
- **Ctrl+M:** Solo Track
- **T:** New Track
- **Ctrl+T:** Delete Track

### Effects

- **E:** Add Effect
- **Ctrl+E:** Effect Chain Editor
- **F:** Focus Effect Panel

### Mixer

- **M:** Open Mixer
- **Ctrl+M:** Master Bus

### Macros

- **Ctrl+Shift+M:** Macro Editor
- **F9:** Run Macro

### General

- **Ctrl+,:** Settings
- **Ctrl+?:** Keyboard Shortcuts Help
- **Esc:** Cancel/Close Dialog
- **Enter:** Confirm/OK
- **F11:** Fullscreen

---

## Tips and Best Practices

### Voice Cloning

1. **Reference Audio:**
   - Use high-quality recordings
   - Clear, natural speech
   - 10-30 seconds optimal
   - Minimal background noise

2. **Engine Selection:**
   - Chatterbox for highest quality
   - XTTS for multilingual
   - Tortoise for ultra-realistic

3. **Quality Settings:**
   - Use "High" or "Ultra" for production
   - Enable quality enhancement
   - Review quality metrics

### Timeline Editing

1. **Organization:**
   - Name tracks descriptively
   - Use color coding
   - Group related tracks

2. **Editing:**
   - Use zoom for precision
   - Enable snap for alignment
   - Use crossfades for smooth transitions

3. **Performance:**
   - Freeze tracks if needed
   - Render effects for CPU savings
   - Use proxy files for large projects

### Mixing

1. **Levels:**
   - Start with faders at unity (0 dB)
   - Use sends for effects
   - Leave headroom (-3 dB peak)

2. **Organization:**
   - Use sub-groups
   - Route logically
   - Save mixer presets

3. **Mastering:**
   - Check LUFS levels
   - Avoid clipping
   - Use master bus effects sparingly

---

**End of User Manual**

For more information, see:
- [Getting Started Guide](GETTING_STARTED.md)
- [Tutorials](TUTORIALS.md)
- [Installation Guide](INSTALLATION.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)

