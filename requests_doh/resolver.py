import requests
from urllib.parse import urlparse

from .exceptions import DNSQueryFailed

_resolver_session = None # type: requests.Session
_available_providers = {
    "cloudflare": "https://cloudflare-dns.com/dns-query",
    "google": "https://dns.google.com/resolve"
}
# Default provider
_provider = _available_providers["cloudflare"]

__all__ = (
    'set_resolver_session', 'get_resolver_session',
    'set_dns_provider', 'get_dns_provider'
)

def set_resolver_session(session):
    """Set http session to resolve DNS

    Parameters
    -----------
    session: :class:`requests.Session`
        An http session to resolve DNS

    Raises
    -------
    ValueError
        ``session`` parameter is not :class:`requests.Session` instance    
    """
    global _resolver_session

    if not isinstance(session, requests.Session):
        raise ValueError(f"`session` must be `requests.Session`, {session.__class__.__name__}")
    
    _resolver_session = session

def get_resolver_session() -> requests.Session:
    """Return an http session for DoH resolver"""
    return _resolver_session

def set_dns_provider(provider):
    """Set a DoH provider, must be 'google' or 'cloudflare'"""
    global _provider

    if provider not in _available_providers.keys():
        raise ValueError(f"invalid DoH provider, must be one of '{list(_available_providers.keys())}'")

    _provider = _available_providers[provider]

def get_dns_provider():
    """Get a DoH provider"""
    return _provider

def resolve_dns(url):
    session = get_resolver_session()

    if session is None:
        session = requests.Session()
        set_resolver_session(session)

    u = urlparse(url)

    params = {
        "name": url,
        "type": 'A'
    }
    r = session.get(
        _provider,
        params=params,
        headers={"Accept": "application/dns-json"}
    )
    data = r.json()

    if data['Status'] != 0:
        raise DNSQueryFailed(f"Failed to query DNS from host '{url}'")

    answers = data['Answer']
    yield from answers