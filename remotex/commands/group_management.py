"""
RemoteX Group Management Commands
Manage server groups for bulk operations
"""

import typer
from rich.console import Console
from rich.table import Table
from typing import List

from remotex import config
from remotex.ssh_config import get_all_hosts

console = Console()
group_app = typer.Typer(help="Manage server groups")


@group_app.command(name="add")
def group_add(
    group_name: str = typer.Argument(..., help="Group name"),
    servers: str = typer.Argument(..., help="Comma-separated list of servers")
):
    """Create or update a server group."""
    server_list = [s.strip() for s in servers.split(",")]
    
    # Validate servers exist
    all_servers_list = get_all_hosts()
    all_servers = {s['alias']: s for s in all_servers_list}
    invalid_servers = [s for s in server_list if s not in all_servers]
    
    if invalid_servers:
        console.print(f"[red]✗[/red] Invalid servers: {', '.join(invalid_servers)}")
        console.print(f"[yellow]Use 'remotex list' to see available servers[/yellow]")
        raise typer.Exit(1)
    
    config.add_group(group_name, server_list)
    console.print(f"[green]✓[/green] Group '[cyan]{group_name}[/cyan]' created with {len(server_list)} servers")
    
    # Show the group
    table = Table(title=f"Group: {group_name}", show_header=False)
    for server in server_list:
        table.add_row(f"• {server}")
    console.print(table)


@group_app.command(name="list")
def group_list():
    """List all server groups."""
    groups = config.get_groups()
    
    if not groups:
        console.print("[yellow]No groups defined yet[/yellow]")
        console.print("Create one with: [cyan]remotex group add <name> <servers>[/cyan]")
        return
    
    table = Table(title="Server Groups", show_header=True)
    table.add_column("Group", style="cyan", no_wrap=True)
    table.add_column("Servers", style="white")
    table.add_column("Count", justify="right", style="green")
    
    for group_name, servers in sorted(groups.items()):
        table.add_row(
            group_name,
            ", ".join(servers),
            str(len(servers))
        )
    
    console.print(table)


@group_app.command(name="show")
def group_show(
    group_name: str = typer.Argument(..., help="Group name")
):
    """Show servers in a group."""
    servers = config.get_group_servers(group_name)
    
    if not servers:
        console.print(f"[red]✗[/red] Group '[cyan]{group_name}[/cyan]' not found")
        raise typer.Exit(1)
    
    table = Table(title=f"Group: {group_name}", show_header=True)
    table.add_column("Server", style="cyan")
    table.add_column("Tags", style="yellow")
    
    all_servers_list = get_all_hosts()
    all_servers = {s['alias']: s for s in all_servers_list}
    for server in servers:
        tags = config.get_server_tags(server)
        server_info = all_servers.get(server, {})
        host = server_info.get('hostname', 'N/A')
        table.add_row(
            f"{server} ({host})",
            ", ".join(tags) if tags else "-"
        )
    
    console.print(table)


@group_app.command(name="add-server")
def group_add_server(
    group_name: str = typer.Argument(..., help="Group name"),
    server: str = typer.Argument(..., help="Server to add")
):
    """Add a server to an existing group."""
    all_servers_list = get_all_hosts()
    all_servers = {s['alias']: s for s in all_servers_list}
    
    if server not in all_servers:
        console.print(f"[red]✗[/red] Server '[cyan]{server}[/cyan]' not found")
        raise typer.Exit(1)
    
    config.add_server_to_group(group_name, server)
    console.print(f"[green]✓[/green] Added '[cyan]{server}[/cyan]' to group '[cyan]{group_name}[/cyan]'")


@group_app.command(name="remove-server")
def group_remove_server(
    group_name: str = typer.Argument(..., help="Group name"),
    server: str = typer.Argument(..., help="Server to remove")
):
    """Remove a server from a group."""
    config.remove_server_from_group(group_name, server)
    console.print(f"[green]✓[/green] Removed '[cyan]{server}[/cyan]' from group '[cyan]{group_name}[/cyan]'")


@group_app.command(name="remove")
def group_remove(
    group_name: str = typer.Argument(..., help="Group name"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation")
):
    """Remove a group."""
    groups = config.get_groups()
    
    if group_name not in groups:
        console.print(f"[red]✗[/red] Group '[cyan]{group_name}[/cyan]' not found")
        raise typer.Exit(1)
    
    if not force:
        servers = config.get_group_servers(group_name)
        console.print(f"[yellow]⚠[/yellow]  About to remove group '[cyan]{group_name}[/cyan]' with {len(servers)} servers")
        confirm = typer.confirm("Are you sure?")
        if not confirm:
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(0)
    
    config.remove_group(group_name)
    console.print(f"[green]✓[/green] Group '[cyan]{group_name}[/cyan]' removed")


def register_group_commands(app: typer.Typer):
    """Register group management commands."""
    app.add_typer(group_app, name="group")
