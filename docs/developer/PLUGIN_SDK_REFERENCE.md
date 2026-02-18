# VoiceStudio Plugin SDK Reference

Complete API reference for the VoiceStudio Plugin SDK.

## Installation

```bash
pip install voicestudio-plugin-sdk
```

## Module Overview

```python
from voicestudio_sdk import (
    # Plugin base classes
    Plugin, SynthesisPlugin, TranscriptionPlugin,
    ProcessingPlugin, EnhancementPlugin, AnalysisPlugin,
    
    # Plugin metadata
    PluginMetadata, PluginType, PluginContext,
    
    # Audio handling
    AudioBuffer, AudioFormat,
    
    # Configuration
    PluginConfig, ConfigField, ConfigType,
    
    # Host communication
    HostAPI, HostConnection,
    
    # Testing utilities
    MockHost, PluginTestCase,
    create_test_manifest, create_test_plugin_directory,
    
    # Decorators
    register_plugin,
)
```

---

## Plugin Classes

### Plugin (Base Class)

Abstract base class for all VoiceStudio plugins.

```python
from voicestudio_sdk import Plugin, PluginContext

class Plugin(ABC):
    """Abstract base class for VoiceStudio plugins."""
    
    async def initialize(self, ctx: PluginContext) -> None:
        """
        Initialize the plugin.
        
        Called once when the plugin is first loaded.
        
        Args:
            ctx: Plugin context with metadata, config, and host API.
        """
        pass
    
    async def shutdown(self) -> None:
        """
        Shutdown the plugin.
        
        Called when the plugin is being unloaded. Use for cleanup.
        """
        pass
    
    def get_config_schema(self) -> Optional[PluginConfig]:
        """
        Return the plugin's configuration schema.
        
        Returns:
            PluginConfig instance or None if no config needed.
        """
        return None
    
    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        pass
    
    @property
    def is_initialized(self) -> bool:
        """Check if plugin is initialized."""
        pass
```

### SynthesisPlugin

Base class for text-to-speech plugins.

```python
from voicestudio_sdk import SynthesisPlugin, AudioBuffer

class SynthesisPlugin(Plugin):
    """Abstract base for synthesis (TTS) plugins."""
    
    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice: str = "default",
        **options
    ) -> AudioBuffer:
        """
        Synthesize speech from text.
        
        Args:
            text: Input text to synthesize.
            voice: Voice identifier to use.
            **options: Additional synthesis options.
        
        Returns:
            AudioBuffer containing generated speech.
        """
        pass
    
    @abstractmethod
    async def get_voices(self) -> List[str]:
        """
        Get list of available voices.
        
        Returns:
            List of voice identifiers.
        """
        pass
    
    async def get_voice_info(self, voice: str) -> Dict[str, Any]:
        """
        Get detailed info about a voice.
        
        Args:
            voice: Voice identifier.
        
        Returns:
            Dictionary with voice metadata.
        """
        return {"id": voice, "name": voice}
```

### TranscriptionPlugin

Base class for speech-to-text plugins.

```python
from voicestudio_sdk import TranscriptionPlugin, AudioBuffer

class TranscriptionPlugin(Plugin):
    """Abstract base for transcription (STT) plugins."""
    
    @abstractmethod
    async def transcribe(
        self,
        audio: AudioBuffer,
        language: str = "en",
        **options
    ) -> str:
        """
        Transcribe audio to text.
        
        Args:
            audio: Audio to transcribe.
            language: Language code (e.g., "en", "es", "fr").
            **options: Additional transcription options.
        
        Returns:
            Transcribed text.
        """
        pass
    
    @abstractmethod
    async def get_languages(self) -> List[str]:
        """
        Get list of supported languages.
        
        Returns:
            List of language codes.
        """
        pass
    
    async def transcribe_with_timestamps(
        self,
        audio: AudioBuffer,
        language: str = "en",
        **options
    ) -> List[Dict[str, Any]]:
        """
        Transcribe with word-level timestamps.
        
        Returns:
            List of {"word": str, "start": float, "end": float}.
        """
        raise NotImplementedError("Timestamps not supported")
```

### ProcessingPlugin

Base class for audio processing/transformation plugins.

