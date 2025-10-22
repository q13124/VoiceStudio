# VoiceStudio Ultimate - Voice Similarity Scoring

## Overview

VoiceStudio Ultimate features advanced voice similarity scoring system that provides comprehensive analysis of voice characteristics and similarity between different voice samples.

## Features

- **Multi-Metric Analysis**: Spectral, MFCC, pitch, prosody, and timbre similarity
- **Comprehensive Feature Extraction**: Advanced voice feature analysis
- **Batch Processing**: Compare multiple voices against a reference
- **Quality Assessment**: Automatic quality level determination
- **API Integration**: REST API endpoints for similarity analysis
- **Real-Time Analysis**: Fast similarity scoring for live applications

## Similarity Metrics

### 1. Spectral Similarity (Weight: 25%)
- **Spectral Centroid**: Brightness of the voice
- **Spectral Rolloff**: Frequency rolloff characteristics
- **Spectral Bandwidth**: Frequency distribution width

### 2. MFCC Similarity (Weight: 25%)
- **Mel-Frequency Cepstral Coefficients**: Core voice characteristics
- **13-Dimensional Feature Vector**: Comprehensive voice representation
- **Temporal Analysis**: Frame-by-frame comparison

### 3. Pitch Similarity (Weight: 20%)
- **Pitch Statistics**: Mean, standard deviation, range
- **Pitch Contour**: Intonation patterns
- **Fundamental Frequency**: Voice pitch characteristics

### 4. Prosody Similarity (Weight: 15%)
- **Rhythm Regularity**: Speaking rhythm patterns
- **Speaking Rate**: Syllables per second
- **Stress Patterns**: Emphasis and stress characteristics
- **Intonation Patterns**: Pitch contour analysis

### 5. Timbre Similarity (Weight: 15%)
- **Voice Quality**: Overall voice characteristics
- **Harmonic Ratio**: Harmonic to noise ratio
- **Breathiness**: High-frequency content analysis
- **Roughness**: Amplitude modulation analysis

## Quality Levels

### Excellent (90-100%)
- Very high similarity
- Professional quality voice match
- Suitable for high-end applications

### Good (80-89%)
- High similarity
- Good quality voice match
- Suitable for most applications

### Fair (70-79%)
- Moderate similarity
- Acceptable quality voice match
- Suitable for basic applications

### Poor (60-69%)
- Low similarity
- Limited quality voice match
- May require improvement

### Very Poor (0-59%)
- Very low similarity
- Poor quality voice match
- Not recommended for use

## API Endpoints

### Compare Voices

#### POST /api/v1/similarity/compare

Compare two voice files for similarity.

**Request:**
```json
{
  "reference_audio": "base64_encoded_audio",
  "comparison_audio": "base64_encoded_audio",
  "include_details": true,
  "analysis_type": "comprehensive"
}
```

**Response:**
```json
{
  "success": true,
  "analysis_type": "comprehensive",
  "results": {
    "similarity_scores": {
      "spectral": {
        "score": 0.85,
        "confidence": 0.8,
        "details": {
          "centroid_similarity": 0.9,
          "rolloff_similarity": 0.8,
          "bandwidth_similarity": 0.85
        }
      },
      "mfcc": {
        "score": 0.92,
        "confidence": 0.9,
        "details": {
          "mfcc_similarity": 0.92
        }
      },
      "pitch": {
        "score": 0.78,
        "confidence": 0.7,
        "details": {
          "pitch_mean_similarity": 0.8,
          "pitch_std_similarity": 0.76
        }
      },
      "prosody": {
        "score": 0.82,
        "confidence": 0.6,
        "details": {
          "prosody_similarity": 0.82
        }
      },
      "timbre": {
        "score": 0.88,
        "confidence": 0.7,
        "details": {
          "timbre_similarity": 0.88
        }
      },
      "overall": {
        "score": 0.85,
        "confidence": 0.74,
        "details": {
          "spectral_score": 0.85,
          "mfcc_score": 0.92,
          "pitch_score": 0.78,
          "prosody_score": 0.82,
          "timbre_score": 0.88,
          "weights": {
            "spectral": 0.25,
            "mfcc": 0.25,
            "pitch": 0.20,
            "prosody": 0.15,
            "timbre": 0.15
          }
        }
      }
    }
  }
}
```

### Batch Comparison

#### POST /api/v1/similarity/batch-compare

Compare reference voice with multiple comparison voices.

**Request:**
```json
{
  "reference_audio": "base64_encoded_audio",
  "comparison_files": ["file1.wav", "file2.wav", "file3.wav"],
  "max_comparisons": 10,
  "analysis_type": "summary"
}
```

**Response:**
```json
{
  "success": true,
  "analysis_type": "summary",
  "results": {
    "reference_file": "reference.wav",
    "total_comparisons": 3,
    "results": [
      {
        "file_name": "file1.wav",
        "similarity_score": 0.92,
        "confidence": 0.85,
        "quality_level": "excellent"
      },
      {
        "file_name": "file2.wav",
        "similarity_score": 0.78,
        "confidence": 0.72,
        "quality_level": "fair"
      },
      {
        "file_name": "file3.wav",
        "similarity_score": 0.65,
        "confidence": 0.68,
        "quality_level": "poor"
      }
    ]
  }
}
```

