"""
Safe Query Builder.

Task 1.3.4 (partial): Parameterized query enforcement.
Provides SQL injection prevention through parameterized queries.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any


class QueryType(Enum):
    """Types of SQL queries."""

    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class JoinType(Enum):
    """Types of SQL joins."""

    INNER = "INNER JOIN"
    LEFT = "LEFT JOIN"
    RIGHT = "RIGHT JOIN"
    FULL = "FULL OUTER JOIN"


@dataclass
class SafeQuery:
    """
    A parameterized query that's safe from SQL injection.
    """

    sql: str
    params: tuple[Any, ...]

    def __str__(self) -> str:
        return self.sql


class QueryBuilder:
    """
    Safe SQL query builder with parameterized queries.

    Features:
    - SQL injection prevention
    - Type-safe parameter binding
    - Fluent interface
    - Cross-database compatibility
    """

    # Allowed characters for identifiers (tables, columns)
    IDENTIFIER_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

    def __init__(self, table: str):
        self._validate_identifier(table)
        self._table = table
        self._query_type: QueryType | None = None
        self._columns: list[str] = []
        self._where_clauses: list[tuple[str, str, Any]] = []
        self._joins: list[tuple[JoinType, str, str]] = []
        self._order_by: list[tuple[str, bool]] = []
        self._group_by: list[str] = []
        self._having: list[tuple[str, str, Any]] = []
        self._limit: int | None = None
        self._offset: int | None = None
        self._update_values: dict[str, Any] = {}
        self._insert_values: dict[str, Any] = {}

    @staticmethod
    def _validate_identifier(identifier: str) -> None:
        """Validate that an identifier is safe."""
        if not QueryBuilder.IDENTIFIER_PATTERN.match(identifier):
            raise ValueError(f"Invalid identifier: {identifier}")

    def select(self, *columns: str) -> QueryBuilder:
        """Start a SELECT query."""
        self._query_type = QueryType.SELECT
        for col in columns:
            self._validate_identifier(
                col.split(".")[-1].split(" ")[0]
            )  # Handle table.column and aliases
        self._columns = list(columns) if columns else ["*"]
        return self

    def insert(self, **values: Any) -> QueryBuilder:
        """Start an INSERT query."""
        self._query_type = QueryType.INSERT
        for key in values:
            self._validate_identifier(key)
        self._insert_values = values
        return self

    def update(self, **values: Any) -> QueryBuilder:
        """Start an UPDATE query."""
        self._query_type = QueryType.UPDATE
        for key in values:
            self._validate_identifier(key)
        self._update_values = values
        return self

    def delete(self) -> QueryBuilder:
        """Start a DELETE query."""
        self._query_type = QueryType.DELETE
        return self

    def where(self, column: str, operator: str, value: Any) -> QueryBuilder:
        """Add a WHERE clause."""
        self._validate_identifier(column.split(".")[-1])

        # Validate operator
        allowed_operators = [
            "=",
            "!=",
            "<>",
            ">",
            "<",
            ">=",
            "<=",
            "LIKE",
            "IN",
            "NOT IN",
            "IS",
            "IS NOT",
        ]
        if operator.upper() not in allowed_operators:
            raise ValueError(f"Invalid operator: {operator}")

        self._where_clauses.append((column, operator.upper(), value))
        return self

    def where_eq(self, column: str, value: Any) -> QueryBuilder:
        """Add equality WHERE clause."""
        return self.where(column, "=", value)

    def where_in(self, column: str, values: list[Any]) -> QueryBuilder:
        """Add WHERE IN clause."""
        return self.where(column, "IN", values)

    def where_like(self, column: str, pattern: str) -> QueryBuilder:
        """Add WHERE LIKE clause."""
        return self.where(column, "LIKE", pattern)

    def where_null(self, column: str) -> QueryBuilder:
        """Add WHERE IS NULL clause."""
        return self.where(column, "IS", None)

    def where_not_null(self, column: str) -> QueryBuilder:
        """Add WHERE IS NOT NULL clause."""
        return self.where(column, "IS NOT", None)

    def join(
        self,
        table: str,
        on: str,
        join_type: JoinType = JoinType.INNER,
    ) -> QueryBuilder:
        """Add a JOIN clause."""
        self._validate_identifier(table)
        self._joins.append((join_type, table, on))
        return self

    def order_by(self, column: str, descending: bool = False) -> QueryBuilder:
        """Add ORDER BY clause."""
        self._validate_identifier(column.split(".")[-1])
        self._order_by.append((column, descending))
        return self

    def group_by(self, *columns: str) -> QueryBuilder:
        """Add GROUP BY clause."""
        for col in columns:
            self._validate_identifier(col.split(".")[-1])
        self._group_by.extend(columns)
        return self

    def having(self, column: str, operator: str, value: Any) -> QueryBuilder:
        """Add HAVING clause."""
        self._validate_identifier(column.split(".")[-1])
        self._having.append((column, operator, value))
        return self

    def limit(self, count: int) -> QueryBuilder:
        """Add LIMIT clause."""
        if count < 0:
            raise ValueError("Limit must be non-negative")
        self._limit = count
        return self

    def offset(self, count: int) -> QueryBuilder:
        """Add OFFSET clause."""
        if count < 0:
            raise ValueError("Offset must be non-negative")
        self._offset = count
        return self

    def build(self) -> SafeQuery:
        """Build the parameterized query."""
        if self._query_type == QueryType.SELECT:
            return self._build_select()
        elif self._query_type == QueryType.INSERT:
            return self._build_insert()
        elif self._query_type == QueryType.UPDATE:
            return self._build_update()
        elif self._query_type == QueryType.DELETE:
            return self._build_delete()
        else:
            raise ValueError("Query type not set")

    def _build_select(self) -> SafeQuery:
        """Build SELECT query."""
        params: list[Any] = []

        sql = f"SELECT {', '.join(self._columns)} FROM {self._table}"

        # Joins
        for join_type, table, on in self._joins:
            sql += f" {join_type.value} {table} ON {on}"

        # Where
        where_sql, where_params = self._build_where()
        if where_sql:
            sql += f" WHERE {where_sql}"
            params.extend(where_params)

        # Group by
        if self._group_by:
            sql += f" GROUP BY {', '.join(self._group_by)}"

        # Having
        if self._having:
            having_parts = []
            for col, op, val in self._having:
                having_parts.append(f"{col} {op} ?")
                params.append(val)
            sql += f" HAVING {' AND '.join(having_parts)}"

        # Order by
        if self._order_by:
            order_parts = [f"{col} {'DESC' if desc else 'ASC'}" for col, desc in self._order_by]
            sql += f" ORDER BY {', '.join(order_parts)}"

        # Limit/offset
        if self._limit is not None:
            sql += f" LIMIT {self._limit}"
        if self._offset is not None:
            sql += f" OFFSET {self._offset}"

        return SafeQuery(sql=sql, params=tuple(params))

    def _build_insert(self) -> SafeQuery:
        """Build INSERT query."""
        columns = list(self._insert_values.keys())
        placeholders = ", ".join(["?" for _ in columns])
        values = list(self._insert_values.values())

        sql = f"INSERT INTO {self._table} ({', '.join(columns)}) VALUES ({placeholders})"

        return SafeQuery(sql=sql, params=tuple(values))

    def _build_update(self) -> SafeQuery:
        """Build UPDATE query."""
        params: list[Any] = []

        set_parts = []
        for col, val in self._update_values.items():
            set_parts.append(f"{col} = ?")
            params.append(val)

        sql = f"UPDATE {self._table} SET {', '.join(set_parts)}"

        # Where
        where_sql, where_params = self._build_where()
        if where_sql:
            sql += f" WHERE {where_sql}"
            params.extend(where_params)

        return SafeQuery(sql=sql, params=tuple(params))

    def _build_delete(self) -> SafeQuery:
        """Build DELETE query."""
        params: list[Any] = []

        sql = f"DELETE FROM {self._table}"

        # Where
        where_sql, where_params = self._build_where()
        if where_sql:
            sql += f" WHERE {where_sql}"
            params.extend(where_params)

        return SafeQuery(sql=sql, params=tuple(params))

    def _build_where(self) -> tuple[str, list[Any]]:
        """Build WHERE clause."""
        if not self._where_clauses:
            return "", []

        parts = []
        params: list[Any] = []

        for col, op, val in self._where_clauses:
            if op == "IN" or op == "NOT IN":
                placeholders = ", ".join(["?" for _ in val])
                parts.append(f"{col} {op} ({placeholders})")
                params.extend(val)
            elif val is None:
                parts.append(f"{col} {op} NULL")
            else:
                parts.append(f"{col} {op} ?")
                params.append(val)

        return " AND ".join(parts), params


# Convenience function
def query(table: str) -> QueryBuilder:
    """Create a new query builder for a table."""
    return QueryBuilder(table)
