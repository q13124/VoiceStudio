"""
Overseer CLI - Main entry point for all Overseer tools.

Usage:
    python -m tools.overseer.cli.main <command> [subcommand] [options]

Commands:
    ledger    - Ledger operations (validate, status, gaps, entry, list)
    gate      - Gate tracking (status, blockers, next, dashboard, export)
    handoff   - Handoff management (validate, reconcile, index, show, create, list)
    report    - Report generation (daily, gate, comprehensive, export)
    agent     - Agent governance (list, stats, approvals, audit)
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    """Main entry point for Overseer CLI."""
    parser = argparse.ArgumentParser(
        prog="overseer",
        description="Overseer governance tools for VoiceStudio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  ledger      Ledger operations
              validate  - Validate all ledger entries
              status    - Show ledger status summary
              gaps      - Find entries with missing information
              entry     - Show details for a specific entry
              list      - List all entry IDs

  gate        Gate tracking
              status    - Show all gate statuses
              blockers  - List blockers for current/specified gate
              next      - Show next actions for gate progression
              dashboard - Generate gate dashboard
              export    - Export gate status as JSON

  handoff     Handoff management
              validate  - Validate all handoff files
              reconcile - Check ledger/handoff alignment
              index     - Generate handoff index
              show      - Show a specific handoff
              create    - Create a new handoff from template
              list      - List all handoffs

  report      Report generation
              daily         - Generate daily status report
              gate          - Generate gate dashboard
              comprehensive - Generate full project status report
              export        - Export status as JSON

  agent       Agent governance
              list      - List agents
              stats     - Show agent registry stats
              approvals - List approval history
              audit     - Show audit entries

  issues      Issue logging and recommendations (Overseer review)
              query     - Query issues with filters (severity, status, instance-type)

  role        Role onboarding + context (same flow as inject_context hook)
              invoke <role_id> - Run onboarding and context for a role
              list      - List available role ids

  debug       Debug workflows (Debug Agent - Role 7)
              scan      - Run proactive scan for issues
              triage    - Triage new/acknowledged issues
              analyze   - Analyze specific issue with deep context
              validate  - Validate fix for issue

Examples:
  python -m tools.overseer.cli.main ledger status
  python -m tools.overseer.cli.main gate status
  python -m tools.overseer.cli.main handoff reconcile
  python -m tools.overseer.cli.main report daily --print
""",
    )

    parser.add_argument(
        "command",
        choices=["ledger", "gate", "handoff", "report", "agent", "issues", "role", "debug"],
        nargs="?",
        help="Command category",
    )
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Command arguments",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="Overseer Tools v1.0.0",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Import and run the appropriate CLI
    if args.command == "ledger":
        from tools.overseer.cli.ledger_cli import main as ledger_main
        return ledger_main(args.args)

    elif args.command == "gate":
        from tools.overseer.cli.gate_cli import main as gate_main
        return gate_main(args.args)

    elif args.command == "handoff":
        from tools.overseer.cli.handoff_cli import main as handoff_main
        return handoff_main(args.args)

    elif args.command == "report":
        from tools.overseer.cli.report_cli import main as report_main
        return report_main(args.args)

    elif args.command == "agent":
        from tools.overseer.cli.agent_cli import main as agent_main
        return agent_main(args.args)

    elif args.command == "issues":
        from tools.overseer.cli.issues_cli import main as issues_main
        return issues_main(args.args)

    elif args.command == "role":
        from tools.overseer.cli.role_cli import main as role_main
        return role_main(args.args)

    elif args.command == "debug":
        from tools.overseer.cli.debug_cli import main as debug_main
        return debug_main(args.args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
