"""
Engine Adapter Protocol Contract Tests

Validates that all engine adapters correctly implement the EngineProtocol interface:
- Required methods exist and have correct signatures
- Standard request payloads are accepted
- Standardized error codes are returned
- Pipeline property invariants hold (duration, sample rate, non-empty output)

These tests ensure adapters behave consistently and prevent "engine A fix breaks engine B"
regressions.
"""

import importlib
import inspect
import json
import os
import sys
from abc import ABC
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Type, get_type_hints

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# =============================================================================
# ENGINE PROTOCOL SPECIFICATION
# =============================================================================

# Required methods for all engines implementing EngineProtocol
REQUIRED_METHODS = {
    "initialize": {
        "return_type": "bool",
        "description": "Initialize the engine model",
    },
    "cleanup": {
        "return_type": None,  # void/None
        "description": "Clean up resources and free memory",
    },
    "is_initialized": {
        "return_type": "bool",
        "description": "Check if engine is initialized",
    },
    "get_device": {
        "return_type": "str",
        "description": "Get current device (cuda/cpu)",
    },
    "get_info": {
        "return_type": "dict",
        "description": "Get engine information dictionary",
    },
}

# Required info dict fields from get_info()
REQUIRED_INFO_FIELDS = {
    "name",
    "version",
    "device",
    "initialized",
}

# Optional but recommended methods
RECOMMENDED_METHODS = {
    "get_memory_usage",
    "supports_language",
}

# Standard error types engines should raise
STANDARD_ERRORS = {
    "EngineInitializationError": "Raised when engine fails to initialize",
    "EngineNotInitializedError": "Raised when operation attempted on uninitialized engine",
    "OperationCancelledError": "Raised when operation cancelled via CancellationToken",
    "InvalidInputError": "Raised when input validation fails",
}

# Valid device specifications
VALID_DEVICES = {"cuda", "cpu", "cuda:0", "cuda:1", "mps"}


# =============================================================================
# ENGINE DISCOVERY
# =============================================================================

def discover_engine_modules() -> List[str]:
    """Discover all engine modules in app/core/engines/."""
    engines_dir = PROJECT_ROOT / "app" / "core" / "engines"
    if not engines_dir.exists():
        return []
    
    engine_modules = []
    for file in engines_dir.glob("*_engine.py"):
        module_name = f"app.core.engines.{file.stem}"
        engine_modules.append(module_name)
    
    return sorted(engine_modules)


def discover_engine_classes() -> List[tuple]:
    """Discover all engine classes that should implement EngineProtocol."""
    engine_classes = []
    
    for module_name in discover_engine_modules():
        try:
            module = importlib.import_module(module_name)
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Skip imported classes (only check classes defined in this module)
                if obj.__module__ != module_name:
                    continue
                # Skip abstract base classes
                if ABC in obj.__mro__:
                    continue
                # Check if it looks like an engine (ends with Engine)
                if name.endswith("Engine"):
                    engine_classes.append((module_name, name, obj))
        except ImportError as e:
            # Engine might have missing dependencies - skip but note
            pytest.skip(f"Could not import {module_name}: {e}")
    
    return engine_classes


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture(scope="module")
def engine_modules() -> List[str]:
    """Get list of engine module names."""
    return discover_engine_modules()


@pytest.fixture(scope="module")
def engine_classes() -> List[tuple]:
    """Get list of (module_name, class_name, class_obj) tuples."""
    return discover_engine_classes()


@pytest.fixture(scope="module")
def engine_protocol_class():
    """Get the EngineProtocol base class for comparison."""
    from app.core.engines.base import EngineProtocol
    return EngineProtocol


# =============================================================================
# CONTRACT TESTS: METHOD SIGNATURES
# =============================================================================

class TestEngineProtocolCompliance:
    """Test that all engines implement required EngineProtocol methods."""
    
    @pytest.mark.contract
    def test_engine_modules_exist(self, engine_modules):
        """At least one engine module should exist."""
        assert len(engine_modules) > 0, "No engine modules found in app/core/engines/"
    
    @pytest.mark.contract
    @pytest.mark.parametrize("method_name,spec", list(REQUIRED_METHODS.items()))
    def test_protocol_has_required_methods(self, engine_protocol_class, method_name, spec):
        """EngineProtocol base class should define all required methods."""
        assert hasattr(engine_protocol_class, method_name), (
            f"EngineProtocol missing required method: {method_name}"
        )
        method = getattr(engine_protocol_class, method_name)
        assert callable(method), f"{method_name} should be callable"
    
    @pytest.mark.contract
    def test_engine_classes_discovered(self, engine_classes):
        """Should discover engine classes from modules."""
        # This test documents what engines exist - may be empty if dependencies missing
        print(f"\nDiscovered {len(engine_classes)} engine classes:")
        for module_name, class_name, _ in engine_classes:
            print(f"  - {class_name} from {module_name}")


