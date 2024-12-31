import pathlib

from sqlmodel import Session, SQLModel, create_engine
from employees.models import Employee
from settings.vars import db_name
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging

root_dir = pathlib.Path(__file__).parent.parent
db_path = root_dir / db_name
if not db_path.exists():
    default_engine = create_engine(f'sqlite:///{db_name}')
    SQLModel.metadata.create_all(default_engine)
else:
    default_engine = create_engine(f'sqlite:///{db_path}')


def parse_employees_and_save_to_db(all_employees, engine=default_engine):
    for emp in all_employees:
        sector = "-"
        job_title = emp.get("jobTitle", "")
        if job_title:
            if "Frontend" in job_title:
                sector = "FE"
            if "Backend" in job_title:
                sector = "BE"
            if "QA" in job_title:
                sector = "QA"
            if "SMG" in job_title or "Java" in job_title:
                sector = "SMG"
            if "DevOps" in job_title or "Ops" in job_title:
                sector = "DVPS"

        tmp_emp = Employee(
            bamboo_id=emp.get('id'),
            f_name=emp.get('firstName'),
            l_name=emp.get('lastName'),
            job_title=emp.get('jobTitle'),
            mobile_phone=emp.get('mobilePhone'),
            photo_url=emp.get('photoUrl'),
            display_name=emp.get('displayName'),
            sector=sector
        )

        try:
            with Session(engine) as session:
                session.add(tmp_emp)
                session.commit()
        except IntegrityError as e:
            logging.error(f"Integrity error: {e.orig}")
            session.rollback()
        except SQLAlchemyError as e:
            logging.error(f"Database error: {e}")
            session.rollback()