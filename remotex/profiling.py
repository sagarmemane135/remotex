"""
Performance Profiling Tools
"""

import time
import cProfile
import pstats
import io
from functools import wraps
from pathlib import Path
from typing import Callable, Optional
from contextlib import contextmanager

from remotex.config import CONFIG_DIR

PROFILE_DIR = CONFIG_DIR / "profiles"
PROFILE_DIR.mkdir(parents=True, exist_ok=True)


def profile_function(func: Callable):
    """Decorator to profile a function."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            result = func(*args, **kwargs)
        finally:
            profiler.disable()
            
            # Save profile
            profile_file = PROFILE_DIR / f"{func.__name__}_{int(time.time())}.prof"
            profiler.dump_stats(str(profile_file))
        
        return result
    
    return wrapper


@contextmanager
def profile_context(name: str = "profile"):
    """Context manager for profiling code blocks."""
    profiler = cProfile.Profile()
    profiler.enable()
    
    try:
        yield profiler
    finally:
        profiler.disable()
        
        # Save profile
        profile_file = PROFILE_DIR / f"{name}_{int(time.time())}.prof"
        profiler.dump_stats(str(profile_file))


def analyze_profile(profile_file: Path, sort_by: str = "cumulative", limit: int = 20):
    """Analyze a profile file and print statistics."""
    stats = pstats.Stats(str(profile_file))
    stats.sort_stats(sort_by)
    
    # Capture output
    output = io.StringIO()
    stats.stream = output  # type: ignore[attr-defined]
    stats.print_stats(limit)
    
    return output.getvalue()


def get_profile_summary(profile_file: Path) -> dict:
    """Get a summary of profile statistics."""
    stats = pstats.Stats(str(profile_file))
    
    return {
        "total_calls": stats.total_calls,  # type: ignore[attr-defined]
        "primitive_calls": stats.primitive_calls,  # type: ignore[attr-defined]
        "total_time": stats.total_tt,  # type: ignore[attr-defined]
        "cumulative_time": sum(call[2] for call in stats.stats.values())  # type: ignore[attr-defined]
    }


class PerformanceTimer:
    """Simple performance timer."""
    
    def __init__(self, name: str = "operation"):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        self.end_time = time.perf_counter()
        elapsed = self.end_time - self.start_time
        print(f"[{self.name}] Elapsed time: {elapsed:.4f}s")
    
    @property
    def elapsed(self):
        """Get elapsed time."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        elif self.start_time:
            return time.perf_counter() - self.start_time
        return None

