from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from tools.onboarding.core.assembler import OnboardingAssembler
from tools.onboarding.core.role_registry import RoleRegistry


def _ensure_utf8_stdout() -> None:
    """Ensure stdout can handle UTF-8 for emoji/unicode in prompts."""
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
    # ALLOWED: bare except - Best effort UTF-8 stdout config
    except Exception:
        pass


def _list_roles(registry: RoleRegistry, output_format: str = "text") -> str:
    """List all available roles.
    
    Args:
        registry: Role registry instance
        output_format: "text", "json", or "table"
    
    Returns:
        Formatted role list
    """
    roles = registry.list_roles()
    
    if output_format == "json":
        role_data = []
        for role in roles:
            role_data.append({
                "id": role.id,
                "name": role.name,
                "short_name": role.short_name,
                "prompt_path": role.prompt_path,
                "guide_path": role.guide_path or "",
            })
        return json.dumps(role_data, indent=2)
    
    elif output_format == "table":
        lines = [
            "",
            "Available Roles",
            "=" * 70,
            f"{'ID':<6} {'Short Name':<20} {'Full Name':<40}",
            "-" * 70,
        ]
        for role in sorted(roles, key=lambda r: r.id):
            lines.append(f"{role.id:<6} {role.short_name:<20} {role.name:<40}")
        lines.append("-" * 70)
        lines.append(f"Total: {len(roles)} roles")
        lines.append("")
        return "\n".join(lines)
    
    else:  # text (default)
        lines = ["Available roles:", ""]
        for role in sorted(roles, key=lambda r: r.id):
            short = f" ({role.short_name})" if role.short_name != role.name else ""
            lines.append(f"  [{role.id}] {role.name}{short}")
        lines.append("")
        lines.append(f"Use --role <id|short_name> to generate an onboarding packet.")
        return "\n".join(lines)


def main(argv: Optional[list] = None) -> int:
    _ensure_utf8_stdout()
    
    parser = argparse.ArgumentParser(
        prog="onboard",
        description="Generate onboarding packets or list available roles"
    )
    
    # List mode
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all available roles"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json", "table"],
        default="text",
        help="Output format for --list (default: text)"
    )
    
    # Generate mode
    parser.add_argument(
        "--role", "-r",
        help="Role id or alias (e.g., 4, core-platform)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Write onboarding packet to file"
    )
    parser.add_argument(
        "--full-guide",
        action="store_true",
        help="Include full role guide in packet"
    )
    
    # Cache options
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Bypass cache and regenerate packet"
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear the onboarding cache"
    )
    
    args = parser.parse_args(argv)

    # Handle cache clear
    if args.clear_cache:
        try:
            from tools.onboarding.core.cache import get_cache
            cache = get_cache()
            count = cache.invalidate_all()
            print(f"Cleared {count} cached entries.")
            return 0
        except ImportError:
            print("Cache module not available.", file=sys.stderr)
            return 1

    # Handle list mode
    if args.list:
        registry = RoleRegistry.from_config()
        output = _list_roles(registry, args.format)
        try:
            print(output)
        except UnicodeEncodeError:
            sys.stdout.buffer.write(output.encode('utf-8'))
            sys.stdout.buffer.write(b'\n')
        return 0

    # Generate mode requires --role
    if not args.role:
        parser.error("--role is required (or use --list to see available roles)")

    assembler = OnboardingAssembler()
    
    # Check cache unless bypassed
    packet = None
    if not args.no_cache:
        try:
            from tools.onboarding.core.cache import get_cache
            cache = get_cache()
            packet = cache.get(args.role)
            if packet:
                # Use cached packet
                content = assembler.render(packet)
                _output_content(content, args.output)
                return 0
        except ImportError:
            pass  # Cache not available, proceed without

    # Assemble new packet
    packet = assembler.assemble(args.role, include_full_guide=bool(args.full_guide))
    
    # Cache the result
    if not args.no_cache:
        try:
            from tools.onboarding.core.cache import get_cache
            cache = get_cache()
            cache.set(args.role, packet)
        except ImportError:
            # ALLOWED: bare except - cache module is optional, gracefully degrade
            print("[onboard] Cache module not available, skipping cache storage", file=sys.stderr)

    content = assembler.render(packet)
    _output_content(content, args.output)
    return 0


def _output_content(content: str, output_path: Optional[str]) -> None:
    """Output content to file or stdout."""
    if output_path:
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
    else:
        # Use sys.stdout.buffer for direct UTF-8 output if reconfigure failed
        try:
            print(content)
        except UnicodeEncodeError:
            sys.stdout.buffer.write(content.encode('utf-8'))
            sys.stdout.buffer.write(b'\n')


if __name__ == "__main__":
    sys.exit(main())
