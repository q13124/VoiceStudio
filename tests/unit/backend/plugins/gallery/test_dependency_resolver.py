"""
Unit tests for the dependency resolver module.

Phase 5C M6: Topological dependency resolution and conflict detection.
"""

from __future__ import annotations

import pytest

from backend.plugins.gallery.dependency_resolver import (
    Conflict,
    ConflictType,
    Dependency,
    DependencyResolver,
    ResolutionResult,
    ResolvedDependency,
    Version,
    VersionConstraint,
    VersionOperator,
    VersionSpec,
    check_compatibility,
    get_dependency_resolver,
    resolve_dependencies,
)


class TestVersion:
    """Tests for Version class."""

    def test_parse_simple(self) -> None:
        """Test parsing simple version strings."""
        v = Version.parse("1.2.3")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3
        assert v.prerelease == ""
        assert v.build == ""

    def test_parse_with_v_prefix(self) -> None:
        """Test parsing version with v prefix."""
        v = Version.parse("v2.0.0")
        assert v.major == 2
        assert v.minor == 0
        assert v.patch == 0

    def test_parse_with_prerelease(self) -> None:
        """Test parsing version with prerelease."""
        v = Version.parse("1.0.0-beta.1")
        assert v.major == 1
        assert v.minor == 0
        assert v.patch == 0
        assert v.prerelease == "beta.1"

    def test_parse_with_build(self) -> None:
        """Test parsing version with build metadata."""
        v = Version.parse("1.0.0+build123")
        assert v.major == 1
        assert v.build == "build123"

    def test_parse_full(self) -> None:
        """Test parsing full version string."""
        v = Version.parse("1.2.3-alpha.1+build.456")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3
        assert v.prerelease == "alpha.1"
        assert v.build == "build.456"

    def test_str(self) -> None:
        """Test string conversion."""
        v = Version(1, 2, 3, "beta", "build1")
        assert str(v) == "1.2.3-beta+build1"

        v2 = Version(1, 0, 0)
        assert str(v2) == "1.0.0"

    def test_comparison(self) -> None:
        """Test version comparison."""
        v1 = Version.parse("1.0.0")
        v2 = Version.parse("1.0.1")
        v3 = Version.parse("1.1.0")
        v4 = Version.parse("2.0.0")

        assert v1 < v2 < v3 < v4
        assert v4 > v3 > v2 > v1
        assert v1 == Version.parse("1.0.0")

    def test_prerelease_ordering(self) -> None:
        """Test prerelease versions are lower than release."""
        v1 = Version.parse("1.0.0-alpha")
        v2 = Version.parse("1.0.0-beta")
        v3 = Version.parse("1.0.0")

        # Prerelease is less than release
        assert v1 < v3
        assert v2 < v3
        # Alpha before beta alphabetically
        assert v1 < v2

    def test_hash(self) -> None:
        """Test version hashing."""
        v1 = Version.parse("1.0.0")
        v2 = Version.parse("1.0.0")

        assert hash(v1) == hash(v2)
        assert {v1} == {v2}


