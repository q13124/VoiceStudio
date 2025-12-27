"""
Progress Bar Utilities
Integrates tqdm for progress tracking in training and processing.
Part of FREE_LIBRARIES_INTEGRATION - Worker 3.
"""

import logging
import sys
from typing import Any, Iterator, Optional, Union

logger = logging.getLogger(__name__)

# Try importing tqdm
try:
    from tqdm import tqdm
    from tqdm.asyncio import tqdm as atqdm

    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    logger.warning("tqdm not installed, progress bars will be disabled")

    # Create dummy tqdm class for fallback
    class tqdm:
        def __init__(self, *args, **kwargs):
            self.total = kwargs.get("total", None)
            self.n = 0

        def update(self, n=1):
            self.n += n

        def set_description(self, desc=None):
            pass

        def close(self):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    class atqdm:
        def __init__(self, *args, **kwargs):
            self.total = kwargs.get("total", None)
            self.n = 0

        async def update(self, n=1):
            self.n += n

        def set_description(self, desc=None):
            pass

        async def close(self):
            pass


def create_progress_bar(
    total: Optional[int] = None,
    desc: Optional[str] = None,
    unit: str = "it",
    disable: bool = False,
    **kwargs,
) -> Union[tqdm, Any]:
    """
    Create a progress bar using tqdm.

    Args:
        total: Total number of iterations
        desc: Description text
        unit: Unit of progress (e.g., 'it', 'epoch', 'file')
        disable: Whether to disable the progress bar
        **kwargs: Additional tqdm parameters

    Returns:
        tqdm progress bar instance
    """
    if not HAS_TQDM or disable:
        return tqdm(total=total, desc=desc, disable=True, **kwargs)

    return tqdm(total=total, desc=desc, unit=unit, disable=disable, **kwargs)


def create_async_progress_bar(
    total: Optional[int] = None,
    desc: Optional[str] = None,
    unit: str = "it",
    disable: bool = False,
    **kwargs,
) -> Union[atqdm, Any]:
    """
    Create an async progress bar using tqdm.

    Args:
        total: Total number of iterations
        desc: Description text
        unit: Unit of progress (e.g., 'it', 'epoch', 'file')
        disable: Whether to disable the progress bar
        **kwargs: Additional tqdm parameters

    Returns:
        Async tqdm progress bar instance
    """
    if not HAS_TQDM or disable:
        return atqdm(total=total, desc=desc, disable=True, **kwargs)

    return atqdm(total=total, desc=desc, unit=unit, disable=disable, **kwargs)


def wrap_iterable(
    iterable: Iterator,
    desc: Optional[str] = None,
    total: Optional[int] = None,
    disable: bool = False,
    **kwargs,
) -> Iterator:
    """
    Wrap an iterable with a progress bar.

    Args:
        iterable: Iterable to wrap
        desc: Description text
        total: Total number of items (if known)
        disable: Whether to disable the progress bar
        **kwargs: Additional tqdm parameters

    Returns:
        Wrapped iterable with progress bar
    """
    if not HAS_TQDM or disable:
        return iterable

    return tqdm(iterable, desc=desc, total=total, disable=disable, **kwargs)


def update_progress(progress_bar: Any, n: int = 1, desc: Optional[str] = None):
    """
    Update a progress bar.

    Args:
        progress_bar: Progress bar instance
        n: Number of items to advance
        desc: Optional description update
    """
    if progress_bar is None:
        return

    try:
        if desc is not None:
            progress_bar.set_description(desc)
        progress_bar.update(n)
    except Exception as e:
        logger.debug(f"Failed to update progress bar: {e}")


def close_progress(progress_bar: Any):
    """
    Close a progress bar.

    Args:
        progress_bar: Progress bar instance
    """
    if progress_bar is None:
        return

    try:
        progress_bar.close()
    except Exception:
        pass
