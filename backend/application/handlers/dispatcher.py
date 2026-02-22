"""
Command and Query Dispatchers.

Task 3.2.3: Mediator pattern for use case orchestration.
"""

from __future__ import annotations

import logging
from typing import Any

from backend.application.commands.base import Command, CommandHandler, CommandResult
from backend.application.queries.base import Query, QueryHandler, QueryResult

logger = logging.getLogger(__name__)


class CommandDispatcher:
    """
    Dispatcher for commands.

    Routes commands to their handlers and provides
    cross-cutting concerns like logging and validation.
    """

    def __init__(self):
        self._handlers: dict[type[Command], CommandHandler] = {}
        self._middleware: list = []

    def register(
        self,
        command_type: type[Command],
        handler: CommandHandler,
    ) -> None:
        """
        Register a handler for a command type.

        Args:
            command_type: Type of command
            handler: Handler instance
        """
        self._handlers[command_type] = handler
        logger.debug(f"Registered handler for {command_type.__name__}")

    def register_handler(self, handler: CommandHandler) -> None:
        """
        Register a handler using its command_type property.

        Args:
            handler: Handler instance with command_type property
        """
        self.register(handler.command_type, handler)

    async def dispatch(self, command: Command) -> CommandResult:
        """
        Dispatch a command to its handler.

        Args:
            command: Command to dispatch

        Returns:
            CommandResult from the handler
        """
        command_type = type(command)
        handler = self._handlers.get(command_type)

        if not handler:
            logger.error(f"No handler for command: {command_type.__name__}")
            return CommandResult.fail(
                f"No handler registered for {command_type.__name__}",
                code="HANDLER_NOT_FOUND",
            )

        logger.info(f"Dispatching command: {command_type.__name__}")

        try:
            # Execute middleware (pre-processing)
            for middleware in self._middleware:
                command = await middleware.before(command)

            # Execute handler
            result = await handler.handle(command)

            # Execute middleware (post-processing)
            for middleware in reversed(self._middleware):
                result = await middleware.after(command, result)

            return result

        except Exception as e:
            logger.exception(f"Command handler error: {e}")
            return CommandResult.fail(str(e), code="HANDLER_ERROR")

    def add_middleware(self, middleware: Any) -> None:
        """Add middleware for cross-cutting concerns."""
        self._middleware.append(middleware)


class QueryDispatcher:
    """
    Dispatcher for queries.

    Routes queries to their handlers with caching support.
    """

    def __init__(self):
        self._handlers: dict[type[Query], QueryHandler] = {}
        self._cache: Any | None = None  # Optional cache implementation

    def register(
        self,
        query_type: type[Query],
        handler: QueryHandler,
    ) -> None:
        """
        Register a handler for a query type.

        Args:
            query_type: Type of query
            handler: Handler instance
        """
        self._handlers[query_type] = handler
        logger.debug(f"Registered handler for {query_type.__name__}")

    def register_handler(self, handler: QueryHandler) -> None:
        """
        Register a handler using its query_type property.

        Args:
            handler: Handler instance with query_type property
        """
        self.register(handler.query_type, handler)

    async def dispatch(self, query: Query) -> QueryResult:
        """
        Dispatch a query to its handler.

        Args:
            query: Query to dispatch

        Returns:
            QueryResult from the handler
        """
        query_type = type(query)
        handler = self._handlers.get(query_type)

        if not handler:
            logger.error(f"No handler for query: {query_type.__name__}")
            return QueryResult.fail(f"No handler registered for {query_type.__name__}")

        logger.debug(f"Dispatching query: {query_type.__name__}")

        try:
            # Check cache if available
            if self._cache:
                cached: QueryResult[Any] | None = await self._cache.get(query)
                if cached is not None:
                    return cached

            # Execute handler
            result = await handler.handle(query)

            # Store in cache if available
            if self._cache and result.success:
                await self._cache.set(query, result)

            return result

        except Exception as e:
            logger.exception(f"Query handler error: {e}")
            return QueryResult.fail(str(e))

    def set_cache(self, cache: Any) -> None:
        """Set cache implementation for query results."""
        self._cache = cache


# Global dispatchers
_command_dispatcher: CommandDispatcher | None = None
_query_dispatcher: QueryDispatcher | None = None


def get_command_dispatcher() -> CommandDispatcher:
    """Get or create the global command dispatcher."""
    global _command_dispatcher
    if _command_dispatcher is None:
        _command_dispatcher = CommandDispatcher()
    return _command_dispatcher


def get_query_dispatcher() -> QueryDispatcher:
    """Get or create the global query dispatcher."""
    global _query_dispatcher
    if _query_dispatcher is None:
        _query_dispatcher = QueryDispatcher()
    return _query_dispatcher


async def dispatch_command(command: Command) -> CommandResult:
    """Convenience function to dispatch a command."""
    return await get_command_dispatcher().dispatch(command)


async def dispatch_query(query: Query) -> QueryResult:
    """Convenience function to dispatch a query."""
    return await get_query_dispatcher().dispatch(query)
