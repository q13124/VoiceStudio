# VoiceStudio Quantum+ Training System Documentation

Complete documentation for the training system.

## Documentation Files

### 📚 Main Documentation

- **[TRAINING_SYSTEM_REFERENCE.md](TRAINING_SYSTEM_REFERENCE.md)** - Complete reference for all training modules
- **[TRAINING_USAGE_GUIDE.md](TRAINING_USAGE_GUIDE.md)** - Usage guide with examples

### 🔧 Related Documentation

- **[../engines/ENGINE_REFERENCE.md](../engines/ENGINE_REFERENCE.md)** - Engine reference
- **[../audio/AUDIO_PROCESSING_REFERENCE.md](../audio/AUDIO_PROCESSING_REFERENCE.md)** - Audio processing reference

---

## Quick Start

### Basic Training

```python
from app.core.training import XTTSTrainer

# Create trainer
trainer = XTTSTrainer(
    base_model="tts_models/multilingual/multi-dataset/xtts_v2",
    device="cuda",
    gpu=True
)

# Prepare dataset
metadata_path = trainer.prepare_dataset(
    audio_files=["audio1.wav", "audio2.wav"],
    transcripts=["Text 1", "Text 2"]
)

# Initialize and train
trainer.initialize_model()
result = await trainer.train(
    metadata_path=metadata_path,
    epochs=100,
    batch_size=4,
    learning_rate=0.0001
)

# Export model
trainer.export_model("my_voice")
```

---

## Training Modules

### Core Modules
- **xtts_trainer.py** - XTTS v2 training engine
- **unified_trainer.py** - Unified interface for multiple engines
- **auto_trainer.py** - Automated training with optimal parameters
- **parameter_optimizer.py** - Hyperparameter optimization
- **training_progress_monitor.py** - Real-time progress tracking

---

## Key Features

### Training Capabilities
- Fine-tune XTTS v2 models
- Dataset preparation and validation
- Training progress tracking
- Model checkpointing
- Model export

### Advanced Features
- Automated parameter selection
- Hyperparameter optimization
- Data augmentation
- Real-time monitoring
- GPU acceleration

---

## Getting Help

### Documentation
- See [TRAINING_SYSTEM_REFERENCE.md](TRAINING_SYSTEM_REFERENCE.md) for module details
- See [TRAINING_USAGE_GUIDE.md](TRAINING_USAGE_GUIDE.md) for usage examples

### API Endpoints
- `POST /api/training/datasets` - Create dataset
- `POST /api/training/start` - Start training
- `GET /api/training/status/{training_id}` - Get training status
- `GET /api/training/logs/{training_id}` - Get training logs

---

**Last Updated:** 2025-01-28

