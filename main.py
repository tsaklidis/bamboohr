import logging
import os
import json
from datetime import datetime, date

from settings.vars import bamboo_domain, api_key
from client import BambooTimeOff
from helpers.helpers import iter_weekdays

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

def validate_date(date_str):
    """Validate that a string is a valid YYYY-MM-DD date."""
    try:
        date.fromisoformat(date_str)
        return True
    except (ValueError, TypeError):
        return False

def input_date(prompt, default=None):
    """
    Prompt the user for a date with optional default.
    Keeps asking until a valid YYYY-MM-DD date is entered.
    """
    hint = f" [default: {default}]" if default else ""
    while True:
        value = input(f"{prompt}{hint}: ").strip()
        if not value and default:
            return default
        if validate_date(value):
            return value
        print(f"  Invalid date '{value}'. Please use YYYY-MM-DD format.")

def print_section_header(title):
    """Print a consistent section header with centered title."""
    width = 55
    print()
    print("=" * width)
    print(title.center(width))
    print("=" * width)


def show_date_range_results(bamboo, start, end, mode):
    """
    Day-by-day interactive display for a date range.
    mode: "available" — summary table + interactive drill-down
    mode: "out"       — shows employee details inline per day
    Uses a single API call, then processes locally per day.
    """
    # One API call for the whole range (raw response)
    raw_whos_out = bamboo.get_who_is_out_employees(start, end)
    holiday_dates = bamboo.extract_holiday_dates(raw_whos_out)

    # Build per-day data (fast local DB queries only)
    weekdays = list(iter_weekdays(start, end))
    if not weekdays:
        print("\n  No working days (Mon-Fri) in the given range.")
        return

    day_data = {}
    for day in weekdays:
        if day in holiday_dates:
            day_data[day] = {"holiday": True, "out_ids": set()}
        else:
            out_ids = bamboo.get_out_ids_for_date(raw_whos_out, day)
            day_data[day] = {"holiday": False, "out_ids": out_ids}

    total_employees = bamboo.emp_qs.count_all_available_employees()

    # Holiday notice
    if holiday_dates:
        sorted_holidays = sorted(holiday_dates)
        print()
        for h in sorted_holidays:
            print(f"  * Holiday: {h.strftime('%A, %Y-%m-%d')}")

    if mode == "out":
        # "Out of office" mode: show names inline per day
        for day in weekdays:
            info = day_data[day]
            day_label = day.strftime("%A, %Y-%m-%d")

            if info["holiday"]:
                print(f"\n  --- {day_label} (Holiday) ---")
                print("  All employees are out of office (company holiday).")
            else:
                out_ids = info["out_ids"]
                out_count = len(out_ids)
                print(f"\n  --- {day_label} ({out_count} out) ---")
                if out_ids:
                    out_emps = bamboo.emp_qs.get_employees_by_ids(list(out_ids))
                    print_emps(out_emps, label="employees out of office")
                else:
                    print("  No employees are out of office.")
        print()
    else:
        # "Available" mode: summary table + drill-down
        w_num, w_date, w_avail, w_out = 3, 18, 8, 8
        border = f"  +{'-'*(w_num+2)}+{'-'*(w_date+2)}+{'-'*(w_avail+2)}+{'-'*(w_out+2)}+"

        print()
        print(border)
        print(f"  | {'#':>{w_num}} | {'Date':<{w_date}} | {'Avail.':>{w_avail}} | {'Out':>{w_out}} |")
        print(border)

        for idx, day in enumerate(weekdays, 1):
            info = day_data[day]
            day_str = day.strftime("%a, %Y-%m-%d")
            if info["holiday"]:
                avail_str = "-"
                out_str = "Holiday"
            else:
                out_count = len(info["out_ids"])
                avail_count = total_employees - out_count
                avail_str = str(avail_count)
                out_str = str(out_count)
            print(f"  | {idx:>{w_num}} | {day_str:<{w_date}} | {avail_str:>{w_avail}} | {out_str:>{w_out}} |")

        print(border)
        print(f"  {'':>{w_num+3}} {'':>{w_date+2}} Total employees: {total_employees}")

        # Interactive drill-down
        while True:
            print()
            detail_input = input("  Date for details (or Enter to go back): ").strip()
            if not detail_input:
                break
            if not validate_date(detail_input):
                print(f"  Invalid date '{detail_input}'. Use YYYY-MM-DD.")
                continue
            detail_date = date.fromisoformat(detail_input)
            if detail_date not in day_data:
                print(f"  {detail_input} is not a working day in this range.")
                continue

            info = day_data[detail_date]
            day_label = detail_date.strftime("%A, %Y-%m-%d")

            if info["holiday"]:
                print(f"\n  {day_label} is a company holiday — no employees available.\n")
            else:
                out_ids = info["out_ids"]
                available = bamboo.emp_qs.get_employees_excluding_ids(list(out_ids))
                print(f"\n  --- {day_label} ---")
                print_emps(available, label="available employees")

