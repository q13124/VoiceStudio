# Training System Reference

Complete reference for all training modules in VoiceStudio Quantum+.

## Table of Contents

1. [Overview](#overview)
2. [Training Modules](#training-modules)
3. [Training Workflows](#training-workflows)
4. [Configuration Parameters](#configuration-parameters)
5. [Performance Notes](#performance-notes)

---

## Overview

VoiceStudio Quantum+ includes a comprehensive training system for fine-tuning voice models:

- **XTTS Training:** Fine-tune XTTS v2 models on custom voice data
- **Unified Trainer:** Unified interface for multiple training engines
- **Auto Trainer:** Automated training with optimal parameter selection
- **Parameter Optimizer:** Hyperparameter optimization
- **Progress Monitor:** Real-time training progress tracking

All training modules support GPU acceleration and checkpointing.

---

## Training Modules

### `XTTSTrainer`

Real training implementation for Coqui TTS XTTS v2 models.

**File:** `app/core/training/xtts_trainer.py`

**Features:**
- Fine-tuning XTTS v2 models
- Dataset preparation and validation
- Training progress tracking
- Model checkpointing and export
- Data augmentation
- Hyperparameter optimization

**Usage:**
```python
from app.core.training import XTTSTrainer

trainer = XTTSTrainer(
    base_model="tts_models/multilingual/multi-dataset/xtts_v2",
    device="cuda",
    gpu=True,
    output_dir="models/trained"
)

# Prepare dataset
metadata_path = trainer.prepare_dataset(
    audio_files=["audio1.wav", "audio2.wav"],
    transcripts=["Text 1", "Text 2"]
)

# Initialize model
trainer.initialize_model()

# Train
async def progress_callback(progress):
    print(f"Epoch: {progress['epoch']}, Loss: {progress['loss']:.4f}")

result = await trainer.train(
    metadata_path=metadata_path,
    epochs=100,
    batch_size=4,
    learning_rate=0.0001,
    progress_callback=progress_callback
)

# Export model
trainer.export_model("my_voice_model")
```

**Methods:**
- `prepare_dataset()` - Prepare training dataset
- `initialize_model()` - Initialize model for training
- `train()` - Start training
- `export_model()` - Export trained model
- `cancel_training()` - Cancel ongoing training
- `create_augmentation_pipeline()` - Create data augmentation pipeline

---

### `UnifiedTrainer`

Unified interface for multiple training engines.

**File:** `app/core/training/unified_trainer.py`

**Features:**
- Multiple training engines (XTTS, RVC, etc.)
- Unified training interface
- Engine selection based on requirements
- Training progress tracking
- Model checkpointing
- Training cancellation

**Usage:**
```python
from app.core.training import UnifiedTrainer, create_unified_trainer

trainer = create_unified_trainer(
    engine="xtts",
    device="cuda",
    gpu=True,
    output_dir="models/trained"
)

# Prepare dataset
metadata_path = trainer.prepare_dataset(
    audio_files=["audio1.wav", "audio2.wav"],
    transcripts=["Text 1", "Text 2"]
)

# Initialize model
trainer.initialize_model()

# Train
result = await trainer.train(
    metadata_path=metadata_path,
    epochs=100,
    batch_size=4,
    learning_rate=0.0001
)

# Export model
trainer.export_model("my_voice_model")
```

**Supported Engines:**
- `xtts` - XTTS v2 training (fully supported)
- `rvc` - RVC training (planned)

---

### `AutoTrainer`

Automated training with optimal parameter selection.

**File:** `app/core/training/auto_trainer.py`

**Features:**
- Automatic parameter selection
- Dataset analysis
- Optimal configuration recommendation
- Automated training execution
- Quality assessment

**Usage:**
```python
from app.core.training import AutoTrainer, create_auto_trainer

trainer = create_auto_trainer(
    engine="xtts",
    device="cuda",
    gpu=True
)

# Analyze dataset and get recommendations
recommendations = trainer.analyze_dataset(
    audio_files=["audio1.wav", "audio2.wav"],
    transcripts=["Text 1", "Text 2"]
)

print(f"Recommended epochs: {recommendations['epochs']}")
print(f"Recommended batch size: {recommendations['batch_size']}")
print(f"Recommended learning rate: {recommendations['learning_rate']}")

# Train with auto-selected parameters
result = await trainer.train_auto(
    audio_files=["audio1.wav", "audio2.wav"],
    transcripts=["Text 1", "Text 2"]
)
```

**Methods:**
- `analyze_dataset()` - Analyze dataset and get recommendations
- `train_auto()` - Train with auto-selected parameters
- `get_optimal_config()` - Get optimal configuration

---

### `ParameterOptimizer`

Hyperparameter optimization for training.

**File:** `app/core/training/parameter_optimizer.py`

**Features:**
- Hyperparameter optimization
- Multiple optimization algorithms (Optuna, Ray Tune, Hyperopt)
- Search space definition
- Optimization results analysis

**Usage:**
```python
from app.core.training import ParameterOptimizer, create_parameter_optimizer

optimizer = create_parameter_optimizer(
    engine="xtts",
    device="cuda",
    gpu=True
)

# Define search space
search_space = {
    "learning_rate": (0.00001, 0.001),
    "batch_size": [2, 4, 8, 16],
    "epochs": [50, 100, 200]
}

# Optimize
best_params = await optimizer.optimize(
    metadata_path=metadata_path,
    search_space=search_space,
    n_trials=20,
    optimization_algorithm="optuna"
)

print(f"Best learning rate: {best_params['learning_rate']}")
print(f"Best batch size: {best_params['batch_size']}")
print(f"Best epochs: {best_params['epochs']}")
```

**Optimization Algorithms:**
- `optuna` - Optuna (Tree-structured Parzen Estimator)
- `ray_tune` - Ray Tune (ASHAScheduler)
- `hyperopt` - Hyperopt (TPE)

---

### `TrainingProgressMonitor`

Real-time training progress tracking.

**File:** `app/core/training/training_progress_monitor.py`

**Features:**
- Real-time progress tracking
- Loss monitoring
- Epoch tracking
- Checkpoint monitoring
- Progress callbacks

**Usage:**
```python
from app.core.training import TrainingProgressMonitor, create_training_progress_monitor

monitor = create_training_progress_monitor()

# Register callback
def on_progress(progress):
    print(f"Epoch: {progress['epoch']}/{progress['total_epochs']}")
    print(f"Loss: {progress['loss']:.4f}")
    print(f"Progress: {progress['progress']:.1f}%")

monitor.register_callback(on_progress)

# Start monitoring
monitor.start_monitoring(training_id="training_123")

# Get current status
status = monitor.get_status("training_123")
print(f"Status: {status['status']}")
print(f"Current epoch: {status['current_epoch']}")
```

**Methods:**
- `register_callback()` - Register progress callback
- `start_monitoring()` - Start monitoring training
- `get_status()` - Get current training status
- `stop_monitoring()` - Stop monitoring

---

## Training Workflows

### Basic Training Workflow

1. **Prepare Dataset:**
```python
metadata_path = trainer.prepare_dataset(
    audio_files=["audio1.wav", "audio2.wav"],
    transcripts=["Text 1", "Text 2"]
)
```

2. **Initialize Model:**
```python
trainer.initialize_model()
```

3. **Train:**
```python
result = await trainer.train(
    metadata_path=metadata_path,
    epochs=100,
    batch_size=4,
    learning_rate=0.0001
)
```

4. **Export Model:**
```python
trainer.export_model("my_voice_model")
```

### Automated Training Workflow

1. **Analyze Dataset:**
```python
recommendations = trainer.analyze_dataset(
    audio_files=["audio1.wav", "audio2.wav"],
    transcripts=["Text 1", "Text 2"]
)
```

2. **Train with Auto Parameters:**
```python
result = await trainer.train_auto(
    audio_files=["audio1.wav", "audio2.wav"],
    transcripts=["Text 1", "Text 2"]
)
```

### Hyperparameter Optimization Workflow

1. **Define Search Space:**
```python
search_space = {
    "learning_rate": (0.00001, 0.001),
    "batch_size": [2, 4, 8, 16],
    "epochs": [50, 100, 200]
}
```

2. **Optimize:**
```python
best_params = await optimizer.optimize(
    metadata_path=metadata_path,
    search_space=search_space,
    n_trials=20
)
```

3. **Train with Best Parameters:**
```python
result = await trainer.train(
    metadata_path=metadata_path,
    **best_params
)
```

---

## Configuration Parameters

### Training Parameters

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| **Epochs** | 10-1000 | 100 | Number of training epochs |
| **Batch Size** | 1-32 | 4 | Training batch size |
| **Learning Rate** | 0.00001-0.01 | 0.0001 | Learning rate for optimizer |
| **GPU** | true/false | true | Use GPU acceleration |

### Dataset Requirements

- **Minimum Audio Files:** 10 files
- **Recommended Audio Files:** 50+ files
- **Audio Duration:** 1-10 seconds per file
- **Total Duration:** 5+ minutes recommended
- **Sample Rate:** 22050 Hz or 24000 Hz
- **Format:** WAV, FLAC, MP3

### Data Augmentation

- **Gaussian Noise:** Add noise to audio
- **Time Stretch:** Stretch/compress time
- **Pitch Shift:** Shift pitch
- **Time Shift:** Shift audio in time

---

## Performance Notes

### GPU Requirements

- **Minimum:** 4GB VRAM (small datasets)
- **Recommended:** 8GB+ VRAM (medium datasets)
- **Optimal:** 16GB+ VRAM (large datasets, batch processing)

### Training Time

- **Small Dataset (10-20 files):** 30-60 minutes
- **Medium Dataset (50-100 files):** 2-4 hours
- **Large Dataset (200+ files):** 8+ hours

### Memory Considerations

- Batch size affects memory usage
- Larger batch sizes = faster training but more memory
- Use gradient accumulation for large models

### Checkpointing

- Checkpoints saved every N epochs (configurable)
- Resume training from checkpoint
- Checkpoint size: ~1-2GB per checkpoint

---

**Last Updated:** 2025-01-28

