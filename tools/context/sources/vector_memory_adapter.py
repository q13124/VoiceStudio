"""
Vector memory adapter – embedding-based long-term memory via Chroma.

When vector_enabled and chromadb is available, fetches relevant memories by
similarity to the allocation context (task_id, role, phase). Falls back to
empty list when chromadb is not installed or on error (ADR-015, file fallback
remains in MemorySourceAdapter).
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from tools.context.core.models import AllocationContext, MemoryItem, SourceResult
from tools.context.sources.base import BaseSourceAdapter

logger = logging.getLogger(__name__)

# Optional chromadb; avoid hard dependency for context tools
try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    _CHROMA_AVAILABLE = True
except ImportError:
    _CHROMA_AVAILABLE = False

COLLECTION_NAME = "voicestudio_memory"
DEFAULT_TOP_K = 5
EMBEDDING_DIM = 384


def _dummy_embedding(text: str, dimension: int = EMBEDDING_DIM) -> List[float]:
    """Deterministic pseudo-embedding when no embedding model is available."""
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return [((int(h[i : i + 2], 16) / 255.0) - 0.5) for i in range(0, min(dimension * 2, len(h) - 1), 2)][:dimension]


def _get_embedding_function():
    """Default embedding when chromadb is available; else dummy embedding function."""
    if not _CHROMA_AVAILABLE:
        return None
    try:
        from chromadb.utils import embedding_functions
        return embedding_functions.DefaultEmbeddingFunction()
    except Exception:
        return _DummyEmbeddingFunction()


class _DummyEmbeddingFunction:
    """Minimal embedding function for Chroma when no model is available."""

    def __call__(self, input_texts: List[str]) -> List[List[float]]:
        return [_dummy_embedding(t) for t in input_texts]


class VectorMemoryAdapter(BaseSourceAdapter):
    """
    Fetch context from a Chroma vector store (task history, role decisions, patterns).

    Uses persist_directory for local storage. When chromadb or embedding is
    unavailable, returns empty list so MemorySourceAdapter (file) remains the fallback.
    
    Features:
    - Semantic similarity search for memory retrieval
    - Persistent vector storage for long-term memory
    - Health checking for chromadb availability
    """

    def __init__(
        self,
        persist_directory: str = ".cursor/chroma",
        top_k: int = DEFAULT_TOP_K,
        offline: bool = True,
    ):
        super().__init__(source_name="memory", priority=55, offline=offline)
        self._persist_directory = persist_directory
        self._top_k = top_k
        self._client = None
        self._collection = None
        self._ef = _get_embedding_function()
    
    def health_check(self) -> bool:
        """Check if vector memory is available."""
        if not _CHROMA_AVAILABLE:
            return False
        
        try:
            root = Path(__file__).resolve().parents[4]
            client = self._get_client(root)
            return client is not None
        except Exception:
            return False

    def _get_client(self, root: Path) -> Optional[Any]:
        """Lazy-init Chroma client; returns None if chromadb unavailable or error."""
        if not _CHROMA_AVAILABLE:
            return None
        if self._client is not None:
            return self._client
        try:
            path = root / self._persist_directory
            path.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=str(path),
                settings=ChromaSettings(anonymized_telemetry=False),
            )
            return self._client
        except Exception as e:
            logger.debug("Vector memory client init failed: %s", e)
            return None

    def _get_collection(self, root: Path):
        """Get or create collection; uses default or dummy embedding function."""
        if self._collection is not None:
            return self._collection
        client = self._get_client(root)
        if client is None or self._ef is None:
            return None
        try:
            self._collection = client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=self._ef,
                metadata={"description": "VoiceStudio long-term memory"},
            )
            return self._collection
        except Exception as e:
            logger.debug("Vector memory collection init failed: %s", e)
            return None

    def _build_query(self, context: AllocationContext) -> str:
        """Build search query from allocation context."""
        parts = []
        if context.task_id:
            parts.append(f"task {context.task_id}")
        if context.phase:
            parts.append(f"phase {context.phase}")
        if context.role:
            parts.append(f"role {context.role}")
        if not parts:
            return "VoiceStudio project context"
        return " ".join(parts)

    def _query_collection(self, query: str, root: Path) -> List[Dict[str, Any]]:
        """Query Chroma collection; returns list of {content, source} dicts."""
        coll = self._get_collection(root)
        if coll is None:
            return []
        try:
            results = coll.query(
                query_texts=[query],
                n_results=min(self._top_k, 10),
                include=["documents", "metadatas"],
            )
            out = []
            docs = (results.get("documents") or [[]])[0]
            metadatas = (results.get("metadatas") or [[]])[0]
            for i, doc in enumerate(docs or []):
                meta = (metadatas or [{}])[i] if i < len(metadatas or []) else {}
                source = meta.get("source", "vector_memory")
                out.append({"content": doc, "source": source})
            return out
        except Exception as e:
            logger.debug("Vector memory query failed: %s", e)
            return []

    def fetch(self, context: AllocationContext) -> SourceResult:
        """Fetch relevant memories from vector store; empty on unavailability."""

        def _load() -> Dict[str, Any]:
            root = Path(__file__).resolve().parents[4]
            query = self._build_query(context)
            raw = self._query_collection(query, root)
            items = [MemoryItem(content=r["content"], source=r.get("source", "vector_memory")) for r in raw]
            return {"memory": items}

        return self._measure(_load, context)

    def estimate_size(self, context: AllocationContext) -> int:
        """Estimate size of vector fetch (typical top_k snippets)."""
        return self._top_k * 256
    
    def store_memory(
        self,
        content: str,
        memory_id: str,
        source: str = "context",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Store a memory in the vector store.
        
        Args:
            content: Memory content
            memory_id: Unique ID for the memory
            source: Source identifier
            metadata: Additional metadata
        
        Returns:
            True if stored successfully
        """
        if not _CHROMA_AVAILABLE:
            return False
        
        try:
            root = Path(__file__).resolve().parents[4]
            coll = self._get_collection(root)
            if coll is None:
                return False
            
            meta = metadata or {}
            meta["source"] = source
            meta["stored_at"] = __import__("datetime").datetime.now().isoformat()
            
            coll.add(
                documents=[content],
                ids=[memory_id],
                metadatas=[meta],
            )
            
            logger.info("Stored vector memory: %s", memory_id)
            return True
            
        except Exception as e:
            logger.error("Failed to store vector memory: %s", e)
            return False
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory by ID."""
        if not _CHROMA_AVAILABLE:
            return False
        
        try:
            root = Path(__file__).resolve().parents[4]
            coll = self._get_collection(root)
            if coll is None:
                return False
            
            coll.delete(ids=[memory_id])
            return True
            
        except Exception:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        if not _CHROMA_AVAILABLE:
            return {"available": False}
        
        try:
            root = Path(__file__).resolve().parents[4]
            coll = self._get_collection(root)
            if coll is None:
                return {"available": False}
            
            return {
                "available": True,
                "collection": COLLECTION_NAME,
                "count": coll.count(),
                "persist_directory": self._persist_directory,
            }
            
        except Exception as e:
            return {"available": False, "error": str(e)}
