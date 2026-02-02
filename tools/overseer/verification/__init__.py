# Overseer verification (boundary checks, proof validation, completion guard)
# Lazy import to avoid double-load when running completion_guard as __main__ (-m)

def run_completion_guard():
    """Run the completion guard; import at call time to avoid module conflict."""
    from tools.overseer.verification.completion_guard import run_guard
    return run_guard()

__all__ = ["run_completion_guard"]
