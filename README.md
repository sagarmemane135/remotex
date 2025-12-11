<div align="center">

# 🚀 RemoteX

### High-Performance SSH Management CLI for DevOps Engineers

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

Manage hundreds of servers with lightning-fast parallel execution, beautiful CLI output, and DevOps-focused shortcuts.

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## ⚡ Highlights

```bash
# Quick start
remotex --version              # Check version
remotex examples               # See usage examples

# Server Groups - organize your infrastructure
remotex group add web web01 web02 web03
remotex exec-group web "systemctl restart nginx"
remotex exec-group web "uptime" --dry-run  # Preview first!

# Command Aliases - reduce repetitive typing
remotex alias add restart-nginx "sudo systemctl restart nginx"
remotex exec-group web restart-nginx

# File Transfer - push/pull files easily
remotex push web01 ./app.tar /opt/app/
remotex pull db01 /var/log/mysql.log ./logs/
remotex push web01 ./dist /var/www/ --recursive

# Execute on all servers in parallel - 10x faster, with retry & dry-run
remotex exec-all "systemctl status nginx" --parallel 10 --retries 2 --dry-run
remotex exec-all "uptime" --json | jq '.succeeded'  # CI/CD integration

# Production-ready output modes for DevOps automation
remotex exec-all "hostname" --json       # Pure JSON (pipe to jq)
remotex exec-all "uptime" --csv          # CSV for spreadsheets
remotex exec-all "df -h" --quiet         # Minimal scriptable output
remotex exec-all "ps aux" --compact      # Condensed single-line
remotex exec-all "systemctl status nginx" --plain  # No colors/formatting

# Quick DevOps shortcuts - no need to type full exec commands
remotex uptime  # Uses default server
remotex disk web01
remotex memory db01

# Beautiful, formatted output with Rich library
remotex list  # Stunning table view of all servers

# Enhanced logging for troubleshooting
remotex --verbose exec web01 "ls -la"
remotex --debug exec-all "uptime"

# Audit logging - all commands tracked automatically
cat ~/.remotex/audit.log  # JSON audit trail

# Command History - track and replay commands
remotex history                    # List recent commands
remotex history show 42            # Show command details
remotex history replay 42          # Replay a command

# SSH Tunnels - port forwarding made easy
remotex tunnel create web01 8080 --remote-port 80
remotex tunnel list                 # List active tunnels
remotex tunnel stop web01 8080     # Stop a tunnel

# Jump Hosts - access private servers through bastions
remotex add private-server -h 10.0.0.5 --jump-host bastion

# Performance Profiling - optimize your operations
remotex profile list                # List profile files
remotex profile show profile.prof   # Analyze performance
```

## 🎯 Why RemoteX?

| Problem | Traditional Approach | RemoteX |
|---------|---------------------|----------|
| Check 20 servers | 20 × 3s = 60 seconds | 12 seconds (parallel) |
| Type repetitive commands | `ssh user@host 'uptime'` | `remotex uptime` |
| Manage server configs | Edit `~/.ssh/config` manually | Interactive `remotex add` |
| View command output | Plain text | Beautiful formatted panels |
| Execute on multiple servers | Write bash loops | `remotex exec-all` |

## ✨ Features

### 🖥️ Server Management
- **Add/Edit/Remove** servers with interactive prompts
- **List** all configured servers with beautiful table view
- **Info** command with connection testing
- Integrates with SSH config (`~/.ssh/config`)

### ⚡ Performance Features
- **Parallel execution** on multiple servers (5-20x faster)
- **Bulk operations** (`exec-all`, `exec-multi`, `exec-group`)
- **Quick commands** for common DevOps tasks
- **Default server** configuration (no need to specify every time)
- **Connection pooling** and caching
- **Production-ready output modes** (JSON, CSV, quiet, plain, compact)
- **Scriptable output** for CI/CD pipelines and automation

### 🎨 Beautiful CLI
- Rich formatted output with colors and panels
- Progress bars for bulk operations
- Interactive prompts with validation
- Clean, organized command structure

### 🔐 Security
- SSH key authentication support
- No password storage
- Respects SSH config security settings
- Connection timeout management
- **Audit logging** - All commands tracked automatically

