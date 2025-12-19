"""
SSH Tunnel Management
"""

import typer
import subprocess
import json
from typing import Optional, Dict
from rich.table import Table
from rich.panel import Panel

from remotex.config import CONFIG_DIR
from remotex.utils import console

app = typer.Typer(name="tunnel", help="Manage SSH tunnels")

TUNNELS_FILE = CONFIG_DIR / "tunnels.json"

# Constants
MSG_NO_ACTIVE_TUNNELS = "[yellow]No active tunnels.[/yellow]"


def load_tunnels() -> Dict:
    """Load active tunnels from file."""
    if not TUNNELS_FILE.exists():
        return {}
    
    try:
        with open(TUNNELS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, PermissionError):
        return {}


def save_tunnels(tunnels: Dict):
    """Save tunnels to file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(TUNNELS_FILE, 'w') as f:
        json.dump(tunnels, f, indent=2)


def get_tunnel_key(host: str, tunnel_type: str, local_port: int) -> str:
    """Generate a unique key for a tunnel."""
    return f"{host}:{tunnel_type}:{local_port}"


def _validate_tunnel_type(tunnel_type: str) -> bool:
    """Validate tunnel type. Returns True if valid."""
    if tunnel_type not in ["local", "remote", "dynamic"]:
        console.print(f"[red]Invalid tunnel type: {tunnel_type}. Must be local, remote, or dynamic.[/red]")
        return False
    return True


def _build_ssh_command(tunnel_type: str, local_port: int, remote_host: str, remote_port: int,
                        host_config: dict, background: bool) -> list:
    """Build SSH command for tunnel."""
    ssh_cmd = ["ssh", "-N"]  # -N: don't execute remote command
    
    if tunnel_type == "local":
        ssh_cmd.extend(["-L", f"{local_port}:{remote_host}:{remote_port}"])
    elif tunnel_type == "remote":
        ssh_cmd.extend(["-R", f"{remote_port}:{remote_host}:{local_port}"])
    elif tunnel_type == "dynamic":
        ssh_cmd.extend(["-D", str(local_port)])
    
    # Add SSH config options
    if host_config.get("identityfile"):
        ssh_cmd.extend(["-i", host_config["identityfile"]])
    if host_config.get("port") and host_config["port"] != 22:
        ssh_cmd.extend(["-p", str(host_config["port"])])
    
    # Add host connection
    user_host = f"{host_config.get('user', '')}@{host_config['hostname']}" if host_config.get('user') else host_config['hostname']
    ssh_cmd.append(user_host)
    
    if background:
        ssh_cmd.append("-f")  # Background mode
    
    return ssh_cmd


def _display_tunnel_info(tunnel_type: str, local_port: int, remote_host: str, remote_port: int, host: str, pid: int) -> None:
    """Display tunnel information after creation."""
    console.print("[green]✓ Tunnel created:[/green]")
    if tunnel_type == "local":
        console.print(f"  Local port {local_port} -> {host}:{remote_host}:{remote_port}")
    elif tunnel_type == "remote":
        console.print(f"  Remote port {remote_port} -> {host}:{remote_host}:{local_port}")
    elif tunnel_type == "dynamic":
        console.print(f"  SOCKS proxy on localhost:{local_port}")
    console.print(f"  PID: {pid}")


def _start_tunnel_background(ssh_cmd: list, host: str, tunnel_type: str, local_port: int,
                             remote_host: str, remote_port: int, tunnel_key: str) -> None:
    """Start tunnel in background mode."""
    import time
    
    process = subprocess.Popen(ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait a moment to check if it started successfully
    time.sleep(0.5)
    if process.poll() is not None:
        # Process exited, likely an error
        stderr = process.stderr.read().decode() if process.stderr else ""
        console.print("[red]Failed to create tunnel:[/red]")
        console.print(f"[red]{stderr}[/red]")
        raise typer.Exit(1)
    
    # Save tunnel info
    tunnels = load_tunnels()
    tunnels[tunnel_key] = {
        "host": host,
        "type": tunnel_type,
        "local_port": local_port,
        "remote_host": remote_host,
        "remote_port": remote_port,
        "pid": process.pid,
        "command": " ".join(ssh_cmd)
    }
    save_tunnels(tunnels)
    
    _display_tunnel_info(tunnel_type, local_port, remote_host, remote_port, host, process.pid)


def _start_tunnel_foreground(ssh_cmd: list) -> None:
    """Start tunnel in foreground mode."""
    console.print("[green]Tunnel running in foreground. Press Ctrl+C to stop.[/green]")
    process = subprocess.Popen(ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        process.wait()
    except KeyboardInterrupt:
        process.terminate()
        console.print("\n[yellow]Tunnel stopped.[/yellow]")


@app.command("create")
def tunnel_create(
    host: str = typer.Argument(..., help="Server alias"),
    local_port: int = typer.Argument(..., help="Local port"),
    remote_host: str = typer.Option("localhost", "--remote-host", "-r", help="Remote host"),
    remote_port: int = typer.Option(None, "--remote-port", help="Remote port (defaults to local_port)"),
    tunnel_type: str = typer.Option("local", "--type", "-t", help="Tunnel type: local, remote, dynamic"),
    background: bool = typer.Option(True, "--background/--foreground", help="Run in background"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview tunnel without creating")
):
    """
    Create an SSH tunnel.
    
    Tunnel types:
    - local: -L (local port forwarding)
    - remote: -R (remote port forwarding)
    - dynamic: -D (dynamic SOCKS proxy)
    """
    if remote_port is None:
        remote_port = local_port
    
    if not _validate_tunnel_type(tunnel_type):
        raise typer.Exit(1)
    
    # Get SSH config for host
    from remotex.ssh_config import parse_ssh_config
    host_config = parse_ssh_config(host)
    
    if not host_config:
        console.print(f"[red]Host '{host}' not found in SSH config.[/red]")
        raise typer.Exit(1)
    
    # Build SSH command
    ssh_cmd = _build_ssh_command(tunnel_type, local_port, remote_host, remote_port, host_config, background)
    
    if dry_run:
        console.print("[yellow]Would create tunnel:[/yellow]")
        console.print(f"[cyan]{' '.join(ssh_cmd)}[/cyan]")
        return
    
    try:
        # Check if tunnel already exists
        tunnels = load_tunnels()
        tunnel_key = get_tunnel_key(host, tunnel_type, local_port)
        
        if tunnel_key in tunnels:
            console.print(f"[yellow]Tunnel already exists. Use 'tunnel stop {host} {local_port}' first.[/yellow]")
            raise typer.Exit(1)
        
        # Start tunnel
        if background:
            _start_tunnel_background(ssh_cmd, host, tunnel_type, local_port, remote_host, remote_port, tunnel_key)
        else:
            _start_tunnel_foreground(ssh_cmd)
    
    except Exception as e:
        console.print(f"[red]Error creating tunnel: {e}[/red]")
        raise typer.Exit(1)


def _check_process_status(pid: int) -> str:
    """Check if process is running."""
    try:
        import os
        os.kill(pid, 0)  # Check if process exists
        return "✅ Active"
    except OSError:
        return "❌ Dead"


def _get_remote_display(tunnel_type: str, remote_host: str, remote_port: int) -> str:
    """Get remote display string based on tunnel type."""
    if tunnel_type == "dynamic":
        return "SOCKS"
    if tunnel_type in ["local", "remote"]:
        return f"{remote_host}:{remote_port}"
    return "-"


@app.command("list")
def tunnel_list():
    """List all active tunnels."""
    tunnels = load_tunnels()
    
    if not tunnels:
        console.print(MSG_NO_ACTIVE_TUNNELS)
        return
    
    table = Table(title="Active SSH Tunnels", show_header=True, header_style="bold magenta")
    table.add_column("Host", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Local Port", style="yellow")
    table.add_column("Remote", style="blue")
    table.add_column("PID", style="magenta")
    table.add_column("Status", width=10)
    
    for key, tunnel in tunnels.items():
        host = tunnel.get("host", "")
        tunnel_type = tunnel.get("type", "")
        local_port = tunnel.get("local_port", "")
        remote_host = tunnel.get("remote_host", "")
        remote_port = tunnel.get("remote_port", "")
        pid = tunnel.get("pid", "")
        
        status = _check_process_status(pid)
        remote = _get_remote_display(tunnel_type, remote_host, remote_port)
        
        table.add_row(
            host,
            tunnel_type,
            str(local_port),
            remote,
            str(pid),
            status
        )
    
    console.print(table)


def _stop_tunnel_process(pid: int, host: str, port: int) -> None:
    """Stop a tunnel process by PID."""
    try:
        import os
        import signal
        os.kill(pid, signal.SIGTERM)
        console.print(f"[green]✓ Stopped tunnel: {host}:{port} (PID: {pid})[/green]")
    except OSError:
        console.print(f"[yellow]Process {pid} not found (may have already stopped).[/yellow]")


@app.command("stop")
def tunnel_stop(
    host: str = typer.Argument(..., help="Server alias"),
    local_port: Optional[int] = typer.Argument(None, help="Local port (optional, stops all if not specified)")
):
    """Stop an SSH tunnel."""
    tunnels = load_tunnels()
    
    if not tunnels:
        console.print(MSG_NO_ACTIVE_TUNNELS)
        return
    
    # Find matching tunnels
    to_remove = []
    for key, tunnel in tunnels.items():
        if tunnel.get("host") == host:
            if local_port is None or tunnel.get("local_port") == local_port:
                to_remove.append((key, tunnel))
    
    if not to_remove:
        console.print(f"[yellow]No tunnels found for host '{host}'" + 
                     (f" on port {local_port}" if local_port else "") + ".[/yellow]")
        return
    
    for key, tunnel in to_remove:
        pid = tunnel.get("pid")
        if pid:
            _stop_tunnel_process(pid, host, tunnel.get('local_port'))
        
        del tunnels[key]
    
    save_tunnels(tunnels)


@app.command("stop-all")
def tunnel_stop_all(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation")
):
    """Stop all active tunnels."""
    tunnels = load_tunnels()
    
    if not tunnels:
        console.print(MSG_NO_ACTIVE_TUNNELS)
        return
    
    if not confirm:
        console.print(f"[yellow]This will stop {len(tunnels)} tunnel(s).[/yellow]")
        response = typer.prompt("Are you sure? (yes/no)", default="no")
        if response.lower() != "yes":
            console.print("[yellow]Cancelled.[/yellow]")
            return
    
    for key, tunnel in tunnels.items():
        pid = tunnel.get("pid")
        if pid:
            try:
                import os
                import signal
                os.kill(pid, signal.SIGTERM)
            except OSError:
                pass
    
    save_tunnels({})
    console.print("[green]✓ Stopped all tunnels.[/green]")

