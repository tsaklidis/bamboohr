import logging
from datetime import datetime

from settings.vars import bamboo_domain, api_key
from client import BambooTimeOff
from helpers.helpers import timer

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    filename='app.log',
    filemode='w',
    format='%(name)s - %(levelname)s - %(message)s'
)

@timer
def calculate_capacity(client, start, end, sector, focus_factor):
    try:
        capacity = client.calculate_capacity(start, end, focus_factor, sector=sector)
        return capacity
    except Exception as e:
        logging.error(f"Error calculating capacity: {e}")
        return None

def welcome_screen():
    welcome_message = """
=====================================================
|                  BambooHR Client                  |
=====================================================
| Version:   v1.3                                   |
| Developer: Stefanos I. Tsaklidis                  |
=====================================================
"""
    print(welcome_message)

def print_emps(employees):
    name_width = 32
    title_width = 37
    sector_width = 10

    # Print header
    header = f"{'Name':<{name_width}} | {'Job Title':<{title_width}} | {'Sector':<{sector_width}}"
    print(header)
    print("=" * (name_width + title_width + sector_width + 6))

    # Print employee data
    for emp in employees:
        row = f"{emp.display_name:<{name_width}} | {emp.job_title:<{title_width}} | {emp.sector:<{sector_width}}"
        print(row)
        print("-" * (name_width + title_width + sector_width + 6))

def main_menu():
    print("1. Calculate capacity")
    print("2. Who is available today")
    print("3. Who is out of office today")
    print("4. Get available employees for date range")
    print("5. Exit")
    print("-" * 53)

if __name__ == "__main__":
    logging.info("Application started")
    try:
        welcome_screen()
        bamboo = BambooTimeOff(api_key, bamboo_domain)
        logging.info("BambooTimeOff client initialized")

        while True:
            main_menu()
            option = input("Pick one option: ").strip()

            if option == "1":
                start = input("Enter start date (YYYY-MM-DD): ").strip()
                end = input("Enter end date (YYYY-MM-DD): ").strip()
                sector = input("Enter sector(s) (BE, FE, QA separated by commas): ").strip()
                focus_factor = input("Enter focus factor (0.75-1.00): ").strip()
                sector = tuple(sector.split(","))
                capacity = calculate_capacity(bamboo, start, end, sector, float(focus_factor))
                if capacity is not None:
                    print(f"Sprint capacity: {capacity} hours")

            elif option == "2":
                today = datetime.now().strftime("%Y-%m-%d")
                employees = bamboo.get_available_employees_no_perms(today, today)
                print_emps(employees)

            elif option == "3":
                today = datetime.now().strftime("%Y-%m-%d")
                employees = bamboo.get_who_is_out_employees(today, today)
                print_emps(employees)

            elif option == "4":
                start = input("Enter start date (YYYY-MM-DD): ").strip()
                end = input("Enter end date (YYYY-MM-DD): ").strip()
                employees = bamboo.get_available_employees_no_perms(start, end)
                print_emps(employees)

            elif option == "5":
                logging.info("Exiting the program")
                print("Exiting by option selection. Goodbye!")
                break
            else:
                print("Invalid option. Please try again.")

    except Exception as e:
        logging.error(f"Unhandled exception: {e}")
        print(f"An error occurred: {e}")
    except KeyboardInterrupt as e:
        logging.info("User interrupted the program")
        print("Exiting by keyboard. Goodbye!")