### ⚙️ Configuration Management
- **Environment variables** - Configure via `REMOTEX_*` env vars
- **Config validation** - `remotex config validate`
- **Config export/import** - Backup and restore configurations
- **Default server** - Set once, use everywhere
- **Server groups** - Organize servers logically
- **Command aliases** - Reusable command shortcuts

## 📦 Installation

### From PyPI (Recommended)
```bash
pip install remotex
```

**Note:** After installation, you may want to install man pages:
```bash
# Linux/Mac (requires sudo for system-wide)
sudo python -m remotex.install_man_pages

# Or user-specific (no sudo needed)
python -m remotex.install_man_pages
```

Then you can use: `man remotex`

### From Source

```bash
# Clone the repository
git clone https://github.com/sagar.memane/remotex.git
cd remotex

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install
pip install -e .
```

### Requirements

- Python 3.8 or higher
- SSH access to remote servers
- SSH keys configured (recommended)

## 🚀 Quick Start

### 1. Add Your First Server

```bash
remotex add
# Follow interactive prompts
```

Or use command-line options:
```bash
remotex add -a web01 -h 192.168.1.100 -u ubuntu --key ~/.ssh/id_rsa
```

### 2. List Servers

```bash
remotex list           # Basic view
remotex list -v        # Verbose with SSH keys
```

### 3. Set Default Server (Optional)

```bash
remotex config set-default web01
# Now you can use: remotex uptime (without specifying server)

# Or use environment variable:
export REMOTEX_DEFAULT_SERVER=web01
```

### 4. Execute Commands

```bash
# Single server
remotex exec web01 "df -h"

# All servers (parallel)
remotex exec-all "uptime"

# Specific servers
remotex exec-multi "web01,web02,db01" "systemctl status nginx"

# Production-ready output modes
remotex exec-all "hostname" --json        # Pure JSON for parsing
remotex exec-all "uptime" --csv           # CSV for reports
remotex exec-all "df -h" --quiet          # Minimal for scripts
remotex exec-all "ps aux" --plain         # No ANSI colors
remotex exec-all "ls -la" --compact       # One line per server
remotex exec-all "uptime" --show-output   # Show detailed output (opt-in)
```

### 5. Quick DevOps Commands

```bash
remotex uptime web01          # Quick uptime
remotex disk web01            # Disk usage
remotex memory web01          # Memory usage
remotex processes web01       # Top processes
remotex status web01 nginx    # Service status
remotex logs web01 nginx      # View logs
```

### 6. Interactive Shell

```bash
remotex connect web01
# Full PTY support - run vim, htop, top, etc.
```

## ⚙️ Configuration

### Output Modes for DevOps Automation

RemoteX provides multiple output formats optimized for different use cases:

| Mode | Flag | Use Case | Example |
|------|------|----------|----------|
| **JSON** | `--json` | CI/CD pipelines, parsing with jq | `remotex exec-all 'cmd' --json \| jq` |
| **CSV** | `--csv` | Spreadsheets, reports, analytics | `remotex exec-all 'cmd' --csv > report.csv` |
| **Quiet** | `--quiet`, `-q` | Shell scripts, log files | `remotex exec-all 'cmd' --quiet` |
| **Plain** | `--plain` | Legacy systems, plain text logs | `remotex exec-all 'cmd' --plain` |
| **Compact** | `--compact` | Quick checks, condensed output | `remotex exec-all 'cmd' --compact` |
| **Default** | (none) | Interactive use, rich formatting | `remotex exec-all 'cmd'` |

**Key Features:**
- `--json` outputs pure JSON (no decorative panels) - perfect for piping to `jq`
- `--csv` exports to CSV format - import into Excel or databases
- `--quiet` provides minimal one-line output per server - ideal for scripts
- `--plain` removes all ANSI formatting - for legacy terminals or log files  
- `--compact` shows condensed single-line format - quick status checks
- `--show-output` displays detailed command output (opt-in, default is summary only)

**Examples:**
```bash
# Parse JSON in CI/CD pipeline
remotex exec-all 'hostname' --json | jq -r '.results[].output'

# Export to spreadsheet
remotex exec-all 'uptime' --csv > server_uptime.csv

# Shell script integration
for server in $(remotex exec-all 'hostname' --quiet | grep '✓' | cut -d: -f1); do
  echo "Processing $server"
done

# Clean logs without colors
remotex exec-all 'systemctl status nginx' --plain >> audit.log

# Quick status check
remotex exec-all 'df -h /' --compact
```

