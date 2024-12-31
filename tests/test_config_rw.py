import unittest
from unittest.mock import mock_open, patch
from main import read_config, write_config
import json

class TestConfigFunctions(unittest.TestCase):
    @patch('builtins.open', new_callable=mock_open, read_data='{"api_key": "api_key_value", "bamboo_domain": "bamboo_domain_value"}')
    @patch('os.path.exists', return_value=True)
    def test_read_config(self, mock_exists, mock_file):
        # Test reading config when file exists and has valid data
        api_key, bamboo_domain = read_config()
        self.assertEqual(api_key, "api_key_value")
        self.assertEqual(bamboo_domain, "bamboo_domain_value")
        mock_file.assert_called_once_with('config.json', 'r')

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists', return_value=False)
    def test_read_config_file_not_found(self, mock_exists, mock_file):
        # Test reading config when file does not exist
        api_key, bamboo_domain = read_config()
        self.assertIsNone(api_key)
        self.assertIsNone(bamboo_domain)
        mock_exists.assert_called_once_with('config.json')

    @patch('builtins.open', new_callable=mock_open)
    def test_write_config(self, mock_file):
        # Test writing config to file
        api_key = "new_api_key"
        bamboo_domain = "new_bamboo_domain"
        write_config(api_key, bamboo_domain)
        mock_file.assert_called_once_with('config.json', 'w')
        handle = mock_file()

        # Get the actual written data
        written_data = ''.join(call.args[0] for call in handle.write.call_args_list)

        # Create the expected JSON string
        expected_output = json.dumps({
            'api_key': api_key,
            'bamboo_domain': bamboo_domain
        }, indent=4)

        self.assertEqual(written_data, expected_output)

if __name__ == '__main__':
    unittest.main()