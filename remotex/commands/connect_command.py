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
    console.print(Panel(
        f"[cyan]Host:[/cyan] {host}\n"
        f"[cyan]Server:[/cyan] {host_config.get('user', 'N/A')}@{host_config['hostname']}:{host_config['port']}\n"
        f"[dim]Press Ctrl+D or type 'exit' to close the session[/dim]",
        title="🔌 Starting Interactive Shell",
        border_style="cyan",
        box=box.ROUNDED
    ))
    console.print()
    
    # Create SSH client
    client = create_ssh_client(host_config)
    if not client:
        raise typer.Exit(code=1)
    
    try:
        # Open interactive shell with PTY
        channel = client.invoke_shell()
        channel.settimeout(0.0)
        
        if platform.system() == 'Windows':
            # Windows implementation
            def read_stdin():
                while True:
                    if msvcrt.kbhit():
                        char = msvcrt.getch()
                        if char == b'\x03':  # Ctrl+C
                            break
                        channel.send(char)
            
            def read_channel():
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
            
            # Start threads for reading
            stdin_thread = threading.Thread(target=read_stdin, daemon=True)
            channel_thread = threading.Thread(target=read_channel, daemon=True)
            
            stdin_thread.start()
            channel_thread.start()
            
            # Wait for channel to close
            channel_thread.join()
            stdin_thread.join()
        else:
            # Unix/Linux implementation
            oldtty = termios.tcgetattr(sys.stdin)
            try:
                tty.setraw(sys.stdin.fileno())
                tty.setcbreak(sys.stdin.fileno())
                channel.settimeout(0.0)
                
                while True:
                    # Check if channel is still open
                    if channel.exit_status_ready():
                        break
                    
                    # Use select to handle I/O
                    r, w, e = select.select([channel, sys.stdin], [], [], 0.1)
                    
                    if channel in r:
                        try:
                            data = channel.recv(1024)
                            if len(data) == 0:
                                break
                            sys.stdout.buffer.write(data)
                            sys.stdout.flush()
                        except Exception:
                            break
                    
                    if sys.stdin in r:
                        input_data = sys.stdin.read(1)
                        if len(input_data) == 0:
                            break
                        channel.send(input_data.encode() if isinstance(input_data, str) else input_data)
                        
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)
        
        console.print()
        console.print(Panel(
            "[green]Session closed successfully[/green]",
            title="👋 Disconnected",
            border_style="green",
            box=box.ROUNDED
        ))
        
    except Exception as e:
        console.print(Panel(
            f"[red]Error in interactive session[/red]\n\n{str(e)}",
            title="❌ Session Error",
            border_style="red"
        ))
        raise typer.Exit(code=1)
    finally:
        client.close()