```python
from voicestudio_sdk import ProcessingPlugin, AudioBuffer

class ProcessingPlugin(Plugin):
    """Abstract base for audio processing plugins."""
    
    @abstractmethod
    async def process(
        self,
        audio: AudioBuffer,
        **options
    ) -> AudioBuffer:
        """
        Process audio.
        
        Args:
            audio: Input audio to process.
            **options: Processing options.
        
        Returns:
            Processed AudioBuffer.
        """
        pass
```

### EnhancementPlugin

Base class for audio enhancement plugins.

```python
from voicestudio_sdk import EnhancementPlugin, AudioBuffer

class EnhancementPlugin(Plugin):
    """Abstract base for audio enhancement plugins."""
    
    @abstractmethod
    async def enhance(
        self,
        audio: AudioBuffer,
        **options
    ) -> AudioBuffer:
        """
        Enhance audio quality.
        
        Args:
            audio: Input audio to enhance.
            **options: Enhancement options.
        
        Returns:
            Enhanced AudioBuffer.
        """
        pass
```

### AnalysisPlugin

Base class for audio analysis plugins.

```python
from voicestudio_sdk import AnalysisPlugin, AudioBuffer

class AnalysisPlugin(Plugin):
    """Abstract base for audio analysis plugins."""
    
    @abstractmethod
    async def analyze(
        self,
        audio: AudioBuffer,
        **options
    ) -> Dict[str, Any]:
        """
        Analyze audio.
        
        Args:
            audio: Audio to analyze.
            **options: Analysis options.
        
        Returns:
            Analysis results dictionary.
        """
        pass
```

---

## Data Classes

### PluginMetadata

```python
@dataclass
class PluginMetadata:
    """Plugin metadata extracted from manifest."""
    
    id: str                           # Unique plugin identifier
    name: str                         # Human-readable name
    version: str                      # Semantic version
    author: str = ""                  # Author name
    description: str = ""             # Brief description
    plugin_type: PluginType = PluginType.UTILITY
    license: str = ""                 # License identifier
    homepage: str = ""                # Plugin homepage URL
    repository: str = ""              # Source repository URL
    min_voicestudio_version: str = "" # Minimum required version
    capabilities: List[str] = []      # Supported capabilities
    permissions: List[str] = []       # Required permissions
    
    @classmethod
    def from_manifest(cls, manifest: Dict[str, Any]) -> "PluginMetadata":
        """Create metadata from manifest dictionary."""
        pass
```

### PluginContext

```python
@dataclass
class PluginContext:
    """Context provided to plugin operations."""
    
    plugin_id: str = ""               # Plugin identifier
    plugin_path: str = ""             # Path to plugin directory
    config: Dict[str, Any] = {}       # User configuration
    host_api: Optional[Any] = None    # Host API reference
    metadata: Optional[PluginMetadata] = None
    session_id: str = ""              # Current session ID
    workspace_path: Optional[str] = None
    
    @property
    def host(self) -> HostAPI:
        """Get host API for VoiceStudio communication."""
        pass
    
    def get_config(self, key: str, default: T = None) -> T:
        """Get configuration value with default."""
        pass
    
    def require_config(self, key: str) -> Any:
        """Get required config value (raises if missing)."""
        pass
```

### PluginType

```python
class PluginType(str, Enum):
    """Plugin type enumeration."""
    
    SYNTHESIS = "synthesis"           # Text-to-speech
    TRANSCRIPTION = "transcription"   # Speech-to-text
    PROCESSING = "processing"         # Audio transformation
    ENHANCEMENT = "enhancement"       # Audio quality improvement
    ANALYSIS = "analysis"             # Audio analysis
    UTILITY = "utility"               # General utility
```

---

## Audio Module

### AudioBuffer

