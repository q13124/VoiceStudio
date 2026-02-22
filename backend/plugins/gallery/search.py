"""
Plugin Search Engine.

Phase 5C M2: Full-text search with relevance ranking and filtering.
Provides local-first search capabilities without requiring external search services.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

from .models import CatalogPlugin, PluginStats

logger = logging.getLogger(__name__)


class SortField(Enum):
    """Available sort fields."""

    RELEVANCE = "relevance"
    NAME = "name"
    RATING = "rating"
    DOWNLOADS = "downloads"
    DATE = "date"


class SortOrder(Enum):
    """Sort order."""

    ASC = "asc"
    DESC = "desc"


@dataclass
class SearchFilter:
    """
    Search filter criteria.

    Supports filtering by multiple attributes with AND logic.
    """

    categories: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    authors: list[str] = field(default_factory=list)
    licenses: list[str] = field(default_factory=list)
    min_rating: float = 0.0
    max_rating: float = 5.0
    min_downloads: int = 0
    verified_only: bool = False
    featured_only: bool = False
    has_versions: bool = True  # Only plugins with at least one version

    def matches(self, plugin: CatalogPlugin) -> bool:
        """Check if plugin matches filter criteria."""
        # Category filter
        if self.categories and plugin.category not in self.categories:
            return False

        # Tag filter (any match)
        if self.tags and not any(tag in plugin.tags for tag in self.tags):
            return False

        # Author filter
        if self.authors and plugin.author not in self.authors:
            return False

        # License filter
        if self.licenses and plugin.license not in self.licenses:
            return False

        # Rating filter
        if not (self.min_rating <= plugin.stats.rating <= self.max_rating):
            return False

        # Downloads filter
        if plugin.stats.downloads < self.min_downloads:
            return False

        # Verified filter
        if self.verified_only and not plugin.verified:
            return False

        # Featured filter
        if self.featured_only and not plugin.featured:
            return False

        # Has versions filter
        return not (self.has_versions and not plugin.versions)


@dataclass
class SearchResult:
    """Search result with relevance score."""

    plugin: CatalogPlugin
    score: float
    highlights: dict[str, list[str]] = field(default_factory=dict)
    matched_fields: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "plugin": self.plugin.to_dict(),
            "score": self.score,
            "highlights": self.highlights,
            "matched_fields": self.matched_fields,
        }


@dataclass
class SearchQuery:
    """
    Search query with all parameters.

    Supports:
    - Free text query with field boosting
    - Filters for narrowing results
    - Sorting options
    - Pagination
    """

    query: str = ""
    filter: SearchFilter = field(default_factory=SearchFilter)
    sort_by: SortField = SortField.RELEVANCE
    sort_order: SortOrder = SortOrder.DESC
    offset: int = 0
    limit: int = 20

    def __post_init__(self) -> None:
        """Validate query parameters."""
        if self.offset < 0:
            self.offset = 0
        if self.limit < 1:
            self.limit = 1
        if self.limit > 100:
            self.limit = 100


@dataclass
class SearchResponse:
    """Search response with pagination info."""

    results: list[SearchResult]
    total: int
    offset: int
    limit: int
    query: str
    facets: dict[str, list[dict[str, Any]]] = field(default_factory=dict)

    @property
    def has_more(self) -> bool:
        """Check if more results are available."""
        return self.offset + len(self.results) < self.total

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "results": [r.to_dict() for r in self.results],
            "total": self.total,
            "offset": self.offset,
            "limit": self.limit,
            "query": self.query,
            "has_more": self.has_more,
            "facets": self.facets,
        }


class PluginSearchEngine:
    """
    Full-text search engine for plugins.

    Implements local-first search with:
    - TF-IDF-like relevance scoring
    - Field-specific boosting
    - Fuzzy matching for typos
    - Faceted search support
    """

    # Field weights for relevance scoring
    FIELD_WEIGHTS = {
        "name": 5.0,
        "id": 3.0,
        "tags": 2.5,
        "description": 1.5,
        "category": 1.0,
        "author": 1.0,
    }

    def __init__(self) -> None:
        """Initialize search engine."""
        self._index: dict[str, list[tuple[CatalogPlugin, str, float]]] = {}
        self._plugins: list[CatalogPlugin] = []

    def index_plugins(self, plugins: list[CatalogPlugin]) -> None:
        """
        Build search index from plugin list.

        Args:
            plugins: List of plugins to index
        """
        self._plugins = plugins
        self._index.clear()

        for plugin in plugins:
            self._index_plugin(plugin)

        logger.info(f"Indexed {len(plugins)} plugins with {len(self._index)} terms")

    def _index_plugin(self, plugin: CatalogPlugin) -> None:
        """Index a single plugin."""
        # Index each field with its weight
        self._index_field(plugin, "name", plugin.name, self.FIELD_WEIGHTS["name"])
        self._index_field(plugin, "id", plugin.id, self.FIELD_WEIGHTS["id"])
        self._index_field(
            plugin, "description", plugin.description, self.FIELD_WEIGHTS["description"]
        )
        self._index_field(plugin, "category", plugin.category, self.FIELD_WEIGHTS["category"])
        self._index_field(plugin, "author", plugin.author, self.FIELD_WEIGHTS["author"])

        # Index tags
        for tag in plugin.tags:
            self._index_field(plugin, "tags", tag, self.FIELD_WEIGHTS["tags"])

    def _index_field(self, plugin: CatalogPlugin, field: str, text: str, weight: float) -> None:
        """Index terms from a field."""
        if not text:
            return

        terms = self._tokenize(text)
        for term in terms:
            if term not in self._index:
                self._index[term] = []
            self._index[term].append((plugin, field, weight))

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize text into searchable terms."""
        # Lowercase and split on non-alphanumeric
        text = text.lower()
        # Split on whitespace and punctuation
        tokens = re.split(r"[\s\-_.,;:!?\"'()\[\]{}]+", text)
        # Filter empty and very short tokens
        return [t for t in tokens if len(t) >= 2]

    def search(self, query: SearchQuery) -> SearchResponse:
        """
        Execute search query.

        Args:
            query: Search query parameters

        Returns:
            Search response with results
        """
        # Start with all plugins if no query text
        if not query.query.strip():
            filtered = [p for p in self._plugins if query.filter.matches(p)]
            results = [
                SearchResult(plugin=p, score=1.0, matched_fields=[], highlights={})
                for p in filtered
            ]
        else:
            # Perform text search
            results = self._text_search(query.query)

            # Apply filters
            results = [r for r in results if query.filter.matches(r.plugin)]

        # Calculate facets before pagination
        facets = self._calculate_facets(results)

        total = len(results)

        # Sort results
        results = self._sort_results(results, query.sort_by, query.sort_order)

        # Apply pagination
        paginated = results[query.offset : query.offset + query.limit]

        return SearchResponse(
            results=paginated,
            total=total,
            offset=query.offset,
            limit=query.limit,
            query=query.query,
            facets=facets,
        )

    def _text_search(self, query_text: str) -> list[SearchResult]:
        """Perform text search with relevance scoring."""
        query_terms = self._tokenize(query_text)
        if not query_terms:
            return []

        # Accumulate scores for each plugin
        plugin_scores: dict[str, float] = {}
        plugin_fields: dict[str, set[str]] = {}
        plugin_highlights: dict[str, dict[str, list[str]]] = {}

        for term in query_terms:
            # Exact match
            if term in self._index:
                for plugin, field, weight in self._index[term]:
                    pid = plugin.id
                    if pid not in plugin_scores:
                        plugin_scores[pid] = 0.0
                        plugin_fields[pid] = set()
                        plugin_highlights[pid] = {}

                    plugin_scores[pid] += weight
                    plugin_fields[pid].add(field)

                    # Store highlight
                    if field not in plugin_highlights[pid]:
                        plugin_highlights[pid][field] = []
                    plugin_highlights[pid][field].append(term)

            # Prefix match for fuzzy search
            for indexed_term in self._index:
                if indexed_term.startswith(term) and indexed_term != term:
                    for plugin, field, weight in self._index[indexed_term]:
                        pid = plugin.id
                        if pid not in plugin_scores:
                            plugin_scores[pid] = 0.0
                            plugin_fields[pid] = set()
                            plugin_highlights[pid] = {}

                        # Prefix matches get reduced weight
                        plugin_scores[pid] += weight * 0.5
                        plugin_fields[pid].add(field)

        # Build results
        results = []
        plugin_map = {p.id: p for p in self._plugins}

        for pid, score in plugin_scores.items():
            if pid in plugin_map:
                results.append(
                    SearchResult(
                        plugin=plugin_map[pid],
                        score=score,
                        matched_fields=list(plugin_fields.get(pid, [])),
                        highlights=plugin_highlights.get(pid, {}),
                    )
                )

        return results

    def _sort_results(
        self,
        results: list[SearchResult],
        sort_by: SortField,
        sort_order: SortOrder,
    ) -> list[SearchResult]:
        """Sort search results."""
        reverse = sort_order == SortOrder.DESC

        key_funcs: dict[SortField, Callable[[SearchResult], Any]] = {
            SortField.RELEVANCE: lambda r: r.score,
            SortField.NAME: lambda r: r.plugin.name.lower(),
            SortField.RATING: lambda r: r.plugin.stats.rating,
            SortField.DOWNLOADS: lambda r: r.plugin.stats.downloads,
            SortField.DATE: lambda r: (
                r.plugin.latest_version.release_date if r.plugin.latest_version else ""
            ),
        }

        key_func = key_funcs.get(sort_by, key_funcs[SortField.RELEVANCE])

        # Name should be ascending by default
        if sort_by == SortField.NAME:
            reverse = sort_order == SortOrder.DESC

        return sorted(results, key=key_func, reverse=reverse)

    def _calculate_facets(self, results: list[SearchResult]) -> dict[str, list[dict[str, Any]]]:
        """Calculate facet counts for filtering UI."""
        category_counts: dict[str, int] = {}
        tag_counts: dict[str, int] = {}
        author_counts: dict[str, int] = {}
        license_counts: dict[str, int] = {}

        for result in results:
            plugin = result.plugin

            # Category facet
            if plugin.category:
                category_counts[plugin.category] = category_counts.get(plugin.category, 0) + 1

            # Tag facets
            for tag in plugin.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

            # Author facet
            if plugin.author:
                author_counts[plugin.author] = author_counts.get(plugin.author, 0) + 1

            # License facet
            if plugin.license:
                license_counts[plugin.license] = license_counts.get(plugin.license, 0) + 1

        return {
            "categories": [
                {"value": k, "count": v}
                for k, v in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
            ],
            "tags": [
                {"value": k, "count": v}
                for k, v in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
            ][
                :20
            ],  # Top 20 tags
            "authors": [
                {"value": k, "count": v}
                for k, v in sorted(author_counts.items(), key=lambda x: x[1], reverse=True)
            ][
                :10
            ],  # Top 10 authors
            "licenses": [
                {"value": k, "count": v}
                for k, v in sorted(license_counts.items(), key=lambda x: x[1], reverse=True)
            ],
        }

    def suggest(self, prefix: str, limit: int = 10) -> list[str]:
        """
        Get search suggestions based on prefix.

        Args:
            prefix: Search prefix
            limit: Maximum suggestions

        Returns:
            List of suggested search terms
        """
        if len(prefix) < 2:
            return []

        prefix_lower = prefix.lower()
        suggestions: list[tuple[str, int]] = []

        # Find matching terms from index
        for term in self._index:
            if term.startswith(prefix_lower):
                # Weight by number of plugins containing this term
                count = len(self._index[term])
                suggestions.append((term, count))

        # Sort by count and return top suggestions
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in suggestions[:limit]]


# Module-level convenience functions
_search_engine: Optional[PluginSearchEngine] = None


def get_search_engine() -> PluginSearchEngine:
    """Get or create the global search engine."""
    global _search_engine
    if _search_engine is None:
        _search_engine = PluginSearchEngine()
    return _search_engine


def search_plugins(
    query: str,
    filter: Optional[SearchFilter] = None,
    sort_by: SortField = SortField.RELEVANCE,
    sort_order: SortOrder = SortOrder.DESC,
    offset: int = 0,
    limit: int = 20,
) -> SearchResponse:
    """
    Search plugins with the global engine.

    Args:
        query: Search query text
        filter: Optional filter criteria
        sort_by: Sort field
        sort_order: Sort direction
        offset: Pagination offset
        limit: Maximum results

    Returns:
        Search response
    """
    engine = get_search_engine()
    search_query = SearchQuery(
        query=query,
        filter=filter or SearchFilter(),
        sort_by=sort_by,
        sort_order=sort_order,
        offset=offset,
        limit=limit,
    )
    return engine.search(search_query)
