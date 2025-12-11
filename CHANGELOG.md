# Changelog

All notable changes to RemoteX will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-12-11

### Changed
- **Package Rename**: Renamed from `remotex688` to `remotex` for professional branding
  - PyPI package name: `remotex`
  - GitHub repository: `sagarmemane135/remotex`
  - CLI command remains: `remotex` (no breaking changes for users)

### Fixed
- **Python 3.8 Compatibility**: Fixed `tuple[]/list[]` type hints (now use `Tuple[]/List[]` from typing)
- **Mypy Type Checking**: Resolved all 18 type errors across 5 files
  - Added type annotations for pstats.Stats attributes
  - Fixed Optional[str] type mismatches in quick_commands
  - Removed duplicate function definitions
  - Fixed stdin encoding and bitwise operation issues
- **Bandit Security**: Addressed security warnings with nosec annotations
  - B507: AutoAddPolicy usage documented (SSH config manages host keys)
  - B601: exec_command usage documented (trusted admin input)
- **CI/CD Pipeline**: Fixed all GitHub Actions failures
  - YAML syntax error (duplicate continue-on-error)
  - Type checking now passes on Python 3.8-3.12
  - All test matrix combinations now pass

## [Unreleased]

### Added - Production-Ready Output Modes (2025-12-11)

#### DevOps Automation & Scriptability
- **`--json` flag** with pure JSON output (no decorative panels) for CI/CD pipelines
  - Perfect for piping to `jq` or parsing in scripts
  - Structured output with command, hosts, success/failure counts
  - Available in exec-all, exec-multi, exec-group
- **`--csv` flag** for spreadsheet/reporting integration
  - Export results to CSV format with headers
  - Import into Excel, databases, or analytics tools
- **`--quiet` / `-q` flag** for minimal scriptable output
  - One-line output per server: `host: ✓ [0] output`
  - Perfect for shell scripts and log files
- **`--plain` flag** for simple text without ANSI formatting
  - No colors or Rich formatting
  - Compatible with legacy terminals and plain text logs
- **`--compact` flag** for condensed single-line format
  - Quick status checks with minimal output
  - Shows: `✓ host [exit_code]: preview`
- **`--show-output` flag** now opt-in (was always-on)
  - Default behavior: show summary table only
  - Use `--show-output` to display detailed command output
  - Reduces terminal clutter for bulk operations

#### Enhancements
- **Output preview increased** from 50 to 150 characters (3x more context)
- **Progress bars suppressed** for machine-readable formats (json, csv, quiet)
- **Decorative panels skipped** when using automation-friendly output modes
- All output modes available across exec-all, exec-multi, exec-group

### Fixed - Command History Integration (2025-12-11)

#### History Tracking
- Fixed history feature not recording commands
- Added `add_to_history()` integration to all command execution paths:
  - `exec` command now tracks single server executions
  - `exec-all` tracks bulk operations with success/failure counts
  - `exec-multi` tracks multi-server operations
  - `exec-group` tracks group-based operations
- History now captures metadata: exit codes, parallel settings, retry counts
- History file (`~/.remotex/history.json`) automatically created on first use

### Added - Phase 2: Reliability & Integration

#### Retry Logic with Exponential Backoff
- `--retries` flag for all bulk operations (exec-all, exec-multi, exec-group)
- Automatic retry on transient failures (timeouts, connection errors)
- Exponential backoff between retry attempts
- Configurable retry count (default: 0, max recommended: 5)
- Verbose mode shows retry attempts in real-time

#### JSON Output Mode
- `--json` flag for machine-readable output on all bulk operations
- Structured JSON with command, hosts, success/failure counts
- Individual host results with exit codes and output
- Perfect for CI/CD pipelines and monitoring
- Compatible with `jq` for advanced filtering

### Added - Phase 1: High-ROI Features

#### Server Groups & Organization
- `group add/remove/list/show` commands for organizing servers
- `group add-server` and `remove-server` for managing group membership
- `exec-group` command to execute commands on all servers in a group
- Server tags support for flexible categorization
- Group-based bulk operations with `--dry-run` support

#### Command Aliases & Macros
- `alias add/remove/list/show` commands for reusable command shortcuts
- Store frequently used commands as aliases
- Reduce typing and improve consistency

#### File Transfer (SFTP)
- `push` command to upload files/directories to remote servers
- `pull` command to download files/directories from remote servers  
- Recursive directory transfer with `--recursive` flag
- Progress bars with transfer speed indicators
- Automatic parent directory creation

#### Safety & Dry-Run Mode
- `--dry-run` flag for `exec-all`, `exec-multi`, and `exec-group`
- Preview affected servers and commands before execution
- Prevents accidental mass operations
- Shows detailed impact summary

#### Audit Logging
- Automatic command execution logging to `~/.remotex/audit.log`
- JSON-formatted audit entries with timestamps
- Track user, hosts, commands, and results
- Success/failure statistics per execution
- Searchable audit history for compliance

#### CLI Best Practices
- `--version` flag for quick version check (works standalone)
- `version` command showing detailed version information
- `examples` command with formatted usage examples
- Standardized exit codes system (0-130) with error suggestions
- `--verbose` and `--debug` global flags for enhanced logging
- Shell completion support (bash/zsh/fish)

### Changed
- Improved CLI user experience following best practices
- Enhanced error handling with meaningful exit codes
- Config schema extended with groups, tags, and aliases (backward compatible)

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
- Configuration persistence at `~/.remotex/config.json`

#### Performance & Optimization
- Parallel execution with ThreadPoolExecutor
- Connection pooling capability
- Caching infrastructure with TTL support
- Compact output modes for CI/CD pipelines
- Default server support to reduce typing

#### Developer Features
- Modular architecture with separate command modules
- Python package with `remotex` CLI entry point
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
remotex/
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
- Converted from `python main.py` execution to installable `remotex` command
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

This is the first production-ready release of RemoteX, a high-performance SSH management CLI designed specifically for DevOps engineers managing multiple servers.

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
remotex --help
```

For detailed usage, see [README.md](README.md) and [QUICK_REFERENCE.md](QUICK_REFERENCE.md).

---

[1.0.0]: https://github.com/sagarmemane135/remotex/releases/tag/v1.0.0
