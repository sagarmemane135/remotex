# 📖 Quick Reference

Command cheat sheet and quick examples for RemoteX.

## 📦 Installation
```bash
pip install -e .                       # Install in development mode
remotex --version                     # Check version
remotex --help                        # View all commands
remotex examples                      # See usage examples
```

## 🎯 Server Management
```bash
remotex list                          # List all servers
remotex list -v                       # Verbose (with SSH keys)
remotex add                           # Add new server (interactive)
remotex info <host>                   # Show server details + test connection
remotex edit <host>                   # Edit server config
remotex remove <host>                 # Remove server
```

## 👥 Server Groups
```bash
remotex group add web web01 web02 web03  # Create group
remotex group list                    # List all groups
remotex group show web                # Show group members
remotex group add-server web web04    # Add server to group
remotex group remove-server web web04 # Remove server from group
remotex group remove web              # Delete group
remotex exec-group web "uptime"       # Execute on group
remotex exec-group web "cmd" --dry-run # Preview execution
```

## 🔖 Command Aliases
```bash
remotex alias add restart-nginx "sudo systemctl restart nginx"
remotex alias add check-disk "df -h /"
remotex alias list                    # List all aliases
remotex alias show restart-nginx      # Show alias details
remotex alias remove restart-nginx    # Delete alias
```

## 📁 File Transfer (SFTP)
```bash
remotex push <host> <local> <remote>  # Upload file
remotex pull <host> <remote> <local>  # Download file
remotex push web01 ./app.tar /opt/app/
remotex pull db01 /var/log/app.log ./logs/
remotex push web01 ./dist /var/www/ -r  # Recursive directory
remotex pull web01 /etc/nginx ./backup/ -r
```

## 🔌 Remote Execution
```bash
remotex exec <host> "<command>"       # Execute command (formatted output)
remotex exec <host> "<command>" -p    # Plain output (no formatting)
remotex connect <host>                # Interactive shell with PTY
```

## ⚡ Quick Commands (Single Server)
```bash
remotex uptime <host>                 # Quick uptime check
remotex disk <host>                   # Disk usage (df -h)
remotex memory <host>                 # Memory usage (free -h)
remotex cpu <host>                    # CPU info
remotex processes <host>              # Top 10 processes
remotex status <host> <service>       # Service status
remotex restart <host> <service>      # Restart service (requires sudo)
remotex logs <host> <service> [opts]  # View logs (journalctl)
```

### Log Options
```bash
remotex logs <host> <service>         # Default: last 50 lines
remotex logs <host> <service> -n 100  # Last 100 lines
remotex logs <host> <service> -f      # Follow logs (real-time)
remotex logs <host> /path/to/log      # Custom log file
```

## 🚀 Bulk Operations (Multiple Servers in Parallel)
```bash
# Execute on ALL configured servers
remotex exec-all "<command>"          
remotex exec-all "<cmd>" -p 10        # 10 parallel connections
remotex exec-all "<cmd>" -t 60        # 60 second timeout
remotex exec-all "<cmd>" --show-output  # Show detailed output (opt-in)
remotex exec-all "<cmd>" --dry-run    # Preview before execution
remotex exec-all "<cmd>" --retries 3  # Retry failed commands 3 times

# Production-ready output modes
remotex exec-all "<cmd>" --json       # Pure JSON for CI/CD pipelines
remotex exec-all "<cmd>" --csv        # CSV for spreadsheets/reports
remotex exec-all "<cmd>" --quiet      # Minimal scriptable output
remotex exec-all "<cmd>" --plain      # Plain text (no ANSI colors)
remotex exec-all "<cmd>" --compact    # Condensed single-line format

# Execute on specific servers
remotex exec-multi "h1,h2,h3" "<cmd>"     # Comma-separated list
remotex exec-multi "web01,web02" "<cmd>" -p 3  # With parallelism
remotex exec-multi "h1,h2" "<cmd>" --dry-run  # Preview first
remotex exec-multi "h1,h2" "<cmd>" --json     # JSON output
remotex exec-multi "h1,h2" "<cmd>" --quiet    # Minimal output

# Execute on server groups
remotex exec-group web "systemctl restart nginx"
remotex exec-group db "pg_dump mydb" -p 3
remotex exec-group prod "uptime" --dry-run  # Always preview on prod!
remotex exec-group web "<cmd>" --json       # JSON output
remotex exec-group prod "<cmd>" --csv       # CSV export
```

## 🎛️ Global Options
```bash
--version              # Show version and exit
--verbose, -v          # Verbose output with detailed logging
--debug                # Debug mode with extensive logging
--help                 # Show help message
```

## ⚙️ Environment Variables
```bash
export REMOTEX_DEFAULT_SERVER=web01    # Set default server
export REMOTEX_OUTPUT_MODE=compact     # Set output mode
export REMOTEX_PARALLEL=10             # Set default parallelism
export REMOTEX_TIMEOUT=60              # Set default timeout
export REMOTEX_AUDIT_ENABLED=true      # Enable/disable audit logging
```

