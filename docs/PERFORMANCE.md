# ⚡ Performance Guide

Performance optimization tips and DevOps patterns for RemoteX.

## 🚀 Quick Commands (Single Server)

Execute common operations without typing full commands:

```bash
# System checks (faster than typing full exec commands)
remotex uptime tf-demo-vm        # Quick uptime
remotex disk tf-demo-vm          # Disk usage (df -h)
remotex memory tf-demo-vm        # Memory usage (free -h)
remotex cpu tf-demo-vm           # CPU info
remotex processes tf-demo-vm     # Top processes

# Service management
remotex status tf-demo-vm nginx      # Service status
remotex restart tf-demo-vm nginx     # Restart service
remotex logs tf-demo-vm nginx -n 100 # View logs

# Custom log file
remotex logs tf-demo-vm /var/log/syslog -n 50
```

## 🔥 Bulk Operations (Multiple Servers in Parallel)

Execute commands on multiple servers simultaneously:

### Execute on ALL servers
```bash
# Run on all configured servers
remotex exec-all "uptime"

# With custom parallelism (default: 5)
remotex exec-all "df -h" --parallel 10

# With timeout control
remotex exec-all "systemctl status nginx" --timeout 10

# Hide individual outputs, show summary only
remotex exec-all "apt update" --no-output
```

### Execute on specific servers
```bash
# Run on selected servers
remotex exec-multi "web01,web02,web03" "systemctl restart nginx"

# Database servers
remotex exec-multi "db01,db02" "pg_isready"

# With parallel control
remotex exec-multi "app01,app02,app03,app04" "git pull" --parallel 4
```

## ⚡ Performance Comparison

### Before (Sequential)
```bash
# Old way - runs one at a time (~60 seconds for 20 servers)
for server in web01 web02 ... web20; do
    remotex exec $server "uptime"
done
```

### After (Parallel)
```bash
# New way - runs in parallel (~6 seconds for 20 servers with --parallel 5)
remotex exec-all "uptime"

# Even faster with more parallelism (~3 seconds)
remotex exec-all "uptime" --parallel 10
```

## 📊 Real-World Examples

### DevOps Workflows

#### 1. Check all servers are up
```bash
remotex exec-all "uptime" --parallel 20
```

#### 2. Deploy application to web servers
```bash
remotex exec-multi "web01,web02,web03" "cd /app && git pull && systemctl restart app" --parallel 3
```

#### 3. Check disk space across infrastructure
```bash
remotex exec-all "df -h /" --parallel 10
```

#### 4. Verify service status across cluster
```bash
remotex exec-multi "app01,app02,app03" "systemctl is-active nginx"
```

#### 5. Quick health check
```bash
remotex exec-all "uptime && free -h | grep Mem" --parallel 15
```

#### 6. Restart services across load balancer pool
```bash
remotex exec-multi "lb01,lb02" "systemctl reload haproxy"
```

#### 7. Collect logs from multiple servers
```bash
remotex exec-all "journalctl -u app -n 10 --no-pager" --show-output
```

### Quick Diagnostics

```bash
# Memory across all servers
remotex exec-all "free -h" --parallel 10

# Disk usage on production servers
remotex exec-multi "prod01,prod02,prod03" "df -h"

# Check specific service
remotex exec-all "systemctl is-active docker" --parallel 20

# Find process
remotex exec-all "ps aux | grep python" --no-output
```

## 🎯 Performance Tips

### 1. Use appropriate parallelism
```bash
# Low parallelism for heavy operations
remotex exec-all "apt upgrade -y" --parallel 2

# High parallelism for quick checks
remotex exec-all "uptime" --parallel 20

# Default is 5 - good for most cases
remotex exec-all "systemctl status nginx"
```

### 2. Use quick commands for common tasks
```bash
# Instead of:
remotex exec server01 "df -h"

# Use:
remotex disk server01
```

### 3. Combine with Unix tools
```bash
# Check which servers have high disk usage
remotex exec-all "df -h /" --no-output | grep "9[0-9]%"

# Count running processes
remotex exec-all "ps aux | wc -l"
```

### 4. Use timeout for slow commands
```bash
# Don't wait forever
remotex exec-all "wget example.com" --timeout 5
```

## 📈 Performance Metrics

| Operation | Old Method | New Method | Speedup |
|-----------|------------|------------|---------|
| 10 servers uptime | 30s | 6s | 5x faster |
| 20 servers disk check | 60s | 12s | 5x faster |
| 50 servers status | 150s | 30s | 5x faster |

*With `--parallel 5` (default setting)*

## 🔧 Advanced Usage

### Error Handling
```bash
# Continue on errors (default)
remotex exec-all "systemctl restart app" --continue

# Stop on first error
remotex exec-all "systemctl restart app" --stop
```

### Output Control
```bash
# Show all outputs (default)
remotex exec-all "uptime" --show-output

# Summary only
remotex exec-all "apt update" --no-output
```

### Timeout Management
```bash
# Quick timeout for fast checks
remotex exec-all "ping -c 1 google.com" --timeout 5

# Longer timeout for updates
remotex exec-all "apt upgrade -y" --timeout 300
```

## 🎨 Example Output

### Bulk Execution with Progress
```
╭───────────────────────────────────────────────────────────╮
│                    🚀 Bulk Execution                      │
│ Command: uptime                                           │
│ Targets: 10 servers                                       │
│ Parallel: 5 connections                                   │
│ Timeout: 30s                                              │
╰───────────────────────────────────────────────────────────╯

⠋ Executing on 10 servers... ━━━━━━━━━━━━━━ 70% 7/10

          Execution Summary          
╭──────────┬───────────┬───────────┬──────╮
│ Server   │ Status    │ Exit Code │ ...  │
├──────────┼───────────┼───────────┼──────┤
│ web01    │ ✓ Success │     0     │ ...  │
│ web02    │ ✓ Success │     0     │ ...  │
│ web03    │ ✗ Failed  │     1     │ ...  │
╰──────────┴───────────┴───────────┴──────╯

Total: 10 | Success: 9 | Failed: 1
```

## 🚀 Common DevOps Patterns

### Rolling Restart
```bash
# Restart services one at a time
remotex exec-multi "web01,web02,web03" "systemctl restart nginx" --parallel 1
```

### Health Check All Servers
```bash
remotex exec-all "curl -sf localhost:8080/health || echo UNHEALTHY"
```

### Update All Servers
```bash
remotex exec-all "sudo apt update && sudo apt upgrade -y" --parallel 3 --timeout 300
```

### Gather Metrics
```bash
remotex exec-all "uptime && free -h && df -h /" --show-output > metrics.txt
```

### Quick Incident Response
```bash
# Check all servers for suspicious activity
remotex exec-all "last -n 20" --parallel 10

# Check for specific process
remotex exec-all "ps aux | grep suspicious_process"
```

## 💡 Pro Tips

1. **Start with low parallelism** for operations that might impact server performance
2. **Use `--no-output`** for large-scale checks where you only care about failures
3. **Combine with shell scripts** for complex workflows
4. **Set appropriate timeouts** based on expected command duration
5. **Use quick commands** for daily operations - they're faster to type

