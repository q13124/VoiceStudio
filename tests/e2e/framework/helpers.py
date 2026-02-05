"""
E2E Test Helpers.

Provides utility classes for common testing operations:
- Wait mechanisms
- Screenshot capture
- Retry logic
- Test data generators
"""

import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar, Generic, List

logger = logging.getLogger(__name__)

T = TypeVar('T')


# =============================================================================
# Wait Helper
# =============================================================================


@dataclass
class WaitResult(Generic[T]):
    """Result of a wait operation."""
    success: bool
    value: Optional[T] = None
    elapsed_seconds: float = 0.0
    attempts: int = 0
    error: Optional[str] = None


class WaitHelper:
    """Helper class for wait operations."""
    
    @staticmethod
    def wait_until(
        condition: Callable[[], bool],
        timeout: float = 10.0,
        poll_interval: float = 0.5,
        message: str = "Condition not met"
    ) -> WaitResult[bool]:
        """
        Wait until a condition is true.
        
        Args:
            condition: Callable that returns True when condition is met
            timeout: Maximum time to wait in seconds
            poll_interval: Time between condition checks
            message: Error message if timeout occurs
            
        Returns:
            WaitResult with success status
        """
        start = time.time()
        attempts = 0
        
        while time.time() - start < timeout:
            attempts += 1
            try:
                if condition():
                    return WaitResult(
                        success=True,
                        value=True,
                        elapsed_seconds=time.time() - start,
                        attempts=attempts
                    )
            except Exception as e:
                logger.debug(f"Wait condition check failed: {e}")
            
            time.sleep(poll_interval)
        
        return WaitResult(
            success=False,
            elapsed_seconds=time.time() - start,
            attempts=attempts,
            error=message
        )
    
    @staticmethod
    def wait_for_value(
        getter: Callable[[], T],
        expected: T,
        timeout: float = 10.0,
        poll_interval: float = 0.5
    ) -> WaitResult[T]:
        """
        Wait until a getter returns an expected value.
        
        Args:
            getter: Callable that returns the value to check
            expected: Expected value
            timeout: Maximum time to wait
            poll_interval: Time between checks
            
        Returns:
            WaitResult with the actual value
        """
        start = time.time()
        attempts = 0
        last_value = None
        
        while time.time() - start < timeout:
            attempts += 1
            try:
                last_value = getter()
                if last_value == expected:
                    return WaitResult(
                        success=True,
                        value=last_value,
                        elapsed_seconds=time.time() - start,
                        attempts=attempts
                    )
            except Exception as e:
                logger.debug(f"Wait value check failed: {e}")
            
            time.sleep(poll_interval)
        
        return WaitResult(
            success=False,
            value=last_value,
            elapsed_seconds=time.time() - start,
            attempts=attempts,
            error=f"Expected {expected}, got {last_value}"
        )
    
    @staticmethod
    def wait_for_not_none(
        getter: Callable[[], Optional[T]],
        timeout: float = 10.0,
        poll_interval: float = 0.5
    ) -> WaitResult[T]:
        """Wait until a getter returns a non-None value."""
        start = time.time()
        attempts = 0
        
        while time.time() - start < timeout:
            attempts += 1
            try:
                value = getter()
                if value is not None:
                    return WaitResult(
                        success=True,
                        value=value,
                        elapsed_seconds=time.time() - start,
                        attempts=attempts
                    )
            except Exception as e:
                logger.debug(f"Wait check failed: {e}")
            
            time.sleep(poll_interval)
        
        return WaitResult(
            success=False,
            elapsed_seconds=time.time() - start,
            attempts=attempts,
            error="Value remained None"
        )


# =============================================================================
# Screenshot Helper
# =============================================================================


