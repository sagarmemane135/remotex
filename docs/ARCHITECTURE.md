# 🏗️ Architecture

**Version:** 1.0.0

This document describes the internal architecture of RemoteX for developers and contributors.

---

## 📁 Project Structure

```
remotex/
├── remotex/                          # Main package
│   ├── __init__.py                    # Package metadata & version
│   ├── cli.py                         # CLI entry point & command registration
│   ├── config.py                      # Configuration management (env vars, file)
│   ├── ssh_config.py                  # SSH config file operations (~/.ssh/config)
│   ├── ssh_client.py                  # SSH connection management
│   ├── performance.py                 # Caching & optimization utilities
│   ├── retry.py                       # Retry logic with exponential backoff
│   ├── audit.py                       # Command execution audit logging
│   ├── exit_codes.py                  # Standardized exit codes & error messages
│   ├── utils.py                       # Shared utilities
│   └── commands/                      # Command modules
│       ├── __init__.py
│       ├── server_management.py       # list, add, edit, remove, info
│       ├── exec_command.py            # exec command (single server)
│       ├── connect_command.py         # Interactive shell (PTY support)
│       ├── bulk_operations.py         # exec-all, exec-multi, exec-group
│       ├── quick_commands.py          # uptime, disk, memory, cpu, etc.
│       ├── config_command.py          # Configuration management
│       ├── group_management.py        # Server groups
│       ├── alias_management.py        # Command aliases
│       └── file_transfer.py           # push/pull (SFTP)
│
├── docs/                              # Documentation
│   ├── ARCHITECTURE.md                # This file
│   ├── CLI_BEST_PRACTICES_ANALYSIS.md # Best practices analysis
│   ├── CLI_BEST_PRACTICES_IMPLEMENTATION_STATUS.md # Implementation status
│   ├── PERFORMANCE.md                 # Performance guide
│   ├── QUICK_REFERENCE.md             # Command cheat sheet
│   └── PUBLISHING.md
│
├── main.py                            # Legacy wrapper (backward compatibility)
├── pyproject.toml                     # Package configuration
├── requirements.txt                   # Python dependencies
├── MANIFEST.in                        # Package manifest
└── README.md                          # Main documentation
```

---

## 🔧 Core Modules

### `remotex/__init__.py`
**Purpose:** Package metadata and version information

**Exports:**
- `__version__` - Package version (1.0.0)
- `__author__` - Author information
- `__description__` - Package description
- `__url__` - Repository URL

---

### `remotex/cli.py`
**Purpose:** Main CLI entry point and command registration

**Key Components:**
- `app` - Main Typer application instance
- `GlobalState` - Global state for verbose/debug modes
- `main_callback()` - Global callback for `--verbose`, `--debug`, `--version`
- `version_command()` - Version information command
- `examples_command()` - Usage examples command
- `main()` - Entry point with error handling

**Command Registration:**
All command modules are registered here:
```python
register_server_commands(app)
register_exec_command(app)
register_connect_command(app)
register_bulk_commands(app)
register_quick_commands(app)
register_config_command(app)
register_group_commands(app)
register_alias_commands(app)
register_file_transfer_commands(app)
```

**Features:**
- Shell completion enabled (`add_completion=True`)
- Rich markup mode for beautiful help
- Global `--verbose` and `--debug` flags
- `--version` flag with callback

---

### `remotex/config.py`
**Purpose:** Configuration management with environment variable support

**Key Functions:**
- `load_config()` - Load config from file + environment variables
- `save_config()` - Save configuration to file
- `get_default_server()` / `set_default_server()` - Default server management
- `get_groups()` / `add_group()` - Server group management
- `get_command_aliases()` / `add_command_alias()` - Command alias management
- `validate_config()` - Validate configuration file
- `export_config()` - Export config to JSON file
- `import_config()` - Import config from JSON file

**Environment Variables:**
- `REMOTEX_DEFAULT_SERVER` - Default server name
- `REMOTEX_OUTPUT_MODE` - Output mode (normal/compact/silent)
- `REMOTEX_PARALLEL` - Default parallel connections
- `REMOTEX_TIMEOUT` - Default timeout in seconds
- `REMOTEX_AUDIT_ENABLED` - Enable/disable audit logging

**Config File:** `~/.remotex/config.json`

---

### `remotex/ssh_config.py`
**Purpose:** SSH configuration file operations

**Key Functions:**
- `get_ssh_config_path()` - Get `~/.ssh/config` path
- `ensure_ssh_config_exists()` - Create SSH config if missing
- `get_all_hosts()` - List all configured hosts
- `parse_ssh_config()` - Parse host configuration
- `add_host_to_config()` - Add new host to SSH config
- `remove_host_from_config()` - Remove host from SSH config
- `host_exists()` - Check if host exists

