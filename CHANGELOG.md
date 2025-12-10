# Changelog

All notable changes to OmniHost will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `--version` flag for quick version check (works standalone)
- `version` command showing detailed version information
- `examples` command with formatted usage examples
- Standardized exit codes system (0-130) with error suggestions
- `--verbose` and `--debug` global flags for enhanced logging
- Shell completion support (bash/zsh/fish)

### Changed
- Improved CLI user experience following best practices
- Enhanced error handling with meaningful exit codes

## [1.0.0] - 2025-12-10

### Added

#### Server Management
- `list` command to display all configured servers in beautiful table format
- `add` command with interactive prompts for adding new servers
- `info` command to show detailed server information with connection testing
- `edit` command to modify existing server configurations
- `remove` command to delete servers with confirmation prompt
- Verbose mode (`-v`) for list command showing SSH keys

#### Remote Operations
- `exec` command for executing commands on remote servers
- `connect` command for interactive PTY shell sessions
- Support for formatted and plain output modes
- Connection timeout management
- SSH key authentication support

#### Bulk Operations (Performance Features)
- `exec-all` command to execute commands on ALL servers in parallel
- `exec-multi` command to execute on specific comma-separated server list
- Configurable parallelism (1-20 connections, default: 5)
- Progress bars for bulk execution
- Summary tables showing success/failure status
- Timeout control per command
- `--no-output` flag for summary-only mode

#### Quick DevOps Commands
- `uptime` - Quick uptime check
- `disk` - Disk usage (df -h)
- `memory` - Memory usage (free -h)
- `cpu` - CPU information
- `processes` - Top 10 processes
- `status` - Service status check
- `restart` - Service restart (requires sudo)
- `logs` - View service logs with journalctl
- Support for optional host parameter (uses default if not specified)

#### Configuration Management
- `config show` - Display current configuration
- `config set-default` - Set default server for quick commands
- `config clear-default` - Clear default server
- Configuration persistence at `~/.omnihost/config.json`

#### Performance & Optimization
- Parallel execution with ThreadPoolExecutor
- Connection pooling capability
- Caching infrastructure with TTL support
- Compact output modes for CI/CD pipelines
- Default server support to reduce typing

#### Developer Features
- Modular architecture with separate command modules
- Python package with `omnihost` CLI entry point
- Rich library integration for beautiful output
- Comprehensive error handling with informative messages
- Type hints throughout codebase
- Development mode installation support

#### Documentation
- Comprehensive README with badges and examples
- CONTRIBUTING.md with development guidelines
- CODE_OF_CONDUCT.md following Contributor Covenant
- QUICK_REFERENCE.md for command cheat sheet
- PERFORMANCE.md with DevOps patterns and benchmarks
- ARCHITECTURE.md for code structure
- SECURITY.md for vulnerability reporting
- MIT LICENSE

### Technical Details

#### Dependencies
- Python 3.8+
- typer >= 0.12.0 (CLI framework)
- paramiko >= 3.4.0 (SSH protocol)
- rich >= 13.7.0 (terminal formatting)

#### Project Structure
```
omnihost/
├── __init__.py
├── cli.py
├── config.py
├── ssh_config.py
├── ssh_client.py
├── performance.py
├── utils.py
└── commands/
    ├── server_management.py
    ├── exec_command.py
    ├── connect_command.py
    ├── bulk_operations.py
    ├── quick_commands.py
    └── config_command.py
```

#### Performance Benchmarks
- 5x faster than sequential execution with default settings
- Scales to 50+ servers efficiently
- Configurable parallelism for different workloads

### Changed
- Moved from monolithic `main.py` to modular package structure
- Converted from `python main.py` execution to installable `omnihost` command
- Enhanced output formatting with Rich library
- Improved error messages with context panels

### Deprecated
- Direct `python main.py` execution (still works via wrapper)

### Fixed
- IndentationError in SSH client identity file handling
- SyntaxError in connect command try-except blocks
- Import path issues after package refactoring
- Connection timeout handling
- SSH config file parsing edge cases

### Security
- SSH key-based authentication recommended
- No password storage
- Secure SSH config permissions enforcement
- Timeout protection against hanging connections

## [Unreleased]

### Planned Features
- Server grouping and tagging system
- Command history and replay functionality
- Custom command templates
- Real-time log streaming
- Integration with cloud providers (AWS, Azure, GCP)
- SSH tunnel management
- File transfer operations (SCP/SFTP)
- Ansible playbook integration
- Web UI for server management
- Output comparison across servers
- Jump host/bastion support

---

## Release Notes

### Version 1.0.0 - Initial Release

This is the first production-ready release of OmniHost, a high-performance SSH management CLI designed specifically for DevOps engineers managing multiple servers.

**Key Highlights:**
- ⚡ **5x faster** than traditional serial execution
- 🎯 **17 commands** covering all common DevOps operations
- 🚀 **Parallel execution** on up to 20 servers simultaneously
- 💎 **Beautiful CLI** with Rich-formatted output
- 🔧 **Zero config** required - works with existing SSH config

**Perfect For:**
- DevOps engineers managing multiple servers
- Site reliability engineers (SRE)
- System administrators
- Infrastructure teams
- Anyone tired of writing bash loops

**Try it now:**
```bash
pip install -e .
omnihost --help
```

For detailed usage, see [README.md](README.md) and [QUICK_REFERENCE.md](QUICK_REFERENCE.md).

---

[1.0.0]: https://github.com/sagar.memane/omnihost/releases/tag/v1.0.0
