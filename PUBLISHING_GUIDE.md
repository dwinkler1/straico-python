# Quick Start Guide for PyPI Publishing

## Step-by-Step Instructions

### 1. Navigate to Package Directory

```bash
cd /Users/daniel/_work_system/10_19_development/17_testing/17.05_straico_api/straico-python
```

### 2. Install Build Tools

```bash
pip install build twine
```

### 3. Build the Package

```bash
python -m build
```

This creates two files in the `dist/` directory:
- `straico-1.0.0-py3-none-any.whl` (wheel)
- `straico-1.0.0.tar.gz` (source distribution)

### 4. Verify the Build

```bash
twine check dist/*
```

Should output: `Checking dist/straico-1.0.0-py3-none-any.whl: PASSED`

### 5. Test Installation Locally

```bash
# Install in development mode
pip install -e .

# Test the CLI
export STRAICO_API_KEY="your-api-key"
straico "Hello, world!"

# Test Python import
python -c "from straico import StraicoClient; print('Import successful!')"
```

### 6. Publish to Test PyPI (Optional but Recommended)

```bash
# Create account at https://test.pypi.org if you don't have one

# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ --no-deps straico
```

### 7. Publish to Production PyPI

```bash
# Create account at https://pypi.org if you don't have one
# Generate API token at https://pypi.org/manage/account/token/

# Upload to PyPI
twine upload dist/*

# Enter your credentials:
# Username: __token__
# Password: pypi-your-api-token-here
```

### 8. Verify Installation

```bash
# Uninstall local version
pip uninstall straico

# Install from PyPI
pip install straico

# Test it works
straico --help
```

## PyPI Credentials Setup

Create or edit `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-production-api-token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token
```

## Common Issues and Solutions

### Issue: "File already exists"

```bash
# Clean old builds
rm -rf dist/ build/ *.egg-info

# Rebuild
python -m build
```

### Issue: Import errors after installation

```bash
# Reinstall in development mode
pip install -e .

# Or reinstall from PyPI
pip install --force-reinstall straico
```

### Issue: Command not found after install

```bash
# Check if installed correctly
pip show straico

# Check if scripts directory is in PATH
which straico

# May need to add to PATH:
export PATH="$HOME/.local/bin:$PATH"
```

## Version Updates

When releasing a new version:

1. Update version in `pyproject.toml`:
   ```toml
   version = "1.0.1"
   ```

2. Update version in `straico/__init__.py`:
   ```python
   __version__ = "1.0.1"
   ```

3. Clean old builds:
   ```bash
   rm -rf dist/ build/ *.egg-info
   ```

4. Rebuild and upload:
   ```bash
   python -m build
   twine upload dist/*
   ```

## Testing Checklist

Before publishing, verify:

- [ ] Package builds without errors
- [ ] `twine check dist/*` passes
- [ ] Local installation works (`pip install -e .`)
- [ ] CLI command works (`straico --help`)
- [ ] Python import works (`from straico import StraicoClient`)
- [ ] Tests pass (`pytest`)
- [ ] README is complete and accurate
- [ ] Version numbers are correct
- [ ] LICENSE is included
- [ ] Test PyPI upload successful (optional)

## Package Info

- **Package Name**: `straico`
- **CLI Command**: `straico`
- **Import**: `from straico import StraicoClient`
- **PyPI URL**: https://pypi.org/project/straico/
- **Test PyPI URL**: https://test.pypi.org/project/straico/

## Support

If you encounter issues:

1. Check build output for errors
2. Verify all files are present
3. Ensure dependencies are installed
4. Check Python version (>= 3.8)
5. Review PyPI documentation: https://packaging.python.org/