**File:** `~/.ssh/config` (standard SSH format)

---

### `remotex/ssh_client.py`
**Purpose:** SSH connection management

**Key Functions:**
- `create_ssh_client()` - Create and connect SSH client using Paramiko

**Features:**
- SSH key authentication support
- Automatic host key policy (AutoAddPolicy)
- Error handling with Rich panels
- Connection timeout management

---

### `remotex/exit_codes.py`
**Purpose:** Standardized exit codes and error messages

**Exit Code Categories:**
- `SUCCESS = 0` - Successful execution
- `GENERAL_ERROR = 1` - General errors
- `CONNECTION_ERROR = 10` - Connection failures
- `AUTH_ERROR = 12` - Authentication failures
- `HOST_NOT_FOUND = 21` - Host not found
- `COMMAND_FAILED = 30` - Command execution failed
- And more...

**Features:**
- `ERROR_MESSAGES` - Error message templates with suggestions
- `get_error_suggestions()` - Get helpful error messages

---

### `remotex/retry.py`
**Purpose:** Retry logic with exponential backoff

**Key Functions:**
- `retry_with_backoff()` - Retry function with exponential backoff
- `should_retry_error()` - Determine if error is retryable

**Features:**
- Configurable max retries
- Exponential backoff with max delay
- Verbose mode for retry attempts
- Automatic retry on transient failures

---

### `remotex/audit.py`
**Purpose:** Command execution audit logging

**Key Functions:**
- `log_command_execution()` - Log command execution to audit log
- `get_recent_audit_entries()` - Get recent audit entries
- `search_audit_log()` - Search audit log with filters

**Features:**
- JSON-formatted audit entries
- Tracks user, hosts, commands, results
- Success/failure statistics
- Searchable audit history

**File:** `~/.remotex/audit.log`

---

### `remotex/performance.py`
**Purpose:** Caching and optimization utilities

**Key Functions:**
- `cache_data()` - Cache data with TTL
- `get_cached_data()` - Get cached data if valid
- `clear_cache()` - Clear all cached data
- `cached()` - Decorator for function result caching

**Cache Directory:** `~/.remotex/cache/`

---

## 📦 Command Modules

### `commands/server_management.py`
**Commands:** `list`, `add`, `edit`, `remove`, `info`

**Features:**
- Beautiful table formatting with Rich
- Interactive prompts for adding servers
- Server information with connection testing
- SSH config integration

---

### `commands/exec_command.py`
**Command:** `exec`

**Features:**
- Multiple output modes (formatted, plain, compact, silent)
- Rich panels for output display
- Exit code propagation
- Error handling

---

### `commands/connect_command.py`
**Command:** `connect`

**Features:**
- Interactive PTY shell sessions
- Cross-platform support (Windows/Unix)
- Real-time I/O streaming
- Works with interactive programs (vim, top, etc.)

**Platform Support:**
- Windows: Uses `msvcrt` and threading
- Unix/Linux: Uses `termios`, `tty`, and `select`

---

### `commands/bulk_operations.py`
**Commands:** `exec-all`, `exec-multi`, `exec-group`

**Features:**
- Parallel execution with ThreadPoolExecutor
- Progress bars with Rich
- JSON output mode for CI/CD
- Dry-run mode for safety
- Retry logic with exponential backoff
- Summary tables with success/failure counts

**Options:**
- `--parallel` - Number of parallel connections
- `--timeout` - Command timeout
- `--retries` - Retry attempts
- `--dry-run` - Preview without execution
- `--json` - JSON output mode
- `--no-output` - Summary only

---

### `commands/quick_commands.py`
**Commands:** `uptime`, `disk`, `memory`, `cpu`, `processes`, `status`, `restart`, `logs`

**Features:**
- Quick DevOps shortcuts
- Default server support
- Compact output by default
- Service management commands

---

### `commands/config_command.py`
**Commands:** `config show`, `config set-default`, `config alias`, `config validate`, `config export`, `config import`

**Features:**
- Configuration display
- Default server management
- Server alias management
- Config validation
- Config export/import

---

### `commands/group_management.py`
**Commands:** `group add`, `group list`, `group show`, `group add-server`, `group remove-server`, `group remove`

**Features:**
- Server group organization
- Group-based bulk operations
- Server validation

---

### `commands/alias_management.py`
**Commands:** `alias add`, `alias list`, `alias show`, `alias remove`

**Features:**
- Command alias management
- Reusable command shortcuts
- Alias validation

---

### `commands/file_transfer.py`
**Commands:** `push`, `pull`

**Features:**
- SFTP file transfer
- Recursive directory transfer
- Progress bars with transfer speed
- Automatic directory creation

---

## 🔄 Data Flow

### Command Execution Flow