class TestVersionConstraint:
    """Tests for VersionConstraint class."""

    def test_parse_exact(self) -> None:
        """Test parsing exact version constraint."""
        c = VersionConstraint.parse("==1.0.0")
        assert c.operator == VersionOperator.EQ
        assert c.version == Version.parse("1.0.0")

    def test_parse_no_operator(self) -> None:
        """Test parsing constraint without operator (exact match)."""
        c = VersionConstraint.parse("1.0.0")
        assert c.operator == VersionOperator.EQ

    def test_parse_gte(self) -> None:
        """Test parsing >= constraint."""
        c = VersionConstraint.parse(">=1.5.0")
        assert c.operator == VersionOperator.GE

    def test_parse_caret(self) -> None:
        """Test parsing caret constraint."""
        c = VersionConstraint.parse("^2.0.0")
        assert c.operator == VersionOperator.CARET

    def test_parse_compatible(self) -> None:
        """Test parsing compatible release constraint."""
        c = VersionConstraint.parse("~=1.2.0")
        assert c.operator == VersionOperator.COMPATIBLE

    def test_satisfies_exact(self) -> None:
        """Test exact match satisfaction."""
        c = VersionConstraint.parse("==1.0.0")
        assert c.satisfies(Version.parse("1.0.0"))
        assert not c.satisfies(Version.parse("1.0.1"))

    def test_satisfies_gte(self) -> None:
        """Test >= satisfaction."""
        c = VersionConstraint.parse(">=1.0.0")
        assert c.satisfies(Version.parse("1.0.0"))
        assert c.satisfies(Version.parse("2.0.0"))
        assert not c.satisfies(Version.parse("0.9.0"))

    def test_satisfies_lt(self) -> None:
        """Test < satisfaction."""
        c = VersionConstraint.parse("<2.0.0")
        assert c.satisfies(Version.parse("1.9.9"))
        assert not c.satisfies(Version.parse("2.0.0"))

    def test_satisfies_caret_major(self) -> None:
        """Test caret constraint with major > 0."""
        c = VersionConstraint.parse("^1.2.3")
        # Same major, >= specified
        assert c.satisfies(Version.parse("1.2.3"))
        assert c.satisfies(Version.parse("1.9.9"))
        # Different major
        assert not c.satisfies(Version.parse("2.0.0"))
        assert not c.satisfies(Version.parse("0.9.0"))

    def test_satisfies_caret_zero(self) -> None:
        """Test caret constraint with major == 0."""
        c = VersionConstraint.parse("^0.2.3")
        # Same major.minor, >= specified
        assert c.satisfies(Version.parse("0.2.3"))
        assert c.satisfies(Version.parse("0.2.9"))
        # Different minor
        assert not c.satisfies(Version.parse("0.3.0"))

    def test_satisfies_compatible(self) -> None:
        """Test compatible release (~=) satisfaction."""
        c = VersionConstraint.parse("~=1.4.2")
        # Same major.minor, patch >= specified
        assert c.satisfies(Version.parse("1.4.2"))
        assert c.satisfies(Version.parse("1.4.9"))
        # Different minor
        assert not c.satisfies(Version.parse("1.5.0"))
        assert not c.satisfies(Version.parse("1.4.1"))


class TestVersionSpec:
    """Tests for VersionSpec class."""

    def test_parse_single(self) -> None:
        """Test parsing single constraint."""
        spec = VersionSpec.parse(">=1.0.0")
        assert len(spec.constraints) == 1

    def test_parse_multiple(self) -> None:
        """Test parsing multiple constraints."""
        spec = VersionSpec.parse(">=1.0.0,<2.0.0")
        assert len(spec.constraints) == 2

    def test_parse_empty(self) -> None:
        """Test parsing empty spec defaults to any."""
        spec = VersionSpec.parse("")
        assert len(spec.constraints) == 1
        assert spec.constraints[0].operator == VersionOperator.GE
        assert spec.constraints[0].version == Version(0, 0, 0)

    def test_satisfies_range(self) -> None:
        """Test version range satisfaction."""
        spec = VersionSpec.parse(">=1.0.0,<2.0.0")

        assert spec.satisfies(Version.parse("1.0.0"))
        assert spec.satisfies(Version.parse("1.9.9"))
        assert not spec.satisfies(Version.parse("0.9.0"))
        assert not spec.satisfies(Version.parse("2.0.0"))

    def test_str(self) -> None:
        """Test string conversion."""
        spec = VersionSpec.parse(">=1.0.0,<2.0.0")
        assert str(spec) == ">=1.0.0,<2.0.0"


