"""
Todo Panel Routes

Endpoints for todo/task management.
"""

import json
import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

try:
    from ..optimization import cache_response
except ImportError:
    # Fallback if optimization module not available
    def cache_response(ttl: int = 300):
        def decorator(func):
            return func

        return decorator


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/todo-panel", tags=["todo-panel"])

# Database integration
_todo_db = None
_todo_db_path = None
_use_database = True


def _get_todo_database():
    """Get or initialize todo database connection."""
    global _todo_db, _todo_db_path

    if _todo_db is not None:
        return _todo_db

    try:
        # Try to use DatabaseQueryOptimizer if available
        try:
            from app.core.database.query_optimizer import DatabaseQueryOptimizer

            # Set database path
            db_dir = Path.home() / ".voicestudio"
            db_dir.mkdir(parents=True, exist_ok=True)
            _todo_db_path = str(db_dir / "todos.db")

            _todo_db = DatabaseQueryOptimizer(
                db_path=_todo_db_path,
                enable_cache=True,
                cache_size=100,
                cache_ttl=300.0,  # 5 minutes
            )

            # Initialize schema
            _init_todo_database(_todo_db)
            logger.info(
                f"Todo database initialized with query optimizer: {_todo_db_path}"
            )
            return _todo_db
        except ImportError:
            # Fallback to direct SQLite
            db_dir = Path.home() / ".voicestudio"
            db_dir.mkdir(parents=True, exist_ok=True)
            _todo_db_path = str(db_dir / "todos.db")

            conn = sqlite3.connect(_todo_db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            _todo_db = conn

            # Initialize schema
            _init_todo_database_simple(_todo_db)
            logger.info(
                f"Todo database initialized with direct SQLite: {_todo_db_path}"
            )
            return _todo_db
    except Exception as e:
        logger.error(f"Failed to initialize todo database: {e}")
        _use_database = False
        return None


def _init_todo_database(db):
    """Initialize database schema using DatabaseQueryOptimizer."""
    try:
        # Create todos table
        db.execute_query(
            """
            CREATE TABLE IF NOT EXISTS todos (
                todo_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                priority TEXT NOT NULL DEFAULT 'medium',
                category TEXT,
                tags TEXT,  -- JSON array
                due_date TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                completed_at TEXT,
                metadata TEXT  -- JSON object
            )
            """,
            use_cache=False,
        )

        # Create indexes for performance
        db.create_index("todos", "status")
        db.create_index("todos", "priority")
        db.create_index("todos", "category")
        db.create_index("todos", "created_at")

        logger.info("Todo database schema initialized")
    except Exception as e:
        logger.error(f"Failed to initialize todo database schema: {e}")
        raise


def _init_todo_database_simple(conn):
    """Initialize database schema using direct SQLite."""
    try:
        cursor = conn.cursor()

        # Create todos table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                todo_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                priority TEXT NOT NULL DEFAULT 'medium',
                category TEXT,
                tags TEXT,
                due_date TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                completed_at TEXT,
                metadata TEXT
            )
            """
        )

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_todos_status ON todos(status)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_todos_priority ON todos(priority)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_todos_category ON todos(category)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_todos_created_at ON todos(created_at)"
        )

        conn.commit()
        logger.info("Todo database schema initialized (simple)")
    except Exception as e:
        logger.error(f"Failed to initialize todo database schema: {e}")
        raise


def _load_todo_from_db(todo_id: str) -> Optional["Todo"]:
    """Load a todo from database.
    
    Args:
        todo_id: The todo ID to load
        
    Returns:
        Todo object if found, None if not found
        
    Raises:
        HTTPException: If database is unavailable (503) or query fails (500)
    """
    db = _get_todo_database()
    if not db or not _use_database:
        raise HTTPException(
            status_code=503,
            detail="Todo service unavailable. Database not initialized."
        )

    try:
        if isinstance(db, sqlite3.Connection):
            # Direct SQLite
            cursor = db.cursor()
            cursor.execute("SELECT * FROM todos WHERE todo_id = ?", (todo_id,))
            row = cursor.fetchone()
            if not row:
                return None  # Not found - valid return
            return _row_to_todo(dict(row))
        else:
            # DatabaseQueryOptimizer
            results = db.execute_query(
                "SELECT * FROM todos WHERE todo_id = ?",
                parameters=(todo_id,),
                use_cache=True,
            )
            if results:
                return _row_to_todo(results[0])
            return None  # Not found - valid return
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Failed to load todo from database: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Database query failed: {str(e)}"
        )


def _save_todo_to_db(todo: "Todo"):
    """Save a todo to database.
    
    Raises:
        HTTPException: If database is unavailable (503) or save fails (500)
    """
    db = _get_todo_database()
    if not db or not _use_database:
        raise HTTPException(
            status_code=503,
            detail="Todo service unavailable. Database not initialized."
        )

    try:
        tags_json = json.dumps(todo.tags) if todo.tags else "[]"
        metadata_json = json.dumps(todo.metadata) if todo.metadata else "{}"

        if isinstance(db, sqlite3.Connection):
            # Direct SQLite
            cursor = db.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO todos 
                (todo_id, title, description, status, priority, category, tags, 
                 due_date, created_at, updated_at, completed_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    todo.todo_id,
                    todo.title,
                    todo.description,
                    todo.status,
                    todo.priority,
                    todo.category,
                    tags_json,
                    todo.due_date,
                    todo.created_at,
                    todo.updated_at,
                    todo.completed_at,
                    metadata_json,
                ),
            )
            db.commit()
        else:
            # DatabaseQueryOptimizer
            db.execute_query(
                """
                INSERT OR REPLACE INTO todos 
                (todo_id, title, description, status, priority, category, tags, 
                 due_date, created_at, updated_at, completed_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                parameters=(
                    todo.todo_id,
                    todo.title,
                    todo.description,
                    todo.status,
                    todo.priority,
                    todo.category,
                    tags_json,
                    todo.due_date,
                    todo.created_at,
                    todo.updated_at,
                    todo.completed_at,
                    metadata_json,
                ),
                use_cache=False,
            )
            # Invalidate cache
            if hasattr(db, "cache"):
                db.cache.invalidate(f"todo_{todo.todo_id}")
        return True
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save todo to database: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save todo: {str(e)}"
        )