```python
@dataclass
class AudioBuffer:
    """Container for audio data."""
    
    data: bytes                       # Raw audio data
    format: AudioFormat = AudioFormat.WAV
    sample_rate: int = 44100
    channels: int = 1
    bit_depth: int = 16
    
    @property
    def duration(self) -> float:
        """Get duration in seconds."""
        pass
    
    @classmethod
    def from_file(cls, path: str) -> "AudioBuffer":
        """Load audio from file."""
        pass
    
    @classmethod
    def from_file_data(cls, data: bytes) -> "AudioBuffer":
        """Create from raw file data (auto-detect format)."""
        pass
    
    @classmethod
    def from_raw_samples(
        cls,
        samples: bytes,
        sample_rate: int,
        channels: int = 1,
        bit_depth: int = 16
    ) -> "AudioBuffer":
        """Create from raw PCM samples."""
        pass
    
    def to_file(self, path: str) -> None:
        """Save audio to file."""
        pass
    
    def save(self, path: str) -> None:
        """Save audio to file (alias for to_file)."""
        pass
    
    def as_raw_samples(self) -> bytes:
        """Get raw PCM sample data."""
        pass
    
    def normalize(self, target_db: float = -3.0) -> "AudioBuffer":
        """
        Normalize audio to target dB level.
        
        Args:
            target_db: Target decibel level (default: -3.0).
        
        Returns:
            New normalized AudioBuffer.
        """
        pass
    
    def resample(self, target_rate: int) -> "AudioBuffer":
        """
        Resample audio to target sample rate.
        
        Args:
            target_rate: Target sample rate in Hz.
        
        Returns:
            New resampled AudioBuffer.
        """
        pass
```

### AudioFormat

```python
class AudioFormat(str, Enum):
    """Supported audio formats."""
    
    WAV = "wav"                       # Uncompressed WAV
    MP3 = "mp3"                       # MP3 compressed
    OGG = "ogg"                       # Ogg Vorbis
    FLAC = "flac"                     # FLAC lossless
    RAW = "raw"                       # Raw PCM samples
```

---

## Configuration Module

### ConfigField

```python
@dataclass
class ConfigField:
    """Definition of a configuration field."""
    
    name: str                         # Field identifier
    field_type: ConfigType            # Field type
    label: str = ""                   # Display label
    description: str = ""             # Help text
    default: Any = None               # Default value
    required: bool = False            # Whether required
    min_value: Optional[float] = None # Minimum (numeric)
    max_value: Optional[float] = None # Maximum (numeric)
    min_length: Optional[int] = None  # Min length (string)
    max_length: Optional[int] = None  # Max length (string)
    pattern: Optional[str] = None     # Regex pattern (string)
    options: Optional[List[Any]] = None  # Options (select)
    extensions: Optional[List[str]] = None  # File extensions
    validator: Optional[Callable] = None  # Custom validator
    
    def validate(self, value: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate a value against this field.
        
        Returns:
            Tuple of (is_valid, error_message).
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        pass
```

### ConfigType

```python
class ConfigType(str, Enum):
    """Configuration field types."""
    
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    SELECT = "select"
    MULTISELECT = "multiselect"
    FILE = "file"
    FILE_PATH = "file_path"           # Alias for FILE
    DIRECTORY = "directory"
    DIRECTORY_PATH = "directory_path" # Alias for DIRECTORY
    COLOR = "color"
    SLIDER = "slider"
    PASSWORD = "password"
```

### PluginConfig

```python
class PluginConfig:
    """Plugin configuration schema manager."""
    
    def __init__(self) -> None:
        """Create empty configuration."""
        pass
    
    @property
    def fields(self) -> List[ConfigField]:
        """Get all defined fields."""
        pass
    
    def add_field(self, field: ConfigField) -> None:
        """Add a configuration field."""
        pass
    
    def get_field(self, name: str) -> Optional[ConfigField]:
        """Get field by name."""
        pass
    
    def get_defaults(self) -> Dict[str, Any]:
        """Get default values for all fields."""
        pass
    
    def merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user config with defaults."""
        pass
    
    def validate(self, user_config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Validate configuration.
        
        Returns:
            True if all fields valid.
        """
        pass
    
    def validate_with_errors(
        self,
        config: Dict[str, Any]
    ) -> List[str]:
        """
        Validate and return error messages.
        
        Returns:
            List of validation error messages.
        """
        pass
    
    def to_schema(self) -> Dict[str, Any]:
        """
        Generate JSON schema for configuration.
        
        Returns:
            {"fields": [field.to_dict(), ...]}
        """
        pass
```

---

## Host API Module

### HostConnection

