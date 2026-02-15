"""
Reflexion / self-correction cycle support.

When Skeptical Validator (or any verification step) returns FAIL, the caller
can use build_reflection_prompt(diagnosis) to re-prompt the agent, then
re-run and re-verify. Limit to max_retries (default 3) to avoid infinite loops;
after that, escalate to Overseer.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class ReflexionResult:
    """Result of a verification step for reflexion loop."""

    passed: bool
    diagnosis: str
    attempt: int

    def reflection_prompt(self, max_retries: int = 3) -> str:
        """Build prompt for agent to reflect and retry."""
        return build_reflection_prompt(self.diagnosis, self.attempt, max_retries)

    def should_escalate(self, max_retries: int = 3) -> bool:
        """True if retries exhausted and should escalate to Overseer."""
        return not self.passed and self.attempt >= max_retries


def build_reflection_prompt(diagnosis: str, attempt: int = 1, max_retries: int = 3) -> str:
    """
    Build the reflection prompt for the agent after a failed verification.

    Use this to re-prompt: "Your previous attempt failed because [reason].
    Reflect on what went wrong and try again."
    """
    if not diagnosis:
        diagnosis = "Verification failed (no diagnosis provided)."
    remaining = max(0, max_retries - attempt)
    return (
        f"Your previous attempt failed because: {diagnosis}\n\n"
        "Reflect on what went wrong and try again. "
        f"(Retries remaining: {remaining}. After {max_retries} failures, escalate to Overseer.)"
    )


def run_verification_step(
    verify_fn: Callable[[], tuple[bool, str]],
    attempt: int = 1,
) -> ReflexionResult:
    """
    Run one verification step and return a ReflexionResult.

    verify_fn should return (passed: bool, diagnosis: str).
    Caller is responsible for re-invoking the agent with reflection_prompt
    and calling again with attempt+1 until passed or should_escalate.
    """
    passed, diagnosis = verify_fn()
    return ReflexionResult(passed=passed, diagnosis=diagnosis or "", attempt=attempt)


def should_escalate(attempt: int, max_retries: int = 3) -> bool:
    """True if attempt count has reached max_retries (escalate to Overseer)."""
    return attempt >= max_retries
