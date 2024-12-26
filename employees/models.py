from settings.vars import db_name

from typing import Optional
from sqlmodel import SQLModel, Field, create_engine, Session, select
from sqlalchemy import not_, func
from sqlalchemy.orm import sessionmaker



class Employee(SQLModel, table=True):
    __tablename__ = "employees"
    bamboo_id: int = Field(primary_key=True)
    f_name: str
    l_name: str
    display_name: str
    job_title: Optional[str] = Field(default=None)
    mobile_phone: Optional[str] = Field(default=None)
    photo_url: str
    sector: str


class EmployeeActions:
    def __init__(self):
        self.engine = create_engine(f'sqlite:///{db_name}')
        SQLModel.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_employees_excluding_ids(self, excluded_ids, only_id=False):
        with Session(self.engine) as session:
            statement = select(Employee)
            if excluded_ids:
                statement = statement.where(not_(Employee.bamboo_id.in_(excluded_ids)))
            employees = session.exec(statement).all()

        return [emp.bamboo_id for emp in employees] if only_id else employees

    def get_all_employees(self):
        # Get all employees
        with Session(self.engine) as session:
            statement = select(Employee)
            employees = session.exec(statement).all()
            return employees

    def get_employees_by_sector_and_id(self, sector, ids):
        with Session(self.engine) as session:
            statement = select(Employee).where(Employee.sector == sector).where(
                Employee.bamboo_id.in_(ids)
            ).order_by(Employee.bamboo_id)
            employees = session.exec(statement).all()
            return employees

    def get_employees_by_ids(self, ids):
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
        with Session(self.engine) as session:
            statement = select(func.count(Employee.bamboo_id)).where(
                Employee.sector == sector, Employee.bamboo_id.in_(ids)
            )
            # Use .one() to fetch the count result
            return session.exec(statement).one()