```python
@dataclass
class HostConnection:
    """Connection parameters for host communication."""
    
    mode: str = "direct"              # "direct" or "subprocess"
    stdin_fd: Optional[int] = None    # stdin file descriptor
    stdout_fd: Optional[int] = None   # stdout file descriptor
    plugin_id: str = ""               # Plugin identifier
    
    @classmethod
    def from_environment(cls) -> "HostConnection":
        """Create connection from environment variables."""
        pass
```

### HostAPI

```python
class HostAPI:
    """API for plugin-to-host communication."""
    
    def __init__(self, connection: Optional[HostConnection] = None):
        """
        Initialize host API.
        
        Args:
            connection: Connection parameters (auto-detected if None).
        """
        pass
    
    def is_connected(self) -> bool:
        """Check if connected to host."""
        pass
    
    def connect(self) -> None:
        """Establish connection to host."""
        pass
    
    def disconnect(self) -> None:
        """Disconnect from host."""
        pass
    
    # === Logging ===
    
    def log(self, level: str, message: str) -> None:
        """
        Log a message.
        
        Args:
            level: "debug", "info", "warning", "error"
            message: Log message.
        """
        pass
    
    # === Progress ===
    
    def report_progress(
        self,
        progress: float,
        message: str = ""
    ) -> None:
        """
        Report operation progress.
        
        Args:
            progress: Progress 0.0 to 1.0.
            message: Optional status message.
        """
        pass
    
    # === Resources ===
    
    def get_resource(self, path: str) -> Optional[bytes]:
        """
        Get a resource from the host.
        
        Args:
            path: Resource path.
        
        Returns:
            Resource data or None if not found.
        """
        pass
    
    def put_resource(self, path: str, data: bytes) -> None:
        """
        Store a resource on the host.
        
        Args:
            path: Resource path.
            data: Data to store.
        """
        pass
    
    def list_resources(self, prefix: str = "") -> List[str]:
        """
        List available resources.
        
        Args:
            prefix: Optional path prefix filter.
        
        Returns:
            List of resource paths.
        """
        pass
    
    # === User Interaction ===
    
    def show_notification(
        self,
        level: str,
        message: str,
        title: Optional[str] = None
    ) -> None:
        """
        Show a notification to the user.
        
        Args:
            level: "info", "warning", "error", "success"
            message: Notification message.
            title: Optional title.
        """
        pass
    
    async def confirm(self, message: str) -> bool:
        """
        Request user confirmation.
        
        Args:
            message: Confirmation prompt.
        
        Returns:
            True if confirmed.
        """
        pass
    
    # === Settings ===
    
    def get_setting(self, key: str) -> Optional[Any]:
        """Get a plugin setting."""
        pass
    
    def set_setting(self, key: str, value: Any) -> None:
        """Set a plugin setting."""
        pass
    
    # === Events ===
    
    def on(self, event: str, handler: Callable) -> None:
        """Register event handler."""
        pass
    
    def off(self, event: str, handler: Optional[Callable] = None) -> None:
        """Remove event handler."""
        pass
    
    def emit(self, event: str, data: Any = None) -> None:
        """Emit an event."""
        pass
    
    # === System Info ===
    
    def get_version(self) -> str:
        """Get VoiceStudio version."""
        pass
    
    def get_capabilities(self) -> List[str]:
        """Get host capabilities."""
        pass
```

---

## Testing Module

### MockHost

```python
class MockHost:
    """Mock host API for testing."""
    
    def __init__(self):
        """Initialize mock host."""
        pass
    
    # Recording access
    @property
    def logs(self) -> List[LogEntry]:
        """Get recorded log entries."""
        pass
    
    @property
    def progress_reports(self) -> List[ProgressEntry]:
        """Get recorded progress reports."""
        pass
    
    @property
    def notifications(self) -> List[Dict]:
        """Get recorded notifications."""
        pass
    
    # Filtering
    def get_logs(
        self,
        level: Optional[str] = None
    ) -> List[LogEntry]:
        """Get logs filtered by level."""
        pass
    
    def has_log(
        self,
        level: str,
        message_contains: str
    ) -> bool:
        """Check if a matching log exists."""
        pass
    
    # Configuration
    def set_resource(self, path: str, data: bytes) -> None:
        """Pre-configure a resource."""
        pass
    
    def set_setting(self, key: str, value: Any) -> None:
        """Pre-configure a setting."""
        pass
    
    def set_capability(self, capability: str, enabled: bool) -> None:
        """Configure capability availability."""
        pass
    
    def set_confirm_response(self, response: bool) -> None:
        """Configure confirm() return value."""
        pass
    
    def set_version(self, version: str) -> None:
        """Configure version string."""
        pass
    
    # Reset
    def clear(self) -> None:
        """Clear all recordings."""
        pass
```