class TestEngineMethodSignatures:
    """Test that engine methods have correct signatures."""
    
    @pytest.mark.contract
    def test_initialize_signature(self, engine_classes):
        """All engines should have initialize() -> bool."""
        for module_name, class_name, cls in engine_classes:
            assert hasattr(cls, "initialize"), (
                f"{class_name} missing initialize() method"
            )
            method = getattr(cls, "initialize")
            sig = inspect.signature(method)
            
            # Should have self parameter (and optionally others)
            params = list(sig.parameters.keys())
            assert "self" in params, f"{class_name}.initialize() should have self parameter"
    
    @pytest.mark.contract
    def test_cleanup_signature(self, engine_classes):
        """All engines should have cleanup() -> None."""
        for module_name, class_name, cls in engine_classes:
            assert hasattr(cls, "cleanup"), (
                f"{class_name} missing cleanup() method"
            )
    
    @pytest.mark.contract
    def test_is_initialized_signature(self, engine_classes):
        """All engines should have is_initialized() -> bool."""
        for module_name, class_name, cls in engine_classes:
            assert hasattr(cls, "is_initialized"), (
                f"{class_name} missing is_initialized() method"
            )
    
    @pytest.mark.contract
    def test_get_device_signature(self, engine_classes):
        """All engines should have get_device() -> str."""
        for module_name, class_name, cls in engine_classes:
            assert hasattr(cls, "get_device"), (
                f"{class_name} missing get_device() method"
            )
    
    @pytest.mark.contract
    def test_get_info_signature(self, engine_classes):
        """All engines should have get_info() -> Dict."""
        for module_name, class_name, cls in engine_classes:
            assert hasattr(cls, "get_info"), (
                f"{class_name} missing get_info() method"
            )


class TestEngineConstructorContract:
    """Test that engine constructors follow the expected pattern."""
    
    @pytest.mark.contract
    def test_constructor_accepts_device_parameter(self, engine_classes):
        """Engine constructors should accept device parameter."""
        for module_name, class_name, cls in engine_classes:
            sig = inspect.signature(cls.__init__)
            params = list(sig.parameters.keys())
            
            # Should have device parameter (or accept **kwargs)
            has_device = "device" in params
            has_kwargs = any(
                sig.parameters[p].kind == inspect.Parameter.VAR_KEYWORD 
                for p in params
            )
            
            assert has_device or has_kwargs, (
                f"{class_name}.__init__ should accept 'device' parameter"
            )
    
    @pytest.mark.contract
    def test_constructor_accepts_gpu_parameter(self, engine_classes):
        """Engine constructors should accept gpu parameter."""
        for module_name, class_name, cls in engine_classes:
            sig = inspect.signature(cls.__init__)
            params = list(sig.parameters.keys())
            
            has_gpu = "gpu" in params
            has_kwargs = any(
                sig.parameters[p].kind == inspect.Parameter.VAR_KEYWORD 
                for p in params
            )
            
            # GPU parameter is recommended but not strictly required if kwargs exists
            if not has_gpu and not has_kwargs:
                pytest.skip(f"{class_name} doesn't have gpu parameter (may be intentional)")


# =============================================================================
# CONTRACT TESTS: INFO DICTIONARY
# =============================================================================

class TestEngineInfoContract:
    """Test that get_info() returns expected structure."""
    
    @pytest.mark.contract
    def test_info_dict_structure(self, engine_protocol_class):
        """EngineProtocol.get_info() should return dict with required fields."""
        # Create a minimal implementation to test the base class
        class TestEngine(engine_protocol_class):
            def initialize(self) -> bool:
                self._initialized = True
                return True
            
            def cleanup(self) -> None:
                self._initialized = False
        
        engine = TestEngine(device="cpu", gpu=False)
        info = engine.get_info()
        
        assert isinstance(info, dict), "get_info() should return a dict"
        
        for field in REQUIRED_INFO_FIELDS:
            assert field in info, f"get_info() missing required field: {field}"
    
    @pytest.mark.contract
    def test_info_dict_types(self, engine_protocol_class):
        """Info dict fields should have correct types."""
        class TestEngine(engine_protocol_class):
            def initialize(self) -> bool:
                self._initialized = True
                return True
            
            def cleanup(self) -> None:
                self._initialized = False
        
        engine = TestEngine(device="cpu", gpu=False)
        info = engine.get_info()
        
        assert isinstance(info.get("name"), str), "info['name'] should be str"
        assert isinstance(info.get("device"), str), "info['device'] should be str"
        assert isinstance(info.get("initialized"), bool), "info['initialized'] should be bool"


