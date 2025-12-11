"""
Command History Management
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from datetime import datetime

from remotex.history import (
    get_history, get_history_entry, clear_history, export_history
)
from remotex.utils import console

app = typer.Typer(name="history", help="Manage command history")


@app.command("list")
def history_list(
    limit: int = typer.Option(20, "--limit", "-n", help="Number of entries to show"),
    host: str = typer.Option(None, "--host", "-h", help="Filter by host"),
    command: str = typer.Option(None, "--command", "-c", help="Filter by command"),
    since: str = typer.Option(None, "--since", help="Show entries since timestamp (ISO format)")
):
    """List command history."""
    entries = get_history(limit=limit, host=host, command=command, since=since)
    
    if not entries:
        console.print("[yellow]No history entries found.[/yellow]")
        return
    
    table = Table(title="Command History", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", width=6)
    table.add_column("Time", style="green", width=20)
    table.add_column("Command", style="yellow", width=30)
    table.add_column("Hosts", style="blue", width=20)
    table.add_column("Status", width=10)
    
    for entry in reversed(entries):  # Show most recent first
        timestamp = entry.get("timestamp", "")
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            time_str = timestamp[:19] if len(timestamp) > 19 else timestamp
        
        cmd = entry.get("command", "")
        hosts = ", ".join(entry.get("hosts", []))[:18]
        success = entry.get("success", False)
        status = "✅" if success else "❌"
        
        table.add_row(
            str(entry.get("id", "")),
            time_str,
            cmd[:28],
            hosts,
            status
        )
    
    console.print(table)
    console.print(f"\n[dim]Showing {len(entries)} of {len(get_history(limit=10000))} total entries[/dim]")


@app.command("show")
def history_show(
    entry_id: int = typer.Argument(..., help="History entry ID")
):
    """Show details of a specific history entry."""
    entry = get_history_entry(entry_id)
    
    if not entry:
        console.print(f"[red]History entry #{entry_id} not found.[/red]")
        raise typer.Exit(1)
    
    timestamp = entry.get("timestamp", "")
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        time_str = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except:
        time_str = timestamp
    
    panel_content = f"""
[bold]ID:[/bold] {entry.get('id')}
[bold]Time:[/bold] {time_str}
[bold]Command:[/bold] {entry.get('command', '')}
[bold]Full Command:[/bold] {entry.get('full_command', '')}
[bold]Hosts:[/bold] {', '.join(entry.get('hosts', []))}
[bold]Status:[/bold] {'✅ Success' if entry.get('success') else '❌ Failed'}
"""
    
    if entry.get("metadata"):
        panel_content += f"\n[bold]Metadata:[/bold]\n"
        for key, value in entry.get("metadata", {}).items():
            panel_content += f"  {key}: {value}\n"
    
    console.print(Panel(panel_content.strip(), title="History Entry", border_style="blue"))


@app.command("replay")
def history_replay(
    entry_id: int = typer.Argument(..., help="History entry ID to replay"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview command without executing")
):
    """Replay a command from history."""
    entry = get_history_entry(entry_id)
    
    if not entry:
        console.print(f"[red]History entry #{entry_id} not found.[/red]")
        raise typer.Exit(1)
    
    full_command = entry.get("full_command", "")
    
    if dry_run:
        console.print(f"[yellow]Would replay:[/yellow] [cyan]{full_command}[/cyan]")
        return
    
    console.print(f"[green]Replaying command #{entry_id}:[/green] [cyan]{full_command}[/cyan]")
    console.print("[yellow]Note: This will execute the command. Use --dry-run to preview.[/yellow]")
    
    # Import here to avoid circular imports
    import subprocess
    import sys
    
    # Parse the command
    parts = full_command.split()
    if parts[0] != "remotex":
        parts.insert(0, "remotex")
    
    # Execute
    try:
        result = subprocess.run(parts, check=False)
        sys.exit(result.returncode)
    except Exception as e:
        console.print(f"[red]Error replaying command: {e}[/red]")
        raise typer.Exit(1)


@app.command("clear")
def history_clear(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation")
):
    """Clear all command history."""
    if not confirm:
        console.print("[yellow]This will delete all command history.[/yellow]")
        response = typer.prompt("Are you sure? (yes/no)", default="no")
        if response.lower() != "yes":
            console.print("[yellow]Cancelled.[/yellow]")
            return
    
    clear_history()
    console.print("[green]✓ Command history cleared.[/green]")


@app.command("export")
def history_export(
    output: str = typer.Option("history.json", "--output", "-o", help="Output file path")
):
    """Export command history to a file."""
    export_history(output)
    console.print(f"[green]✓ History exported to {output}[/green]")

