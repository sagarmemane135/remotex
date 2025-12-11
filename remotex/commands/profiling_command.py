"""
Performance Profiling Commands
"""

import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table

from remotex.profiling import PROFILE_DIR, analyze_profile, get_profile_summary
from remotex.utils import console

app = typer.Typer(name="profile", help="Performance profiling tools")


@app.command("list")
def profile_list():
    """List all profile files."""
    if not PROFILE_DIR.exists():
        console.print("[yellow]No profile files found.[/yellow]")
        return
    
    profiles = sorted(PROFILE_DIR.glob("*.prof"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if not profiles:
        console.print("[yellow]No profile files found.[/yellow]")
        return
    
    table = Table(title="Profile Files", show_header=True, header_style="bold magenta")
    table.add_column("File", style="cyan")
    table.add_column("Size", style="green")
    table.add_column("Modified", style="yellow")
    
    for profile in profiles[:20]:  # Show last 20
        size = profile.stat().st_size
        mtime = profile.stat().st_mtime
        from datetime import datetime
        mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
        
        table.add_row(
            profile.name,
            f"{size / 1024:.1f} KB",
            mtime_str
        )
    
    console.print(table)


@app.command("show")
def profile_show(
    profile_file: str = typer.Argument(..., help="Profile file name"),
    limit: int = typer.Option(20, "--limit", "-n", help="Number of lines to show"),
    sort_by: str = typer.Option("cumulative", "--sort", help="Sort by: cumulative, time, calls")
):
    """Show profile analysis."""
    profile_path = PROFILE_DIR / profile_file
    
    if not profile_path.exists():
        console.print(f"[red]Profile file not found: {profile_file}[/red]")
        raise typer.Exit(1)
    
    # Get summary
    summary = get_profile_summary(profile_path)
    console.print(f"\n[bold]Profile Summary:[/bold]")
    console.print(f"  Total calls: {summary['total_calls']}")
    console.print(f"  Total time: {summary['total_time']:.4f}s")
    console.print(f"  Cumulative time: {summary['cumulative_time']:.4f}s")
    
    # Show analysis
    analysis = analyze_profile(profile_path, sort_by=sort_by, limit=limit)
    console.print(f"\n[bold]Top {limit} functions (sorted by {sort_by}):[/bold]")
    console.print(f"[dim]{analysis}[/dim]")


@app.command("clean")
def profile_clean(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation")
):
    """Clean all profile files."""
    if not PROFILE_DIR.exists():
        console.print("[yellow]No profile files to clean.[/yellow]")
        return
    
    profiles = list(PROFILE_DIR.glob("*.prof"))
    
    if not profiles:
        console.print("[yellow]No profile files to clean.[/yellow]")
        return
    
    if not confirm:
        console.print(f"[yellow]This will delete {len(profiles)} profile file(s).[/yellow]")
        response = typer.prompt("Are you sure? (yes/no)", default="no")
        if response.lower() != "yes":
            console.print("[yellow]Cancelled.[/yellow]")
            return
    
    for profile in profiles:
        profile.unlink()
    
    console.print(f"[green]✓ Deleted {len(profiles)} profile file(s).[/green]")

