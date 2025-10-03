"""
Test cases for StraicoClient.
"""

import os
import pytest
from straico_api import StraicoClient


def test_client_initialization():
    """Test that client initializes correctly."""
    client = StraicoClient(api_key="test-key")
    assert client.api_key == "test-key"
    assert client.api_version == "v1"
    assert client.base_url == "https://api.straico.com/v1"


def test_client_custom_version():
    """Test client with custom API version."""
    client = StraicoClient(api_key="test-key", api_version="v0")
    assert client.api_version == "v0"
    assert client.base_url == "https://api.straico.com/v0"


def test_quantity_validation():
    """Test quantity parameter validation."""
    client = StraicoClient(api_key="test-key")

    # Test invalid quantities
    for invalid_qty in [0, -1, 5, 10]:
        response = client.chat("test", quantity=invalid_qty, show_animation=False)
        assert response["success"] is False
        assert "Quantity must be between 1 and 4" in response["error"]

    # Valid quantities should not raise validation error
    # (they may fail for other reasons like invalid API key)
    for valid_qty in [1, 2, 3, 4]:
        response = client.chat("test", quantity=valid_qty, show_animation=False)
        # Should not have quantity validation error
        if not response.get("success"):
            assert "Quantity must be between 1 and 4" not in response.get("error", "")


@pytest.mark.skipif(not os.environ.get("STRAICO_API_KEY"), reason="STRAICO_API_KEY not set")
def test_real_api_call():
    """Test actual API call (requires API key)."""
    api_key = os.environ.get("STRAICO_API_KEY")
    client = StraicoClient(api_key=api_key)

    response = client.chat("What is 2+2?", pricing_method="budget", show_animation=False)

    assert response.get("success") is not False
    assert "data" in response


@pytest.mark.skipif(not os.environ.get("STRAICO_API_KEY"), reason="STRAICO_API_KEY not set")
def test_get_models():
    """Test fetching models from API."""
    api_key = os.environ.get("STRAICO_API_KEY")
    client = StraicoClient(api_key=api_key)

    models = client.get_models()

    assert models.get("success") is not False
    assert "data" in models


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
