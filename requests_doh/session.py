import requests
from .adapter import DNSOverHTTPSAdapter

__all__ = ('DNSOverHTTPSSession',)

class DNSOverHTTPSSession(requests.Session):
    """A ready-to-use DoH (DNS-over-HTTPS) :class:`requests.Session`

    Parameters
    -----------
    provider: :class:`str`
        A registered DoH provider, see :doc:`doh_providers`
    cache_expire_time: :class:`float`
        Set DNS cache expire time
    provider_url: :class:`str`
        Full URL / endpoint for a custom DoH provider, without the need to
        register it with :func:`add_dns_provider` first. May contain an IP
        address to skip DNS resolution of the provider itself.
    provider_host: :class:`str`
        The provider hostname. If given together with an IP based
        ``provider_url``, the connection is made to that IP (bypassing DNS)
        while TLS SNI and certificate verification use ``provider_host``.
    verify: Union[:class:`bool`, :class:`str`]
        TLS certificate verification for a ``provider_url`` provider.
    """
    def __init__(self, *args, **kwargs):
        super().__init__()

        doh = DNSOverHTTPSAdapter(*args, **kwargs)
        self.mount('https://', doh)
        self.mount('http://', doh)