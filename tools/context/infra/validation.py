from __future__ import annotations

from typing import Any


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float))


def validate_config(config: dict[str, Any]) -> list[str]:
    """Lightweight validation for context config."""
    errors: list[str] = []
    if not isinstance(config, dict):
        return ["Config must be a JSON object."]

    budgets = config.get("budgets", {})
    if not isinstance(budgets, dict):
        errors.append("budgets must be an object.")
    else:
        for k, v in budgets.items():
            if not _is_number(v):
                errors.append(f"budget '{k}' must be numeric.")
            elif v < 0:
                errors.append(f"budget '{k}' must be >= 0.")

    weights = config.get("weights", {})
    if not isinstance(weights, dict):
        errors.append("weights must be an object.")
    else:
        for k, v in weights.items():
            if not _is_number(v):
                errors.append(f"weight '{k}' must be numeric.")

    for section in ("rules", "git", "memory", "ledger", "telemetry", "gitkraken", "issues", "conversation", "notes"):
        if section in config and not isinstance(config.get(section), dict):
            errors.append(f"{section} must be an object.")

    roles = config.get("roles", {})
    if roles and not isinstance(roles, dict):
        errors.append("roles must be an object if present.")

    return errors