def welcome_screen():
    welcome_message = """
=====================================================
|                  BambooHR Client                  |
=====================================================
| Version:   v1.52                                   |
| Developer: Stefanos I. Tsaklidis                  |
=====================================================
"""
    print(welcome_message)

def print_emps(employees, label="employees"):
    if not employees:
        print(f"  No {label} found.")
        return

    w_id = 5
    w_name = 30
    w_title = 35
    w_sector = 8

    border = f"  +{'-'*(w_id+2)}+{'-'*(w_name+2)}+{'-'*(w_title+2)}+{'-'*(w_sector+2)}+"

    print()
    print(border)
    print(f"  | {'ID':<{w_id}} | {'Name':<{w_name}} | {'Job Title':<{w_title}} | {'Sector':<{w_sector}} |")
    print(border)

    for emp in employees:
        bamboo_id = str(emp.bamboo_id) if emp.bamboo_id else "-"
        display_name = (emp.display_name or "-")[:w_name]
        job_title = (emp.job_title or "-")[:w_title]
        sector = (emp.sector or "-")[:w_sector]

        print(f"  | {bamboo_id:<{w_id}} | {display_name:<{w_name}} | {job_title:<{w_title}} | {sector:<{w_sector}} |")

    print(border)
    print(f"  Total: {len(employees)} {label}")
    print()

def main_menu():
    print()
    print("-" * 55)
    print("  [1] Calculate capacity")
    print("  [2] Who is available today")
    print("  [3] Who is out of office today")
    print("  [4] Get available employees for date range")
    print("  [5] Who is out of office for date range")
    print("  [6] Exit")
    print("-" * 55)

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
                start = input_date("Enter start date (YYYY-MM-DD)", default=today)
                end = input_date("Enter end date (YYYY-MM-DD)")
                focus_factor = input("Enter focus factor (0.75-1.00): ").strip()

                mode = input("Select employees by: IDs or SECTOR?: ").strip()
                if mode.lower() == "ids":
                    available_emps = bamboo.get_available_employees_no_perms(
                        start, end, sector=("BE", "FE", "QA")
                    )
                    print_emps(available_emps, label="available employees")
                    print_section_header("Capacity calculation by employee IDs")
                    ids = input("Enter IDs, separated by commas: ").strip().replace(" ", "")
                    ids = ids.split(",")
                    capacity = calculate_capacity(
                        bamboo, start, end, ids, float(focus_factor)
                    )
                else:
                    print_section_header("Capacity calculation by sector")
                    sector = input("Enter sector(s) (BE, FE, QA, separated by commas): ").strip()
                    sector = tuple(sector.split(","))
                    capacity = calculate_capacity(bamboo, start, end, sector, float(focus_factor))

                print_section_header("Results")
                print(f"Sprint capacity: {capacity} hours")
                print("-" * 53)

            elif option == "2":
                print_section_header(f"Available employees for {today}")
                employees = bamboo.get_available_employees_no_perms(today, today)
                print_emps(employees, label="available employees")

            elif option == "3":
                print_section_header(f"Out of office today ({today})")
                employees = bamboo.get_who_is_out_employees(today, today, only_ids=True)
                if employees:
                    db_employees = bamboo.emp_qs.get_employees_by_ids(employees)
                    print_emps(db_employees, label="employees out of office")
                else:
                    print("  No employees are out of office today.")

            elif option == "4":
                start = input_date("Enter start date (YYYY-MM-DD)", default=today)
                end = input_date("Enter end date (YYYY-MM-DD)")
                print_section_header(f"Available employees ({start} to {end})")
                show_date_range_results(bamboo, start, end, mode="available")

            elif option == "5":
                start = input_date("Enter start date (YYYY-MM-DD)", default=today)
                end = input_date("Enter end date (YYYY-MM-DD)")
                print_section_header(f"Out of office ({start} to {end})")
                show_date_range_results(bamboo, start, end, mode="out")

            elif option == "6":
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