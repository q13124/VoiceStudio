# VoiceStudio Ultimate - Batch Processing

## Overview

VoiceStudio Ultimate features comprehensive batch processing capabilities for handling multiple voice cloning, audio processing, and analysis operations efficiently.

## Features

- **Multiple Job Types**: Voice cloning, audio processing, similarity analysis, quality assessment, feature extraction, mixed operations
- **Concurrent Processing**: Multi-threaded processing with configurable worker limits
- **Progress Tracking**: Real-time job status and progress monitoring
- **Export Options**: JSON, CSV, and Excel export formats
- **Job Management**: Pause, resume, cancel operations
- **Error Handling**: Comprehensive error handling and retry mechanisms
- **API Integration**: REST API endpoints for batch operations

## Job Types

### 1. Voice Cloning
- **Description**: Batch voice cloning operations
- **Max Items**: 100
- **Timeout per Item**: 60 seconds
- **Parameters**: text, reference_audio, engine, language, quality

### 2. Audio Processing
- **Description**: Batch audio processing with DSP chains
- **Max Items**: 200
- **Timeout per Item**: 30 seconds
- **Parameters**: dsp_chain, output_format

### 3. Similarity Analysis
- **Description**: Batch voice similarity analysis
- **Max Items**: 50
- **Timeout per Item**: 45 seconds
- **Parameters**: reference_path, comparison_path

### 4. Quality Assessment
- **Description**: Batch audio quality assessment
- **Max Items**: 100
- **Timeout per Item**: 20 seconds
- **Parameters**: quality_metrics

### 5. Feature Extraction
- **Description**: Batch voice feature extraction
- **Max Items**: 150
- **Timeout per Item**: 25 seconds
- **Parameters**: feature_types

### 6. Mixed Operations
- **Description**: Batch mixed operations
- **Max Items**: 75
- **Timeout per Item**: 90 seconds
- **Parameters**: operation_type, operation-specific parameters

## API Endpoints

### Create Batch Job

#### POST /api/v1/batch/create-job

Create a new batch processing job.

**Request:**
```json
{
  "job_type": "voice_cloning",
  "items_file": "batch_items.json",
  "configuration": {
    "max_workers": 8,
    "chunk_size": 10
  }
}
```

**Response:**
```json
{
  "success": true,
  "job_id": "batch_job_12345",
  "job_type": "voice_cloning",
  "total_items": 25,
  "status": "queued"
}
```

### Get Job Status

#### GET /api/v1/batch/jobs/{job_id}/status

Get batch job status and progress.

**Response:**
```json
{
  "success": true,
  "job_id": "batch_job_12345",
  "job_type": "voice_cloning",
  "status": "processing",
  "progress": {
    "total_items": 25,
    "completed_items": 15,
    "failed_items": 2,
    "success_rate": 0.6,
    "percentage": 68.0
  },
  "created_at": "2025-01-21T12:00:00Z",
  "started_at": "2025-01-21T12:01:00Z"
}
```

### Get Job Results

#### GET /api/v1/batch/jobs/{job_id}/results

Get detailed batch job results.

**Response:**
```json
{
  "success": true,
  "job_id": "batch_job_12345",
  "job_type": "voice_cloning",
  "status": "completed",
  "results": [
    {
      "item_id": "batch_job_12345_item_0",
      "status": "completed",
      "processing_time": 45.2,
      "created_at": "2025-01-21T12:00:00Z",
      "completed_at": "2025-01-21T12:00:45Z",
      "result": {
        "success": true,
        "output_file": "cloned_voice_1.wav",
        "quality_score": 0.95
      }
    }
  ],
  "summary": {
    "total_items": 25,
    "completed_items": 23,
    "failed_items": 2,
    "success_rate": 0.92
  }
}
```

### Export Results

#### GET /api/v1/batch/jobs/{job_id}/export?format=json

Export batch job results in various formats.

**Response:**
```json
{
  "success": true,
  "output_path": "outputs/batch_job_12345_results.json"
}
```

## Batch Items Format

### Voice Cloning Items

```json
[
  {
    "input_path": "reference_voice_1.wav",
    "output_path": "cloned_voice_1.wav",
    "parameters": {
      "text": "Hello, this is VoiceStudio Ultimate!",
      "reference_audio": "reference_voice_1.wav",
      "engine": "xtts",
      "language": "en",
      "quality": "high"
    }
  },
  {
    "input_path": "reference_voice_2.wav",
    "output_path": "cloned_voice_2.wav",
    "parameters": {
      "text": "Welcome to the future of voice cloning!",
      "reference_audio": "reference_voice_2.wav",
      "engine": "openvoice",
      "language": "en",
      "quality": "high"
    }
  }
]
```

