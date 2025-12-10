# PyPI Trusted Publishing Setup Guide

This guide walks you through setting up **Trusted Publishing** (OpenID Connect) for OmniHost on PyPI. This is the modern, secure method that eliminates the need for API tokens or passwords.

## What is Trusted Publishing?

Trusted Publishing uses OpenID Connect (OIDC) to allow GitHub Actions to publish directly to PyPI without storing credentials. It's more secure and easier to manage than API tokens.

## Prerequisites

1. A PyPI account: https://pypi.org/account/register/
2. Repository: https://github.com/sagarmemane135/omnihost
3. Admin access to the GitHub repository

## Step 1: Configure Pending Publisher on PyPI

Since the `omnihost` package doesn't exist on PyPI yet, you need to add a "pending publisher":

### Go to PyPI Pending Publishers Page:
👉 https://pypi.org/manage/account/publishing/

### Fill in the Form:

| Field | Value |
|-------|-------|
| **PyPI Project Name** | `omnihost` |
| **Owner** | `sagarmemane135` |
| **Repository name** | `omnihost` |
| **Workflow name** | `publish-to-pypi.yml` |
| **Environment name** | `pypi` |

### Click "Add" Button

✅ This creates a "pending publisher" that will:
- Allow the first publish to create the project
- Automatically convert to a regular trusted publisher after first use
- No one else can use this pending publisher (it's tied to your GitHub account)

## Step 2: Create GitHub Environments

### 2.1 Create PyPI Environment (Production)

1. Go to: https://github.com/sagarmemane135/omnihost/settings/environments
2. Click **"New environment"**
3. Name: `pypi`
4. **Environment protection rules** (recommended):
   - ✅ **Required reviewers**: Add yourself (prevents accidental publishes)
   - ✅ **Deployment branches**: Only `main` or tags matching `v*`
5. Click **"Configure environment"**

### 2.2 Create TestPyPI Environment (Testing)

1. Click **"New environment"** again
2. Name: `testpypi`
3. Protection rules (optional for testing):
   - Can leave less restricted
4. Click **"Configure environment"**

## Step 3: Set Up TestPyPI (Optional but Recommended)

To test the workflow before publishing to production PyPI:

### Go to TestPyPI Pending Publishers:
👉 https://test.pypi.org/manage/account/publishing/

### Fill in the Same Form:

| Field | Value |
|-------|-------|
| **PyPI Project Name** | `omnihost` |
| **Owner** | `sagarmemane135` |
| **Repository name** | `omnihost` |
| **Workflow name** | `publish-to-pypi.yml` |
| **Environment name** | `testpypi` |

### Click "Add"

## Step 4: Verify Workflow File

The workflow file `.github/workflows/publish-to-pypi.yml` has been created with:

✅ **Key Features:**
- Builds on every GitHub release
- Can be triggered manually
- Publishes to both PyPI and TestPyPI
- Uses trusted publishing (no tokens needed)
- Requires environment approval for safety

✅ **Critical Settings:**
```yaml
permissions:
  id-token: write  # Required for trusted publishing
environment:
  name: pypi  # Matches the environment you created
```

## Step 5: Test the Setup

### Option A: Test with Manual Trigger First

1. Go to: https://github.com/sagarmemane135/omnihost/actions
2. Click on **"Publish to PyPI"** workflow
3. Click **"Run workflow"**
4. Select branch: `main`
5. Click **"Run workflow"** button

This will:
- Build the package
- Wait for your approval (if you set up reviewers)
- Publish to TestPyPI first
- Publish to PyPI

### Option B: Test with GitHub Release

1. Go to: https://github.com/sagarmemane135/omnihost/releases
2. Click **"Draft a new release"**
3. Tag version: `v1.0.0`
4. Release title: `v1.0.0 - Initial Release`
5. Description: Copy from CHANGELOG.md
6. Click **"Publish release"**

This automatically triggers the workflow.

## Step 6: Monitor the Workflow

1. Go to: https://github.com/sagarmemane135/omnihost/actions
2. Click on the running workflow
3. Watch the build and publish steps
4. If you set up reviewers, approve the deployment

## Step 7: Verify Publication

### Check PyPI:
👉 https://pypi.org/project/omnihost/

### Test Installation:
```bash
pip install omnihost
omnihost --version
```

## Troubleshooting

### Error: "pending publisher already exists"
- You've already configured it, that's fine!
- Check: https://pypi.org/manage/account/publishing/

### Error: "workflow failed with 403"
- Verify environment name matches exactly: `pypi` (lowercase)
- Check that `id-token: write` permission is set
- Ensure pending publisher is configured on PyPI

### Error: "this filename has already been used"
- You cannot re-upload the same version
- Bump version in `pyproject.toml`
- Create a new release with the new version

### Workflow doesn't trigger
- Ensure workflow file is on `main` branch
- Check: https://github.com/sagarmemane135/omnihost/actions
- Verify workflow file is in `.github/workflows/` directory

## Future Releases

Once set up, publishing new versions is simple:

1. **Update version** in `pyproject.toml`:
   ```toml
   version = "1.0.1"
   ```

2. **Update CHANGELOG.md**

3. **Commit and push**:
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "chore: Bump version to 1.0.1"
   git push origin main
   ```

4. **Create GitHub release**:
   - Go to https://github.com/sagarmemane135/omnihost/releases/new
   - Tag: `v1.0.1`
   - Title: `v1.0.1 - [Brief description]`
   - Description: Copy from CHANGELOG
   - Click "Publish release"

5. **Workflow runs automatically** ✨

No tokens, no passwords, completely automated!

## Security Benefits

✅ **No credentials in GitHub Secrets**
✅ **No risk of token leakage**
✅ **Automatic token rotation**
✅ **Fine-grained control with environments**
✅ **Audit trail in GitHub Actions logs**
✅ **Approval workflow for production releases**

## Quick Reference

| Task | URL |
|------|-----|
| PyPI Pending Publishers | https://pypi.org/manage/account/publishing/ |
| TestPyPI Pending Publishers | https://test.pypi.org/manage/account/publishing/ |
| GitHub Environments | https://github.com/sagarmemane135/omnihost/settings/environments |
| GitHub Actions | https://github.com/sagarmemane135/omnihost/actions |
| GitHub Releases | https://github.com/sagarmemane135/omnihost/releases |
| Published Package | https://pypi.org/project/omnihost/ |

## Need Help?

- PyPI Trusted Publishing Docs: https://docs.pypi.org/trusted-publishers/
- GitHub Actions OIDC: https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect
- PyPI Support: https://pypi.org/help/
