# 📦 Packaging Guide

This document explains how RemoteX is packaged and what gets included in distributions.

## Package Contents

### Included Files

The package includes:

1. **Python Package** (`remotex/`)
   - All source code and modules
   - Command implementations
   - Core utilities

2. **Documentation** (`docs/`)
   - All markdown documentation files
   - Architecture, guides, references

3. **Man Pages** (`man/man1/`)
   - Generated man pages for the CLI
   - File: `remotex.1`

4. **Scripts** (`scripts/`)
   - `generate_man_pages.py` - Man page generator

5. **Test Suite** (`tests/`)
   - Unit tests and test runner

6. **Configuration Files**
   - `pyproject.toml` - Package metadata
   - `MANIFEST.in` - File inclusion rules
   - `requirements.txt` - Dependencies

## Building the Package

### 1. Generate Man Pages

Before building, generate man pages:

```bash
python scripts/generate_man_pages.py
```

This creates `man/man1/remotex.1`.

### 2. Build Distribution

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build source and wheel distributions
python -m build
```

This creates:
- `dist/remotex-1.0.0.tar.gz` (source distribution)
- `dist/remotex-1.0.0-py3-none-any.whl` (wheel)

### 3. Verify Package Contents

Check what's included:

```bash
# For source distribution
tar -tzf dist/remotex-*.tar.gz | grep -E "(man|scripts|docs)"

# For wheel
unzip -l dist/remotex-*.whl | grep -E "(man|scripts|docs)"
```

## Installation

### Standard Installation

```bash
pip install remotex
```

This installs:
- ✅ Python package to site-packages
- ✅ CLI command (`remotex`)
- ✅ All Python modules
- ❌ Man pages (not automatically installed)

### Installing Man Pages

Man pages are included in the package but require manual installation:

#### Option 1: Using the Install Script (Recommended)

```bash
# After pip install
python -m remotex.install_man_pages

# Or with sudo for system-wide installation
sudo python -m remotex.install_man_pages
```

#### Option 2: Manual Installation

```bash
# Find package location
python -c "import remotex; import os; print(os.path.dirname(remotex.__file__))"

# Copy man pages (adjust path as needed)
sudo cp -r /path/to/remotex/man/* /usr/share/man/
sudo mandb
```

#### Option 3: User-Specific Installation

```bash
# Install to user's local man directory
mkdir -p ~/.local/share/man/man1
cp man/man1/remotex.1 ~/.local/share/man/man1/
```

Then add to `~/.bashrc` or `~/.zshrc`:
```bash
export MANPATH="$HOME/.local/share/man:$MANPATH"
```

## Verification

After installation, verify:

```bash
# Check CLI works
remotex --version

# Check man page (if installed)
man remotex

# Check package location
python -c "import remotex; print(remotex.__file__)"
```

## MANIFEST.in

The `MANIFEST.in` file controls what gets included in source distributions:

```
include README.md LICENSE CHANGELOG.md ...
recursive-include docs *.md
recursive-include man *.1          # Man pages
recursive-include scripts *.py     # Scripts
recursive-include .github *.md *.yml
```

## pyproject.toml Configuration

Key packaging settings:

```toml
[project]
name = "remotex688"
version = "1.0.0"
# ... metadata ...

[project.scripts]
remotex = "remotex.cli:main"

[tool.setuptools.package-data]
remotex = ["../man/**/*.1"]
```

## Troubleshooting

### Man Pages Not Found

**Problem:** `man remotex` returns "No manual entry"

**Solutions:**
1. Run the install script: `python -m remotex.install_man_pages`
2. Check man page location: `find /usr -name "remotex.1" 2>/dev/null`
3. Regenerate man pages: `python scripts/generate_man_pages.py`

### Package Missing Files

**Problem:** Files not included in distribution

**Solutions:**
1. Check `MANIFEST.in` includes the files
2. Regenerate with: `python -m build --sdist`
3. Verify with: `tar -tzf dist/*.tar.gz | grep filename`

### Installation Issues

**Problem:** Package installs but command not found

**Solutions:**
1. Check Python path: `python -m site`
2. Verify entry point: `pip show remotex`
3. Reinstall: `pip install --force-reinstall remotex`

## Best Practices

1. **Always generate man pages before building**
   ```bash
   python scripts/generate_man_pages.py
   python -m build
   ```

2. **Test installation in clean environment**
   ```bash
   python -m venv test_env
   source test_env/bin/activate
   pip install dist/remotex-*.whl
   remotex --version
   ```

3. **Include man pages in release notes**
   - Mention that users need to run install script
   - Provide installation instructions

4. **Verify package contents before publishing**
   ```bash
   python -m build
   tar -tzf dist/*.tar.gz | head -20
   ```

## Future Improvements

Potential enhancements:

- [ ] Automatic man page installation via setuptools hooks
- [ ] Support for multiple man page sections
- [ ] Integration with package managers (apt, yum, etc.)
- [ ] Post-install script in wheel metadata

