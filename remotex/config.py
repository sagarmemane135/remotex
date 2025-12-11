"""
RemoteX Configuration Module
Handles user preferences like default server, output mode, etc.
Supports environment variables for configuration.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Tuple, List

CONFIG_DIR = Path.home() / ".remotex"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Environment variable prefixes
ENV_PREFIX = "REMOTEX_"


def ensure_config_dir():
    """Ensure config directory exists."""
    if not CONFIG_DIR.exists():
        CONFIG_DIR.mkdir(mode=0o755, parents=True)


def load_config() -> Dict:
    """Load configuration from file and environment variables."""
    ensure_config_dir()
    
    # Default configuration
    default_config: Dict = {
        "default_server": None,
        "output_mode": "normal",  # normal, compact, silent
        "parallel_connections": 5,
        "timeout": 30,
        "groups": {},  # group_name: [server1, server2, ...]
        "server_tags": {},  # server_name: [tag1, tag2, ...]
        "command_aliases": {},  # alias_name: command_string
        "audit_enabled": True
    }
    
    # Load from file
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
        except Exception:
            config = default_config.copy()
    else:
        config = default_config.copy()
    
    # Override with environment variables (env vars take precedence)
    env_default_server = os.getenv(f"{ENV_PREFIX}DEFAULT_SERVER")
    if env_default_server:
        config["default_server"] = env_default_server
    
    env_output_mode = os.getenv(f"{ENV_PREFIX}OUTPUT_MODE")
    if env_output_mode:
        config["output_mode"] = env_output_mode
    
    env_parallel = os.getenv(f"{ENV_PREFIX}PARALLEL")
    if env_parallel:
        try:
            config["parallel_connections"] = int(env_parallel)
        except ValueError:
            pass
    
    env_timeout = os.getenv(f"{ENV_PREFIX}TIMEOUT")
    if env_timeout:
        try:
            config["timeout"] = int(env_timeout)
        except ValueError:
            pass
    
    env_audit = os.getenv(f"{ENV_PREFIX}AUDIT_ENABLED")
    if env_audit:
        config["audit_enabled"] = env_audit.lower() in ("true", "1", "yes", "on")
    
    return config


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


# ========== Group Management ==========

def get_groups() -> Dict:
    """Get all groups."""
    config = load_config()
    return config.get("groups", {})


def get_group_servers(group_name: str) -> list:
    """Get servers in a group."""
    groups = get_groups()
    return groups.get(group_name, [])


def add_group(group_name: str, servers: list):
    """Create or update a group."""
    config = load_config()
    if "groups" not in config:
        config["groups"] = {}
    config["groups"][group_name] = servers
    save_config(config)


def remove_group(group_name: str):
    """Remove a group."""
    config = load_config()
    if "groups" in config and group_name in config["groups"]:
        del config["groups"][group_name]
        save_config(config)


def add_server_to_group(group_name: str, server: str):
    """Add a server to a group."""
    config = load_config()
    if "groups" not in config:
        config["groups"] = {}
    if group_name not in config["groups"]:
        config["groups"][group_name] = []
    if server not in config["groups"][group_name]:
        config["groups"][group_name].append(server)
    save_config(config)


def remove_server_from_group(group_name: str, server: str):
    """Remove a server from a group."""
    config = load_config()
    if "groups" in config and group_name in config["groups"]:
        if server in config["groups"][group_name]:
            config["groups"][group_name].remove(server)
            save_config(config)


# ========== Tag Management ==========

def get_server_tags(server: str) -> list:
    """Get tags for a server."""
    config = load_config()
    server_tags = config.get("server_tags", {})
    return server_tags.get(server, [])


def add_tag_to_server(server: str, tag: str):
    """Add a tag to a server."""
    config = load_config()
    if "server_tags" not in config:
        config["server_tags"] = {}
    if server not in config["server_tags"]:
        config["server_tags"][server] = []
    if tag not in config["server_tags"][server]:
        config["server_tags"][server].append(tag)
    save_config(config)


def remove_tag_from_server(server: str, tag: str):
    """Remove a tag from a server."""
    config = load_config()
    if "server_tags" in config and server in config["server_tags"]:
        if tag in config["server_tags"][server]:
            config["server_tags"][server].remove(tag)
            save_config(config)


def get_servers_by_tag(tag: str) -> list:
    """Get all servers with a specific tag."""
    config = load_config()
    server_tags = config.get("server_tags", {})
    return [server for server, tags in server_tags.items() if tag in tags]


# ========== Command Aliases ==========

def get_command_aliases() -> Dict:
    """Get all command aliases."""
    config = load_config()
    return config.get("command_aliases", {})


def get_command_alias(alias: str) -> Optional[str]:
    """Get command for an alias."""
    aliases = get_command_aliases()
    return aliases.get(alias)


def add_command_alias(alias: str, command: str):
    """Create or update a command alias."""
    config = load_config()
    if "command_aliases" not in config:
        config["command_aliases"] = {}
    config["command_aliases"][alias] = command
    save_config(config)


def remove_command_alias(alias: str):
    """Remove a command alias."""
    config = load_config()
    if "command_aliases" in config and alias in config["command_aliases"]:
        del config["command_aliases"][alias]
        save_config(config)


# ========== Config Validation & Management ==========

def validate_config() -> Tuple[bool, List[str]]:
    """
    Validate configuration file.
    
    Returns:
        tuple: (is_valid, list_of_errors)
    """
    errors = []
    
    try:
        config = load_config()
        
        # Validate output_mode
        valid_modes = ["normal", "compact", "silent"]
        if config.get("output_mode") not in valid_modes:
            errors.append(f"Invalid output_mode: {config.get('output_mode')}. Must be one of {valid_modes}")
        
        # Validate parallel_connections
        parallel = config.get("parallel_connections", 5)
        if not isinstance(parallel, int) or parallel < 1 or parallel > 50:
            errors.append(f"Invalid parallel_connections: {parallel}. Must be between 1 and 50")
        
        # Validate timeout
        timeout = config.get("timeout", 30)
        if not isinstance(timeout, int) or timeout < 1:
            errors.append(f"Invalid timeout: {timeout}. Must be a positive integer")
        
        # Validate default_server exists (if set)
        default_server = config.get("default_server")
        if default_server:
            from remotex.ssh_config import host_exists
            if not host_exists(default_server):
                errors.append(f"Default server '{default_server}' not found in SSH config")
        
        # Validate groups reference existing servers
        from remotex.ssh_config import get_all_hosts
        all_hosts = {h['alias'] for h in get_all_hosts()}
        groups = config.get("groups", {})
        for group_name, servers in groups.items():
            if not isinstance(servers, list):
                errors.append(f"Group '{group_name}' has invalid format (not a list)")
                continue
            for server in servers:
                if server not in all_hosts:
                    errors.append(f"Group '{group_name}' references non-existent server: {server}")
        
    except Exception as e:
        errors.append(f"Error loading config: {str(e)}")
    
    return len(errors) == 0, errors


def export_config(output_file: Optional[str] = None) -> str:
    """
    Export configuration to a JSON file.
    
    Args:
        output_file: Path to output file (default: config_backup_<timestamp>.json)
    
    Returns:
        str: Path to exported file
    """
    from datetime import datetime
    
    config = load_config()
    
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = str(CONFIG_DIR / f"config_backup_{timestamp}.json")
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    return str(output_path)


def import_config(input_file: str, merge: bool = False) -> bool:
    """
    Import configuration from a JSON file.
    
    Args:
        input_file: Path to input JSON file
        merge: If True, merge with existing config. If False, replace.
    
    Returns:
        bool: True if successful, False otherwise
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        return False
    
    try:
        with open(input_path, 'r') as f:
            imported_config = json.load(f)
        
        if merge:
            # Merge with existing config
            existing_config = load_config()
            existing_config.update(imported_config)
            save_config(existing_config)
        else:
            # Replace config
            save_config(imported_config)
        
        return True
    except Exception:
        return False
