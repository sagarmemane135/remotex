"""
Interactive Shell Connection Module
Handles interactive SSH shell sessions with PTY support.
"""

import sys
import platform

import typer
from rich.console import Console
from rich.panel import Panel
from rich import box

from remotex.ssh_config import parse_ssh_config
from remotex.ssh_client import create_ssh_client

console = Console()

# Platform-specific imports
if platform.system() == 'Windows':
    import msvcrt
    import threading
else:
    import select
    import termios
    import tty


def register_connect_command(app: typer.Typer):
    """Register the connect command to the app."""
    app.command()(connect)


def _display_connection_info(host: str, host_config: dict) -> None:
    """Display connection information panel."""
    console.print(Panel(
        f"[cyan]Host:[/cyan] {host}\n"
        f"[cyan]Server:[/cyan] {host_config.get('user', 'N/A')}@{host_config['hostname']}:{host_config['port']}\n"
        f"[dim]Press Ctrl+D or type 'exit' to close the session[/dim]",
        title="🔌 Starting Interactive Shell",
        border_style="cyan",
        box=box.ROUNDED
    ))
    console.print()


def _read_stdin_windows(channel):
    """Read from stdin on Windows."""
    while True:
        if msvcrt.kbhit():
            char = msvcrt.getch()
            if char == b'\x03':  # Ctrl+C
                break
            channel.send(char)


def _read_channel_windows(channel):
    """Read from channel on Windows."""
    while True:
        try:
            if channel.recv_ready():
                data = channel.recv(1024)
                if len(data) == 0:
                    break
                sys.stdout.buffer.write(data)
                sys.stdout.flush()
            if channel.exit_status_ready():
                break
        except Exception:
            break


def _handle_windows_shell(channel):
    """Handle interactive shell on Windows platform."""
    stdin_thread = threading.Thread(target=_read_stdin_windows, args=(channel,), daemon=True)
    channel_thread = threading.Thread(target=_read_channel_windows, args=(channel,), daemon=True)
    
    stdin_thread.start()
    channel_thread.start()
    
    channel_thread.join()
    stdin_thread.join()


def _handle_channel_input(channel) -> bool:
    """Handle input from channel. Returns False if channel closed."""
    try:
        data = channel.recv(1024)
        if len(data) == 0:
            return False
        sys.stdout.buffer.write(data)
        sys.stdout.flush()
        return True
    except Exception:
        return False


def _handle_stdin_input(channel) -> bool:
    """Handle input from stdin. Returns False if stdin closed."""
    input_data = sys.stdin.read(1)
    if len(input_data) == 0:
        return False
    channel.send(input_data.encode() if isinstance(input_data, str) else input_data)
    return True


def _handle_unix_shell(channel):
    """Handle interactive shell on Unix/Linux platform."""
    oldtty = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        channel.settimeout(0.0)
        
        while True:
            if channel.exit_status_ready():
                break
            
            r, _, _ = select.select([channel, sys.stdin], [], [], 0.1)
            
            if channel in r and not _handle_channel_input(channel):
                break
            
            if sys.stdin in r and not _handle_stdin_input(channel):
                break
                    
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)


def _display_success_message() -> None:
    """Display session closed successfully message."""
    console.print()
    console.print(Panel(
        "[green]Session closed successfully[/green]",
        title="👋 Disconnected",
        border_style="green",
        box=box.ROUNDED
    ))


def _display_error_message(error: Exception) -> None:
    """Display session error message."""
    console.print(Panel(
        f"[red]Error in interactive session[/red]\n\n{str(error)}",
        title="❌ Session Error",
        border_style="red"
    ))


def connect(
    host: str = typer.Argument(..., help="SSH host alias from ~/.ssh/config")
):
    """
    Open an interactive shell session on a remote server.
    Supports PTY for interactive commands like top, htop, vim, etc.
    
    Example:
        python main.py connect myserver
    """
    # Parse SSH config
    host_config = parse_ssh_config(host)
    if not host_config:
        raise typer.Exit(code=1)
    
    # Show connection info
    _display_connection_info(host, host_config)
    
    # Create SSH client
    client = create_ssh_client(host_config)
    if not client:
        raise typer.Exit(code=1)
    
    try:
        # Open interactive shell with PTY
        channel = client.invoke_shell()
        channel.settimeout(0.0)
        
        # Handle platform-specific shell interaction
        if platform.system() == 'Windows':
            _handle_windows_shell(channel)
        else:
            _handle_unix_shell(channel)
        
        _display_success_message()
        
    except Exception as e:
        _display_error_message(e)
        raise typer.Exit(code=1)
    finally:
        client.close()
