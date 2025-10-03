"""
Test cases for CLI argument parsing.
"""

import sys
from unittest.mock import Mock, patch
import pytest
from straico_api.cli import main


def test_api_version_argument_default():
    """Test that API version defaults to v1."""
    test_args = ["straico-api", "--help"]
    
    with patch.object(sys, 'argv', test_args):
        with pytest.raises(SystemExit) as exc_info:
            main()
        # --help causes exit with code 0
        assert exc_info.value.code == 0


def test_api_version_argument_v0():
    """Test that API version can be set to v0."""
    test_args = ["straico-api", "--api-version", "v0", "test prompt"]
    
    with patch.object(sys, 'argv', test_args):
        with patch('straico_api.cli.get_api_key', return_value='test-key'):
            with patch('straico_api.cli.StraicoClient') as mock_client_class:
                mock_client = Mock()
                mock_client.chat.return_value = {
                    'success': True,
                    'data': {
                        'completion': {
                            'model': 'test-model',
                            'choices': [{'message': {'content': 'test response'}}]
                        },
                        'price': {'total': 10},
                        'words': {'total': 20}
                    }
                }
                mock_client_class.return_value = mock_client
                
                main()
                
                # Verify StraicoClient was initialized with v0
                mock_client_class.assert_called_once_with('test-key', api_version='v0')


def test_api_version_argument_v1():
    """Test that API version can be set to v1."""
    test_args = ["straico-api", "--api-version", "v1", "test prompt"]
    
    with patch.object(sys, 'argv', test_args):
        with patch('straico_api.cli.get_api_key', return_value='test-key'):
            with patch('straico_api.cli.StraicoClient') as mock_client_class:
                mock_client = Mock()
                mock_client.chat.return_value = {
                    'success': True,
                    'data': {
                        'completion': {
                            'model': 'test-model',
                            'choices': [{'message': {'content': 'test response'}}]
                        },
                        'price': {'total': 10},
                        'words': {'total': 20}
                    }
                }
                mock_client_class.return_value = mock_client
                
                main()
                
                # Verify StraicoClient was initialized with v1
                mock_client_class.assert_called_once_with('test-key', api_version='v1')


def test_api_version_argument_without_explicit_value():
    """Test that API version defaults to v1 when not specified."""
    test_args = ["straico-api", "test prompt"]
    
    with patch.object(sys, 'argv', test_args):
        with patch('straico_api.cli.get_api_key', return_value='test-key'):
            with patch('straico_api.cli.StraicoClient') as mock_client_class:
                mock_client = Mock()
                mock_client.chat.return_value = {
                    'success': True,
                    'data': {
                        'completion': {
                            'model': 'test-model',
                            'choices': [{'message': {'content': 'test response'}}]
                        },
                        'price': {'total': 10},
                        'words': {'total': 20}
                    }
                }
                mock_client_class.return_value = mock_client
                
                main()
                
                # Verify StraicoClient was initialized with default v1
                mock_client_class.assert_called_once_with('test-key', api_version='v1')


def test_api_version_invalid_value():
    """Test that invalid API version values are rejected."""
    test_args = ["straico-api", "--api-version", "v2", "test prompt"]
    
    with patch.object(sys, 'argv', test_args):
        with pytest.raises(SystemExit) as exc_info:
            main()
        # Invalid choice should exit with error code
        assert exc_info.value.code != 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
