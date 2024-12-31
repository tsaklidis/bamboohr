import unittest
from unittest.mock import patch
from main import calculate_capacity, welcome_screen, main_menu

class TestMainFunctions(unittest.TestCase):



    @patch('main.BambooTimeOff')
    @patch('main.logging')
    def test_calculate_capacity(self, mock_logging, MockBambooTimeOff):
        mock_client = MockBambooTimeOff()
        mock_client.calculate_capacity.return_value = 100

        start = '2024-01-01'
        end = '2024-01-15'
        sector = ('BE', 'FE')
        focus_factor = 0.9

        capacity = calculate_capacity(mock_client, start, end, sector, focus_factor)
        self.assertEqual(capacity, 100)
        mock_client.calculate_capacity.assert_called_once_with(start, end, focus_factor, sector=sector)

    @patch('builtins.print')
    def test_welcome_screen(self, mock_print):
        welcome_screen()
        mock_print.assert_called_once_with("""
=====================================================
|                  BambooHR Client                  |
=====================================================
| Version:   v1.3                                   |
| Developer: Stefanos I. Tsaklidis                  |
=====================================================
""")


    @patch('builtins.print')
    def test_main_menu(self, mock_print):
        main_menu()
        mock_print.assert_any_call("1. Calculate capacity")
        mock_print.assert_any_call("2. Who is available today")
        mock_print.assert_any_call("3. Who is out of office today")
        mock_print.assert_any_call("4. Get available employees for date range")
        mock_print.assert_any_call("5. Exit")
        mock_print.assert_any_call("-" * 53)

if __name__ == '__main__':
    unittest.main()