"""
Unit Tests for Validation Optimizer
Tests all optimizations: schema caching (LRU), early validation failures,
batch validation, performance metrics, and validation middleware.
"""

import contextlib
import sys
from pathlib import Path

import pytest
from pydantic import BaseModel, ValidationError

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import modules
try:
    from app.core.validation.optimizer import (
        ValidationOptimizer,
        clear_schema_cache,
        get_cached_schema,
        get_schema_cache_stats,
        get_validation_optimizer,
        optimized_validate,
        validate_batch,
        validate_early,
        validation_middleware,
    )
except ImportError as e:
    pytest.skip(
        f"Could not import validation optimizer modules: {e}", allow_module_level=True
    )


# Test Pydantic models
class TestModel(BaseModel):
    """Test Pydantic model for validation."""

    name: str
    age: int
    email: str = "test@example.com"


class TestModelOptional(BaseModel):
    """Test model with optional fields."""

    name: str
    age: int | None = None


class TestValidationOptimizer:
    """Test ValidationOptimizer class."""

    def test_initialization(self):
        """Test ValidationOptimizer initializes correctly."""
        optimizer = ValidationOptimizer()
        assert optimizer._validation_count == 0
        assert optimizer._validation_errors == 0
        assert optimizer._cache_hits == 0
        assert optimizer._cache_misses == 0

    def test_validate_success(self):
        """Test successful validation."""
        optimizer = ValidationOptimizer()
        data = {"name": "Test", "age": 25, "email": "test@example.com"}

        result = optimizer.validate(TestModel, data)

        assert isinstance(result, TestModel)
        assert result.name == "Test"
        assert result.age == 25
        assert optimizer._validation_count == 1
        assert optimizer._validation_errors == 0

    def test_validate_with_early_validation(self):
        """Test validation with early validation enabled."""
        optimizer = ValidationOptimizer()
        data = {"name": "Test", "age": 25}

        result = optimizer.validate(TestModel, data, early_validation=True)

        assert isinstance(result, TestModel)
        assert result.name == "Test"

    def test_validate_without_early_validation(self):
        """Test validation without early validation."""
        optimizer = ValidationOptimizer()
        data = {"name": "Test", "age": 25}

        result = optimizer.validate(TestModel, data, early_validation=False)

        assert isinstance(result, TestModel)

    def test_validate_error(self):
        """Test validation with error."""
        optimizer = ValidationOptimizer()
        data = {"name": "Test"}  # Missing required 'age' field

        with pytest.raises(ValidationError):
            optimizer.validate(TestModel, data)

        assert optimizer._validation_count == 1
        assert optimizer._validation_errors == 1

    def test_validate_batch_success(self):
        """Test batch validation with all valid items."""
        optimizer = ValidationOptimizer()
        items = [
            {"name": "Test1", "age": 25},
            {"name": "Test2", "age": 30},
        ]

        validated, errors = optimizer.validate_batch(TestModel, items)

        assert len(validated) == 2
        assert len(errors) == 0
        assert optimizer._validation_count == 2

    def test_validate_batch_with_errors(self):
        """Test batch validation with some errors."""
        optimizer = ValidationOptimizer()
        items = [
            {"name": "Test1", "age": 25},  # Valid
            {"name": "Test2"},  # Invalid - missing age
            {"name": "Test3", "age": 30},  # Valid
        ]

        validated, errors = optimizer.validate_batch(
            TestModel, items, stop_on_first_error=False
        )

        assert len(validated) == 2
        assert len(errors) == 1

    def test_validate_batch_stop_on_first_error(self):
        """Test batch validation stopping on first error."""
        optimizer = ValidationOptimizer()
        items = [
            {"name": "Test1", "age": 25},  # Valid
            {"name": "Test2"},  # Invalid - missing age
            {"name": "Test3", "age": 30},  # Valid (won't be processed)
        ]

        validated, errors = optimizer.validate_batch(
            TestModel, items, stop_on_first_error=True
        )

        assert len(validated) == 1
        assert len(errors) == 1

    def test_get_stats(self):
        """Test statistics retrieval."""
        optimizer = ValidationOptimizer()
        data = {"name": "Test", "age": 25}

        # Perform some validations
        optimizer.validate(TestModel, data)
        optimizer.validate(TestModel, data)

        stats = optimizer.get_stats()
        assert stats["validation_count"] == 2
        assert stats["validation_errors"] == 0
        assert stats["error_rate"] == 0.0
        assert "schema_cache_stats" in stats

    def test_get_stats_with_errors(self):
        """Test statistics with errors."""
        optimizer = ValidationOptimizer()

        # Valid validation
        optimizer.validate(TestModel, {"name": "Test", "age": 25})

        # Invalid validation
        with contextlib.suppress(ValidationError):
            optimizer.validate(TestModel, {"name": "Test"})

        stats = optimizer.get_stats()
        assert stats["validation_count"] == 2
        assert stats["validation_errors"] == 1
        assert stats["error_rate"] == 0.5

    def test_reset_stats(self):
        """Test statistics reset."""
        optimizer = ValidationOptimizer()
        data = {"name": "Test", "age": 25}

        optimizer.validate(TestModel, data)
        assert optimizer._validation_count == 1

        optimizer.reset_stats()
        assert optimizer._validation_count == 0
        assert optimizer._validation_errors == 0
        assert optimizer._cache_hits == 0
        assert optimizer._cache_misses == 0


