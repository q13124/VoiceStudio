"""
Query Pattern Base Classes.

Task 3.2.2: CQRS query pattern implementation.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass
class Query(ABC):
    """
    Base class for queries.

    Queries represent a request for data without side effects.
    They are named as questions (GetProject, ListUsers).
    """

    # Unique query ID for tracking
    query_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # When the query was issued
    timestamp: datetime = field(default_factory=datetime.now)

    # Optional correlation ID for request tracing
    correlation_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "query_type": self.__class__.__name__,
            "query_id": self.query_id,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
        }


@dataclass
class QueryResult(Generic[T]):
    """
    Result of a query execution.

    Wraps the data or error from query handling.
    """

    success: bool
    data: T | None = None
    error_message: str | None = None

    # Pagination info for list queries
    total_count: int | None = None
    page: int | None = None
    page_size: int | None = None

    @classmethod
    def ok(
        cls,
        data: T,
        total_count: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
    ) -> QueryResult[T]:
        """Create a successful result."""
        return cls(
            success=True,
            data=data,
            total_count=total_count,
            page=page,
            page_size=page_size,
        )

    @classmethod
    def empty(cls) -> QueryResult[T]:
        """Create an empty result (not found)."""
        return cls(success=True, data=None)

    @classmethod
    def fail(cls, message: str) -> QueryResult[T]:
        """Create a failed result."""
        return cls(success=False, error_message=message)

    @property
    def has_more_pages(self) -> bool:
        """Check if there are more pages."""
        if self.total_count is None or self.page is None or self.page_size is None:
            return False
        return (self.page * self.page_size) < self.total_count


class QueryHandler(ABC, Generic[T]):
    """
    Base class for query handlers.

    Handlers process queries and return results.
    Each query type has exactly one handler.
    """

    @abstractmethod
    async def handle(self, query: Query) -> QueryResult[T]:
        """
        Handle the query.

        Args:
            query: The query to handle

        Returns:
            QueryResult with data or error
        """
        pass

    @property
    @abstractmethod
    def query_type(self) -> type:
        """Return the type of query this handler processes."""
        pass
