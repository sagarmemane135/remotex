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

from remotex.ssh_config import get_all_hosts, parse_ssh_config
from remotex.ssh_client import create_ssh_client
from remotex.connection_pool import get_pooled_connection, close_connection_pool
from remotex.performance import cached
from remotex.history import add_to_history

console = Console()

# Constants for help text to avoid duplication
HELP_PARALLEL = "Number of parallel connections"
HELP_TIMEOUT = "Command timeout in seconds"
HELP_RETRIES = "Number of retry attempts on failure"
HELP_DRY_RUN = "Show what would be executed without running"
HELP_JSON = "Output results as JSON"
HELP_CSV = "Output results as CSV"
HELP_PLAIN = "Plain output without formatting"
HELP_COMPACT = "Compact output format"
HELP_QUIET = "Minimal output for scripting"
HELP_SHOW_OUTPUT = "Show detailed command output"

# Constants for UI text
TITLE_DRY_RUN = "🔍 Dry Run Preview"
TITLE_AFFECTED_SERVERS = "Affected Servers"
PROGRESS_DESCRIPTION = "[progress.description]{task.description}"
ERROR_PREFIX = "\n\n[red bold]Errors:[/red bold]\n"


def register_bulk_commands(app: typer.Typer):
    """Register bulk operation commands."""
    app.command(name="exec-all")(exec_all)
    app.command(name="exec-multi")(exec_multi)
    app.command(name="exec-group")(exec_group)


def _display_dry_run(command: str, targets: List, title: str = TITLE_DRY_RUN) -> None:
    """Display dry run preview."""
    console.print(Panel(
        f"[cyan]Command:[/cyan] {command}\n"
        f"[cyan]Targets:[/cyan] {len(targets)} servers\n"
        "[yellow]Mode:[/yellow] DRY RUN (no execution)",
        title=title,
        border_style="yellow",
        box=box.ROUNDED
    ))


def _display_dry_run_table(hosts: List, command: str) -> None:
    """Display affected servers table for dry run."""
    console.print()
    table = Table(title=TITLE_AFFECTED_SERVERS, box=box.ROUNDED)
    table.add_column("#", justify="right", style="dim")
    table.add_column("Server", style="cyan")
    table.add_column("Hostname", style="white")
    table.add_column("Command", style="yellow")
    
    for idx, host_info in enumerate(hosts, 1):
        hostname = host_info.get('hostname', 'N/A') if isinstance(host_info, dict) else 'N/A'
        alias = host_info['alias'] if isinstance(host_info, dict) else host_info
        table.add_row(str(idx), alias, hostname, command)
    
    console.print(table)
    console.print("\n[yellow]⚠[/yellow]  This is a dry run. Use without --dry-run to execute.")


def _execute_with_progress(host_aliases: List[str], command: str, timeout: int, retries: int, parallel: int) -> List[Dict]:
    """Execute commands with progress bar."""
    results = []
    with Progress(
        SpinnerColumn(),
        TextColumn(PROGRESS_DESCRIPTION),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"[cyan]Executing on {len(host_aliases)} servers...", total=len(host_aliases))
        
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            future_to_host = {
                executor.submit(execute_on_host, host, command, timeout, retries): host 
                for host in host_aliases
            }
            
            for future in as_completed(future_to_host):
                host = future_to_host[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        'host': host,
                        'success': False,
                        'output': '',
                        'error': str(e),
                        'exit_code': -1
                    })
                progress.update(task, advance=1)
    return results


