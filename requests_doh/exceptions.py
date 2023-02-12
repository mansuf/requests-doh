class RequestsDOHException(Exception):
    """Base exception for requests_doh library"""

class DNSQueryFailed(RequestsDOHException):
    """Failed to query DNS from given host"""
    pass

class DoHProviderNotExist(RequestsDOHException):
    """DoH provider is not exist in list of available DoH providers"""
    pass