### Audio Processing Items

```json
[
  {
    "input_path": "input_audio_1.wav",
    "output_path": "processed_audio_1.wav",
    "parameters": {
      "dsp_chain": {
        "deesser": {
          "enabled": true,
          "threshold": -20.0,
          "ratio": 4.0
        },
        "eq": {
          "enabled": true,
          "bands": [
            {
              "freq": 80,
              "gain": 0,
              "q": 0.7,
              "type": "highpass"
            }
          ]
        },
        "compressor": {
          "enabled": true,
          "threshold": -18.0,
          "ratio": 3.0,
          "attack": 5.0,
          "release": 50.0
        }
      },
      "output_format": "wav"
    }
  }
]
```

### Similarity Analysis Items

```json
[
  {
    "input_path": "reference.wav",
    "output_path": "similarity_results_1.json",
    "parameters": {
      "reference_path": "reference.wav",
      "comparison_path": "comparison_1.wav"
    }
  }
]
```

## Command Line Usage

### Create Batch Job

```bash
python voice_studio_batch_processor.py \
  --action create \
  --job-type voice_cloning \
  --items voice_cloning_batch.json \
  --config job_config.json
```

### Get Job Status

```bash
python voice_studio_batch_processor.py \
  --action status \
  --job-id batch_job_12345
```

### Get Job Results

```bash
python voice_studio_batch_processor.py \
  --action results \
  --job-id batch_job_12345
```

### Export Results

```bash
python voice_studio_batch_processor.py \
  --action export \
  --job-id batch_job_12345 \
  --format csv
```

### Worker Usage

```bash
# Create batch job
python workers/batch_processing_worker.py \
  --action create \
  --job-type voice_cloning \
  --items voice_cloning_batch.json

# Get job status
python workers/batch_processing_worker.py \
  --action status \
  --job-id batch_job_12345

# Export results
python workers/batch_processing_worker.py \
  --action export \
  --job-id batch_job_12345 \
  --format excel
```

## Configuration

### Batch Processing Settings

```json
{
  "batch_processing": {
    "enabled": true,
    "max_workers": 8,
    "max_concurrent_jobs": 3,
    "chunk_size": 10,
    "timeout_seconds": 300,
    "retry_attempts": 3,
    "retry_delay": 5,
    "auto_cleanup": true,
    "cleanup_interval_hours": 24
  }
}
```

### Job Type Settings

```json
{
  "job_types": {
    "voice_cloning": {
      "enabled": true,
      "max_items": 100,
      "timeout_per_item": 60
    },
    "audio_processing": {
      "enabled": true,
      "max_items": 200,
      "timeout_per_item": 30
    }
  }
}
```

## Performance

### Processing Speed
- **Voice Cloning**: ~45-60 seconds per item
- **Audio Processing**: ~20-30 seconds per item
- **Similarity Analysis**: ~30-45 seconds per item
- **Quality Assessment**: ~15-20 seconds per item
- **Feature Extraction**: ~20-25 seconds per item

### Scalability
- **Max Workers**: 8 concurrent workers
- **Max Concurrent Jobs**: 3 simultaneous jobs
- **Chunk Size**: 10 items per chunk
- **Max Items per Job**: 1000 items

### Resource Usage
- **Memory**: ~200MB per active job
- **Storage**: ~100MB per 100 items
- **CPU**: Scales with worker count

## Best Practices

### Job Design
- **Chunk Size**: Use appropriate chunk sizes (5-15 items)
- **Timeout**: Set realistic timeouts based on operation complexity
- **Retry Logic**: Enable retry for transient failures
- **Error Handling**: Implement proper error handling

### Resource Management
- **Worker Limits**: Don't exceed system capabilities
- **Storage Cleanup**: Enable automatic cleanup
- **Memory Monitoring**: Monitor memory usage
- **Queue Management**: Manage job queue size

### Error Handling
- **Validation**: Validate items before processing
- **Retry Logic**: Implement retry for failed items
- **Logging**: Enable comprehensive logging
- **Monitoring**: Monitor job progress and errors

## Use Cases

### Content Production
- **Voice Cloning**: Batch clone multiple voices for content
- **Audio Processing**: Process large audio libraries
- **Quality Control**: Batch quality assessment

### Research and Development
- **Feature Extraction**: Extract features from large datasets
- **Similarity Analysis**: Compare multiple voice samples
- **Performance Testing**: Test system performance

### Enterprise Applications
- **Voice Synthesis**: Batch voice synthesis for applications
- **Audio Enhancement**: Enhance large audio collections
- **Quality Assurance**: Automated quality assessment

---

**Batch Processing** - Efficient large-scale voice processing operations
