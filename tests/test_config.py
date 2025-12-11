"""
Tests for configuration management
"""

import unittest
from unittest.mock import patch
import tempfile
import json
import os

from remotex.config import (
    load_config,
    save_config,
    get_default_server,
    set_default_server
)


class TestConfig(unittest.TestCase):
    """Test configuration operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_config = {
            "default_server": "test1",
            "parallel_connections": 5,
            "timeout": 30,
            "groups": {},
            "command_aliases": {}
        }
    
    @patch('remotex.config.CONFIG_FILE')
    def test_load_config(self, mock_file):
        """Test loading configuration."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(self.test_config, f)
            temp_path = f.name
        
        try:
            mock_file.__str__ = lambda x: temp_path
            config = load_config()
            
            self.assertEqual(config['default_server'], 'test1')
            self.assertEqual(config['parallel_connections'], 5)
        finally:
            os.unlink(temp_path)
    
    def test_get_default_server(self):
        """Test getting default server."""
        with patch('remotex.config.load_config') as mock_load:
            mock_load.return_value = {"default_server": "test1"}
            server = get_default_server()
            self.assertEqual(server, "test1")


if __name__ == '__main__':
    unittest.main()

