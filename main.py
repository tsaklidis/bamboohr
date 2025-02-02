import logging
import os
import json
from datetime import datetime

from settings.vars import bamboo_domain, api_key
from client import BambooTimeOff

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    filename='app.log',
    filemode='w',
    format='%(name)s - %(levelname)s - %(message)s'
)

CONFIG_FILE = 'config.json'

def read_config():
    """Reads the api_key and bamboo_domain from the JSON config file if it exists."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
            return config.get('api_key'), config.get('bamboo_domain')
    return None, None

def write_config(api_key, bamboo_domain):
    """Writes the api_key and bamboo_domain to the JSON config file."""
    config = {
        'api_key': api_key,
        'bamboo_domain': bamboo_domain
    }
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=4)

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
| Version:   v1.4                                   |
| Developer: Stefanos I. Tsaklidis                  |
=====================================================
"""
    print(welcome_message)

def print_emps(employees):
    name_width = 32
    title_width = 43
    sector_width = 13
    id_width = 5

    # Print header
    header = f"{'ID':<{id_width}} | {'Name':<{name_width}} | {'Job Title':<{title_width}} | {'Sector':<{sector_width}}"
    print(header)
    print("=" * (name_width + title_width + sector_width + 6))

    # Print employee data
    for emp in employees:
        bamboo_id = emp.bamboo_id or "-"
        display_name = emp.display_name or "-"
        job_title = emp.job_title or "-"
        sector = emp.sector or "-"

        row = f"{bamboo_id:<{id_width}} | {display_name:<{name_width}} | {job_title:<{title_width}} | {sector:<{sector_width}}"
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
    welcome_screen()
    try:
        # Read API key and domain from config file
        api_key, bamboo_domain = read_config()

        # If not found, ask user and save to config file
        if not api_key or not bamboo_domain:
            print("API key and Bamboo domain not found in config file.")
            api_key = input("Enter your API key: ").strip()
            bamboo_domain = input("Enter your Bamboo domain: ").strip()
            write_config(api_key, bamboo_domain)
            print("First time setup completed. Getting initial data from BambooHR...")
            print("-" * 53)

        bamboo = BambooTimeOff(api_key, bamboo_domain)
        logging.info("BambooTimeOff client initialized")

        while True:
            main_menu()
            today = datetime.now().strftime("%Y-%m-%d")
            option = input("Pick one option: ").strip()

            if option == "1":
                start = input("Enter start date (YYYY-MM-DD): ").strip()
                end = input("Enter end date (YYYY-MM-DD): ").strip()
                focus_factor = input("Enter focus factor (0.75-1.00): ").strip()

                mode = input("Select employees by: IDs or SECTOR?: ").strip()
                if mode.lower() == "ids":
                    available_emps = bamboo.get_available_employees_no_perms(
                        start, end, sector=("BE", "FE", "QA")
                    )
                    print_emps(available_emps)
                    print("=========================================================")
                    print("|   Capacity calculation by selecting employees mode    |")
                    print("=========================================================")
                    ids = input("Enter IDs, separated by commas: ").strip().replace(" ", "")
                    ids = ids.split(",")
                    capacity = calculate_capacity(
                        bamboo, start, end, ids, float(focus_factor)
                    )
                else:
                    print("=========================================================")
                    print("| Capacity calculation by selecting employees by sector |")
                    print("=========================================================")
                    sector = input("Enter sector(s) (BE, FE, QA, separated by commas): ").strip()
                    sector = tuple(sector.split(","))
                    capacity = calculate_capacity(bamboo, start, end, sector, float(focus_factor))

                print("=================")
                print("|    Results    |")
                print("=================")
                print(f"Sprint capacity: {capacity} hours")
                print("-" * 53)

            elif option == "2":
                employees = bamboo.get_available_employees_no_perms(today, today)
                print_emps(employees)

            elif option == "3":
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