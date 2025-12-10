# Project Structure

```
ServerManager/
├── main.py                          # Entry point - registers all commands
├── ssh_config.py                    # SSH config file operations
├── ssh_client.py                    # SSH client connection management
├── utils.py                         # Shared utilities
├── commands/                        # Command modules
│   ├── __init__.py
│   ├── server_management.py         # list, add, edit, remove, info
│   ├── exec_command.py              # exec command
│   └── connect_command.py           # connect command
├── requirements.txt                 # Dependencies
└── README.md                        # User documentation
```

## Module Descriptions

### `main.py` (36 lines)
- **Purpose**: Application entry point
- **Responsibilities**:
  - Initialize Typer app
  - Import and register all command modules
  - Handle application startup

### `ssh_config.py` (224 lines)
- **Purpose**: SSH configuration file management
- **Functions**:
  - `get_ssh_config_path()` - Get SSH config file path
  - `ensure_ssh_config_exists()` - Create config if missing
  - `get_all_hosts()` - List all configured servers
  - `parse_ssh_config()` - Parse host details
  - `add_host_to_config()` - Add new server
  - `remove_host_from_config()` - Remove server
  - `host_exists()` - Check if host exists

### `ssh_client.py` (52 lines)
- **Purpose**: SSH connection management
- **Functions**:
  - `create_ssh_client()` - Create and connect SSH client
  - Handles authentication with keys
  - Error handling for connection failures

### `commands/server_management.py` (259 lines)
- **Purpose**: Server CRUD operations
- **Commands**:
  - `list` - Display all servers in a table
  - `add` - Add new server (interactive or CLI)
  - `info` - Show server details
  - `edit` - Modify server configuration
  - `remove` - Delete server from config

### `commands/exec_command.py` (108 lines)
- **Purpose**: Remote command execution
- **Commands**:
  - `exec` - Execute commands on remote servers
- **Features**:
  - Formatted output with panels
  - Plain mode for piping
  - Error handling
  - Exit status reporting

### `commands/connect_command.py` (112 lines)
- **Purpose**: Interactive shell sessions
- **Commands**:
  - `connect` - Open interactive SSH shell
- **Features**:
  - Full PTY support
  - Terminal raw mode handling
  - Real-time I/O streaming
  - Works with interactive programs (top, vim, etc.)

## Adding New Features

### To add a new command:

1. **Create a new command file** in `commands/` directory:
```python
# commands/my_new_command.py
import typer
from ssh_config import parse_ssh_config
from ssh_client import create_ssh_client

def register_my_command(app: typer.Typer):
    app.command()(my_new_command)

def my_new_command(host: str):
    """My new command description."""
    # Your implementation
    pass
```

2. **Register in main.py**:
```python
from commands.my_new_command import register_my_command

# In main.py
register_my_command(app)
```

### To add new SSH config operations:

Add functions to `ssh_config.py`:
```python
def my_new_ssh_function():
    """New SSH config operation."""
    pass
```

### To add connection utilities:

Add functions to `ssh_client.py`:
```python
def my_connection_helper(client):
    """Helper for SSH connections."""
    pass
```

## Benefits of This Structure

1. **Separation of Concerns**:
   - SSH config logic isolated from commands
   - Connection management separate from business logic
   - Each command in its own file

2. **Scalability**:
   - Easy to add new commands without touching existing code
   - Modular structure allows parallel development
   - Clear boundaries between components

3. **Maintainability**:
   - Smaller files are easier to understand
   - Changes to one area don't affect others
   - Clear module responsibilities

4. **Testability**:
   - Each module can be tested independently
   - Mock SSH connections easily
   - Unit test individual commands

5. **Reusability**:
   - SSH config functions can be reused across commands
   - Client creation logic centralized
   - Common utilities shared via utils.py

## Example Usage After Refactoring

All commands work exactly the same as before:

```bash
# List servers
python main.py list
python main.py list --verbose

# Add server
python main.py add
python main.py add -a myserver -h 192.168.1.100 -u ubuntu

# Execute commands
python main.py exec s3-dev "ls -la"
python main.py exec s3-dev "df -h" --plain

# Connect interactively
python main.py connect s3-dev

# Server management
python main.py info s3-dev
python main.py edit s3-dev
python main.py remove s3-dev
```

## Future Enhancement Ideas

With this modular structure, you can easily add:

1. **Bulk Operations Module** (`commands/bulk_operations.py`)
   - Execute commands on multiple servers
   - Parallel execution
   - Result aggregation

2. **File Transfer Module** (`commands/file_transfer.py`)
   - SCP/SFTP file uploads
   - Batch file downloads
   - Progress tracking

3. **Monitoring Module** (`commands/monitoring.py`)
   - Server health checks
   - Resource monitoring
   - Alert notifications

4. **Configuration Templates** (`templates/`)
   - Pre-defined server configurations
   - Import/export configurations
   - Share configs across teams

5. **History & Logging** (`history.py`)
   - Command history
   - Execution logs
   - Audit trail

6. **SSH Tunneling** (`commands/tunneling.py`)
   - Port forwarding
   - Proxy management
   - Jump host support

7. **Plugin System**
   - Load external command modules
   - Custom integrations
   - Extension marketplace
