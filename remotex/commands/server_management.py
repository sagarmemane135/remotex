"""
Server Management Commands
Handles listing, adding, editing, removing, and viewing server information.
"""

import os
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box

from remotex.ssh_config import (
    get_all_hosts,
    parse_ssh_config,
    add_host_to_config,
    remove_host_from_config,
    ensure_ssh_config_exists,
    host_exists
)
from remotex.ssh_client import create_ssh_client

console = Console()


def register_server_commands(app: typer.Typer):
    """Register all server management commands to the app."""
    app.command(name="list")(list_servers)
    app.command(name="add")(add_server)
    app.command()(info)
    app.command()(edit)
    app.command()(remove)


def list_servers(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed information")
):
    """
    List all configured servers from SSH config.
    
    Example:
        python main.py list
        python main.py list --verbose
    """
    hosts = get_all_hosts()
    
    if not hosts:
        console.print("[yellow]No servers configured yet.[/yellow]")
        console.print("\n[dim]Use 'remotex add' to add a new server.[/dim]")
        return
    
    table = Table(title="Configured Servers", box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Alias", style="cyan", no_wrap=True)
    table.add_column("Hostname", style="green")
    table.add_column("User", style="yellow")
    table.add_column("Port", style="blue", justify="center")
    
    if verbose:
        table.add_column("Identity File", style="dim")
    
    for host in hosts:
        row = [host['alias'], host['hostname'], host['user'], host['port']]
        if verbose:
            identity = host['identityfile']
            if identity != 'N/A':
                identity = identity.replace(str(Path.home()), '~')
            row.append(identity)
        table.add_row(*row)
    
    console.print()
    console.print(table)
    console.print(f"\n[dim]Total servers: {len(hosts)}[/dim]")


def add_server(
    alias: str = typer.Option(None, "--alias", "-a", help="Server alias"),
    hostname: str = typer.Option(None, "--hostname", "-h", help="Server hostname or IP"),
    user: str = typer.Option(None, "--user", "-u", help="SSH username"),
    port: int = typer.Option(22, "--port", "-p", help="SSH port"),
    identity_file: str = typer.Option(None, "--key", "-k", help="Path to SSH private key"),
    jump_host: str = typer.Option(None, "--jump-host", "-j", help="Jump host/bastion alias")
):
    """
    Add a new server to SSH config.
    
    Example:
        python main.py add
        python main.py add -a myserver -h 192.168.1.100 -u ubuntu
        python main.py add --alias prod --hostname prod.example.com --user admin --key ~/.ssh/prod_key
    """
    ensure_ssh_config_exists()
    
    console.print(Panel.fit(
        "[bold cyan]Add New Server[/bold cyan]",
        border_style="cyan"
    ))
    
    # Interactive prompts if not provided
    if not alias:
        alias = Prompt.ask("[cyan]Server alias[/cyan]")
    
    if not hostname:
        hostname = Prompt.ask("[cyan]Hostname or IP address[/cyan]")
    
    if not user:
        user = Prompt.ask("[cyan]SSH username[/cyan]")
    
    if port == 22:
        port_input = Prompt.ask("[cyan]SSH port[/cyan]", default="22")
        try:
            port = int(port_input)
        except ValueError:
            console.print("[red]Invalid port number, using default 22[/red]")
            port = 22
    
    if not identity_file:
        use_key = Confirm.ask("[cyan]Use SSH key file?[/cyan]", default=True)
        if use_key:
            default_key = "~/.ssh/id_rsa"
            identity_file = Prompt.ask("[cyan]Path to private key[/cyan]", default=default_key)
    
    if not jump_host:
        use_jump = Confirm.ask("[cyan]Use jump host/bastion?[/cyan]", default=False)
        if use_jump:
            jump_host = Prompt.ask("[cyan]Jump host alias[/cyan]")
    
    # Show summary
    console.print("\n[bold]Configuration Summary:[/bold]")
    console.print(f"  Alias: [cyan]{alias}[/cyan]")
    console.print(f"  Hostname: [green]{hostname}[/green]")
    console.print(f"  User: [yellow]{user}[/yellow]")
    console.print(f"  Port: [blue]{port}[/blue]")
    if identity_file:
        console.print(f"  Identity File: [magenta]{identity_file}[/magenta]")
    if jump_host:
        console.print(f"  Jump Host: [cyan]{jump_host}[/cyan]")
    
    if Confirm.ask("\n[bold]Add this server?[/bold]", default=True):
        add_host_to_config(alias, hostname, user, port, identity_file, jump_host)
    else:
        console.print("[yellow]Cancelled[/yellow]")


def remove(
    host: str = typer.Argument(..., help="Server alias to remove")
):
    """
    Remove a server from SSH config.
    
    Example:
        python main.py remove myserver
    """
    # Check if host exists
    if not host_exists(host):
        console.print(f"[red]Error: Server '{host}' not found[/red]")
        console.print("\n[dim]Use 'remotex list' to see all configured servers.[/dim]")
        raise typer.Exit(code=1)
    
    # Confirm removal
    if Confirm.ask(f"[bold red]Remove server '{host}'?[/bold red]", default=False):
        remove_host_from_config(host)
    else:
        console.print("[yellow]Cancelled[/yellow]")


def info(
    host: str = typer.Argument(..., help="Server alias")
):
    """
    Show detailed information about a server.
    
    Example:
        python main.py info myserver
    """
    host_config = parse_ssh_config(host)
    
    if not host_config or not host_config.get('hostname'):
        console.print(f"[red]Error: Server '{host}' not found in SSH config[/red]")
        raise typer.Exit(code=1)
    
    # Create info panel
    info_text = f"[bold]Alias:[/bold] [cyan]{host}[/cyan]\n"
    info_text += f"[bold]Hostname:[/bold] [green]{host_config['hostname']}[/green]\n"
    info_text += f"[bold]User:[/bold] [yellow]{host_config.get('user', 'N/A')}[/yellow]\n"
    info_text += f"[bold]Port:[/bold] [blue]{host_config['port']}[/blue]\n"
    
    if host_config.get('identityfile'):
        key_path = host_config['identityfile']
        key_exists = os.path.exists(os.path.expanduser(key_path))
        status = "[green]✓[/green]" if key_exists else "[red]✗[/red]"
        info_text += f"[bold]Identity File:[/bold] {status} [magenta]{key_path}[/magenta]\n"
    
    console.print()
    console.print(Panel(
        info_text,
        title=f"[bold]Server Information[/bold]",
        border_style="cyan",
        box=box.ROUNDED
    ))
    
    # Test connection
    if Confirm.ask("\n[cyan]Test connection?[/cyan]", default=False):
        console.print("\n[cyan]Testing connection...[/cyan]")
        client = create_ssh_client(host_config)
        if client:
            console.print("[green]✓ Connection successful![/green]")
            client.close()
        else:
            console.print("[red]✗ Connection failed[/red]")


def edit(
    host: str = typer.Argument(..., help="Server alias to edit")
):
    """
    Edit an existing server configuration.
    
    Example:
        python main.py edit myserver
    """
    # Check if host exists
    host_config = parse_ssh_config(host)
    
    if not host_config or not host_config.get('hostname'):
        console.print(f"[red]Error: Server '{host}' not found[/red]")
        raise typer.Exit(code=1)
    
    console.print(Panel.fit(
        f"[bold cyan]Edit Server: {host}[/bold cyan]",
        border_style="cyan"
    ))
    
    # Show current config
    console.print("\n[bold]Current configuration:[/bold]")
    console.print(f"  Hostname: [green]{host_config['hostname']}[/green]")
    console.print(f"  User: [yellow]{host_config.get('user', 'N/A')}[/yellow]")
    console.print(f"  Port: [blue]{host_config['port']}[/blue]")
    if host_config.get('identityfile'):
        console.print(f"  Identity File: [magenta]{host_config['identityfile']}[/magenta]")
    
    console.print("\n[dim]Press Enter to keep current value[/dim]\n")
    
    # Get new values
    hostname = Prompt.ask("[cyan]Hostname[/cyan]", default=host_config['hostname'])
    user = Prompt.ask("[cyan]User[/cyan]", default=host_config.get('user', ''))
    port_str = Prompt.ask("[cyan]Port[/cyan]", default=str(host_config['port']))
    
    try:
        port = int(port_str)
    except ValueError:
        console.print("[red]Invalid port, keeping current value[/red]")
        port = host_config['port']
    
    current_key = host_config.get('identityfile', '')
    identity_file = Prompt.ask("[cyan]Identity File[/cyan]", default=current_key)
    
    # Remove old entry and add new one
    if Confirm.ask("\n[bold]Save changes?[/bold]", default=True):
        if remove_host_from_config(host):
            add_host_to_config(host, hostname, user, port, identity_file if identity_file else None)
    else:
        console.print("[yellow]Cancelled[/yellow]")