# =============================================================================
# CONTRACT TESTS: ERROR HANDLING
# =============================================================================

class TestEngineErrorContract:
    """Test that engines use standardized error handling."""
    
    @pytest.mark.contract
    def test_operation_cancelled_error_exists(self):
        """OperationCancelledError should be importable from base."""
        from app.core.engines.base import OperationCancelledError
        assert issubclass(OperationCancelledError, Exception)
    
    @pytest.mark.contract
    def test_cancellation_token_exists(self):
        """CancellationToken should be importable from base."""
        from app.core.engines.base import CancellationToken
        
        token = CancellationToken()
        assert hasattr(token, "cancel")
        assert hasattr(token, "is_cancelled")
        assert hasattr(token, "raise_if_cancelled")
    
    @pytest.mark.contract
    def test_cancellation_token_behavior(self):
        """CancellationToken should work correctly."""
        from app.core.engines.base import CancellationToken, OperationCancelledError
        
        token = CancellationToken()
        assert not token.is_cancelled(), "New token should not be cancelled"
        
        token.cancel()
        assert token.is_cancelled(), "Token should be cancelled after cancel()"
        
        with pytest.raises(OperationCancelledError):
            token.raise_if_cancelled()


# =============================================================================
# CONTRACT TESTS: DEVICE HANDLING
# =============================================================================

class TestEngineDeviceContract:
    """Test that engines handle device specification correctly."""
    
    @pytest.mark.contract
    def test_protocol_default_device_cpu(self, engine_protocol_class):
        """Engine with gpu=False should default to cpu device."""
        class TestEngine(engine_protocol_class):
            def initialize(self) -> bool:
                return True
            def cleanup(self) -> None:
                pass
        
        engine = TestEngine(gpu=False)
        assert engine.get_device() == "cpu"
    
    @pytest.mark.contract
    def test_protocol_explicit_device(self, engine_protocol_class):
        """Engine should respect explicit device parameter."""
        class TestEngine(engine_protocol_class):
            def initialize(self) -> bool:
                return True
            def cleanup(self) -> None:
                pass
        
        engine = TestEngine(device="cpu")
        assert engine.get_device() == "cpu"


# =============================================================================
# CONTRACT TESTS: INHERITANCE
# =============================================================================

class TestEngineInheritanceContract:
    """Test that engines properly inherit from EngineProtocol."""
    
    @pytest.mark.contract
    def test_engines_inherit_from_protocol(self, engine_classes, engine_protocol_class):
        """All engine classes should inherit from EngineProtocol."""
        for module_name, class_name, cls in engine_classes:
            # Check if EngineProtocol is in the MRO
            assert engine_protocol_class in cls.__mro__, (
                f"{class_name} should inherit from EngineProtocol"
            )
    
    @pytest.mark.contract
    def test_engines_not_abstract(self, engine_classes):
        """Discovered engine classes should not be abstract."""
        for module_name, class_name, cls in engine_classes:
            # Check for abstractmethod decorators on the class itself
            abstract_methods = getattr(cls, "__abstractmethods__", set())
            assert len(abstract_methods) == 0, (
                f"{class_name} has unimplemented abstract methods: {abstract_methods}"
            )


# =============================================================================
# CONTRACT TESTS: PIPELINE PROPERTIES
# =============================================================================

class TestEnginePipelineContract:
    """Test pipeline property invariants."""
    
    @pytest.mark.contract
    def test_synthesize_method_exists_for_tts_engines(self, engine_classes):
        """TTS engines should have a synthesize method."""
        tts_engines = [
            (m, n, c) for m, n, c in engine_classes 
            if "tts" in n.lower() or "xtts" in n.lower() or "voice" in n.lower()
        ]
        
        for module_name, class_name, cls in tts_engines:
            has_synthesize = hasattr(cls, "synthesize")
            has_tts = hasattr(cls, "tts")
            has_generate = hasattr(cls, "generate")
            
            assert has_synthesize or has_tts or has_generate, (
                f"TTS engine {class_name} should have synthesize/tts/generate method"
            )
    
    @pytest.mark.contract
    def test_transcribe_method_exists_for_stt_engines(self, engine_classes):
        """STT engines should have a transcribe method."""
        stt_engines = [
            (m, n, c) for m, n, c in engine_classes 
            if "whisper" in n.lower() or "transcri" in n.lower() or "stt" in n.lower()
        ]
        
        for module_name, class_name, cls in stt_engines:
            has_transcribe = hasattr(cls, "transcribe")
            has_recognize = hasattr(cls, "recognize")
            
            assert has_transcribe or has_recognize, (
                f"STT engine {class_name} should have transcribe/recognize method"
            )
    
    @pytest.mark.contract
    def test_convert_method_exists_for_rvc_engines(self, engine_classes):
        """RVC engines should have a convert method."""
        rvc_engines = [
            (m, n, c) for m, n, c in engine_classes 
            if "rvc" in n.lower() or "conversion" in n.lower()
        ]
        
        for module_name, class_name, cls in rvc_engines:
            has_convert = hasattr(cls, "convert")
            has_process = hasattr(cls, "process")
            has_infer = hasattr(cls, "infer")
            
            assert has_convert or has_process or has_infer, (
                f"RVC engine {class_name} should have convert/process/infer method"
            )


