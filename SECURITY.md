# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of RemoteX seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please DO NOT:
- Open a public GitHub issue
- Discuss the vulnerability in public forums or social media
- Exploit the vulnerability beyond what is necessary to demonstrate it

### Please DO:
1. **Email** the maintainers directly at: [sagar.memane@treadbinary.com]
2. **Include** the following information:
   - Type of vulnerability
   - Full paths of source file(s) related to the vulnerability
   - Location of the affected source code (tag/branch/commit or URL)
   - Step-by-step instructions to reproduce the issue
   - Proof-of-concept or exploit code (if possible)
   - Impact of the vulnerability and how an attacker might exploit it

### What to Expect:
- **Within 48 hours**: Acknowledgment of your report
- **Within 7 days**: Initial assessment and severity classification
- **Within 30 days**: Fix development and testing
- **Coordinated disclosure**: We'll work with you on a responsible disclosure timeline

## Security Best Practices for Users

### SSH Key Management
```bash
# Use strong SSH keys
ssh-keygen -t ed25519 -a 100

# Set proper permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub

# Never commit private keys
# RemoteX's .gitignore already excludes common key files
```

### Configuration Security
```bash
# RemoteX config is stored at ~/.remotex/config.json
# Ensure proper permissions:
chmod 700 ~/.remotex
chmod 600 ~/.remotex/config.json

# Review your SSH config regularly
cat ~/.ssh/config
```

### Connection Security
- **Always use SSH keys** instead of passwords
- **Use strong passphrases** for SSH keys
- **Rotate keys regularly** (every 6-12 months)
- **Use different keys** for different environments (dev/staging/prod)
- **Enable SSH agent forwarding** only when necessary
- **Review authorized_keys** on remote servers regularly

### Command Execution Safety
```bash
# Avoid running untrusted commands
remotex exec server "$(cat untrusted_input.txt)"  # DON'T DO THIS

# Validate commands before bulk execution
remotex exec-all "dangerous_command"  # Review carefully

# Use timeout to prevent hanging
remotex exec server "long_command" --timeout 300
```

### Network Security
- **Use VPN** when connecting to servers over public networks
- **Enable firewall** rules to restrict SSH access
- **Use fail2ban** on servers to prevent brute force
- **Monitor SSH logs** for suspicious activity
- **Use bastion/jump hosts** for production environments

## Known Security Considerations

### 1. SSH Config Storage
- RemoteX reads and writes to `~/.ssh/config`
- File permissions must be `600` or stricter
- Config file is plain text (no encryption)
- **Mitigation**: Never store passwords in config; use keys only

### 2. Configuration Storage
- Default server and preferences stored at `~/.remotex/config.json`
- File contains server aliases (no passwords or keys)
- **Mitigation**: File permissions set to `600` automatically

### 3. Command Execution
- Commands are executed as the authenticated SSH user
- No privilege escalation is performed by RemoteX
- **Mitigation**: Review commands before bulk execution

### 4. Connection Pooling
- Future versions may cache SSH connections
- Connections should time out appropriately
- **Mitigation**: Implement connection timeout and cleanup

### 5. Dependencies
- RemoteX depends on Paramiko, Typer, and Rich
- Vulnerabilities in dependencies could affect RemoteX
- **Mitigation**: Keep dependencies updated

## Security Updates

Security updates will be released as patch versions (e.g., 1.0.1, 1.0.2).

### How to Stay Informed:
1. **Watch this repository** on GitHub
2. **Subscribe to security advisories** on GitHub Security tab
3. **Check CHANGELOG.md** regularly
4. **Enable Dependabot alerts** (if you forked the repo)

### Updating RemoteX:
```bash
cd remotex
git pull origin main
pip install --upgrade -e .
```

## Security Checklist for Contributors

When contributing code, ensure:

- [ ] No hardcoded credentials or API keys
- [ ] Proper input validation and sanitization
- [ ] No command injection vulnerabilities
- [ ] Proper error handling (don't expose sensitive info)
- [ ] Dependencies are up-to-date and without known CVEs
- [ ] File permissions are set correctly
- [ ] Sensitive data is not logged
- [ ] SSH connections are properly closed
- [ ] Timeouts are implemented for network operations
- [ ] Code follows principle of least privilege

## Vulnerability Disclosure Timeline

We follow responsible disclosure practices:

1. **Day 0**: Vulnerability reported
2. **Day 2**: Report acknowledged, investigation begins
3. **Day 7**: Severity assessment complete, fix development starts
4. **Day 30**: Fix tested and ready for release
5. **Day 30+**: Security advisory published, fix released
6. **Day 37**: Public disclosure (7 days after release)

This timeline may be adjusted based on severity and complexity.

## Security Hall of Fame

We thank the following researchers for responsibly disclosing vulnerabilities:

_No vulnerabilities reported yet_

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [SSH Best Practices](https://www.ssh.com/academy/ssh/keygen)
- [Secure Coding Guidelines](https://www.securecoding.cert.org/)
- [Python Security](https://python.readthedocs.io/en/latest/library/security_warnings.html)

## Contact

For security concerns, please email: [sagar.memane@treadbinary.com]

For general questions, use [GitHub Issues](https://github.com/sagar.memane/remotex/issues).

---

**Last Updated**: December 10, 2025
