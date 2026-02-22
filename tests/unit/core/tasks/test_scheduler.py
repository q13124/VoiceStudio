"""
Unit Tests for Background Task Scheduler
Tests background task scheduling functionality including optimizations.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the scheduler module
try:
    from app.core.tasks.scheduler import (
        BackgroundTaskScheduler,
        Task,
        TaskPriority,
        TaskStatus,
        get_scheduler,
    )
except ImportError:
    pytest.skip("Could not import scheduler module", allow_module_level=True)


class TestSchedulerImports:
    """Test scheduler module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        from app.core.tasks import scheduler

        assert scheduler is not None, "Failed to import scheduler module"

    def test_scheduler_class_exists(self):
        """Test BackgroundTaskScheduler class exists."""
        assert BackgroundTaskScheduler is not None
        assert isinstance(BackgroundTaskScheduler, type)

    def test_task_class_exists(self):
        """Test Task dataclass exists."""
        assert Task is not None

    def test_task_priority_enum_exists(self):
        """Test TaskPriority enum exists."""
        assert TaskPriority is not None
        assert TaskPriority.LOW.value == 1
        assert TaskPriority.NORMAL.value == 2
        assert TaskPriority.HIGH.value == 3
        assert TaskPriority.CRITICAL.value == 4

    def test_task_status_enum_exists(self):
        """Test TaskStatus enum exists."""
        assert TaskStatus is not None
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"


