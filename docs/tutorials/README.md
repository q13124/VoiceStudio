# VoiceStudio Ultimate - Tutorials

## 📚 Step-by-Step Tutorials

Learn VoiceStudio Ultimate through hands-on tutorials covering all major features and use cases.

## 🚀 Getting Started Tutorials

### Tutorial 1: Your First Voice Clone

Learn how to create your first voice clone in 5 minutes.

**Prerequisites:**
- VoiceStudio Ultimate installed
- Reference audio file (WAV format, 3-10 seconds)

**Steps:**

1. **Start VoiceStudio**
   ```bash
   python tools/voicestudio_launcher.py --mode dev
   ```

2. **Prepare Reference Audio**
   - Record or obtain a clear reference audio
   - Ensure it's in WAV format, 22kHz sample rate
   - Keep it between 3-10 seconds for best results

3. **Basic Voice Cloning**
   ```python
   from UltraClone.EngineService.routing.engine_router import EngineRouter
   
   # Initialize router
   router = EngineRouter("config/engines.config.json")
   
   # Choose engine
   engine, chain = router.choose(lang="en")
   
   # Clone voice
   text = "Hello, this is my first voice clone!"
   reference_audio = "reference.wav"
   output_path = "my_first_clone.wav"
   
   result = clone_voice(engine, text, reference_audio, output_path)
   print(f"Success: {result['success']}")
   ```

4. **Test Your Clone**
   - Play the output audio
   - Compare with reference
   - Adjust settings if needed

**Expected Result:** A high-quality voice clone that sounds like your reference speaker.

### Tutorial 2: Advanced Voice Cloning with Options

Learn to use advanced features for professional voice cloning.

**Steps:**

1. **Configure Advanced Options**
   ```python
   options = {
       "engine": "xtts",
       "language": "en",
       "quality": "high",
       "latency": "normal",
       "prosody_control": True,
       "emotion": "neutral"
   }
   ```

2. **Apply Prosody Control**
   ```python
   # Load prosody overrides
   prosody_data = {
       "words": [
           {"word": "Hello", "pitch": 0.2, "speed": 1.0, "energy": 0.8},
           {"word": "world", "pitch": -0.1, "speed": 0.9, "energy": 0.7}
       ]
   }
   
   result = clone_voice_with_prosody(text, reference_audio, prosody_data, options)
   ```

3. **Quality Assessment**
   ```python
   # Analyze quality
   quality_score = analyze_voice_quality(result['output_path'])
   print(f"Quality Score: {quality_score}")
   ```

## 🎛️ Audio Processing Tutorials

### Tutorial 3: Real-time DSP Processing

Learn to use the real-time DSP chain for professional audio processing.

**Steps:**

1. **Initialize DSP Chain**
   ```python
   from voicestudio.dsp import RealtimeDSPChain
   
   dsp_chain = RealtimeDSPChain(
       sample_rate=22050,
       buffer_size=512,
       max_latency_ms=50
   )
   ```

2. **Configure DSP Modules**
   ```python
   dsp_config = {
       "deesser": {
           "enabled": True,
           "threshold": -20.0,
           "ratio": 4.0,
           "frequency": 6000.0
       },
       "eq": {
           "enabled": True,
           "bands": [
               {"freq": 80, "gain": 0, "q": 0.7, "type": "highpass"},
               {"freq": 200, "gain": 2, "q": 1.0, "type": "peak"},
               {"freq": 5000, "gain": 3, "q": 1.0, "type": "peak"}
           ]
       },
       "compressor": {
           "enabled": True,
           "threshold": -18.0,
           "ratio": 3.0,
           "attack": 5.0,
           "release": 50.0
       }
   }
   
   dsp_chain.configure_modules(dsp_config)
   ```

3. **Process Audio**
   ```python
   # Process audio chunk
   processed_audio = dsp_chain.process_audio_chunk(audio_chunk)
   
   # Monitor performance
   stats = dsp_chain.get_performance_stats()
   print(f"Processing time: {stats['avg_processing_time_ms']}ms")
   ```

### Tutorial 4: Alignment Lane Control

Learn to use the Alignment Lane for precise prosody control.

**Steps:**

1. **Load Text for Alignment**
   ```python
   text = "This is a test of the alignment lane control system."
   ```

