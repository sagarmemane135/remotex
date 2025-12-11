# Contributing to RemoteX

First off, thank you for considering contributing to RemoteX! It's people like you that make RemoteX such a great tool for DevOps engineers.

## 🌟 Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## 🤔 How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps to reproduce the problem**
* **Provide specific examples**
* **Describe the behavior you observed after following the steps**
* **Explain which behavior you expected to see instead and why**
* **Include screenshots if relevant**
* **Include your environment details**: OS, Python version, RemoteX version

**Example bug report:**
```markdown
## Bug: exec-all fails with timeout error

**Environment:**
- OS: Ubuntu 22.04
- Python: 3.11.5
- RemoteX: 1.0.0

**Steps to reproduce:**
1. Configure 10 servers
2. Run `remotex exec-all "uptime"`
3. Observe timeout errors

**Expected:** All servers respond successfully
**Actual:** 5 servers timeout after 30 seconds

**Additional context:** Servers are in different regions with varying latency
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the steps**
* **Describe the current behavior and explain which behavior you expected to see instead**
* **Explain why this enhancement would be useful**

### Pull Requests

* Fill in the required template
* Follow the Python style guide (PEP 8)
* Include appropriate test cases
* Update documentation as needed
* End all files with a newline

## 🚀 Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/sagar.memane/remotex.git
cd remotex
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install in Development Mode

```bash
pip install -e .
```

### 4. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## 📝 Development Guidelines

### Code Style

We follow PEP 8 with some specific preferences:

```python
# ✅ Good
def execute_command(host: str, command: str, timeout: int = 30) -> dict:
    """
    Execute a command on a remote host.
    
    Args:
        host: The hostname or alias
        command: The command to execute
        timeout: Command timeout in seconds
        
    Returns:
        dict: Result containing stdout, stderr, and exit code
    """
    pass

# ❌ Bad
def exec_cmd(h,c,t=30):
    pass
```

### Project Structure

```
remotex/
├── __init__.py           # Package metadata
├── cli.py                # CLI entry point
├── config.py             # Configuration management
├── ssh_config.py         # SSH config operations
├── ssh_client.py         # Connection management
├── performance.py        # Caching & optimization
├── utils.py              # Shared utilities
└── commands/             # Command modules
    ├── server_management.py
    ├── exec_command.py
    ├── connect_command.py
    ├── bulk_operations.py
    └── quick_commands.py
```

### Adding New Commands

1. **Create command file** in `remotex/commands/`:

```python
# remotex/commands/my_command.py
import typer
from rich.console import Console

console = Console()

def register_my_command(app: typer.Typer):
    @app.command(name="mycommand")
    def my_command(
        host: str = typer.Argument(..., help="Server hostname"),
        option: bool = typer.Option(False, "--opt", help="Some option")
    ):
        """
        Description of what your command does.
        """
        console.print(f"[green]Running my command on {host}[/green]")
        # Your implementation here
```

2. **Register in cli.py**:

```python
from remotex.commands.my_command import register_my_command

def main():
    app = typer.Typer(...)
    # ... other registrations
    register_my_command(app)
    app()
```

3. **Reinstall package**:

```bash
pip install -e .
```

### Coding Conventions

#### Use Type Hints
```python
# ✅ Good
def connect(host: str, port: int = 22) -> paramiko.SSHClient:
    pass

# ❌ Bad
def connect(host, port=22):
    pass
```

#### Use Rich for Output
```python
from rich.console import Console
from rich.panel import Panel

console = Console()

# ✅ Good
console.print(Panel("Success!", style="green"))

# ❌ Bad
print("Success!")
```

#### Handle Errors Gracefully
```python
# ✅ Good
try:
    client = create_ssh_client(host)
except ConnectionError as e:
    console.print(Panel(
        f"[red]Connection failed: {e}[/red]",
        title="❌ Error"
    ))
    raise typer.Exit(1)

# ❌ Bad
client = create_ssh_client(host)  # Let it crash
```

#### Use Descriptive Variable Names
```python
# ✅ Good
connection_timeout = 30
ssh_client = create_ssh_client(host_config)

# ❌ Bad
t = 30
c = create_ssh_client(h)
```

### Testing

We use pytest for testing. Add tests for new features:

```python
# tests/test_my_command.py
import pytest
from remotex.commands.my_command import my_command

def test_my_command_success():
    result = my_command("testhost")
    assert result.exit_code == 0

def test_my_command_invalid_host():
    with pytest.raises(ValueError):
        my_command("invalid-host")
