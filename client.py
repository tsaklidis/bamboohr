import base64
import logging
from typing import Union

import requests
import time
from datetime import date, timedelta

from employees.load_employees_to_db import parse_employees_and_save_to_db
from employees.models import EmployeeActions
from helpers.helpers import add_params_to_url
from settings.vars import debug, api_key, bamboo_domain

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    filename='client.log',
    filemode='w',
    format='%(name)s - %(levelname)s - %(message)s'
)

class BambooTimeOff:
    def __init__(self, token=None, company_domain=None):
        _token = token or api_key
        _company_domain = bamboo_domain or company_domain

        self.base_url = f"https://api.bamboohr.com/api/gateway.php/{_company_domain}/v1"
        self.token = f"{_token}:random"
        self.token = base64.b64encode(self.token.encode('utf-8')).decode('utf-8')
        self.headers = {
            "Accept": "application/json",
            "authorization": "Basic {}".format(self.token)
        }
        # Use session for connection reuse
        self.session = requests.Session()
        self.emp_qs = EmployeeActions()

        if self.emp_qs.count_all_available_employees() == 0:
            try:
                emps = self.get_employees_from_bamboo()
                parse_employees_and_save_to_db(emps)
            except Exception as e:
                logging.error(f"Error: {e}")

    def send_request(self, method: str, url: str, extra_headers=None) -> Union[None, requests.Response]:
        headers = self.headers.copy()
        if extra_headers:
            headers.update(extra_headers)

        start_time = time.time()
        try:
            if method == "GET":
                response = self.session.get(url, headers=headers, timeout=10)
            else:
                raise NotImplementedError(f"Method {method} is not implemented.")
        except requests.exceptions.RequestException as e:
            print(f"[E] Error sending the request for URL: {url} - Exception: {e}")
            return None

        end_time = time.time()

        if debug:
            execution_time = round((end_time - start_time), 3)
            print(f"[i] {method}: {url} - {response.status_code} | Execution time: {execution_time}s")
        response.raise_for_status()
        return response

    def get_employees_from_bamboo(self) -> list[dict]:
        """
        Fetch all employees from BambooHR.
        """
        url = f"{self.base_url}/employees/directory"
        response = self.send_request("GET", url)
        employees = response.json().get("employees")
        return employees

    def get_time_off(self, start_date: str, end_date: str) -> list[dict]:
        """
        Fetch time-off data for the specified date range.
        Attention: Restrictions are applied for Time-Off Data Access.
        """
        url = f"{self.base_url}/time_off/requests"
        params = {
            "start": start_date,
            "end": end_date
        }
        url = add_params_to_url(url, params)
        response = self.send_request("GET", url)
        time_off_data = response.json()
        return time_off_data

    def get_who_is_out_employees(self, start: str, end: str, only_ids=False) -> (list)[dict]:
        """
        Get the employees that are out of office for specific date range
        # start - a date in the form YYYY-MM-DD - defaults to the current date.
        # end - a date in the form YYYY-MM-DD - defaults to 14 days from the start date.
        """
        url = f"{self.base_url}/time_off/whos_out/"
        url = add_params_to_url(url, {"start": start, "end": end})
        rsp = self.send_request("GET", url)
        employees = rsp.json()
        if only_ids:
            employees = [emp.get("employeeId") for emp in employees]
        return employees

    def get_available_employees(self, start_date:str, end_date:str,  only_ids=False) -> list[dict]:
        """
        Calculate available employees with the use of '/employees/directory'
        The logic here is:
        1. Get all the employees from bamboo
        2. Get the time_off requests
        3. Filter the approved time off requests
        4. Get the employees who are available
        """
        employees = self.get_employees_from_bamboo()
        time_off = self.get_time_off(start_date, end_date)

        unavailable_employee_ids = set()
        for request in time_off:
            if request.get("status", {}).get("id") == "approved":
                unavailable_employee_ids.add(request["employeeId"])

        if only_ids:
            available_employees = [
                emp["id"] for emp in employees if emp["id"] not in unavailable_employee_ids
            ]
        else:
            available_employees = [
                emp for emp in employees if emp["id"] not in unavailable_employee_ids
            ]

        return available_employees

    def get_available_employees_no_perms(self, start:str, end:str, sector=None) -> list:
        """
        Get available employees with the use of '/time_off/whos_out/' endpoint.
        This endpoint can show employees without the use of an API key that
        is associated with a user who has permission to view time-off requests

        The logic here is:
        1. Get the employees who are out of office for specific date range
        2. Get all the employees that are available by excluding unavailable
        """

        out_employees_ids = self.get_who_is_out_employees(start, end, only_ids=True)

        if self.emp_qs.count_all_available_employees() == 0:
            # The database is empty try loading employees from bamboo
            try:
                emps = self.get_employees_from_bamboo()
                parse_employees_and_save_to_db(emps)
            except Exception as e:
                print(f"Error: {e}")

        employees_objs = self.emp_qs.get_employees_excluding_ids(out_employees_ids)

        if sector is not None and isinstance(sector, tuple):
            employees_objs_filtered = []
            for emp in employees_objs:
                if emp.sector in sector:
                    employees_objs_filtered.append(emp)
            return employees_objs_filtered

        return employees_objs

    def get_company_holidays(self, start:str, end:str) -> list:
        """
        This function retrieves company holidays within a specified date range.
        The logic is:
        1.Getting a list of employees who are out of office (get_who_is_out_employees)
        2.Filtering this list to only include items where the type is "holiday"
        3.Extracting the start date of each holiday and converting it to a date object
        4.Returning a list of these holiday dates
        """
        items = self.get_who_is_out_employees(start, end)
        holidays_dates = []
        for item in items:
            if item.get("type") == "holiday":
                tmp_date = date.fromisoformat(item.get("start"))
                holidays_dates.append(tmp_date)
        return holidays_dates

    def get_working_days(self, start:str, end:str, return_total=False) -> Union[int, list[date]]:
        """
        Calculate the number of working days between two dates.
        Working days are considered to be Monday through Friday, excluding weekends and holidays.
        Args:
            start (str): The start date.
            end (str): The end date.
        Returns:
            list: Returns a list of datetime.date(2024, 12, 23)
            If "return_total" flag is se to True
            int: The number of working days between the start and end dates.

        """

        working_week_days = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")
        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end)
        company_holidays = self.get_company_holidays(start, end)

        working_dates = []
        current_date = start_date
        while current_date <= end_date:
            if current_date.strftime("%A") in working_week_days and current_date not in company_holidays:
                working_dates.append(current_date)
            current_date += timedelta(days=1)

        if return_total:
            return len(working_dates)
        return working_dates

    def calculate_capacity(self, sprint_start, sprint_end, focus_factor=0.75, sector=None) -> float:
        """
        Calculates the sprint capacity of a team.

        Args:
            sprint_start (str): The start date of the sprint in YYYY-MM-DD format.
            sprint_end (str): The end date of the sprint in YYYY-MM-DD format.
            focus_factor (float, optional): The focus factor to apply to the capacity. Defaults to 0.75.
            sector (tuple, optional): The sectors to filter employees by.

        Returns:
            float: The adjusted sprint capacity in hours.
        """
        # Step 1: Get the working dates within the sprint period
        working_dates = self.get_working_days(sprint_start, sprint_end)
        hours_per_day = 8

        if not working_dates:
            # Avoid unnecessary calculations if there are no working days
            return 0.0

        working_days_in_sprint = len(working_dates)

        # Step 2: Fetch employees who are out during the sprint period
        out_employees = self.get_who_is_out_employees(sprint_start, sprint_end)

        # Step 3: Track unavailable days for each employee
        unavailable_days = {}
        for record in out_employees:
            emp_id = record.get('employeeId')
            if not emp_id:
                continue

            out_start = date.fromisoformat(record['start'])
            out_end = date.fromisoformat(record['end'])
            if emp_id not in unavailable_days:
                unavailable_days[emp_id] = set()

            # Calculate the intersection of unavailable days and working days
            unavailable_days[emp_id].update(
                working_date for working_date in working_dates if out_start <= working_date <= out_end
            )

        # Step 4: Fetch all employees from BambooHR and filter by sector if needed
        employees = []
        for emp in self.get_employees_from_bamboo():
            emp_id = emp.get('id')
            if not emp_id:
                continue

            if sector:
                _emp = self.emp_qs.get_employee_by_id(emp_id)
                if _emp and _emp.sector in sector:
                    employees.append(_emp)
            else:
                employees.append(emp)

        # Step 5: Calculate total raw capacity
        total_raw_capacity = 0
        for emp in employees:
            emp_id = emp.bamboo_id if sector else emp['id']
            # Calculate the number of available days for each employee
            available_days = working_days_in_sprint - len(unavailable_days.get(emp_id, set()))
            total_raw_capacity += available_days * hours_per_day

        # Step 6: Apply the focus factor
        total_capacity = total_raw_capacity * focus_factor

        return total_capacity