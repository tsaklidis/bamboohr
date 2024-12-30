import time
from requests.models import PreparedRequest

def add_params_to_url(url:str, params:dict) -> str:
    """
    Helper function to add a query string to a URL from a dictionary of parameters.
    """
    req = PreparedRequest()
    req.prepare_url(url, params)
    return req.url


def timer(func):
    """
    A decorator function that measures the execution time of the decorated function.
    Args:
      func: The function to be decorated.
    Returns:
      A wrapper function that measures the execution time of the decorated function.
    """
    def wrapper_timer(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        exec_time = end_time - start_time
        print(f"[i] {func.__name__}() | Execution time: {exec_time:.2f}s")
        return result
    return wrapper_timer
