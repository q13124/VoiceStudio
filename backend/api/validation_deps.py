"""
FastAPI Dependencies for Optimized Validation

Provides dependencies for using the validation optimizer in route handlers.
"""

from typing import TypeVar

from pydantic import BaseModel

from app.core.validation.optimizer import (
    ValidationOptimizer,
    get_validation_optimizer,
)

T = TypeVar("T", bound=BaseModel)


def get_validator(model: type[T]) -> ValidationOptimizer:
    """
    Dependency to get validation optimizer for a specific model.

    Args:
        model: Pydantic model class

    Returns:
        Validation optimizer instance
    """
    optimizer = get_validation_optimizer()
    # Pre-warm schema cache
    optimizer.validate(model, {}, early_validation=False)
    return optimizer


def optimized_validate_dependency(model: type[T]):
    """
    Create a dependency for optimized validation of a model.

    Usage:
        @router.post("/endpoint")
        async def endpoint(
            data: dict = Body(...),
            validator: ValidationOptimizer = Depends(
                optimized_validate_dependency(VoiceSynthesizeRequest)
            )
        ):
            validated = validator.validate(VoiceSynthesizeRequest, data)
            ...
    """

    def _get_validator() -> ValidationOptimizer:
        return get_validator(model)

    return _get_validator

