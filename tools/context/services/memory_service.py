"""
Unified Memory Service - Single interface for all memory operations.

Combines file-based (openmemory.md) and vector-based (Chroma) memory
with role-aware retrieval and automatic storage.

ADR-015 compliant: Falls back gracefully when services unavailable.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from tools.context.core.models import AllocationContext, MemoryItem
from tools.context.sources.memory_adapter import MemorySourceAdapter
from tools.context.sources.vector_memory_adapter import VectorMemoryAdapter

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """A memory entry with metadata."""
    
    content: str
    title: str
    memory_type: str = "project_info"
    source: str = "unknown"
    relevance: float = 0.5
    created_at: str = ""
    role: Optional[str] = None
    task_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "title": self.title,
            "memory_type": self.memory_type,
            "source": self.source,
            "relevance": self.relevance,
            "created_at": self.created_at,
            "role": self.role,
            "task_id": self.task_id,
        }


@dataclass
class MemorySearchResult:
    """Result of a memory search."""
    
    memories: List[MemoryEntry] = field(default_factory=list)
    total_found: int = 0
    search_time_ms: float = 0.0
    sources_queried: List[str] = field(default_factory=list)


class MemoryService:
    """
    Unified memory service for VoiceStudio context system.
    
    Features:
    - Role-aware memory retrieval
    - Dual-store support (file + vector)
    - Automatic fallback when stores unavailable
    - Memory persistence and retrieval
    - Health monitoring
    """
    
    def __init__(
        self,
        file_adapter: Optional[MemorySourceAdapter] = None,
        vector_adapter: Optional[VectorMemoryAdapter] = None,
        prefer_vector: bool = False,
    ):
        """
        Initialize memory service.
        
        Args:
            file_adapter: File-based memory adapter
            vector_adapter: Vector memory adapter
            prefer_vector: Prefer vector results over file results
        """
        self._file_adapter = file_adapter or MemorySourceAdapter(offline=True)
        self._vector_adapter = vector_adapter or VectorMemoryAdapter(offline=True)
        self._prefer_vector = prefer_vector
    
    def search(
        self,
        query: Optional[str] = None,
        role: Optional[str] = None,
        task_id: Optional[str] = None,
        phase: Optional[str] = None,
        max_results: int = 5,
        include_vector: bool = True,
    ) -> MemorySearchResult:
        """
        Search memories with optional role context.
        
        Args:
            query: Search query (optional)
            role: Role for context-aware retrieval
            task_id: Task ID for context
            phase: Phase for context
            max_results: Maximum results to return
            include_vector: Include vector search results
        
        Returns:
            MemorySearchResult with found memories
        """
        import time
        start = time.time()
        
        # Build allocation context
        ctx = AllocationContext(
            task_id=task_id,
            phase=phase,
            role=role,
            include_git=False,
            budget_chars=10000,
        )
        
        memories = []
        sources = []
        
        # Fetch from file adapter
        try:
            file_result = self._file_adapter.fetch(ctx)
            if file_result.success and file_result.data:
                file_memories = file_result.data.get("memory", [])
                for mem in file_memories:
                    if isinstance(mem, MemoryItem):
                        memories.append(MemoryEntry(
                            content=mem.content,
                            title=f"Memory from {mem.source}",
                            source=mem.source or "openmemory",
                            memory_type="file",
                        ))
                sources.append("file")
        except Exception as e:
            logger.debug("File memory search failed: %s", e)
        
        # Fetch from vector adapter if enabled
        if include_vector:
            try:
                vec_result = self._vector_adapter.fetch(ctx)
                if vec_result.success and vec_result.data:
                    vec_memories = vec_result.data.get("memory", [])
                    for mem in vec_memories:
                        if isinstance(mem, MemoryItem):
                            memories.append(MemoryEntry(
                                content=mem.content,
                                title=f"Vector memory",
                                source=mem.source or "vector",
                                memory_type="vector",
                            ))
                    sources.append("vector")
            except Exception as e:
                logger.debug("Vector memory search failed: %s", e)
        
        # Sort by relevance and limit
        memories = sorted(
            memories,
            key=lambda m: m.relevance,
            reverse=True,
        )[:max_results]
        
        elapsed = (time.time() - start) * 1000
        
        return MemorySearchResult(
            memories=memories,
            total_found=len(memories),
            search_time_ms=elapsed,
            sources_queried=sources,
        )
    
    def store(
        self,
        content: str,
        title: str,
        memory_type: str = "project_info",
        role: Optional[str] = None,
        task_id: Optional[str] = None,
        persist_to_vector: bool = False,
    ) -> bool:
        """
        Store a memory.
        
        Args:
            content: Memory content
            title: Memory title
            memory_type: Type (component, implementation, debug, etc.)
            role: Associated role
            task_id: Associated task
            persist_to_vector: Also store in vector database
        
        Returns:
            True if stored successfully
        """
        success = False
        
        # Store to file
        try:
            section = self._get_section_for_role(role, memory_type)
            success = self._file_adapter.store_memory(
                content=content,
                title=title,
                memory_type=memory_type,
                section=section,
            )
        except Exception as e:
            logger.error("Failed to store to file: %s", e)
        
        # Optionally store to vector
        if persist_to_vector:
            try:
                memory_id = f"{memory_type}_{title.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                vec_success = self._vector_adapter.store_memory(
                    content=content,
                    memory_id=memory_id,
                    source=f"role:{role}" if role else "manual",
                    metadata={
                        "title": title,
                        "memory_type": memory_type,
                        "role": role,
                        "task_id": task_id,
                    },
                )
                success = success or vec_success
            except Exception as e:
                logger.error("Failed to store to vector: %s", e)
        
        return success
    
    def _get_section_for_role(
        self,
        role: Optional[str],
        memory_type: str,
    ) -> Optional[str]:
        """Determine openmemory.md section based on role and type."""
        if role:
            role_sections = {
                "system-architect": "Architecture",
                "build-tooling": "Components",
                "ui-engineer": "Components",
                "engine-engineer": "Components",
                "debug-agent": "Debug History",
            }
            if role in role_sections:
                return role_sections[role]
        
        return None  # Use default based on memory_type
    
    def get_health(self) -> Dict[str, Any]:
        """Get health status of memory sources."""
        return {
            "file_available": self._file_adapter.health_check(),
            "vector_available": self._vector_adapter.health_check(),
            "vector_stats": self._vector_adapter.get_stats(),
        }
    
    def get_role_context(
        self,
        role: str,
        max_results: int = 3,
    ) -> List[MemoryEntry]:
        """
        Get memories specifically relevant to a role.
        
        Shortcut for search with role context.
        """
        result = self.search(
            role=role,
            max_results=max_results,
            include_vector=True,
        )
        return result.memories


# Global memory service instance
_global_service: Optional[MemoryService] = None


def get_memory_service() -> MemoryService:
    """Get or create global memory service."""
    global _global_service
    if _global_service is None:
        _global_service = MemoryService()
    return _global_service


def search_memories(
    query: Optional[str] = None,
    role: Optional[str] = None,
    max_results: int = 5,
) -> List[Dict[str, Any]]:
    """Convenience function to search memories."""
    service = get_memory_service()
    result = service.search(query=query, role=role, max_results=max_results)
    return [m.to_dict() for m in result.memories]


def store_memory(
    content: str,
    title: str,
    memory_type: str = "project_info",
) -> bool:
    """Convenience function to store a memory."""
    service = get_memory_service()
    return service.store(content=content, title=title, memory_type=memory_type)
