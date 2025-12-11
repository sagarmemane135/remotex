"""
RemoteX Command History
Track and replay command history
"""

import json
import shlex
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from remotex.config import CONFIG_DIR

HISTORY_FILE = CONFIG_DIR / "history.json"


def ensure_history_file():
    """Ensure history file exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'w') as f:
            json.dump({"commands": []}, f)


def add_to_history(
    command: str,
    args: List[str],
    hosts: List[str],
    success: bool = True,
    metadata: Optional[Dict] = None
):
    """Add a command to history."""
    ensure_history_file()
    
    with open(HISTORY_FILE, 'r') as f:
        data = json.load(f)
    
    entry = {
        "id": len(data["commands"]) + 1,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "command": command,
        "args": args,
        "hosts": hosts,
        "success": success,
        "full_command": f"{command} {' '.join(shlex.quote(str(a)) for a in args)}"
    }
    
    if metadata:
        entry["metadata"] = metadata
    
    data["commands"].append(entry)
    
    # Keep only last 1000 entries
    if len(data["commands"]) > 1000:
        data["commands"] = data["commands"][-1000:]
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    return entry["id"]


def get_history(
    limit: int = 50,
    host: Optional[str] = None,
    command: Optional[str] = None,
    since: Optional[str] = None
) -> List[Dict]:
    """Get command history with optional filters."""
    if not HISTORY_FILE.exists():
        return []
    
    with open(HISTORY_FILE, 'r') as f:
        data = json.load(f)
    
    commands = data.get("commands", [])
    
    # Apply filters
    filtered = []
    for cmd in commands:
        if host and host not in cmd.get("hosts", []):
            continue
        if command and cmd.get("command") != command:
            continue
        if since and cmd.get("timestamp", "") < since:
            continue
        filtered.append(cmd)
    
    # Return most recent
    return filtered[-limit:]


def get_history_entry(entry_id: int) -> Optional[Dict]:
    """Get a specific history entry by ID."""
    if not HISTORY_FILE.exists():
        return None
    
    with open(HISTORY_FILE, 'r') as f:
        data = json.load(f)
    
    for cmd in data.get("commands", []):
        if cmd.get("id") == entry_id:
            return cmd
    
    return None


def clear_history():
    """Clear all command history."""
    ensure_history_file()
    with open(HISTORY_FILE, 'w') as f:
        json.dump({"commands": []}, f)


def export_history(output_file: str):
    """Export history to a file."""
    if not HISTORY_FILE.exists():
        return
    
    with open(HISTORY_FILE, 'r') as f:
        data = json.load(f)
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

