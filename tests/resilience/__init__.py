"""
Resilience Test Suite for VoiceStudio Plugin System.

This package contains comprehensive tests for plugin system resilience,
covering crash recovery, OOM handling, IPC timeouts, and concurrent load.

Test Categories:
- test_crash_recovery: Plugin crash detection and recovery
- test_oom_scenarios: Out-of-memory handling and prevention
- test_ipc_timeout: IPC timeout detection and recovery
- test_concurrent_load: High concurrency and load testing

Running Tests:
    # Run all resilience tests
    pytest tests/resilience/ -v

    # Run specific category
    pytest tests/resilience/ -v -m crash
    pytest tests/resilience/ -v -m oom
    pytest tests/resilience/ -v -m ipc_timeout
    pytest tests/resilience/ -v -m concurrent

    # Run slow tests (may take longer)
    pytest tests/resilience/ -v -m slow
"""
