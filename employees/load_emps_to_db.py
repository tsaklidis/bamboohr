from settings.vars import db_name
from sqlmodel import Session, SQLModel, create_engine
from employees.models import Employee

# Database setup
engine = create_engine(f'sqlite:///../{db_name}')
SQLModel.metadata.create_all(engine)


def parse_emps_and_save_to_db(all_emps):
    for emp in all_emps:
        sector = "-"
        job_title = emp.get("jobTitle", "")
        if job_title:
            if "Frontend" in job_title:
                sector = "FE"
            if "Backend" in job_title:
                sector = "BE"
            if "QA" in job_title:
                sector = "QA"
            if "DevOps" in job_title:
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
        with Session(engine) as session:
            session.add(tmp_emp)
            session.commit()
