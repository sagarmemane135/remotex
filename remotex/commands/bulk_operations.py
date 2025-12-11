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
from remotex.history import add_to_history

console = Console()


def register_bulk_commands(app: typer.Typer):
    """Register bulk operation commands."""
    app.command(name="exec-all")(exec_all)
    app.command(name="exec-multi")(exec_multi)
    app.command(name="exec-group")(exec_group)


def execute_on_host(host_alias: str, command: str, timeout: int = 30, retries: int = 0, verbose: bool = False) -> Dict:
    """Execute command on a single host and return result."""
    from remotex.retry import retry_with_backoff
    
    def attempt_execution():
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
                # Command is provided by trusted admin user for their managed infrastructure
                stdin, stdout, stderr = client.exec_command(command, timeout=timeout)  # nosec B601
                result['output'] = stdout.read().decode('utf-8', errors='ignore')
                result['error'] = stderr.read().decode('utf-8', errors='ignore')
                result['exit_code'] = stdout.channel.recv_exit_status()
                result['success'] = result['exit_code'] == 0
            finally:
                client.close()
                
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
    parallel: int = typer.Option(5, "--parallel", "-p", help="Number of parallel connections"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Command timeout in seconds"),
    retries: int = typer.Option(0, "--retries", "-r", help="Number of retry attempts on failure"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be executed without running"),
    json_output: bool = typer.Option(False, "--json", help="Output results as JSON"),
    csv_output: bool = typer.Option(False, "--csv", help="Output results as CSV"),
    plain: bool = typer.Option(False, "--plain", help="Plain output without formatting"),
    compact: bool = typer.Option(False, "--compact", help="Compact output format"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Minimal output for scripting"),
    continue_on_error: bool = typer.Option(True, "--continue/--stop", help="Continue on errors"),
    show_output: bool = typer.Option(False, "--show-output", help="Show detailed command output")
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
        console.print(Panel(
            f"[cyan]Command:[/cyan] {command}\n"
            f"[cyan]Targets:[/cyan] {len(host_aliases)} servers\n"
            f"[yellow]Mode:[/yellow] DRY RUN (no execution)",
            title="🔍 Dry Run Preview",
            border_style="yellow",
            box=box.ROUNDED
        ))
        console.print()
        
        table = Table(title="Affected Servers", box=box.ROUNDED)
        table.add_column("#", justify="right", style="dim")
        table.add_column("Server", style="cyan")
        table.add_column("Hostname", style="white")
        table.add_column("Command", style="yellow")
        
        for idx, host_info in enumerate(hosts, 1):
            table.add_row(str(idx), host_info['alias'], host_info.get('hostname', 'N/A'), command)
        
        console.print(table)
        console.print(f"\n[yellow]⚠[/yellow]  This is a dry run. Use without --dry-run to execute.")
        console.print(f"[dim]Would execute on {len(host_aliases)} servers with {parallel} parallel connections[/dim]")
        return
    
    # Skip decorative output for machine-readable formats
    if not (json_output or csv_output or quiet):
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
    
    # Skip progress bars for machine-readable formats
    if json_output or csv_output or quiet:
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
    else:
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
                    executor.submit(execute_on_host, host, command, timeout, retries): host 
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
    success_count = sum(1 for r in results if r['success'])
    failed_count = len(results) - success_count
    
    # JSON output mode (pure, no decorations)
    if json_output:
        import json
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
        # Pure JSON output to stdout, bypassing rich console
        print(json.dumps(output_data, indent=2))
        if failed_count > 0:
            raise typer.Exit(code=1)
        return
    
    # CSV output mode (pure, no decorations)
    if csv_output:
        import csv
        import sys
        writer = csv.writer(sys.stdout)
        writer.writerow(["Host", "Success", "ExitCode", "Output", "Error"])
        for r in results:
            writer.writerow([r['host'], r['success'], r['exit_code'], r['output'].replace('\n', ' '), r['error'].replace('\n', ' ')])
        if failed_count > 0:
            raise typer.Exit(code=1)
        return
    
    # Quiet mode (minimal output for scripting)
    if quiet:
        for r in results:
            status = "✓" if r['success'] else "✗"
            output = r['output'].strip() or r['error'].strip()
            print(f"{r['host']}: {status} [{r['exit_code']}] {output}")
        if failed_count > 0:
            raise typer.Exit(code=1)
        return
    
    # Plain mode (simple text without colors)
    if plain:
        print(f"\nExecuting on {len(host_aliases)} servers...\n")
        for r in results:
            status = "SUCCESS" if r['success'] else "FAILED"
            print(f"{r['host']}: {status} (exit code: {r['exit_code']})")
            if show_output and r['output']:
                print(r['output'])
            if r['error']:
                print(f"Error: {r['error']}")
            print()
        print(f"Summary: {success_count}/{len(results)} successful")
        if failed_count > 0:
            raise typer.Exit(code=1)
        return
    
    # Compact mode (condensed output)
    if compact:
        for r in results:
            status = "✓" if r['success'] else "✗"
            output_preview = (r['output'] or r['error']).replace('\n', ' ')[:100]
            console.print(f"{status} [cyan]{r['host']}[/cyan] [{r['exit_code']}]: {output_preview}")
        console.print(f"\n{success_count}/{len(results)} successful")
        if failed_count > 0:
            raise typer.Exit(code=1)
        return
    
    console.print()
    
    # Summary table
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
    
    # Add to history
    try:
        add_to_history(
            command="exec-all",
            args=[command],
            hosts=[r['host'] for r in results],
            success=(failed_count == 0),
            metadata={
                "total": len(results),
                "succeeded": success_count,
                "failed": failed_count,
                "parallel": parallel,
                "timeout": timeout,
                "retries": retries
            }
        )
    except:
        pass  # Don't fail command if history fails
    
    if failed_count > 0 and not continue_on_error:
        raise typer.Exit(code=1)


def exec_multi(
    hosts: str = typer.Argument(..., help="Comma-separated list of host aliases"),
    command: str = typer.Argument(..., help="Command to execute"),
    parallel: int = typer.Option(5, "--parallel", "-p", help="Number of parallel connections"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Command timeout in seconds"),
    retries: int = typer.Option(0, "--retries", "-r", help="Number of retry attempts on failure"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be executed without running"),
    json_output: bool = typer.Option(False, "--json", help="Output results as JSON"),
    csv_output: bool = typer.Option(False, "--csv", help="Output results as CSV"),
    plain: bool = typer.Option(False, "--plain", help="Plain output without formatting"),
    compact: bool = typer.Option(False, "--compact", help="Compact output format"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Minimal output for scripting"),
    show_output: bool = typer.Option(False, "--show-output", help="Show detailed command output")
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
        console.print(Panel(
            f"[cyan]Command:[/cyan] {command}\n"
            f"[cyan]Targets:[/cyan] {', '.join(host_list)}\n"
            f"[yellow]Mode:[/yellow] DRY RUN (no execution)",
            title="🔍 Dry Run Preview",
            border_style="yellow",
            box=box.ROUNDED
        ))
        console.print()
        
        table = Table(title="Affected Servers", box=box.ROUNDED)
        table.add_column("#", justify="right", style="dim")
        table.add_column("Server", style="cyan")
        table.add_column("Command", style="yellow")
        
        for idx, host in enumerate(host_list, 1):
            table.add_row(str(idx), host, command)
        
        console.print(table)
        console.print(f"\n[yellow]⚠[/yellow]  This is a dry run. Use without --dry-run to execute.")
        return
    
    # Skip decorative output for machine-readable formats
    if not (json_output or csv_output or quiet):
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
    
    # Skip progress bars for machine-readable formats
    if json_output or csv_output or quiet:
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            future_to_host = {
                executor.submit(execute_on_host, host, command, timeout, retries): host 
                for host in host_list
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
    else:
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
                    executor.submit(execute_on_host, host, command, timeout, retries): host 
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
    
    success_count = sum(1 for r in results if r['success'])
    failed_count = len(results) - success_count
    
    # JSON output mode (pure, no decorations)
    if json_output:
        import json
        output_data = {
            "command": command,
            "hosts": host_list,
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
        if failed_count > 0:
            raise typer.Exit(code=1)
        return
    
    # CSV output mode
    if csv_output:
        import csv
        import sys
        writer = csv.writer(sys.stdout)
        writer.writerow(["Host", "Success", "ExitCode", "Output", "Error"])
        for r in results:
            writer.writerow([r['host'], r['success'], r['exit_code'], r['output'].replace('\n', ' '), r['error'].replace('\n', ' ')])
        if failed_count > 0:
            raise typer.Exit(code=1)
        return
    
    # Quiet mode
    if quiet:
        for r in results:
            status = "✓" if r['success'] else "✗"
            output = r['output'].strip() or r['error'].strip()
            print(f"{r['host']}: {status} [{r['exit_code']}] {output}")
        if failed_count > 0:
            raise typer.Exit(code=1)
        return
    
    # Plain mode
    if plain:
        print(f"\nExecuting on {len(host_list)} servers...\n")
        for r in results:
            status = "SUCCESS" if r['success'] else "FAILED"
            print(f"{r['host']}: {status} (exit code: {r['exit_code']})")
            if show_output and r['output']:
                print(r['output'])
            if r['error']:
                print(f"Error: {r['error']}")
            print()
        print(f"Summary: {success_count}/{len(results)} successful")
        if failed_count > 0:
            raise typer.Exit(code=1)
        return
    
    # Compact mode
    if compact:
        for r in results:
            status = "✓" if r['success'] else "✗"
            output_preview = (r['output'] or r['error']).replace('\n', ' ')[:100]
            console.print(f"{status} [cyan]{r['host']}[/cyan] [{r['exit_code']}]: {output_preview}")
        console.print(f"\n{success_count}/{len(results)} successful")
        if failed_count > 0:
            raise typer.Exit(code=1)
        return
    
    console.print()
    
    # Show detailed output if requested
    if show_output:
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
    
    # Add to history
    try:
        add_to_history(
            command="exec-multi",
            args=[command],
            hosts=host_list,
            success=(success_count == len(results)),
            metadata={
                "hosts_list": hosts,
                "total": len(results),
                "succeeded": success_count,
                "failed": len(results) - success_count,
                "parallel": parallel,
                "timeout": timeout
            }
        )
    except:
        pass  # Don't fail command if history fails
    
    if success_count < len(results):
        raise typer.Exit(code=1)


def exec_group(
    group_name: str = typer.Argument(..., help="Name of the server group"),
    command: str = typer.Argument(..., help="Command to execute"),
    parallel: int = typer.Option(5, "--parallel", "-p", help="Number of parallel connections"),
    timeout: int = typer.Option(30, "--timeout", "-t", help="Command timeout in seconds"),
    retries: int = typer.Option(0, "--retries", "-r", help="Number of retry attempts on failure"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be executed without running"),
    json_output: bool = typer.Option(False, "--json", help="Output results as JSON"),
    csv_output: bool = typer.Option(False, "--csv", help="Output results as CSV"),
    plain: bool = typer.Option(False, "--plain", help="Plain output without formatting"),
    compact: bool = typer.Option(False, "--compact", help="Compact output format"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Minimal output for scripting"),
    show_output: bool = typer.Option(False, "--show-output", help="Show detailed command output")
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
            f"[yellow]Mode:[/yellow] DRY RUN (no execution)",
            title="🔍 Dry Run Preview",
            border_style="yellow",
            box=box.ROUNDED
        ))
        console.print()
        
        table = Table(title="Affected Servers", box=box.ROUNDED)
        table.add_column("#", justify="right", style="dim")
        table.add_column("Server", style="cyan")
        table.add_column("Command", style="yellow")
        
        for idx, server in enumerate(servers, 1):
            table.add_row(str(idx), server, command)
        
        console.print(table)
        console.print(f"\n[yellow]⚠[/yellow]  This is a dry run. Use without --dry-run to execute.")
        return
    
    # Skip decorative output for machine-readable formats
    if not (json_output or csv_output or quiet):
        console.print(Panel(
            f"[cyan]Command:[/cyan] {command}\n"
            f"[cyan]Group:[/cyan] {group_name}\n"
            f"[cyan]Targets:[/cyan] {len(servers)} servers\n"
            f"[cyan]Parallel:[/cyan] {parallel} connections\n"
            f"[cyan]Timeout:[/cyan] {timeout}s",
            title="🚀 Group Execution",
            border_style="cyan",
            box=box.ROUNDED
        ))
        console.print()
    
    results = []
    
    # Skip progress bars for machine-readable formats
    if json_output or csv_output or quiet:
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            future_to_host = {
                executor.submit(execute_on_host, host, command, timeout, retries): host 
                for host in servers
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
    else:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task(f"[cyan]Executing on {len(servers)} servers...", total=len(servers))
            
            with ThreadPoolExecutor(max_workers=parallel) as executor:
                future_to_host = {
                    executor.submit(execute_on_host, host, command, timeout, retries): host 
                    for host in servers
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
    success_count = sum(1 for r in results if r['success'])
    failed_count = len(results) - success_count
    
    # JSON output mode (pure, no decorations)
    if json_output:
        import json
        output_data = {
            "command": command,
            "group": group_name,
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
        
        # Audit log
        from remotex.audit import log_command_execution
        log_command_execution(
            command_type="exec-group",
            hosts=servers,
            command=command,
            results={r['host']: r for r in results},
            metadata={"group": group_name, "parallel": parallel, "timeout": timeout, "retries": retries}
        )
        
        if failed_count > 0:
            raise typer.Exit(code=1)
        return
    
    # CSV output mode
    if csv_output:
        import csv
        import sys
        writer = csv.writer(sys.stdout)
        writer.writerow(["Host", "Success", "ExitCode", "Output", "Error"])
        for r in results:
            writer.writerow([r['host'], r['success'], r['exit_code'], r['output'].replace('\n', ' '), r['error'].replace('\n', ' ')])
        if failed_count > 0:
            raise typer.Exit(code=1)
        return
    
    # Quiet mode
    if quiet:
        for r in results:
            status = "✓" if r['success'] else "✗"
            output = r['output'].strip() or r['error'].strip()
            print(f"{r['host']}: {status} [{r['exit_code']}] {output}")
        if failed_count > 0:
            raise typer.Exit(code=1)
        return
    
    # Plain mode
    if plain:
        print(f"\nExecuting on {len(servers)} servers in group '{group_name}'...\n")
        for r in results:
            status = "SUCCESS" if r['success'] else "FAILED"
            print(f"{r['host']}: {status} (exit code: {r['exit_code']})")
            if show_output and r['output']:
                print(r['output'])
            if r['error']:
                print(f"Error: {r['error']}")
            print()
        print(f"Summary: {success_count}/{len(results)} successful")
        if failed_count > 0:
            raise typer.Exit(code=1)
        return
    
    # Compact mode
    if compact:
        for r in results:
            status = "✓" if r['success'] else "✗"
            output_preview = (r['output'] or r['error']).replace('\n', ' ')[:100]
            console.print(f"{status} [cyan]{r['host']}[/cyan] [{r['exit_code']}]: {output_preview}")
        console.print(f"\n{success_count}/{len(results)} successful")
        if failed_count > 0:
            raise typer.Exit(code=1)
        return
    
    console.print()
    failed_count = len(results) - success_count
    
    # Summary table
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
    console.print(f"[bold]Results:[/bold] [green]{success_count} successful[/green], [red]{failed_count} failed[/red]")
    
    # Show detailed output if requested
    if show_output:
        console.print("\n[bold cyan]Detailed Output:[/bold cyan]")
        for result in results:
            title = f"{result['host']}"
            border_style = "green" if result['success'] else "red"
            
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
    
    # Audit log
    from remotex.audit import log_command_execution
    log_command_execution(
        command_type="exec-group",
        hosts=servers,
        command=command,
        results={r['host']: r for r in results},
        metadata={"group": group_name, "parallel": parallel, "timeout": timeout}
    )
    
    success_count = sum(1 for r in results if r['success'])
    console.print(f"\n[bold]Summary:[/bold] {success_count}/{len(results)} successful")
    
    # Add to history
    try:
        add_to_history(
            command="exec-group",
            args=[command],
            hosts=servers,
            success=(success_count == len(results)),
            metadata={
                "group_name": group_name,
                "total": len(results),
                "succeeded": success_count,
                "failed": len(results) - success_count,
                "parallel": parallel,
                "timeout": timeout
            }
        )
    except:
        pass  # Don't fail command if history fails
    
    if success_count < len(results):
        raise typer.Exit(code=1)

