"""
Quick Commands Module
Common DevOps shortcuts and frequently used commands.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich import box

from typing import Optional

from remotex.commands.exec_command import exec_command
from remotex.config import resolve_server

console = Console()


def register_quick_commands(app: typer.Typer):
    """Register quick shortcut commands."""
    app.command(name="uptime")(uptime)
    app.command(name="disk")(disk)
    app.command(name="memory")(memory)
    app.command(name="cpu")(cpu)
    app.command(name="processes")(processes)
    app.command(name="restart")(restart_service)
    app.command(name="status")(service_status)
    app.command(name="logs")(logs)


def uptime(
    host: Optional[str] = typer.Argument(None, help="Server alias (uses default if not specified)"),
    compact: bool = typer.Option(True, "--compact/--normal", "-c/-n", help="Compact output (default for quick commands)")
):
    """Quick uptime check."""
    host = resolve_server(host)
    if not host:
        console.print("[red]No server specified and no default server set. Use: remotex config set-default <server>[/red]")
        raise typer.Exit(code=1)
    exec_command(host, "uptime", plain=False, compact=compact, silent=False)


def disk(
    host: Optional[str] = typer.Argument(None, help="Server alias (uses default if not specified)"),
    compact: bool = typer.Option(True, "--compact/--normal", "-c/-n", help="Compact output")
):
    """Quick disk usage check."""
    host = resolve_server(host)
    if not host:
        console.print("[red]No server specified and no default server set. Use: remotex config set-default <server>[/red]")
        raise typer.Exit(code=1)
    exec_command(host, "df -h", plain=False, compact=compact, silent=False)


def memory(
    host: Optional[str] = typer.Argument(None, help="Server alias (uses default if not specified)"),
    compact: bool = typer.Option(True, "--compact/--normal", "-c/-n", help="Compact output")
):
    """Quick memory usage check."""
    host = resolve_server(host)
    if not host:
        console.print("[red]No server specified and no default server set. Use: remotex config set-default <server>[/red]")
        raise typer.Exit(code=1)
    exec_command(host, "free -h", plain=False, compact=compact, silent=False)


def cpu(
    host: Optional[str] = typer.Argument(None, help="Server alias (uses default if not specified)"),
    compact: bool = typer.Option(True, "--compact/--normal", "-c/-n")
):
    """Quick CPU info."""
    host = resolve_server(host)
    if not host:
        console.print("[red]No server specified and no default server set.[/red]")
        raise typer.Exit(code=1)
    exec_command(host, "lscpu | head -20", plain=False, compact=compact, silent=False)


def processes(
    host: Optional[str] = typer.Argument(None, help="Server alias (uses default if not specified)"),
    limit: int = typer.Option(15, "--limit", "-n", help="Number of processes to show"),
    compact: bool = typer.Option(True, "--compact/--normal", "-c/-n")
):
    """Quick process list."""
    host = resolve_server(host)
    if not host:
        console.print("[red]No server specified and no default server set.[/red]")
        raise typer.Exit(code=1)
    exec_command(host, f"ps aux --sort=-%mem | head -{limit}", plain=False, compact=compact, silent=False)


def restart_service(
    host: Optional[str] = typer.Argument(None, help="Server alias (uses default if not specified)"),
    service: str = typer.Argument(..., help="Service name"),
    compact: bool = typer.Option(True, "--compact/--normal", "-c/-n")
):
    """Quick service restart."""
    host = resolve_server(host)
    if not host:
        console.print("[red]No server specified and no default server set.[/red]")
        raise typer.Exit(code=1)
    exec_command(host, f"sudo systemctl restart {service} && sudo systemctl status {service}", plain=False, compact=compact, silent=False)


def service_status(
    host: Optional[str] = typer.Argument(None, help="Server alias (uses default if not specified)"),
    service: str = typer.Argument(..., help="Service name"),
    compact: bool = typer.Option(True, "--compact/--normal", "-c/-n")
):
    """Quick service status check."""
    host = resolve_server(host)
    if not host:
        console.print("[red]No server specified and no default server set.[/red]")
        raise typer.Exit(code=1)
    exec_command(host, f"sudo systemctl status {service}", plain=False, compact=compact, silent=False)


def logs(
    host: Optional[str] = typer.Argument(None, help="Server alias (uses default if not specified)"),
    service: str = typer.Argument(..., help="Service name or log file path"),
    lines: int = typer.Option(50, "--lines", "-n", help="Number of lines to show"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output"),
    compact: bool = typer.Option(True, "--compact/--normal", "-c/-n")
):
    """Quick log viewing."""
    host = resolve_server(host)
    if not host:
        console.print("[red]No server specified and no default server set.[/red]")
        raise typer.Exit(code=1)
    
    if '/' in service or service.endswith('.log'):
        # It's a file path
        cmd = f"tail -n {lines} {service}"
    else:
        # It's a service name
        cmd = f"sudo journalctl -u {service} -n {lines}"
    
    if follow:
        cmd += " -f"
    
    exec_command(host, cmd, plain=False, compact=compact, silent=False)
