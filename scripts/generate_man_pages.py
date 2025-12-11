#!/usr/bin/env python3
"""
Generate man pages from RemoteX command docstrings
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from remotex import __version__, __author__


def escape_man_text(text: str) -> str:
    """Escape special characters for man pages."""
    return text.replace('\\', '\\\\').replace('.', '\\.').replace('-', '\\-')


def generate_man_page(command_name: str, description: str, synopsis: str, 
                    options: list, examples: list = None) -> str:
    """Generate a man page in troff format."""
    
    date = datetime.now().strftime("%B %Y")
    
    man_page = f""".TH REMOTEX "{command_name}" "1" "{date}" "RemoteX {__version__}" "User Commands"
.SH NAME
remotex-{command_name} \\- {description}
.SH SYNOPSIS
.B remotex {synopsis}
.SH DESCRIPTION
{escape_man_text(description)}
"""
    
    if options:
        man_page += ".SH OPTIONS\n"
        for opt in options:
            man_page += f".TP\n.BI {opt['flag']}\n{escape_man_text(opt['help'])}\n"
    
    if examples:
        man_page += ".SH EXAMPLES\n"
        for ex in examples:
            man_page += f".PP\n{escape_man_text(ex)}\n"
    
    man_page += f""".SH AUTHOR
{__author__}
.SH "SEE ALSO"
.BR remotex (1)
"""
    
    return man_page


def main():
    """Generate all man pages."""
    man_dir = Path(__file__).parent.parent / "man" / "man1"
    man_dir.mkdir(parents=True, exist_ok=True)
    
    # Main remotex man page
    main_man = f""".TH REMOTEX "1" "{datetime.now().strftime('%B %Y')}" "RemoteX {__version__}" "User Commands"
.SH NAME
remotex \\- High-Performance SSH Management CLI
.SH SYNOPSIS
.B remotex
.RI [ OPTIONS ]
.RI [ COMMAND ]
.RI [ ARGS ]
.SH DESCRIPTION
RemoteX is a high-performance command-line tool for managing SSH servers and executing commands remotely. It supports parallel execution, server groups, command aliases, and more.
.SH OPTIONS
.TP
.BI \\-v ", " \\-\\-verbose
Verbose output
.TP
.BI \\-\\-debug
Debug mode with detailed logging
.TP
.BI \\-\\-version
Show version and exit
.TP
.BI \\-\\-help
Show help message
.SH COMMANDS
.TP
.B list
List all configured servers
.TP
.B add
Add a new server to SSH config
.TP
.B exec
Execute a command on a remote server
.TP
.B connect
Open an interactive shell session
.TP
.B exec-all
Execute a command on all servers in parallel
.TP
.B exec-multi
Execute a command on specific servers
.TP
.B exec-group
Execute a command on all servers in a group
.TP
.B history
Manage command history
.TP
.B tunnel
Manage SSH tunnels
.SH EXAMPLES
.PP
List all servers:
.RS
.B remotex list
.RE
.PP
Execute command on server:
.RS
.B remotex exec web01 "uptime"
.RE
.PP
Execute on all servers in parallel:
.RS
.B remotex exec-all "df -h" --parallel 10
.RE
.SH AUTHOR
{__author__}
.SH "SEE ALSO"
Full documentation: https://github.com/sagarmemane135/remotex
"""
    
    with open(man_dir / "remotex.1", "w") as f:
        f.write(main_man)
    
    print(f"✓ Generated man page: {man_dir / 'remotex.1'}")
    print(f"\nTo install man pages:")
    print(f"  sudo cp -r man/* /usr/share/man/")
    print(f"  sudo mandb")


if __name__ == "__main__":
    main()

