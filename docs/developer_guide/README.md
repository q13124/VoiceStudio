# VoiceStudio Ultimate - Developer Guide

## 🛠️ Plugin Development

VoiceStudio Ultimate features a comprehensive plugin system that allows developers to extend functionality with custom voice adapters, DSP filters, exporters, and analyzers.

## 📋 Plugin Types

### Voice Adapter Plugins
Custom voice cloning engines that integrate with the routing system.

### DSP Filter Plugins
Real-time audio processing filters for the DSP chain.

### Exporter Plugins
Audio format exporters for different output formats.

### Analyzer Plugins
Audio analysis tools for quality assessment and processing.

## 🔧 Plugin Development Setup

### Prerequisites
- Python 3.10+
- VoiceStudio Ultimate installed
- Plugin development dependencies

### Installation
```bash
pip install -e .[dev,plugins]
```

### Plugin Structure
```
plugins/
├── my_plugin/
│   ├── __init__.py
│   ├── plugin.py
│   ├── config.json
│   └── README.md
```

## 🎙️ Voice Adapter Plugin

### Basic Structure

```python
# plugins/my_voice_adapter/plugin.py
from voicestudio.plugins import VoiceAdapterPlugin
from voicestudio.common.errors import VoiceStudioError

class MyVoiceAdapter(VoiceAdapterPlugin):
    def __init__(self, config):
        super().__init__(config)
        self.model = None
        
    def initialize(self):
        """Initialize the voice adapter"""
        try:
            # Load your model
            self.model = load_my_model(self.config['model_path'])
            return True
        except Exception as e:
            raise VoiceStudioError(f"Failed to initialize: {e}")
    
    def clone_voice(self, text, reference_audio, output_path, options=None):
        """Clone voice using your custom engine"""
        try:
            # Your voice cloning logic
            result = self.model.synthesize(
                text=text,
                reference_audio=reference_audio,
                output_path=output_path,
                **options or {}
            )
            return {
                'success': True,
                'output_path': output_path,
                'duration': result.duration,
                'quality_score': result.quality_score
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_capabilities(self):
        """Return plugin capabilities"""
        return {
            'languages': ['en', 'es', 'fr'],
            'quality': 'high',
            'latency': 'normal',
            'features': ['prosody_control', 'emotion_synthesis']
        }
```

### Configuration

```json
{
  "name": "My Voice Adapter",
  "version": "1.0.0",
  "type": "voice-adapter",
  "config": {
    "model_path": "/path/to/model",
    "device": "cuda",
    "batch_size": 1
  }
}
```

## 🎛️ DSP Filter Plugin

### Basic Structure

```python
# plugins/my_dsp_filter/plugin.py
from voicestudio.plugins import DSPFilterPlugin
import numpy as np

class MyDSPFilter(DSPFilterPlugin):
    def __init__(self, config):
        super().__init__(config)
        self.threshold = config.get('threshold', -20.0)
        
    def process_audio(self, audio_data, sample_rate, options=None):
        """Process audio chunk"""
        try:
            # Your DSP processing logic
            processed = self.apply_filter(audio_data, sample_rate)
            return {
                'success': True,
                'audio_data': processed,
                'latency_ms': self.calculate_latency()
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def apply_filter(self, audio_data, sample_rate):
        """Apply your custom filter"""
        # Example: Simple high-pass filter
        cutoff_freq = self.config.get('cutoff_freq', 80.0)
        nyquist = sample_rate / 2
        normalized_cutoff = cutoff_freq / nyquist
        
        # Apply filter (simplified example)
        filtered = audio_data  # Your actual filtering logic
        return filtered
    
    def get_latency_ms(self):
        """Return processing latency in milliseconds"""
        return 5.0  # Your actual latency calculation
```

## 📤 Exporter Plugin

### Basic Structure

```python
# plugins/my_exporter/plugin.py
from voicestudio.plugins import ExporterPlugin
import subprocess

class MyExporter(ExporterPlugin):
    def __init__(self, config):
        super().__init__(config)
        self.format = config.get('format', 'ogg')
        
    def export_audio(self, input_path, output_path, options=None):
        """Export audio to custom format"""
        try:
            # Your export logic
            if self.format == 'ogg':
                self.export_to_ogg(input_path, output_path, options)
            elif self.format == 'mp3':
                self.export_to_mp3(input_path, output_path, options)
            
            return {
                'success': True,
                'output_path': output_path,
                'file_size': os.path.getsize(output_path)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def export_to_ogg(self, input_path, output_path, options):
        """Export to OGG format"""
        quality = options.get('quality', 5) if options else 5
        subprocess.run([
            'ffmpeg', '-y', '-i', input_path,
            '-c:a', 'libvorbis', '-q:a', str(quality),
            output_path
        ], check=True)
```

## 🔍 Analyzer Plugin

### Basic Structure

