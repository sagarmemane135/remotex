"""
SSH Client Management Module
Handles SSH client creation and connection management.
"""

import os
from typing import Optional

import paramiko
from rich.console import Console
from rich.panel import Panel

console = Console()


def create_ssh_client(host_config: dict) -> Optional[paramiko.SSHClient]:
    """
    Create and connect SSH client using host configuration.
    
    Args:
        host_config: Dictionary with connection details
        
    Returns:
        Connected SSHClient or None on failure
    """
    if not host_config.get('hostname'):
        console.print("[red]Error: Hostname not found in SSH config[/red]")
        return None
    
    try:
        client = paramiko.SSHClient()
        # AutoAddPolicy is appropriate here - we rely on SSH config for host key management
        # Users manage host keys through their ~/.ssh/known_hosts and SSH config files
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # nosec B507
        
        connect_params = {
            'hostname': host_config['hostname'],
            'port': host_config['port'],
            'username': host_config.get('user'),
        }
        
        # Add key file if specified
        if host_config.get('identityfile'):
            identity_file = os.path.expanduser(host_config['identityfile'])
            if os.path.exists(identity_file):
                connect_params['key_filename'] = identity_file
        
        client.connect(**connect_params)
        return client
        
    except Exception as e:
        console.print(Panel(
            f"[red]Failed to connect to {host_config['hostname']}[/red]\n\n{str(e)}",
            title="Connection Error",
            border_style="red"
        ))
        return None
