# Straico Python Package

This directory contains a PyPI-ready Python package for the Straico API client and CLI.

## Package Structure

```
straico-python/
├── straico/              # Main package directory
│   ├── __init__.py      # Package initialization
│   ├── client.py        # API client implementation
│   ├── cli.py           # Command-line interface
│   └── py.typed         # PEP 561 type stub marker
├── tests/               # Test directory
│   └── __init__.py
├── pyproject.toml       # Package configuration (PEP 517/518)
├── README.md            # Package documentation
├── LICENSE              # MIT License
├── .gitignore           # Git ignore file
└── MANIFEST.in          # Include additional files in distribution
```

## Building the Package

### Prerequisites

```bash
pip install build twine
```

### Build Distribution

```bash
# From the straico-python directory
python -m build
```

This creates:
- `dist/straico-1.0.0-py3-none-any.whl` (wheel distribution)
- `dist/straico-1.0.0.tar.gz` (source distribution)

### Verify Build

```bash
twine check dist/*
```

## Testing Locally

### Install in Development Mode

```bash
pip install -e .
```

### Test the CLI

```bash
export STRAICO_API_KEY="your-api-key"
straico "Test prompt"
```

### Test the Python API

```python
from straico import StraicoClient

client = StraicoClient(api_key="your-api-key")
response = client.chat("Test prompt")
print(response)
```

## Publishing to PyPI

### Test PyPI (Recommended First)

```bash
# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Install from Test PyPI to verify
pip install --index-url https://test.pypi.org/simple/ straico
```

### Production PyPI

```bash
# Upload to PyPI
twine upload dist/*
```

You'll need PyPI credentials. Set them up with:

```bash
# Create ~/.pypirc
[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
username = __token__
password = pypi-your-test-api-token-here
```

## Installation from PyPI

Once published, users can install with:

```bash
pip install straico
```

## Development

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
```

### Code Formatting

```bash
black straico tests
```

### Linting

```bash
flake8 straico tests
```

### Type Checking

```bash
mypy straico
```

## Version Management

Update version in:
- `pyproject.toml` - `version = "x.y.z"`
- `straico/__init__.py` - `__version__ = "x.y.z"`

## Package Metadata

- **Name**: straico
- **Version**: 1.0.0
- **License**: MIT
- **Python**: >=3.8
- **Homepage**: https://github.com/dwinkler1/straico-python
- **Documentation**: https://github.com/dwinkler1/straico-python

## Support

For issues or questions:
- GitHub Issues: https://github.com/dwinkler1/straico-python/issues
- Email: dw@dwinkler.org
