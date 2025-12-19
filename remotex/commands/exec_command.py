"""
Execute Command Module
Handles remote command execution on SSH servers.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich import box

from remotex.ssh_config import parse_ssh_config
from remotex.ssh_client import create_ssh_client
from remotex.history import add_to_history

console = Console()


def register_exec_command(app: typer.Typer):
    """Register the exec command to the app."""
    app.command(name="exec")(exec_command)


def _display_connection_panel(host: str, host_config: dict, command: str, plain: bool, compact: bool, silent: bool) -> None:
    """Display connection information based on output mode."""
    if not plain and not compact and not silent:
        console.print(Panel(
            f"[cyan]Host:[/cyan] {host}\n"
            f"[cyan]Server:[/cyan] {host_config.get('user', 'N/A')}@{host_config['hostname']}:{host_config['port']}\n"
            f"[cyan]Command:[/cyan] {command}",
            title="🔌 Connecting",
            border_style="cyan",
            box=box.ROUNDED
        ))
    elif plain and not compact and not silent:
        console.print(f"Connecting to {host}...")


def _display_silent_output(output: str, error: str) -> None:
    """Display output in silent mode (no output)."""
    pass  # Silent mode - no output


def _display_compact_output(output: str, error: str) -> None:
    """Display output in compact mode."""
    if output:
        console.print(output.strip())
    if error:
        console.print(f"[red]{error.strip()}[/red]")


def _display_plain_output(output: str, error: str) -> None:
    """Display output in plain mode."""
    if output:
        console.print(output, end='')
    if error:
        console.print(error, end='', style="red")


def _build_formatted_output(output: str, error: str) -> str:
    """Build formatted output text with colors."""
    output_text = ""
    
    if output:
        output_text += f"[green]{output.rstrip()}[/green]"
    
    if error:
        if output_text:
            output_text += "\n\n"
        output_text += f"[red bold]Errors:[/red bold]\n[red]{error.rstrip()}[/red]"
    
    return output_text


def _display_formatted_output(output: str, error: str, exit_status: int) -> None:
    """Display output in formatted mode with panels."""
    if output or error:
        output_text = _build_formatted_output(output, error)
        
        if exit_status == 0:
            title = "✓ Output"
            border_style = "green"
        else:
            title = f"⚠ Output (Exit Code: {exit_status})"
            border_style = "yellow"
        
        console.print(Panel(
            output_text,
            title=title,
            border_style=border_style,
            box=box.ROUNDED,
            expand=False
        ))
    else:
        console.print(Panel(
            "[dim]Command executed successfully with no output[/dim]",
            title="✓ Complete",
            border_style="green",
            box=box.ROUNDED
        ))


def _display_output(output: str, error: str, exit_status: int, plain: bool, compact: bool, silent: bool) -> None:
    """Display output based on the selected mode."""
    if silent:
        _display_silent_output(output, error)
    elif compact:
        _display_compact_output(output, error)
    elif plain:
        _display_plain_output(output, error)
    else:
        _display_formatted_output(output, error, exit_status)


def _log_to_history(command: str, host: str, exit_status: int, plain: bool, compact: bool) -> None:
    """Log command execution to history."""
    try:
        add_to_history(
            command="exec",
            args=[command],
            hosts=[host],
            success=(exit_status == 0),
            metadata={"exit_code": exit_status, "plain": plain, "compact": compact}
        )
    except Exception:
        pass  # Don't fail command if history fails


def _display_error(error: Exception) -> None:
    """Display execution error message."""
    console.print(Panel(
        f"[red]Error executing command[/red]\n\n{str(error)}",
        title="❌ Execution Error",
        border_style="red"
    ))


def exec_command(
    host: str = typer.Argument(..., help="SSH host alias from ~/.ssh/config"),
    command: str = typer.Argument(..., help="Command to execute on remote host"),
    plain: bool = typer.Option(False, "--plain", "-p", help="Plain output without formatting"),
    compact: bool = typer.Option(False, "--compact", "-c", help="Compact output (minimal formatting)"),
    silent: bool = typer.Option(False, "--silent", "-s", help="Silent mode (only exit codes)")
):
    """
    Execute a command on a remote server and print the output.
    
    Example:
        remotex exec myserver "ls -la"           # Full formatted output
        remotex exec myserver "df -h" -p         # Plain output
        remotex exec myserver "uptime" -c        # Compact (fast)
        remotex exec myserver "test -f /tmp/x" -s  # Silent (exit code only)
    """
    # Get host info for display
    host_config = parse_ssh_config(host)
    if not host_config:
        raise typer.Exit(code=1)
    
    # Show connection info
    _display_connection_panel(host, host_config, command, plain, compact, silent)
    
    # Create SSH client
    client = create_ssh_client(host_config)
    if not client:
        raise typer.Exit(code=1)
    
    try:
        if not plain and not compact and not silent:
            console.print()
        
        # Execute command
        _, stdout, stderr = client.exec_command(command)
        
        # Read output
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        exit_status = stdout.channel.recv_exit_status()
        
        # Display output based on mode
        _display_output(output, error, exit_status, plain, compact, silent)
        
        # Add to history
        _log_to_history(command, host, exit_status, plain, compact)
        
        # Exit with command's exit status
        if exit_status != 0:
            raise typer.Exit(code=exit_status)
            
    except Exception as e:
        _display_error(e)
        raise typer.Exit(code=1)
    finally:
        client.close()
