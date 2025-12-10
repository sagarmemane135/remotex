# Publishing OmniHost to PyPI

This guide walks you through publishing OmniHost to PyPI (Python Package Index).

## Prerequisites

1. **PyPI Account**: Create accounts on both:
   - [PyPI](https://pypi.org/account/register/) (production)
   - [TestPyPI](https://test.pypi.org/account/register/) (testing)

2. **Install Build Tools**:
```bash
pip install --upgrade pip build twine
```

## Step 1: Clean Previous Builds

```bash
rm -rf dist/ build/ *.egg-info
```

## Step 2: Build the Package

```bash
python -m build
```

This creates:
- `dist/omnihost-1.0.0.tar.gz` (source distribution)
- `dist/omnihost-1.0.0-py3-none-any.whl` (wheel distribution)

## Step 3: Test on TestPyPI (Recommended)

### Upload to TestPyPI:
```bash
python -m twine upload --repository testpypi dist/*
```

Enter your TestPyPI credentials when prompted.

### Test Installation:
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple omnihost
```

### Verify:
```bash
omnihost --version
omnihost --help
```

## Step 4: Upload to PyPI (Production)

### Upload:
```bash
python -m twine upload dist/*
```

Enter your PyPI credentials when prompted.

### Alternative - Using API Token (Recommended):

1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Generate API token
3. Create `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcC...your-token-here...
```

Then upload:
```bash
python -m twine upload dist/*
```

## Step 5: Verify Published Package

### Check on PyPI:
https://pypi.org/project/omnihost/

### Install and Test:
```bash
pip install omnihost
omnihost --version
```

## Step 6: Add PyPI Badge to README

Add to your README.md:

```markdown
[![PyPI version](https://badge.fury.io/py/omnihost.svg)](https://badge.fury.io/py/omnihost)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/omnihost)](https://pypi.org/project/omnihost/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/omnihost)](https://pypi.org/project/omnihost/)
```

## Updating the Package

When releasing a new version:

1. **Update Version** in `pyproject.toml`:
```toml
version = "1.0.1"
```

2. **Update CHANGELOG.md** - Move unreleased changes to new version section

3. **Commit and Tag**:
```bash
git add pyproject.toml CHANGELOG.md
git commit -m "chore: Bump version to 1.0.1"
git tag v1.0.1
git push origin main --tags
```

4. **Rebuild and Upload**:
```bash
rm -rf dist/
python -m build
python -m twine upload dist/*
```

## Automation with GitHub Actions (Optional)

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

Add your PyPI API token to GitHub Secrets as `PYPI_API_TOKEN`.

## Troubleshooting

### "File already exists" Error:
- You cannot re-upload the same version
- Increment version number in `pyproject.toml`

### Import Errors After Installation:
- Check `[project.scripts]` in `pyproject.toml`
- Verify entry point: `omnihost = "omnihost.cli:main"`

### Missing Dependencies:
- Ensure all dependencies are listed in `dependencies` array
- Test in a clean virtual environment

## Quick Command Reference

```bash
# Build
python -m build

# Check package
twine check dist/*

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*

# Install from PyPI
pip install omnihost

# Uninstall
pip uninstall omnihost
```

## Post-Publication Checklist

- [ ] Verify package on PyPI: https://pypi.org/project/omnihost/
- [ ] Test installation: `pip install omnihost`
- [ ] Update README with PyPI badges
- [ ] Create GitHub release with changelog
- [ ] Announce on social media/forums
- [ ] Update documentation with pip install instructions
- [ ] Monitor issue tracker for user feedback
