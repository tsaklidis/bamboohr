import unittest
from unittest.mock import patch, MagicMock
from datetime import date

from client import BambooTimeOff

class TestBambooTimeOff(unittest.TestCase):

    def setUp(self):
        self.bamboo = BambooTimeOff(token='fake_token', company_domain='fake_domain')

    @patch('client.requests.Session.get')
    def test_send_request(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        response = self.bamboo.send_request("GET", "https://tsaklidis.gr")
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

    @patch('client.requests.Session.get')
    def test_get_employees_from_bamboo(self, mock_get):
        mock_response = MagicMock()
        fake_rsp = {
            "employees": [
                {
                    "id": "190",
                    "displayName": "Stefanos Tsaklidis",
                    "firstName": "Stefanos",
                    "lastName": "Tsaklidis",
                    "preferredName": None,
                    "jobTitle": "Senior BE Manager",
                    "workPhone": None,
                    "mobilePhone": "+30697123456",
                    "workEmail": "stefanos@tsaklidis.gr",
                    "department": "Server",
                    "location": None,
                    "division": None,
                    "linkedIn": "https://www.linkedin.com/pub/stefanos-i-tsaklidis/46/718/883",
                    "pronouns": None,
                    "workPhoneExtension": None,
                    "supervisor": "Jhn Doe",
                    "photoUploaded": False,
                    "photoUrl": "https://resources.bamboohr.com/images/photo_person_160x160.png",
                    "canUploadPhoto": 0
                },
                {
                    "id": "145",
                    "displayName": "Bob Ross",
                    "firstName": "Bob",
                    "lastName": "Ross",
                    "preferredName": None,
                    "jobTitle": "QA Automation Engineer",
                    "workPhone": None,
                    "mobilePhone": "+30 6986548787",
                    "workEmail": "bob@ross.com",
                    "department": "QA",
                    "location": "Athens, Greece",
                    "division": "Athens",
                    "linkedIn": None,
                    "pronouns": None,
                    "workPhoneExtension": None,
                    "supervisor": "Jhn Doe",
                    "photoUploaded": False,
                    "photoUrl": "https://resources.bamboohr.com/images/photo_person_160x160.png",
                    "canUploadPhoto": 0
                }
            ]
        }
        mock_response.json.return_value = fake_rsp
        mock_get.return_value = mock_response

        employees = self.bamboo.get_employees_from_bamboo()
        self.assertEqual(len(employees), 2)
        self.assertEqual(employees[0]['id'], "190")
        self.assertEqual(employees[0]['displayName'], "Stefanos Tsaklidis")

    @patch('client.requests.Session.get')
    def test_get_time_off(self, mock_get):
        mock_response = MagicMock()
        fake_rsp = [
            {
                "id": 1,
                "employeeId": 5,
                "status": {
                    "lastChanged": "2024-12-05",
                    "lastChangedByUserId": "1",
                    "status": "approved"
                },
                "name": "Stefanos Tsaklidis",
                "start": "2024-12-05",
                "end": "2024-12-05",
                "created": "2024-12-05",
                "type": {
                    "id": "85",
                    "name": "Parental",
                    "icon": "teddy-bear"
                },
                "amount": {
                    "unit": "days",
                    "amount": "1"
                },
                "actions": {
                    "view": True,
                    "edit": False,
                    "cancel": False,
                    "approve": False,
                    "deny": False,
                    "bypass": False
                },
                "dates": {
                    "2024-12-05": "1"
                },
                "notes": {}
            },
            {
                "id": 2,
                "employeeId": 6,
                "status": {
                    "lastChanged": "2024-11-01",
                    "lastChangedByUserId": "1",
                    "status": "approved"
                },
                "name": "John Travolta",
                "start": "2024-12-06",
                "end": "2024-12-06",
                "created": "2024-10-31",
                "type": {
                    "id": "83",
                    "name": "Vacation GR",
                    "icon": "palm-trees"
                },
                "amount": {
                    "unit": "days",
                    "amount": "1"
                },
                "actions": {
                    "view": True,
                    "edit": False,
                    "cancel": False,
                    "approve": False,
                    "deny": False,
                    "bypass": False
                },
                "dates": {
                    "2024-12-06": "1"
                },
                "notes": {}
            }
        ]
        mock_response.json.return_value = fake_rsp
        mock_get.return_value = mock_response

        time_off = self.bamboo.get_time_off('2024-01-01', '2024-01-31')
        self.assertEqual(len(time_off), 2)
        self.assertEqual(time_off[0]['employeeId'], 5)

    @patch('client.requests.Session.get')
    def test_get_who_is_out_employees(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [{"employeeId": 1, "type": "vacation"}]
        mock_get.return_value = mock_response

        who_is_out = self.bamboo.get_who_is_out_employees('2024-01-01', '2024-01-31')
        self.assertEqual(len(who_is_out), 1)
        self.assertEqual(who_is_out[0]['employeeId'], 1)

    @patch('client.requests.Session.get')
    @patch('client.BambooTimeOff.get_employees_from_bamboo')
    @patch('client.BambooTimeOff.get_time_off')
    def test_get_available_employees(self, mock_get_time_off, mock_get_employees, mock_get):
        mock_get_employees.return_value = [
            {"id": 1, "name": "Stefanos Tsaklidis"},
            {"id": 2, "name": "Jane Doe"}
        ]
        mock_get_time_off.return_value = [{"employeeId": 1, "status": {"id": "approved"}}]

        available_employees = self.bamboo.get_available_employees('2024-01-01', '2024-01-31')
        self.assertEqual(len(available_employees), 1)
        self.assertEqual(available_employees[0]['id'], 2)

    @patch('client.requests.Session.get')
    @patch('client.EmployeeActions.count_all_available_employees')
    @patch('client.EmployeeActions.get_employees_excluding_ids')
    def test_get_available_employees_no_perms(self, mock_get_employees_excluding_ids, mock_count_all_available, mock_get):
        mock_count_all_available.return_value = 0
        mock_get_employees_excluding_ids.return_value = [{"id": 1, "name": "Stefanos Tsaklidis"}]

        available_employees_no_perms = self.bamboo.get_available_employees_no_perms(
            '2024-01-01', '2024-01-31'
        )
        self.assertEqual(len(available_employees_no_perms), 1)
        self.assertEqual(available_employees_no_perms[0]['id'], 1)

    @patch('client.requests.Session.get')
    def test_get_company_holidays(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [{"type": "holiday", "start": "2024-12-25"}]
        mock_get.return_value = mock_response

        holidays = self.bamboo.get_company_holidays('2024-12-01', '2024-12-31')
        self.assertEqual(len(holidays), 1)
        self.assertEqual(holidays[0], date(2024, 12, 25))

    @patch('client.requests.Session.get')
    def test_get_working_days(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [{"type": "holiday", "start": "2024-12-25"}]
        mock_get.return_value = mock_response

        working_days = self.bamboo.get_working_days('2024-12-20', '2024-12-31')
        self.assertEqual(len(working_days), 7)

    @patch('client.requests.Session.get')
    @patch('client.BambooTimeOff.get_who_is_out_employees')
    @patch('client.BambooTimeOff.get_employees_from_bamboo')
    def test_calculate_capacity(self, mock_get_employees, mock_get_who_is_out, mock_get):
        mock_get_employees.return_value = [{"id": 1, "name": "Stefanos Tsaklidis"}]
        mock_get_who_is_out.return_value = [{"employeeId": 1, "start": "2024-12-20", "end": "2024-12-31"}]

        capacity = self.bamboo.calculate_capacity('2024-12-20', '2024-12-31')
        self.assertEqual(capacity, 0.0)


if __name__ == '__main__':
    unittest.main()