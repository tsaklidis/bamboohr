import unittest
from helpers.helpers import add_params_to_url

class TestHelpers(unittest.TestCase):

    def test_add_params_to_url(self):
        url = "http://example.com"
        params = {'key1': 'value1', 'key2': 'value2'}
        expected_url = "http://example.com/?key1=value1&key2=value2"

        result = add_params_to_url(url, params)
        self.assertEqual(result, expected_url)

        url = "http://example.com?existing_key=existing_value"
        params = {'key1': 'value1', 'key2': 'value2'}
        expected_url = "http://example.com/?existing_key=existing_value&key1=value1&key2=value2"

        result = add_params_to_url(url, params)
        self.assertEqual(result, expected_url)

        # Testing without trailing slash
        url = "http://example.com"
        params = {'key1': 'value1', 'key2': 'value2'}
        expected_url_without_slash = "http://example.com/?key1=value1&key2=value2"

        result = add_params_to_url(url, params)
        self.assertIn(result, [expected_url, expected_url_without_slash])

if __name__ == '__main__':
    unittest.main()