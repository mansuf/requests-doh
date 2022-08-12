from __future__ import absolute_import

import socket
from urllib3.connection import HTTPSConnection, HTTPConnection
from urllib3.util.connection import allowed_gai_family, _set_socket_options
from urllib3.exceptions import ConnectTimeoutError, NewConnectionError, LocationParseError
from urllib3.packages import six
from socket import error as SocketError
from socket import timeout as SocketTimeout

from .resolver import resolve_dns

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
        return six.raise_from(
            LocationParseError(u"'%s', label empty or too long" % host), None
        )

    orig_answers = socket.getaddrinfo(host, port, family, socket.SOCK_STREAM)

    try:
        af, socktype, proto, canonname, sa = orig_answers[0]
    except IndexError:
        raise socket.error("getaddrinfo returns an empty list")

    answers = resolve_dns(host)

    for answer in answers:
        sa = (answer['data'], 443)
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

class ModifiedHTTPConnection(HTTPConnection):
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

class ModifiedHTTPSConnection(ModifiedHTTPConnection, HTTPSConnection):
    pass