def _delete_todo_from_db(todo_id: str) -> bool:
    """Delete a todo from database.
    
    Raises:
        HTTPException: If database is unavailable (503) or delete fails (500)
    """
    db = _get_todo_database()
    if not db or not _use_database:
        raise HTTPException(
            status_code=503,
            detail="Todo service unavailable. Database not initialized."
        )

    try:
        if isinstance(db, sqlite3.Connection):
            # Direct SQLite
            cursor = db.cursor()
            cursor.execute("DELETE FROM todos WHERE todo_id = ?", (todo_id,))
            db.commit()
        else:
            # DatabaseQueryOptimizer
            db.execute_query(
                "DELETE FROM todos WHERE todo_id = ?",
                parameters=(todo_id,),
                use_cache=False,
            )
            # Invalidate cache
            if hasattr(db, "cache"):
                db.cache.invalidate(f"todo_{todo_id}")
        return True
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete todo from database: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete todo: {str(e)}"
        )


def _list_todos_from_db(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    tag: Optional[str] = None,
) -> List["Todo"]:
    """List todos from database with optional filters."""
    db = _get_todo_database()
    if not db or not _use_database:
        return []

    try:
        query = "SELECT * FROM todos WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)
        if priority:
            query += " AND priority = ?"
            params.append(priority)
        if category:
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY "
        # Priority order: urgent > high > medium > low
        query += "CASE priority WHEN 'urgent' THEN 0 WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 ELSE 99 END, created_at"

        if isinstance(db, sqlite3.Connection):
            # Direct SQLite
            cursor = db.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            todos = [_row_to_todo(dict(row)) for row in rows]
        else:
            # DatabaseQueryOptimizer
            results = db.execute_query(query, parameters=tuple(params), use_cache=True)
            todos = [_row_to_todo(row) for row in results]

        # Filter by tag if specified (post-processing since tags are JSON)
        if tag:
            todos = [t for t in todos if tag in (t.tags or [])]

        return todos
    except Exception as e:
        logger.error(f"Failed to list todos from database: {e}")
        return []


def _row_to_todo(row: Dict) -> "Todo":
    """Convert database row to Todo object."""
    tags = json.loads(row.get("tags", "[]")) if row.get("tags") else []
    metadata = json.loads(row.get("metadata", "{}")) if row.get("metadata") else {}

    return Todo(
        todo_id=row["todo_id"],
        title=row["title"],
        description=row.get("description"),
        status=row["status"],
        priority=row["priority"],
        category=row.get("category"),
        tags=tags,
        due_date=row.get("due_date"),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        completed_at=row.get("completed_at"),
        metadata=metadata,
    )


class Todo(BaseModel):
    """Todo item information."""

    todo_id: str
    title: str
    description: Optional[str] = None
    status: str  # pending, in_progress, completed, cancelled
    priority: str  # low, medium, high, urgent
    category: Optional[str] = None
    tags: List[str] = []
    due_date: Optional[str] = None
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
    metadata: Dict[str, str] = {}


class TodoCreateRequest(BaseModel):
    """Request to create a new todo."""

    title: str
    description: Optional[str] = None
    priority: str = "medium"  # low, medium, high, urgent
    category: Optional[str] = None
    tags: List[str] = []
    due_date: Optional[str] = None
    metadata: Dict[str, str] = {}


