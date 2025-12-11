"""
Config Command Module
Manage RemoteX configuration (default server, aliases, preferences).
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from remotex.config import (
    get_default_server, set_default_server,
    get_server_alias, set_server_alias,
    load_config, save_config,
    validate_config, export_config, import_config
)
from remotex.exit_codes import ExitCode
from remotex.ssh_config import host_exists

console = Console()


def register_config_command(app: typer.Typer):
    """Register config command and subcommands."""
    config_app = typer.Typer(name="config", help="Manage RemoteX configuration")
    
    config_app.command(name="show")(show_config)
    config_app.command(name="set-default")(set_default)
    config_app.command(name="alias")(add_alias)
    config_app.command(name="list-aliases")(list_aliases)
    config_app.command(name="validate")(validate)
    config_app.command(name="export")(export)
    config_app.command(name="import")(import_cmd)
    
    app.add_typer(config_app)


def show_config():
    """Show current configuration."""
    config = load_config()
    
    # Create table
    table = Table(title="🔧 RemoteX Configuration", box=box.ROUNDED)
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
    console.print("\n[dim]Config file: ~/.remotex/config.json[/dim]")


def set_default(
    server: str = typer.Argument(..., help="Server name to set as default")
):
    """Set default server (no need to specify server in commands)."""
    # Verify server exists
    if not host_exists(server):
        console.print(Panel(
            f"[red]Server '{server}' not found in SSH config.[/red]\n\n"
            f"Use: [cyan]remotex list[/cyan] to see available servers\n"
            f"Use: [cyan]remotex add[/cyan] to add a new server",
            title="❌ Server Not Found",
            border_style="red"
        ))
        raise typer.Exit(code=1)
    
    set_default_server(server)
    console.print(Panel(
        f"[green]✓[/green] Default server set to: [bold]{server}[/bold]\n\n"
        f"Now you can use quick commands without specifying the server:\n"
        f"  [cyan]remotex uptime[/cyan]\n"
        f"  [cyan]remotex disk[/cyan]\n"
        f"  [cyan]remotex memory[/cyan]",
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
            f"Use: [cyan]remotex list[/cyan] to see available servers",
            title="❌ Server Not Found",
            border_style="red"
        ))
        raise typer.Exit(code=1)
    
    set_server_alias(alias, server)
    console.print(Panel(
        f"[green]✓[/green] Alias created: [bold]{alias}[/bold] → [bold]{server}[/bold]\n\n"
        f"Now you can use:\n"
        f"  [cyan]remotex uptime {alias}[/cyan]\n"
        f"  [cyan]remotex exec {alias} \"<command>\"[/cyan]",
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
            "[cyan]remotex config alias prod my-production-server[/cyan]",
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


def validate():
    """Validate configuration file."""
    is_valid, errors = validate_config()
    
    if is_valid:
        console.print(Panel(
            "[green]✓ Configuration is valid[/green]",
            title="✓ Validation Success",
            border_style="green",
            box=box.ROUNDED
        ))
    else:
        error_text = "\n".join(f"  • {error}" for error in errors)
        console.print(Panel(
            f"[red]Configuration validation failed:[/red]\n\n{error_text}",
            title="❌ Validation Errors",
            border_style="red",
            box=box.ROUNDED
        ))
        raise typer.Exit(code=ExitCode.CONFIG_ERROR)


def export(
    output_file: str = typer.Option(None, "--output", "-o", help="Output file path (default: auto-generated)")
):
    """Export configuration to a JSON file."""
    try:
        exported_path = export_config(output_file)
        console.print(Panel(
            f"[green]✓[/green] Configuration exported to:\n[cyan]{exported_path}[/cyan]",
            title="✓ Export Success",
            border_style="green",
            box=box.ROUNDED
        ))
    except Exception as e:
        console.print(Panel(
            f"[red]Export failed:[/red] {str(e)}",
            title="❌ Export Error",
            border_style="red",
            box=box.ROUNDED
        ))
        raise typer.Exit(code=ExitCode.CONFIG_FILE_ERROR)


def import_cmd(
    input_file: str = typer.Argument(..., help="Path to JSON config file to import"),
    merge: bool = typer.Option(False, "--merge", "-m", help="Merge with existing config instead of replacing")
):
    """Import configuration from a JSON file."""
    try:
        success = import_config(input_file, merge=merge)
        if success:
            mode = "merged with" if merge else "replaced by"
            console.print(Panel(
                f"[green]✓[/green] Configuration {mode} imported file:\n[cyan]{input_file}[/cyan]",
                title="✓ Import Success",
                border_style="green",
                box=box.ROUNDED
            ))
        else:
            console.print(Panel(
                f"[red]Import failed:[/red] File not found or invalid JSON\n[cyan]{input_file}[/cyan]",
                title="❌ Import Error",
                border_style="red",
                box=box.ROUNDED
            ))
            raise typer.Exit(code=ExitCode.CONFIG_FILE_ERROR)
    except Exception as e:
        console.print(Panel(
            f"[red]Import failed:[/red] {str(e)}",
            title="❌ Import Error",
            border_style="red",
            box=box.ROUNDED
        ))
        raise typer.Exit(code=ExitCode.CONFIG_FILE_ERROR)
