"""
RemoteX Audit Logging
Track all command executions for compliance and debugging
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from remotex.config import CONFIG_DIR, load_config

AUDIT_LOG_FILE = CONFIG_DIR / "audit.log"


def is_audit_enabled() -> bool:
    """Check if audit logging is enabled."""
    config = load_config()
    return config.get("audit_enabled", True)


def log_command_execution(
    command_type: str,
    hosts: List[str],
    command: str,
    results: Dict[str, Dict],
    user: Optional[str] = None,
    metadata: Optional[Dict] = None
):
    """
    Log a command execution to audit log.
    
    Args:
        command_type: Type of command (exec, exec-all, exec-group, etc.)
        hosts: List of target hosts
        command: Command that was executed
        results: Dict of {host: {success: bool, exit_code: int, output: str}}
        user: Username (defaults to system user)
        metadata: Additional metadata (group, tags, etc.)
    """
    if not is_audit_enabled():
        return
    
    import os
    import getpass
    
    # Build audit entry
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "unix_time": int(time.time()),
        "user": user or getpass.getuser(),
        "command_type": command_type,
        "command": command,
        "hosts": hosts,
        "host_count": len(hosts),
        "results": {
            host: {
                "success": res.get("success", False),
                "exit_code": res.get("exit_code", -1),
                "output_length": len(res.get("output", ""))
            }
            for host, res in results.items()
        },
        "summary": {
            "total": len(hosts),
            "succeeded": sum(1 for r in results.values() if r.get("success")),
            "failed": sum(1 for r in results.values() if not r.get("success"))
        }
    }
    
    # Add optional metadata
    if metadata:
        audit_entry["metadata"] = metadata
    
    # Ensure audit directory exists
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Append to audit log
    with open(AUDIT_LOG_FILE, 'a') as f:
        f.write(json.dumps(audit_entry) + "\n")


def get_recent_audit_entries(count: int = 20) -> List[Dict]:
    """Get recent audit log entries."""
    if not AUDIT_LOG_FILE.exists():
        return []
    
    entries = []
    with open(AUDIT_LOG_FILE, 'r') as f:
        for line in f:
            try:
                entries.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue
    
    # Return most recent entries
    return entries[-count:]


def search_audit_log(
    user: Optional[str] = None,
    command_type: Optional[str] = None,
    host: Optional[str] = None,
    since: Optional[str] = None,
    limit: int = 50
) -> List[Dict]:
    """Search audit log with filters."""
    if not AUDIT_LOG_FILE.exists():
        return []
    
    entries = []
    with open(AUDIT_LOG_FILE, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                
                # Apply filters
                if user and entry.get("user") != user:
                    continue
                if command_type and entry.get("command_type") != command_type:
                    continue
                if host and host not in entry.get("hosts", []):
                    continue
                if since:
                    # Simple timestamp comparison
                    if entry.get("timestamp", "") < since:
                        continue
                
                entries.append(entry)
            except json.JSONDecodeError:
                continue
    
    # Return most recent matching entries
    return entries[-limit:]
