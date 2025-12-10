#!/usr/bin/env python3
"""
OmniHost CLI Entry Point
Main command-line interface for OmniHost SSH server management tool.
"""

import typer

from omnihost.commands.server_management import register_server_commands
from omnihost.commands.exec_command import register_exec_command
from omnihost.commands.connect_command import register_connect_command
from omnihost.commands.bulk_operations import register_bulk_commands
from omnihost.commands.quick_commands import register_quick_commands
from omnihost.commands.config_command import register_config_command

# Initialize the main Typer app
app = typer.Typer(
    name="omnihost",
    help="🚀 OmniHost - Manage SSH servers and execute commands remotely",
    add_completion=False,
    rich_markup_mode="rich",
)

# Register all command modules
register_server_commands(app)
register_exec_command(app)
register_connect_command(app)
register_bulk_commands(app)
register_quick_commands(app)
register_config_command(app)


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
