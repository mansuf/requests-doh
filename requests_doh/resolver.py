import httpx
from dns.message import make_query
from dns.rdatatype import RdataType
from dns.query import https as query_https
from dns.rcode import Rcode

from .exceptions import (
    DNSQueryFailed,
    DoHProviderNotExist,
    NoDoHProvider
)

_resolver_session = None # type: httpx.Client
_available_providers = {
    "cloudflare": {"url": "https://cloudflare-dns.com/dns-query", "bootstrap_address": None, "verify": True},
    "cloudflare-security": {"url": "https://security.cloudflare-dns.com/dns-query", "bootstrap_address": None, "verify": True},
    "cloudflare-family": {"url": "https://family.cloudflare-dns.com/dns-query", "bootstrap_address": None, "verify": True},
    "opendns": {"url": "https://doh.opendns.com/dns-query", "bootstrap_address": None, "verify": True},
    "opendns-family": {"url": "https://doh.familyshield.opendns.com/dns-query", "bootstrap_address": None, "verify": True},
    "adguard": {"url": "https://dns.adguard.com/dns-query", "bootstrap_address": None, "verify": True},
    "adguard-family": {"url": "https://dns-family.adguard.com/dns-query", "bootstrap_address": None, "verify": True},
    "adguard-unfiltered": {"url": "https://unfiltered.adguard-dns.com/dns-query", "bootstrap_address": None, "verify": True},
    "quad9": {"url": "https://dns.quad9.net/dns-query", "bootstrap_address": None, "verify": True},
    "quad9-unsecured": {"url": "https://dns10.quad9.net/dns-query", "bootstrap_address": None, "verify": True},
    "google": {"url": "https://dns.google/dns-query", "bootstrap_address": None, "verify": True}
}
# Default provider
_provider = _available_providers["cloudflare"]

__all__ = (
    'set_resolver_session', 'get_resolver_session',
    'set_dns_provider', 'get_dns_provider',
    'add_dns_provider', 'remove_dns_provider',
    'get_all_dns_provider', 'resolve_dns'
)

def set_resolver_session(session):
    """Set http session to resolve DNS

    Parameters
    -----------
    session: :class:`httpx.Client`
        An http session to resolve DNS

    Raises
    -------
    ValueError
        ``session`` parameter is not :class:`httpx.Client` instance    
    """
    global _resolver_session

    if not isinstance(session, httpx.Client):
        raise ValueError(f"`session` must be `httpx.Client`, {session.__class__.__name__}")
    
    _resolver_session = session

def get_resolver_session() -> httpx.Client:
    """
    Return
    -------
    httpx.Client
        Return an http session for DoH resolver
    """
    return _resolver_session

def set_dns_provider(provider):
    """Set a DoH provider, must be a valid DoH providers
    
    Parameters
    -----------
    provider: :class:`str`
        An valid DoH provider, see :doc:`doh_providers`

    Raises
    -------
    DoHProviderNotExist
        Invalid DoH provider
    """
    global _provider

    if provider not in _available_providers.keys():
        raise DoHProviderNotExist(f"invalid DoH provider, must be one of '{list(_available_providers.keys())}'")

    _provider = _available_providers[provider]

def get_dns_provider():
    """
    Return
    -------
    str
        Return current DoH provider
    """
    if _provider is None:
        return None

    return _provider["url"]

def add_dns_provider(name, address, switch=False, bootstrap_address=None, verify=True):
    """Add a DoH provider

    Passing ``bootstrap_address`` makes it possible to skip DNS resolution
    entirely, including resolving the IP address of the DoH provider itself.
    The connection is made straight to that IP, while TLS SNI and certificate
    verification still use the hostname from ``address``.

    For example:

    .. code-block:: python3

        from requests_doh import DNSOverHTTPSSession, add_dns_provider

        # Connect to Cloudflare by IP, verifying the certificate against
        # ``cloudflare-dns.com``
        add_dns_provider(
            "cloudflare-by-ip",
            "https://cloudflare-dns.com/dns-query",
            bootstrap_address="104.16.249.249"
        )

        session = DNSOverHTTPSSession("cloudflare-by-ip")
        r = session.get("https://example.com")
        print(r.status_code)

    Parameters
    -----------
    name: :class:`str`
        Name for DoH provider
    address: :class:`str`
        Full URL / endpoint for DoH provider
    switch: Optional[:class:`bool`]
        If ``True``, the DoH provider will automatically switch to
        newly created DoH provider
    bootstrap_address: Optional[:class:`str`]
        IP address used to connect to the DoH provider directly, bypassing
        DNS resolution of the provider hostname
    verify: Optional[Union[:class:`bool`, :class:`str`]]
        TLS certificate verification. ``True`` (the default) verifies against
        the default CA bundle, ``False`` disables verification, and a ``str``
        specifies a path to a CA certificate file or directory.
    """
    _available_providers[name] = {
        "url": address,
        "bootstrap_address": bootstrap_address,
        "verify": verify
    }

    if switch:
        set_dns_provider(name)