2. **Create Word Alignment**
   ```python
   alignment_data = {
       "words": [
           {"word": "This", "start": 0.0, "duration": 0.3, "pitch": 0, "speed": 1.0, "energy": 0.8},
           {"word": "is", "start": 0.3, "duration": 0.2, "pitch": 0, "speed": 1.0, "energy": 0.7},
           {"word": "a", "start": 0.5, "duration": 0.1, "pitch": 0, "speed": 1.0, "energy": 0.6},
           {"word": "test", "start": 0.6, "duration": 0.4, "pitch": 0.2, "speed": 0.9, "energy": 0.9},
           # ... continue for all words
       ]
   }
   ```

3. **Apply Alignment**
   ```python
   result = voice_clone_with_alignment(text, reference_audio, alignment_data)
   ```

4. **Fine-tune Prosody**
   - Adjust pitch for emphasis
   - Modify speed for pacing
   - Change energy for dynamics

## 🔧 Advanced Feature Tutorials

### Tutorial 5: Artifact Killer System

Learn to use the artifact killer for automatic quality enhancement.

**Steps:**

1. **Enable Artifact Detection**
   ```python
   artifact_config = {
       "enabled": True,
       "threshold": 0.75,
       "repair_strategy": "denoise_crossfade",
       "heatmap_source": "synthetic_detection"
   }
   ```

2. **Process with Artifact Killer**
   ```python
   result = process_with_artifact_killer(
       audio_path="input.wav",
       config=artifact_config,
       output_path="enhanced.wav"
   )
   ```

3. **Compare Results**
   - Play original audio
   - Play enhanced audio
   - Notice artifact reduction

### Tutorial 6: Watermarking and Policy

Learn to implement content protection and compliance.

**Steps:**

1. **Configure Watermarking**
   ```python
   watermark_config = {
       "enabled": True,
       "policy_key": "commercial_license",
       "metadata": {
           "user_id": "user_123",
           "license": "commercial",
           "timestamp": "2025-01-01T12:00:00Z",
           "content_id": "content_456"
       }
   }
   ```

2. **Apply Watermark**
   ```python
   result = apply_watermark(
       audio_path="voice_clone.wav",
       config=watermark_config,
       output_path="watermarked.wav"
   )
   ```

3. **Verify Watermark**
   ```python
   verification = verify_watermark("watermarked.wav", "commercial_license")
   print(f"Watermark valid: {verification['valid']}")
   ```

## 🔌 Plugin Development Tutorials

### Tutorial 7: Creating a Custom DSP Filter

Learn to create your own DSP filter plugin.

**Steps:**

1. **Create Plugin Structure**
   ```
   plugins/my_custom_filter/
   ├── __init__.py
   ├── plugin.py
   ├── config.json
   └── README.md
   ```

2. **Implement Filter Logic**
   ```python
   # plugins/my_custom_filter/plugin.py
   from voicestudio.plugins import DSPFilterPlugin
   import numpy as np
   
   class MyCustomFilter(DSPFilterPlugin):
       def __init__(self, config):
           super().__init__(config)
           self.strength = config.get('strength', 1.0)
           
       def process_audio(self, audio_data, sample_rate, options=None):
           # Your custom filtering logic
           filtered = self.apply_custom_filter(audio_data)
           return {
               'success': True,
               'audio_data': filtered,
               'latency_ms': 2.0
           }
       
       def apply_custom_filter(self, audio_data):
           # Example: Custom noise reduction
           return audio_data * self.strength
   ```

3. **Register Plugin**
   ```python
   # plugins/my_custom_filter/__init__.py
   from .plugin import MyCustomFilter
   
   def register_plugin():
       return {
           'name': 'My Custom Filter',
           'version': '1.0.0',
           'type': 'dsp-filter',
           'class': MyCustomFilter
       }
   ```

4. **Test Plugin**
   ```python
   # Test your plugin
   plugin = MyCustomFilter({'strength': 0.8})
   result = plugin.process_audio(audio_data, 22050)
   assert result['success'] == True
   ```

## 🎯 Use Case Tutorials

### Tutorial 8: Podcast Production

Learn to use VoiceStudio for professional podcast production.

**Steps:**

1. **Prepare Episode Script**
   - Write your podcast script
   - Mark emphasis and pacing
   - Note special effects needed

2. **Record Reference Audio**
   - Record clear reference samples
   - Use consistent microphone setup
   - Maintain consistent speaking style

3. **Generate Episode Audio**
   ```python
   # Process each segment
   segments = [
       {"text": "Welcome to our podcast...", "reference": "intro.wav"},
       {"text": "Today we're discussing...", "reference": "main.wav"},
       {"text": "Thanks for listening...", "reference": "outro.wav"}
   ]
   
   for segment in segments:
       result = clone_voice(
           text=segment["text"],
           reference_audio=segment["reference"],
           output_path=f"segment_{i}.wav"
       )
   ```

