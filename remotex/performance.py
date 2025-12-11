"""
Performance Utilities
Caching and optimization utilities for faster operations.
"""

import json
import time
from pathlib import Path
from typing import Optional, Dict, List
from functools import wraps

# Cache directory
CACHE_DIR = Path.home() / ".remotex" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_cache_file(name: str) -> Path:
    """Get path to cache file."""
    return CACHE_DIR / f"{name}.json"


def cache_data(name: str, data: Dict, ttl: int = 300):
    """Cache data with TTL (time to live) in seconds."""
    cache_file = get_cache_file(name)
    cache_content = {
        'timestamp': time.time(),
        'ttl': ttl,
        'data': data
    }
    with open(cache_file, 'w') as f:
        json.dump(cache_content, f)


def get_cached_data(name: str) -> Optional[Dict]:
    """Get cached data if still valid."""
    cache_file = get_cache_file(name)
    
    if not cache_file.exists():
        return None
    
    try:
        with open(cache_file, 'r') as f:
            cache_content = json.load(f)
        
        # Check if cache is still valid
        age = time.time() - cache_content['timestamp']
        if age < cache_content['ttl']:
            return cache_content['data']
        else:
            # Cache expired, delete it
            cache_file.unlink()
            return None
    except Exception:
        return None


def clear_cache():
    """Clear all cached data."""
    for cache_file in CACHE_DIR.glob("*.json"):
        cache_file.unlink()


def cached(ttl: int = 300):
    """Decorator to cache function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
            
            # Try to get cached result
            cached_result = get_cached_data(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache_data(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator
