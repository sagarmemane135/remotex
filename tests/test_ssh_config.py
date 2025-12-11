"""
Tests for SSH config management
"""

import unittest
from pathlib import Path
from unittest.mock import patch, mock_open
import tempfile
import os

from remotex.ssh_config import (
    get_ssh_config_path,
    ensure_ssh_config_exists,
    get_all_hosts,
    parse_ssh_config,
    add_host_to_config,
    host_exists
)


class TestSSHConfig(unittest.TestCase):
    """Test SSH config operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_config = """Host test1
    HostName 192.168.1.1
    User ubuntu
    Port 22
    IdentityFile ~/.ssh/id_rsa

Host test2
    HostName 192.168.1.2
    User root
    Port 2222
"""
    
    def test_get_ssh_config_path(self):
        """Test getting SSH config path."""
        path = get_ssh_config_path()
        self.assertIsInstance(path, Path)
        self.assertTrue(str(path).endswith(".ssh/config"))
    
    @patch('remotex.ssh_config.get_ssh_config_path')
    def test_parse_ssh_config(self, mock_path):
        """Test parsing SSH config."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(self.test_config)
            temp_path = f.name
        
        try:
            mock_path.return_value = Path(temp_path)
            config = parse_ssh_config("test1")
            
            self.assertIsNotNone(config)
            self.assertEqual(config['hostname'], '192.168.1.1')
            self.assertEqual(config['user'], 'ubuntu')
            self.assertEqual(config['port'], 22)
        finally:
            os.unlink(temp_path)
    
    def test_host_exists(self):
        """Test checking if host exists."""
        # This would need mocking of get_all_hosts
        pass


if __name__ == '__main__':
    unittest.main()