def remove_dns_provider(name, fallback=None):
    """Remove a DoH provider
    
    If parameter ``name`` is an active DoH provider, 
    :func:`get_dns_provider` will return ``None``. 
    You must set ``fallback`` parameter to one of available DoH providers 
    (``fallback`` and ``name`` parameters cannot be same value) 
    or you can call :func:`set_dns_provider` after calling this function
    in order to get DoH working

    For example:

    .. code-block:: python3

        from requests_doh import DNSOverHTTPSSession, add_dns_provider, remove_dns_provider

        # Add a custom DNS and set it to active
        add_dns_provider("another-dns", "https://another-dns.example.com/dns-query", switch=True)

        # At this point, the session is still working
        session = DNSOverHTTPSSession("another-dns")
        r = session.get("https://example.com")
        print(r.status_code)

        # Let's try to remove the newly created DNS
        remove_dns_provider("another-dns", fallback="cloudflare")

        # Or we can call `set_dns_provider()`
        # if we didn't set `fallback` parameter
        # set_dns_provider("cloudflare")

        # At this point DoH provider "another-dns" is removed 
        # and "cloudflare" is set to active DoH provider
        # the session is still working
        r = session.get("https://google.com")

    But what will happend if we didn't add ``fallback`` parameter or didn't call :func:`set_dns_provider()` ?
    Well error will occurred, take a look at this example:

    .. code-block:: python3

        from requests_doh import DNSOverHTTPSSession, add_dns_provider, remove_dns_provider

        # Add a custom DNS and set it to active
        add_dns_provider("another-dns", "https://another-dns.example.com/dns-query", switch=True)

        # At this point, the session is still working
        session = DNSOverHTTPSSession("another-dns")
        r = session.get("https://example.com")
        print(r.status_code)

        # Let's try to remove the newly created DNS
        remove_dns_provider("another-dns")

        # If we send request to same URL, it would still working
        r = session.get("https://example.com")
        print(r.status_code)

        # An error occurred when we send to another URL
        # Because we didn't set ``falback`` parameter in `remove_dns_provider()`
        # (or calling function `set_dns_provider()`)
        # `get_dns_provider()` will return ``None`` and thus resolving DNS will be failed
        # Because there is no valid endpoint where we wanna resolve DNS of the host
        r = session.get("https://google.com")

    Parameters
    -----------
    name: :class:`str`
        DoH provider that want to remove
    fallback: :class:`str`
        Set a fallback DoH provider

    Raises
    -------
    DoHProviderNotExist
        DoH provider is not exist in list of available DoH providers
    """
    global _provider

    try:
        _available_providers.pop(name)
    except KeyError:
        raise DoHProviderNotExist(
            "DoH provider is not exist in list of available DoH providers"
        )

    if fallback:
        set_dns_provider(fallback)
    else:
        _provider = None

def get_all_dns_provider():
    """
    Return
    -------
    tuple[str]
        Return all available DoH providers
    """
    return tuple(_available_providers.keys())

def _resolve(session, doh_endpoint, host, rdatatype, bootstrap_address=None, verify=True):
    req_message = make_query(host, rdatatype)
    res_message = query_https(
        req_message,
        doh_endpoint,
        session=session,
        bootstrap_address=bootstrap_address,
        verify=verify,
    )
    rcode = Rcode(res_message.rcode())
    if rcode != Rcode.NOERROR:
        raise DNSQueryFailed(f"Failed to query DNS {rdatatype.name} from host '{host}' (rcode = {rcode.name}")

    answers = res_message.resolve_chaining().answer
    if answers is None:
        return None

    return tuple(str(i) for i in answers)

def resolve_dns(host):
    if _provider is None:
        raise NoDoHProvider("There is no active DoH provider")

    if _provider["bootstrap_address"] is not None or _provider["verify"] is not True:
        # dnspython ignores ``bootstrap_address`` and ``verify`` when an existing
        # session is passed in, so let it build its own client with those applied.
        session = None
    else:
        session = get_resolver_session()

        if session is None:
            session = httpx.Client()
            set_resolver_session(session)

    answers = set()

    # Reuse is good
    def query(rdatatype):
        return _resolve(
            session,
            _provider["url"],
            host,
            rdatatype,
            bootstrap_address=_provider["bootstrap_address"],
            verify=_provider["verify"],
        )

    # Query A type
    A_ANSWERS = query(RdataType.A)
    if A_ANSWERS is not None:
        answers.update(A_ANSWERS)

    # Query AAAA type
    AAAA_ANSWERS = query(RdataType.AAAA)
    if AAAA_ANSWERS is not None:
        answers.update(AAAA_ANSWERS)

    if not answers:
        raise DNSQueryFailed(
            f"DNS server {_provider['url']} returned empty results from host '{host}'"
        )

    return list(answers)
