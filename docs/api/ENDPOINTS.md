# VoiceStudio Quantum+ API Endpoints

Complete list of all 133+ API endpoints organized by category.

## Table of Contents

1. [Core Endpoints](#core-endpoints)
2. [Voice Profiles](#voice-profiles)
3. [Voice Synthesis](#voice-synthesis)
4. [Projects](#projects)
5. [Tracks and Clips](#tracks-and-clips)
6. [Audio Analysis](#audio-analysis)
7. [Effects](#effects)
8. [Mixer](#mixer)
9. [Macros](#macros)
10. [Training](#training)
11. [Batch Processing](#batch-processing)
12. [Transcription](#transcription)
13. [Models](#models)
14. [Settings](#settings)
15. [Backup & Restore](#backup--restore)
16. [Tag Management](#tag-management)
17. [Quality Improvement Features](#quality-improvement-features)
18. [Quality Testing & Comparison Features](#quality-testing--comparison-features)
19. [Search](#search)
20. [MCP Dashboard](#mcp-dashboard)
21. [Additional Endpoints](#additional-endpoints)

---

## Core Endpoints

### Health Check

**GET** `/health`
- Health check endpoint
- Returns: `{"status": "ok", "version": "1.0"}`

**GET** `/api/health`
- API health check
- Returns: `{"status": "ok", "version": "1.0"}`

### Root

**GET** `/`
- API information
- Returns: `{"message": "VoiceStudio Backend API", "version": "1.0"}`

---

## Voice Profiles

**Base Path:** `/api/profiles`

### List Profiles

**GET** `/api/profiles`
- List all voice profiles
- Returns: `List[VoiceProfile]`

**Response:**
```json
[
  {
    "id": "profile-123",
    "name": "My Voice",
    "language": "en",
    "emotion": null,
    "quality_score": 0.92,
    "tags": ["male", "english"],
    "reference_audio_url": "/api/voice/audio/ref-123"
  }
]
```

### Get Profile

**GET** `/api/profiles/{profile_id}`
- Get specific voice profile
- Parameters:
  - `profile_id` (path): Profile ID
- Returns: `VoiceProfile`
- Errors: 404 if not found

### Create Profile

**POST** `/api/profiles`
- Create new voice profile
- Request Body: `ProfileCreateRequest`
  - `name` (string, required): Profile name
  - `language` (string, default: "en"): Language code
  - `emotion` (string, optional): Emotion tag
  - `tags` (array, optional): Tags
- Returns: `VoiceProfile`

### Update Profile

**PUT** `/api/profiles/{profile_id}`
- Update existing profile
- Parameters:
  - `profile_id` (path): Profile ID
- Request Body: `ProfileUpdateRequest`
  - `name` (string, optional)
  - `language` (string, optional)
  - `emotion` (string, optional)
  - `tags` (array, optional)
- Returns: `VoiceProfile`
- Errors: 404 if not found

### Delete Profile

**DELETE** `/api/profiles/{profile_id}`
- Delete voice profile
- Parameters:
  - `profile_id` (path): Profile ID
- Returns: `ApiOk`
- Errors: 404 if not found

---

## Voice Synthesis

**Base Path:** `/api/voice`

### Synthesize Speech

**POST** `/api/voice/synthesize`
- Synthesize speech from text
- Request Body: `VoiceSynthesizeRequest`
  - `engine` (string, required): Engine name (chatterbox, xtts_v2, tortoise)
  - `profile_id` (string, required): Voice profile ID
  - `text` (string, required): Text to synthesize (1-10000 chars)
  - `language` (string, default: "en"): Language code
  - `emotion` (string, optional): Emotion (Chatterbox only)
  - `enhance_quality` (boolean, default: false): Enable quality enhancement
- Returns: `VoiceSynthesizeResponse`
  - `audio_id`: Generated audio ID
  - `audio_url`: URL to download audio
  - `quality_metrics`: QualityMetrics object
    - `mos_score`: MOS score (1.0-5.0)
    - `similarity`: Similarity to reference (0.0-1.0)
    - `naturalness`: Naturalness score (0.0-1.0)
    - `snr_db`: Signal-to-noise ratio (dB)
    - `artifacts_detected`: Boolean
- Errors: 400 (invalid engine/profile), 404 (profile not found), 500 (synthesis failed)

### Analyze Audio Quality

**POST** `/api/voice/analyze`
- Analyze audio quality metrics
- Request Body: `VoiceAnalyzeRequest`
  - `audio_id` (string, required): Audio file ID
  - `reference_audio_id` (string, optional): Reference audio for similarity
- Returns: `VoiceAnalyzeResponse`
  - `quality_metrics`: Complete quality metrics
- Errors: 404 (audio not found), 500 (analysis failed)

### Clone Voice

**POST** `/api/voice/clone`
- Clone voice from reference audio
- Request Body: `VoiceCloneRequest`
  - `reference_audio_id` (string, required): Reference audio ID
  - `name` (string, required): Profile name
  - `language` (string, default: "en"): Language code
- Returns: `VoiceCloneResponse`
  - `profile_id`: Created profile ID
  - `quality_metrics`: Quality metrics
- Errors: 404 (reference not found), 500 (cloning failed)

### Get Audio File

**GET** `/api/voice/audio/{audio_id}`
- Download audio file
- Parameters:
  - `audio_id` (path): Audio ID
- Returns: Audio file (WAV format)
- Errors: 404 if not found

---

## Projects

**Base Path:** `/api/projects`

### List Projects

**GET** `/api/projects`
- List all projects
- Returns: `List[Project]`

### Get Project

**GET** `/api/projects/{project_id}`
- Get specific project
- Parameters:
  - `project_id` (path): Project ID
- Returns: `Project`
- Errors: 404 if not found

### Create Project

**POST** `/api/projects`
- Create new project
- Request Body: `ProjectCreateRequest`
  - `name` (string, required): Project name
  - `description` (string, optional): Project description
- Returns: `Project`

### Update Project

**PUT** `/api/projects/{project_id}`
- Update existing project
- Parameters:
  - `project_id` (path): Project ID
- Request Body: `ProjectUpdateRequest`
  - `name` (string, optional)
  - `description` (string, optional)
  - `voice_profile_ids` (array, optional): Associated profile IDs
- Returns: `Project`
- Errors: 404 if not found

### Delete Project

**DELETE** `/api/projects/{project_id}`
- Delete project
- Parameters:
  - `project_id` (path): Project ID
- Returns: `ApiOk`
- Errors: 404 if not found

### Save Audio to Project

**POST** `/api/projects/{project_id}/audio/save`
- Save audio file to project directory
- Parameters:
  - `project_id` (path): Project ID
- Request Body: `SaveAudioRequest`
  - `audio_id` (string, required): Audio ID to save
  - `filename` (string, optional): Custom filename
- Returns: `ProjectAudioFileResponse`
- Errors: 404 (project/audio not found)

### List Project Audio Files

**GET** `/api/projects/{project_id}/audio`
- List all audio files in project
- Parameters:
  - `project_id` (path): Project ID
- Returns: `List[ProjectAudioFile]`
- Errors: 404 if project not found

### Get Project Audio File

**GET** `/api/projects/{project_id}/audio/{filename}`
- Download project audio file
- Parameters:
  - `project_id` (path): Project ID
  - `filename` (path): Audio filename
- Returns: Audio file (WAV format)
- Errors: 404 if not found

---

## Tracks and Clips

**Base Path:** `/api/projects/{project_id}/tracks`

### List Tracks

**GET** `/api/projects/{project_id}/tracks`
- List all tracks in project
- Parameters:
  - `project_id` (path): Project ID
- Returns: `List[AudioTrack]`
- Errors: 404 if project not found

### Get Track

**GET** `/api/projects/{project_id}/tracks/{track_id}`
- Get specific track
- Parameters:
  - `project_id` (path): Project ID
  - `track_id` (path): Track ID
- Returns: `AudioTrack`
- Errors: 404 if not found

### Create Track

**POST** `/api/projects/{project_id}/tracks`
- Create new track
- Parameters:
  - `project_id` (path): Project ID
- Request Body: `TrackCreateRequest`
  - `name` (string, required): Track name
  - `engine` (string, optional): Default engine for track
- Returns: `AudioTrack`
- Errors: 404 if project not found

### Update Track

**PUT** `/api/projects/{project_id}/tracks/{track_id}`
- Update existing track
- Parameters:
  - `project_id` (path): Project ID
  - `track_id` (path): Track ID
- Request Body: `TrackUpdateRequest`
  - `name` (string, optional)
  - `engine` (string, optional)
- Returns: `AudioTrack`
- Errors: 404 if not found

### Delete Track

**DELETE** `/api/projects/{project_id}/tracks/{track_id}`
- Delete track and all clips
- Parameters:
  - `project_id` (path): Project ID
  - `track_id` (path): Track ID
- Returns: `ApiOk`
- Errors: 404 if not found

### Add Clip to Track

**POST** `/api/projects/{project_id}/tracks/{track_id}/clips`
- Add audio clip to track
- Parameters:
  - `project_id` (path): Project ID
  - `track_id` (path): Track ID
- Request Body: `ClipCreateRequest`
  - `name` (string, required): Clip name
  - `profile_id` (string, required): Voice profile ID
  - `audio_id` (string, required): Audio ID
  - `audio_url` (string, required): Audio URL
  - `duration_seconds` (float, required): Clip duration
  - `start_time` (float, required): Start time on timeline
  - `engine` (string, optional): Engine used
  - `quality_score` (float, optional): Quality score
- Returns: `AudioClip`
- Errors: 404 if track not found

### Update Clip

**PUT** `/api/projects/{project_id}/tracks/{track_id}/clips/{clip_id}`
- Update clip in track
- Parameters:
  - `project_id` (path): Project ID
  - `track_id` (path): Track ID
  - `clip_id` (path): Clip ID
- Request Body: `ClipUpdateRequest`
  - `name` (string, optional)
  - `start_time` (float, optional): New start time
- Returns: `AudioClip`
- Errors: 404 if not found

### Delete Clip

**DELETE** `/api/projects/{project_id}/tracks/{track_id}/clips/{clip_id}`
- Delete clip from track
- Parameters:
  - `project_id` (path): Project ID
  - `track_id` (path): Track ID
  - `clip_id` (path): Clip ID
- Returns: `ApiOk`
- Errors: 404 if not found

---

## Audio Analysis

**Base Path:** `/api/audio`

### Get Waveform Data

**GET** `/api/audio/waveform`
- Get waveform visualization data
- Query Parameters:
  - `audio_id` (string, required): Audio ID
  - `width` (int, default: 1000): Waveform width in pixels
  - `mode` (string, default: "peak"): Mode (peak, rms)
- Returns: `WaveformData`
  - `points`: Array of amplitude values
  - `duration`: Audio duration
  - `sample_rate`: Sample rate
- Errors: 404 if audio not found

### Get Spectrogram Data

**GET** `/api/audio/spectrogram`
- Get spectrogram visualization data
- Query Parameters:
  - `audio_id` (string, required): Audio ID
  - `width` (int, default: 1000): Spectrogram width
  - `height` (int, default: 256): Spectrogram height
  - `n_fft` (int, default: 2048): FFT size
  - `hop_length` (int, default: 512): Hop length
- Returns: `SpectrogramData`
  - `frames`: Array of frequency frames
  - `frequencies`: Frequency bins
  - `times`: Time points
- Errors: 404 if audio not found

### Get Loudness Analysis

**GET** `/api/audio/loudness`
- Get loudness analysis (LUFS)
- Query Parameters:
  - `audio_id` (string, required): Audio ID
- Returns: `LoudnessData`
  - `integrated_lufs`: Integrated LUFS
  - `momentary_lufs`: Momentary LUFS array
  - `peak_lufs`: Peak LUFS
  - `true_peak_db`: True peak (dB)
- Errors: 404 if audio not found

### Get VU Meters

**GET** `/api/audio/meters`
- Get real-time VU meter data
- Query Parameters:
  - `project_id` (string, optional): Project ID for project meters
- Returns: `AudioMeters`
  - `channels`: Per-channel meter data
  - `master`: Master bus meter data
- Updates via WebSocket: `/ws/realtime?topics=meters`

### Get Radar Chart Data

**GET** `/api/audio/radar`
- Get multi-dimensional analysis data for radar chart
- Query Parameters:
  - `audio_id` (string, required): Audio ID
- Returns: `RadarData`
  - `metrics`: Dictionary of metric values
  - `categories`: Metric categories
- Errors: 404 if audio not found

### Get Phase Analysis

**GET** `/api/audio/phase`
- Get phase analysis data
- Query Parameters:
  - `audio_id` (string, required): Audio ID
- Returns: `PhaseData`
  - `correlation`: Stereo correlation
  - `phase_diff`: Phase difference
  - `mono_compatible`: Mono compatibility flag
- Errors: 404 if audio not found

---

## Effects

**Base Path:** `/api/effects`

### List Effect Chains

**GET** `/api/effects/chains/{project_id}`
- List all effect chains for project
- Parameters:
  - `project_id` (path): Project ID
- Returns: `List[EffectChain]`

### Get Effect Chain

**GET** `/api/effects/chains/{project_id}/{chain_id}`
- Get specific effect chain
- Parameters:
  - `project_id` (path): Project ID
  - `chain_id` (path): Chain ID
- Returns: `EffectChain`
- Errors: 404 if not found

### Create Effect Chain

**POST** `/api/effects/chains/{project_id}`
- Create new effect chain
- Parameters:
  - `project_id` (path): Project ID
- Request Body: `EffectChainCreateRequest`
  - `name` (string, required): Chain name
  - `effects` (array, required): List of effects
- Returns: `EffectChain`

### Update Effect Chain

**PUT** `/api/effects/chains/{project_id}/{chain_id}`
- Update effect chain
- Parameters:
  - `project_id` (path): Project ID
  - `chain_id` (path): Chain ID
- Request Body: `EffectChainUpdateRequest`
- Returns: `EffectChain`
- Errors: 404 if not found

### Delete Effect Chain

**DELETE** `/api/effects/chains/{project_id}/{chain_id}`
- Delete effect chain
- Parameters:
  - `project_id` (path): Project ID
  - `chain_id` (path): Chain ID
- Returns: `ApiOk`
- Errors: 404 if not found

### Process Audio with Chain

**POST** `/api/effects/chains/{project_id}/{chain_id}/process`
- Apply effect chain to audio
- **Enhanced with PostFXProcessor integration** for professional-quality audio effects
  - Uses PostFXProcessor with pedalboard support when available
  - Falls back to basic implementations if PostFXProcessor unavailable
  - Provides studio-quality effects processing
- Parameters:
  - `project_id` (path): Project ID
  - `chain_id` (path): Chain ID
- Request Body: `ProcessAudioRequest`
  - `audio_id` (string, required): Audio ID to process
  - `output_filename` (string, optional): Output filename
- Returns: `ProcessedAudioResponse`
  - `audio_id`: Processed audio ID
  - `audio_url`: URL to processed audio
- Errors: 404 if chain/audio not found, 500 if processing fails
- **Performance:** Typically completes in < 3.0s

### List Effect Presets

**GET** `/api/effects/presets`
- List all effect presets
- Returns: `List[EffectPreset]`

### Create Effect Preset

**POST** `/api/effects/presets`
- Create effect preset
- Request Body: `EffectPresetCreateRequest`
  - `name` (string, required): Preset name
  - `effect_type` (string, required): Effect type
  - `parameters` (object, required): Effect parameters
- Returns: `EffectPreset`

### Delete Effect Preset

**DELETE** `/api/effects/presets/{preset_id}`
- Delete effect preset
- Parameters:
  - `preset_id` (path): Preset ID
- Returns: `ApiOk`
- Errors: 404 if not found

### Available Audio Effects

VoiceStudio Quantum+ supports **10 audio effects** for processing audio:

#### Basic Effects
1. **normalize** - Audio normalization
   - Parameters: `Target LUFS` (float, -30.0 to -6.0 dB)

2. **denoise** - Noise reduction
   - Parameters: `Strength` (float, 0.0 to 1.0)

3. **eq** - 3-band equalizer
   - Parameters: `Low Gain` (float, dB), `Mid Gain` (float, dB), `High Gain` (float, dB)

4. **compressor** - Dynamic range compression
   - Parameters: `Threshold` (float, dB), `Ratio` (float), `Attack` (float, ms), `Release` (float, ms)

5. **reverb** - Reverb effect
   - Parameters: `Room Size` (float, 0.0 to 1.0), `Damping` (float, 0.0 to 1.0), `Wet Level` (float, 0.0 to 1.0)

6. **delay** - Delay/echo effect
   - Parameters: `Delay Time` (float, ms), `Feedback` (float, 0.0 to 1.0), `Mix` (float, 0.0 to 1.0)

7. **filter** - Lowpass/Highpass/Bandpass filter
   - Parameters: `Cutoff` (float, Hz), `Resonance` (float), `Filter Type` (int, 0=lowpass, 1=highpass, 2=bandpass)

#### Advanced Effects
8. **chorus** - Chorus effect
   - Parameters: `Depth` (float, 0.0 to 1.0), `Rate` (float, 0.1 to 10.0 Hz), `Feedback` (float, 0.0 to 1.0), `Mix` (float, 0.0 to 1.0)

9. **pitch_correction** - Auto-tune/pitch correction
   - Parameters: `Key` (float, 0-11: C, C#, D, ..., B), `Scale` (float, 0=major, 1=minor, 2=chromatic), `Strength` (float, 0.0 to 1.0), `Speed` (float, 0.0 to 1.0)

10. **convolution_reverb** - Impulse response reverb
    - Parameters: `IR Path` (string, optional), `Wet Level` (float, 0.0 to 1.0), `Pre Delay` (float, 0.0 to 200.0 ms), `High Cut` (float, 1000.0 to 20000.0 Hz), `Low Cut` (float, 20.0 to 500.0 Hz)

11. **formant_shifter** - Voice character modification
    - Parameters: `Formant Shift` (float, -1.0 to 1.0), `Formant Scale` (float, 0.5 to 2.0), `Preserve Pitch` (bool), `Mix` (float, 0.0 to 1.0)

12. **distortion** - Distortion/saturation
    - Parameters: `Drive` (float, 0.0 to 1.0), `Tone` (float, 0.0 to 1.0), `Level` (float, 0.0 to 1.0), `Mix` (float, 0.0 to 1.0)

13. **multi_band_processor** - Multi-band processing
    - Parameters: `Low Gain` (float, -24.0 to 24.0 dB), `Mid Gain` (float, -24.0 to 24.0 dB), `High Gain` (float, -24.0 to 24.0 dB), `Low Freq` (float, 50.0 to 1000.0 Hz), `High Freq` (float, 2000.0 to 15000.0 Hz)

14. **dynamic_eq** - Frequency-dependent dynamics
    - Parameters: `Frequency` (float, 20.0 to 20000.0 Hz), `Threshold` (float, -60.0 to 0.0 dB), `Ratio` (float, 1.0 to 20.0), `Attack` (float, 0.1 to 100.0 ms), `Release` (float, 10.0 to 500.0 ms), `Gain` (float, -12.0 to 12.0 dB), `Q` (float, 0.1 to 10.0)

15. **spectral_processor** - Frequency-domain editing
    - Parameters: `Mode` (float, 0=enhance, 1=suppress, 2=shift), `Frequency` (float, 20.0 to 20000.0 Hz), `Bandwidth` (float, 50.0 to 5000.0 Hz), `Strength` (float, 0.0 to 1.0), `Shift Amount` (float, -2000.0 to 2000.0 Hz)

16. **granular_synthesizer** - Granular synthesis
    - Parameters: `Grain Size` (float, 10.0 to 200.0 ms), `Grain Density` (float, 1.0 to 50.0 grains/s), `Pitch` (float, 0.5 to 2.0), `Position` (float, 0.0 to 1.0), `Spread` (float, 0.0 to 1.0), `Mix` (float, 0.0 to 1.0)

17. **vocoder** - Vocoder effect
    - Parameters: `Carrier Type` (float, 0=noise, 1=sawtooth, 2=square), `Bandwidth` (float, 0.0 to 1.0), `Depth` (float, 0.0 to 1.0), `Formant Shift` (float, -1.0 to 1.0), `Mix` (float, 0.0 to 1.0)

**Effect Chain Example:**
```json
{
  "name": "Vocal Chain",
  "effects": [
    {
      "type": "normalize",
      "parameters": {
        "Target LUFS": -23.0
      }
    },
    {
      "type": "eq",
      "parameters": {
        "Low Gain": 2.0,
        "Mid Gain": 0.0,
        "High Gain": 1.0
      }
    },
    {
      "type": "compressor",
      "parameters": {
        "Threshold": -12.0,
        "Ratio": 4.0,
        "Attack": 5.0,
        "Release": 50.0
      }
    },
    {
      "type": "reverb",
      "parameters": {
        "Room Size": 0.5,
        "Damping": 0.5,
        "Wet Level": 0.3
      }
    }
  ]
}
```

---

## Mixer

**Base Path:** `/api/mixer`

### Get Mixer State

**GET** `/api/mixer/state/{project_id}`
- Get complete mixer state for project
- Parameters:
  - `project_id` (path): Project ID
- Returns: `MixerState`
  - `channels`: Track channel states
  - `sends`: Send buses
  - `returns`: Return buses
  - `subgroups`: Sub-groups
  - `master`: Master bus state
- Errors: 404 if project not found

### Update Mixer State

**PUT** `/api/mixer/state/{project_id}`
- Update mixer state
- Parameters:
  - `project_id` (path): Project ID
- Request Body: `MixerState`
- Returns: `MixerState`
- Errors: 404 if project not found

### Reset Mixer State

**POST** `/api/mixer/state/{project_id}/reset`
- Reset mixer to defaults
- Parameters:
  - `project_id` (path): Project ID
- Returns: `MixerState`
- Errors: 404 if project not found

### Create Send

**POST** `/api/mixer/state/{project_id}/sends`
- Create send bus
- Parameters:
  - `project_id` (path): Project ID
- Request Body: `MixerSendCreateRequest`
  - `name` (string, required): Send name
  - `bus_number` (int, required): Bus number
- Returns: `MixerSend`
- Errors: 404 if project not found

### Update Send

**PUT** `/api/mixer/state/{project_id}/sends/{send_id}`
- Update send bus
- Parameters:
  - `project_id` (path): Project ID
  - `send_id` (path): Send ID
- Request Body: `MixerSendUpdateRequest`
- Returns: `MixerSend`
- Errors: 404 if not found

### Delete Send

**DELETE** `/api/mixer/state/{project_id}/sends/{send_id}`
- Delete send bus
- Parameters:
  - `project_id` (path): Project ID
  - `send_id` (path): Send ID
- Returns: `ApiOk`
- Errors: 404 if not found

### Create Return

**POST** `/api/mixer/state/{project_id}/returns`
- Create return bus
- Parameters:
  - `project_id` (path): Project ID
- Request Body: `MixerReturnCreateRequest`
- Returns: `MixerReturn`
- Errors: 404 if project not found

### Update Return

**PUT** `/api/mixer/state/{project_id}/returns/{return_id}`
- Update return bus
- Parameters:
  - `project_id` (path): Project ID
  - `return_id` (path): Return ID
- Request Body: `MixerReturnUpdateRequest`
- Returns: `MixerReturn`
- Errors: 404 if not found

### Delete Return

**DELETE** `/api/mixer/state/{project_id}/returns/{return_id}`
- Delete return bus
- Parameters:
  - `project_id` (path): Project ID
  - `return_id` (path): Return ID
- Returns: `ApiOk`
- Errors: 404 if not found

### Create Sub-Group

**POST** `/api/mixer/state/{project_id}/subgroups`
- Create sub-group
- Parameters:
  - `project_id` (path): Project ID
- Request Body: `MixerSubGroupCreateRequest`
- Returns: `MixerSubGroup`
- Errors: 404 if project not found

### Update Sub-Group

**PUT** `/api/mixer/state/{project_id}/subgroups/{subgroup_id}`
- Update sub-group
- Parameters:
  - `project_id` (path): Project ID
  - `subgroup_id` (path): Sub-group ID
- Request Body: `MixerSubGroupUpdateRequest`
- Returns: `MixerSubGroup`
- Errors: 404 if not found

### Delete Sub-Group

**DELETE** `/api/mixer/state/{project_id}/subgroups/{subgroup_id}`
- Delete sub-group
- Parameters:
  - `project_id` (path): Project ID
  - `subgroup_id` (path): Sub-group ID
- Returns: `ApiOk`
- Errors: 404 if not found

### Update Master Bus

**PUT** `/api/mixer/state/{project_id}/master`
- Update master bus settings
- Parameters:
  - `project_id` (path): Project ID
- Request Body: `MixerMasterUpdateRequest`
- Returns: `MixerMaster`
- Errors: 404 if project not found

### Update Channel Routing

**PUT** `/api/mixer/state/{project_id}/channels/{channel_id}/routing`
- Update channel routing
- Parameters:
  - `project_id` (path): Project ID
  - `channel_id` (path): Channel ID
- Request Body: `ChannelRoutingUpdateRequest`
- Returns: `ChannelRouting`
- Errors: 404 if not found

### List Mixer Presets

**GET** `/api/mixer/presets/{project_id}`
- List all mixer presets for project
- Parameters:
  - `project_id` (path): Project ID
- Returns: `List[MixerPreset]`

### Get Mixer Preset

**GET** `/api/mixer/presets/{project_id}/{preset_id}`
- Get specific mixer preset
- Parameters:
  - `project_id` (path): Project ID
  - `preset_id` (path): Preset ID
- Returns: `MixerPreset`
- Errors: 404 if not found

### Create Mixer Preset

**POST** `/api/mixer/presets/{project_id}`
- Create mixer preset
- Parameters:
  - `project_id` (path): Project ID
- Request Body: `MixerPresetCreateRequest`
  - `name` (string, required): Preset name
  - `state` (object, required): Mixer state to save
- Returns: `MixerPreset`

### Update Mixer Preset

**PUT** `/api/mixer/presets/{project_id}/{preset_id}`
- Update mixer preset
- Parameters:
  - `project_id` (path): Project ID
  - `preset_id` (path): Preset ID
- Request Body: `MixerPresetUpdateRequest`
- Returns: `MixerPreset`
- Errors: 404 if not found

### Delete Mixer Preset

**DELETE** `/api/mixer/presets/{project_id}/{preset_id}`
- Delete mixer preset
- Parameters:
  - `project_id` (path): Project ID
  - `preset_id` (path): Preset ID
- Returns: `ApiOk`
- Errors: 404 if not found

### Apply Mixer Preset

**POST** `/api/mixer/presets/{project_id}/{preset_id}/apply`
- Apply mixer preset to project
- Parameters:
  - `project_id` (path): Project ID
  - `preset_id` (path): Preset ID
- Returns: `MixerState`
- Errors: 404 if not found

### Get VU Meters

**GET** `/api/mixer/meters/{project_id}`
- Get real-time VU meter data
- Parameters:
  - `project_id` (path): Project ID
- Returns: `Dict[str, Any]`
  - `channels`: Per-channel meters
  - `master`: Master bus meters
- Updates via WebSocket: `/ws/realtime?topics=meters`

### Simulate Meters

**POST** `/api/mixer/meters/{project_id}/simulate`
- Simulate meter data (for testing)
- Parameters:
  - `project_id` (path): Project ID
- Returns: `Dict[str, Any]`

---

## Macros

**Base Path:** `/api/macros`

### List Macros

**GET** `/api/macros`
- List all macros
- Returns: `List[Macro]`

### Get Macro

**GET** `/api/macros/{macro_id}`
- Get specific macro
- Parameters:
  - `macro_id` (path): Macro ID
- Returns: `Macro`
- Errors: 404 if not found

### Create Macro

**POST** `/api/macros`
- Create new macro
- Request Body: `MacroCreateRequest`
  - `name` (string, required): Macro name
  - `nodes` (array, required): Node graph
  - `connections` (array, required): Node connections
- Returns: `Macro`

### Update Macro

**PUT** `/api/macros/{macro_id}`
- Update macro
- Parameters:
  - `macro_id` (path): Macro ID
- Request Body: `MacroUpdateRequest`
- Returns: `Macro`
- Errors: 404 if not found

### Delete Macro

**DELETE** `/api/macros/{macro_id}`
- Delete macro
- Parameters:
  - `macro_id` (path): Macro ID
- Returns: `ApiOk`
- Errors: 404 if not found

### Execute Macro

**POST** `/api/macros/{macro_id}/execute`
- Execute macro
- Parameters:
  - `macro_id` (path): Macro ID
- Request Body: `MacroExecuteRequest`
  - `parameters` (object, optional): Execution parameters
- Returns: `ApiOk`
- Errors: 404 if not found, 500 if execution fails

### Get Execution Status

**GET** `/api/macros/{macro_id}/execution-status`
- Get macro execution status
- Parameters:
  - `macro_id` (path): Macro ID
- Returns: `MacroExecutionStatus`
  - `status`: Execution status (running, completed, failed)
  - `progress`: Progress (0.0-1.0)
  - `results`: Execution results
- Errors: 404 if not found

### List Automation Curves

**GET** `/api/macros/automation/{track_id}`
- List automation curves for track
- Parameters:
  - `track_id` (path): Track ID
- Returns: `List[AutomationCurve]`

### Create Automation Curve

**POST** `/api/macros/automation`
- Create automation curve
- Request Body: `AutomationCurveCreateRequest`
  - `track_id` (string, required): Track ID
  - `parameter` (string, required): Parameter name
  - `keyframes` (array, required): Keyframe data
- Returns: `AutomationCurve`

### Update Automation Curve

**PUT** `/api/macros/automation/{curve_id}`
- Update automation curve
- Parameters:
  - `curve_id` (path): Curve ID
- Request Body: `AutomationCurveUpdateRequest`
- Returns: `AutomationCurve`
- Errors: 404 if not found

### Delete Automation Curve

**DELETE** `/api/macros/automation/{curve_id}`
- Delete automation curve
- Parameters:
  - `curve_id` (path): Curve ID
- Returns: `ApiOk`
- Errors: 404 if not found

---

## Training

**Base Path:** `/api/training`

### Create Dataset

**POST** `/api/training/datasets`
- Create training dataset
- Request Body: `TrainingDatasetCreateRequest`
  - `name` (string, required): Dataset name
  - `description` (string, optional): Description
  - `audio_files` (array, required): Audio file IDs
  - `transcripts` (array, optional): Transcripts
- Returns: `TrainingDataset`

### List Datasets

**GET** `/api/training/datasets`
- List all training datasets
- Returns: `List[TrainingDataset]`

### Get Dataset

**GET** `/api/training/datasets/{dataset_id}`
- Get specific dataset
- Parameters:
  - `dataset_id` (path): Dataset ID
- Returns: `TrainingDataset`
- Errors: 404 if not found

### Start Training

**POST** `/api/training/start`
- Start training job
- Request Body: `TrainingStartRequest`
  - `dataset_id` (string, required): Dataset ID
  - `engine` (string, default: "xtts_v2"): Training engine
  - `epochs` (int, default: 50): Number of epochs
  - `batch_size` (int, default: 4): Batch size
  - `learning_rate` (float, default: 0.0001): Learning rate
  - `quality_mode` (string, default: "high"): Quality mode
- Returns: `TrainingStatus`
  - `training_id`: Training job ID
  - `status`: Status (pending, running, completed, failed)
  - `progress`: Progress (0.0-1.0)
- Updates via WebSocket: `/ws/realtime?topics=training`

### Get Training Status

**GET** `/api/training/status/{training_id}`
- Get training job status
- Parameters:
  - `training_id` (path): Training ID
- Returns: `TrainingStatus`
- Errors: 404 if not found

### List Training Jobs

**GET** `/api/training/status`
- List all training jobs
- Returns: `List[TrainingStatus]`

### Cancel Training

**POST** `/api/training/cancel/{training_id}`
- Cancel training job
- Parameters:
  - `training_id` (path): Training ID
- Returns: `ApiOk`
- Errors: 404 if not found

### Get Training Logs

**GET** `/api/training/logs/{training_id}`
- Get training logs
- Parameters:
  - `training_id` (path): Training ID
- Returns: `List[TrainingLogEntry]`
- Errors: 404 if not found

### Delete Training Job

**DELETE** `/api/training/{training_id}`
- Delete training job
- Parameters:
  - `training_id` (path): Training ID
- Returns: `ApiOk`
- Errors: 404 if not found

### Export Model

**POST** `/api/training/export`
- Export trained model
- Request Body: `ModelExportRequest`
  - `training_id` (string, required): Training ID
  - `format` (string, default: "pytorch"): Export format
  - `include_metadata` (boolean, default: true): Include metadata
- Returns: `ModelExportResponse`
  - `export_id`: Export ID
  - `download_url`: Download URL
- Errors: 404 if training not found, 500 if export fails

### Import Model

**POST** `/api/training/import`
- Import trained model
- Request Body: `ModelImportRequest`
  - `model_file` (file, required): Model file
  - `name` (string, required): Model name
  - `engine` (string, required): Engine type
- Returns: `TrainingStatus`
- Errors: 400 if invalid file, 500 if import fails

### Download Exported Model

**GET** `/api/training/exports/{export_id}/download`
- Download exported model
- Parameters:
  - `export_id` (path): Export ID
- Returns: Model file
- Errors: 404 if not found

---

## Batch Processing

**Base Path:** `/api/batch`

### Create Batch Job

**POST** `/api/batch/jobs`
- Create batch processing job
- Request Body: `BatchJobCreateRequest`
  - `name` (string, required): Job name
  - `project_id` (string, required): Project ID
  - `voice_profile_id` (string, required): Voice profile ID
  - `engine_id` (string, required): Engine ID
  - `texts` (array, required): List of texts to synthesize
  - `language` (string, default: "en"): Language
- Returns: `BatchJob`
  - `id`: Job ID
  - `status`: Status (pending, running, completed, failed)
  - `progress`: Progress (0.0-1.0)
- Updates via WebSocket: `/ws/realtime?topics=batch`

### List Batch Jobs

**GET** `/api/batch/jobs`
- List all batch jobs
- Query Parameters:
  - `project_id` (string, optional): Filter by project
  - `status` (string, optional): Filter by status
- Returns: `List[BatchJob]`

### Get Batch Job

**GET** `/api/batch/jobs/{job_id}`
- Get specific batch job
- Parameters:
  - `job_id` (path): Job ID
- Returns: `BatchJob`
- Errors: 404 if not found

### Delete Batch Job

**DELETE** `/api/batch/jobs/{job_id}`
- Delete batch job
- Parameters:
  - `job_id` (path): Job ID
- Returns: `ApiOk`
- Errors: 404 if not found

### Start Batch Job

**POST** `/api/batch/jobs/{job_id}/start`
- Start batch job processing
- Parameters:
  - `job_id` (path): Job ID
- Returns: `BatchJob`
- Errors: 404 if not found, 400 if already running

### Cancel Batch Job

**POST** `/api/batch/jobs/{job_id}/cancel`
- Cancel batch job
- Parameters:
  - `job_id` (path): Job ID
- Returns: `BatchJob`
- Errors: 404 if not found

### Get Queue Status

**GET** `/api/batch/queue/status`
- Get batch queue status
- Returns: `QueueStatus`
  - `pending`: Number of pending jobs
  - `running`: Number of running jobs
  - `completed`: Number of completed jobs
  - `failed`: Number of failed jobs

---

## Transcription

**Base Path:** `/api/transcribe`

### Get Supported Languages

**GET** `/api/transcribe/languages`
- Get list of supported languages
- Returns: `List[SupportedLanguage]`
  - `code`: Language code (ISO 639-1)
  - `name`: Language name

### Transcribe Audio

**POST** `/api/transcribe/`
- Transcribe audio file
- Request Body: `TranscriptionRequest`
  - `audio_id` (string, required): Audio ID
  - `engine` (string, default: "whisper"): STT engine
  - `language` (string, optional): Language code (auto-detect if None)
  - `word_timestamps` (boolean, default: false): Include word timestamps
  - `diarization` (boolean, default: false): Speaker diarization
- Query Parameters:
  - `project_id` (string, optional): Associate with project
- Returns: `TranscriptionResponse`
  - `id`: Transcription ID
  - `text`: Full transcript
  - `language`: Detected language
  - `segments`: Segments with timestamps
  - `word_timestamps`: Word-level timestamps (if requested)
- Errors: 404 if audio not found, 500 if transcription fails

### Get Transcription

**GET** `/api/transcribe/{transcription_id}`
- Get transcription by ID
- Parameters:
  - `transcription_id` (path): Transcription ID
- Returns: `TranscriptionResponse`
- Errors: 404 if not found

### List Transcriptions

**GET** `/api/transcribe/`
- List transcriptions
- Query Parameters:
  - `audio_id` (string, optional): Filter by audio ID
  - `project_id` (string, optional): Filter by project ID
- Returns: `List[TranscriptionResponse]`

### Delete Transcription

**DELETE** `/api/transcribe/{transcription_id}`
- Delete transcription
- Parameters:
  - `transcription_id` (path): Transcription ID
- Returns: `ApiOk`
- Errors: 404 if not found

---

## Models

**Base Path:** `/api/models`

### List Models

**GET** `/api/models`
- List all registered models
- Returns: `List[ModelInfoResponse]`

### Get Model Info

**GET** `/api/models/{engine}/{model_name}`
- Get model information
- Parameters:
  - `engine` (path): Engine name
  - `model_name` (path): Model name
- Returns: `ModelInfoResponse`
  - `engine`: Engine name
  - `model_name`: Model name
  - `model_path`: Path to model file
  - `checksum`: File checksum
  - `size`: File size (bytes)
  - `version`: Model version
  - `metadata`: Additional metadata
- Errors: 404 if not found

### Register Model

**POST** `/api/models`
- Register new model
- Request Body: `ModelRegisterRequest`
  - `engine` (string, required): Engine name
  - `model_name` (string, required): Model name
  - `model_path` (string, required): Path to model file
  - `version` (string, optional): Model version
  - `metadata` (object, optional): Additional metadata
- Returns: `ModelInfoResponse`

### Verify Model

**POST** `/api/models/{engine}/{model_name}/verify`
- Verify model integrity
- Parameters:
  - `engine` (path): Engine name
  - `model_name` (path): Model name
- Returns: `ModelVerifyResponse`
  - `valid`: Whether model is valid
  - `checksum_match`: Whether checksum matches
  - `errors`: List of errors if invalid
- Errors: 404 if not found

### Update Checksum

**PUT** `/api/models/{engine}/{model_name}/update-checksum`
- Update model checksum
- Parameters:
  - `engine` (path): Engine name
  - `model_name` (path): Model name
- Returns: `ModelInfoResponse`
- Errors: 404 if not found

### Delete Model

**DELETE** `/api/models/{engine}/{model_name}`
- Delete model
- Parameters:
  - `engine` (path): Engine name
  - `model_name` (path): Model name
- Returns: `ApiOk`
- Errors: 404 if not found

### Get Storage Stats

**GET** `/api/models/stats/storage`
- Get model storage statistics
- Returns: `StorageStatsResponse`
  - `total_size`: Total storage used (bytes)
  - `model_count`: Number of models
  - `engines`: Per-engine statistics

### Export Model

**GET** `/api/models/{engine}/{model_name}/export`
- Export model file
- Parameters:
  - `engine` (path): Engine name
  - `model_name` (path): Model name
- Returns: Model file
- Errors: 404 if not found

### Import Model

**POST** `/api/models/import`
- Import model file
- Request Body: `ModelImportRequest` (multipart/form-data)
  - `file` (file, required): Model file
  - `engine` (string, required): Engine name
  - `model_name` (string, required): Model name
- Returns: `ModelInfoResponse`
- Errors: 400 if invalid file, 500 if import fails

---

## Settings

**Base Path:** `/api/settings`

### Get All Settings

**GET** `/api/settings`
- Get all application settings
- Returns: `SettingsData`
  - `general`: GeneralSettings (theme, language, auto-save)
  - `engine`: EngineSettings (default engines, quality level)
  - `audio`: AudioSettings (devices, sample rate, buffer size)
  - `timeline`: TimelineSettings (time format, snap, grid)
  - `backend`: BackendSettings (API URL, timeout, retry count)
  - `performance`: PerformanceSettings (caching, threads, memory)
  - `plugins`: PluginSettings (enabled plugins)
  - `mcp`: McpSettings (MCP server settings)
  - `quality`: QualitySettings (quality presets, thresholds)

### Get Settings Category

**GET** `/api/settings/{category}`
- Get settings for a specific category
- Parameters:
  - `category` (path): Category name (general, engine, audio, timeline, backend, performance, plugins, mcp, quality)
- Returns: Category-specific settings model
- Errors: 404 if category not found

### Save All Settings

**POST** `/api/settings`
- Save all application settings
- Request Body: `SettingsData`
- Returns: `SettingsData`
- Errors: 400 if validation fails, 500 if save fails

### Update Settings Category

**PUT** `/api/settings/{category}`
- Update settings for a specific category
- Parameters:
  - `category` (path): Category name
- Request Body: Category-specific settings model (partial update supported)
- Returns: Updated category settings
- Errors: 400 if validation fails, 404 if category not found, 500 if update fails

### Reset Settings

**POST** `/api/settings/reset`
- Reset all settings to defaults
- Returns: `SettingsData` (default values)
- Errors: 500 if reset fails

---

## Backup & Restore

**Base Path:** `/api/backup`

### List Backups

**GET** `/api/backup`
- List all available backups
- Returns: `List[BackupInfo]`
  - `id`: Backup ID
  - `name`: Backup name
  - `created`: Creation timestamp (ISO)
  - `size_bytes`: Backup file size
  - `includes_profiles`: Whether profiles are included
  - `includes_projects`: Whether projects are included
  - `includes_settings`: Whether settings are included
  - `includes_models`: Whether models are included
  - `description`: Optional description

### Get Backup Info

**GET** `/api/backup/{backup_id}`
- Get information about a specific backup
- Parameters:
  - `backup_id` (path): Backup ID
- Returns: `BackupInfo`
- Errors: 404 if backup not found

### Create Backup

**POST** `/api/backup`
- Create a new backup
- Request Body: `BackupCreateRequest`
  - `name` (string, required): Backup name
  - `includes_profiles` (boolean, default: true): Include voice profiles
  - `includes_projects` (boolean, default: true): Include projects
  - `includes_settings` (boolean, default: true): Include settings
  - `includes_models` (boolean, default: false): Include models (large)
  - `description` (string, optional): Backup description
- Returns: `BackupInfo`
- Errors: 400 if validation fails, 500 if creation fails

### Download Backup

**GET** `/api/backup/{backup_id}/download`
- Download backup file
- Parameters:
  - `backup_id` (path): Backup ID
- Returns: File download (application/zip)
- Errors: 404 if backup not found, 500 if download fails

### Restore Backup

**POST** `/api/backup/{backup_id}/restore`
- Restore from a backup
- Parameters:
  - `backup_id` (path): Backup ID
- Request Body: `RestoreRequest`
  - `restore_profiles` (boolean, default: true): Restore voice profiles
  - `restore_projects` (boolean, default: true): Restore projects
  - `restore_settings` (boolean, default: true): Restore settings
  - `restore_models` (boolean, default: false): Restore models
- Returns: `ApiOk`
- Errors: 404 if backup not found, 500 if restore fails

### Upload Backup

**POST** `/api/backup/upload`
- Upload a backup file
- Request Body: `multipart/form-data`
  - `file` (file, required): Backup ZIP file
  - `name` (string, optional): Backup name (defaults to filename)
  - `description` (string, optional): Backup description
- Returns: `BackupInfo`
- Errors: 400 if file invalid, 500 if upload fails

### Delete Backup

**DELETE** `/api/backup/{backup_id}`
- Delete a backup
- Parameters:
  - `backup_id` (path): Backup ID
- Returns: `ApiOk`
- Errors: 404 if backup not found, 500 if deletion fails

---

## Tag Management

**Base Path:** `/api/tags`

### List Tags

**GET** `/api/tags`
- Get all tags, optionally filtered
- Query Parameters:
  - `category` (string, optional): Filter by category
  - `search` (string, optional): Search in name and description
  - `limit` (integer, default: 100, min: 1, max: 1000): Maximum results
- Returns: `List[Tag]`
  - `id`: Tag ID
  - `name`: Tag name
  - `category`: Optional category
  - `color`: Optional hex color code
  - `description`: Optional description
  - `usage_count`: Number of resources using this tag
  - `created`: Creation timestamp (ISO)
  - `modified`: Last modification timestamp (ISO)

### Get Tag

**GET** `/api/tags/{tag_id}`
- Get a specific tag
- Parameters:
  - `tag_id` (path): Tag ID
- Returns: `Tag`
- Errors: 404 if tag not found

### Create Tag

**POST** `/api/tags`
- Create a new tag
- Request Body: `TagCreateRequest`
  - `name` (string, required): Tag name (max 100 chars)
  - `category` (string, optional): Category name
  - `color` (string, optional): Hex color code (e.g., #FF0000)
  - `description` (string, optional): Description (max 500 chars)
- Returns: `Tag`
- Errors: 400 if validation fails, 500 if creation fails

### Update Tag

**PUT** `/api/tags/{tag_id}`
- Update an existing tag
- Parameters:
  - `tag_id` (path): Tag ID
- Request Body: `TagUpdateRequest` (all fields optional)
  - `name` (string, optional): Tag name
  - `category` (string, optional): Category name
  - `color` (string, optional): Hex color code
  - `description` (string, optional): Description
- Returns: `Tag`
- Errors: 400 if validation fails, 404 if tag not found, 500 if update fails

### Delete Tag

**DELETE** `/api/tags/{tag_id}`
- Delete a tag (only if not in use)
- Parameters:
  - `tag_id` (path): Tag ID
- Returns: `ApiOk`
- Errors: 400 if tag is in use, 404 if tag not found, 500 if deletion fails

### Get Tag Usage

**GET** `/api/tags/{tag_id}/usage`
- Get resources using a tag
- Parameters:
  - `tag_id` (path): Tag ID
- Returns: `TagUsageResponse`
  - `tag_id`: Tag ID
  - `tag_name`: Tag name
  - `resources`: List of resources using this tag
- Errors: 404 if tag not found

### Increment Tag Usage

**POST** `/api/tags/{tag_id}/increment-usage`
- Increment usage count for a tag
- Parameters:
  - `tag_id` (path): Tag ID
- Returns: `ApiOk`
- Errors: 404 if tag not found

### Decrement Tag Usage

**POST** `/api/tags/{tag_id}/decrement-usage`
- Decrement usage count for a tag
- Parameters:
  - `tag_id` (path): Tag ID
- Returns: `ApiOk`
- Errors: 404 if tag not found

### List Categories

**GET** `/api/tags/categories/list`
- Get all tag categories
- Returns: `List[str]` (category names)

### Merge Tags

**POST** `/api/tags/merge`
- Merge two tags (combine usage, delete source)
- Request Body:
  - `source_tag_id` (string, required): Tag to merge from
  - `target_tag_id` (string, required): Tag to merge into
- Returns: `ApiOk`
- Errors: 400 if validation fails, 404 if tags not found, 500 if merge fails

---

## Search

**Base Path:** `/api/search`

### Global Search

**GET** `/api/search`
- Global search across all panels and content types (IDEA 5)
- Searches across profiles, projects, audio files, markers, and scripts
- Query Parameters:
  - `q` (string, required, min_length: 2): Search query
  - `types` (string, optional): Comma-separated list of types to search (profile, project, audio, marker, script)
  - `limit` (integer, optional, default: 50, min: 1, max: 100): Maximum number of results per type
- Returns: `SearchResponse`
  - `query` (string): Search query
  - `results` (array of SearchResultItem): Search results
    - `id` (string): Item identifier
    - `type` (string): Item type (profile, project, audio, marker, script)
    - `title` (string): Item title/name
    - `description` (string, optional): Item description
    - `panel_id` (string): Panel ID to navigate to
    - `preview` (string, optional): Preview text snippet
    - `metadata` (object): Additional metadata
  - `total_results` (integer): Total number of results
  - `results_by_type` (object): Result count by type
- Errors: 400 if query is less than 2 characters

**Example Request:**
```
GET /api/search?q=my+voice&types=profile,audio&limit=10
```

**Example Response:**
```json
{
  "query": "my voice",
  "results": [
    {
      "id": "profile-123",
      "type": "profile",
      "title": "My Voice Profile",
      "description": "Personal voice profile",
      "panel_id": "profiles",
      "preview": "Name: My Voice Profile",
      "metadata": {
        "language": "en",
        "tags": ["male", "english"]
      }
    }
  ],
  "total_results": 1,
  "results_by_type": {
    "profile": 1,
    "audio": 0
  }
}
```

---

## Quality Testing & Comparison Features

**Base Path:** `/api/quality` and `/api/voice`

### Quality Presets

**GET** `/api/quality/presets`
- List all available quality presets
- Returns: `Dict[str, QualityPresetResponse]`
  - Each preset includes:
    - `name` (string): Preset name (fast, standard, high, ultra, professional)
    - `description` (string): Preset description
    - `target_metrics` (object): Target quality metrics
    - `parameters` (object): Synthesis parameters for the preset
- Errors: 503 if quality presets not available

**GET** `/api/quality/presets/{preset_name}`
- Get information about a specific quality preset
- Path Parameters:
  - `preset_name` (string): Preset name (fast, standard, high, ultra, professional)
- Returns: `QualityPresetResponse`
  - `name` (string): Preset name
  - `description` (string): Preset description
  - `target_metrics` (object): Target quality metrics
  - `parameters` (object): Synthesis parameters
- Errors: 404 if preset not found, 503 if quality presets not available

### Quality Analysis

**POST** `/api/quality/analyze`
- Analyze quality metrics and determine if optimization is needed
- Request Body: `QualityAnalysisRequest`
  - `mos_score` (float, optional): MOS score (1.0-5.0)
  - `similarity` (float, optional): Similarity to reference (0.0-1.0)
  - `naturalness` (float, optional): Naturalness score (0.0-1.0)
  - `snr_db` (float, optional): Signal-to-noise ratio (dB)
  - `target_tier` (string, optional, default: "standard"): Quality tier - `fast`, `standard`, `high`, `ultra`
- Returns: `QualityAnalysisResponse`
  - `meets_target` (boolean): Whether metrics meet target tier
  - `quality_score` (float): Overall quality score
  - `deficiencies` (array of object): List of quality deficiencies found
  - `recommendations` (array of object): Optimization recommendations
- Errors: 503 if quality optimization not available

**POST** `/api/quality/optimize`
- Optimize synthesis parameters based on quality metrics
- Request Body: `QualityOptimizationRequest`
  - `metrics` (object, required): Current quality metrics
  - `current_params` (object, required): Current synthesis parameters
  - `target_tier` (string, optional, default: "standard"): Quality tier - `fast`, `standard`, `high`, `ultra`
- Returns: `QualityOptimizationResponse`
  - `optimized_params` (object): Optimized synthesis parameters
  - `analysis` (object): Optimization analysis results
- Errors: 503 if quality optimization not available

**POST** `/api/quality/compare`
- Compare quality metrics across multiple audio samples
- Request Body: `multipart/form-data`
  - `audio_files` (array of file, required): List of audio files to compare
  - `reference_audio` (file, optional): Reference audio for similarity comparison
- Returns: `QualityComparisonResponse`
  - `total_samples` (integer): Total number of samples compared
  - `rankings` (object): Rankings by quality metrics
  - `statistics` (object): Statistical analysis per metric
  - `best_samples` (object): Best samples per metric
  - `comparison_table` (array of object): Detailed comparison table
- Errors: 503 if quality comparison not available

### Quality History (IDEA 30)

**POST** `/api/quality/history`
- Store a quality history entry for a voice profile
- Implements IDEA 30: Voice Profile Quality History
- Request Body: `QualityHistoryRequest`
  - `profile_id` (string, required): Voice profile ID
  - `engine` (string, required): Engine used for synthesis
  - `metrics` (object, required): Quality metrics dictionary
  - `quality_score` (float, required): Overall quality score
  - `synthesis_text` (string, optional): Text that was synthesized
  - `audio_url` (string, optional): URL to synthesized audio
  - `enhanced_quality` (boolean, optional, default: false): Whether quality enhancement was used
  - `metadata` (object, optional): Additional metadata
- Returns: `QualityHistoryEntry`
  - `id` (string): Entry ID
  - `profile_id` (string): Voice profile ID
  - `timestamp` (string): ISO format timestamp
  - `engine` (string): Engine used
  - `metrics` (object): Quality metrics
  - `quality_score` (float): Quality score
  - `synthesis_text` (string, optional): Synthesis text
  - `audio_url` (string, optional): Audio URL
  - `enhanced_quality` (boolean): Whether enhancement was used
  - `metadata` (object, optional): Additional metadata

**GET** `/api/quality/history/{profile_id}`
- Get quality history for a voice profile
- Implements IDEA 30: Voice Profile Quality History
- Path Parameters:
  - `profile_id` (string, required): Voice profile ID
- Query Parameters:
  - `limit` (integer, optional): Maximum number of entries to return
  - `start_date` (string, optional): Start date filter (ISO format)
  - `end_date` (string, optional): End date filter (ISO format)
- Returns: `QualityHistoryResponse`
  - `entries` (array of QualityHistoryEntry): Quality history entries (newest first)
  - `total` (integer): Total number of entries

**GET** `/api/quality/history/{profile_id}/trends`
- Get quality trends for a voice profile
- Implements IDEA 30: Voice Profile Quality History
- Calculates trends, statistics, and identifies best/worst samples
- Path Parameters:
  - `profile_id` (string, required): Voice profile ID
- Query Parameters:
  - `time_range` (string, optional, default: "30d"): Time range - `7d`, `30d`, `90d`, `1y`, `all`
- Returns: `QualityTrendsResponse`
  - `profile_id` (string): Voice profile ID
  - `time_range` (string): Time range used
  - `trends` (object): Trends per metric (metric_name -> [{timestamp, value}])
  - `statistics` (object): Statistics per metric (metric_name -> {avg, min, max, trend})
  - `best_entry` (QualityHistoryEntry, optional): Best quality entry
  - `worst_entry` (QualityHistoryEntry, optional): Worst quality entry

### Adaptive Quality Optimization (IDEA 53)

**POST** `/api/quality/analyze-text`
- Analyze text content for adaptive quality optimization
- Implements IDEA 53: Adaptive Quality Optimization
- Analyzes text for complexity, content type, and characteristics to help determine optimal quality settings
- Request Body: `TextAnalysisRequest`
  - `text` (string, required): Text to analyze
  - `language` (string, optional, default: "en"): Language code
- Returns: `TextAnalysisResponse`
  - `complexity` (string): Text complexity level
  - `content_type` (string): Content type classification
  - `word_count` (integer): Word count
  - `sentence_count` (integer): Sentence count
  - `character_count` (integer): Character count
  - `avg_words_per_sentence` (float): Average words per sentence
  - `has_dialogue` (boolean): Whether text contains dialogue
  - `has_technical_terms` (boolean): Whether text contains technical terms
  - `detected_emotions` (array of string): Detected emotions
  - `language` (string): Detected language

**POST** `/api/quality/recommend-quality`
- Get quality recommendations based on text analysis
- Implements IDEA 53: Adaptive Quality Optimization
- Analyzes text and recommends optimal engine, quality mode, and settings for best quality output
- Request Body: `QualityRecommendationRequest`
  - `text` (string, required): Text to analyze
  - `language` (string, optional, default: "en"): Language code
  - `available_engines` (array of string, optional): List of available engines
  - `target_quality` (float, optional): Target quality score
- Returns: `QualityRecommendationResponse`
  - `recommended_engine` (string): Recommended engine name
  - `recommended_quality_mode` (string): Recommended quality mode
  - `recommended_enhance_quality` (boolean): Whether to enhance quality
  - `predicted_quality_score` (float): Predicted quality score
  - `reasoning` (string): Explanation for recommendations
  - `confidence` (float): Confidence score (0.0-1.0)
  - `text_analysis` (TextAnalysisResponse): Text analysis results

### Quality Degradation Detection (IDEA 56)

**GET** `/api/quality/degradation/{profile_id}`
- Check for quality degradation in a voice profile
- Implements IDEA 56: Quality Degradation Detection
- Compares recent quality metrics against baseline to detect degradation
- Path Parameters:
  - `profile_id` (string, required): Voice profile ID to check
- Query Parameters:
  - `time_window_days` (integer, optional, default: 7): Number of recent days to analyze
  - `degradation_threshold_percent` (float, optional, default: 10.0): Percentage drop to trigger warning
  - `critical_threshold_percent` (float, optional, default: 25.0): Percentage drop to trigger critical alert
- Returns: `List[QualityDegradationAlertResponse]`
  - `profile_id` (string): Voice profile ID
  - `severity` (string): Alert severity (warning, critical)
  - `message` (string): Alert message
  - `degradation_percentage` (float): Percentage of degradation
  - `baseline_quality` (float): Baseline quality score
  - `current_quality` (float): Current quality score
  - `time_window_days` (integer): Time window analyzed
  - `detected_at` (string): Detection timestamp
  - `confidence` (float): Detection confidence (0.0-1.0)
- Returns empty list if no degradation detected

**GET** `/api/quality/baseline/{profile_id}`
- Get quality baseline for a voice profile
- Implements IDEA 56: Quality Degradation Detection
- Calculates the baseline quality metrics from historical data
- Path Parameters:
  - `profile_id` (string, required): Voice profile ID
- Query Parameters:
  - `time_period_days` (integer, optional, default: 30): Number of days to use for baseline calculation
- Returns: `QualityBaselineResponse` or `null` if insufficient data
  - `profile_id` (string): Voice profile ID
  - `baseline_quality` (float): Baseline quality score
  - `baseline_date` (string): Baseline calculation date
  - `sample_count` (integer): Number of samples used
  - `metrics` (object): Baseline metrics per metric type

### A/B Testing

**POST** `/api/voice/ab-test`
- Run A/B test comparing two synthesis configurations (IDEA 46)
- Synthesizes the same text with two different configurations and compares quality metrics
- Request Body: `ABTestRequest`
  - `profile_id` (string, optional): Voice profile ID to use (alternative to reference_audio_id)
  - `reference_audio_id` (string, optional): Reference audio ID to use (alternative to profile_id)
  - `test_text` (string, required): Text to synthesize for A/B testing
  - `language` (string, optional, default: "en"): Language code
  - `config_a` (object, required): Configuration A
    - `engine_id` (string, required): Engine ID for configuration A
    - `settings` (object, optional): Engine-specific settings for configuration A
  - `config_b` (object, required): Configuration B
    - `engine_id` (string, required): Engine ID for configuration B
    - `settings` (object, optional): Engine-specific settings for configuration B
  - `enhance_quality` (boolean, optional, default: true): Apply quality enhancement during synthesis
- Returns: `ABTestResponse`
  - `test_id` (string): A/B test ID
  - `result_a` (object): Result for configuration A
    - `audio_id` (string): Generated audio ID
    - `audio_url` (string): URL to access generated audio
    - `quality_metrics` (object): Quality metrics (MOS, similarity, naturalness, SNR, artifacts)
    - `performance` (object): Performance metrics (synthesis_time)
  - `result_b` (object): Result for configuration B (same structure as result_a)
  - `winner` (string, optional): Winner determination ("a", "b", or "tie")
  - `comparison` (object): Detailed comparison
    - `mos_score_diff` (float): Difference in MOS scores
    - `similarity_diff` (float): Difference in similarity scores
    - `naturalness_diff` (float): Difference in naturalness scores
    - `overall_winner` (string): Overall winner based on weighted scoring

**Example Request:**
```json
{
  "profile_id": "profile-123",
  "test_text": "Hello, this is a test.",
  "config_a": {
    "engine_id": "xtts",
    "settings": {}
  },
  "config_b": {
    "engine_id": "chatterbox",
    "settings": {}
  }
}
```

---

## Additional Endpoints

### Engine Telemetry

**GET** `/api/engine/telemetry`
- Get engine performance telemetry
- Returns: `Telemetry`
  - `engine_ms`: Engine processing time (ms)
  - `underruns`: Audio underruns count
  - `vram_pct`: GPU VRAM usage (%)

### A/B Testing (ABX Evaluation)

**POST** `/api/eval/abx/start`
- Start A/B testing evaluation (IDEA 46)
- Compares multiple audio samples for quality assessment
- Request Body: `AbxStartRequest`
  - `items` (array of string, required): Audio item IDs to evaluate
- Returns: `ApiOk`
  - `success` (boolean): Whether the test was started successfully

**GET** `/api/eval/abx/results`
- Get A/B testing evaluation results
- Returns: `List[AbxResult]`
  - `item` (string): Audio item identifier
  - `mos` (float): Mean Opinion Score (0.0-5.0)
  - `pref` (string): Preference indicator ("A", "B", "X", or "None")

### Dataset Scoring

**POST** `/api/dataset/score`
- Score dataset clips
- Request Body: `DatasetScoreRequest`
  - `clips` (array, required): Audio clip IDs
- Returns: `List[ScoreResult]`

**POST** `/api/dataset/cull`
- Cull low-quality clips from dataset
- Request Body: `DatasetCullRequest`
- Returns: `DatasetCullResponse`

### ADR (Automatic Dialogue Replacement)

**POST** `/api/adr/align`
- Align audio with video for ADR
- Request Body: `AdrAlignRequest`
  - `video_id` (string, required): Video ID
  - `audio_id` (string, required): Audio ID
- Returns: `AdrAlignResponse`

### Prosody

**Base Path:** `/api/prosody`

**Enhanced with pyrubberband and Phonemizer integration** for high-quality prosody control:
- **pyrubberband:** High-quality pitch/rate modification
- **Phonemizer:** Advanced phoneme analysis (phonemizer/gruut)
- Falls back to librosa/espeak-ng if advanced methods unavailable

#### Prosody Configuration

**POST** `/api/prosody/configs`
- Create prosody configuration
- Request Body: `ProsodyCreateRequest`
  - `name` (string, required): Config name
  - `pitch` (float, 0.5-2.0, default: 1.0): Pitch multiplier
  - `rate` (float, 0.5-2.0, default: 1.0): Rate multiplier
  - `volume` (float, 0.0-1.0, default: 1.0): Volume level
  - `emphasis` (object, optional): Word-level emphasis
  - `pauses` (array, optional): Pause positions and durations
  - `intonation` (string, optional): Intonation pattern (rising, falling, flat, etc.)
- Returns: `ProsodyConfig` with `config_id`

**GET** `/api/prosody/configs`
- List all prosody configurations
- Returns: `List[ProsodyConfig]`

**GET** `/api/prosody/configs/{config_id}`
- Get prosody configuration
- Returns: `ProsodyConfig`
- Errors: 404 if not found

**PUT** `/api/prosody/configs/{config_id}`
- Update prosody configuration
- Request Body: `ProsodyCreateRequest`
- Returns: `ProsodyConfig`
- Errors: 404 if not found

**DELETE** `/api/prosody/configs/{config_id}`
- Delete prosody configuration
- Returns: `ApiOk`
- Errors: 404 if not found

#### Phoneme Analysis

**POST** `/api/prosody/phonemes/analyze`
- Analyze text to extract phonemes
- **Uses Phonemizer (phonemizer/gruut) if available** for highest quality
- Falls back to espeak-ng, then lexicon estimation
- Query Parameters:
  - `text` (string, required): Text to analyze
  - `language` (string, default: "en"): Language code
- Returns: `PhonemeAnalysis`
  - `phonemes`: Phoneme string
  - `method`: Method used (phonemizer, espeak-ng, lexicon-estimation)
- **Performance:** Typically completes in < 1.0s

#### Apply Prosody

**POST** `/api/prosody/apply`
- Apply prosody configuration to text synthesis
- **Uses pyrubberband via audio_utils** for high-quality pitch/rate modification
- Falls back to librosa if pyrubberband unavailable
- Request Body: `ProsodyApplyRequest`
  - `config_id` (string, required): Prosody config ID
  - `text` (string, required): Text to synthesize
  - `voice_profile_id` (string, required): Voice profile ID
  - `engine` (string, optional): Synthesis engine
  - `language` (string, optional): Language code
- Returns: `SynthesizedAudioResponse`
  - `audio_id`: Synthesized audio ID
  - `audio_url`: URL to synthesized audio
  - `duration`: Audio duration in seconds
- Errors: 404 if config not found, 500 if synthesis fails

#### Quantize Prosody

**POST** `/api/prosody/quantize`
- Quantize prosody to grid
- Request Body: `ProsodyQuantizeRequest`
  - `audio_id` (string, required): Audio ID
  - `grid` (string, default: "1/8"): Grid size
- Returns: `ApiOk`

### Emotion

**POST** `/api/emotion/analyze`
- Analyze emotion in audio
- Request Body: `EmotionAnalyzeRequest`
  - `audio_id` (string, required): Audio ID
- Returns: `EmotionAnalysis`
  - `valence`: Valence array
  - `arousal`: Arousal array

**POST** `/api/emotion/apply`
- Apply emotion curve to audio
- Request Body: `EmotionApplyRequest`
  - `audio_id` (string, required): Audio ID
  - `curve` (array, required): Emotion curve
- Returns: `ApiOk`

### Formant

**POST** `/api/formant/analyze`
- Analyze formants
- Request Body: `FormantAnalyzeRequest`
  - `audio_id` (string, required): Audio ID
- Returns: `FormantAnalysis`

**POST** `/api/formant/apply`
- Apply formant shifts
- Request Body: `FormantEditRequest`
  - `audio_id` (string, required): Audio ID
  - `shifts` (object, required): Formant shifts
- Returns: `ApiOk`

### Spectral

**POST** `/api/spectral/inpaint`
- Spectral inpainting
- Request Body: `SpectralInpaintRequest`
  - `audio_id` (string, required): Audio ID
  - `mask` (string, required): Mask data
- Returns: `ApiOk`

### Model Inspection

**POST** `/api/model_inspect/inspect`
- Inspect model layer
- Request Body: `ModelInspectRequest`
  - `layer` (int, required): Layer number
- Returns: `ModelInspection`

### Granular Synthesis

**POST** `/api/granular/render`
- Render granular synthesis
- Request Body: `GranularRenderRequest`
  - `audio_id` (string, required): Audio ID
  - `params` (object, required): Granular parameters
- Returns: `ApiOk`

### RVC (Real-Time Voice Conversion)

**POST** `/api/rvc/start`
- Start RVC session
- Request Body: `RvcStartRequest`
  - `target_voice` (string, required): Target voice ID
- Returns: `RvcSession`

**POST** `/api/rvc/stop`
- Stop RVC session
- Request Body: `RvcStopRequest`
- Returns: `ApiOk`

### Dubbing

**POST** `/api/dubbing/translate`
- Translate audio for dubbing
- Request Body: `DubTranslateRequest`
  - `audio_id` (string, required): Audio ID
  - `lang` (string, required): Target language
- Returns: `DubTranslation`

**POST** `/api/dubbing/sync`
- Sync dubbed audio
- Request Body: `DubSyncRequest`
- Returns: `ApiOk`

### Articulation

**POST** `/api/articulation/analyze`
- Analyze articulation issues in audio
- **Enhanced with PitchTracker integration** for improved pitch analysis accuracy
  - Uses crepe or pyin for pitch tracking when available
  - Falls back to librosa yin if advanced methods unavailable
  - Detects pitch instability as potential articulation issue
- Request Body: `ArticulationAnalyzeRequest`
  - `audio_id` (string, required): Audio ID
- Returns: `ArticulationAnalysis`
  - `issues`: List of articulation issues with types:
    - `clipping`: Audio clipping detected
    - `silence`: Long silence regions
    - `pitch_instability`: Unstable pitch (potential articulation issue)
    - `distortion`: Potential audio distortion
- **Performance:** Typically completes in < 2.0s

### Noise Reduction

**POST** `/api/nr/apply`
- Apply noise reduction
- Request Body: `NrApplyRequest`
  - `audio_id` (string, required): Audio ID
  - `noise_print_id` (string, required): Noise print ID
- Returns: `NrResponse`

### Audio Repair

**POST** `/api/repair/clipping`
- Repair clipping
- Request Body: `RepairClippingRequest`
  - `audio_id` (string, required): Audio ID
- Returns: `ApiOk`

### Mix Scene Analysis

**POST** `/api/mix_scene/analyze`
- Analyze mix scene
- Request Body: `SceneMixAnalyzeRequest`
  - `tracks` (array, required): Track IDs
- Returns: `SceneMixAnalysis`

### Reward Model

**POST** `/api/reward/train`
- Train reward model
- Request Body: `RmTrainRequest`
  - `ratings` (array, required): Training ratings
- Returns: `ApiOk`

**POST** `/api/reward/predict`
- Predict reward score
- Request Body: `RewardPredictRequest`
- Returns: `RewardPrediction`
  - `score`: Reward score (0.0-1.0)

### Safety

**POST** `/api/safety/scan`
- Scan text for safety issues
- Request Body: `SafetyScanRequest`
  - `text` (string, required): Text to scan
- Returns: `SafetyScanResult`
  - `flags`: List of safety flags

### Image Sampling

**POST** `/api/img_sampler/render`
- Render image sample
- Request Body: `ImgSamplerRequest`
  - `prompt` (string, required): Image prompt
  - `sampler` (string, default: "ddim"): Sampler type
- Returns: `ImgSamplerResponse`

### Assistant

**POST** `/api/assistant_run/run`
- Run assistant action
- Request Body: `AssistantRunRequest`
  - `action_id` (string, required): Action ID
  - `params` (object, optional): Action parameters
- Returns: `AssistantRunResponse`

---

## Quality Improvement Features

These endpoints provide advanced quality enhancement and analysis capabilities for voice cloning, image generation, video generation, and training data optimization (IDEA 61-70).

### Multi-Pass Synthesis

**POST** `/api/voice/synthesize/multipass`
- Multi-pass synthesis with quality refinement (IDEA 61)
- Generates multiple synthesis passes, compares quality metrics, and selects the best segments for maximum quality output
- Request Body: `MultiPassSynthesisRequest`
  - `engine` (string, required): Engine name (e.g., chatterbox, xtts, tortoise)
  - `profile_id` (string, required): Voice profile ID
  - `text` (string, required): Text to synthesize (1-10000 characters)
  - `language` (string, optional, default: "en"): Language code (ISO 639-1)
  - `emotion` (string, optional): Emotion to apply
  - `max_passes` (integer, optional, default: 3): Maximum number of passes (1-10)
  - `min_quality_improvement` (float, optional, default: 0.02): Minimum quality improvement to continue (0.0-1.0)
  - `pass_preset` (string, optional): Pass preset - `naturalness_focus`, `similarity_focus`, or `artifact_focus`
  - `adaptive` (boolean, optional, default: true): Adaptively determine optimal pass count
- Returns: `MultiPassSynthesisResponse`
  - `audio_id` (string): Final selected audio ID
  - `audio_url` (string): URL to access the audio
  - `duration` (float): Audio duration in seconds
  - `quality_score` (float): Overall quality score
  - `quality_metrics` (QualityMetrics): Detailed quality metrics
  - `passes_completed` (integer): Number of passes completed
  - `passes` (array of PassResult): All passes for comparison
  - `best_pass` (integer): Pass number with best quality
  - `improvement_tracking` (array of float): Quality improvement per pass

### Reference Audio Pre-Processing

**POST** `/api/profiles/{profile_id}/preprocess-reference`
- Advanced reference audio pre-processing and optimization (IDEA 62)
- Analyzes reference audio for quality issues, enhances it automatically, and selects optimal segments for voice cloning
- Path Parameters:
  - `profile_id` (string, required): Voice profile ID
- Request Body: `ReferenceAudioPreprocessRequest`
  - `profile_id` (string, optional): Profile ID if processing existing profile
  - `reference_audio_path` (string, optional): Path to reference audio file
  - `auto_enhance` (boolean, optional, default: true): Automatically enhance reference audio
  - `select_optimal_segments` (boolean, optional, default: true): Select optimal segments for cloning
  - `min_segment_duration` (float, optional, default: 1.0): Minimum segment duration in seconds (0.5-10.0)
  - `max_segments` (integer, optional, default: 5): Maximum number of segments to select (1-20)
- Returns: `ReferenceAudioPreprocessResponse`
  - `processed_audio_id` (string): ID of processed audio
  - `processed_audio_url` (string): URL to access processed audio
  - `original_analysis` (ReferenceAudioAnalysis): Analysis of original audio
  - `processed_analysis` (ReferenceAudioAnalysis, optional): Analysis of processed audio
  - `improvements_applied` (array of string): List of enhancements applied
  - `quality_improvement` (float): Quality improvement score (0.0-1.0)

### Artifact Removal

**POST** `/api/voice/remove-artifacts`
- Advanced artifact removal and audio repair (IDEA 63)
- Detects various artifacts (clicks, pops, distortion, glitches, phase issues) and applies targeted removal algorithms
- Request Body: `ArtifactRemovalRequest`
  - `audio_id` (string, required): Audio ID to process
  - `artifact_types` (array of string, optional): Specific artifact types to remove - `clicks`, `pops`, `distortion`, `glitches`, `phase_issues`
  - `preview` (boolean, optional, default: false): Preview removal without applying
  - `repair_preset` (string, optional): Repair preset - `click_removal`, `distortion_repair`, or `comprehensive`
- Returns: `ArtifactRemovalResponse`
  - `audio_id` (string): Original audio ID
  - `repaired_audio_id` (string, optional): Repaired audio ID (if not preview)
  - `repaired_audio_url` (string, optional): URL to access repaired audio
  - `artifacts_detected` (array of ArtifactDetection): List of detected artifacts
  - `artifacts_removed` (array of string): Types of artifacts removed
  - `quality_improvement` (float): Quality improvement score (0.0-1.0)
  - `preview_available` (boolean): Whether preview is available

### Voice Characteristic Analysis

**POST** `/api/voice/analyze-characteristics`
- Analyze voice characteristics for preservation and enhancement (IDEA 64)
- Analyzes pitch, formants, timbre, and prosody to preserve voice identity during cloning
- Request Body: `VoiceCharacteristicAnalysisRequest`
  - `audio_id` (string, required): Audio ID to analyze
  - `reference_audio_id` (string, optional): Reference audio for comparison
  - `include_pitch` (boolean, optional, default: true): Include pitch analysis
  - `include_formants` (boolean, optional, default: true): Include formant analysis
  - `include_timbre` (boolean, optional, default: true): Include timbre analysis
  - `include_prosody` (boolean, optional, default: true): Include prosody analysis
- Returns: `VoiceCharacteristicAnalysisResponse`
  - `audio_id` (string): Audio ID analyzed
  - `characteristics` (VoiceCharacteristicData): Voice characteristic data
  - `reference_characteristics` (VoiceCharacteristicData, optional): Reference characteristics for comparison
  - `similarity_score` (float, optional): Similarity score (0.0-1.0)
  - `preservation_score` (float, optional): Preservation score (0.0-1.0)
  - `recommendations` (array of string): List of recommendations

### Prosody Control

**POST** `/api/voice/prosody-control`
- Advanced prosody and intonation control (IDEA 65)
- Fine-tune prosody patterns, pitch contours, rhythm, and stress for natural speech synthesis
- Request Body: `ProsodyControlRequest`
  - `audio_id` (string, required): Audio ID to process
  - `pitch_contour` (array of float, optional): Pitch contour adjustments
  - `rhythm_adjustments` (object, optional): Rhythm adjustments
  - `stress_markers` (array of object, optional): Word stress markers
  - `intonation_pattern` (string, optional): Intonation pattern - `rising`, `falling`, or `flat`
  - `prosody_template` (string, optional): Prosody template name
- Returns: `ProsodyControlResponse`
  - `audio_id` (string): Original audio ID
  - `processed_audio_id` (string): Processed audio ID
  - `processed_audio_url` (string): URL to access processed audio
  - `prosody_applied` (object): Dictionary of prosody adjustments applied
  - `quality_improvement` (float): Quality improvement score (0.0-1.0)

### Face Enhancement

**POST** `/api/image/enhance-face`
- Face quality enhancement for images and videos (IDEA 66)
- Enhances face quality in generated images and videos with multi-stage enhancement
- Request Body: `FaceEnhancementRequest`
  - `image_id` (string, optional): Image ID to enhance
  - `video_id` (string, optional): Video ID to enhance
  - `enhancement_preset` (string, optional): Enhancement preset - `portrait`, `full_body`, or `close_up`
  - `multi_stage` (boolean, optional, default: true): Apply multi-stage enhancement
  - `face_specific` (boolean, optional, default: true): Apply face-specific enhancement
- Returns: `FaceEnhancementResponse`
  - `image_id` (string, optional): Original image ID
  - `video_id` (string, optional): Original video ID
  - `enhanced_image_id` (string, optional): Enhanced image ID
  - `enhanced_video_id` (string, optional): Enhanced video ID
  - `enhanced_image_url` (string, optional): URL to access enhanced image
  - `enhanced_video_url` (string, optional): URL to access enhanced video
  - `original_analysis` (FaceQualityAnalysis): Analysis of original image/video
  - `enhanced_analysis` (FaceQualityAnalysis, optional): Analysis of enhanced image/video
  - `quality_improvement` (float): Quality improvement score (0.0-1.0)

### Temporal Consistency

**POST** `/api/video/temporal-consistency`
- Temporal consistency enhancement for video deepfakes (IDEA 67)
- Analyzes and improves frame-to-frame stability, motion smoothness, and reduces flickering/jitter
- Request Body: `TemporalConsistencyRequest`
  - `video_id` (string, required): Video ID to process
  - `smoothing_strength` (float, optional, default: 0.5): Temporal smoothing strength (0.0-1.0)
  - `motion_consistency` (boolean, optional, default: true): Ensure motion consistency
  - `detect_artifacts` (boolean, optional, default: true): Detect temporal artifacts
- Returns: `TemporalConsistencyResponse`
  - `video_id` (string): Original video ID
  - `processed_video_id` (string): Processed video ID
  - `processed_video_url` (string): URL to access processed video
  - `original_analysis` (TemporalAnalysis): Analysis of original video
  - `processed_analysis` (TemporalAnalysis, optional): Analysis of processed video
  - `quality_improvement` (float): Quality improvement score (0.0-1.0)

### Training Data Optimization

**POST** `/api/training/datasets/{dataset_id}/optimize`
- Advanced training data optimization (IDEA 68)
- Analyzes training data quality, diversity, and coverage, and recommends optimal samples
- Path Parameters:
  - `dataset_id` (string, required): Dataset ID to optimize
- Request Body: `TrainingDataOptimizationRequest`
  - `dataset_id` (string, required): Dataset ID to optimize
  - `analyze_quality` (boolean, optional, default: true): Analyze data quality
  - `select_optimal` (boolean, optional, default: true): Select optimal samples
  - `suggest_augmentation` (boolean, optional, default: true): Suggest augmentation strategies
  - `analyze_diversity` (boolean, optional, default: true): Analyze data diversity
- Returns: `TrainingDataOptimizationResponse`
  - `dataset_id` (string): Original dataset ID
  - `analysis` (TrainingDataAnalysis): Training data analysis results
  - `optimized_dataset_id` (string, optional): ID of optimized dataset (if created)
  - `quality_improvement` (float): Quality improvement score (0.0-1.0)

### Post-Processing Pipeline

**POST** `/api/voice/post-process`
- Advanced post-processing enhancement pipeline (IDEA 70)
- Applies multi-stage enhancement (denoise, normalize, enhance, repair) with quality tracking for each stage
- Supports audio, image, and video processing
- Request Body: `PostProcessingPipelineRequest`
  - `audio_id` (string, optional): Audio ID to process
  - `image_id` (string, optional): Image ID to process
  - `video_id` (string, optional): Video ID to process
  - `enhancement_stages` (array of string, optional): Enhancement stages - `denoise`, `normalize`, `enhance`, `repair`
  - `optimize_order` (boolean, optional, default: true): Optimize enhancement order
  - `preview` (boolean, optional, default: false): Preview without applying
- Returns: `PostProcessingPipelineResponse`
  - `audio_id` (string, optional): Original audio ID
  - `image_id` (string, optional): Original image ID
  - `video_id` (string, optional): Original video ID
  - `processed_audio_id` (string, optional): Processed audio ID
  - `processed_image_id` (string, optional): Processed image ID
  - `processed_video_id` (string, optional): Processed video ID
  - `processed_audio_url` (string, optional): URL to access processed audio
  - `processed_image_url` (string, optional): URL to access processed image
  - `processed_video_url` (string, optional): URL to access processed video
  - `stages_applied` (array of EnhancementStageResult): Results from each enhancement stage
  - `total_quality_improvement` (float): Total quality improvement score (0.0-1.0)
  - `preview_available` (boolean): Whether preview is available

### Engine Recommendation

**GET** `/api/quality/engine-recommendation`
- Get recommended engine based on quality requirements (IDEA 47)
- Analyzes quality requirements and suggests the best engine for the task
- Query Parameters:
  - `target_tier` (string, optional, default: "standard"): Quality tier - `fast`, `standard`, `high`, `ultra`
  - `min_mos_score` (float, optional): Minimum MOS score required (0.0-5.0)
  - `min_similarity` (float, optional): Minimum similarity required (0.0-1.0)
  - `min_naturalness` (float, optional): Minimum naturalness required (0.0-1.0)
- Returns: `EngineRecommendationResponse`
  - `recommended_engine` (string): Recommended engine name (e.g., "xtts", "chatterbox", "tortoise")
  - `target_tier` (string): Quality tier used for recommendation
  - `target_metrics` (object): Target quality metrics used
  - `reasoning` (string): Explanation for the recommendation

### Quality Benchmarking

**POST** `/api/quality/benchmark`
- Run quality benchmark across multiple engines (IDEA 52)
- Tests multiple engines with the same input and compares quality metrics
- Request Body: `BenchmarkRequest`
  - `profile_id` (string, optional): Voice profile ID to use (alternative to reference_audio_id)
  - `reference_audio_id` (string, optional): Reference audio ID to use (alternative to profile_id)
  - `test_text` (string, required): Text to synthesize for benchmarking
  - `language` (string, optional, default: "en"): Language code
  - `engines` (array of string, optional): List of engine names to benchmark (if None, benchmarks all available engines)
  - `enhance_quality` (boolean, optional, default: true): Apply quality enhancement during synthesis
- Returns: `BenchmarkResponse`
  - `results` (array of BenchmarkResult): Benchmark results for each engine
    - `engine` (string): Engine name
    - `success` (boolean): Whether benchmark succeeded
    - `error` (string, optional): Error message if benchmark failed
    - `quality_metrics` (object): Quality metrics (MOS, similarity, naturalness, SNR, artifacts)
    - `performance` (object): Performance metrics (synthesis_time, initialization_time)
  - `total_engines` (integer): Total number of engines tested
  - `successful_engines` (integer): Number of successful benchmarks
  - `benchmark_id` (string, optional): Benchmark ID for tracking historical benchmarks

### Quality Dashboard

**GET** `/api/quality/dashboard`
- Get quality metrics dashboard data (IDEA 49)
- Provides overview, trends, distribution, and alerts for quality metrics
- Query Parameters:
  - `project_id` (string, optional): Project ID to filter by

---

## Analytics

**Base Path:** `/api/analytics`

**Enhanced with ModelExplainer integration** for consistent explainability:
- **ModelExplainer:** Provides SHAP and LIME explanations for quality predictions
- **Caching:** Responses cached for 5 minutes (TTL) for performance
- Uses ModelExplainer from ml_optimization module for consistency

### Analytics Summary

**GET** `/api/analytics/summary`
- Get analytics summary for the application
- Query Parameters:
  - `start_date` (string, optional): Start date (ISO format)
  - `end_date` (string, optional): End date (ISO format)
- Returns: `AnalyticsSummary`
  - `period_start`: Period start date
  - `period_end`: Period end date
  - `total_synthesis`: Total synthesis operations
  - `categories`: Category breakdown
- **Performance:** Typically completes in < 1.0s

### Category Metrics

**GET** `/api/analytics/metrics/{category}`
- Get metrics for a specific category
- Path Parameters:
  - `category` (string, required): Category name (e.g., "Synthesis", "Quality")
- Query Parameters:
  - `interval` (string, optional): Time interval - `hour`, `day`, `week`, `month`
  - `start_date` (string, optional): Start date (ISO format)
  - `end_date` (string, optional): End date (ISO format)
- Returns: `List[AnalyticsMetric]`

### List Categories

**GET** `/api/analytics/categories`
- List all available analytics categories
- Returns: `List[str]`
  - Common categories: "Synthesis", "Projects", "Engines", "Quality", "Performance"

### Explain Quality Prediction

**GET** `/api/analytics/explain-quality`
- Explain quality prediction using SHAP or LIME
- **Uses ModelExplainer** for consistent explainability
- **Cached for 5 minutes** (TTL) for performance
- Query Parameters:
  - `audio_id` (string, required): Audio file ID
  - `method` (string, optional, default: "shap"): Explanation method - `shap` or `lime`
- Returns: `QualityExplanation`
  - `audio_id`: Audio file ID
  - `method`: Explanation method used
  - `feature_importance`: Feature importance scores
  - `explanation`: Explanation details
  - `available_methods`: List of available explanation methods
- Errors: 400 if method not available, 404 if audio not found
- **Performance:** Typically completes in < 5.0s

### Visualize Quality Metrics

**GET** `/api/analytics/visualize-quality`
- Generate visualization of quality metrics
- Requires yellowbrick library
- Returns: Visualization image (PNG/JPEG)
- Errors: 400 if yellowbrick not available

### Export Analytics

**GET** `/api/analytics/export/summary`
- Export analytics summary
- Query Parameters:
  - `format` (string, optional, default: "json"): Export format - `json` or `csv`
- Returns: Analytics summary in requested format

**GET** `/api/analytics/export/metrics/{category}`
- Export category metrics
- Path Parameters:
  - `category` (string, required): Category name
- Query Parameters:
  - `format` (string, optional, default: "json"): Export format - `json` or `csv`
- Returns: Category metrics in requested format

---
  - `days` (integer, optional, default: 30): Number of days to include in trends
- Returns: `QualityDashboardResponse`
  - `overview` (object): Overview statistics
    - `total_syntheses` (integer): Total number of syntheses
    - `average_mos_score` (float): Average MOS score
    - `average_similarity` (float): Average similarity score
    - `average_naturalness` (float): Average naturalness score
    - `quality_tier_distribution` (object): Distribution across quality tiers (fast, standard, high, ultra)
  - `trends` (object): Quality trends over time
    - `mos_score` (array of float): MOS score trend data
    - `similarity` (array of float): Similarity trend data
    - `naturalness` (array of float): Naturalness trend data
    - `dates` (array of string): Dates for trend data
  - `distribution` (object): Quality metric distributions
    - `mos_score` (object): MOS score distribution
    - `similarity` (object): Similarity distribution
    - `naturalness` (object): Naturalness distribution
  - `alerts` (array of object): Quality alerts and warnings
  - `insights` (array of string): Quality insights and recommendations

---

## MCP Dashboard

**Base Path:** `/api/mcp-dashboard`

### MCP Dashboard Summary

**GET** `/api/mcp-dashboard`
- Get MCP dashboard summary with server statistics
- Returns: `MCPDashboardSummary`
  - `total_servers` (integer): Total number of MCP servers
  - `connected_servers` (integer): Number of connected servers
  - `disconnected_servers` (integer): Number of disconnected servers
  - `error_servers` (integer): Number of servers with errors
  - `total_operations` (integer): Total number of operations across all servers
  - `available_operations` (integer): Number of available operations from connected servers

### List MCP Servers

**GET** `/api/mcp-dashboard/servers`
- List all MCP servers
- Returns: Array of `MCPServerResponse`
  - `server_id` (string): Unique server identifier
  - `name` (string): Server name
  - `description` (string): Server description
  - `server_type` (string): Server type (figma, tts, analysis, etc.)
  - `status` (string): Server status (connected, disconnected, error)
  - `endpoint` (string, optional): Server endpoint URL
  - `version` (string, optional): Server version
  - `capabilities` (array of string): List of server capabilities
  - `last_connected` (string, optional): Last connection timestamp
  - `error_message` (string, optional): Error message if status is error
  - `metadata` (object): Additional server metadata

### Get MCP Server

**GET** `/api/mcp-dashboard/servers/{server_id}`
- Get specific MCP server details
- Path Parameters:
  - `server_id` (string, required): Server identifier
- Returns: `MCPServerResponse`
- Errors: 404 if server not found

### Create MCP Server

**POST** `/api/mcp-dashboard/servers`
- Add a new MCP server
- Request Body: `MCPServerCreateRequest`
  - `name` (string, required): Server name
  - `description` (string, required): Server description
  - `server_type` (string, required): Server type
  - `endpoint` (string, optional): Server endpoint URL
  - `version` (string, optional): Server version
  - `capabilities` (array of string, optional): List of capabilities
  - `metadata` (object, optional): Additional metadata
- Returns: `MCPServerResponse` (201 Created)
- Errors: 400 if request is invalid

### Update MCP Server

**PUT** `/api/mcp-dashboard/servers/{server_id}`
- Update an existing MCP server
- Path Parameters:
  - `server_id` (string, required): Server identifier
- Request Body: `MCPServerUpdateRequest`
  - `name` (string, optional): Server name
  - `description` (string, optional): Server description
  - `endpoint` (string, optional): Server endpoint URL
  - `metadata` (object, optional): Additional metadata
- Returns: `MCPServerResponse`
- Errors: 404 if server not found, 400 if request is invalid

### Connect MCP Server

**POST** `/api/mcp-dashboard/servers/{server_id}/connect`
- Connect to an MCP server
- Path Parameters:
  - `server_id` (string, required): Server identifier
- Returns: `MCPServerResponse` with updated status
- Errors: 404 if server not found, 500 if connection fails

### Disconnect MCP Server

**POST** `/api/mcp-dashboard/servers/{server_id}/disconnect`
- Disconnect from an MCP server
- Path Parameters:
  - `server_id` (string, required): Server identifier
- Returns: `MCPServerResponse` with updated status
- Errors: 404 if server not found

### Delete MCP Server

**DELETE** `/api/mcp-dashboard/servers/{server_id}`
- Remove an MCP server
- Path Parameters:
  - `server_id` (string, required): Server identifier
- Returns: 204 No Content
- Errors: 404 if server not found

### List Server Operations

**GET** `/api/mcp-dashboard/servers/{server_id}/operations`
- List operations available from a specific MCP server
- Path Parameters:
  - `server_id` (string, required): Server identifier
- Returns: Array of `MCPOperation`
  - `operation_id` (string): Operation identifier
  - `server_id` (string): Server identifier
  - `operation_name` (string): Operation name
  - `description` (string): Operation description
  - `parameters` (object): Operation parameters
  - `result_type` (string): Result type (json, text, binary)
  - `is_available` (boolean): Whether operation is available
- Errors: 404 if server not found

### List Server Types

**GET** `/api/mcp-dashboard/server-types`
- Get list of available MCP server types
- Returns: Array of string (server type names)

---

## WebSocket Endpoints

See [WEBSOCKET_EVENTS.md](WEBSOCKET_EVENTS.md) for WebSocket documentation.

- `ws://localhost:8000/ws/events` - Legacy heartbeat
- `ws://localhost:8000/ws/realtime?topics=meters,training,batch` - Real-time updates

---

## Summary

**Total Endpoints:** 185+

**Categories:**
- Core: 3 endpoints
- Voice Profiles: 5 endpoints
- Voice Synthesis: 4 endpoints
- Projects: 8 endpoints
- Tracks/Clips: 8 endpoints
- Audio Analysis: 6 endpoints
- Effects: 8 endpoints
- Mixer: 19 endpoints
- Macros: 10 endpoints
- Training: 12 endpoints
- Batch Processing: 7 endpoints
- Transcription: 5 endpoints
- Models: 9 endpoints
- Settings: 5 endpoints
- Backup & Restore: 7 endpoints
- Tag Management: 10 endpoints
- Quality Improvement Features: 13 endpoints
- Quality Testing & Comparison: 4 endpoints (A/B Testing, Engine Recommendation, Quality Benchmarking, Quality Dashboard)
- Search: 1 endpoint
- MCP Dashboard: 10 endpoints (server management, operations, connections)
- Additional: 20+ endpoints

---

**For detailed request/response schemas and examples, see:**
- [API Reference](API_REFERENCE.md)
- [Code Examples](EXAMPLES.md)
- [WebSocket Events](WEBSOCKET_EVENTS.md)