def _execute_without_progress(host_aliases: List[str], command: str, timeout: int, retries: int, parallel: int) -> List[Dict]:
    """Execute commands without progress bar (for machine-readable output)."""
    results = []
    with ThreadPoolExecutor(max_workers=parallel) as executor:
        future_to_host = {
            executor.submit(execute_on_host, host, command, timeout, retries): host 
            for host in host_aliases
        }
        
        for future in as_completed(future_to_host):
            host = future_to_host[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append({
                    'host': host,
                    'success': False,
                    'output': '',
                    'error': str(e),
                    'exit_code': -1
                })
    return results


def _output_json(results: List[Dict], command: str, failed_count: int) -> None:
    """Output results in JSON format."""
    import json
    success_count = len(results) - failed_count
    output_data = {
        "command": command,
        "total": len(results),
        "succeeded": success_count,
        "failed": failed_count,
        "results": [
            {
                "host": r['host'],
                "success": r['success'],
                "exit_code": r['exit_code'],
                "output": r['output'],
                "error": r['error']
            }
            for r in results
        ]
    }
    print(json.dumps(output_data, indent=2))


def _output_csv(results: List[Dict]) -> None:
    """Output results in CSV format."""
    import csv
    import sys
    writer = csv.writer(sys.stdout)
    writer.writerow(["Host", "Success", "ExitCode", "Output", "Error"])
    for r in results:
        writer.writerow([
            r['host'], 
            r['success'], 
            r['exit_code'], 
            r['output'].replace('\n', ' '), 
            r['error'].replace('\n', ' ')
        ])


def _output_quiet(results: List[Dict]) -> None:
    """Output results in quiet mode."""
    for r in results:
        status = "✓" if r['success'] else "✗"
        output = r['output'].strip() or r['error'].strip()
        print(f"{r['host']}: {status} [{r['exit_code']}] {output}")


def _output_plain(results: List[Dict], show_output: bool, success_count: int) -> None:
    """Output results in plain text format."""
    print(f"\nExecuting on {len(results)} servers...\n")
    for r in results:
        status = "SUCCESS" if r['success'] else "FAILED"
        print(f"{r['host']}: {status} (exit code: {r['exit_code']})")
        if show_output and r['output']:
            print(r['output'])
        if r['error']:
            print(f"Error: {r['error']}")
        print()
    print(f"Summary: {success_count}/{len(results)} successful")


def _output_compact(results: List[Dict], success_count: int) -> None:
    """Output results in compact format."""
    for r in results:
        status = "✓" if r['success'] else "✗"
        output_preview = (r['output'] or r['error']).replace('\n', ' ')[:100]
        console.print(f"{status} [cyan]{r['host']}[/cyan] [{r['exit_code']}]: {output_preview}")
    console.print(f"\n{success_count}/{len(results)} successful")


def _display_execution_panel(title: str, command: str, targets_info: str, parallel: int, timeout: int) -> None:
    """Display execution panel with command details."""
    console.print(Panel(
        f"[cyan]Command:[/cyan] {command}\n"
        f"{targets_info}\n"
        f"[cyan]Parallel:[/cyan] {parallel} connections\n"
        f"[cyan]Timeout:[/cyan] {timeout}s",
        title=title,
        border_style="cyan",
        box=box.ROUNDED
    ))
    console.print()


def _log_to_history(command_type: str, command: str, hosts: List[str], 
                    success: bool, metadata: Dict) -> None:
    """Log command execution to history."""
    try:
        add_to_history(
            command=command_type,
            args=[command],
            hosts=hosts,
            success=success,
            metadata=metadata
        )
    except Exception:
        pass  # Don't fail command if history fails

def _handle_output_format(results: List[Dict], command: str, failed_count: int,
                          json_output: bool, csv_output: bool, quiet: bool,
                          plain: bool, compact: bool, show_output: bool, success_count: int) -> bool:
    """Handle different output formats. Returns True if format was handled."""
    if json_output:
        _output_json(results, command, failed_count)
        if failed_count > 0:
            raise typer.Exit(code=1)
        return True
    
    if csv_output:
        _output_csv(results)
        if failed_count > 0:
            raise typer.Exit(code=1)
        return True
    
    if quiet:
        _output_quiet(results)
        if failed_count > 0:
            raise typer.Exit(code=1)
        return True
    
    if plain:
        _output_plain(results, show_output, success_count)
        if failed_count > 0:
            raise typer.Exit(code=1)
        return True
    
    if compact:
        _output_compact(results, success_count)
        if failed_count > 0:
            raise typer.Exit(code=1)
        return True
    
    return False

def _display_summary_table(results: List[Dict]) -> None:
    """Display summary table with execution results."""
    table = Table(title="Execution Summary", box=box.ROUNDED)
    table.add_column("Server", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Exit Code", justify="center")
    table.add_column("Output Preview", style="dim")
    
    for result in results:
        status = "[green]✓ Success[/green]" if result['success'] else "[red]✗ Failed[/red]"
        preview = result['output'][:150].replace('\n', ' ') if result['output'] else result['error'][:150].replace('\n', ' ')
        table.add_row(
            result['host'],
            status,
            str(result['exit_code']),
            preview + "..." if len(preview) == 150 else preview
        )
    
    console.print(table)
    console.print()


def _build_result_content(result: Dict) -> str:
    """Build content string from result output and error."""
    content = ""
    if result['output']:
        content += result['output'].rstrip()
    if result['error']:
        if content:
            content += ERROR_PREFIX
        content += f"[red]{result['error'].rstrip()}[/red]"
    return content


def _display_detailed_panels(results: List[Dict]) -> None:
    """Display detailed output panels for each result."""
    for result in results:
        if result['output'] or result['error']:
            border_style = "green" if result['success'] else "red"
            title = f"{'✓' if result['success'] else '✗'} {result['host']}"
            content = _build_result_content(result)
            
            console.print(Panel(
                content,
                title=title,
                border_style=border_style,
                box=box.ROUNDED
            ))


def _display_final_summary(results: List[Dict], success_count: int) -> None:
    """Display final summary panel."""
    console.print(Panel(
        f"[cyan]Total:[/cyan] {len(results)} | "
        f"[green]Success:[/green] {success_count} | "
        f"[red]Failed:[/red] {len(results) - success_count}",
        title="📊 Summary",
        border_style="cyan" if success_count == len(results) else "yellow",
        box=box.ROUNDED
    ))


def _output_formatted(results: List[Dict], show_output: bool, success_count: int) -> None:
    """Output results with rich formatted tables and panels."""
    console.print()
    _display_summary_table(results)
    
    if show_output:
        _display_detailed_panels(results)
    
    _display_final_summary(results, success_count)


def execute_on_host(host_alias: str, command: str, timeout: int = 30, retries: int = 0, verbose: bool = False) -> Dict:
    """Execute command on a single host and return result."""
    from remotex.retry import retry_with_backoff
    
    @cached(ttl=60)  # Cache SSH config parsing for 60 seconds
    def get_cached_config(alias: str):
        return parse_ssh_config(alias)
    
    def attempt_execution():
        result = {
            'host': host_alias,
            'success': False,
            'output': '',
            'error': '',
            'exit_code': -1
        }
        
        try:
            host_config = get_cached_config(host_alias)
            if not host_config:
                result['error'] = 'Failed to parse SSH config'
                return result
            
            # Use connection pooling for better performance
            client = get_pooled_connection(host_alias, host_config)
            if not client:
                result['error'] = 'Failed to connect'
                return result
            
            # Command is provided by trusted admin user for their managed infrastructure
            _, stdout, stderr = client.exec_command(command, timeout=timeout)  # nosec B601
            result['output'] = stdout.read().decode('utf-8', errors='ignore')
            result['error'] = stderr.read().decode('utf-8', errors='ignore')
            result['exit_code'] = stdout.channel.recv_exit_status()
            result['success'] = result['exit_code'] == 0
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    # Use retry logic if retries > 0
    if retries > 0:
        return retry_with_backoff(attempt_execution, max_retries=retries, verbose=verbose)
    else:
        return attempt_execution()


def exec_all(
    command: str = typer.Argument(..., help="Command to execute on all servers"),
    parallel: int = typer.Option(10, "--parallel", "-p", help=HELP_PARALLEL),
    timeout: int = typer.Option(30, "--timeout", "-t", help=HELP_TIMEOUT),
    retries: int = typer.Option(0, "--retries", "-r", help=HELP_RETRIES),
    dry_run: bool = typer.Option(False, "--dry-run", help=HELP_DRY_RUN),
    json_output: bool = typer.Option(False, "--json", help=HELP_JSON),
    csv_output: bool = typer.Option(False, "--csv", help=HELP_CSV),
    plain: bool = typer.Option(False, "--plain", help=HELP_PLAIN),
    compact: bool = typer.Option(False, "--compact", help=HELP_COMPACT),
    quiet: bool = typer.Option(False, "--quiet", "-q", help=HELP_QUIET),
    continue_on_error: bool = typer.Option(True, "--continue/--stop", help="Continue on errors"),
    show_output: bool = typer.Option(False, "--show-output", help=HELP_SHOW_OUTPUT)
):
    """
    Execute a command on ALL configured servers in parallel.
    
    Example:
        remotex exec-all "uptime"
        remotex exec-all "df -h" --parallel 10
        remotex exec-all "systemctl status nginx" --timeout 10
        remotex exec-all "rm -rf /tmp/*" --dry-run
    """
    hosts = get_all_hosts()
    
    if not hosts:
        console.print("[yellow]No servers configured.[/yellow]")
        return
    
    host_aliases = [h['alias'] for h in hosts]
    
    # Dry-run mode
    if dry_run:
        _display_dry_run(command, host_aliases)
        _display_dry_run_table(hosts, command)
        console.print(f"[dim]Would execute on {len(host_aliases)} servers with {parallel} parallel connections[/dim]")
        return
    
    # Skip decorative output for machine-readable formats
    if not (json_output or csv_output or quiet):
        _display_execution_panel(
            "🚀 Bulk Execution",
            command,
            f"[cyan]Targets:[/cyan] {len(host_aliases)} servers",
            parallel,
            timeout
        )
    
    # Execute commands
    if json_output or csv_output or quiet:
        results = _execute_without_progress(host_aliases, command, timeout, retries, parallel)
    else:
        results = _execute_with_progress(host_aliases, command, timeout, retries, parallel)
    
    # Display results
    success_count = sum(1 for r in results if r['success'])
    failed_count = len(results) - success_count
    
    # Handle different output formats
    if _handle_output_format(results, command, failed_count, json_output, csv_output, 
                              quiet, plain, compact, show_output, success_count):
        return
    
    _output_formatted(results, show_output, success_count)
    
    # Add to history
    _log_to_history(
        "exec-all",
        command,
        [r['host'] for r in results],
        failed_count == 0,
        {
            "total": len(results),
            "succeeded": success_count,
            "failed": failed_count,
            "parallel": parallel,
            "timeout": timeout,
            "retries": retries
        }
    )
    
    # Note: We don't close the connection pool here to allow reuse across commands
    # Connections will timeout naturally after 10 minutes (max_age)
    
    if failed_count > 0 and not continue_on_error:
        raise typer.Exit(code=1)


def exec_multi(
    hosts: str = typer.Argument(..., help="Comma-separated list of host aliases"),
    command: str = typer.Argument(..., help="Command to execute"),
    parallel: int = typer.Option(5, "--parallel", "-p", help=HELP_PARALLEL),
    timeout: int = typer.Option(30, "--timeout", "-t", help=HELP_TIMEOUT),
    retries: int = typer.Option(0, "--retries", "-r", help=HELP_RETRIES),
    dry_run: bool = typer.Option(False, "--dry-run", help=HELP_DRY_RUN),
    json_output: bool = typer.Option(False, "--json", help=HELP_JSON),
    csv_output: bool = typer.Option(False, "--csv", help=HELP_CSV),
    plain: bool = typer.Option(False, "--plain", help=HELP_PLAIN),
    compact: bool = typer.Option(False, "--compact", help=HELP_COMPACT),
    quiet: bool = typer.Option(False, "--quiet", "-q", help=HELP_QUIET),
    show_output: bool = typer.Option(False, "--show-output", help=HELP_SHOW_OUTPUT)
):
    """
    Execute a command on specific servers (comma-separated list).
    
    Example:
        remotex exec-multi "web01,web02,web03" "systemctl restart nginx"
        remotex exec-multi "db01,db02" "pg_isready" --parallel 2
        remotex exec-multi "web01,db01" "uptime" --dry-run
    """
    host_list = [h.strip() for h in hosts.split(',')]
    
    # Dry-run mode
    if dry_run:
        _display_dry_run(command, host_list)
        _display_dry_run_table(host_list, command)
        return
    
    # Skip decorative output for machine-readable formats
    if not (json_output or csv_output or quiet):
        _display_execution_panel(
            "🎯 Multi-Server Execution",
            command,
            f"[cyan]Targets:[/cyan] {', '.join(host_list)}",
            parallel,
            timeout
        )
    
    # Execute commands
    if json_output or csv_output or quiet:
        results = _execute_without_progress(host_list, command, timeout, retries, parallel)
    else:
        results = _execute_with_progress(host_list, command, timeout, retries, parallel)
    
    success_count = sum(1 for r in results if r['success'])
    failed_count = len(results) - success_count
    
    # Handle different output formats
    if _handle_output_format(results, command, failed_count, json_output, csv_output, 
                              quiet, plain, compact, show_output, success_count):
        return
    
    _output_formatted(results, show_output, success_count)
    
    # Add to history
    _log_to_history(
        "exec-multi",
        command,
        host_list,
        success_count == len(results),
        {
            "hosts_list": hosts,
            "total": len(results),
            "succeeded": success_count,
            "failed": failed_count,
            "parallel": parallel,
            "timeout": timeout
        }
    )
    
    if success_count < len(results):
        raise typer.Exit(code=1)


def exec_group(
    group_name: str = typer.Argument(..., help="Name of the server group"),
    command: str = typer.Argument(..., help="Command to execute"),
    parallel: int = typer.Option(5, "--parallel", "-p", help=HELP_PARALLEL),
    timeout: int = typer.Option(30, "--timeout", "-t", help=HELP_TIMEOUT),
    retries: int = typer.Option(0, "--retries", "-r", help=HELP_RETRIES),
    dry_run: bool = typer.Option(False, "--dry-run", help=HELP_DRY_RUN),
    json_output: bool = typer.Option(False, "--json", help=HELP_JSON),
    csv_output: bool = typer.Option(False, "--csv", help=HELP_CSV),
    plain: bool = typer.Option(False, "--plain", help=HELP_PLAIN),
    compact: bool = typer.Option(False, "--compact", help=HELP_COMPACT),
    quiet: bool = typer.Option(False, "--quiet", "-q", help=HELP_QUIET),
    show_output: bool = typer.Option(False, "--show-output", help=HELP_SHOW_OUTPUT)
):
    """
    Execute a command on all servers in a group.
    
    Example:
        remotex exec-group web "systemctl restart nginx"
        remotex exec-group db "pg_dump mydb" --parallel 3
        remotex exec-group prod "uptime" --dry-run
    """
    from remotex import config
    
    servers = config.get_group_servers(group_name)
    
    if not servers:
        console.print(f"[red]✗[/red] Group '[cyan]{group_name}[/cyan]' not found or empty")
        console.print("[yellow]Use 'remotex group list' to see available groups[/yellow]")
        raise typer.Exit(1)
    
    # Dry-run mode
    if dry_run:
        console.print(Panel(
            f"[cyan]Command:[/cyan] {command}\n"
            f"[cyan]Group:[/cyan] {group_name}\n"
            f"[cyan]Targets:[/cyan] {len(servers)} servers\n"
            "[yellow]Mode:[/yellow] DRY RUN (no execution)",
            title=TITLE_DRY_RUN,
            border_style="yellow",
            box=box.ROUNDED
        ))
        console.print()
        
        table = Table(title=TITLE_AFFECTED_SERVERS, box=box.ROUNDED)
        table.add_column("#", justify="right", style="dim")
        table.add_column("Server", style="cyan")
        table.add_column("Command", style="yellow")
        
        for idx, server in enumerate(servers, 1):
            table.add_row(str(idx), server, command)
        
        console.print(table)
        console.print("\n[yellow]⚠[/yellow]  This is a dry run. Use without --dry-run to execute.")
        return
    
    # Skip decorative output for machine-readable formats
    if not (json_output or csv_output or quiet):
        _display_execution_panel(
            "🚀 Group Execution",
            command,
            f"[cyan]Group:[/cyan] {group_name}\n[cyan]Targets:[/cyan] {len(servers)} servers",
            parallel,
            timeout
        )
    
    # Execute commands
    if json_output or csv_output or quiet:
        results = _execute_without_progress(servers, command, timeout, retries, parallel)
    else:
        results = _execute_with_progress(servers, command, timeout, retries, parallel)
    
    # Display results
    success_count = sum(1 for r in results if r['success'])
    failed_count = len(results) - success_count
    
    # Handle different output formats
    if _handle_output_format(results, command, failed_count, json_output, csv_output, 
                              quiet, plain, compact, show_output, success_count):
        # Audit log for JSON output
        if json_output:
            from remotex.audit import log_command_execution
            log_command_execution(
                command_type="exec-group",
                hosts=servers,
                command=command,
                results={r['host']: r for r in results},
                metadata={"group": group_name, "parallel": parallel, "timeout": timeout, "retries": retries}
            )
        return
    
    _output_formatted(results, show_output, success_count)
    
    # Audit log
    from remotex.audit import log_command_execution
    log_command_execution(
        command_type="exec-group",
        hosts=servers,
        command=command,
        results={r['host']: r for r in results},
        metadata={"group": group_name, "parallel": parallel, "timeout": timeout}
    )
    
    # Add to history
    _log_to_history(
        "exec-group",
        command,
        servers,
        success_count == len(results),
        {
            "group_name": group_name,
            "total": len(results),
            "succeeded": success_count,
            "failed": failed_count,
            "parallel": parallel,
            "timeout": timeout
        }
    )
    
    if success_count < len(results):
        raise typer.Exit(code=1)

