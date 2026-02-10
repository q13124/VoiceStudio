#!/usr/bin/env python3
"""Show role-specific context budget allocation."""

from tools.context.core.manager import ContextManager
from tools.context.core.models import AllocationContext

m = ContextManager.from_config()

for role in ['overseer', 'ui-engineer', 'engine-engineer', 'debug-agent']:
    ctx = AllocationContext(task_id=None, phase=None, role=role, include_git=False, budget_chars=12000)
    budget = m._build_budget(ctx)
    sl = budget.source_limits
    print(f"{role}:")
    print(f"  Priority Order: {budget.priority_order[:5]}")
    print(f"  state={sl.get('state',0)}, brief={sl.get('brief',0)}, ledger={sl.get('ledger',0)}, progress={sl.get('progress',0)}")
    print()