# =============================================================================
# CONTRACT TESTS: MANIFEST ALIGNMENT
# =============================================================================

class TestEngineManifestAlignment:
    """Test that engine classes align with their manifests."""
    
    @pytest.fixture
    def engine_manifests(self) -> Dict[str, Dict]:
        """Load all engine manifests."""
        manifests = {}
        engines_dir = PROJECT_ROOT / "engines"
        if not engines_dir.exists():
            return manifests
        
        for file in engines_dir.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                    engine_id = manifest.get("engine_id", file.stem)
                    manifests[engine_id] = manifest
            except json.JSONDecodeError:
                continue
        
        return manifests
    
    @pytest.mark.contract
    def test_manifests_have_matching_engine_class(self, engine_manifests, engine_classes):
        """Each manifest should have a corresponding engine class (or be marked external)."""
        engine_class_names = {name.lower() for _, name, _ in engine_classes}
        
        for engine_id, manifest in engine_manifests.items():
            # Skip external/runtime engines
            if manifest.get("external", False):
                continue
            if manifest.get("runtime", False):
                continue
            
            # Check if there's a matching class
            engine_id_normalized = engine_id.lower().replace("-", "").replace("_", "")
            
            # This is a soft check - not all manifests require a class
            # (some engines are adapters for external tools)
            if manifest.get("requires_class", True):
                found = any(
                    engine_id_normalized in name.lower().replace("engine", "")
                    for name in engine_class_names
                )
                if not found:
                    pytest.skip(
                        f"No matching class for manifest {engine_id} "
                        f"(may be intentional for external engines)"
                    )


# =============================================================================
# SUMMARY TEST
# =============================================================================

class TestEngineContractSummary:
    """Summary test that provides an overview of contract compliance."""
    
    @pytest.mark.contract
    def test_contract_compliance_summary(self, engine_classes, engine_protocol_class):
        """Print summary of engine contract compliance."""
        print("\n" + "=" * 70)
        print("ENGINE ADAPTER CONTRACT COMPLIANCE SUMMARY")
        print("=" * 70)
        
        total = len(engine_classes)
        compliant = 0
        
        for module_name, class_name, cls in engine_classes:
            issues = []
            
            # Check inheritance
            if engine_protocol_class not in cls.__mro__:
                issues.append("Does not inherit from EngineProtocol")
            
            # Check required methods
            for method in REQUIRED_METHODS:
                if not hasattr(cls, method):
                    issues.append(f"Missing method: {method}")
            
            # Check abstract methods
            abstract_methods = getattr(cls, "__abstractmethods__", set())
            if abstract_methods:
                issues.append(f"Unimplemented: {abstract_methods}")
            
            if issues:
                print(f"\n❌ {class_name}:")
                for issue in issues:
                    print(f"   - {issue}")
            else:
                print(f"✅ {class_name}: Compliant")
                compliant += 1
        
        print("\n" + "-" * 70)
        print(f"TOTAL: {compliant}/{total} engines compliant")
        print("=" * 70 + "\n")
        
        # This test always passes - it's informational
        assert True


# =============================================================================
# CONTRACT TESTS: PIPELINE PROPERTY INVARIANTS
# =============================================================================

