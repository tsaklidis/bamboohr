from settings.vars import bamboo_domain, api_key
from client import BambooTimeOff

def print_emps(emps):
    for emp in emps:
        print(f"{emp.display_name} - {emp.job_title} | {emp.sector}")

if __name__ == "__main__":
    bamboo = BambooTimeOff(api_key, bamboo_domain)
    start = "2024-12-30"
    end = "2024-12-30"

    print("Using method without special permissions")
    employees = bamboo.get_available_employees_no_perms(start, end)
    be_employees = bamboo.get_available_employees_no_perms(
        start, end, sector=("BE", "FE", "QA")
    )

    print(f"For the range between {start} and {end}")
    print(f"The following {len(employees)} employees are available:")
    print_emps(employees)


    print(100*"#")
    print("For the backend issues the following employees are available:")
    print_emps(be_employees)


