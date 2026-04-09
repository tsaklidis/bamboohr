import time
from datetime import date, timedelta
from requests.models import PreparedRequest

def add_params_to_url(url:str, params:dict) -> str:
    """
    Helper function to add a query string to a URL from a dictionary of parameters.
    """
    req = PreparedRequest()
    req.prepare_url(url, params)
    return req.url

def iter_weekdays(start_str, end_str):
    """Yield each weekday (Mon-Fri) date object in the range."""
    current = date.fromisoformat(start_str)
    end_date = date.fromisoformat(end_str)
    while current <= end_date:
        if current.weekday() < 5:  # Mon=0 … Fri=4
            yield current
        current += timedelta(days=1)