class TestSchemaCaching:
    """Test schema caching functionality."""

    def test_get_cached_schema_first_call(self):
        """Test schema caching on first call."""
        clear_schema_cache()
        schema = get_cached_schema(TestModel)

        assert schema is not None
        assert "properties" in schema or "type" in schema

    def test_get_cached_schema_cached(self):
        """Test schema is cached on subsequent calls."""
        clear_schema_cache()

        schema1 = get_cached_schema(TestModel)
        schema2 = get_cached_schema(TestModel)

        assert schema1 == schema2

    def test_get_cached_schema_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        clear_schema_cache()

        # Create many models to fill cache
        models = []
        for i in range(110):  # More than max_cache_size (100)

            class TempModel(BaseModel):
                field: str = f"value{i}"

            models.append(TempModel)
            get_cached_schema(TempModel)

        # First model should be evicted
        stats = get_schema_cache_stats()
        assert stats["cache_size"] <= 100

    def test_get_schema_cache_stats(self):
        """Test schema cache statistics."""
        clear_schema_cache()

        get_cached_schema(TestModel)
        stats = get_schema_cache_stats()

        assert stats["cache_size"] == 1
        assert stats["max_cache_size"] == 100
        assert "cached_models" in stats
        assert "TestModel" in stats["cached_models"]

    def test_clear_schema_cache(self):
        """Test clearing schema cache."""
        get_cached_schema(TestModel)
        assert get_schema_cache_stats()["cache_size"] > 0

        clear_schema_cache()
        assert get_schema_cache_stats()["cache_size"] == 0


class TestValidationFunctions:
    """Test validation utility functions."""

    def test_validate_early_success(self):
        """Test early validation with valid data."""
        data = {"name": "Test", "age": 25}
        result = validate_early(TestModel, data, required_fields=["name", "age"])

        assert isinstance(result, TestModel)
        assert result.name == "Test"

    def test_validate_early_missing_field(self):
        """Test early validation fails on missing required field."""
        data = {"name": "Test"}  # Missing 'age'

        with pytest.raises(ValidationError):
            validate_early(TestModel, data, required_fields=["name", "age"])

    def test_validate_early_no_required_fields(self):
        """Test early validation without required fields list."""
        data = {"name": "Test", "age": 25}
        result = validate_early(TestModel, data, required_fields=None)

        assert isinstance(result, TestModel)

    def test_optimized_validate_with_cache(self):
        """Test optimized validation with caching."""
        data = {"name": "Test", "age": 25}
        result = optimized_validate(TestModel, data, use_cache=True)

        assert isinstance(result, TestModel)

    def test_optimized_validate_without_cache(self):
        """Test optimized validation without caching."""
        data = {"name": "Test", "age": 25}
        result = optimized_validate(TestModel, data, use_cache=False)

        assert isinstance(result, TestModel)

    def test_validate_batch_all_valid(self):
        """Test batch validation with all valid items."""
        items = [
            {"name": "Test1", "age": 25},
            {"name": "Test2", "age": 30},
        ]

        validated, errors = validate_batch(TestModel, items)

        assert len(validated) == 2
        assert len(errors) == 0
        assert all(isinstance(v, TestModel) for v in validated)

    def test_validate_batch_with_errors(self):
        """Test batch validation with some errors."""
        items = [
            {"name": "Test1", "age": 25},  # Valid
            {"name": "Test2"},  # Invalid
            {"name": "Test3", "age": 30},  # Valid
        ]

        validated, errors = validate_batch(TestModel, items, stop_on_first_error=False)

        assert len(validated) == 2
        assert len(errors) == 1

    def test_validate_batch_stop_on_first_error(self):
        """Test batch validation stops on first error."""
        items = [
            {"name": "Test1", "age": 25},  # Valid
            {"name": "Test2"},  # Invalid
            {"name": "Test3", "age": 30},  # Valid (won't be processed)
        ]

        validated, errors = validate_batch(TestModel, items, stop_on_first_error=True)

        assert len(validated) == 1
        assert len(errors) == 1


class TestValidationMiddleware:
    """Test validation middleware decorator."""

    @pytest.mark.asyncio
    async def test_validation_middleware(self):
        """Test validation middleware decorator."""

        @validation_middleware
        async def test_handler(model: TestModel):
            return model.name

        data = TestModel(name="Test", age=25)
        result = await test_handler(model=data)

        assert result == "Test"

    @pytest.mark.asyncio
    async def test_validation_middleware_with_multiple_models(self):
        """Test middleware with multiple Pydantic models."""

        @validation_middleware
        async def test_handler(model1: TestModel, model2: TestModel):
            return f"{model1.name}-{model2.name}"

        data1 = TestModel(name="Test1", age=25)
        data2 = TestModel(name="Test2", age=30)
        result = await test_handler(model1=data1, model2=data2)

        assert result == "Test1-Test2"


class TestGlobalFunctions:
    """Test global functions."""

    def test_get_validation_optimizer(self):
        """Test getting global validation optimizer."""
        optimizer = get_validation_optimizer()

        assert optimizer is not None
        assert isinstance(optimizer, ValidationOptimizer)

    def test_get_validation_optimizer_singleton(self):
        """Test global optimizer is singleton."""
        optimizer1 = get_validation_optimizer()
        optimizer2 = get_validation_optimizer()

        assert optimizer1 is optimizer2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