class TodoUpdateRequest(BaseModel):
    """Request to update a todo."""

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    due_date: Optional[str] = None
    metadata: Dict[str, str] = {}


class TodoResponse(BaseModel):
    """Todo response."""

    todo_id: str
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    category: Optional[str] = None
    tags: List[str] = []
    due_date: Optional[str] = None
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
    metadata: Dict[str, str] = {}


def _generate_todo_id() -> str:
    """Generate a unique todo ID."""
    import uuid

    return f"todo-{uuid.uuid4().hex[:8]}"


@router.get("", response_model=List[TodoResponse])
@cache_response(ttl=30)  # Cache for 30 seconds (todos change moderately)
async def list_todos(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
):
    """List all todos with optional filtering."""
    try:
        todos = _list_todos_from_db(
            status=status, priority=priority, category=category, tag=tag
        )

        return [
            TodoResponse(
                todo_id=todo.todo_id,
                title=todo.title,
                description=todo.description,
                status=todo.status,
                priority=todo.priority,
                category=todo.category,
                tags=todo.tags,
                due_date=todo.due_date,
                created_at=todo.created_at,
                updated_at=todo.updated_at,
                completed_at=todo.completed_at,
                metadata=todo.metadata,
            )
            for todo in todos
        ]
    except Exception as e:
        logger.error(f"Failed to list todos: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list todos: {str(e)}",
        ) from e


@router.get("/{todo_id}", response_model=TodoResponse)
@cache_response(
    ttl=60
)  # Cache for 60 seconds (individual todos change less frequently)
async def get_todo(todo_id: str):
    """Get a specific todo."""
    try:
        todo = _load_todo_from_db(todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail=f"Todo '{todo_id}' not found")

        return TodoResponse(
            todo_id=todo.todo_id,
            title=todo.title,
            description=todo.description,
            status=todo.status,
            priority=todo.priority,
            category=todo.category,
            tags=todo.tags,
            due_date=todo.due_date,
            created_at=todo.created_at,
            updated_at=todo.updated_at,
            completed_at=todo.completed_at,
            metadata=todo.metadata,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get todo: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get todo: {str(e)}",
        ) from e


@router.post("", response_model=TodoResponse)
async def create_todo(request: TodoCreateRequest):
    """Create a new todo."""
    try:
        if not request.title or len(request.title.strip()) == 0:
            raise HTTPException(status_code=400, detail="Title is required")

        if request.priority not in ["low", "medium", "high", "urgent"]:
            raise HTTPException(
                status_code=400,
                detail="Priority must be low, medium, high, or urgent",
            )

        todo_id = _generate_todo_id()
        now = datetime.utcnow().isoformat()

        todo = Todo(
            todo_id=todo_id,
            title=request.title.strip(),
            description=request.description,
            status="pending",
            priority=request.priority,
            category=request.category,
            tags=request.tags or [],
            due_date=request.due_date,
            created_at=now,
            updated_at=now,
            metadata=request.metadata,
        )

        if not _save_todo_to_db(todo):
            raise HTTPException(
                status_code=500,
                detail="Failed to save todo to database",
            )

        logger.info(f"Created todo: {todo_id} - {todo.title}")

        return TodoResponse(
            todo_id=todo.todo_id,
            title=todo.title,
            description=todo.description,
            status=todo.status,
            priority=todo.priority,
            category=todo.category,
            tags=todo.tags,
            due_date=todo.due_date,
            created_at=todo.created_at,
            updated_at=todo.updated_at,
            completed_at=todo.completed_at,
            metadata=todo.metadata,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create todo: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create todo: {str(e)}",
        ) from e


@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(todo_id: str, request: TodoUpdateRequest):
    """Update a todo."""
    try:
        todo = _load_todo_from_db(todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail=f"Todo '{todo_id}' not found")

        if request.title is not None:
            todo.title = request.title.strip()
        if request.description is not None:
            todo.description = request.description
        if request.status is not None:
            if request.status not in [
                "pending",
                "in_progress",
                "completed",
                "cancelled",
            ]:
                raise HTTPException(
                    status_code=400,
                    detail="Status must be pending, in_progress, completed, or cancelled",
                )
            todo.status = request.status
            if request.status == "completed" and not todo.completed_at:
                todo.completed_at = datetime.utcnow().isoformat()
            elif request.status != "completed":
                todo.completed_at = None
        if request.priority is not None:
            if request.priority not in ["low", "medium", "high", "urgent"]:
                raise HTTPException(
                    status_code=400,
                    detail="Priority must be low, medium, high, or urgent",
                )
            todo.priority = request.priority
        if request.category is not None:
            todo.category = request.category
        if request.tags is not None:
            todo.tags = request.tags
        if request.due_date is not None:
            todo.due_date = request.due_date
        if request.metadata:
            todo.metadata.update(request.metadata)

        todo.updated_at = datetime.utcnow().isoformat()

        if not _save_todo_to_db(todo):
            raise HTTPException(
                status_code=500,
                detail="Failed to save todo to database",
            )

        logger.info(f"Updated todo: {todo_id}")

        return TodoResponse(
            todo_id=todo.todo_id,
            title=todo.title,
            description=todo.description,
            status=todo.status,
            priority=todo.priority,
            category=todo.category,
            tags=todo.tags,
            due_date=todo.due_date,
            created_at=todo.created_at,
            updated_at=todo.updated_at,
            completed_at=todo.completed_at,
            metadata=todo.metadata,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update todo: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update todo: {str(e)}",
        ) from e


