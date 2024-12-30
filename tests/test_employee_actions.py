import unittest
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy import text
from employees.models import EmployeeActions
from settings.vars import db_test_name


class TestEmployeeActions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(f"sqlite:///../{db_test_name}")
        SQLModel.metadata.create_all(cls.engine)
        cls.actions = EmployeeActions(cls.engine)

    def setUp(self):
        # Clean the database before each test
        with Session(self.engine) as session:
            session.execute(text("DELETE FROM employees"))
            session.commit()

    def test_add_employee(self):
        employee_data = {
            "bamboo_id": 1,
            "f_name": "John",
            "l_name": "Doe",
            "display_name": "John Doe",
            "job_title": "Backend Developer",
            "mobile_phone": "1234567890",
            "photo_url": "http://example.com/photo.jpg",
            "sector": "BE",
        }
        employee = self.actions.add_employee(employee_data)
        with Session(self.engine) as session:
            # Refresh the employee instance within the session
            session.add(employee)
            session.refresh(employee)
            self.assertIsNotNone(employee)
            self.assertEqual(employee.bamboo_id, 1)
            self.assertEqual(employee.f_name, "John")

    def test_get_employee(self):
        employee_data = {
            "bamboo_id": 2,
            "f_name": "Jane",
            "l_name": "Doe",
            "display_name": "Jane Doe",
            "job_title": "Frontend Developer",
            "mobile_phone": "0987654321",
            "photo_url": "http://example.com/photo.jpg",
            "sector": "FE",
        }
        self.actions.add_employee(employee_data)
        employee = self.actions.get_employee(2)
        with Session(self.engine) as session:
            # Refresh the employee instance within the session
            session.add(employee)
            session.refresh(employee)
            self.assertIsNotNone(employee)
            self.assertEqual(employee.bamboo_id, 2)
            self.assertEqual(employee.f_name, "Jane")

    def test_update_employee(self):
        employee_data = {
            "bamboo_id": 3,
            "f_name": "Alice",
            "l_name": "Smith",
            "display_name": "Alice Smith",
            "job_title": "QA Engineer",
            "mobile_phone": "1122334455",
            "photo_url": "http://example.com/photo.jpg",
            "sector": "QA",
        }
        self.actions.add_employee(employee_data)
        update_data = {"job_title": "Senior QA Engineer", "mobile_phone": "5566778899"}
        updated_employee = self.actions.update_employee(3, update_data)
        with Session(self.engine) as session:
            # Refresh the updated employee instance within the session
            session.add(updated_employee)
            session.refresh(updated_employee)
            self.assertIsNotNone(updated_employee)
            self.assertEqual(updated_employee.job_title, "Senior QA Engineer")
            self.assertEqual(updated_employee.mobile_phone, "5566778899")

    def test_delete_employee(self):
        employee_data = {
            "bamboo_id": 4,
            "f_name": "Bob",
            "l_name": "Brown",
            "display_name": "Bob Brown",
            "job_title": "DevOps Engineer",
            "mobile_phone": "6677889900",
            "photo_url": "http://example.com/photo.jpg",
            "sector": "DevOps",
        }
        self.actions.add_employee(employee_data)
        result = self.actions.delete_employee(4)
        self.assertTrue(result)
        deleted_employee = self.actions.get_employee(4)
        self.assertIsNone(deleted_employee)

    def test_get_employees_excluding_ids(self):
        employees_data = [
            {
                "bamboo_id": 5,
                "f_name": "Alice",
                "l_name": "Johnson",
                "display_name": "Alice Johnson",
                "job_title": "Manager",
                "mobile_phone": "1111111111",
                "photo_url": "http://example.com/photo.jpg",
                "sector": "HR",
            },
            {
                "bamboo_id": 6,
                "f_name": "Bob",
                "l_name": "Smith",
                "display_name": "Bob Smith",
                "job_title": "Engineer",
                "mobile_phone": "2222222222",
                "photo_url": "http://example.com/photo.jpg",
                "sector": "IT",
            },
        ]
        for data in employees_data:
            self.actions.add_employee(data)
        employees = self.actions.get_employees_excluding_ids([5])
        self.assertEqual(len(employees), 1)
        self.assertEqual(employees[0].bamboo_id, 6)

    def test_get_all_employees(self):
        employees_data = [
            {
                "bamboo_id": 7,
                "f_name": "Charlie",
                "l_name": "Brown",
                "display_name": "Charlie Brown",
                "job_title": "Analyst",
                "mobile_phone": "3333333333",
                "photo_url": "http://example.com/photo.jpg",
                "sector": "Finance",
            },
            {
                "bamboo_id": 8,
                "f_name": "Daisy",
                "l_name": "Miller",
                "display_name": "Daisy Miller",
                "job_title": "Consultant",
                "mobile_phone": "4444444444",
                "photo_url": "http://example.com/photo.jpg",
                "sector": "Consulting",
            },
        ]
        for data in employees_data:
            self.actions.add_employee(data)
        employees = self.actions.get_all_employees()
        self.assertEqual(len(employees), 2)

    def test_get_employees_by_sector_and_id(self):
        employee_data = {
            "bamboo_id": 9,
            "f_name": "Eve",
            "l_name": "Davis",
            "display_name": "Eve Davis",
            "job_title": "QA Engineer",
            "mobile_phone": "5555555555",
            "photo_url": "http://example.com/photo.jpg",
            "sector": "QA",
        }
        self.actions.add_employee(employee_data)
        employees = self.actions.get_employees_by_sector_and_id("QA", [9])
        self.assertEqual(len(employees), 1)
        self.assertEqual(employees[0].bamboo_id, 9)

    def test_get_employees_by_sector(self):
        employee_data = {
            "bamboo_id": 10,
            "f_name": "Frank",
            "l_name": "White",
            "display_name": "Frank White",
            "job_title": "QA Engineer",
            "mobile_phone": "6666666666",
            "photo_url": "http://example.com/photo.jpg",
            "sector": "QA",
        }
        self.actions.add_employee(employee_data)
        employees = self.actions.get_employees_by_sector("QA")
        self.assertEqual(len(employees), 1)
        self.assertEqual(employees[0].bamboo_id, 10)

    def test_get_employees_by_ids(self):
        employees_data = [
            {
                "bamboo_id": 11,
                "f_name": "Grace",
                "l_name": "Hall",
                "display_name": "Grace Hall",
                "job_title": "Engineer",
                "mobile_phone": "7777777777",
                "photo_url": "http://example.com/photo.jpg",
                "sector": "IT",
            },
            {
                "bamboo_id": 12,
                "f_name": "Hank",
                "l_name": "Green",
                "display_name": "Hank Green",
                "job_title": "Manager",
                "mobile_phone": "8888888888",
                "photo_url": "http://example.com/photo.jpg",
                "sector": "HR",
            },
        ]
        for data in employees_data:
            self.actions.add_employee(data)
        employees = self.actions.get_employees_by_ids([11, 12])
        self.assertEqual(len(employees), 2)

    def test_get_employee_by_id(self):
        employee_data = {
            "bamboo_id": 13,
            "f_name": "Ivy",
            "l_name": "King",
            "display_name": "Ivy King",
            "job_title": "Consultant",
            "mobile_phone": "9999999999",
            "photo_url": "http://example.com/photo.jpg",
            "sector": "Consulting",
        }
        self.actions.add_employee(employee_data)
        employee = self.actions.get_employee_by_id(13)
        self.assertIsNotNone(employee)
        self.assertEqual(employee.bamboo_id, 13)

    def test_count_all_available_employees(self):
        employees_data = [
            {
                "bamboo_id": 14,
                "f_name": "Jack",
                "l_name": "Lewis",
                "display_name": "Jack Lewis",
                "job_title": "Analyst",
                "mobile_phone": "1010101010",
                "photo_url": "http://example.com/photo.jpg",
                "sector": "Finance",
            },
            {
                "bamboo_id": 15,
                "f_name": "Kim",
                "l_name": "Young",
                "display_name": "Kim Young",
                "job_title": "Consultant",
                "mobile_phone": "1111111111",
                "photo_url": "http://example.com/photo.jpg",
                "sector": "Consulting",
            },
        ]
        for data in employees_data:
            self.actions.add_employee(data)
        count = self.actions.count_all_available_employees()
        self.assertEqual(count, 2)

    def test_count_employees_by_sector_and_id(self):
        employee_data = {
            "bamboo_id": 16,
            "f_name": "Liam",
            "l_name": "Walker",
            "display_name": "Liam Walker",
            "job_title": "QA Engineer",
            "mobile_phone": "1212121212",
            "photo_url": "http://example.com/photo.jpg",
            "sector": "QA",
        }
        self.actions.add_employee(employee_data)
        count = self.actions.count_employees_by_sector_and_id("QA", [16])
        self.assertEqual(count, 1)


if __name__ == "__main__":
    unittest.main()
