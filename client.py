import base64
from typing import Union, List

import requests
from datetime import date, datetime, timedelta


from settings.vars import debug
from employees.models import EmployeeActions
from helpers import add_params_to_url
from employees.load_emps_to_db import parse_emps_and_save_to_db

class BambooTimeOff:
    def __init__(self, token, company_domain):
        self.base_url = f"https://api.bamboohr.com/api/gateway.php/{company_domain}/v1"
        self.token = token
        self.token = base64.b64encode(self.token.encode('utf-8')).decode('utf-8')
        self.headers = {
            "Accept": "application/json",
            "authorization": "Basic {}".format(self.token)
        }
        self.emp_qs = EmployeeActions()

    def send_request(self, method, url, extra_headers=None):
        headers = self.headers
        response = {}
        if extra_headers:
            headers.update(extra_headers)
        if method == "GET":
            response = requests.get(url, headers=headers)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"Error sending the request for url:{url} exception error:{e}")
            return {}
        if debug:
            print(f"{method}: {url} - {response.status_code}")
        return response

    def get_employees_from_bamboo(self):
        """
        Fetch all employees from BambooHR.
        """
        url = f"{self.base_url}/employees/directory"
        response = self.send_request("GET", url)
        employees = response.json().get("employees")
        return employees

    def get_time_off(self, start_date, end_date):
        """
        Fetch time-off data for the specified date range.
        Attention: Restrictions are applied for Time-Off Data Access.

        The API key must be associated with a user who has permission to view
        time-off requests for all employees in BambooHR.This is typically granted
        by assigning the user a role that includes access to the "Time Off" module in the BambooHR system.

        Admin-Level Access:
            If you are an administrator or have been granted company-wide access,
            you can view all time-off requests.
        Manager Access:
            If you are a manager, you might only be able to view time-off requests
             for employees reporting to you, unless explicitly granted wider access.
        API-Specific Role:
            Some organizations configure API-specific roles. Ensure the role tied to the API key has permissions to access the time_off/requests endpoint.

        """
        url = f"{self.base_url}/time_off/requests"
        params = {
            "start": start_date,
            "end": end_date
        }
        url = add_params_to_url(url, params)
        response = self.send_request("GET", url)
        return response.json()

    def get_who_is_out_employees(self, start, end, only_ids=False):
        """
        Get the employees who are out of office for specific date range
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

    def get_available_employees(self, start_date, end_date):
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

        available_employees = [
            emp for emp in employees if emp["id"] not in unavailable_employee_ids
        ]

        return available_employees

    def get_available_employees_v2(self, start:str, end:str, sector=None) -> list:
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
                parse_emps_and_save_to_db(emps.json()['employees'])
            except Exception as e:
                print(e)

        employees_objs = self.emp_qs.get_employees_excluding_ids(out_employees_ids)

        if sector and isinstance(sector, tuple):
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


