import logging
from settings.vars import bamboo_domain, api_key
from client import BambooTimeOff
from helpers.helpers import timer

# Set up logging
logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

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
| Version:   v1.2                                   |
| Developer: Stefanos I. Tsaklidis                  |
=====================================================
"""
    print(welcome_message)

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
            option = input("Pick one option: ").replace(" ", "")

            if option == "1":
                start = input("Enter start date (YYYY-MM-DD): ")
                end = input("Enter end date (YYYY-MM-DD): ")
                sector = input("Enter sector(s) (BE, FE, QA separated by commas): ")
                focus_factor = input("Enter focus factor (0.75-1.00): ")
                sector = tuple(sector.split(","))
                capacity = calculate_capacity(bamboo, start, end, sector, float(focus_factor))
                if capacity is not None:
                    print(f"Sprint capacity: {capacity} hours")

            elif option == "5":
                logging.info("Exiting the program")
                print("Exiting the program. Goodbye!")
                break

    except Exception as e:
        logging.error(f"Unhandled exception: {e}")