@router.delete("/{todo_id}")
async def delete_todo(todo_id: str):
    """Delete a todo."""
    try:
        todo = _load_todo_from_db(todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail=f"Todo '{todo_id}' not found")

        if not _delete_todo_from_db(todo_id):
            raise HTTPException(
                status_code=500,
                detail="Failed to delete todo from database",
            )

        logger.info(f"Deleted todo: {todo_id}")

        return {"message": f"Todo '{todo_id}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete todo: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete todo: {str(e)}",
        ) from e


@router.get("/categories/list", response_model=List[str])
@cache_response(ttl=300)  # Cache for 5 minutes (categories are relatively static)
async def list_categories():
    """List all todo categories."""
    try:
        todos = _list_todos_from_db()
        categories = set()
        for todo in todos:
            if todo.category:
                categories.add(todo.category)
        return sorted(list(categories))
    except Exception as e:
        logger.error(f"Failed to list categories: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list categories: {str(e)}",
        ) from e


@router.get("/tags/list", response_model=List[str])
@cache_response(ttl=300)  # Cache for 5 minutes (tags are relatively static)
async def list_tags():
    """List all todo tags."""
    try:
        todos = _list_todos_from_db()
        tags = set()
        for todo in todos:
            tags.update(todo.tags)
        return sorted(list(tags))
    except Exception as e:
        logger.error(f"Failed to list tags: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list tags: {str(e)}",
        ) from e


@router.get("/stats/summary")
@cache_response(ttl=10)  # Cache for 10 seconds (stats change frequently)
async def get_todo_summary():
    """Get todo statistics summary."""
    try:
        todos = _list_todos_from_db()
        total = len(todos)
        by_status = {"pending": 0, "in_progress": 0, "completed": 0, "cancelled": 0}
        by_priority = {"low": 0, "medium": 0, "high": 0, "urgent": 0}

        for todo in todos:
            by_status[todo.status] = by_status.get(todo.status, 0) + 1
            by_priority[todo.priority] = by_priority.get(todo.priority, 0) + 1

        return {
            "total": total,
            "by_status": by_status,
            "by_priority": by_priority,
        }
    except Exception as e:
        logger.error(f"Failed to get todo summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get todo summary: {str(e)}",
        ) from e


@router.get("/export")
@cache_response(ttl=60)  # Cache for 60 seconds (exports are moderately expensive)
async def export_todos(format: str = "json"):
    """
    Export todos to file.

    Args:
        format: Export format (json, csv)

    Returns:
        Exported todos file
    """
    try:
        import csv
        import io

        todos = _list_todos_from_db()

        if format.lower() == "csv":
            output = io.StringIO()
            writer = csv.writer(output)

            # Header
            writer.writerow(
                [
                    "ID",
                    "Title",
                    "Description",
                    "Status",
                    "Priority",
                    "Category",
                    "Tags",
                    "Due Date",
                    "Created At",
                    "Updated At",
                    "Completed At",
                ]
            )

            # Data rows
            for todo in todos:
                writer.writerow(
                    [
                        todo.todo_id,
                        todo.title,
                        todo.description or "",
                        todo.status,
                        todo.priority,
                        todo.category or "",
                        ", ".join(todo.tags),
                        todo.due_date or "",
                        todo.created_at,
                        todo.updated_at,
                        todo.completed_at or "",
                    ]
                )

            from fastapi.responses import Response

            return Response(
                content=output.getvalue(),
                media_type="text/csv",
                headers={
                    "Content-Disposition": ('attachment; filename="todos_export.csv"')
                },
            )
        else:
            # JSON format
            import json

            todos_data = [todo.model_dump() for todo in todos]

            from fastapi.responses import Response

            return Response(
                content=json.dumps(todos_data, indent=2),
                media_type="application/json",
                headers={
                    "Content-Disposition": ('attachment; filename="todos_export.json"')
                },
            )

    except Exception as e:
        logger.error(f"Failed to export todos: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export todos: {str(e)}",
        ) from e
