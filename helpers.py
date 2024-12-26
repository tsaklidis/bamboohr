from requests.models import PreparedRequest

def add_params_to_url(url:str, params:dict) -> str:
    """
    Helper function to add a query string to a URL from a dictionary of parameters.
    """
    req = PreparedRequest()
    req.prepare_url(url, params)
    return req.url