### Environment Variables

RemoteX supports configuration via environment variables (takes precedence over config file):

```bash
export REMOTEX_DEFAULT_SERVER=web01
export REMOTEX_OUTPUT_MODE=compact
export REMOTEX_PARALLEL=10
export REMOTEX_TIMEOUT=60
export REMOTEX_AUDIT_ENABLED=true
```

### Config Management

```bash
# Show current configuration
remotex config show

# Validate configuration
remotex config validate

# Export configuration (backup)
remotex config export
remotex config export --output my-config.json

# Import configuration (restore)
remotex config import my-config.json
remotex config import my-config.json --merge  # Merge with existing
```

## 📖 Documentation

- **[Quick Reference](docs/QUICK_REFERENCE.md)** - Command cheat sheet
- **[Performance Guide](docs/PERFORMANCE.md)** - Optimization tips
- **[Architecture](docs/ARCHITECTURE.md)** - Code structure
- **[CLI Best Practices](docs/CLI_BEST_PRACTICES_ANALYSIS.md)** - Best practices
- **[Feature Roadmap](docs/FEATURE_ROADMAP.md)** - Planned features
- **[Contributing](CONTRIBUTING.md)** - Development guide
- **[Security](SECURITY.md)** - Security policy
- **[Changelog](CHANGELOG.md)** - Version history

## 🎯 Common Use Cases

### Daily Operations
```bash
# Morning health check
remotex exec-all "uptime && free -h" --parallel 10

# Check disk space across infrastructure
remotex exec-all "df -h /" --compact | grep "9[0-9]%"

# Export server inventory to CSV
remotex exec-all "hostname && cat /etc/os-release | grep PRETTY_NAME" --csv > inventory.csv

# Quick status check in shell script
if remotex exec-all 'systemctl is-active nginx' --quiet | grep -q '✗'; then
  echo "Alert: Some servers have nginx down!"
fi
```

### Deployments
```bash
# Deploy to web servers
remotex exec-multi "web01,web02,web03" \
  "cd /app && git pull && systemctl restart app" --parallel 3

# Verify deployment
remotex exec-multi "web01,web02,web03" "curl -s localhost/health"
```

### Troubleshooting
```bash
# Quick diagnostics
remotex memory prod01
remotex processes prod01
remotex logs prod01 nginx -n 100

# Check all servers for issues
remotex exec-all "systemctl is-failed --quiet || echo 'Services OK'"
```

## 🏗️ Project Structure

```
remotex/
├── __init__.py              # Package metadata  
├── cli.py                   # CLI entry point
├── config.py                # Configuration management
├── ssh_config.py            # SSH config operations
├── ssh_client.py            # Connection management
├── performance.py           # Caching & optimization
└── commands/                # Command modules
    ├── server_management.py # list, add, edit, remove, info
    ├── exec_command.py      # Remote execution
    ├── connect_command.py   # Interactive shell
    ├── bulk_operations.py   # exec-all, exec-multi
    ├── quick_commands.py    # Quick DevOps shortcuts
    └── config_command.py    # Configuration management
```

## 📚 Commands Reference

### Server Management
| Command | Description | Example |
|---------|-------------|---------|
| `list` | Show all configured servers | `remotex list -v` |
| `add` | Add a new server | `remotex add -a web01 -h 1.2.3.4 -u ubuntu` |
| `info` | Show server details | `remotex info myserver` |
| `edit` | Edit server configuration | `remotex edit myserver` |
| `remove` | Remove a server | `remotex remove myserver` |

### Execution
| Command | Description | Example |
|---------|-------------|----------|
| `exec` | Execute command on server | `remotex exec myserver "ls -la"` |
| `connect` | Open interactive shell | `remotex connect myserver` |
| `exec-all` | Execute on all servers | `remotex exec-all "uptime" --parallel 10` |
| `exec-multi` | Execute on specific servers | `remotex exec-multi "web01,web02" "df -h"` |
| `exec-group` | Execute on server group | `remotex exec-group web "systemctl restart nginx"` |

