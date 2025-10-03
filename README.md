# Straico API Python Client

[![PyPI version](https://badge.fury.io/py/straico-api.svg)](https://badge.fury.io/py/straico-api)
[![Python Versions](https://img.shields.io/pypi/pyversions/straico-api.svg)](https://pypi.org/project/straico-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Unofficial Python client and CLI for the Straico API. Straico provides a unified interface to interact with multiple Large Language Models (LLMs) including GPT-4, Claude, Gemini, and more.

## Features

- 🤖 **Smart LLM Selection**: Automatically selects the best model for your prompt using Straico's intelligent selector
- 💰 **Flexible Pricing**: Choose between quality, balance, or budget pricing strategies
- 🔄 **Multi-Model Support**: Query multiple models simultaneously (v1 API)
- 📊 **Model Management**: List and discover available models
- 🎯 **Direct Model Control**: Specify exact models when needed
- 🔐 **Secure Authentication**: Environment variable or direct API key support
- ✨ **Citation Support**: Automatic formatting of annotations and sources
- 🎨 **Interactive Mode**: Continuous conversation sessions
- ⚡ **Async Support**: Non-blocking API calls with loading animations

## Installation

```bash
pip install straico-api
```

### Development Installation

```bash
git clone https://github.com/dwinkler1/straico-python.git
cd straico-python
pip install -e ".[dev]"
```

## Quick Start

### Python API

```python
from straico_api import StraicoClient

# Initialize client
client = StraicoClient(api_key="your-api-key")

# Simple query with smart LLM selector
response = client.chat("What is the capital of France?")
print(response['data']['completion']['choices'][0]['message']['content'])

# Query with specific pricing strategy
response = client.chat(
    "Explain quantum computing",
    pricing_method="quality"
)

# Query specific model
response = client.chat(
    "Tell me a joke",
    model="openai/gpt-4o"
)

# Query multiple models simultaneously (v1 API)
response = client.chat(
    "Compare perspectives on AI",
    models=["openai/gpt-4o-mini", "anthropic/claude-3-5-haiku-20241022"]
)

# Smart selector with multiple models
response = client.chat(
    "Analyze this topic from different angles",
    pricing_method="balance",
    quantity=3  # Let Straico pick 3 best models
)

# List available models
models = client.get_models()
for model in models['data']['chat']:
    print(f"{model['name']}: {model['model']}")
```

### Command Line Interface

```bash
# Set your API key
export STRAICO_API_KEY="your-api-key"

# Simple query
straico-api "What is the capital of France?"

# Use specific pricing strategy
straico-api --pricing quality "Explain quantum computing"
straico-api --pricing budget "What is 2+2?"
straico-api --pricing balance "Write a short story"

# Query specific model
straico-api --model "openai/gpt-4o" "Tell me a joke"

# Query multiple models
straico-api --models "openai/gpt-4o-mini" "anthropic/claude-3-5-haiku-20241022" "Compare AI approaches"

# Smart selector with quantity
straico-api --pricing balance --quantity 2 "Give me different perspectives"

# Interactive mode
straico-api --interactive --pricing balance

# List available models
straico-api --list-models

# Verbose output
straico-api --verbose "Your prompt here"
```

## API Reference

### StraicoClient

#### Constructor

```python
StraicoClient(api_key: str, api_version: str = "v1")
```

- `api_key`: Your Straico API key
- `api_version`: API version to use ("v0" or "v1", default: "v1")

#### Methods

##### `chat()`

Send a chat message to Straico API.

```python
chat(
    message: str,
    pricing_method: str = "balance",
    model: Optional[str] = None,
    models: Optional[List[str]] = None,
    quantity: Optional[int] = None,
    show_animation: bool = True
) -> Dict
```

**Parameters:**
- `message`: The prompt/question to send
- `pricing_method`: Pricing strategy - "quality", "balance", or "budget" (default: "balance")
- `model`: Specific model to use (overrides smart selector)
- `models`: List of models to query simultaneously (v1 only)
- `quantity`: Number of models to select with smart selector (1-4, v1 only)
- `show_animation`: Show loading animation (default: True)

**Returns:** API response dictionary

##### `get_models()`

Fetch available models from Straico.

```python
get_models() -> Dict
```

**Returns:** Dictionary containing all available models

##### `find_similar_models()`

Find models with similar names (useful for typo correction).

```python
find_similar_models(model_name: str, max_suggestions: int = 5) -> List[Dict]
```

**Parameters:**
- `model_name`: Model name to find matches for
- `max_suggestions`: Maximum number of suggestions (default: 5)

**Returns:** List of similar models with details

## CLI Reference

### Basic Usage

```bash
straico-api [OPTIONS] PROMPT
```

### Options

- `-p, --pricing {quality,balance,budget}`: Pricing method (default: balance)
- `-m, --model MODEL`: Specific model to use
- `--models MODEL [MODEL ...]`: Multiple models to query simultaneously
- `-q, --quantity N`: Number of models (1-4) for smart selector
- `-i, --interactive`: Run in interactive mode
- `-l, --list-models`: List available models and exit
- `--api-key KEY`: API key (or use STRAICO_API_KEY env var)
- `-v, --verbose`: Show verbose output
- `-h, --help`: Show help message

### Examples

#### Different Pricing Strategies

```bash
# Quality - best results, higher cost
straico-api --pricing quality "Write a detailed analysis of climate change"

# Balance - good quality, moderate cost (default)
straico-api --pricing balance "Explain machine learning"

# Budget - fast and cheap
straico-api --pricing budget "What is 2+2?"
```

#### Model Selection

```bash
# Specific model
straico-api --model "openai/gpt-4o" "Complex reasoning task"

# Multiple specific models
straico-api --models "openai/gpt-4o-mini" "anthropic/claude-3-5-sonnet-20241022" "Compare approaches"

# Smart selector with quantity
straico-api --pricing quality --quantity 3 "Analyze from multiple perspectives"
```

#### Interactive Sessions

```bash
# Start interactive mode
straico-api --interactive

# Interactive with specific settings
straico-api -i --pricing quality --model "openai/gpt-4o"
```

## Environment Variables

- `STRAICO_API_KEY`: Your Straico API key (recommended method)

## Pricing Methods

- **quality**: Prioritizes response quality and accuracy (may cost more)
- **balance**: Balances quality and cost (recommended for most use cases)
- **budget**: Minimizes cost while maintaining acceptable quality

## API Versions

- **v0**: Single model responses, basic smart selector
- **v1**: Multi-model support, advanced smart selector with quantity parameter (default)

## Error Handling

The client provides helpful error messages and suggestions:

```python
try:
    response = client.chat("Hello", model="invalid-model")
except Exception as e:
    print(f"Error: {e}")
```

For invalid model names, the client automatically suggests similar models:

```bash
$ straico-api --model "gpt4" "Hello"
❌ Error: Model not found: gpt4

💡 Did you mean one of these models?

1. GPT-4o
   ID: openai/gpt-4o
   Cost: 2.5 coins per 100 words

2. GPT-4o Mini
   ID: openai/gpt-4o-mini
   Cost: 0.15 coins per 100 words
```

## Response Format

Responses include:

- **Model Information**: Which model(s) processed the request
- **Content**: The AI-generated response
- **Pricing**: Coins used and word count
- **Citations**: Automatic formatting of sources and annotations (when available)
- **Justification**: Model selection reasoning (when using smart selector with quantity)

## Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=straico_api tests/

# Run specific test
pytest tests/test_client.py::test_chat
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Format code
black straico_api tests

# Lint code
flake8 straico_api tests

# Type checking
mypy straico_api
```

## Building and Publishing

```bash
# Build package
python -m build

# Upload to PyPI (requires credentials)
twine upload dist/*
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/dwinkler1/straico-python/issues)
- **Author**: Daniel Winkler (dw@dwinkler.org)

## Changelog

### 1.0.0 (2025-03-10)

- Initial release
- Smart LLM selector with pricing strategies
- Multi-model support (v1 API)
- Quantity-based model selection
- Interactive CLI mode
- Loading animations
- Citation formatting
- Model suggestions for typos
- Comprehensive error handling
