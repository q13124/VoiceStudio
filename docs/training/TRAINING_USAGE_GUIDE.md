# Training System Usage Guide

Complete guide to using the training system in VoiceStudio Quantum+.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Common Workflows](#common-workflows)
3. [Best Practices](#best-practices)
4. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Basic Training Setup

```python
from app.core.training import XTTSTrainer

# Create trainer
trainer = XTTSTrainer(
    base_model="tts_models/multilingual/multi-dataset/xtts_v2",
    device="cuda",
    gpu=True,
    output_dir="models/trained"
)
```

### Prepare Dataset

```python
# Prepare dataset from audio files
metadata_path = trainer.prepare_dataset(
    audio_files=[
        "dataset/audio1.wav",
        "dataset/audio2.wav",
        "dataset/audio3.wav"
    ],
    transcripts=[
        "This is the first audio file.",
        "This is the second audio file.",
        "This is the third audio file."
    ]
)
```

### Initialize Model

```python
# Initialize model for training
if not trainer.initialize_model():
    raise RuntimeError("Failed to initialize model")
```

### Start Training

```python
# Define progress callback
async def progress_callback(progress):
    epoch = progress.get('epoch', 0)
    loss = progress.get('loss', 0.0)
    print(f"Epoch {epoch}: Loss = {loss:.4f}")

# Start training
result = await trainer.train(
    metadata_path=metadata_path,
    epochs=100,
    batch_size=4,
    learning_rate=0.0001,
    progress_callback=progress_callback
)

print(f"Training completed: {result['status']}")
print(f"Final loss: {result['final_loss']:.4f}")
```

### Export Model

```python
# Export trained model
trainer.export_model("my_custom_voice")
```

---

## Common Workflows

### Workflow 1: Basic Voice Training

```python
from app.core.training import XTTSTrainer

# 1. Create trainer
trainer = XTTSTrainer(
    base_model="tts_models/multilingual/multi-dataset/xtts_v2",
    device="cuda",
    gpu=True
)

# 2. Prepare dataset
metadata_path = trainer.prepare_dataset(
    audio_files=["audio1.wav", "audio2.wav", "audio3.wav"],
    transcripts=["Text 1", "Text 2", "Text 3"]
)

# 3. Initialize model
trainer.initialize_model()

# 4. Train
result = await trainer.train(
    metadata_path=metadata_path,
    epochs=100,
    batch_size=4,
    learning_rate=0.0001
)

# 5. Export
trainer.export_model("my_voice")
```

### Workflow 2: Automated Training

```python
from app.core.training import AutoTrainer, create_auto_trainer

# 1. Create auto trainer
trainer = create_auto_trainer(engine="xtts", device="cuda", gpu=True)

# 2. Analyze dataset
recommendations = trainer.analyze_dataset(
    audio_files=["audio1.wav", "audio2.wav"],
    transcripts=["Text 1", "Text 2"]
)

# 3. Train with auto parameters
result = await trainer.train_auto(
    audio_files=["audio1.wav", "audio2.wav"],
    transcripts=["Text 1", "Text 2"]
)
```

### Workflow 3: Hyperparameter Optimization

```python
from app.core.training import ParameterOptimizer, create_parameter_optimizer

# 1. Create optimizer
optimizer = create_parameter_optimizer(engine="xtts", device="cuda", gpu=True)

# 2. Define search space
search_space = {
    "learning_rate": (0.00001, 0.001),
    "batch_size": [2, 4, 8, 16],
    "epochs": [50, 100, 200]
}

# 3. Optimize
best_params = await optimizer.optimize(
    metadata_path=metadata_path,
    search_space=search_space,
    n_trials=20,
    optimization_algorithm="optuna"
)

# 4. Train with best parameters
from app.core.training import XTTSTrainer
trainer = XTTSTrainer(device="cuda", gpu=True)
trainer.initialize_model()
result = await trainer.train(metadata_path=metadata_path, **best_params)
```

### Workflow 4: Training with Progress Monitoring

```python
from app.core.training import (
    XTTSTrainer,
    TrainingProgressMonitor,
    create_training_progress_monitor
)

# 1. Create trainer and monitor
trainer = XTTSTrainer(device="cuda", gpu=True)
monitor = create_training_progress_monitor()

# 2. Register progress callback
def on_progress(progress):
    epoch = progress.get('epoch', 0)
    loss = progress.get('loss', 0.0)
    progress_pct = progress.get('progress', 0.0)
    print(f"Epoch {epoch}: Loss = {loss:.4f}, Progress = {progress_pct:.1f}%")

monitor.register_callback(on_progress)

# 3. Start monitoring
monitor.start_monitoring(training_id="training_123")

# 4. Train
metadata_path = trainer.prepare_dataset(...)
trainer.initialize_model()
result = await trainer.train(
    metadata_path=metadata_path,
    epochs=100,
    batch_size=4,
    learning_rate=0.0001,
    progress_callback=on_progress
)

# 5. Stop monitoring
monitor.stop_monitoring("training_123")
```

---

## Best Practices

### 1. Dataset Preparation

**Quality over Quantity:**
- Use high-quality audio files
- Ensure clear speech
- Remove background noise
- Normalize audio levels

**Recommended Dataset:**
- 50+ audio files
- 5+ minutes total duration
- 1-10 seconds per file
- Clear transcripts

### 2. Training Parameters

**Epochs:**
- Start with 50-100 epochs
- Increase if loss not converging
- Monitor for overfitting

**Batch Size:**
- Start with 4
- Increase if GPU memory allows
- Use gradient accumulation for large models

**Learning Rate:**
- Start with 0.0001
- Use learning rate scheduling
- Reduce if loss not decreasing

### 3. Monitoring Training

**Track Metrics:**
- Loss (should decrease)
- Validation loss (check for overfitting)
- Training time per epoch
- GPU memory usage

**Checkpoints:**
- Save checkpoints regularly
- Keep best checkpoint
- Resume from checkpoint if training interrupted

### 4. Data Augmentation

**Enable Augmentation:**
- Increases dataset diversity
- Improves model generalization
- Use moderate augmentation

**Augmentation Types:**
- Gaussian noise (light)
- Time stretch (small range)
- Pitch shift (small range)

### 5. Model Export

**Export Best Model:**
- Export after training completes
- Test exported model
- Keep checkpoints for comparison

---

## Troubleshooting

### Training Not Starting

**Problem:** Training fails to start

**Solutions:**
- Check GPU availability: `torch.cuda.is_available()`
- Verify dataset format
- Check audio file paths
- Verify transcripts match audio files

### Out of Memory

**Problem:** CUDA out of memory error

**Solutions:**
- Reduce batch size
- Use gradient accumulation
- Process smaller datasets
- Use CPU training (slower)

### Loss Not Decreasing

**Problem:** Loss stays high or increases

**Solutions:**
- Reduce learning rate
- Check dataset quality
- Verify transcripts accuracy
- Increase training epochs
- Check for data issues

### Training Too Slow

**Problem:** Training takes too long

**Solutions:**
- Use GPU acceleration
- Increase batch size (if memory allows)
- Reduce dataset size
- Use mixed precision training

### Model Quality Issues

**Problem:** Trained model quality is poor

**Solutions:**
- Increase training epochs
- Improve dataset quality
- Use more training data
- Tune hyperparameters
- Try different base models

---

## Complete Example

```python
import asyncio
from app.core.training import XTTSTrainer

async def train_voice_model():
    # 1. Create trainer
    trainer = XTTSTrainer(
        base_model="tts_models/multilingual/multi-dataset/xtts_v2",
        device="cuda",
        gpu=True,
        output_dir="models/trained"
    )
    
    # 2. Prepare dataset
    audio_files = [
        "dataset/audio1.wav",
        "dataset/audio2.wav",
        "dataset/audio3.wav"
    ]
    transcripts = [
        "This is the first audio file.",
        "This is the second audio file.",
        "This is the third audio file."
    ]
    
    metadata_path = trainer.prepare_dataset(
        audio_files=audio_files,
        transcripts=transcripts
    )
    
    # 3. Initialize model
    if not trainer.initialize_model():
        raise RuntimeError("Failed to initialize model")
    
    # 4. Define progress callback
    def progress_callback(progress):
        epoch = progress.get('epoch', 0)
        loss = progress.get('loss', 0.0)
        print(f"Epoch {epoch}: Loss = {loss:.4f}")
    
    # 5. Train
    result = await trainer.train(
        metadata_path=metadata_path,
        epochs=100,
        batch_size=4,
        learning_rate=0.0001,
        progress_callback=progress_callback
    )
    
    # 6. Export model
    trainer.export_model("my_custom_voice")
    
    print(f"Training completed: {result['status']}")
    print(f"Final loss: {result['final_loss']:.4f}")

# Run training
asyncio.run(train_voice_model())
```

---

**Last Updated:** 2025-01-28

