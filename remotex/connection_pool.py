"""
SSH Connection Pool Module
Manages reusable SSH connections for improved performance.
"""

import threading
import time
from typing import Dict, Optional
from datetime import datetime, timedelta

import paramiko
from rich.console import Console

console = Console()


class SSHConnectionPool:
    """Thread-safe SSH connection pool for reusing connections."""
    
    def __init__(self, max_age: int = 600):
        """
        Initialize connection pool.
        
        Args:
            max_age: Maximum age of connections in seconds (default 10 minutes)
        """
        self._connections: Dict[str, tuple[paramiko.SSHClient, datetime]] = {}
        self._lock = threading.Lock()
        self._max_age = max_age
    
    def _log_debug(self, host_alias: str, is_reuse: bool) -> None:
        """Log debug message if debug mode is enabled."""
        import os
        if os.getenv('REMOTEX_DEBUG'):
            if is_reuse:
                console.print(f"[dim]♻️  Reusing connection to {host_alias}[/dim]")
            else:
                console.print(f"[dim]🔌 Creating new connection to {host_alias}[/dim]")
    
    def _is_connection_valid(self, client: paramiko.SSHClient, created_at: datetime) -> bool:
        """Check if connection is still valid and not too old."""
        age = (datetime.now() - created_at).total_seconds()
        if age >= self._max_age:
            return False
        
        try:
            transport = client.get_transport()
            return transport is not None and transport.is_active()
        except Exception:
            return False
    
    def _close_connection(self, host_alias: str) -> None:
        """Close and remove a connection from the pool."""
        if host_alias in self._connections:
            client, _ = self._connections[host_alias]
            try:
                client.close()
            except Exception:
                pass
            del self._connections[host_alias]
    
    def _create_new_connection(self, host_alias: str, host_config: dict) -> Optional[paramiko.SSHClient]:
        """Create and store a new SSH connection."""
        from remotex.ssh_client import create_ssh_client
        client = create_ssh_client(host_config)
        
        if client:
            self._connections[host_alias] = (client, datetime.now())
        
        return client
    
    def get_connection(self, host_alias: str, host_config: dict) -> Optional[paramiko.SSHClient]:
        """
        Get a connection from the pool or create a new one.
        
        Args:
            host_alias: Host alias identifier
            host_config: SSH configuration dictionary
            
        Returns:
            Active SSH client or None on failure
        """
        with self._lock:
            # Check if we have a valid cached connection
            is_reuse = host_alias in self._connections
            self._log_debug(host_alias, is_reuse)
            
            if is_reuse:
                client, created_at = self._connections[host_alias]
                
                # Check if connection is still valid
                if self._is_connection_valid(client, created_at):
                    return client
                
                # Connection is dead or too old, remove it
                self._close_connection(host_alias)
            
            # Create new connection
            return self._create_new_connection(host_alias, host_config)
    
    def close_all(self):
        """Close all pooled connections."""
        with self._lock:
            for host_alias, (client, _) in self._connections.items():
                try:
                    client.close()
                except Exception:
                    pass
            self._connections.clear()
    
    def get_stats(self) -> Dict:
        """Get connection pool statistics."""
        with self._lock:
            active = 0
            for client, _ in self._connections.values():
                try:
                    transport = client.get_transport()
                    if transport and transport.is_active():
                        active += 1
                except Exception:
                    pass
            
            return {
                'total': len(self._connections),
                'active': active,
                'max_age': self._max_age
            }


# Global connection pool instance
_connection_pool = SSHConnectionPool()


def get_pooled_connection(host_alias: str, host_config: dict) -> Optional[paramiko.SSHClient]:
    """
    Get a pooled SSH connection.
    
    Args:
        host_alias: Host alias identifier
        host_config: SSH configuration dictionary
        
    Returns:
        Active SSH client or None on failure
    """
    return _connection_pool.get_connection(host_alias, host_config)


def close_connection_pool():
    """Close all pooled connections."""
    _connection_pool.close_all()


def get_pool_stats() -> Dict:
    """Get connection pool statistics."""
    return _connection_pool.get_stats()
