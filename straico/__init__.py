"""
Straico Python Client - Unofficial Python client for Straico API.

This package provides both a Python API client and a command-line interface
for interacting with Straico's multi-LLM chat service.

Example usage:
    >>> from straico import StraicoClient
    >>> client = StraicoClient(api_key="your-api-key")
    >>> response = client.chat("What is the capital of France?")
    >>> print(response['data']['completion']['choices'][0]['message']['content'])
"""

__version__ = "1.0.0"
__author__ = "Daniel Winkler"
__email__ = "dw@dwinkler.org"

from .client import StraicoClient, LoadingAnimation

__all__ = ["StraicoClient", "LoadingAnimation", "__version__"]
