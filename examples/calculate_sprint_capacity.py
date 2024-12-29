from settings.vars import bamboo_domain, api_key
from client import BambooTimeOff
from helpers import timer


@timer
def calculate_capacity_example():
    bamboo = BambooTimeOff(api_key, bamboo_domain)
    start = "2024-12-23"
    end = "2024-12-29"

    # The "sector" used, is a mapping that can be found in "employees/load_employees_to_db.py"
    # It is used for the purpose of the project and can be changed/avoided
    sector = ("BE", "QA", "FE")
    capacity = bamboo.calculate_capacity(
        start, end, sector=sector
    )

    print(f"For the sprint in range {start} and {end}")
    print(f"The capacity is: {capacity} hours")
    print(f"Teams in the sprint: {sector}")

if __name__ == "__main__":
    calculate_capacity_example()
