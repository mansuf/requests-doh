from requests.adapters import HTTPAdapter
from urllib3.connectionpool import HTTPSConnectionPool, HTTPConnectionPool

from .connector import (
    RequestsDoHHTTPConnection,
    RequestsDoHHTTPSConnection,
    set_dns_cache_expire_time
)
from .resolver import set_dns_provider

__all__ = ('DNSOverHTTPSAdapter',)

class DNSOverHTTPSAdapter(HTTPAdapter):
    """An DoH (DNS over HTTPS) adapter for :class:`requests.Session`
    
    Parameters
    -----------
    provider: :class:`str`
        A DoH provider
    cache_expire_time: :class:`float`
        Set DNS cache expire time
    **kwargs
        These parameters will be passed to :class:`requests.adapters.HTTPAdapter`
    """
    def __init__(self, provider=None, cache_expire_time=None, **kwargs):
        if provider:
            set_dns_provider(provider)

        if cache_expire_time:
            set_dns_cache_expire_time(cache_expire_time)

        super().__init__(**kwargs)

    def get_connection(self, url, proxies=None):
        conn = super().get_connection(url, proxies)
        if isinstance(conn, HTTPSConnectionPool):
            conn.ConnectionCls = RequestsDoHHTTPSConnection
        else:
            # HTTP type
            conn.ConnectionCls = RequestsDoHHTTPConnection
        return conn