"""
Test cases for StraicoClient.
"""

import os
import pytest
from unittest.mock import Mock, patch
import requests
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


@patch('requests.post')
def test_model_not_found_single_model_v1(mock_post):
    """Test model not found error handling for single model in v1 API."""
    # Mock response for model not found error
    mock_response = Mock()
    mock_response.status_code = 422
    mock_response.json.return_value = {
        "error": "Model not found: invalid-model"
    }
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_post.return_value = mock_response
    
    client = StraicoClient(api_key="test-key", api_version="v1")
    
    # Mock get_models to return some test models for suggestions
    with patch.object(client, 'get_models') as mock_get_models:
        mock_get_models.return_value = {
            "success": True,
            "data": {
                "chat": [
                    {"model": "openai/gpt-4", "name": "GPT-4"},
                    {"model": "openai/gpt-3.5-turbo", "name": "GPT-3.5 Turbo"}
                ]
            }
        }
        
        response = client.chat("test", model="invalid-model", show_animation=False)
        
        assert response["success"] is False
        assert response.get("model_not_found") is True
        assert response.get("requested_model") == "invalid-model"
        assert "suggestions" in response
        assert isinstance(response["suggestions"], list)


@patch('requests.post')
def test_model_not_found_models_list_single_v1(mock_post):
    """Test model not found error handling for single model in models list in v1 API."""
    # Mock response for model not found error
    mock_response = Mock()
    mock_response.status_code = 422
    mock_response.json.return_value = {
        "error": "Model not found: invalid-model"
    }
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_post.return_value = mock_response
    
    client = StraicoClient(api_key="test-key", api_version="v1")
    
    # Mock get_models to return some test models for suggestions
    with patch.object(client, 'get_models') as mock_get_models:
        mock_get_models.return_value = {
            "success": True,
            "data": {
                "chat": [
                    {"model": "openai/gpt-4", "name": "GPT-4"},
                    {"model": "openai/gpt-3.5-turbo", "name": "GPT-3.5 Turbo"}
                ]
            }
        }
        
        response = client.chat("test", models=["invalid-model"], show_animation=False)
        
        assert response["success"] is False
        assert response.get("model_not_found") is True
        assert response.get("requested_model") == "invalid-model"
        assert "suggestions" in response


@patch('requests.post')
def test_model_not_found_models_list_multiple_v1(mock_post):
    """Test model not found error handling for multiple models in models list in v1 API."""
    # Mock response for model not found error
    mock_response = Mock()
    mock_response.status_code = 422
    mock_response.json.return_value = {
        "error": "Model not found: invalid-model-2"
    }
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_post.return_value = mock_response
    
    client = StraicoClient(api_key="test-key", api_version="v1")
    
    # Mock get_models to return some test models for suggestions
    with patch.object(client, 'get_models') as mock_get_models:
        mock_get_models.return_value = {
            "success": True,
            "data": {
                "chat": [
                    {"model": "openai/gpt-4", "name": "GPT-4"},
                    {"model": "openai/gpt-3.5-turbo", "name": "GPT-3.5 Turbo"}
                ]
            }
        }
        
        response = client.chat("test", models=["openai/gpt-4", "invalid-model-2"], show_animation=False)
        
        assert response["success"] is False
        assert response.get("model_not_found") is True
        assert response.get("requested_model") == "invalid-model-2"  # Should extract from error message
        assert "suggestions" in response


@patch('requests.post')
def test_model_not_found_models_list_multiple_fallback_v1(mock_post):
    """Test model not found error handling fallback when specific model can't be identified."""
    # Mock response for model not found error without specific model in message
    mock_response = Mock()
    mock_response.status_code = 422
    mock_response.json.return_value = {
        "error": "Model not found"
    }
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_post.return_value = mock_response
    
    client = StraicoClient(api_key="test-key", api_version="v1")
    
    # Mock get_models to return some test models for suggestions
    with patch.object(client, 'get_models') as mock_get_models:
        mock_get_models.return_value = {
            "success": True,
            "data": {
                "chat": [
                    {"model": "openai/gpt-4", "name": "GPT-4"},
                    {"model": "openai/gpt-3.5-turbo", "name": "GPT-3.5 Turbo"}
                ]
            }
        }
        
        response = client.chat("test", models=["invalid-model-1", "invalid-model-2"], show_animation=False)
        
        assert response["success"] is False
        assert response.get("model_not_found") is True
        assert response.get("requested_model") == "invalid-model-1"  # Should use first as fallback
        assert "suggestions" in response


@patch('requests.post')
def test_model_not_found_v0_api(mock_post):
    """Test model not found error handling for v0 API (backward compatibility)."""
    # Mock response for model not found error
    mock_response = Mock()
    mock_response.status_code = 422
    mock_response.json.return_value = {
        "error": "Model not found: invalid-model"
    }
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_post.return_value = mock_response
    
    client = StraicoClient(api_key="test-key", api_version="v0")
    
    # Mock get_models to return some test models for suggestions
    with patch.object(client, 'get_models') as mock_get_models:
        mock_get_models.return_value = {
            "success": True,
            "data": {
                "chat": [
                    {"model": "openai/gpt-4", "name": "GPT-4"},
                    {"model": "openai/gpt-3.5-turbo", "name": "GPT-3.5 Turbo"}
                ]
            }
        }
        
        response = client.chat("test", model="invalid-model", show_animation=False)
        
        assert response["success"] is False
        assert response.get("model_not_found") is True
        assert response.get("requested_model") == "invalid-model"
        assert "suggestions" in response


@patch('requests.post')
def test_non_model_error_handling(mock_post):
    """Test that non-model errors are handled correctly."""
    # Mock response for different type of error
    mock_response = Mock()
    mock_response.status_code = 422
    mock_response.json.return_value = {
        "error": "Invalid API key"
    }
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()
    mock_post.return_value = mock_response
    
    client = StraicoClient(api_key="test-key", api_version="v1")
    
    response = client.chat("test", model="valid-model", show_animation=False)
    
    assert response["success"] is False
    assert response.get("model_not_found") is not True
    assert "suggestions" not in response


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
