"""
Integration tests for FREE_LIBRARIES_INTEGRATION libraries.
Tests all libraries integrated in the FREE_LIBRARIES_INTEGRATION phase.
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestTestingFramework:
    """Tests for testing framework libraries (pytest, pytest-cov, pytest-asyncio)."""

    def test_pytest_import(self):
        """Test that pytest can be imported."""
        import pytest

        assert pytest is not None
        assert hasattr(pytest, "fixture")
        assert hasattr(pytest, "mark")

    def test_pytest_cov_import(self):
        """Test that pytest-cov can be imported."""
        try:
            import pytest_cov

            assert pytest_cov is not None
        except ImportError:
            pytest.skip("pytest-cov not installed")

    def test_pytest_asyncio_import(self):
        """Test that pytest-asyncio can be imported."""
        try:
            import pytest_asyncio

            assert pytest_asyncio is not None
        except ImportError:
            pytest.skip("pytest-asyncio not installed")

    @pytest.mark.asyncio
    async def test_async_test_support(self):
        """Test that async tests work with pytest-asyncio."""
        import asyncio

        await asyncio.sleep(0.01)
        assert True


class TestConfigurationLibraries:
    """Tests for configuration and validation libraries."""

    def test_pyyaml_import(self):
        """Test that pyyaml can be imported."""
        try:
            import yaml

            assert yaml is not None
            # Test basic YAML parsing
            data = yaml.safe_load("test: value")
            assert data == {"test": "value"}
        except ImportError:
            pytest.skip("pyyaml not installed")

    def test_toml_import(self):
        """Test that toml can be imported."""
        try:
            import toml

            assert toml is not None
            # Test basic TOML parsing
            data = toml.loads("test = 'value'")
            assert data == {"test": "value"}
        except ImportError:
            pytest.skip("toml not installed")

    def test_pydantic_import(self):
        """Test that pydantic can be imported."""
        try:
            from pydantic import BaseModel

            assert BaseModel is not None

            # Test basic model creation
            class TestModel(BaseModel):
                name: str

            model = TestModel(name="test")
            assert model.name == "test"
        except ImportError:
            pytest.skip("pydantic not installed")

    def test_cerberus_import(self):
        """Test that cerberus can be imported."""
        try:
            from cerberus import Validator

            assert Validator is not None
            # Test basic validation
            schema = {"name": {"type": "string"}}
            v = Validator(schema)
            assert v.validate({"name": "test"})
        except ImportError:
            pytest.skip("cerberus not installed")


class TestNLPLibraries:
    """Tests for Natural Language Processing libraries."""

    def test_nltk_import(self):
        """Test that nltk can be imported."""
        try:
            import nltk

            assert nltk is not None
        except ImportError:
            pytest.skip("nltk not installed")

    def test_textblob_import(self):
        """Test that textblob can be imported."""
        try:
            from textblob import TextBlob

            assert TextBlob is not None
            # Test basic text processing
            blob = TextBlob("Hello world")
            assert len(blob.words) == 2
        except ImportError:
            pytest.skip("textblob not installed")


class TestTTSUtilities:
    """Tests for Text-to-Speech utility libraries."""

    def test_gtts_import(self):
        """Test that gTTS can be imported."""
        try:
            from gtts import gTTS

            assert gTTS is not None
        except ImportError:
            pytest.skip("gTTS not installed")

    def test_pyttsx3_import(self):
        """Test that pyttsx3 can be imported."""
        try:
            import pyttsx3

            assert pyttsx3 is not None
        except ImportError:
            pytest.skip("pyttsx3 not installed")


class TestUtilityLibraries:
    """Tests for utility and helper libraries."""

    def test_tqdm_import(self):
        """Test that tqdm can be imported."""
        try:
            from tqdm import tqdm

            assert tqdm is not None
            # Test basic progress bar
            result = list(tqdm(range(5), desc="test", disable=True))
            assert len(result) == 5
        except ImportError:
            pytest.skip("tqdm not installed")

    def test_cython_import(self):
        """Test that cython can be imported."""
        try:
            import Cython

            assert Cython is not None
        except ImportError:
            pytest.skip("cython not installed")


class TestQualityMetrics:
    """Tests for additional quality metric libraries."""

    def test_warpq_import(self):
        """Test that warpq can be imported (if available)."""
        try:
            import warpq

            assert warpq is not None
        except ImportError:
            pytest.skip("warpq not installed or not available")

    def test_nlpaug_import(self):
        """Test that nlpaug can be imported."""
        try:
            import nlpaug

            assert nlpaug is not None
        except ImportError:
            pytest.skip("nlpaug not installed")


class TestNewlyIntegratedLibraries:
    """Tests for newly integrated FREE_LIBRARIES_INTEGRATION libraries."""

    def test_soxr_import(self):
        """Test that soxr can be imported."""
        try:
            import soxr

            assert soxr is not None
        except ImportError:
            pytest.skip("soxr not installed")

    def test_pandas_import(self):
        """Test that pandas can be imported."""
        try:
            import pandas as pd

            assert pd is not None
            # Test basic DataFrame creation
            df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
            assert len(df) == 3
        except ImportError:
            pytest.skip("pandas not installed")

    def test_numba_import(self):
        """Test that numba can be imported."""
        try:
            from numba import jit

            assert jit is not None
        except ImportError:
            pytest.skip("numba not installed")

    def test_joblib_import(self):
        """Test that joblib can be imported."""
        try:
            from joblib import Parallel, delayed

            assert Parallel is not None
            assert delayed is not None
        except ImportError:
            pytest.skip("joblib not installed")

    def test_scikit_learn_import(self):
        """Test that scikit-learn can be imported."""
        try:
            from sklearn.metrics import mean_squared_error
            from sklearn.preprocessing import StandardScaler

            assert mean_squared_error is not None
            assert StandardScaler is not None
        except ImportError:
            pytest.skip("scikit-learn not installed")

    def test_optuna_import(self):
        """Test that optuna can be imported."""
        try:
            import optuna

            assert optuna is not None
        except ImportError:
            pytest.skip("optuna not installed")

    def test_ray_import(self):
        """Test that ray[tune] can be imported."""
        try:
            import ray
            from ray import tune

            assert ray is not None
            assert tune is not None
        except ImportError:
            pytest.skip("ray[tune] not installed")

    def test_hyperopt_import(self):
        """Test that hyperopt can be imported."""
        try:
            from hyperopt import fmin, hp, tpe

            assert fmin is not None
            assert tpe is not None
            assert hp is not None
        except ImportError:
            pytest.skip("hyperopt not installed")

    def test_shap_import(self):
        """Test that shap can be imported."""
        try:
            import shap

            assert shap is not None
        except ImportError:
            pytest.skip("shap not installed")

    def test_lime_import(self):
        """Test that lime can be imported."""
        try:
            import lime

            assert lime is not None
        except ImportError:
            pytest.skip("lime not installed")

    def test_yellowbrick_import(self):
        """Test that yellowbrick can be imported."""
        try:
            import yellowbrick

            assert yellowbrick is not None
        except ImportError:
            pytest.skip("yellowbrick not installed")

    def test_vosk_import(self):
        """Test that vosk can be imported."""
        try:
            from vosk import KaldiRecognizer, Model

            assert Model is not None
            assert KaldiRecognizer is not None
        except ImportError:
            pytest.skip("vosk not installed")

    def test_phonemizer_import(self):
        """Test that phonemizer can be imported."""
        try:
            from phonemizer import phonemize
            from phonemizer.backend import EspeakBackend

            assert phonemize is not None
            assert EspeakBackend is not None
        except ImportError:
            pytest.skip("phonemizer not installed")

    def test_gruut_import(self):
        """Test that gruut can be imported."""
        try:
            import gruut

            assert gruut is not None
        except ImportError:
            pytest.skip("gruut not installed")

    def test_silero_vad_import(self):
        """Test that silero-vad can be imported."""
        try:
            from silero_vad import load_silero_vad

            assert load_silero_vad is not None
        except ImportError:
            pytest.skip("silero-vad not installed")

    def test_pywavelets_import(self):
        """Test that pywavelets can be imported."""
        try:
            import pywt

            assert pywt is not None
        except ImportError:
            pytest.skip("pywavelets not installed")

    def test_mutagen_import(self):
        """Test that mutagen can be imported."""
        try:
            from mutagen import File as MutagenFile

            assert MutagenFile is not None
        except ImportError:
            pytest.skip("mutagen not installed")


class TestLibraryIntegrationInCode:
    """Test that libraries are actually used in codebase."""

    def test_audio_utils_uses_soxr(self):
        """Test that audio_utils.py uses soxr."""
        try:
            from app.core.audio import audio_utils

            assert hasattr(audio_utils, "HAS_SOXR")
        except ImportError:
            pytest.skip("audio_utils module not available")

    def test_audio_utils_uses_silero_vad(self):
        """Test that audio_utils.py uses silero-vad."""
        try:
            from app.core.audio import audio_utils

            assert hasattr(audio_utils, "HAS_SILERO_VAD")
        except ImportError:
            pytest.skip("audio_utils module not available")

    def test_audio_utils_uses_pywavelets(self):
        """Test that audio_utils.py uses pywavelets."""
        try:
            from app.core.audio import audio_utils

            assert hasattr(audio_utils, "HAS_PYWAVELETS")
            assert hasattr(audio_utils, "analyze_audio_wavelets")
        except ImportError:
            pytest.skip("audio_utils module not available")

    def test_audio_utils_uses_mutagen(self):
        """Test that audio_utils.py uses mutagen."""
        try:
            from app.core.audio import audio_utils

            assert hasattr(audio_utils, "HAS_MUTAGEN")
            assert hasattr(audio_utils, "read_audio_metadata")
        except ImportError:
            pytest.skip("audio_utils module not available")

    def test_quality_metrics_uses_pandas(self):
        """Test that quality_metrics.py uses pandas."""
        try:
            from app.core.engines import quality_metrics

            assert hasattr(quality_metrics, "HAS_PANDAS")
            assert hasattr(quality_metrics, "analyze_quality_batch")
        except ImportError:
            pytest.skip("quality_metrics module not available")

    def test_quality_metrics_uses_numba(self):
        """Test that quality_metrics.py uses numba."""
        try:
            from app.core.engines import quality_metrics

            assert hasattr(quality_metrics, "HAS_NUMBA")
            assert hasattr(quality_metrics, "calculate_snr_fast")
        except ImportError:
            pytest.skip("quality_metrics module not available")

    def test_quality_metrics_uses_sklearn(self):
        """Test that quality_metrics.py uses scikit-learn."""
        try:
            from app.core.engines import quality_metrics

            assert hasattr(quality_metrics, "HAS_SKLEARN")
            assert hasattr(quality_metrics, "predict_quality_with_ml")
        except ImportError:
            pytest.skip("quality_metrics module not available")

    def test_batch_uses_joblib(self):
        """Test that batch.py uses joblib."""
        try:
            from backend.api.routes import batch

            assert hasattr(batch, "HAS_JOBLIB")
            assert hasattr(batch, "process_batch_jobs_parallel")
        except ImportError:
            pytest.skip("batch module not available")

    def test_batch_uses_dask(self):
        """Test that batch.py uses dask."""
        try:
            from backend.api.routes import batch

            assert hasattr(batch, "HAS_DASK")
        except ImportError:
            pytest.skip("batch module not available")

    def test_training_uses_optuna(self):
        """Test that xtts_trainer.py uses optuna."""
        try:
            from app.core.training import xtts_trainer

            assert hasattr(xtts_trainer, "HAS_OPTUNA")
            assert hasattr(xtts_trainer.XTTSTrainer, "optimize_hyperparameters")
        except ImportError:
            pytest.skip("xtts_trainer module not available")

    def test_training_uses_ray(self):
        """Test that xtts_trainer.py uses ray."""
        try:
            from app.core.training import xtts_trainer

            assert hasattr(xtts_trainer, "HAS_RAY")
        except ImportError:
            pytest.skip("xtts_trainer module not available")

    def test_training_uses_hyperopt(self):
        """Test that xtts_trainer.py uses hyperopt."""
        try:
            from app.core.training import xtts_trainer

            assert hasattr(xtts_trainer, "HAS_HYPEROPT")
        except ImportError:
            pytest.skip("xtts_trainer module not available")

    def test_analytics_uses_shap(self):
        """Test that analytics.py uses shap."""
        try:
            from backend.api.routes import analytics

            assert hasattr(analytics, "HAS_SHAP")
            assert hasattr(analytics, "explain_quality_prediction")
        except ImportError:
            pytest.skip("analytics module not available")

    def test_analytics_uses_lime(self):
        """Test that analytics.py uses lime."""
        try:
            from backend.api.routes import analytics

            assert hasattr(analytics, "HAS_LIME")
        except ImportError:
            pytest.skip("analytics module not available")

    def test_analytics_uses_yellowbrick(self):
        """Test that analytics.py uses yellowbrick."""
        try:
            from backend.api.routes import analytics

            assert hasattr(analytics, "HAS_YELLOWBRICK")
            assert hasattr(analytics, "visualize_quality_metrics")
        except ImportError:
            pytest.skip("analytics module not available")

    def test_nlp_uses_phonemizer(self):
        """Test that text_processing.py uses phonemizer."""
        try:
            from app.core.nlp import text_processing

            assert hasattr(text_processing, "HAS_PHONEMIZER")
            assert hasattr(text_processing.TextPreprocessor, "phonemize_text")
        except ImportError:
            pytest.skip("text_processing module not available")

    def test_nlp_uses_gruut(self):
        """Test that text_processing.py uses gruut."""
        try:
            from app.core.nlp import text_processing

            assert hasattr(text_processing, "HAS_GRUUT")
        except ImportError:
            pytest.skip("text_processing module not available")

    def test_vosk_engine_exists(self):
        """Test that vosk_engine.py exists and can be imported."""
        try:
            from app.core.engines import vosk_engine

            assert hasattr(vosk_engine, "VoskEngine")
            assert hasattr(vosk_engine, "HAS_VOSK")
        except ImportError:
            pytest.skip("vosk_engine module not available")


@pytest.mark.integration
class TestLibraryIntegration:
    """Integration tests for library usage in actual code."""

    def test_yaml_config_loading(self):
        """Test YAML configuration loading."""
        try:
            import yaml

            config_data = """
            app:
              name: VoiceStudio
              version: 1.0.0
            """
            data = yaml.safe_load(config_data)
            assert data["app"]["name"] == "VoiceStudio"
        except ImportError:
            pytest.skip("pyyaml not installed")

    def test_toml_config_loading(self):
        """Test TOML configuration loading."""
        try:
            import toml

            config_data = """
            [app]
            name = "VoiceStudio"
            version = "1.0.0"
            """
            data = toml.loads(config_data)
            assert data["app"]["name"] == "VoiceStudio"
        except ImportError:
            pytest.skip("toml not installed")

    def test_pydantic_validation(self):
        """Test Pydantic model validation."""
        try:
            from pydantic import BaseModel, ValidationError

            class ConfigModel(BaseModel):
                name: str
                version: str
                enabled: bool = True

            # Valid data
            config = ConfigModel(name="test", version="1.0")
            assert config.name == "test"
            assert config.enabled is True

            # Invalid data
            with pytest.raises(ValidationError):
                ConfigModel(name="test")  # Missing required field
        except ImportError:
            pytest.skip("pydantic not installed")