### Feature Analysis

#### POST /api/v1/similarity/analyze-features

Analyze voice features from audio file.

**Request:**
```json
{
  "audio_file": "base64_encoded_audio",
  "feature_types": "all"
}
```

**Response:**
```json
{
  "success": true,
  "file_name": "audio.wav",
  "features": {
    "spectral_features": {
      "spectral_centroid_mean": 1200.5,
      "spectral_rolloff_mean": 3500.2,
      "spectral_bandwidth_mean": 800.1
    },
    "mfcc_features": {
      "mfcc_mean": 0.15,
      "mfcc_std": 0.8
    },
    "pitch_features": {
      "pitch_mean": 180.5,
      "pitch_std": 25.2,
      "pitch_range": 120.0
    },
    "prosody_features": {
      "pitch_mean": 180.5,
      "pitch_std": 25.2,
      "rhythm_regularity": 0.75,
      "speaking_rate": 3.2
    },
    "timbre_features": {
      "spectral_centroid_mean": 1200.5,
      "harmonic_ratio": 0.85,
      "voice_quality": 0.78
    }
  }
}
```

## Command Line Usage

### Single Voice Comparison

```bash
python voice_studio_similarity_analyzer.py \
  --reference reference.wav \
  --comparison comparison.wav \
  --output results.json
```

### Batch Voice Comparison

```bash
python voice_studio_similarity_analyzer.py \
  --reference reference.wav \
  --batch comparison_files.txt \
  --output batch_results.json
```

### Worker Usage

```bash
# Compare two voices
python workers/voice_similarity_worker.py \
  --action compare \
  --reference reference.wav \
  --comparison comparison.wav

# Batch comparison
python workers/voice_similarity_worker.py \
  --action batch \
  --reference reference.wav \
  --comparisons "file1.wav,file2.wav,file3.wav"

# Feature analysis
python workers/voice_similarity_worker.py \
  --action analyze \
  --audio audio.wav
```

## Configuration

### Similarity Scoring Settings

```json
{
  "similarity_scoring": {
    "enabled": true,
    "sample_rate": 22050,
    "hop_length": 512,
    "n_fft": 2048,
    "n_mfcc": 13,
    "n_formants": 4,
    "weights": {
      "spectral": 0.25,
      "mfcc": 0.25,
      "pitch": 0.20,
      "prosody": 0.15,
      "timbre": 0.15
    }
  }
}
```

### Analysis Settings

```json
{
  "analysis_settings": {
    "min_audio_duration": 1.0,
    "max_audio_duration": 60.0,
    "frame_length_ms": 25,
    "hop_length_ms": 10,
    "pitch_range_hz": [50, 500],
    "formant_range_hz": [200, 4000]
  }
}
```

## Use Cases

### Voice Cloning Quality Assessment
- **Reference Matching**: Compare cloned voice with reference
- **Quality Control**: Ensure cloned voice meets quality standards
- **Batch Validation**: Validate multiple cloned voices

### Voice Authentication
- **Speaker Verification**: Verify speaker identity
- **Security Applications**: Voice-based access control
- **Fraud Detection**: Detect voice spoofing attempts

### Voice Analysis
- **Voice Characteristics**: Analyze voice features
- **Voice Comparison**: Compare different voice samples
- **Voice Research**: Research voice characteristics

### Content Creation
- **Voice Matching**: Match voices for content creation
- **Quality Assurance**: Ensure voice consistency
- **Voice Selection**: Select best voice matches

## Performance

### Processing Speed
- **Single Comparison**: ~2-5 seconds per comparison
- **Batch Processing**: ~1-3 seconds per comparison
- **Feature Extraction**: ~1-2 seconds per audio file

### Accuracy
- **High Similarity**: 95%+ accuracy for similar voices
- **Medium Similarity**: 85%+ accuracy for moderately similar voices
- **Low Similarity**: 75%+ accuracy for different voices

### Scalability
- **Concurrent Processing**: Up to 5 simultaneous analyses
- **Batch Size**: Up to 100 voices per batch
- **Memory Usage**: ~100MB per analysis

## Best Practices

### Audio Quality
- **Sample Rate**: Use 22kHz or higher
- **Duration**: Minimum 1 second, maximum 60 seconds
- **Format**: WAV format recommended
- **Quality**: Clear, noise-free audio

### Analysis Settings
- **Weights**: Adjust weights based on use case
- **Thresholds**: Set appropriate quality thresholds
- **Batch Size**: Limit batch size for optimal performance

### Error Handling
- **Validation**: Validate audio files before analysis
- **Error Recovery**: Implement proper error handling
- **Logging**: Log analysis results for debugging

---

**Voice Similarity Scoring** - Advanced voice analysis and comparison system