class ScreenshotHelper:
    """Helper class for screenshot operations."""
    
    def __init__(self, output_dir: Path):
        """
        Initialize screenshot helper.
        
        Args:
            output_dir: Directory to save screenshots
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._screenshot_count = 0
    
    def capture(
        self,
        driver,
        name: str,
        include_timestamp: bool = True
    ) -> Optional[Path]:
        """
        Capture a screenshot.
        
        Args:
            driver: WebDriver instance
            name: Screenshot name (without extension)
            include_timestamp: Whether to include timestamp in filename
            
        Returns:
            Path to saved screenshot, or None if failed
        """
        if driver is None:
            logger.warning("No driver available for screenshot")
            return None
        
        self._screenshot_count += 1
        
        if include_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self._screenshot_count:03d}_{name}_{timestamp}.png"
        else:
            filename = f"{self._screenshot_count:03d}_{name}.png"
        
        filepath = self.output_dir / filename
        
        try:
            driver.save_screenshot(str(filepath))
            logger.info(f"Screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None
    
    def capture_on_failure(self, driver, test_name: str) -> Optional[Path]:
        """Capture a screenshot on test failure."""
        return self.capture(driver, f"FAILED_{test_name}")
    
    def capture_step(self, driver, step_name: str) -> Optional[Path]:
        """Capture a screenshot for a test step."""
        return self.capture(driver, f"step_{step_name}")
    
    def get_screenshot_count(self) -> int:
        """Get number of screenshots captured."""
        return self._screenshot_count
    
    def get_all_screenshots(self) -> List[Path]:
        """Get list of all captured screenshots."""
        return sorted(self.output_dir.glob("*.png"))


# =============================================================================
# Retry Helper
# =============================================================================


class RetryHelper:
    """Helper class for retry operations."""
    
    @staticmethod
    def retry(
        func: Callable[[], T],
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        exceptions: tuple = (Exception,),
        on_retry: Optional[Callable[[int, Exception], None]] = None
    ) -> T:
        """
        Retry a function until it succeeds or max attempts reached.
        
        Args:
            func: Function to retry
            max_attempts: Maximum number of attempts
            delay: Initial delay between attempts
            backoff: Multiplier for delay after each attempt
            exceptions: Exception types to catch and retry
            on_retry: Callback called on each retry (attempt_num, exception)
            
        Returns:
            Result of successful function call
            
        Raises:
            Last exception if all attempts failed
        """
        current_delay = delay
        last_exception = None
        
        for attempt in range(1, max_attempts + 1):
            try:
                return func()
            except exceptions as e:
                last_exception = e
                if attempt < max_attempts:
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed: {e}. "
                        f"Retrying in {current_delay}s..."
                    )
                    if on_retry:
                        on_retry(attempt, e)
                    time.sleep(current_delay)
                    current_delay *= backoff
        
        raise last_exception


def retry_decorator(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """Decorator for retry logic."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return RetryHelper.retry(
                lambda: func(*args, **kwargs),
                max_attempts=max_attempts,
                delay=delay,
                backoff=backoff,
                exceptions=exceptions
            )
        return wrapper
    return decorator


# =============================================================================
# Test Data Helper
# =============================================================================


class TestDataHelper:
    """Helper class for test data generation."""
    
    @staticmethod
    def unique_name(prefix: str = "Test") -> str:
        """Generate a unique name with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"{prefix}_{timestamp}"
    
    @staticmethod
    def sample_text(length: int = 100) -> str:
        """Generate sample text for synthesis testing."""
        sample = (
            "The quick brown fox jumps over the lazy dog. "
            "This is a test sentence for voice synthesis. "
            "VoiceStudio provides professional voice cloning capabilities. "
        )
        return (sample * ((length // len(sample)) + 1))[:length]
    
    @staticmethod
    def sample_ssml(text: str = "Hello world") -> str:
        """Generate sample SSML for synthesis testing."""
        return f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis">
            <prosody rate="medium" pitch="default">
                {text}
            </prosody>
        </speak>"""
    
    @staticmethod
    def sample_project_config() -> dict:
        """Generate sample project configuration."""
        return {
            "name": TestDataHelper.unique_name("Project"),
            "description": "Test project for E2E testing",
            "settings": {
                "language": "en",
                "sample_rate": 22050,
                "format": "wav"
            }
        }
    
    @staticmethod
    def sample_voice_profile() -> dict:
        """Generate sample voice profile data."""
        return {
            "name": TestDataHelper.unique_name("Voice"),
            "description": "Test voice profile",
            "language": "en",
            "gender": "neutral",
            "tags": ["test", "e2e"]
        }


# =============================================================================
# Performance Timer
# =============================================================================


class PerformanceTimer:
    """Helper class for measuring performance."""
    
    def __init__(self, name: str = "Operation"):
        """Initialize timer with operation name."""
        self.name = name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.checkpoints: List[tuple] = []
    
    def start(self) -> "PerformanceTimer":
        """Start the timer."""
        self.start_time = time.time()
        logger.info(f"Timer started: {self.name}")
        return self
    
    def checkpoint(self, name: str) -> float:
        """Record a checkpoint and return elapsed time since start."""
        if self.start_time is None:
            raise RuntimeError("Timer not started")
        
        elapsed = time.time() - self.start_time
        self.checkpoints.append((name, elapsed))
        logger.info(f"Checkpoint '{name}': {elapsed:.3f}s")
        return elapsed
    
    def stop(self) -> float:
        """Stop the timer and return total elapsed time."""
        if self.start_time is None:
            raise RuntimeError("Timer not started")
        
        self.end_time = time.time()
        elapsed = self.end_time - self.start_time
        logger.info(f"Timer stopped: {self.name} - Total: {elapsed:.3f}s")
        return elapsed
    
    @property
    def elapsed(self) -> float:
        """Get elapsed time."""
        if self.start_time is None:
            return 0.0
        end = self.end_time or time.time()
        return end - self.start_time
    
    def __enter__(self) -> "PerformanceTimer":
        """Context manager entry."""
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
