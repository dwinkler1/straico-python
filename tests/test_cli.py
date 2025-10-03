"""
Test cases for CLI.
"""

import sys
import pytest
from unittest.mock import Mock, patch
from straico_api.cli import main


def test_api_version_default():
    """Test that default API version is v1."""
    with patch('straico_api.cli.StraicoClient') as mock_client, \
         patch('straico_api.cli.get_api_key', return_value='test-key'):
        
        sys.argv = ['cli.py', '--list-models']
        
        # Mock the get_models response
        mock_instance = Mock()
        mock_instance.get_models.return_value = {
            "success": True,
            "data": {"chat": []}
        }
        mock_client.return_value = mock_instance
        
        main()
        
        # Verify StraicoClient was initialized with v1 (default)
        mock_client.assert_called_once_with('test-key', api_version='v1')


def test_api_version_v0():
    """Test that API version v0 is accepted and passed to client."""
    with patch('straico_api.cli.StraicoClient') as mock_client, \
         patch('straico_api.cli.get_api_key', return_value='test-key'):
        
        sys.argv = ['cli.py', '--api-version', 'v0', '--list-models']
        
        # Mock the get_models response
        mock_instance = Mock()
        mock_instance.get_models.return_value = {
            "success": True,
            "data": {"chat": []}
        }
        mock_client.return_value = mock_instance
        
        main()
        
        # Verify StraicoClient was initialized with v0
        mock_client.assert_called_once_with('test-key', api_version='v0')


def test_api_version_v1():
    """Test that API version v1 is accepted and passed to client."""
    with patch('straico_api.cli.StraicoClient') as mock_client, \
         patch('straico_api.cli.get_api_key', return_value='test-key'):
        
        sys.argv = ['cli.py', '--api-version', 'v1', '--list-models']
        
        # Mock the get_models response
        mock_instance = Mock()
        mock_instance.get_models.return_value = {
            "success": True,
            "data": {"chat": []}
        }
        mock_client.return_value = mock_instance
        
        main()
        
        # Verify StraicoClient was initialized with v1
        mock_client.assert_called_once_with('test-key', api_version='v1')


def test_api_version_invalid():
    """Test that invalid API version is rejected."""
    import subprocess
    
    result = subprocess.run(
        [sys.executable, '-m', 'straico_api.cli', '--api-version', 'v2', '--list-models'],
        capture_output=True,
        text=True
    )
    
    # Should exit with error
    assert result.returncode != 0
    assert "invalid choice: 'v2'" in result.stderr
    assert "choose from 'v0', 'v1'" in result.stderr


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
