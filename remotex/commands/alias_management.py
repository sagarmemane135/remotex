"""
RemoteX Command Alias Management
Define and execute reusable command aliases
"""

import typer
from rich.console import Console
from rich.table import Table
from typing import Optional

from remotex import config

console = Console()
alias_app = typer.Typer(help="Manage command aliases")


@alias_app.command(name="add")
def alias_add(
    alias_name: str = typer.Argument(..., help="Alias name"),
    command: str = typer.Argument(..., help="Command to alias")
):
    """Create or update a command alias."""
    config.add_command_alias(alias_name, command)
    console.print(f"[green]✓[/green] Alias '[cyan]{alias_name}[/cyan]' created")
    console.print(f"  Command: [yellow]{command}[/yellow]")
    console.print(f"  Usage: [dim]remotex run {alias_name} <host>[/dim]")


@alias_app.command(name="list")
def alias_list():
    """List all command aliases."""
    aliases = config.get_command_aliases()
    
    if not aliases:
        console.print("[yellow]No aliases defined yet[/yellow]")
        console.print("Create one with: [cyan]remotex alias add <name> '<command>'[/cyan]")
        return
    
    table = Table(title="Command Aliases", show_header=True)
    table.add_column("Alias", style="cyan", no_wrap=True)
    table.add_column("Command", style="yellow")
    
    for alias_name, command in sorted(aliases.items()):
        table.add_row(alias_name, command)
    
    console.print(table)


@alias_app.command(name="show")
def alias_show(
    alias_name: str = typer.Argument(..., help="Alias name")
):
    """Show details of an alias."""
    command = config.get_command_alias(alias_name)
    
    if not command:
        console.print(f"[red]✗[/red] Alias '[cyan]{alias_name}[/cyan]' not found")
        raise typer.Exit(1)
    
    console.print(f"[cyan]{alias_name}[/cyan] → [yellow]{command}[/yellow]")


@alias_app.command(name="remove")
def alias_remove(
    alias_name: str = typer.Argument(..., help="Alias name"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation")
):
    """Remove a command alias."""
    aliases = config.get_command_aliases()
    
    if alias_name not in aliases:
        console.print(f"[red]✗[/red] Alias '[cyan]{alias_name}[/cyan]' not found")
        raise typer.Exit(1)
    
    if not force:
        command = aliases[alias_name]
        console.print(f"[yellow]⚠[/yellow]  About to remove alias '[cyan]{alias_name}[/cyan]'")
        console.print(f"  Command: [yellow]{command}[/yellow]")
        confirm = typer.confirm("Are you sure?")
        if not confirm:
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(0)
    
    config.remove_command_alias(alias_name)
    console.print(f"[green]✓[/green] Alias '[cyan]{alias_name}[/cyan]' removed")


def register_alias_commands(app: typer.Typer):
    """Register alias management commands."""
    app.add_typer(alias_app, name="alias")
