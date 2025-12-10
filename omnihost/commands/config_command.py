"""
Config Command Module
Manage OmniHost configuration (default server, aliases, preferences).
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from omnihost.config import (
    get_default_server, set_default_server,
    get_server_alias, set_server_alias,
    load_config, save_config
)
from omnihost.ssh_config import host_exists

console = Console()


def register_config_command(app: typer.Typer):
    """Register config command and subcommands."""
    config_app = typer.Typer(name="config", help="Manage OmniHost configuration")
    
    config_app.command(name="show")(show_config)
    config_app.command(name="set-default")(set_default)
    config_app.command(name="alias")(add_alias)
    config_app.command(name="list-aliases")(list_aliases)
    
    app.add_typer(config_app)


def show_config():
    """Show current configuration."""
    config = load_config()
    
    # Create table
    table = Table(title="🔧 OmniHost Configuration", box=box.ROUNDED)
    table.add_column("Setting", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    
    # Add rows
    default_server = config.get("default_server") or "[dim]Not set[/dim]"
    table.add_row("Default Server", default_server)
    table.add_row("Output Mode", config.get("output_mode", "normal"))
    table.add_row("Parallel Connections", str(config.get("parallel_connections", 5)))
    table.add_row("Timeout (seconds)", str(config.get("timeout", 30)))
    
    # Show aliases
    aliases = config.get("aliases", {})
    if aliases:
        table.add_row("", "")  # Separator
        table.add_row("[bold]Aliases[/bold]", "")
        for alias, server in aliases.items():
            table.add_row(f"  {alias}", server)
    
    console.print(table)
    console.print("\n[dim]Config file: ~/.omnihost/config.json[/dim]")


def set_default(
    server: str = typer.Argument(..., help="Server name to set as default")
):
    """Set default server (no need to specify server in commands)."""
    # Verify server exists
    if not host_exists(server):
        console.print(Panel(
            f"[red]Server '{server}' not found in SSH config.[/red]\n\n"
            f"Use: [cyan]omnihost list[/cyan] to see available servers\n"
            f"Use: [cyan]omnihost add[/cyan] to add a new server",
            title="❌ Server Not Found",
            border_style="red"
        ))
        raise typer.Exit(code=1)
    
    set_default_server(server)
    console.print(Panel(
        f"[green]✓[/green] Default server set to: [bold]{server}[/bold]\n\n"
        f"Now you can use quick commands without specifying the server:\n"
        f"  [cyan]omnihost uptime[/cyan]\n"
        f"  [cyan]omnihost disk[/cyan]\n"
        f"  [cyan]omnihost memory[/cyan]",
        title="✓ Configuration Updated",
        border_style="green",
        box=box.ROUNDED
    ))


def add_alias(
    alias: str = typer.Argument(..., help="Short alias name (e.g., 'prod', 'staging')"),
    server: str = typer.Argument(..., help="Full server name")
):
    """Add a server alias (shortcut)."""
    # Verify server exists
    if not host_exists(server):
        console.print(Panel(
            f"[red]Server '{server}' not found in SSH config.[/red]\n\n"
            f"Use: [cyan]omnihost list[/cyan] to see available servers",
            title="❌ Server Not Found",
            border_style="red"
        ))
        raise typer.Exit(code=1)
    
    set_server_alias(alias, server)
    console.print(Panel(
        f"[green]✓[/green] Alias created: [bold]{alias}[/bold] → [bold]{server}[/bold]\n\n"
        f"Now you can use:\n"
        f"  [cyan]omnihost uptime {alias}[/cyan]\n"
        f"  [cyan]omnihost exec {alias} \"<command>\"[/cyan]",
        title="✓ Alias Created",
        border_style="green",
        box=box.ROUNDED
    ))


def list_aliases():
    """List all configured aliases."""
    config = load_config()
    aliases = config.get("aliases", {})
    
    if not aliases:
        console.print(Panel(
            "[yellow]No aliases configured yet.[/yellow]\n\n"
            "Create an alias with:\n"
            "[cyan]omnihost config alias prod my-production-server[/cyan]",
            title="📋 Aliases",
            border_style="yellow"
        ))
        return
    
    table = Table(title="📋 Server Aliases", box=box.ROUNDED)
    table.add_column("Alias", style="cyan", no_wrap=True)
    table.add_column("→", style="dim")
    table.add_column("Server", style="green")
    
    for alias, server in sorted(aliases.items()):
        table.add_row(alias, "→", server)
    
    console.print(table)
