import unittest
from sqlmodel import create_engine, Session, SQLModel, select
from sqlalchemy import text
from employees.models import Employee
from settings.vars import db_test_name  # Ensure this points to the correct test database name

class TestModels(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(f'sqlite:///../{db_test_name}')
        SQLModel.metadata.create_all(cls.engine)

    def setUp(self):
        # Clean the database before each test
        with Session(self.engine) as session:
            session.execute(text("DELETE FROM employees"))
            session.commit()

    def test_employee_model_creation(self):
        employee = Employee(
            bamboo_id=1,
            f_name="John",
            l_name="Doe",
            display_name="John Doe",
            job_title="Backend Developer",
            mobile_phone="1234567890",
            photo_url="http://example.com/photo.jpg",
            sector="BE"  # Provide a value for sector
        )
        with Session(self.engine) as session:
            session.add(employee)
            session.commit()

        with Session(self.engine) as session:
            result = session.execute(select(Employee).where(Employee.bamboo_id == 1))
            employee_from_db = result.scalar_one()
            self.assertIsNotNone(employee_from_db)
            self.assertEqual(employee_from_db.f_name, "John")
            self.assertEqual(employee_from_db.l_name, "Doe")
            self.assertEqual(employee_from_db.display_name, "John Doe")
            self.assertEqual(employee_from_db.job_title, "Backend Developer")
            self.assertEqual(employee_from_db.mobile_phone, "1234567890")
            self.assertEqual(employee_from_db.photo_url, "http://example.com/photo.jpg")
            self.assertEqual(employee_from_db.sector, "BE")

    def test_employee_optional_fields(self):
        employee = Employee(
            bamboo_id=2,
            f_name="Jane",
            l_name="Doe",
            display_name="Jane Doe",
            job_title="Frontend Developer",
            photo_url="http://example.com/default.jpg",  # Provide a default photo_url
            sector=""  # Provide an empty string if sector is optional
        )
        with Session(self.engine) as session:
            session.add(employee)
            session.commit()

        with Session(self.engine) as session:
            result = session.execute(select(Employee).where(Employee.bamboo_id == 2))
            employee_from_db = result.scalar_one()
            self.assertIsNotNone(employee_from_db)
            self.assertEqual(employee_from_db.f_name, "Jane")
            self.assertEqual(employee_from_db.l_name, "Doe")
            self.assertEqual(employee_from_db.display_name, "Jane Doe")
            self.assertEqual(employee_from_db.job_title, "Frontend Developer")
            self.assertIsNone(employee_from_db.mobile_phone)
            self.assertEqual(employee_from_db.photo_url, "http://example.com/default.jpg")
            self.assertEqual(employee_from_db.sector, "")

    def test_employee_query(self):
        employees = [
            Employee(
                bamboo_id=3, f_name="Alice", l_name="Smith",
                display_name="Alice Smith", job_title="QA Engineer",
                photo_url="http://example.com/photo.jpg",
                sector="QA"
            ),
            Employee(
                bamboo_id=4, f_name="Bob", l_name="Brown",
                display_name="Bob Brown", job_title="DevOps Engineer",
                photo_url="http://example.com/photo.jpg",
                sector="BE"
            )
        ]
        with Session(self.engine) as session:
            session.add_all(employees)
            session.commit()

        with Session(self.engine) as session:
            result = session.execute(select(Employee))
            all_employees = result.scalars().all()
            self.assertEqual(len(all_employees), 2)

if __name__ == '__main__':
    unittest.main()