```
User Input
    ↓
cli.py (main_callback)
    ↓
Command Module (e.g., exec_command.py)
    ↓
config.py (load_config) → Environment Variables + File
    ↓
ssh_config.py (parse_ssh_config)
    ↓
ssh_client.py (create_ssh_client)
    ↓
Paramiko SSH Client
    ↓
Remote Server
    ↓
Results → Rich Console Output
    ↓
audit.py (log_command_execution)
```

### Configuration Loading Priority

1. **Environment Variables** (highest priority)
2. **Config File** (`~/.remotex/config.json`)
3. **Defaults** (lowest priority)

---

## 🎨 Design Patterns

### 1. Modular Command Architecture
Each command module is self-contained with a `register_*_commands()` function.

### 2. Separation of Concerns
- SSH config operations → `ssh_config.py`
- Connection management → `ssh_client.py`
- Configuration → `config.py`
- Commands → `commands/*.py`

### 3. Error Handling
- Standardized exit codes → `exit_codes.py`
- Rich error panels with suggestions
- Debug mode for detailed errors

### 4. Performance Optimization
- Parallel execution for bulk operations
- Caching infrastructure
- Connection pooling capability

### 5. Cross-Platform Support
- Windows-specific code in `connect_command.py`
- Platform detection for terminal handling
- Path handling with `pathlib`

---

## 🚀 Adding New Features

### Adding a New Command

1. **Create command file** in `remotex/commands/`:
```python
# remotex/commands/my_command.py
import typer
from rich.console import Console
from remotex.exit_codes import ExitCode

console = Console()

def register_my_command(app: typer.Typer):
    """Register my command."""
    app.command(name="mycommand")(my_command)

def my_command(
    host: str = typer.Argument(..., help="Server hostname"),
    option: bool = typer.Option(False, "--option", help="Some option")
):
    """My new command description."""
    try:
        # Implementation
        console.print("[green]Success![/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=ExitCode.GENERAL_ERROR)
```

2. **Register in `cli.py`**:
```python
from remotex.commands.my_command import register_my_command

# In main() or after app creation
register_my_command(app)
```

3. **Reinstall package**:
```bash
pip install -e .
```

### Adding Configuration Options

1. **Add to `config.py`**:
```python
def get_my_setting() -> str:
    """Get my setting."""
    config = load_config()
    # Check env var first
    env_value = os.getenv(f"{ENV_PREFIX}MY_SETTING")
    if env_value:
        return env_value
    return config.get("my_setting", "default")
```

2. **Update default config** in `load_config()`

### Adding Exit Codes

1. **Add to `exit_codes.py`**:
```python
class ExitCode:
    MY_ERROR = 70  # Use appropriate range
```

2. **Add error message**:
```python
ERROR_MESSAGES = {
    ExitCode.MY_ERROR: {
        "title": "My Error",
        "suggestions": ["Fix suggestion 1", "Fix suggestion 2"]
    }
}
```

---

## 📊 Module Dependencies

```
cli.py
├── config.py
├── exit_codes.py
└── commands/
    ├── server_management.py
    │   ├── ssh_config.py
    │   └── ssh_client.py
    ├── exec_command.py
    │   ├── ssh_config.py
    │   └── ssh_client.py
    ├── bulk_operations.py
    │   ├── ssh_config.py
    │   ├── ssh_client.py
    │   ├── retry.py
    │   └── audit.py
    └── ...
```

---

## 🔐 Security Considerations

1. **SSH Key Authentication** - No password storage
2. **File Permissions** - Proper permissions on config files
3. **Connection Timeouts** - Prevent hanging connections
4. **Audit Logging** - Track all command executions
5. **Input Validation** - Validate all user inputs
6. **Error Messages** - Don't leak sensitive information

---

## 🧪 Testing Strategy

### Unit Tests
- Test individual functions in isolation
- Mock SSH connections
- Test configuration loading

### Integration Tests
- Test command execution flow
- Test error handling
- Test cross-platform compatibility

### Manual Testing
- Test with real SSH servers
- Test all output modes
- Test bulk operations

---

## 📈 Performance Characteristics

- **Startup Time:** < 100ms
- **Parallel Execution:** 5-20x faster than sequential
- **Connection Pooling:** Reusable connections
- **Caching:** TTL-based caching for performance

---

## 🔮 Future Enhancements

1. **Command History** - Track executed commands
2. **Config Templates** - Pre-defined configurations
3. **SSH Tunneling** - Port forwarding support
4. **Cloud Integration** - AWS/Azure/GCP integration
5. **Web UI** - Browser-based interface
6. **Plugin System** - Extensible command system

---

---

## 📚 References

- [Typer Documentation](https://typer.tiangolo.com/)
- [Paramiko Documentation](https://www.paramiko.org/)
- [Rich Documentation](https://rich.readthedocs.io/)
