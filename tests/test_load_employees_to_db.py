import unittest
import random
import string
from unittest.mock import patch
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlmodel import Session, SQLModel, create_engine
from employees.load_employees_to_db import parse_employees_and_save_to_db
from settings.vars import db_test_name


class TestLoadEmployeesToDB(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(f'sqlite:///../{db_test_name}')
        SQLModel.metadata.create_all(cls.engine)

    def setUp(self):
        # Ensure the database is clean before each test
        with Session(self.engine) as session:
            session.execute(text("DELETE FROM employees"))
            session.commit()

        # Verify the database is clean
        with Session(self.engine) as session:
            result = session.execute(text("SELECT * FROM employees"))
            employees = result.fetchall()
            assert len(employees) == 0

    def generate_random_string(self, length=10):
        letters = string.ascii_letters
        return ''.join(random.choice(letters) for _ in range(length))

    def generate_random_phone_number(self):
        return ''.join(random.choice(string.digits) for _ in range(10))

    def test_parse_employees_and_save_to_db(self):
        random_id = random.randint(1, 1000000)
        random_first_name = self.generate_random_string()
        random_last_name = self.generate_random_string()
        random_job_title = self.generate_random_string()
        random_phone_number = self.generate_random_phone_number()
        random_photo_url = f"http://example.com/{self.generate_random_string()}.jpg"
        random_display_name = f"{random_first_name} {random_last_name}"

        all_employees = [
            {
                "id": random_id,
                "firstName": random_first_name,
                "lastName": random_last_name,
                "jobTitle": random_job_title,
                "mobilePhone": random_phone_number,
                "photoUrl": random_photo_url,
                "displayName": random_display_name
            }
        ]
        parse_employees_and_save_to_db(all_employees, engine=self.engine)  # Pass the test database engine
        with Session(self.engine) as session:
            result = session.execute(text("SELECT * FROM employees"))
            employees = result.fetchall()
            self.assertEqual(len(employees), 1)

    def test_sector_assignment(self):
        test_cases = [
            {"jobTitle": "Frontend Developer", "expected_sector": "FE"},
            {"jobTitle": "Backend Developer", "expected_sector": "BE"},
            {"jobTitle": "QA Engineer", "expected_sector": "QA"},
            {"jobTitle": "SMG Manager", "expected_sector": "SMG"},
            {"jobTitle": "Java Developer", "expected_sector": "SMG"},
            {"jobTitle": "DevOps Engineer", "expected_sector": "DVPS"},
            {"jobTitle": "Ops Specialist", "expected_sector": "DVPS"},
            {"jobTitle": "Unknown Title", "expected_sector": "-"}
        ]

        for case in test_cases:
            all_employees = [
                {
                    "id": random.randint(1, 1000000),
                    "firstName": "Test",
                    "lastName": "User",
                    "jobTitle": case["jobTitle"],
                    "mobilePhone": "1234567890",
                    "photoUrl": "http://example.com/test.jpg",
                    "displayName": "Test User"
                }
            ]
            parse_employees_and_save_to_db(all_employees, engine=self.engine)
            with Session(self.engine) as session:
                result = session.execute(
                    text("SELECT sector FROM employees WHERE job_title = :job_title"),
                    {"job_title": case["jobTitle"]}
                )
                sector = result.fetchone()[0]
                self.assertEqual(sector, case["expected_sector"])


if __name__ == '__main__':
    unittest.main()