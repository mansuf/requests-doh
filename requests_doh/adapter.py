from requests.adapters import HTTPAdapter
from urllib3.connectionpool import HTTPSConnectionPool, HTTPConnectionPool

from .connector import ModifiedHTTPConnection, ModifiedHTTPSConnection
from .resolver import set_dns_provider

__all__ = ('DNSOverHTTPSAdapter',)

class DNSOverHTTPSAdapter(HTTPAdapter):
    """An DoH (DNS over HTTPS) adapter for :class:`requests.Session`
    
    Parameters
    -----------
    provider: :class:`str`
        A DoH provider
    **kwargs
        These parameters will be passed to :meth:`requests.adapters.HTTPAdapter.__init__()`
    """
    def __init__(self, provider=None, **kwargs):
        if provider:
            set_dns_provider(provider)

        super().__init__(**kwargs)

    def get_connection(self, url, proxies=None):
        conn = super().get_connection(url, proxies)
        if isinstance(conn, HTTPSConnectionPool):
            conn.ConnectionCls = ModifiedHTTPSConnection
        else:
            # HTTP type
            conn.ConnectionCls = ModifiedHTTPConnection
        return conn