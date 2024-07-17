# Custom exception messages

class Error(Exception):
    pass

class InvalidRequestListError(Error):
    """Raised when making a request with over 100 steam ids"""
    pass