from typing import Optional
from sqlmodel import SQLModel, Field, Session, select
from sqlalchemy import not_, func

from db.manager import DatabaseManager


class Employee(SQLModel, table=True):
    __tablename__ = "employees"
    bamboo_id: int = Field(primary_key=True)
    f_name: str
    l_name: str
    display_name: str
    job_title: Optional[str] = Field(default=None)
    mobile_phone: Optional[str] = Field(default=None)
    photo_url: Optional[str] = Field(default=None)
    sector: Optional[str] = Field(default=None)

    # Set default ordering by 'sector' column
    __table_args__ = (
        None,
        {"order_by": "sector"}
    )


class EmployeeActions:
    def __init__(self, engine=None):
        # Get the database instance
        self.engine = engine or DatabaseManager.get_db_instance()

    def _clean_ids(self, ids):
        return [id for id in ids if id is not None]

    def add_employee(self, employee_data):
        with Session(self.engine) as session:
            employee = Employee(**employee_data)
            session.add(employee)
            session.commit()
            return employee

    def get_employee(self, bamboo_id):
        with Session(self.engine) as session:
            statement = select(Employee).where(Employee.bamboo_id == bamboo_id)
            result = session.execute(statement)
            return result.scalar_one_or_none()

    def update_employee(self, bamboo_id, update_data):
        with Session(self.engine) as session:
            statement = select(Employee).where(Employee.bamboo_id == bamboo_id)
            result = session.execute(statement)
            employee = result.scalar_one_or_none()
            if employee:
                for key, value in update_data.items():
                    setattr(employee, key, value)
                session.commit()
                return employee
            return None

    def delete_employee(self, bamboo_id):
        with Session(self.engine) as session:
            statement = select(Employee).where(Employee.bamboo_id == bamboo_id)
            result = session.execute(statement)
            employee = result.scalar_one_or_none()
            if employee:
                session.delete(employee)
                session.commit()
                return True
            return False
    def get_employees_excluding_ids(self, excluded_ids, only_id=False):
        excluded_ids = self._clean_ids(excluded_ids)
        with Session(self.engine) as session:
            statement = select(Employee)
            if excluded_ids:
                statement = statement.where(not_(Employee.bamboo_id.in_(
                    excluded_ids))).order_by("sector")
            employees = session.exec(statement).all()

        return [emp.bamboo_id for emp in employees] if only_id else employees

    def get_all_employees(self):
        # Get all employees
        with Session(self.engine) as session:
            statement = select(Employee)
            employees = session.exec(statement).all()
            return employees

    def get_employees_by_sector_and_id(self, sector, ids):
        ids = self._clean_ids(ids)
        with Session(self.engine) as session:
            statement = select(Employee).where(Employee.sector == sector).where(
                Employee.bamboo_id.in_(ids)
            ).order_by(Employee.bamboo_id)
            employees = session.exec(statement).all()
            return employees

    def get_employees_by_sector(self, sector):
        with Session(self.engine) as session:
            statement = select(Employee).where(
                Employee.sector == sector
            ).where().order_by(Employee.bamboo_id)
            employees = session.exec(statement).all()
            return employees

    def get_employees_by_ids(self, ids):
        ids = self._clean_ids(ids)
        with Session(self.engine) as session:
            statement = select(Employee).where(Employee.bamboo_id.in_(ids))
            employees = session.exec(statement).all()
            return employees

    def get_employee_by_id(self, id):
        with Session(self.engine) as session:
            statement = select(Employee).where(Employee.bamboo_id == id)
            employee = session.exec(statement).first()
            return employee

    def count_all_available_employees(self):
        with Session(self.engine) as session:
            # Use .one() to fetch a single result
            return session.exec(select(func.count(Employee.bamboo_id))).one()

    def count_employees_by_sector_and_id(self, sector, ids):
        ids = self._clean_ids(ids)
        with Session(self.engine) as session:
            statement = select(func.count(Employee.bamboo_id)).where(
                Employee.sector == sector, Employee.bamboo_id.in_(ids)
            )
            # Use .one() to fetch the count result
            return session.exec(statement).one()