class TestDependency:
    """Tests for Dependency class."""

    def test_parse(self) -> None:
        """Test parsing dependency."""
        dep = Dependency.parse("my-plugin", ">=1.0.0")
        assert dep.plugin_id == "my-plugin"
        assert not dep.optional

    def test_parse_optional(self) -> None:
        """Test parsing optional dependency."""
        dep = Dependency.parse("opt-plugin", "^2.0.0", optional=True)
        assert dep.plugin_id == "opt-plugin"
        assert dep.optional

    def test_str(self) -> None:
        """Test string representation."""
        dep = Dependency.parse("plugin", ">=1.0.0")
        assert "plugin" in str(dep)
        assert ">=1.0.0" in str(dep)

        dep_opt = Dependency.parse("plugin", ">=1.0.0", optional=True)
        assert "(optional)" in str(dep_opt)


class TestConflict:
    """Tests for Conflict class."""

    def test_to_dict(self) -> None:
        """Test conflict to_dict."""
        conflict = Conflict(
            conflict_type=ConflictType.VERSION_MISMATCH,
            plugins=["plugin-a", "plugin-b"],
            message="Version conflict",
            suggestions=["Try updating plugin-a"],
        )

        d = conflict.to_dict()
        assert d["type"] == "version_mismatch"
        assert d["plugins"] == ["plugin-a", "plugin-b"]
        assert d["message"] == "Version conflict"
        assert len(d["suggestions"]) == 1


class TestResolvedDependency:
    """Tests for ResolvedDependency class."""

    def test_to_dict(self) -> None:
        """Test resolved dependency to_dict."""
        resolved = ResolvedDependency(
            plugin_id="my-plugin",
            version=Version.parse("1.2.3"),
            required_by=["other-plugin"],
            optional=False,
        )

        d = resolved.to_dict()
        assert d["plugin_id"] == "my-plugin"
        assert d["version"] == "1.2.3"
        assert d["required_by"] == ["other-plugin"]
        assert d["optional"] is False


class TestResolutionResult:
    """Tests for ResolutionResult class."""

    def test_to_dict_success(self) -> None:
        """Test successful result to_dict."""
        result = ResolutionResult(
            success=True,
            resolved=[
                ResolvedDependency("p1", Version.parse("1.0.0")),
                ResolvedDependency("p2", Version.parse("2.0.0")),
            ],
            install_order=["p1", "p2"],
            message="Resolved",
        )

        d = result.to_dict()
        assert d["success"] is True
        assert len(d["resolved"]) == 2
        assert d["install_order"] == ["p1", "p2"]

    def test_to_dict_failure(self) -> None:
        """Test failed result to_dict."""
        result = ResolutionResult(
            success=False,
            conflicts=[
                Conflict(ConflictType.CIRCULAR, ["a", "b"], "Cycle"),
            ],
            message="Failed",
        )

        d = result.to_dict()
        assert d["success"] is False
        assert len(d["conflicts"]) == 1


