"""
Base Domain Service.

Task 3.1.4: Domain services for cross-entity operations.
"""

from __future__ import annotations

from abc import ABC
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class DomainService(ABC):
    """
    Base class for domain services.
    
    Domain services encapsulate domain logic that:
    - Doesn't naturally fit within a single entity
    - Requires orchestration across multiple entities
    - Implements a stateless business operation
    
    Domain services are stateless and operate on entities.
    They don't handle persistence (that's the repository's job).
    """
    
    def __init__(self, name: Optional[str] = None):
        """
        Initialize domain service.
        
        Args:
            name: Optional service name for logging
        """
        self._name = name or self.__class__.__name__
        self._logger = logging.getLogger(f"domain.services.{self._name}")
    
    def _log_operation(self, operation: str, **kwargs) -> None:
        """Log a domain operation."""
        self._logger.info(f"{operation}: {kwargs}")
