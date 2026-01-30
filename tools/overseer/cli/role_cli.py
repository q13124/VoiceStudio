"""
Role CLI - invoke role onboarding + context flow (same as inject_context hook).

Commands:
  invoke <role_id>  Run onboarding and context allocation for a role; print context preamble.
  list              List available role ids and short names.
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "buffer"):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Project root when running as tools.overseer.cli.role_cli
PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _invoke(args: argparse.Namespace) -> int:
    """Run onboarding + context allocation for role_id; print context preamble. Optionally write packet to --output."""
    from tools.onboarding.core.assembler import OnboardingAssembler
    from tools.onboarding.core.role_registry import RoleRegistry
    from tools.context.core.manager import ContextManager
    from tools.context.core.models import AllocationContext

    roles_path = PROJECT_ROOT / "tools" / "onboarding" / "config" / "roles.json"
    context_config_path = PROJECT_ROOT / "tools" / "context" / "config" / "context-sources.json"

    registry = RoleRegistry.from_config(roles_path)
    try:
        resolved_id = registry.resolve_role_id(args.role_id)
        role_config = registry.get_role(resolved_id)
    except ValueError as e:
        sys.stderr.write(f"role invoke: {e}\n")
        return 1

    short_name = role_config.short_name

    # Onboarding packet
    assembler = OnboardingAssembler()
    packet = assembler.assemble(resolved_id, include_full_guide=False)
    packet_md = assembler.render(packet)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(packet_md, encoding="utf-8")

    # Context allocation (same as hook)
    manager = ContextManager.from_config(context_config_path)
    budget = manager.config.get("budgets", {}).get("total_chars", 12000)
    bundle = manager.allocate(
        AllocationContext(
            task_id=None,
            phase=None,
            role=short_name,
            include_git=bool(args.git),
            budget_chars=budget,
        )
    )
    print(bundle.to_preamble_markdown())
    return 0


def _list_roles(args: argparse.Namespace) -> int:
    """List available roles (id, short_name, name)."""
    from tools.onboarding.core.role_registry import RoleRegistry

    roles_path = PROJECT_ROOT / "tools" / "onboarding" / "config" / "roles.json"
    registry = RoleRegistry.from_config(roles_path)
    for role in registry.list_roles():
        print(f"  {role.id}: {role.short_name} ({role.name})")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="overseer role",
        description="Role onboarding and context – same flow as inject_context hook",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    invoke_parser = subparsers.add_parser("invoke", help="Run onboarding + context for a role")
    invoke_parser.add_argument("role_id", help="Role id or alias (0-6, overseer, system-architect, validator, …)")
    invoke_parser.add_argument("--output", "-o", help="Write onboarding packet to this path")
    invoke_parser.add_argument("--git", action="store_true", help="Include git context in allocation")
    invoke_parser.set_defaults(func=_invoke)

    list_parser = subparsers.add_parser("list", help="List available roles")
    list_parser.set_defaults(func=_list_roles)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