class TestSchedulerClass:
    """Test BackgroundTaskScheduler class."""

    def test_scheduler_initialization(self):
        """Test scheduler can be initialized."""
        scheduler = BackgroundTaskScheduler()

        assert scheduler is not None
        assert scheduler._max_concurrent_tasks > 0
        assert scheduler._check_interval > 0

    def test_scheduler_initialization_with_custom_params(self):
        """Test scheduler can be initialized with custom parameters."""
        scheduler = BackgroundTaskScheduler(max_concurrent_tasks=5, check_interval=2.0)

        assert scheduler._max_concurrent_tasks == 5
        assert scheduler._check_interval == 2.0

    def test_add_task_immediate(self):
        """Test adding an immediate task."""
        scheduler = BackgroundTaskScheduler()

        def test_func():
            return "test_result"

        task_id = scheduler.add_task(
            name="Test Task",
            func=test_func,
            priority=TaskPriority.NORMAL,
        )

        assert task_id is not None
        assert task_id in scheduler._tasks
        task = scheduler._tasks[task_id]
        assert task.name == "Test Task"
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.NORMAL

    def test_add_task_scheduled(self):
        """Test adding a scheduled task."""
        scheduler = BackgroundTaskScheduler()

        def test_func():
            return "test_result"

        scheduled_time = datetime.now() + timedelta(seconds=10)
        task_id = scheduler.add_task(
            name="Scheduled Task",
            func=test_func,
            scheduled_at=scheduled_time,
            priority=TaskPriority.HIGH,
        )

        assert task_id is not None
        task = scheduler._tasks[task_id]
        assert task.scheduled_at == scheduled_time
        assert task.priority == TaskPriority.HIGH

    def test_add_task_periodic(self):
        """Test adding a periodic task."""
        scheduler = BackgroundTaskScheduler()

        def test_func():
            return "test_result"

        task_id = scheduler.add_task(
            name="Periodic Task",
            func=test_func,
            interval=60.0,
            priority=TaskPriority.LOW,
        )

        assert task_id is not None
        task = scheduler._tasks[task_id]
        assert task.interval == 60.0
        assert task.interval is not None

    def test_add_task_with_args_kwargs(self):
        """Test adding a task with arguments."""
        scheduler = BackgroundTaskScheduler()

        def test_func(arg1, arg2, kwarg1=None):
            return f"{arg1}-{arg2}-{kwarg1}"

        task_id = scheduler.add_task(
            "Task with Args",
            test_func,
            "arg1",
            "arg2",
            kwarg1="kwarg_value",
        )

        assert task_id is not None
        task = scheduler._tasks[task_id]
        assert task.args == ("arg1", "arg2")
        assert task.kwargs == {"kwarg1": "kwarg_value"}

    def test_remove_task(self):
        """Test removing a task."""
        scheduler = BackgroundTaskScheduler()

        def test_func():
            return "test_result"

        task_id = scheduler.add_task(name="Test Task", func=test_func)
        result = scheduler.remove_task(task_id)

        assert result is True
        assert task_id not in scheduler._tasks

    def test_remove_task_not_found(self):
        """Test removing a non-existent task."""
        scheduler = BackgroundTaskScheduler()
        result = scheduler.remove_task("nonexistent_task")

        assert result is False

    def test_cancel_task(self):
        """Test cancelling a task."""
        scheduler = BackgroundTaskScheduler()

        def test_func():
            return "test_result"

        task_id = scheduler.add_task(name="Test Task", func=test_func)
        result = scheduler.cancel_task(task_id)

        assert result is True
        task = scheduler._tasks[task_id]
        assert task.status == TaskStatus.CANCELLED

    def test_cancel_task_not_found(self):
        """Test cancelling a non-existent task."""
        scheduler = BackgroundTaskScheduler()
        result = scheduler.cancel_task("nonexistent_task")

        assert result is False

    def test_get_task(self):
        """Test getting a task."""
        scheduler = BackgroundTaskScheduler()

        def test_func():
            return "test_result"

        task_id = scheduler.add_task(name="Test Task", func=test_func)
        task = scheduler.get_task(task_id)

        assert task is not None
        assert task.id == task_id
        assert task.name == "Test Task"

    def test_get_task_not_found(self):
        """Test getting a non-existent task."""
        scheduler = BackgroundTaskScheduler()
        task = scheduler.get_task("nonexistent_task")

        assert task is None

    def test_list_tasks(self):
        """Test listing tasks."""
        scheduler = BackgroundTaskScheduler()

        def test_func():
            return "test_result"

        scheduler.add_task(name="Task 1", func=test_func, priority=TaskPriority.HIGH)
        scheduler.add_task(name="Task 2", func=test_func, priority=TaskPriority.LOW)

        tasks = scheduler.list_tasks()

        assert len(tasks) == 2
        assert all(isinstance(task, Task) for task in tasks)

    def test_list_tasks_filtered_by_status(self):
        """Test listing tasks filtered by status."""
        scheduler = BackgroundTaskScheduler()

        def test_func():
            return "test_result"

        task1_id = scheduler.add_task(name="Task 1", func=test_func, priority=TaskPriority.HIGH)
        scheduler.add_task(name="Task 2", func=test_func, priority=TaskPriority.LOW)

        # Cancel one task
        scheduler.cancel_task(task1_id)

        tasks = scheduler.list_tasks(status=TaskStatus.CANCELLED)

        assert len(tasks) == 1
        assert tasks[0].status == TaskStatus.CANCELLED

    def test_list_tasks_filtered_by_priority(self):
        """Test listing tasks filtered by priority."""
        scheduler = BackgroundTaskScheduler()

        def test_func():
            return "test_result"

        scheduler.add_task(name="Task 1", func=test_func, priority=TaskPriority.HIGH)
        scheduler.add_task(name="Task 2", func=test_func, priority=TaskPriority.LOW)

        tasks = scheduler.list_tasks(priority=TaskPriority.HIGH)

        assert len(tasks) == 1
        assert tasks[0].priority == TaskPriority.HIGH

    @pytest.mark.asyncio
    async def test_execute_task_success(self):
        """Test executing a task successfully."""
        scheduler = BackgroundTaskScheduler()

        async def test_func():
            return "test_result"

        task = Task(
            id="test_task",
            name="Test Task",
            func=test_func,
            priority=TaskPriority.NORMAL,
        )

        await scheduler._execute_task(task)

        assert task.status == TaskStatus.COMPLETED
        assert task.result == "test_result"
        assert task.last_run is not None

    @pytest.mark.asyncio
    async def test_execute_task_failure(self):
        """Test executing a task that fails."""
        scheduler = BackgroundTaskScheduler()

        async def test_func():
            raise ValueError("Test error")

        task = Task(
            id="test_task",
            name="Test Task",
            func=test_func,
            priority=TaskPriority.NORMAL,
            max_retries=0,
        )

        await scheduler._execute_task(task)

        assert task.status == TaskStatus.FAILED
        assert task.error is not None
        assert "Test error" in task.error

    @pytest.mark.asyncio
    async def test_execute_task_with_retry(self):
        """Test executing a task with retry on failure."""
        scheduler = BackgroundTaskScheduler()

        call_count = 0

        async def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Test error")
            return "success"

        task = Task(
            id="test_task",
            name="Test Task",
            func=test_func,
            priority=TaskPriority.NORMAL,
            max_retries=3,
        )

        await scheduler._execute_task(task)

        # Task should be requeued for retry
        assert task.retry_count >= 1
        assert task.status in [TaskStatus.PENDING, TaskStatus.COMPLETED]

    def test_task_should_run(self):
        """Test task should_run method."""
        task = Task(
            id="test_task",
            name="Test Task",
            func=lambda: None,
            priority=TaskPriority.NORMAL,
        )

        assert task.should_run() is True

    def test_task_should_run_cancelled(self):
        """Test cancelled task should not run."""
        task = Task(
            id="test_task",
            name="Test Task",
            func=lambda: None,
            priority=TaskPriority.NORMAL,
            status=TaskStatus.CANCELLED,
        )

        assert task.should_run() is False

    def test_task_should_run_scheduled(self):
        """Test scheduled task should not run before scheduled time."""
        scheduled_time = datetime.now() + timedelta(seconds=10)
        task = Task(
            id="test_task",
            name="Test Task",
            func=lambda: None,
            priority=TaskPriority.NORMAL,
            scheduled_at=scheduled_time,
        )

        assert task.should_run() is False

    def test_get_scheduler_singleton(self):
        """Test get_scheduler returns singleton."""
        scheduler1 = get_scheduler()
        scheduler2 = get_scheduler()

        assert scheduler1 is scheduler2
        assert isinstance(scheduler1, BackgroundTaskScheduler)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
