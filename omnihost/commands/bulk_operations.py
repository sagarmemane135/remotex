"""
Bulk Operations Module
Execute commands on multiple servers in parallel.
"""

import asyncio
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import typer
import paramiko
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich import box
from rich.live import Live

from omnihost.ssh_config import get_all_hosts, parse_ssh_config
from omnihost.ssh_client import create_ssh_client

console = Console()


def register_bulk_commands(app: typer.Typer):
    """Register bulk operation commands."""
    app.command(name="exec-all")(exec_all)
    app.command(name="exec-multi")(exec_multi)


def execute_on_host(host_alias: str, command: str, timeout: int = 30) -> Dict:
    """Execute command on a single host and return result."""
    result = {
        'host': host_alias,
        'success': False,
        'output': '',
        'error': '',
        'exit_code': -1
    }
    
    try:
        host_config = parse_ssh_config(host_alias)
        if not host_config:
            result['error'] = 'Failed to parse SSH config'
            return result
        
        client = create_ssh_client(host_config)
        if not client:
            result['error'] = 'Failed to connect'
            return result
        
        try:
            stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
            result['output'] = stdout.read().decode('utf-8', errors='ignore')
            result['error'] = stderr.read().decode('utf-8', errors='ignore')
            result['exit_code'] = stdout.channel.recv_exit_status()
            result['success'] = result['exit_code'] == 0
        finally:
            client.close()
            
    except Exception as e:
        result['error'] = str(e)
    
    return result


def exec_all(
    command: str = typer.Argument(..., help="Command to execute on all servers"),
    parallel: int = typer.Option(5, "--parallel", "-p", help="Number of parallel connections"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Command timeout in seconds"),
    continue_on_error: bool = typer.Option(True, "--continue/--stop", help="Continue on errors"),
    show_output: bool = typer.Option(True, "--show-output/--no-output", help="Show command output")
):
    """
    Execute a command on ALL configured servers in parallel.
    
    Example:
        omnihost exec-all "uptime"
        omnihost exec-all "df -h" --parallel 10
        omnihost exec-all "systemctl status nginx" --timeout 10
    """
    hosts = get_all_hosts()
    
    if not hosts:
        console.print("[yellow]No servers configured.[/yellow]")
        return
    
    host_aliases = [h['alias'] for h in hosts]
    
    console.print(Panel(
        f"[cyan]Command:[/cyan] {command}\n"
        f"[cyan]Targets:[/cyan] {len(host_aliases)} servers\n"
        f"[cyan]Parallel:[/cyan] {parallel} connections\n"
        f"[cyan]Timeout:[/cyan] {timeout}s",
        title="🚀 Bulk Execution",
        border_style="cyan",
        box=box.ROUNDED
    ))
    console.print()
    
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"[cyan]Executing on {len(host_aliases)} servers...", total=len(host_aliases))
        
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            future_to_host = {
                executor.submit(execute_on_host, host, command, timeout): host 
                for host in host_aliases
            }
            
            for future in as_completed(future_to_host):
                host = future_to_host[future]
                try:
                    result = future.result()
                    results.append(result)
                    progress.update(task, advance=1)
                except Exception as e:
                    results.append({
                        'host': host,
                        'success': False,
                        'output': '',
                        'error': str(e),
                        'exit_code': -1
                    })
                    progress.update(task, advance=1)
    
    # Display results
    console.print()
    
    success_count = sum(1 for r in results if r['success'])
    failed_count = len(results) - success_count
    
    # Summary table
    table = Table(title="Execution Summary", box=box.ROUNDED)
    table.add_column("Server", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Exit Code", justify="center")
    table.add_column("Output Preview", style="dim")
    
    for result in results:
        status = "[green]✓ Success[/green]" if result['success'] else "[red]✗ Failed[/red]"
        preview = result['output'][:50].replace('\n', ' ') if result['output'] else result['error'][:50].replace('\n', ' ')
        table.add_row(
            result['host'],
            status,
            str(result['exit_code']),
            preview + "..." if len(preview) == 50 else preview
        )
    
    console.print(table)
    console.print()
    
    # Show detailed output if requested
    if show_output:
        for result in results:
            if result['output'] or result['error']:
                border_style = "green" if result['success'] else "red"
                title = f"{'✓' if result['success'] else '✗'} {result['host']}"
                
                content = ""
                if result['output']:
                    content += result['output'].rstrip()
                if result['error']:
                    if content:
                        content += "\n\n[red bold]Errors:[/red bold]\n"
                    content += f"[red]{result['error'].rstrip()}[/red]"
                
                console.print(Panel(
                    content,
                    title=title,
                    border_style=border_style,
                    box=box.ROUNDED
                ))
    
    # Final summary
    summary_text = f"[bold]Total:[/bold] {len(results)} | "
    summary_text += f"[green]Success:[/green] {success_count} | "
    summary_text += f"[red]Failed:[/red] {failed_count}"
    
    console.print(Panel(summary_text, box=box.ROUNDED))
    
    if failed_count > 0 and not continue_on_error:
        raise typer.Exit(code=1)


def exec_multi(
    hosts: str = typer.Argument(..., help="Comma-separated list of host aliases"),
    command: str = typer.Argument(..., help="Command to execute"),
    parallel: int = typer.Option(5, "--parallel", "-p", help="Number of parallel connections"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Command timeout in seconds")
):
    """
    Execute a command on specific servers (comma-separated list).
    
    Example:
        omnihost exec-multi "web01,web02,web03" "systemctl restart nginx"
        omnihost exec-multi "db01,db02" "pg_isready" --parallel 2
    """
    host_list = [h.strip() for h in hosts.split(',')]
    
    console.print(Panel(
        f"[cyan]Command:[/cyan] {command}\n"
        f"[cyan]Targets:[/cyan] {', '.join(host_list)}\n"
        f"[cyan]Parallel:[/cyan] {parallel} connections",
        title="🎯 Multi-Server Execution",
        border_style="cyan",
        box=box.ROUNDED
    ))
    console.print()
    
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"[cyan]Executing on {len(host_list)} servers...", total=len(host_list))
        
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            future_to_host = {
                executor.submit(execute_on_host, host, command, timeout): host 
                for host in host_list
            }
            
            for future in as_completed(future_to_host):
                host = future_to_host[future]
                try:
                    result = future.result()
                    results.append(result)
                    progress.update(task, advance=1)
                except Exception as e:
                    results.append({
                        'host': host,
                        'success': False,
                        'output': '',
                        'error': str(e),
                        'exit_code': -1
                    })
                    progress.update(task, advance=1)
    
    console.print()
    
    # Display results
    for result in results:
        border_style = "green" if result['success'] else "red"
        title = f"{'✓' if result['success'] else '✗'} {result['host']}"
        
        content = ""
        if result['output']:
            content += result['output'].rstrip()
        if result['error']:
            if content:
                content += "\n\n[red bold]Errors:[/red bold]\n"
            content += f"[red]{result['error'].rstrip()}[/red]"
        
        if not content:
            content = "[dim]No output[/dim]"
        
        console.print(Panel(
            content,
            title=title,
            border_style=border_style,
            box=box.ROUNDED
        ))
    
    success_count = sum(1 for r in results if r['success'])
    console.print(f"\n[bold]Summary:[/bold] {success_count}/{len(results)} successful")
    
    if success_count < len(results):
        raise typer.Exit(code=1)
