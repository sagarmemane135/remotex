#!/usr/bin/env python3
"""
Module to install man pages after package installation
Usage: python -m remotex.install_man_pages
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


def install_man_pages():
    """Install man pages to system man directory."""
    # Find the package installation location
    try:
        import remotex
        package_path = Path(remotex.__file__).parent.parent
    except ImportError:
        # Fallback to current directory
        package_path = Path(__file__).parent.parent
    
    # Try multiple locations for man pages
    possible_man_locations = [
        package_path / "man",
        Path(__file__).parent.parent / "man",
        Path("/usr/share/remotex/man"),
    ]
    
    man_source = None
    for loc in possible_man_locations:
        if loc.exists() and (loc / "man1").exists():
            man_source = loc
            break
    
    if not man_source:
        print("Warning: Man pages not found in package.")
        print("They may need to be generated first:")
        print("  python scripts/generate_man_pages.py")
        return False
    
    man_dest = get_man_path()
    
    # Check for sudo/admin rights
    if os.geteuid() != 0 and str(man_dest).startswith("/usr"):
        print("Installing man pages to system directory requires administrator privileges.")
        print(f"Please run: sudo python -m remotex.install_man_pages")
        print(f"Or manually: sudo cp -r {man_source}/* {man_dest}/")
        return False
    
    try:
        # Copy man pages
        installed = 0
        for man_file in man_source.rglob("*.1"):
            rel_path = man_file.relative_to(man_source)
            dest_file = man_dest / rel_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(man_file, dest_file)
            print(f"Installed: {dest_file}")
            installed += 1
        
        if installed == 0:
            print("No man pages found to install.")
            return False
        
        # Update man database if mandb exists
        if shutil.which("mandb"):
            import subprocess
            result = subprocess.run(["mandb"], capture_output=True, text=True)
            if result.returncode == 0:
                print("Updated man database.")
        
        print(f"✓ Successfully installed {installed} man page(s)!")
        print(f"  You can now use: man remotex")
        return True
    
    except PermissionError:
        print("Permission denied. Please run with sudo.")
        return False
    except Exception as e:
        print(f"Error installing man pages: {e}")
        return False


if __name__ == "__main__":
    install_man_pages()

