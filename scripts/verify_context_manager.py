#!/usr/bin/env python3
"""
Context Manager Verification Script.

Verifies that the context manager is functioning correctly by:
1. Loading configuration
2. Testing all registered source adapters
3. Testing role-specific allocations
4. Checking audit adapter integration
5. Generating a verification report
"""

from _env_setup import PROJECT_ROOT

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


def verify_configuration() -> Tuple[bool, str, Dict[str, Any]]:
    """Verify that context manager configuration loads correctly."""
    config_path = Path("tools/context/config/context-sources.json")
    
    if not config_path.exists():
        return False, f"Configuration file not found: {config_path}", {}
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # Verify required sections exist
        required_sections = ["weights", "budgets"]
        missing = [s for s in required_sections if s not in config]
        
        if missing:
            return False, f"Missing required sections: {missing}", config
        
        return True, "Configuration loaded successfully", config
        
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON in configuration: {e}", {}
    except Exception as e:
        return False, f"Error loading configuration: {e}", {}


def verify_role_configs() -> Tuple[bool, str, List[str]]:
    """Verify all role-specific configurations load correctly."""
    roles_dir = Path("tools/context/config/roles")
    
    if not roles_dir.exists():
        return False, f"Roles directory not found: {roles_dir}", []
    
    role_files = list(roles_dir.glob("*.json"))
    if not role_files:
        return False, "No role configuration files found", []
    
    valid_roles = []
    errors = []
    
    for role_file in role_files:
        try:
            with open(role_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            # Check for required keys
            if "weights" in config or "budgets" in config:
                valid_roles.append(role_file.stem)
            else:
                errors.append(f"{role_file.name}: missing weights/budgets")
                
        except json.JSONDecodeError as e:
            errors.append(f"{role_file.name}: invalid JSON - {e}")
        except Exception as e:
            errors.append(f"{role_file.name}: error - {e}")
    
    if errors:
        return False, f"Errors in role configs: {errors}", valid_roles
    
    return True, f"All {len(valid_roles)} role configs valid", valid_roles


def verify_source_adapters() -> Tuple[bool, str, Dict[str, bool]]:
    """Verify all source adapters can be imported and instantiated."""
    adapter_results: Dict[str, bool] = {}
    errors = []
    
    adapters_to_test = [
        ("state", "tools.context.sources.state_adapter", "StateSourceAdapter"),
        ("task", "tools.context.sources.task_adapter", "TaskSourceAdapter"),
        ("rules", "tools.context.sources.rules_adapter", "RulesSourceAdapter"),
        ("memory", "tools.context.sources.memory_adapter", "MemorySourceAdapter"),
        ("git", "tools.context.sources.git_adapter", "GitSourceAdapter"),
        ("ledger", "tools.context.sources.ledger_adapter", "LedgerSourceAdapter"),
        ("issues", "tools.context.sources.issues_adapter", "IssuesSourceAdapter"),
        ("audit", "tools.context.sources.audit_adapter", "AuditSourceAdapter"),
    ]
    
    for name, module_path, class_name in adapters_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            adapter_class = getattr(module, class_name)
            # Try instantiation
            if name == "audit":
                instance = adapter_class(max_entries=5, hours_lookback=1)
            else:
                instance = adapter_class()
            adapter_results[name] = True
        except Exception as e:
            adapter_results[name] = False
            errors.append(f"{name}: {e}")
    
    passed = all(adapter_results.values())
    
    if not passed:
        return False, f"Adapter failures: {errors}", adapter_results
    
    return True, f"All {len(adapters_to_test)} adapters verified", adapter_results


def verify_registry_build() -> Tuple[bool, str, int]:
    """Verify that the source registry builds correctly."""
    try:
        from tools.context.core.registry import build_default_registry
        
        # Load config
        config_path = Path("tools/context/config/context-sources.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        registry = build_default_registry(config)
        sources = registry.all()
        
        if not sources:
            return False, "Registry built but has no sources", 0
        
        source_names = [s.source_name for s in sources]
        
        # Verify audit adapter is registered
        if "audit" not in source_names:
            return False, f"Audit adapter not registered. Found: {source_names}", len(sources)
        
        return True, f"Registry built with {len(sources)} sources: {source_names}", len(sources)
        
    except Exception as e:
        return False, f"Failed to build registry: {e}", 0


def verify_allocation() -> Tuple[bool, str, Dict[str, Any]]:
    """Verify that context allocation works correctly."""
    try:
        from tools.context.core.manager import ContextManager
        from tools.context.core.models import AllocationContext, ContextLevel
        
        # Create manager
        manager = ContextManager.from_config()
        
        # Test allocation
        context = AllocationContext(
            task_id="TEST-0001",
            phase="Verify",
            role="debug-agent",
            include_git=False,
            budget_chars=5000,
            max_level=ContextLevel.MID,
        )
        
        bundle = manager.allocate(context)
        
        # Check bundle contents
        sources_present = []
        if bundle.task and bundle.task.id is not None:
            sources_present.append("task")
        if bundle.state and bundle.state.phase is not None:
            sources_present.append("state")
        if bundle.brief:
            sources_present.append("brief")
        if bundle.rules:
            sources_present.append("rules")
        if bundle.memory:
            sources_present.append("memory")
        if bundle.git:
            sources_present.append("git")
        if bundle.ledger:
            sources_present.append("ledger")
        
        # Estimate total chars from bundle
        bundle_json = bundle.to_json()
        total_chars = len(bundle_json)
        
        result = {
            "sources_present": sources_present,
            "total_chars": total_chars,
            "has_meta": bool(bundle.meta),
            "role_set": bundle.meta.get("role") == "debug-agent",
        }
        
        if total_chars < 100:
            return False, "Allocation returned minimal content", result
        
        return True, f"Allocation successful: {total_chars} chars, sources: {sources_present}", result
        
    except Exception as e:
        return False, f"Allocation failed: {e}", {}


def verify_audit_adapter() -> Tuple[bool, str, Dict[str, Any]]:
    """Verify that the audit adapter can fetch entries."""
    try:
        from tools.context.sources.audit_adapter import AuditSourceAdapter
        from tools.context.core.models import AllocationContext, ContextLevel
        
        adapter = AuditSourceAdapter(
            max_entries=10,
            severity_filter=["error", "warning", "critical"],
            hours_lookback=24,
        )
        
        context = AllocationContext(
            task_id="TEST-0001",
            phase="Verify",
            role="debug-agent",
            include_git=False,
            budget_chars=5000,
            max_level=ContextLevel.MID,
        )
        
        result = adapter.fetch(context)
        
        info = {
            "success": result.success,
            "size_chars": result.size_chars,
            "fetch_time_ms": round(result.fetch_time_ms, 2),
            "error": result.error,
            "entry_count": len(result.data.get("audit_entries", [])) if result.data else 0,
        }
        
        if not result.success:
            return False, f"Audit adapter fetch failed: {result.error}", info
        
        return True, f"Audit adapter OK: {info['entry_count']} entries in {info['fetch_time_ms']}ms", info
        
    except Exception as e:
        return False, f"Audit adapter verification failed: {e}", {}


def generate_report(results: List[Tuple[str, bool, str, Any]]) -> str:
    """Generate a verification report."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    passed = sum(1 for _, ok, _, _ in results if ok)
    total = len(results)
    
    report = f"""# Context Manager Verification Report

**Generated**: {timestamp}
**Status**: {'PASS' if passed == total else 'FAIL'} ({passed}/{total} checks passed)

## Verification Results

| Check | Status | Details |
|-------|--------|---------|
"""
    
    for name, ok, msg, _ in results:
        status = "PASS" if ok else "FAIL"
        report += f"| {name} | {status} | {msg} |\n"
    
    report += f"""

## Summary

- Configuration: {'OK' if results[0][1] else 'FAIL'}
- Role Configs: {'OK' if results[1][1] else 'FAIL'}
- Source Adapters: {'OK' if results[2][1] else 'FAIL'}
- Registry Build: {'OK' if results[3][1] else 'FAIL'}
- Allocation Test: {'OK' if results[4][1] else 'FAIL'}
- Audit Adapter: {'OK' if results[5][1] else 'FAIL'}

"""
    return report


def main() -> int:
    """Run context manager verification."""
    print("=" * 60)
    print("Context Manager Verification")
    print("=" * 60)
    
    results: List[Tuple[str, bool, str, Any]] = []
    
    # Run verifications
    checks = [
        ("Configuration", verify_configuration),
        ("Role Configs", verify_role_configs),
        ("Source Adapters", verify_source_adapters),
        ("Registry Build", verify_registry_build),
        ("Allocation Test", verify_allocation),
        ("Audit Adapter", verify_audit_adapter),
    ]
    
    for name, check_fn in checks:
        try:
            ok, msg, data = check_fn()
            results.append((name, ok, msg, data))
            status = "PASS" if ok else "FAIL"
            print(f"[{status}] {name}: {msg}")
        except Exception as e:
            results.append((name, False, str(e), {}))
            print(f"[FAIL] {name}: {e}")
    
    print()
    
    # Generate report
    report = generate_report(results)
    
    # Save report
    report_dir = Path(".buildlogs/verification")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    report_path = report_dir / "context_manager_verification.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"Report saved to: {report_path}")
    
    # Overall result
    passed = all(ok for _, ok, _, _ in results)
    
    if passed:
        print("\n[PASS] Context Manager verification complete")
        return 0
    else:
        print("\n[FAIL] Context Manager verification failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
