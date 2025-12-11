#!/usr/bin/env python3
"""
RemoteX CLI Entry Point
Main command-line interface for RemoteX SSH server management tool.
"""

import logging
import sys
from typing import Optional

import typer
from rich.console import Console

from remotex import __version__
from remotex.commands.server_management import register_server_commands
from remotex.commands.exec_command import register_exec_command
from remotex.commands.connect_command import register_connect_command
from remotex.commands.bulk_operations import register_bulk_commands
from remotex.commands.quick_commands import register_quick_commands
from remotex.commands.config_command import register_config_command
from remotex.commands.group_management import register_group_commands
from remotex.commands.alias_management import register_alias_commands
from remotex.commands.file_transfer import register_file_transfer_commands
from remotex.commands.history_command import app as history_app
from remotex.commands.tunnel_command import app as tunnel_app
from remotex.commands.profiling_command import app as profile_app

console = Console()

# Initialize the main Typer app
app = typer.Typer(
    name="remotex",
    help="🚀 RemoteX - Manage SSH servers and execute commands remotely",
    add_completion=True,  # Enable shell completion
    rich_markup_mode="rich",
)

# Global state for verbose/debug modes
class GlobalState:
    verbose: bool = False
    debug: bool = False
    
global_state = GlobalState()


def version_callback(value: bool):
    """Handle --version flag."""
    if value:
        from remotex import __author__, __description__, __url__
        console.print(f"[bold cyan]RemoteX[/bold cyan] v[bold]{__version__}[/bold]")
        console.print()
        console.print(__description__)
        console.print()
        console.print(f"Author: {__author__}")
        console.print(f"License: MIT")
        console.print(f"Repository: {__url__}")
        raise typer.Exit(0)


@app.callback()
def main_callback(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    debug: bool = typer.Option(False, "--debug", help="Debug mode with detailed logging"),
    version: Optional[bool] = typer.Option(None, "--version", callback=version_callback, is_eager=True, help="Show version and exit")
):
    """
    RemoteX - High-Performance SSH Management CLI
    
    Global options:
      --verbose, -v   Show detailed output
      --debug         Enable debug logging
      --version       Show version information
    """
    global_state.verbose = verbose
    global_state.debug = debug
    
    # Configure logging
    if debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format='[%(levelname)s] %(name)s: %(message)s'
        )
    elif verbose:
        logging.basicConfig(
            level=logging.INFO,
            format='[%(levelname)s] %(message)s'
        )


@app.command(name="version")
def version_command():
    """Show version information."""
    from remotex import __author__, __description__
    
    console.print(f"\n[bold cyan]RemoteX[/bold cyan] v[bold]{__version__}[/bold]\n")
    console.print(f"[dim]{__description__}[/dim]\n")
    console.print(f"[dim]Author: {__author__}[/dim]")
    console.print(f"[dim]License: MIT[/dim]")
    console.print(f"[dim]Repository: https://github.com/sagarmemane135/remotex[/dim]\n")


@app.command(name="examples")
def examples_command():
    """Show common usage examples."""
    examples = """
[bold cyan]RemoteX Usage Examples[/bold cyan]

[bold]Server Management:[/bold]
  remotex list                    # List all servers
  remotex add                     # Add new server (interactive)
  remotex info web01              # Show server details
  remotex config set-default web01  # Set default server

[bold]Remote Execution:[/bold]
  remotex exec web01 "uptime"     # Execute command
  remotex exec web01 "df -h" -p   # Plain output (for piping)
  remotex connect web01           # Interactive shell

[bold]Quick Commands:[/bold]
  remotex uptime                  # Quick uptime (uses default server)
  remotex disk web01              # Check disk usage
  remotex memory web01            # Check memory
  remotex logs web01 nginx -n 100 # View logs

[bold]Bulk Operations (Parallel):[/bold]
  remotex exec-all "uptime"                    # All servers
  remotex exec-all "systemctl status nginx" -p 10  # 10 parallel
  remotex exec-multi "web01,web02,db01" "df -h"    # Specific servers

[bold]CI/CD & Scripting:[/bold]
  remotex exec web01 "test -f /app/ready" -s  # Silent (exit code only)
  remotex exec web01 "hostname" -c            # Compact output
  remotex exec-all "uptime" --no-output       # Summary only

[bold]Advanced:[/bold]
  remotex exec-all "apt update" --timeout 300   # Custom timeout
  remotex exec web01 "uptime" --verbose         # Verbose output
  remotex --debug exec web01 "uptime"           # Debug mode

[dim]For more information, see: remotex --help[/dim]
"""
    console.print(examples)


# Register all command modules
register_server_commands(app)
register_exec_command(app)
register_connect_command(app)
register_bulk_commands(app)
register_quick_commands(app)
register_config_command(app)
register_group_commands(app)
register_alias_commands(app)
register_file_transfer_commands(app)
app.add_typer(history_app)
app.add_typer(tunnel_app)
app.add_typer(profile_app)


def main():
    """Main entry point for the CLI."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)  # Standard SIGINT exit code
    except Exception as e:
        if global_state.debug:
            console.print_exception()
        else:
            console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