class TestDependencyResolver:
    """Tests for DependencyResolver class."""

    def test_add_plugin(self) -> None:
        """Test adding a plugin to the resolver."""
        resolver = DependencyResolver()
        resolver.add_plugin("my-plugin", {"dep-a": ">=1.0.0"})

        assert "my-plugin" in resolver._graph
        assert len(resolver._graph["my-plugin"]) == 1

    def test_add_available_version(self) -> None:
        """Test adding available versions."""
        resolver = DependencyResolver()
        resolver.add_available_version("plugin", "1.0.0")
        resolver.add_available_version("plugin", "2.0.0")

        versions = resolver.get_available_versions("plugin")
        assert len(versions) == 2
        # Sorted newest first
        assert versions[0] == Version.parse("2.0.0")

    def test_simple_resolution(self) -> None:
        """Test simple dependency resolution."""
        resolver = DependencyResolver()

        # Plugin A depends on B
        resolver.add_plugin("plugin-a", {"plugin-b": ">=1.0.0"})
        resolver.add_plugin("plugin-b", {})

        # Available versions
        resolver.add_available_version("plugin-b", "1.5.0")

        result = resolver.resolve(["plugin-a"])

        assert result.success
        # plugin-b should be resolved
        resolved_ids = [r.plugin_id for r in result.resolved]
        assert "plugin-b" in resolved_ids

    def test_transitive_resolution(self) -> None:
        """Test transitive dependency resolution."""
        resolver = DependencyResolver()

        # A -> B -> C
        resolver.add_plugin("plugin-a", {"plugin-b": ">=1.0.0"})
        resolver.add_plugin("plugin-b", {"plugin-c": ">=1.0.0"})
        resolver.add_plugin("plugin-c", {})

        resolver.add_available_version("plugin-b", "1.0.0")
        resolver.add_available_version("plugin-c", "1.0.0")

        result = resolver.resolve(["plugin-a"])

        assert result.success
        resolved_ids = [r.plugin_id for r in result.resolved]
        assert "plugin-b" in resolved_ids
        assert "plugin-c" in resolved_ids

    def test_topological_order(self) -> None:
        """Test install order is topological."""
        resolver = DependencyResolver()

        # A -> B -> C (C should be installed first)
        resolver.add_plugin("plugin-a", {"plugin-b": ">=1.0.0"})
        resolver.add_plugin("plugin-b", {"plugin-c": ">=1.0.0"})
        resolver.add_plugin("plugin-c", {})

        resolver.add_available_version("plugin-b", "1.0.0")
        resolver.add_available_version("plugin-c", "1.0.0")

        result = resolver.resolve(["plugin-a"])

        assert result.success
        # C should come before B, B before A
        order = result.install_order
        if "plugin-c" in order and "plugin-b" in order:
            assert order.index("plugin-c") < order.index("plugin-b")
        if "plugin-b" in order and "plugin-a" in order:
            assert order.index("plugin-b") < order.index("plugin-a")

    def test_circular_detection(self) -> None:
        """Test circular dependency detection."""
        resolver = DependencyResolver()

        # A -> B -> A (circular)
        resolver.add_plugin("plugin-a", {"plugin-b": ">=1.0.0"})
        resolver.add_plugin("plugin-b", {"plugin-a": ">=1.0.0"})

        resolver.add_available_version("plugin-a", "1.0.0")
        resolver.add_available_version("plugin-b", "1.0.0")

        result = resolver.resolve(["plugin-a"])

        assert not result.success
        assert any(c.conflict_type == ConflictType.CIRCULAR for c in result.conflicts)

    def test_version_conflict(self) -> None:
        """Test version conflict detection."""
        resolver = DependencyResolver()

        # A requires C>=2.0.0, B requires C<2.0.0
        resolver.add_plugin("plugin-a", {"plugin-c": ">=2.0.0"})
        resolver.add_plugin("plugin-b", {"plugin-c": "<2.0.0"})
        resolver.add_plugin("plugin-c", {})

        # Only version 1.0.0 available (conflicts with A's requirement)
        resolver.add_available_version("plugin-c", "1.0.0")

        result = resolver.resolve(["plugin-a", "plugin-b"])

        assert not result.success
        assert any(c.conflict_type == ConflictType.VERSION_MISMATCH for c in result.conflicts)

    def test_missing_dependency(self) -> None:
        """Test missing dependency detection."""
        resolver = DependencyResolver()

        # A requires B, but B has no available versions
        resolver.add_plugin("plugin-a", {"plugin-b": ">=1.0.0"})

        result = resolver.resolve(["plugin-a"])

        assert not result.success
        assert any(c.conflict_type == ConflictType.MISSING for c in result.conflicts)

    def test_optional_dependencies(self) -> None:
        """Test optional dependency handling."""
        resolver = DependencyResolver()

        resolver.add_plugin(
            "plugin-a",
            {},
            optional_dependencies={"plugin-opt": ">=1.0.0"},
        )
        resolver.add_available_version("plugin-opt", "1.0.0")

        result = resolver.resolve(["plugin-a"])

        assert result.success

    def test_clear(self) -> None:
        """Test clearing resolver state."""
        resolver = DependencyResolver()
        resolver.add_plugin("plugin-a", {})
        resolver.add_available_version("plugin-a", "1.0.0")

        resolver.clear()

        assert len(resolver._graph) == 0
        assert len(resolver._available_versions) == 0


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_get_dependency_resolver(self) -> None:
        """Test singleton getter."""
        r1 = get_dependency_resolver()
        r2 = get_dependency_resolver()
        assert r1 is r2

    def test_resolve_dependencies(self) -> None:
        """Test resolve_dependencies convenience function."""
        plugins = {
            "plugin-a": {"plugin-b": ">=1.0.0"},
            "plugin-b": {},
        }
        available = {
            "plugin-b": ["1.0.0", "2.0.0"],
        }

        result = resolve_dependencies(plugins, available)

        assert result.success

    def test_check_compatibility_true(self) -> None:
        """Test check_compatibility returns True for compatible versions."""
        assert check_compatibility("test", "1.5.0", [">=1.0.0", "<2.0.0"])

    def test_check_compatibility_false(self) -> None:
        """Test check_compatibility returns False for incompatible versions."""
        assert not check_compatibility("test", "2.5.0", [">=1.0.0", "<2.0.0"])


