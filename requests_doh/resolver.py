import requests
from dns.message import make_query
from dns.rdatatype import RdataType
from dns.query import https as query_https
from dns.rcode import Rcode

from .exceptions import DNSQueryFailed

_resolver_session = None # type: requests.Session
_available_providers = {
    "cloudflare": "https://cloudflare-dns.com/dns-query",
    "cloudflare-security": "https://security.cloudflare-dns.com/dns-query",
    "cloudflare-family": "https://family.cloudflare-dns.com/dns-query",
    "opendns": "https://doh.opendns.com/dns-query",
    "opendns-family": "https://doh.familyshield.opendns.com/dns-query",
    "adguard": "https://dns.adguard.com/dns-query",
    "adguard-family": "https://dns-family.adguard.com/dns-query",
    "google": "https://dns.google/dns-query"
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

def get_all_dns_provider():
    """Return all available DoH providers"""
    return tuple(_available_providers.keys())

def _resolve(session, doh_endpoint, host, rdatatype):
    req_message = make_query(host, rdatatype)
    res_message = query_https(req_message, doh_endpoint, session=session)
    rcode = Rcode(res_message.rcode())
    if rcode != Rcode.NOERROR:
        raise DNSQueryFailed(f"Failed to query DNS {rdatatype.name} from host '{host}' (rcode = {rcode.name}")

    return tuple(str(i) for i in res_message.resolve_chaining().answer)

def resolve_dns(host):
    session = get_resolver_session()

    if session is None:
        session = requests.Session()
        set_resolver_session(session)

    answers = set()

    # Reuse is good
    query = lambda rdatatype: _resolve(
        session,
        _provider,
        host,
        rdatatype
    )

    # Query A type
    answers.update(query(RdataType.A))

    # Query AAAA type
    answers.update(query(RdataType.AAAA))

    return answers, _provider