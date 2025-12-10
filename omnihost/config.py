"""
OmniHost Configuration Module
Handles user preferences like default server, output mode, etc.
"""

import json
from pathlib import Path
from typing import Optional, Dict

CONFIG_DIR = Path.home() / ".omnihost"
CONFIG_FILE = CONFIG_DIR / "config.json"


def ensure_config_dir():
    """Ensure config directory exists."""
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(mode=0o755, parents=True)


def load_config() -> Dict:
    """Load configuration from file."""
    ensure_config_dir()
    
    if not CONFIG_FILE.exists():
        return {
            "default_server": None,
            "output_mode": "normal",  # normal, compact, silent
            "parallel_connections": 5,
            "timeout": 30
        }
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(config: Dict):
    """Save configuration to file."""
    ensure_config_dir()
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def get_default_server() -> Optional[str]:
    """Get the default server."""
    config = load_config()
    return config.get("default_server")


def set_default_server(server: str):
    """Set the default server."""
    config = load_config()
    config["default_server"] = server
    save_config(config)


def get_output_mode() -> str:
    """Get output mode preference."""
    config = load_config()
    return config.get("output_mode", "normal")


def set_output_mode(mode: str):
    """Set output mode preference."""
    config = load_config()
    config["output_mode"] = mode
    save_config(config)


def get_server_alias(alias: str) -> Optional[str]:
    """Get actual server name from alias."""
    config = load_config()
    aliases = config.get("aliases", {})
    return aliases.get(alias)


def set_server_alias(alias: str, server: str):
    """Set a server alias."""
    config = load_config()
    if "aliases" not in config:
        config["aliases"] = {}
    config["aliases"][alias] = server
    save_config(config)


def resolve_server(server_input: Optional[str]) -> Optional[str]:
    """
    Resolve server input to actual server name.
    Checks: direct name -> alias -> default server
    """
    if server_input:
        # Check if it's an alias
        alias_result = get_server_alias(server_input)
        if alias_result:
            return alias_result
        return server_input
    
    # No input, try default server
    return get_default_server()
