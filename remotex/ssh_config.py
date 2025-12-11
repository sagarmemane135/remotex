"""
SSH Config Management Module
Handles reading, parsing, and modifying SSH configuration files.
"""

import re
from pathlib import Path
from typing import Optional, List, Dict

import paramiko
from rich.console import Console

console = Console()


def get_ssh_config_path() -> Path:
    """Get the SSH config file path."""
    return Path.home() / ".ssh" / "config"


def ensure_ssh_config_exists():
    """Ensure SSH config file and directory exist."""
    ssh_dir = Path.home() / ".ssh"
    ssh_config_path = get_ssh_config_path()
    
    if not ssh_dir.exists():
        ssh_dir.mkdir(mode=0o700)
        console.print(f"[green]Created .ssh directory at {ssh_dir}[/green]")
    
    if not ssh_config_path.exists():
        ssh_config_path.touch(mode=0o600)
        console.print(f"[green]Created SSH config file at {ssh_config_path}[/green]")


def get_all_hosts() -> List[Dict[str, str]]:
    """
    Get all configured hosts from SSH config.
    
    Returns:
        List of dictionaries with host information
    """
    ssh_config_path = get_ssh_config_path()
    
    if not ssh_config_path.exists():
        return []
    
    hosts = []
    try:
        ssh_config = paramiko.SSHConfig()
        with open(ssh_config_path, 'r') as f:
            ssh_config.parse(f)
        
        # Read raw config to get all host aliases
        with open(ssh_config_path, 'r') as f:
            content = f.read()
            host_pattern = re.compile(r'^Host\s+(.+)$', re.MULTILINE | re.IGNORECASE)
            host_aliases = host_pattern.findall(content)
        
        for alias in host_aliases:
            # Skip wildcards and special patterns
            if '*' in alias or '?' in alias or alias.lower() == 'host':
                continue
            
            host_config = ssh_config.lookup(alias)
            hosts.append({
                'alias': alias,
                'hostname': host_config.get('hostname', 'N/A'),
                'user': host_config.get('user', 'N/A'),
                'port': str(host_config.get('port', '22')),
                'identityfile': host_config.get('identityfile', ['N/A'])[0] if host_config.get('identityfile') else 'N/A',
                'proxyjump': host_config.get('proxyjump', 'N/A')
            })
    except Exception as e:
        console.print(f"[red]Error reading SSH config: {e}[/red]")
    
    return hosts


def parse_ssh_config(host_alias: str) -> Optional[dict]:
    """
    Parse SSH config file to get host details.
    
    Args:
        host_alias: The host alias from SSH config
        
    Returns:
        Dictionary with connection details or None if not found
    """
    ssh_config_path = get_ssh_config_path()
    
    if not ssh_config_path.exists():
        console.print(f"[red]Error: SSH config file not found at {ssh_config_path}[/red]")
        return None
    
    try:
        ssh_config = paramiko.SSHConfig()
        with open(ssh_config_path, 'r') as f:
            ssh_config.parse(f)
        
        host_config = ssh_config.lookup(host_alias)
        
        return {
            'hostname': host_config.get('hostname'),
            'port': int(host_config.get('port', 22)),
            'user': host_config.get('user'),
            'identityfile': host_config.get('identityfile', [None])[0],
            'proxyjump': host_config.get('proxyjump')
        }
    except Exception as e:
        console.print(f"[red]Error parsing SSH config: {e}[/red]")
        return None


def add_host_to_config(alias: str, hostname: str, user: str, port: int = 22, identity_file: Optional[str] = None, jump_host: Optional[str] = None) -> bool:
    """
    Add a new host to SSH config.
    
    Args:
        alias: Host alias
        hostname: Server hostname or IP
        user: SSH username
        port: SSH port (default 22)
        identity_file: Path to private key file (optional)
        jump_host: Jump host/bastion alias (optional)
        
    Returns:
        True if successful, False otherwise
    """
    ssh_config_path = get_ssh_config_path()
    
    # Check if alias already exists
    hosts = get_all_hosts()
    if any(h['alias'] == alias for h in hosts):
        console.print(f"[red]Error: Host alias '{alias}' already exists![/red]")
        return False
    
    # Build config entry
    config_entry = f"\n\nHost {alias}\n"
    config_entry += f"    HostName {hostname}\n"
    config_entry += f"    User {user}\n"
    config_entry += f"    Port {port}\n"
    
    if identity_file:
        config_entry += f"    IdentityFile {identity_file}\n"
    
    if jump_host:
        config_entry += f"    ProxyJump {jump_host}\n"
    
    # Append to config
    try:
        with open(ssh_config_path, 'a') as f:
            f.write(config_entry)
        console.print(f"[green]✓ Successfully added server '{alias}'[/green]")
        if jump_host:
            console.print(f"[dim]  Using jump host: {jump_host}[/dim]")
        return True
    except Exception as e:
        console.print(f"[red]Error writing to SSH config: {e}[/red]")
        return False


def remove_host_from_config(alias: str) -> bool:
    """
    Remove a host from SSH config.
    
    Args:
        alias: Host alias to remove
        
    Returns:
        True if successful, False otherwise
    """
    ssh_config_path = get_ssh_config_path()
    
    try:
        with open(ssh_config_path, 'r') as f:
            lines = f.readlines()
        
        new_lines = []
        skip_until_next_host = False
        found = False
        
        for i, line in enumerate(lines):
            if re.match(r'^Host\s+', line, re.IGNORECASE):
                # Check if this is the host to remove
                if re.match(rf'^Host\s+{re.escape(alias)}\s*$', line, re.IGNORECASE):
                    skip_until_next_host = True
                    found = True
                    continue
                else:
                    skip_until_next_host = False
            
            if not skip_until_next_host:
                new_lines.append(line)
        
        if not found:
            console.print(f"[red]Error: Host alias '{alias}' not found[/red]")
            return False
        
        with open(ssh_config_path, 'w') as f:
            f.writelines(new_lines)
        
        console.print(f"[green]✓ Successfully removed server '{alias}'[/green]")
        return True
    except Exception as e:
        console.print(f"[red]Error modifying SSH config: {e}[/red]")
        return False


def host_exists(alias: str) -> bool:
    """
    Check if a host exists in SSH config.
    
    Args:
        alias: Host alias to check
        
    Returns:
        True if host exists, False otherwise
    """
    hosts = get_all_hosts()
    return any(h['alias'] == alias for h in hosts)
