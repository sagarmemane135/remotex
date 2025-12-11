#!/usr/bin/env python3
"""
Post-install script to install man pages
This can be run after package installation to install man pages
"""

import os
import sys
import shutil
from pathlib import Path


def get_man_path():
    """Get the system man path."""
    # Try common locations
    possible_paths = [
        Path("/usr/share/man"),
        Path("/usr/local/share/man"),
        Path.home() / ".local/share/man",
    ]
    
    # Check if any exist
    for path in possible_paths:
        if path.exists():
            return path
    
    # Default to /usr/share/man
    return Path("/usr/share/man")


def install_man_pages(dry_run=False):
    """Install man pages to system man directory."""
    # Find the package installation location
    try:
        import remotex
        package_path = Path(remotex.__file__).parent.parent
    except ImportError:
        # Fallback to current directory
        package_path = Path(__file__).parent
    
    man_source = package_path / "man"
    
    if not man_source.exists():
        print(f"Warning: Man pages not found at {man_source}")
        print("Man pages may not be included in the package.")
        return False
    
    man_dest = get_man_path()
    
    if dry_run:
        print(f"Would copy man pages from {man_source} to {man_dest}")
        return True
    
    # Check for sudo/admin rights
    if os.geteuid() != 0 and str(man_dest).startswith("/usr"):
        print("Installing man pages requires administrator privileges.")
        print(f"Please run: sudo python -m remotex.install_man_pages")
        print(f"Or manually: sudo cp -r {man_source}/* {man_dest}/")
        return False
    
    try:
        # Copy man pages
        for man_file in man_source.rglob("*.1"):
            rel_path = man_file.relative_to(man_source)
            dest_file = man_dest / rel_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(man_file, dest_file)
            print(f"Installed: {dest_file}")
        
        # Update man database if mandb exists
        if shutil.which("mandb"):
            import subprocess
            subprocess.run(["mandb"], check=False)
            print("Updated man database.")
        
        print("✓ Man pages installed successfully!")
        return True
    
    except PermissionError:
        print("Permission denied. Please run with sudo.")
        return False
    except Exception as e:
        print(f"Error installing man pages: {e}")
        return False


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    install_man_pages(dry_run=dry_run)

