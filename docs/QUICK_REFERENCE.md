# 📖 OmniHost Quick Reference

## 📦 Installation
```bash
pip install -e .                       # Install in development mode
omnihost --version                     # Check version
omnihost --help                        # View all commands
omnihost examples                      # See usage examples
```

## 🎯 Server Management
```bash
omnihost list                          # List all servers
omnihost list -v                       # Verbose (with SSH keys)
omnihost add                           # Add new server (interactive)
omnihost info <host>                   # Show server details + test connection
omnihost edit <host>                   # Edit server config
omnihost remove <host>                 # Remove server
```

## 🔌 Remote Execution
```bash
omnihost exec <host> "<command>"       # Execute command (formatted output)
omnihost exec <host> "<command>" -p    # Plain output (no formatting)
omnihost connect <host>                # Interactive shell with PTY
```

## ⚡ Quick Commands (Single Server)
```bash
omnihost uptime <host>                 # Quick uptime check
omnihost disk <host>                   # Disk usage (df -h)
omnihost memory <host>                 # Memory usage (free -h)
omnihost cpu <host>                    # CPU info
omnihost processes <host>              # Top 10 processes
omnihost status <host> <service>       # Service status
omnihost restart <host> <service>      # Restart service (requires sudo)
omnihost logs <host> <service> [opts]  # View logs (journalctl)
```

### Log Options
```bash
omnihost logs <host> <service>         # Default: last 50 lines
omnihost logs <host> <service> -n 100  # Last 100 lines
omnihost logs <host> <service> -f      # Follow logs (real-time)
omnihost logs <host> /path/to/log      # Custom log file
```

## 🚀 Bulk Operations (Multiple Servers in Parallel)
```bash
# Execute on ALL configured servers
omnihost exec-all "<command>"          
omnihost exec-all "<cmd>" -p 10        # 10 parallel connections
omnihost exec-all "<cmd>" -t 60        # 60 second timeout
omnihost exec-all "<cmd>" --no-output  # Summary only (hide outputs)

# Execute on specific servers
omnihost exec-multi "h1,h2,h3" "<cmd>"     # Comma-separated list
omnihost exec-multi "web01,web02" "<cmd>" -p 3  # With parallelism
```

## 🎛️ Global Options
```bash
--version              # Show version and exit
--verbose, -v          # Verbose output with detailed logging
--debug                # Debug mode with extensive logging
--help                 # Show help message
```

## 🎛️ Common Command Options
```bash
-p, --parallel N       # Parallel connections (default: 5, range: 1-20)
-t, --timeout N        # Timeout in seconds (default: 30)
--show-output          # Show individual outputs (default for bulk ops)
--no-output            # Hide outputs, show summary only
--plain                # Plain output without Rich formatting
-n, --lines N          # Number of log lines (for logs command)
-f, --follow           # Follow logs in real-time
```

## 💡 Quick Examples

### Daily Operations
```bash
# Morning check: all servers up?
omnihost exec-all "uptime"

# Check disk space across infrastructure
omnihost exec-all "df -h /" -p 10

# Quick health check on production
omnihost uptime prod01
omnihost disk prod01
omnihost memory prod01
```

### Service Management
```bash
# Restart nginx on all web servers
omnihost exec-multi "web01,web02,web03" "sudo systemctl restart nginx"

# Check service status
omnihost status app01 nginx
omnihost status db01 postgresql

# View recent logs
omnihost logs web01 nginx -n 100
```

### Deployment
```bash
# Deploy to multiple servers
omnihost exec-multi "app01,app02,app03" "cd /app && git pull && sudo systemctl restart app" -p 3

# Verify deployment
omnihost exec-multi "app01,app02,app03" "curl -s localhost:8080/health"
```

### Troubleshooting
```bash
# Check all servers for high disk usage
omnihost exec-all "df -h /" --no-output | grep "9[0-9]%"

# Find processes using high memory
omnihost processes prod01

# Check last logins
omnihost exec db01 "last -n 20"
```

## 🏗️ Project Structure
```
omnihost/
├── __init__.py                # Package metadata
├── cli.py                     # CLI entry point
├── ssh_config.py              # SSH config CRUD (224 lines)
├── ssh_client.py              # Connection management (52 lines)
├── utils.py                   # Shared utilities
├── performance.py             # Caching & optimizations
└── commands/
    ├── server_management.py   # list, add, edit, remove, info
    ├── exec_command.py        # Remote execution
    ├── connect_command.py     # Interactive shell
    ├── bulk_operations.py     # exec-all, exec-multi
    └── quick_commands.py      # uptime, disk, memory, etc.
```

## 🔧 Development

### Add New Command
1. Create function in appropriate module under `omnihost/commands/`
2. Register in `omnihost/cli.py`
3. Reinstall: `pip install -e .`

### Test Commands
```bash
omnihost --help                        # List all commands
omnihost list                          # Test server listing
omnihost exec <host> "echo test"       # Test execution
```

## 📚 Documentation
- **README.md** - Getting started & features
- **PERFORMANCE.md** - Performance guide & DevOps patterns
- **ARCHITECTURE.md** - Developer guide
- **QUICK_REFERENCE.md** - This file

## 🎨 Features
✅ 17 commands (server mgmt, execution, bulk ops, quick commands)
✅ Parallel execution with ThreadPoolExecutor
✅ Beautiful CLI with Rich library (tables, progress bars, panels)
✅ Interactive prompts & PTY shells
✅ SSH config management (~/.ssh/config)
✅ Caching infrastructure for performance
✅ Comprehensive error handling
✅ Modular & scalable architecture

## 💡 Pro Tips
1. Use **quick commands** for daily checks (faster to type)
2. Use **bulk operations** to save time on multiple servers
3. Adjust `--parallel` based on server load (2-5 for heavy ops, 10-20 for checks)
4. Use `--no-output` for large-scale operations where you only care about failures
5. Combine with Unix tools: `omnihost exec-all "uptime" | grep load`