```

Run tests:
```bash
pytest
pytest tests/test_my_command.py  # Specific test
pytest -v  # Verbose output
```

### Documentation

Update documentation when adding features:

1. **Docstrings** - All functions need docstrings
2. **QUICK_REFERENCE.md** - Add command examples
3. **PERFORMANCE.md** - If it affects performance
4. **README.md** - If it's a major feature

## 🔄 Pull Request Process

### 1. Update Your Fork

```bash
git remote add upstream https://github.com/sagar.memane/remotex.git
git fetch upstream
git checkout main
git merge upstream/main
```

### 2. Make Your Changes

```bash
git checkout -b feature/amazing-feature
# Make your changes
git add .
git commit -m "Add: Amazing feature that does X"
```

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification strictly:

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type (Required)

Must be one of:

- **feat**: New feature for the user
  ```
  feat(commands): add bulk SSH key deployment command
  ```

- **fix**: Bug fix for the user
  ```
  fix(ssh): resolve connection timeout issues with Python 3.8
  ```

- **docs**: Documentation changes only
  ```
  docs(readme): update installation instructions
  ```

- **style**: Code style changes (formatting, no functional changes)
  ```
  style(cli): format code with black
  ```

- **refactor**: Code refactoring (no feature change or bug fix)
  ```
  refactor(config): simplify configuration loading logic
  ```

- **perf**: Performance improvements
  ```
  perf(bulk): optimize parallel execution with connection pooling
  ```

- **test**: Adding or updating tests
  ```
  test(ssh): add unit tests for connection retry logic
  ```

- **build**: Build system or dependency changes
  ```
  build(deps): upgrade paramiko to v3.4.0
  ```

- **ci**: CI/CD configuration changes
  ```
  ci(actions): add Python 3.12 to test matrix
  ```

- **chore**: Other changes (maintenance, tooling)
  ```
  chore(release): bump version to 1.0.2
  ```

- **revert**: Revert a previous commit
  ```
  revert: feat(auth): remove OAuth support
  ```

#### Scope (Optional but Recommended)

The scope specifies which part of the codebase is affected:
- `commands` - Command implementations
- `ssh` - SSH connection handling
- `config` - Configuration management
- `cli` - CLI interface
- `audit` - Audit logging
- `bulk` - Bulk operations
- `ci` - CI/CD pipelines
- `docs` - Documentation

#### Subject (Required)

- Use imperative, present tense: "add" not "added" or "adds"
- Don't capitalize first letter
- No period (.) at the end
- Keep it under 50 characters

#### Body (Optional)

- Explain **what** and **why** (not how)
- Wrap at 72 characters
- Separate from subject with a blank line

#### Footer (Optional)

Reference issues and breaking changes:

```
Fixes #123
Closes #456

BREAKING CHANGE: Configuration format changed from YAML to JSON
```

#### Full Examples

**Simple feature:**
```bash
git commit -m "feat(commands): add quick-ssh command for rapid connections"
```

**Bug fix with description:**
```bash
git commit -m "fix(ssh): handle connection timeout gracefully

Previously, connection timeouts would crash the application.
Now they're caught and reported with a clear message.

Fixes #234"
```

**Breaking change:**
```bash
git commit -m "feat(config)!: migrate configuration to JSON format

Replace YAML with JSON for better compatibility.

BREAKING CHANGE: Config files must be migrated from
.remotex/config.yaml to .remotex/config.json"
```

**Performance improvement:**
```bash
git commit -m "perf(bulk): implement connection pooling

Reuse SSH connections for multiple commands to reduce overhead.
Improves exec-all performance by 3x for 100+ servers."
```

**Multiple types of changes** (create separate commits):
```bash
git commit -m "feat(audit): add audit log export command"
git commit -m "docs(audit): update audit documentation"
git commit -m "test(audit): add audit export tests"
```

### 3. Push and Create PR

```bash
git push origin feature/amazing-feature
```

Then create a Pull Request on GitHub with:
- **Clear title** describing the change
- **Description** explaining what and why
- **Link to related issues** (Fixes #123)
- **Screenshots** if UI/output changed
- **Testing** description of how you tested

### 4. Code Review

* Address review comments
* Keep discussions focused and professional
* Update your PR based on feedback

```bash
# Make changes based on feedback
git add .
git commit -m "fix: Address review comments"
git push origin feature/amazing-feature
```

## 🎯 Good First Issues

Look for issues labeled `good first issue` or `help wanted`. These are great starting points for new contributors.

## 💬 Questions?

* Open an issue with the `question` label
* Join our discussions
* Check existing documentation

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- README.md contributors section
- CHANGELOG.md for their contributions
- GitHub contributors page

Thank you for contributing to RemoteX! 🚀
