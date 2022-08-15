import requests
from .adapter import DNSOverHTTPSAdapter

__all__ = ('DNSOverHTTPSSession',)

class DNSOverHTTPSSession(requests.Session):
    """A ready-to-use DoH (DNS-over-HTTPS) :class:`requests.Session`

    Parameters
    -----------
    provider: :class:`str`
        A DoH provider
    cache_expire_time: :class:`float`
        Set DNS cache expire time
    """
    def __init__(self, *args, **kwargs):
        super().__init__()

        doh = DNSOverHTTPSAdapter(*args, **kwargs)
        self.mount('https://', doh)
        self.mount('http://', doh)