class TestComplexScenarios:
    """Tests for complex resolution scenarios."""

    def test_diamond_dependency(self) -> None:
        """Test diamond dependency pattern."""
        resolver = DependencyResolver()

        # Diamond: A -> B, A -> C, B -> D, C -> D
        resolver.add_plugin(
            "plugin-a",
            {
                "plugin-b": ">=1.0.0",
                "plugin-c": ">=1.0.0",
            },
        )
        resolver.add_plugin("plugin-b", {"plugin-d": ">=1.0.0"})
        resolver.add_plugin("plugin-c", {"plugin-d": ">=1.0.0"})
        resolver.add_plugin("plugin-d", {})

        resolver.add_available_version("plugin-b", "1.0.0")
        resolver.add_available_version("plugin-c", "1.0.0")
        resolver.add_available_version("plugin-d", "1.0.0")

        result = resolver.resolve(["plugin-a"])

        assert result.success
        # D should be resolved once
        d_count = sum(1 for r in result.resolved if r.plugin_id == "plugin-d")
        assert d_count == 1

    def test_version_selection(self) -> None:
        """Test that the best compatible version is selected."""
        resolver = DependencyResolver()

        resolver.add_plugin("plugin-a", {"plugin-b": ">=1.5.0"})
        resolver.add_plugin("plugin-b", {})

        # Multiple versions available
        resolver.add_available_version("plugin-b", "1.0.0")
        resolver.add_available_version("plugin-b", "1.5.0")
        resolver.add_available_version("plugin-b", "2.0.0")

        result = resolver.resolve(["plugin-a"])

        assert result.success
        # Should select 2.0.0 (latest that satisfies)
        b_resolved = next(r for r in result.resolved if r.plugin_id == "plugin-b")
        assert b_resolved.version == Version.parse("2.0.0")

    def test_multiple_constraints_on_same_package(self) -> None:
        """Test multiple constraints on the same dependency."""
        resolver = DependencyResolver()

        # A requires B>=1.0.0, C requires B>=1.5.0,<2.0.0
        resolver.add_plugin("plugin-a", {"plugin-b": ">=1.0.0"})
        resolver.add_plugin("plugin-c", {"plugin-b": ">=1.5.0,<2.0.0"})
        resolver.add_plugin("plugin-b", {})

        resolver.add_available_version("plugin-b", "1.0.0")
        resolver.add_available_version("plugin-b", "1.8.0")
        resolver.add_available_version("plugin-b", "2.0.0")

        result = resolver.resolve(["plugin-a", "plugin-c"])

        assert result.success
        # 1.8.0 satisfies both constraints
        b_resolved = next(r for r in result.resolved if r.plugin_id == "plugin-b")
        assert b_resolved.version == Version.parse("1.8.0")
