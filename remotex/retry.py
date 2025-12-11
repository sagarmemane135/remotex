"""
RemoteX Retry Logic Module
Implements retry mechanisms with exponential backoff for SSH operations
"""

import time
from typing import Callable, Dict, Any, Optional
from rich.console import Console

console = Console()


def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Retry a function with exponential backoff.
    
    Args:
        func: Function to retry (should return dict with 'success' key)
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each attempt
        max_delay: Maximum delay between retries
        verbose: Print retry attempts
        
    Returns:
        Result from successful execution or last failed attempt
    """
    delay = initial_delay
    last_result = None
    
    for attempt in range(max_retries + 1):  # +1 for initial attempt
        try:
            result = func()
            
            # Check if successful
            if result.get('success', False):
                if verbose and attempt > 0:
                    console.print(f"[green]✓[/green] Succeeded on attempt {attempt + 1}/{max_retries + 1}")
                return result
            
            # Not successful, prepare for retry
            last_result = result
            
            # Don't sleep after last attempt
            if attempt < max_retries:
                if verbose:
                    console.print(
                        f"[yellow]⚠[/yellow] Attempt {attempt + 1}/{max_retries + 1} failed. "
                        f"Retrying in {delay:.1f}s..."
                    )
                time.sleep(delay)
                delay = min(delay * backoff_factor, max_delay)
            
        except Exception as e:
            last_result = {
                'success': False,
                'error': str(e),
                'exit_code': -1,
                'output': ''
            }
            
            if attempt < max_retries:
                if verbose:
                    console.print(
                        f"[yellow]⚠[/yellow] Attempt {attempt + 1}/{max_retries + 1} failed with error: {e}. "
                        f"Retrying in {delay:.1f}s..."
                    )
                time.sleep(delay)
                delay = min(delay * backoff_factor, max_delay)
    
    # All retries exhausted
    if verbose:
        console.print(f"[red]✗[/red] All {max_retries + 1} attempts failed")
    
    return last_result or {
        'success': False,
        'error': 'All retry attempts failed',
        'exit_code': -1,
        'output': ''
    }


def should_retry_error(error: str, exit_code: int) -> bool:
    """
    Determine if an error should trigger a retry.
    
    Args:
        error: Error message
        exit_code: Command exit code
        
    Returns:
        True if error is retryable
    """
    # Retryable network/connection errors
    retryable_errors = [
        'timeout',
        'connection refused',
        'connection reset',
        'broken pipe',
        'no route to host',
        'network unreachable',
        'temporarily unavailable'
    ]
    
    error_lower = error.lower()
    return any(err in error_lower for err in retryable_errors)
