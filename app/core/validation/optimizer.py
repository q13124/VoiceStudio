"""
Pydantic Validation Optimizer

Optimizes Pydantic model validation for better performance:
- Schema caching
- Early validation failures
- Optimized field validation
- Reduced validation overhead
"""

from __future__ import annotations

import functools
import logging
from collections import OrderedDict
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# Schema cache for Pydantic models
_schema_cache: dict[type[BaseModel], dict[str, Any]] = OrderedDict()
_max_cache_size: int = 100


def get_cached_schema(model: type[BaseModel]) -> dict[str, Any]:
    """
    Get cached JSON schema for a Pydantic model.

    Args:
        model: Pydantic model class

    Returns:
        Cached JSON schema
    """
    if model in _schema_cache:
        # Move to end (LRU)
        schema = _schema_cache.pop(model)
        _schema_cache[model] = schema
        return schema

    # Generate and cache schema
    # Support both Pydantic v1 and v2
    try:
        # Pydantic v2
        schema = model.model_json_schema()
    except AttributeError:
        try:
            # Pydantic v1
            schema = model.schema()
        except AttributeError:
            # Fallback: create instance and get schema
            try:
                schema = model.__pydantic_model__.schema()
            except AttributeError:
                # Last resort: empty schema
                logger.warning(
                    f"Could not generate schema for {model.__name__}"
                )
                schema = {"type": "object"}

    _schema_cache[model] = schema

    # Evict oldest if cache is full
    if len(_schema_cache) > _max_cache_size:
        _schema_cache.popitem(last=False)

    return schema


def clear_schema_cache():
    """Clear the schema cache."""
    _schema_cache.clear()


def get_schema_cache_stats() -> dict[str, Any]:
    """Get schema cache statistics."""
    return {
        "cache_size": len(_schema_cache),
        "max_cache_size": _max_cache_size,
        "cached_models": [model.__name__ for model in _schema_cache],
    }


def validate_early(
    model: type[T], data: dict[str, Any], required_fields: list[str] | None = None
) -> T:
    """
    Validate a model with early failure for required fields.

    Args:
        model: Pydantic model class
        data: Data to validate
        required_fields: List of required field names to check first

    Returns:
        Validated model instance

    Raises:
        ValidationError: If validation fails
    """
    # Early validation: Check required fields first
    if required_fields:
        schema = get_cached_schema(model)
        required = schema.get("required", [])
        for field in required_fields:
            if field in required and field not in data:
                raise ValidationError.from_exception_data(
                    model.__name__,
                    [
                        {
                            "type": "missing",
                            "loc": (field,),
                            "msg": "Field required",
                            "input": data,
                        }
                    ],
                )

    # Full validation
    return model(**data)


def optimized_validate(
    model: type[T], data: dict[str, Any], use_cache: bool = True
) -> T:
    """
    Optimized validation with schema caching.

    Args:
        model: Pydantic model class
        data: Data to validate
        use_cache: Whether to use schema cache

    Returns:
        Validated model instance
    """
    if use_cache:
        # Pre-warm schema cache
        get_cached_schema(model)

    return model(**data)


def validate_batch(
    model: type[T], items: list[dict[str, Any]], stop_on_first_error: bool = False
) -> tuple[list[T], list[ValidationError]]:
    """
    Validate a batch of items with optimized performance.

    Args:
        model: Pydantic model class
        items: List of data dictionaries to validate
        stop_on_first_error: Whether to stop on first validation error

    Returns:
        Tuple of (validated_items, errors)
    """
    # Pre-warm schema cache
    get_cached_schema(model)

    validated = []
    errors = []

    for _i, item in enumerate(items):
        try:
            validated_item = model(**item)
            validated.append(validated_item)
        except ValidationError as e:
            errors.append(e)
            if stop_on_first_error:
                break

    return validated, errors


def validation_middleware(func):
    """
    Decorator to add validation optimization to route handlers.

    Automatically caches schemas and optimizes validation.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Pre-warm schema cache for any Pydantic models in kwargs
        for value in kwargs.values():
            if isinstance(value, BaseModel):
                model_type = type(value)
                get_cached_schema(model_type)

        return await func(*args, **kwargs)

    return wrapper


class ValidationOptimizer:
    """
    Validation optimizer for Pydantic models.

    Provides:
    - Schema caching
    - Batch validation
    - Early validation failures
    - Performance metrics
    """

    def __init__(self):
        self._validation_count = 0
        self._validation_errors = 0
        self._cache_hits = 0
        self._cache_misses = 0

    def validate(
        self, model: type[T], data: dict[str, Any], early_validation: bool = True
    ) -> T:
        """
        Validate data against a model with optimizations.

        Args:
            model: Pydantic model class
            data: Data to validate
            early_validation: Whether to use early validation

        Returns:
            Validated model instance
        """
        self._validation_count += 1

        try:
            if early_validation:
                # Get required fields from schema
                schema = get_cached_schema(model)
                required_fields = schema.get("required", [])
                return validate_early(model, data, required_fields)
            else:
                return optimized_validate(model, data)
        except ValidationError:
            self._validation_errors += 1
            raise

    def validate_batch(
        self,
        model: type[T],
        items: list[dict[str, Any]],
        stop_on_first_error: bool = False,
    ) -> tuple[list[T], list[ValidationError]]:
        """
        Validate a batch of items.

        Args:
            model: Pydantic model class
            items: List of data dictionaries
            stop_on_first_error: Whether to stop on first error

        Returns:
            Tuple of (validated_items, errors)
        """
        self._validation_count += len(items)
        return validate_batch(model, items, stop_on_first_error)

    def get_stats(self) -> dict[str, Any]:
        """Get validation statistics."""
        cache_hit_rate = (
            self._cache_hits / (self._cache_hits + self._cache_misses)
            if (self._cache_hits + self._cache_misses) > 0
            else 0.0
        )
        error_rate = (
            self._validation_errors / self._validation_count
            if self._validation_count > 0
            else 0.0
        )

        return {
            "validation_count": self._validation_count,
            "validation_errors": self._validation_errors,
            "error_rate": error_rate,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "cache_hit_rate": cache_hit_rate,
            "schema_cache_stats": get_schema_cache_stats(),
        }

    def reset_stats(self):
        """Reset validation statistics."""
        self._validation_count = 0
        self._validation_errors = 0
        self._cache_hits = 0
        self._cache_misses = 0


# Global validation optimizer instance
_optimizer = ValidationOptimizer()


def get_validation_optimizer() -> ValidationOptimizer:
    """Get the global validation optimizer instance."""
    return _optimizer

