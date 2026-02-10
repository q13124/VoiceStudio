"""Application handlers package."""

from backend.application.handlers.dispatcher import (
    CommandDispatcher,
    QueryDispatcher,
    get_command_dispatcher,
    get_query_dispatcher,
)

__all__ = [
    "CommandDispatcher",
    "QueryDispatcher",
    "get_command_dispatcher",
    "get_query_dispatcher",
]