**Output Mode Flags** (available for all bulk commands):
- `--json` - Pure JSON output for parsing
- `--csv` - CSV format for spreadsheets
- `--quiet` / `-q` - Minimal scriptable output
- `--plain` - No ANSI colors/formatting
- `--compact` - Condensed single-line format
- `--show-output` - Display detailed command output

### Configuration
| Command | Description | Example |
|---------|-------------|---------|
| `config show` | Show configuration | `remotex config show` |
| `config set-default` | Set default server | `remotex config set-default web01` |
| `config validate` | Validate configuration | `remotex config validate` |
| `config export` | Export configuration | `remotex config export` |
| `config import` | Import configuration | `remotex config import backup.json` |

### Groups & Aliases
| Command | Description | Example |
|---------|-------------|---------|
| `group add` | Create server group | `remotex group add web web01 web02` |
| `alias add` | Create command alias | `remotex alias add restart-nginx "sudo systemctl restart nginx"` |


## 📝 SSH Config

RemoteX works with standard SSH config format:

```
Host myserver
    HostName 192.168.1.100
    User ubuntu
    Port 22
    IdentityFile ~/.ssh/id_rsa

Host production
    HostName prod.example.com
    User admin
    IdentityFile ~/.ssh/prod_key
```

RemoteX can create and manage this file for you!

## 🤝 Contributing

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Quick Start

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/remotex.git
cd remotex

# Set up development environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .

# Create a feature branch
git checkout -b feat/your-feature-name
# or
git checkout -b fix/bug-description

# Make your changes and commit using conventional commits
git commit -m "feat(commands): add new feature"
git commit -m "fix(ssh): resolve connection issue"
git commit -m "docs(readme): update installation guide"
```

### Commit Guidelines

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `perf:` Performance improvements
- `refactor:` Code refactoring
- `test:` Tests
- `ci:` CI/CD changes
- `chore:` Maintenance

**Example:** `feat(bulk): add connection pooling for 3x faster execution`

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines and examples.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) - Modern CLI framework
- Styled with [Rich](https://rich.readthedocs.io/) - Beautiful terminal formatting  
- SSH via [Paramiko](http://www.paramiko.org/) - Pure Python SSH implementation

## 📮 Support

- **Issues**: [GitHub Issues](https://github.com/sagar.memane/remotex/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sagar.memane/remotex/discussions)
- **Security**: See [SECURITY.md](SECURITY.md) for reporting vulnerabilities

## 🗺️ Roadmap

### ✅ Implemented
- [x] Server management (add, edit, remove, list)
- [x] Remote command execution
- [x] Interactive shell sessions
- [x] Bulk parallel operations
- [x] Quick DevOps shortcuts
- [x] Server grouping
- [x] Command aliases
- [x] File transfer (push/pull)
- [x] Configuration management
- [x] Audit logging
- [x] Dry-run mode
- [x] JSON output
- [x] **Command history and replay** ✨ NEW
- [x] **SSH tunnel management** ✨ NEW
- [x] **Jump host / bastion support** ✨ NEW
- [x] **Performance profiling tools** ✨ NEW
- [x] **Man page generation** ✨ NEW
- [x] **Test suite structure** ✨ NEW

### 🚧 Planned
- [ ] Custom command templates
- [ ] Real-time log streaming
- [ ] Output comparison across servers
- [ ] Cloud provider integration (AWS, Azure, GCP)
- [ ] Ansible playbook integration

See [Feature Roadmap](docs/FEATURE_ROADMAP.md) for detailed information.

## 🆘 Troubleshooting

### Command not found after installation
```bash
source venv/bin/activate  # Activate virtual environment
pip install -e .  # Reinstall if needed
which remotex  # Should show path in venv
```

### Connection issues
```bash
# Test SSH manually first
ssh -F ~/.ssh/config myserver

# Check server configuration
remotex info myserver
```

### Permission errors with SSH keys
```bash
chmod 600 ~/.ssh/id_rsa
chmod 700 ~/.ssh
```

### Slow bulk operations
```bash
# Increase parallelism (default is 5)
remotex exec-all "uptime" --parallel 10

# Reduce timeout for faster failure detection
remotex exec-all "ping -c 1 google.com" --timeout 5
```

---

<div align="center">

**[⬆ back to top](#-remotex)**

Made with ❤️ for DevOps Engineers

If you find RemoteX useful, please ⭐ star this repository!

</div>
