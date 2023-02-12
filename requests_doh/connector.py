from __future__ import absolute_import
import ipaddress

import socket
import logging
from urllib3.connection import HTTPSConnection, HTTPConnection
from urllib3.util.connection import allowed_gai_family, _set_socket_options
from urllib3.exceptions import ConnectTimeoutError, NewConnectionError, LocationParseError
from socket import error as SocketError
from socket import timeout as SocketTimeout

try:
    from urllib3.packages.six import raise_from
except ImportError:
    # Broken package mostly
    def raise_from(value, from_value):
        try:
            raise value from from_value
        finally:
            value = None

from .resolver import resolve_dns
from .cachemanager import DNSCacheManager

__all__ = ('set_dns_cache_expire_time', 'purge_dns_cache')

log = logging.getLogger(__name__)
_cache = DNSCacheManager()

def set_dns_cache_expire_time(time):
    """Set DNS cache expired time in seconds
    
    Parameters
    -----------
    time: :class:`float`
        An expire time
    """
    _cache.set_expire_time(time)

def purge_dns_cache(host=None):
    """Purge DNS cache

    Parameters
    -----------
    host: :class:`str`
        Cached DNS host want to be purged, if ``host`` is None, all DNS caches will be purged.
    """
    if host:
        _cache.purge(host)
    else:
        _cache.purge_all()

# This code is copied from urllib3/util/connection.py version 1.26.8 (from requests v2.28.1)
def create_connection(
    address,
    timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
    source_address=None,
    socket_options=None,
):
    """Same as :meth:`urllib3.util.connection.create_connection()`, 
    except it has DNS over HTTPS resovler inside of it.
    """

    host, port = address
    if host.startswith("["):
        host = host.strip("[]")
    err = None

    # Using the value from allowed_gai_family() in the context of getaddrinfo lets
    # us select whether to work with IPv4 DNS records, IPv6 records, or both.
    # The original create_connection function always returns all records.
    family = allowed_gai_family()

    try:
        host.encode("idna")
    except UnicodeError:
        return raise_from(
            LocationParseError(u"'%s', label empty or too long" % host), None
        )

    cached = _cache.get_cache(host)
    if not cached:
        # Uncached DNS
        answers = resolve_dns(host)

        _cache.set_cache(host, answers)
    else:
        answers = cached

    for answer in answers:
        try:
            ip = ipaddress.ip_address(answer)
        except ValueError:
            # Most likely this is domain returned from DoH provider
            log.warning(f"Domain detected ({answer}) in DoH query result to {host}")
            continue
        
        for res in socket.getaddrinfo(answer, port, family, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            sock = None
            try:
                sock = socket.socket(af, socktype, proto)

                # If provided, set socket level options before connecting.
                _set_socket_options(sock, socket_options)

                if timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
                    sock.settimeout(timeout)
                if source_address:
                    sock.bind(source_address)
                sock.connect(sa)
                return sock

            except socket.error as e:
                err = e
                if sock is not None:
                    sock.close()
                    sock = None

    if err is not None:
        raise err

class RequestsDoHHTTPConnection(HTTPConnection):
    # This code is copied from urllib3/connection.py version 1.26.8 (from requests v2.28.1)
    def _new_conn(self):
        """Establish a socket connection and set nodelay settings on it.

        :return: New socket connection.
        """
        extra_kw = {}
        if self.source_address:
            extra_kw["source_address"] = self.source_address

        if self.socket_options:
            extra_kw["socket_options"] = self.socket_options

        try:
            conn = create_connection(
                (self._dns_host, self.port), self.timeout, **extra_kw
            )

        except SocketTimeout:
            raise ConnectTimeoutError(
                self,
                "Connection to %s timed out. (connect timeout=%s)"
                % (self.host, self.timeout),
            )

        except SocketError as e:
            raise NewConnectionError(
                self, "Failed to establish a new connection: %s" % e
            )

        return conn

class RequestsDoHHTTPSConnection(RequestsDoHHTTPConnection, HTTPSConnection):
    pass