### PluginTestCase

```python
class PluginTestCase:
    """Base class for plugin tests."""
    
    plugin_class: Type[Plugin]        # Override in subclass
    plugin: Plugin                    # Initialized plugin instance
    host: MockHost                    # Mock host instance
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        pass
    
    def tearDown(self) -> None:
        """Clean up after test."""
        pass
    
    def create_context(
        self,
        config: Optional[Dict] = None,
        host_api: Optional[MockHost] = None
    ) -> PluginContext:
        """Create a plugin context for testing."""
        pass
    
    def create_test_audio(
        self,
        duration: float = 1.0,
        frequency: float = 440.0,
        sample_rate: int = 44100
    ) -> AudioBuffer:
        """Generate test audio (sine wave)."""
        pass
    
    def create_temp_file(
        self,
        content: bytes = b"",
        suffix: str = ""
    ) -> str:
        """Create a temporary file."""
        pass
    
    def create_temp_dir(self) -> str:
        """Create a temporary directory."""
        pass
    
    def assert_valid_audio(
        self,
        audio: AudioBuffer,
        min_duration: float = 0.0,
        max_duration: Optional[float] = None
    ) -> None:
        """Assert audio buffer is valid."""
        pass
```

### Helper Functions

```python
def create_test_manifest(
    plugin_id: str = "com.test.plugin",
    name: str = "Test Plugin",
    version: str = "1.0.0",
    plugin_type: str = "utility",
    **kwargs
) -> Dict[str, Any]:
    """
    Create a test plugin manifest.
    
    Args:
        plugin_id: Plugin identifier.
        name: Plugin name.
        version: Version string.
        plugin_type: Plugin type.
        **kwargs: Additional manifest fields.
    
    Returns:
        Manifest dictionary.
    """
    pass

def create_test_plugin_directory(
    base_dir: str,
    plugin_id: str = "com.test.plugin",
    create_module: bool = True,
    **manifest_kwargs
) -> str:
    """
    Create a complete test plugin directory.
    
    Args:
        base_dir: Parent directory.
        plugin_id: Plugin identifier.
        create_module: Whether to create Python module.
        **manifest_kwargs: Additional manifest fields.
    
    Returns:
        Path to plugin directory.
    """
    pass
```

---

## Decorators

### @register_plugin

```python
def register_plugin(plugin_id: str):
    """
    Decorator to register a plugin class.
    
    Sets the `_plugin_id` attribute on the class and registers
    it in the global plugin registry.
    
    Args:
        plugin_id: Unique plugin identifier.
    
    Example:
        @register_plugin("com.example.my-plugin")
        class MyPlugin(Plugin):
            pass
    """
    pass
```

---

## Error Handling

### Common Exceptions

| Exception | When Raised |
|-----------|-------------|
| `ValueError` | Invalid argument values |
| `RuntimeError` | Operation not allowed in current state |
| `FileNotFoundError` | Required file/resource missing |
| `NotImplementedError` | Optional method not implemented |
| `PermissionError` | Insufficient permissions |

### Best Practices

```python
async def synthesize(self, text: str, **options) -> AudioBuffer:
    # Validate inputs
    if not text:
        raise ValueError("Text cannot be empty")
    
    if len(text) > 10000:
        raise ValueError("Text exceeds maximum length")
    
    try:
        result = await self._generate(text)
    except ModelNotLoadedError:
        raise RuntimeError("Model not initialized - call initialize() first")
    except ExternalServiceError as e:
        self.host.log("error", f"Service error: {e}")
        raise RuntimeError(f"Synthesis failed: {e}") from e
    
    return result
```

---

## Version History

| Version | Changes |
|---------|---------|
| 1.0.0 | Initial release with core plugin types |
| 1.1.0 | Added ConfigType.PASSWORD, FILE alias |
| 1.2.0 | Added PluginContext.plugin_path field |