```python
# plugins/my_analyzer/plugin.py
from voicestudio.plugins import AnalyzerPlugin
import librosa

class MyAnalyzer(AnalyzerPlugin):
    def __init__(self, config):
        super().__init__(config)
        
    def analyze_audio(self, audio_path, options=None):
        """Analyze audio quality and characteristics"""
        try:
            # Load audio
            audio, sr = librosa.load(audio_path)
            
            # Your analysis logic
            analysis = {
                'duration': len(audio) / sr,
                'sample_rate': sr,
                'rms_energy': np.sqrt(np.mean(audio**2)),
                'spectral_centroid': librosa.feature.spectral_centroid(y=audio, sr=sr).mean(),
                'zero_crossing_rate': librosa.feature.zero_crossing_rate(audio).mean(),
                'quality_score': self.calculate_quality_score(audio, sr)
            }
            
            return {
                'success': True,
                'analysis': analysis
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def calculate_quality_score(self, audio, sr):
        """Calculate audio quality score"""
        # Your quality assessment logic
        return 0.95  # Example score
```

## 🔌 Plugin Registration

### Registry Integration

```python
# plugins/my_plugin/__init__.py
from .plugin import MyPlugin

def register_plugin():
    """Register plugin with VoiceStudio"""
    return {
        'name': 'My Plugin',
        'version': '1.0.0',
        'type': 'dsp-filter',
        'class': MyPlugin,
        'config_schema': {
            'type': 'object',
            'properties': {
                'threshold': {'type': 'number', 'default': -20.0},
                'cutoff_freq': {'type': 'number', 'default': 80.0}
            }
        }
    }
```

### Hot Reload Support

```python
# Enable hot reload for development
import voicestudio.plugins.hot_reload as hot_reload

hot_reload.enable_hot_reload('plugins/my_plugin')
```

## 🧪 Testing Plugins

### Unit Testing

```python
# tests/test_my_plugin.py
import pytest
from plugins.my_plugin import MyPlugin

def test_plugin_initialization():
    config = {'threshold': -20.0}
    plugin = MyPlugin(config)
    assert plugin.threshold == -20.0

def test_audio_processing():
    config = {'threshold': -20.0}
    plugin = MyPlugin(config)
    
    # Test audio data
    audio_data = np.random.randn(1024)
    result = plugin.process_audio(audio_data, 22050)
    
    assert result['success'] == True
    assert 'audio_data' in result
```

### Integration Testing

```python
# tests/test_plugin_integration.py
import pytest
from voicestudio import VoiceStudioClient

def test_plugin_integration():
    client = VoiceStudioClient()
    
    # Test plugin loading
    plugins = client.list_plugins()
    assert 'my_plugin' in [p['name'] for p in plugins]
    
    # Test plugin functionality
    result = client.process_audio_with_plugin(
        'my_plugin',
        audio_data,
        options={'threshold': -20.0}
    )
    assert result['success'] == True
```

## 📦 Plugin Packaging

### Package Structure

```
my_plugin/
├── setup.py
├── pyproject.toml
├── README.md
├── LICENSE
├── my_plugin/
│   ├── __init__.py
│   ├── plugin.py
│   └── config.json
└── tests/
    ├── test_plugin.py
    └── test_integration.py
```

### Setup Configuration

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="voicestudio-my-plugin",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "voicestudio>=1.0.0",
        "numpy>=1.21.0",
        "librosa>=0.9.0"
    ],
    entry_points={
        "voicestudio.plugins": [
            "my_plugin = my_plugin:register_plugin"
        ]
    }
)
```

## 🚀 Deployment

### Plugin Installation

```bash
# Install plugin
pip install my_plugin/

# Register with VoiceStudio
python tools/plugin_manager.py install my_plugin

# Enable plugin
python tools/plugin_manager.py enable my_plugin
```

### Plugin Management

```bash
# List plugins
python tools/plugin_manager.py list

# Disable plugin
python tools/plugin_manager.py disable my_plugin

# Uninstall plugin
python tools/plugin_manager.py uninstall my_plugin
```

## 📚 Best Practices

### Performance Optimization
- Use efficient algorithms for real-time processing
- Implement proper error handling and recovery
- Optimize memory usage for large audio files
- Use appropriate data types (float32 vs float64)

### Code Quality
- Follow PEP 8 style guidelines
- Write comprehensive unit tests
- Document all public methods
- Use type hints for better IDE support

### Security Considerations
- Validate all input parameters
- Sanitize file paths and URLs
- Implement proper authentication for sensitive operations
- Follow secure coding practices

## 🤝 Contributing

### Submitting Plugins
1. Fork the VoiceStudio repository
2. Create a feature branch for your plugin
3. Implement your plugin following the guidelines
4. Write comprehensive tests
5. Submit a pull request

### Plugin Review Process
- Code quality review
- Security assessment
- Performance testing
- Documentation review
- Integration testing

---

**Need Help?** Contact the development team at dev@voicestudio.com
