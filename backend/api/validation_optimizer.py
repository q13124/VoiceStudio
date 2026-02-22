"""
Request Validation Optimization System

Optimizes Pydantic model validation through:
- Schema caching
- Early validation failures
- Optimized validation order
- Performance monitoring
"""

from __future__ import annotations

import hashlib
import logging
import time
from collections import OrderedDict
from typing import Any, TypeVar, cast

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# Schema cache: maps model class name to compiled schema
_schema_cache: dict[str, Any] = {}

# Validation cache: maps (model_hash, data_hash) to validated instance
_validation_cache: OrderedDict[str, BaseModel] = OrderedDict()
_validation_cache_max_size: int = 1000

# Validation statistics
_validation_stats: dict[str, dict[str, Any]] = {}


def _get_model_hash(model: type[BaseModel]) -> str:
    """Generate hash for a Pydantic model."""
    try:
        # Use model's JSON schema as hash source
        schema = model.model_json_schema()
        schema_str = str(sorted(schema.items()))
        return hashlib.md5(schema_str.encode()).hexdigest()
    except Exception as e:
        logger.debug(f"Failed to generate model hash: {e}")
        return model.__name__


def _get_data_hash(data: dict[str, Any]) -> str:
    """Generate hash for validation data."""
    try:
        # Sort keys for consistent hashing
        sorted_data = json.dumps(data, sort_keys=True)
        return hashlib.md5(sorted_data.encode()).hexdigest()
    except Exception:
        return str(hash(str(data)))


def _get_cached_schema(model: type[BaseModel]) -> Any:
    """Get cached schema for a model."""
    model_name = model.__name__
    if model_name not in _schema_cache:
        try:
            # Cache the model's schema
            schema = model.model_json_schema()
            _schema_cache[model_name] = schema
            logger.debug(f"Cached schema for {model_name}")
        except Exception as e:
            logger.debug(f"Failed to cache schema for {model_name}: {e}")
            return None
    return _schema_cache.get(model_name)


def _validate_early(model: type[BaseModel], data: dict[str, Any]) -> str | None:
    """
    Perform early validation checks before full Pydantic validation.

    Returns:
        Error message if validation fails early, None otherwise
    """
    try:
        # Get model fields
        fields = model.model_fields

        # Check required fields first (fastest check)
        for field_name, field_info in fields.items():
            if field_info.is_required() and field_name not in data:
                return f"Missing required field: {field_name}"

        # Check field types early (before validators)
        for field_name, value in data.items():
            if field_name not in fields:
                # Allow extra fields if configured
                continue

            field_info = fields[field_name]
            annotation = field_info.annotation

            # Basic type checking
            if annotation and value is not None:
                # Check for common types
                origin = getattr(annotation, "__origin__", None)
                if origin is list:
                    if not isinstance(value, list):
                        return f"Field {field_name} must be a list"
                elif origin is dict:
                    if not isinstance(value, dict):
                        return f"Field {field_name} must be a dict"
                elif annotation == str:
                    if not isinstance(value, str):
                        return f"Field {field_name} must be a string"
                elif annotation == int:
                    if not isinstance(value, int):
                        return f"Field {field_name} must be an integer"
                elif annotation == float and not isinstance(value, (int, float)):
                    return f"Field {field_name} must be a number"

        return None
    except Exception as e:
        logger.debug(f"Early validation check failed: {e}")
        return None


def validate_optimized(model: type[T], data: dict[str, Any], use_cache: bool = True) -> T:
    """
    Optimized validation with caching and early failure detection.

    Args:
        model: Pydantic model class
        data: Data to validate
        use_cache: Whether to use validation cache

    Returns:
        Validated model instance

    Raises:
        ValidationError: If validation fails
    """
    start_time = time.perf_counter()
    model_name = model.__name__

    # Initialize stats if needed
    if model_name not in _validation_stats:
        _validation_stats[model_name] = {
            "total_validations": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "early_failures": 0,
            "total_time": 0.0,
            "avg_time": 0.0,
        }

    stats = _validation_stats[model_name]
    stats["total_validations"] += 1

    # Check validation cache
    if use_cache:
        model_hash = _get_model_hash(model)
        data_hash = _get_data_hash(data)
        cache_key = f"{model_hash}:{data_hash}"

        if cache_key in _validation_cache:
            stats["cache_hits"] += 1
            validation_time = time.perf_counter() - start_time
            stats["total_time"] += validation_time
            stats["avg_time"] = stats["total_time"] / stats["total_validations"]
            return cast(T, _validation_cache[cache_key])

        stats["cache_misses"] += 1

    # Early validation check
    early_error = _validate_early(model, data)
    if early_error:
        stats["early_failures"] += 1
        validation_time = time.perf_counter() - start_time
        stats["total_time"] += validation_time
        stats["avg_time"] = stats["total_time"] / stats["total_validations"]
        raise ValidationError.from_exception_data(
            model.__name__, [{"type": "value_error", "loc": (), "input": data}]
        )

    # Full Pydantic validation
    try:
        instance = model(**data)

        # Cache validated instance
        if use_cache:
            if len(_validation_cache) >= _validation_cache_max_size:
                # Remove oldest entry (LRU)
                _validation_cache.popitem(last=False)
            _validation_cache[cache_key] = instance

        validation_time = time.perf_counter() - start_time
        stats["total_time"] += validation_time
        stats["avg_time"] = stats["total_time"] / stats["total_validations"]

        return instance
    except ValidationError:
        validation_time = time.perf_counter() - start_time
        stats["total_time"] += validation_time
        stats["avg_time"] = stats["total_time"] / stats["total_validations"]
        raise


def optimize_model(model: type[BaseModel]) -> type[BaseModel]:
    """
    Optimize a Pydantic model for faster validation.

    Args:
        model: Pydantic model class

    Returns:
        Optimized model class (may be the same)
    """
    # Cache schema
    _get_cached_schema(model)

    # Return original model (optimization is in validation, not model itself)
    return model


def get_validation_stats(model_name: str | None = None) -> dict[str, Any]:
    """
    Get validation statistics.

    Args:
        model_name: Optional model name to get stats for specific model

    Returns:
        Validation statistics
    """
    if model_name:
        return _validation_stats.get(model_name, {})
    return _validation_stats.copy()


def clear_validation_cache():
    """Clear the validation cache."""
    global _validation_cache
    _validation_cache.clear()
    logger.info("Validation cache cleared")


def clear_schema_cache():
    """Clear the schema cache."""
    global _schema_cache
    _schema_cache.clear()
    logger.info("Schema cache cleared")


def get_cache_stats() -> dict[str, Any]:
    """Get cache statistics."""
    return {
        "schema_cache_size": len(_schema_cache),
        "validation_cache_size": len(_validation_cache),
        "validation_cache_max_size": _validation_cache_max_size,
        "validation_stats": get_validation_stats(),
    }


# Import json for data hashing
import json