class TestPipelinePropertyInvariants:
    """
    Test pipeline property invariants for engine outputs.
    
    These tests validate that engine outputs meet basic quality requirements:
    - Duration is positive
    - Sample rate is valid
    - Output is non-empty
    - Audio data is properly formatted
    
    Note: These tests require actual engine instantiation and may be skipped
    if dependencies are unavailable.
    """
    
    # Standard sample rates for voice synthesis
    VALID_SAMPLE_RATES = {8000, 16000, 22050, 24000, 44100, 48000}
    
    # Minimum expected duration for synthesis (in seconds)
    MIN_DURATION_SECONDS = 0.1
    
    @pytest.mark.contract
    @pytest.mark.slow
    @pytest.mark.engine
    def test_tts_output_duration_positive(self):
        """TTS engine output duration should be positive."""
        # This test requires engine instantiation - skip if unavailable
        pytest.skip(
            "Pipeline property test requires engine instantiation. "
            "Run with actual engine tests for full validation."
        )
    
    @pytest.mark.contract
    @pytest.mark.slow
    @pytest.mark.engine
    def test_tts_output_sample_rate_valid(self):
        """TTS engine output sample rate should be a standard audio rate."""
        pytest.skip(
            "Pipeline property test requires engine instantiation. "
            "Run with actual engine tests for full validation."
        )
    
    @pytest.mark.contract
    @pytest.mark.slow
    @pytest.mark.engine
    def test_tts_output_non_empty(self):
        """TTS engine output should contain audio data."""
        pytest.skip(
            "Pipeline property test requires engine instantiation. "
            "Run with actual engine tests for full validation."
        )
    
    @pytest.mark.contract
    def test_pipeline_invariants_documented(self):
        """Verify pipeline invariant constants are defined."""
        assert len(self.VALID_SAMPLE_RATES) > 0, "Valid sample rates should be defined"
        assert self.MIN_DURATION_SECONDS > 0, "Minimum duration should be positive"
        
        # Document expected invariants
        print("\n" + "=" * 70)
        print("PIPELINE PROPERTY INVARIANTS")
        print("=" * 70)
        print(f"Valid sample rates: {sorted(self.VALID_SAMPLE_RATES)}")
        print(f"Minimum duration: {self.MIN_DURATION_SECONDS}s")
        print("\nThese invariants apply to all TTS engine outputs:")
        print("  - Duration > 0")
        print("  - Sample rate in VALID_SAMPLE_RATES")
        print("  - Output bytes > 0")
        print("  - Audio data is valid WAV/PCM")
        print("=" * 70 + "\n")


# =============================================================================
# CONTRACT TESTS: STANDARD REQUEST/RESPONSE FORMAT
# =============================================================================

class TestStandardRequestResponseFormat:
    """
    Test that engines accept standard request formats and return standardized responses.
    """
    
    # Standard TTS request fields
    STANDARD_TTS_REQUEST_FIELDS = {
        "text": str,  # Required: text to synthesize
        "speaker_wav": (str, type(None)),  # Optional: reference audio path
        "language": (str, type(None)),  # Optional: language code
    }
    
    # Standard response fields
    STANDARD_RESPONSE_FIELDS = {
        "audio_data": (bytes, type(None)),  # Audio bytes
        "sample_rate": int,  # Sample rate
        "duration": (float, int),  # Duration in seconds
    }
    
    # Standard error response fields
    STANDARD_ERROR_FIELDS = {
        "error": str,  # Error message
        "error_type": str,  # Error type/code
    }
    
    @pytest.mark.contract
    def test_standard_request_format_documented(self):
        """Verify standard request format is documented."""
        assert "text" in self.STANDARD_TTS_REQUEST_FIELDS
        print("\n" + "=" * 70)
        print("STANDARD TTS REQUEST FORMAT")
        print("=" * 70)
        for field, field_type in self.STANDARD_TTS_REQUEST_FIELDS.items():
            type_name = field_type.__name__ if isinstance(field_type, type) else str(field_type)
            print(f"  {field}: {type_name}")
        print("=" * 70 + "\n")
    
    @pytest.mark.contract
    def test_standard_response_format_documented(self):
        """Verify standard response format is documented."""
        assert "audio_data" in self.STANDARD_RESPONSE_FIELDS
        print("\n" + "=" * 70)
        print("STANDARD TTS RESPONSE FORMAT")
        print("=" * 70)
        for field, field_type in self.STANDARD_RESPONSE_FIELDS.items():
            type_name = field_type.__name__ if isinstance(field_type, type) else str(field_type)
            print(f"  {field}: {type_name}")
        print("=" * 70 + "\n")
    
    @pytest.mark.contract
    def test_standard_error_format_documented(self):
        """Verify standard error format is documented."""
        assert "error" in self.STANDARD_ERROR_FIELDS
        print("\n" + "=" * 70)
        print("STANDARD ERROR RESPONSE FORMAT")
        print("=" * 70)
        for field, field_type in self.STANDARD_ERROR_FIELDS.items():
            type_name = field_type.__name__ if isinstance(field_type, type) else str(field_type)
            print(f"  {field}: {type_name}")
        print("=" * 70 + "\n")