## 🏛️ Common Command Options
```bash
-p, --parallel N       # Parallel connections (default: 5, range: 1-20)
-t, --timeout N        # Timeout in seconds (default: 30)
--show-output          # Show detailed output (opt-in, for bulk ops)
--plain                # Plain output without Rich formatting (single exec)
-n, --lines N          # Number of log lines (for logs command)
-f, --follow           # Follow logs in real-time

# Output modes (for bulk operations: exec-all, exec-multi, exec-group)
--json                 # Pure JSON output (no decorations, pipe to jq)
--csv                  # CSV format for spreadsheets/databases
--quiet, -q            # Minimal one-line output per server
--plain                # Simple text without ANSI colors
--compact              # Condensed single-line format
```

## 📊 Output Modes for Automation

RemoteX provides multiple output formats optimized for different workflows:

| Mode | Flag | Best For | Output Style |
|------|------|----------|-------------|
| **Interactive** | (default) | Human use | Rich formatting, colors, panels |
| **JSON** | `--json` | CI/CD, parsing | Pure JSON, no decorations |
| **CSV** | `--csv` | Reports, Excel | CSV format with headers |
| **Quiet** | `--quiet`, `-q` | Shell scripts | One line per server: host: ✓ [0] output |
| **Plain** | `--plain` | Logs, legacy | Simple text, no ANSI codes |
| **Compact** | `--compact` | Quick checks | Single line: ✓ host [0]: preview |

**Examples:**
```bash
# Parse with jq in CI/CD
remotex exec-all 'hostname' --json | jq -r '.results[] | select(.success) | .host'

# Export to spreadsheet
remotex exec-all 'uptime' --csv > server_uptime.csv

# Shell script integration
for line in $(remotex exec-all 'hostname' --quiet); do
  host=$(echo $line | cut -d: -f1)
  echo "Processing $host"
done

# Plain text for logging
remotex exec-all 'systemctl status app' --plain >> /var/log/deploy.log 2>&1

# Quick status check
remotex exec-all 'df -h /' --compact | grep -E '(9[0-9]|100)%'
```

## ⚙️ Configuration Management
```bash
remotex config show                   # Show current configuration
remotex config validate               # Validate configuration
remotex config export                 # Export config (backup)
remotex config export -o backup.json  # Export to specific file
remotex config import backup.json     # Import config (replace)
remotex config import backup.json --merge  # Import config (merge)
```

## 🔍 Audit & Compliance
```bash
cat ~/.remotex/audit.log              # View audit trail (JSON)
tail -f ~/.remotex/audit.log          # Monitor in real-time
grep '"user": "alice"' ~/.remotex/audit.log  # Filter by user
```

## 💡 Quick Examples

### Server Groups Workflow
```bash
# Organize servers
remotex group add web web01 web02 web03
remotex group add db db01 db02
remotex group add prod web01 db01

# Execute safely with dry-run
remotex exec-group web "systemctl restart nginx" --dry-run
remotex exec-group web "systemctl restart nginx"  # Now execute

# File deployment
remotex push web01 ./app-v2.tar /opt/app/
remotex exec-group web "cd /opt/app && tar xf app-v2.tar"
```

### Daily Operations
```bash
# Morning check: all servers up?
remotex exec-all "uptime" --compact

# Check disk space across infrastructure
remotex exec-all "df -h /" -p 10 --compact

# Export server inventory
remotex exec-all "hostname && uname -r" --csv > inventory.csv

# Shell script automation
remotex exec-all "systemctl is-active nginx" --quiet | while read line; do
  if echo $line | grep -q '✗'; then
    host=$(echo $line | cut -d: -f1)
    echo "ALERT: nginx down on $host" | mail -s "Alert" ops@example.com
  fi
done

# CI/CD Integration - JSON output
remotex exec-all "systemctl status app" --json | jq '.succeeded'
remotex exec-group prod "uptime" --json > results.json

# Quick health check on production
remotex uptime prod01
remotex disk prod01
remotex memory prod01
```

### Service Management
```bash
# Restart nginx on all web servers
remotex exec-multi "web01,web02,web03" "sudo systemctl restart nginx"

# Check service status
remotex status app01 nginx
remotex status db01 postgresql

# View recent logs
remotex logs web01 nginx -n 100
```

### Deployment
```bash
# Deploy to multiple servers
remotex exec-multi "app01,app02,app03" "cd /app && git pull && sudo systemctl restart app" -p 3

# Verify deployment
remotex exec-multi "app01,app02,app03" "curl -s localhost:8080/health"
```

### Troubleshooting
```bash
# Check all servers for high disk usage
remotex exec-all "df -h /" --no-output | grep "9[0-9]%"

# Find processes using high memory
remotex processes prod01

# Check last logins
remotex exec db01 "last -n 20"
```

## 💡 Pro Tips
1. Use **quick commands** for daily checks (faster to type)
2. Use **bulk operations** to save time on multiple servers
3. Adjust `--parallel` based on server load (2-5 for heavy ops, 10-20 for checks)
4. Use `--no-output` for large-scale operations where you only care about failures
5. Combine with Unix tools: `remotex exec-all "uptime" | grep load`
