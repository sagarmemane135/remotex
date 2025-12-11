"""
RemoteX File Transfer Commands
Push and pull files using SFTP
"""

import os
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TransferSpeedColumn, DownloadColumn
from rich import box

from remotex.ssh_config import parse_ssh_config
from remotex.ssh_client import create_ssh_client

console = Console()


def register_file_transfer_commands(app: typer.Typer):
    """Register file transfer commands."""
    app.command(name="push")(push)
    app.command(name="pull")(pull)


def push(
    host: str = typer.Argument(..., help="Target server"),
    local_path: str = typer.Argument(..., help="Local file or directory path"),
    remote_path: str = typer.Argument(..., help="Remote destination path"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Transfer directories recursively")
):
    """
    Push (upload) files to a remote server using SFTP.
    
    Example:
        remotex push web01 ./app.tar /opt/app/
        remotex push db01 ./config.json /etc/myapp/
        remotex push web01 ./dist /var/www/ --recursive
    """
    # Validate local path
    local = Path(local_path)
    if not local.exists():
        console.print(f"[red]✗[/red] Local path '[cyan]{local_path}[/cyan]' not found")
        raise typer.Exit(1)
    
    is_dir = local.is_dir()
    
    if is_dir and not recursive:
        console.print(f"[red]✗[/red] '[cyan]{local_path}[/cyan]' is a directory. Use --recursive to upload directories.")
        raise typer.Exit(1)
    
    console.print(Panel(
        f"[cyan]Source:[/cyan] {local_path}\n"
        f"[cyan]Destination:[/cyan] {host}:{remote_path}\n"
        f"[cyan]Type:[/cyan] {'Directory' if is_dir else 'File'}",
        title="📤 Push (Upload)",
        border_style="cyan",
        box=box.ROUNDED
    ))
    
    # Connect to server
    host_config = parse_ssh_config(host)
    if not host_config:
        console.print(f"[red]✗[/red] Failed to parse SSH config for '[cyan]{host}[/cyan]'")
        raise typer.Exit(1)
    
    client = create_ssh_client(host_config)
    if not client:
        console.print(f"[red]✗[/red] Failed to connect to '[cyan]{host}[/cyan]'")
        raise typer.Exit(1)
    
    try:
        sftp = client.open_sftp()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            console=console
        ) as progress:
            if is_dir:
                # Recursive directory upload
                task = progress.add_task(f"[cyan]Uploading directory...", total=None)
                _upload_dir_recursive(sftp, local_path, remote_path, progress, task)
            else:
                # Single file upload
                file_size = local.stat().st_size
                task = progress.add_task(f"[cyan]Uploading {local.name}...", total=file_size)
                
                def callback(transferred, total):
                    progress.update(task, completed=transferred)
                
                sftp.put(local_path, remote_path, callback=callback)
        
        sftp.close()
        client.close()
        
        console.print(f"[green]✓[/green] Successfully uploaded to '[cyan]{host}:{remote_path}[/cyan]'")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Upload failed: {e}")
        if client:
            client.close()
        raise typer.Exit(1)


def pull(
    host: str = typer.Argument(..., help="Source server"),
    remote_path: str = typer.Argument(..., help="Remote file or directory path"),
    local_path: str = typer.Argument(..., help="Local destination path"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Transfer directories recursively")
):
    """
    Pull (download) files from a remote server using SFTP.
    
    Example:
        remotex pull web01 /var/log/nginx/access.log ./logs/
        remotex pull db01 /etc/mysql/my.cnf ./configs/
        remotex pull web01 /var/www/html ./backup/ --recursive
    """
    console.print(Panel(
        f"[cyan]Source:[/cyan] {host}:{remote_path}\n"
        f"[cyan]Destination:[/cyan] {local_path}\n"
        f"[cyan]Recursive:[/cyan] {'Yes' if recursive else 'No'}",
        title="📥 Pull (Download)",
        border_style="cyan",
        box=box.ROUNDED
    ))
    
    # Connect to server
    host_config = parse_ssh_config(host)
    if not host_config:
        console.print(f"[red]✗[/red] Failed to parse SSH config for '[cyan]{host}[/cyan]'")
        raise typer.Exit(1)
    
    client = create_ssh_client(host_config)
    if not client:
        console.print(f"[red]✗[/red] Failed to connect to '[cyan]{host}[/cyan]'")
        raise typer.Exit(1)
    
    try:
        sftp = client.open_sftp()
        
        # Check if remote path is a directory
        try:
            sftp.stat(remote_path)
            remote_attrs = sftp.lstat(remote_path)
            is_dir = bool(remote_attrs.st_mode and (remote_attrs.st_mode & 0o040000))  # Directory bit
        except IOError:
            console.print(f"[red]✗[/red] Remote path '[cyan]{remote_path}[/cyan]' not found")
            sftp.close()
            client.close()
            raise typer.Exit(1)
        
        if is_dir and not recursive:
            console.print(f"[red]✗[/red] '[cyan]{remote_path}[/cyan]' is a directory. Use --recursive to download directories.")
            sftp.close()
            client.close()
            raise typer.Exit(1)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            console=console
        ) as progress:
            if is_dir:
                # Recursive directory download
                task = progress.add_task(f"[cyan]Downloading directory...", total=None)
                _download_dir_recursive(sftp, remote_path, local_path, progress, task)
            else:
                # Single file download
                file_size = remote_attrs.st_size
                task = progress.add_task(f"[cyan]Downloading {Path(remote_path).name}...", total=file_size)
                
                # Ensure local directory exists
                Path(local_path).parent.mkdir(parents=True, exist_ok=True)
                
                def callback(transferred, total):
                    progress.update(task, completed=transferred)
                
                sftp.get(remote_path, local_path, callback=callback)
        
        sftp.close()
        client.close()
        
        console.print(f"[green]✓[/green] Successfully downloaded to '[cyan]{local_path}[/cyan]'")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Download failed: {e}")
        if client:
            client.close()
        raise typer.Exit(1)


def _upload_dir_recursive(sftp, local_dir, remote_dir, progress, task):
    """Recursively upload a directory."""
    try:
        sftp.mkdir(remote_dir)
    except IOError:
        pass  # Directory may already exist
    
    for item in os.listdir(local_dir):
        local_path = os.path.join(local_dir, item)
        remote_path = f"{remote_dir}/{item}"
        
        if os.path.isfile(local_path):
            progress.update(task, description=f"[cyan]Uploading {item}...")
            sftp.put(local_path, remote_path)
        elif os.path.isdir(local_path):
            _upload_dir_recursive(sftp, local_path, remote_path, progress, task)


def _download_dir_recursive(sftp, remote_dir, local_dir, progress, task):
    """Recursively download a directory."""
    Path(local_dir).mkdir(parents=True, exist_ok=True)
    
    for item in sftp.listdir(remote_dir):
        remote_path = f"{remote_dir}/{item}"
        local_path = os.path.join(local_dir, item)
        
        try:
            attrs = sftp.lstat(remote_path)
            is_dir = attrs.st_mode & 0o040000
            
            if is_dir:
                _download_dir_recursive(sftp, remote_path, local_path, progress, task)
            else:
                progress.update(task, description=f"[cyan]Downloading {item}...")
                sftp.get(remote_path, local_path)
        except IOError:
            continue  # Skip inaccessible files