4. **Post-process Audio**
   - Apply DSP chain for consistency
   - Use artifact killer for quality
   - Apply watermarking for protection

### Tutorial 9: Audiobook Creation

Learn to create professional audiobooks with VoiceStudio.

**Steps:**

1. **Prepare Book Content**
   - Format text into chapters
   - Mark character voices
   - Note emotional context

2. **Create Character Voices**
   ```python
   characters = {
       "narrator": {"reference": "narrator.wav", "engine": "xtts"},
       "protagonist": {"reference": "protagonist.wav", "engine": "openvoice"},
       "antagonist": {"reference": "antagonist.wav", "engine": "cosyvoice2"}
   }
   ```

3. **Generate Chapter Audio**
   ```python
   for chapter in chapters:
       for character, dialogue in chapter.dialogues:
           voice_config = characters[character]
           result = clone_voice(
               text=dialogue,
               reference_audio=voice_config["reference"],
               engine=voice_config["engine"],
               output_path=f"chapter_{chapter.number}_{character}.wav"
           )
   ```

4. **Assemble Final Audiobook**
   - Combine character voices
   - Apply consistent DSP processing
   - Export to final format

## 📊 Performance Optimization Tutorials

### Tutorial 10: System Optimization

Learn to optimize VoiceStudio for your hardware.

**Steps:**

1. **Monitor Performance**
   ```python
   from voicestudio.monitoring import PerformanceMonitor
   
   monitor = PerformanceMonitor()
   monitor.start_monitoring()
   
   # Check performance stats
   stats = monitor.get_current_stats()
   print(f"CPU: {stats['cpu_percent']}%")
   print(f"Memory: {stats['memory_percent']}%")
   print(f"GPU: {stats['gpu_percent']}%")
   ```

2. **Optimize Settings**
   ```python
   # Adjust based on hardware
   if stats['cpu_percent'] > 80:
       # Reduce quality settings
       options['quality'] = 'medium'
       options['batch_size'] = 1
   
   if stats['memory_percent'] > 85:
       # Reduce buffer sizes
       options['buffer_size'] = 256
   ```

3. **Test Performance**
   ```python
   # Benchmark different configurations
   configs = [
       {'quality': 'high', 'latency': 'normal'},
       {'quality': 'medium', 'latency': 'low'},
       {'quality': 'low', 'latency': 'ultra'}
   ]
   
   for config in configs:
       start_time = time.time()
       result = clone_voice(text, reference, config)
       duration = time.time() - start_time
       print(f"Config: {config}, Duration: {duration}s")
   ```

## 🎓 Advanced Techniques

### Tutorial 11: Multi-language Voice Cloning

Learn to create voices that can speak multiple languages.

**Steps:**

1. **Prepare Multi-language References**
   - Record reference audio in multiple languages
   - Ensure consistent voice characteristics
   - Use same microphone and environment

2. **Configure Language Routing**
   ```python
   language_config = {
       "en": {"engine": "xtts", "reference": "reference_en.wav"},
       "es": {"engine": "xtts", "reference": "reference_es.wav"},
       "fr": {"engine": "openvoice", "reference": "reference_fr.wav"},
       "zh": {"engine": "cosyvoice2", "reference": "reference_zh.wav"}
   }
   ```

3. **Generate Multi-language Content**
   ```python
   for language, text in multilingual_content.items():
       config = language_config[language]
       result = clone_voice(
           text=text,
           reference_audio=config["reference"],
           engine=config["engine"],
           language=language,
           output_path=f"output_{language}.wav"
       )
   ```

### Tutorial 12: Real-time Voice Conversion

Learn to implement real-time voice conversion for live applications.

**Steps:**

1. **Setup Real-time Processing**
   ```python
   from voicestudio.realtime import RealtimeVoiceConverter
   
   converter = RealtimeVoiceConverter(
       reference_audio="reference.wav",
       target_latency_ms=50,
       buffer_size=512
   )
   ```

2. **Process Live Audio**
   ```python
   # Process audio chunks in real-time
   for audio_chunk in live_audio_stream:
       converted_chunk = converter.process_chunk(audio_chunk)
       output_stream.write(converted_chunk)
   ```

3. **Monitor Performance**
   ```python
   # Ensure real-time performance
   stats = converter.get_performance_stats()
   if stats['avg_latency_ms'] > 50:
       converter.optimize_for_latency()
   ```

---

**Need Help?** Check the [User Guide](user_guide/README.md) or contact support at tutorials@voicestudio.com
