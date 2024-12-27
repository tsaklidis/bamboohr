# BambooHR API Client
[![python](https://img.shields.io/badge/python-3.9-blue)](https://www.python.org/)
[![db](https://img.shields.io/badge/db-sqlmodel-7e56c2)](https://sqlmodel.tiangolo.com/)
[![api](https://img.shields.io/badge/BambooHR-v1-73c41d)](https://documentation.bamboohr.com/docs/getting-started)


 This project provides a Python client for interacting with the [BambooHR](https://www.bamboohr.com/) API.

 It allows you to view time-off requests, read employees data, time-off requests, and more. <br>
 The data can be fetched without the use of an API key 
 that is associated with a user who has special permissions.


### ✨ Features ✨
<hr>

* **Employees Listing**:
  * Get available employees. A use case could be to calculate sprint capacity.
  * Fetch all company's employees from BambooHR including bamboo ID, 
    names, job title, phone number and photo url.
* **Time Off information**:
  * Retrieve time-off data for the specified date range.
  * List company holidays within a specified date range.
  * Calculate the number of working days between two dates. Working days 
    are considered to be Monday through Friday, excluding weekends and company 
    holidays.


### 🔧 Setup
<hr>

#### Get a BambooHR API key:
1. Log in to BambooHR.
2. Navigate to API Keys. Click your avatar in the bottom left-hand corner. 
   There will be an "API Keys" option in that menu.
3. Click "Add New Key."
   The generated API key will be displayed. Copy it immediately.
   Store the key securely in a password manager or a secure location. Do not share it with anyone.

#### Set your values:

1. Under the [settings](settings) directory, create a file named `vars.py`. 
   There is a `vars.py.example` file.
2. Set the `bamboo_domain` to the domain of your BambooHR instance. This can be found in the URL of your online BambooHR instance.
2. Set the `api_key` to your generated API key.

#### Install the required packages:
Using a virtual environment is recommended.
```bash
pip install -r requirements.txt
```

### 📚 Usage
More examples can be found under the [examples](examples) directory.
<hr>

```python
from settings.vars import bamboo_domain, api_key
from client import BambooTimeOff

def print_some_data():
    # Create the instance. If not set in settings/vars.py, provide the api and the domain
    bamboo = BambooTimeOff(api_key, bamboo_domain)
    start = "2024-12-23"
    end = "2024-12-27"
    
    # Check the company holidays
    company_holidays = bamboo.get_company_holidays(start, end)
    
    # Get info for the specified date range
    working_dates = bamboo.get_working_days(start, end)
    
    # Get the employees that can contribute the specified date range
    employees = bamboo.get_available_employees_no_perms(start, end)

    for emp in employees:
        # Check the class Employee() located in employees/models.py for more attrs
        print(f"{emp.display_name} - {emp.job_title} | {emp.sector}")
```

### 📝 Restrictions are applied for Time-Off Data Access 
<hr>

>  The API key must be associated with a user who has permission to view time-off requests for all employees in BambooHR.
> 
>  This is typically granted by assigning the user a role that includes access to the "Time Off" module in the BambooHR system.

#### Admin-Level Access:
- If you are an administrator or have been granted company-wide access, you 
can view all time-off requests.
#### Manager Access:
- If you are a manager, you might only be able to view time-off requests for employees reporting to you, unless explicitly granted wider access.
#### API-Specific Role:
- Some organizations configure API-specific roles. Ensure the role tied to 
the API key has permissions to access the `GET /time_off/requests` endpoint.