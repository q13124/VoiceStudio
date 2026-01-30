from __future__ import annotations

import argparse
from datetime import datetime, timedelta

from tools.overseer.agent.approval_manager import ApprovalManager, ApprovalStatus
from tools.overseer.agent.audit_store import AuditStore
from tools.overseer.agent.registry import AgentRegistry


def _list(args: argparse.Namespace) -> int:
    registry = AgentRegistry()
    if args.active_only:
        agents = registry.get_active()
    elif args.state:
        agents = registry.get_by_state(args.state)
    else:
        agents = registry.list_all()
    for agent in agents:
        print(f"{agent.agent_id} | {agent.role.value} | {agent.state.value} | {agent.session_id}")
    return 0


def _stats(args: argparse.Namespace) -> int:
    registry = AgentRegistry()
    agents = registry.list_all()
    by_state = {}
    by_role = {}
    for agent in agents:
        by_state[agent.state.value] = by_state.get(agent.state.value, 0) + 1
        by_role[agent.role.value] = by_role.get(agent.role.value, 0) + 1
    print(f"Total agents: {len(agents)}")
    print("By state:")
    for state, count in sorted(by_state.items()):
        print(f"- {state}: {count}")
    print("By role:")
    for role, count in sorted(by_role.items()):
        print(f"- {role}: {count}")
    return 0


def _approvals(args: argparse.Namespace) -> int:
    manager = ApprovalManager()
    status = ApprovalStatus(args.status) if args.status else None
    history = manager.get_history(
        start_date=datetime.now() - timedelta(days=args.days),
        status=status,
        limit=args.limit,
    )
    for record in history:
        print(
            f"{record.decided_at.isoformat()} | {record.status.value} | {record.agent_id} | {record.tool_name}"
        )
    return 0


def _audit(args: argparse.Namespace) -> int:
    store = AuditStore()
    entries = store.query(limit=args.limit)
    for entry in entries:
        print(
            f"{entry.timestamp.isoformat()} | {entry.agent_id} | {entry.tool_name} | {entry.result}"
        )
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="overseer agent", description="Agent governance CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List agents")
    list_parser.add_argument("--active-only", action="store_true", help="Show only active agents")
    list_parser.add_argument("--state", help="Filter by agent state")
    list_parser.set_defaults(func=_list)

    stats_parser = subparsers.add_parser("stats", help="Show agent stats")
    stats_parser.set_defaults(func=_stats)

    approvals_parser = subparsers.add_parser("approvals", help="List approval history")
    approvals_parser.add_argument("--days", type=int, default=30, help="Look back window in days")
    approvals_parser.add_argument("--status", help="Filter by status (Pending/Approved/Denied/Expired/Cancelled)")
    approvals_parser.add_argument("--limit", type=int, default=50, help="Max records")
    approvals_parser.set_defaults(func=_approvals)

    audit_parser = subparsers.add_parser("audit", help="List audit entries")
    audit_parser.add_argument("--limit", type=int, default=50, help="Max entries")
    audit_parser.set_defaults(func=_audit)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
