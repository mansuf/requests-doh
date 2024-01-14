"""
This module is intended to modify socks (socks5:// & socks4://) and http proxies to resolve DNS 
remotely to public DNS servers (such as google, cloudlflare, etc) or private DNS servers instead of locally.

NOTE: This may be useless if users are using socks proxy with DNS remote resolver (socks5h:// & socks4a://)
"""

from base64 import b64encode
import typing
import socket
import struct
from urllib3.contrib.socks import socks, _TYPE_SOCKS_OPTIONS, SocketTimeout
from urllib3.exceptions import ConnectTimeoutError, NewConnectionError
from urllib3.connection import HTTPConnection, HTTPSConnection

from ..resolver import resolve_dns
from ..cachemanager import cachemanager

class socksocketmod(socks.socksocket):
    """Modified socks socket to resolve DNS remotely to public or private DNS servers"""
    def _write_SOCKS5_address(self, addr, file):
        """
        Return the host and port packed for the SOCKS5 protocol,
        and the resolved address as a tuple object.
        """
        host, port = addr
        proxy_type, _, _, rdns, username, password = self.proxy
        family_to_byte = {socket.AF_INET: b"\x01", socket.AF_INET6: b"\x04"}

        # If the given destination address is an IP address, we'll
        # use the IP address request even if remote resolving was specified.
        # Detect whether the address is IPv4/6 directly.
        for family in (socket.AF_INET, socket.AF_INET6):
            try:
                addr_bytes = socket.inet_pton(family, host)
                file.write(family_to_byte[family] + addr_bytes)
                host = socket.inet_ntop(family, addr_bytes)
                file.write(struct.pack(">H", port))
                return host, port
            except socket.error:
                continue

        # Well it's not an IP number, so it's probably a DNS name.
        if rdns:
            # Resolve remotely
            host_bytes = host.encode("idna")
            file.write(b"\x03" + chr(len(host_bytes)).encode() + host_bytes)
        else:
            # { MODIFIED CODE }
            # Resolve remotely
            cached = cachemanager.get_cache(host)
            if not cached:
                addresses = resolve_dns(host)

                cachemanager.set_cache(host, addresses)
            else:
                addresses = cached

            addresses = socket.getaddrinfo(addresses[0], port, socket.AF_UNSPEC,
                                           socket.SOCK_STREAM,
                                           socket.IPPROTO_TCP,
                                           socket.AI_ADDRCONFIG)
            
            # We can't really work out what IP is reachable, so just pick the
            # first.
            target_addr = addresses[0]
            family = target_addr[0]
            host = target_addr[4][0]

            addr_bytes = socket.inet_pton(family, host)
            file.write(family_to_byte[family] + addr_bytes)
            host = socket.inet_ntop(family, addr_bytes)
        file.write(struct.pack(">H", port))
        return host, port

    # ============
    # Negotiators
    # ============

    def _negotiate_SOCKS5(self, *dest_addr):
        return super()._negotiate_SOCKS5(*dest_addr)

    def _negotiate_SOCKS4(self, dest_addr, dest_port):
        """Negotiates a connection through a SOCKS4 server."""
        proxy_type, addr, port, rdns, username, password = self.proxy

        writer = self.makefile("wb")
        reader = self.makefile("rb", 0)  # buffering=0 renamed in Python 3
        try:
            # Check if the destination address provided is an IP address
            remote_resolve = False
            try:
                addr_bytes = socket.inet_aton(dest_addr)
            except socket.error:
                # It's a DNS name. Check where it should be resolved.
                if rdns:
                    addr_bytes = b"\x00\x00\x00\x01"
                    remote_resolve = True
                else:
                    # { MODIFIED CODE }
                    cached = cachemanager.get_cache(dest_addr)
                    if not cached:
                        addresses = resolve_dns(dest_addr)

                        cachemanager.set_cache(dest_addr, addresses)
                    else:
                        addresses = cached

                    address = addresses[0]
                    addr_bytes = socket.inet_aton(address)

            # Construct the request packet
            writer.write(struct.pack(">BBH", 0x04, 0x01, dest_port))
            writer.write(addr_bytes)

            # The username parameter is considered userid for SOCKS4
            if username:
                writer.write(username)
            writer.write(b"\x00")

            # DNS name if remote resolving is required
            # NOTE: This is actually an extension to the SOCKS4 protocol
            # called SOCKS4A and may not be supported in all cases.
            if remote_resolve:
                writer.write(dest_addr.encode("idna") + b"\x00")
            writer.flush()

            # Get the response from the server
            resp = self._readall(reader, 8)
            if resp[0:1] != b"\x00":
                # Bad data
                raise socks.GeneralProxyError(
                    "SOCKS4 proxy server sent invalid data")

            status = ord(resp[1:2])
            if status != 0x5A:
                # Connection failed: server returned an error
                error = socks.SOCKS4_ERRORS.get(status, "Unknown error")
                raise socks.SOCKS4Error("{:#04x}: {}".format(status, error))

            # Get the bound address/port
            self.proxy_sockname = (socket.inet_ntoa(resp[4:]),
                                   struct.unpack(">H", resp[2:4])[0])
            if remote_resolve:
                self.proxy_peername = socket.inet_ntoa(addr_bytes), dest_port
            else:
                self.proxy_peername = dest_addr, dest_port
        finally:
            reader.close()
            writer.close()

    def _negotiate_HTTP(self, dest_addr, dest_port):
        """Negotiates a connection through an HTTP server.

        NOTE: This currently only supports HTTP CONNECT-style proxies."""
        proxy_type, addr, port, rdns, username, password = self.proxy

        # { MODIFIED CODE }
        # If we need to resolve locally, we do this now (with caching)
        cached = cachemanager.get_cache(dest_addr)
        if not cached and not rdns:
            addresses = resolve_dns(dest_addr)

            cachemanager.set_cache(dest_addr, addresses)
        else:
            addresses = cached

        addr = dest_addr if rdns else addresses[0]

        http_headers = [
            (b"CONNECT " + addr.encode("idna") + b":"
             + str(dest_port).encode() + b" HTTP/1.1"),
            b"Host: " + dest_addr.encode("idna")
        ]

        if username and password:
            http_headers.append(b"Proxy-Authorization: basic "
                                + b64encode(username + b":" + password))

        http_headers.append(b"\r\n")

        self.sendall(b"\r\n".join(http_headers))

        # We just need the first line to check if the connection was successful
        fobj = self.makefile()
        status_line = fobj.readline()
        fobj.close()

        if not status_line:
            raise socks.GeneralProxyError("Connection closed unexpectedly")

        try:
            proto, status_code, status_msg = status_line.split(" ", 2)
        except ValueError:
            raise socks.GeneralProxyError("HTTP proxy server sent invalid response")

        if not proto.startswith("HTTP/"):
            raise socks.GeneralProxyError(
                "Proxy server does not appear to be an HTTP proxy")

        try:
            status_code = int(status_code)
        except ValueError:
            raise socks.HTTPError(
                "HTTP proxy server did not return a valid HTTP status")

        if status_code != 200:
            error = "{}: {}".format(status_code, status_msg)
            if status_code in (400, 403, 405):
                # It's likely that the HTTP proxy server does not support the
                # CONNECT tunneling method
                error += ("\n[*] Note: The HTTP proxy server may not be"
                          " supported by PySocks (must be a CONNECT tunnel"
                          " proxy)")
            raise socks.HTTPError(error)

        self.proxy_sockname = (b"0.0.0.0", 0)
        self.proxy_peername = addr, dest_port

    # Redeclare modified proxy negotiators
    _proxy_negotiators = {
        socks.SOCKS4: _negotiate_SOCKS4,
        socks.SOCKS5: _negotiate_SOCKS5,
        socks.HTTP: _negotiate_HTTP
    }

# This code is copied from PySocks version 1.7.1
def create_connection(dest_pair,
                      timeout=None, source_address=None,
                      proxy_type=None, proxy_addr=None,
                      proxy_port=None, proxy_rdns=True,
                      proxy_username=None, proxy_password=None,
                      socket_options=None):
    """create_connection(dest_pair, *[, timeout], **proxy_args) -> socket object

    Like socket.create_connection(), but connects to proxy
    before returning the socket object.

    dest_pair - 2-tuple of (IP/hostname, port).
    **proxy_args - Same args passed to socksocket.set_proxy() if present.
    timeout - Optional socket timeout value, in seconds.
    source_address - tuple (host, port) for the socket to bind to as its source
    address before connecting (only for compatibility)
    """
    # Remove IPv6 brackets on the remote address and proxy address.
    remote_host, remote_port = dest_pair
    if remote_host.startswith("["):
        remote_host = remote_host.strip("[]")
    if proxy_addr and proxy_addr.startswith("["):
        proxy_addr = proxy_addr.strip("[]")

    err = None

    # Allow the SOCKS proxy to be on IPv4 or IPv6 addresses.
    for r in socket.getaddrinfo(proxy_addr, proxy_port, 0, socket.SOCK_STREAM):
        family, socket_type, proto, canonname, sa = r
        sock = None
        try:
            sock = socksocketmod(family, socket_type, proto)

            if socket_options:
                for opt in socket_options:
                    sock.setsockopt(*opt)

            if isinstance(timeout, (int, float)):
                sock.settimeout(timeout)

            if proxy_type:
                sock.set_proxy(proxy_type, proxy_addr, proxy_port, proxy_rdns,
                               proxy_username, proxy_password)
            if source_address:
                sock.bind(source_address)

            sock.connect((remote_host, remote_port))
            return sock

        except (socket.error, socks.ProxyError) as e:
            err = e
            if sock:
                sock.close()
                sock = None

    if err:
        raise err

    raise socket.error("gai returned empty list.")

# This code is copied from urllib3/contrib/socks.py version 2.1.0 (from requests v2.31.0)
class SOCKSConnection(HTTPConnection):
    """
    A plain-text HTTP connection that connects via a SOCKS proxy.
    """

    def __init__(
        self,
        _socks_options: _TYPE_SOCKS_OPTIONS,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        self._socks_options = _socks_options
        super().__init__(*args, **kwargs)

    def _new_conn(self) -> socksocketmod:
        """
        Establish a new connection via the SOCKS proxy.
        """
        extra_kw: dict[str, typing.Any] = {}
        if self.source_address:
            extra_kw["source_address"] = self.source_address

        if self.socket_options:
            extra_kw["socket_options"] = self.socket_options

        try:
            conn = create_connection(
                (self.host, self.port),
                proxy_type=self._socks_options["socks_version"],
                proxy_addr=self._socks_options["proxy_host"],
                proxy_port=self._socks_options["proxy_port"],
                proxy_username=self._socks_options["username"],
                proxy_password=self._socks_options["password"],
                proxy_rdns=self._socks_options["rdns"],
                timeout=self.timeout,
                **extra_kw,
            )

        except SocketTimeout as e:
            raise ConnectTimeoutError(
                self,
                f"Connection to {self.host} timed out. (connect timeout={self.timeout})",
            ) from e

        except socks.ProxyError as e:
            # This is fragile as hell, but it seems to be the only way to raise
            # useful errors here.
            if e.socket_err:
                error = e.socket_err
                if isinstance(error, SocketTimeout):
                    raise ConnectTimeoutError(
                        self,
                        f"Connection to {self.host} timed out. (connect timeout={self.timeout})",
                    ) from e
                else:
                    # Adding `from e` messes with coverage somehow, so it's omitted.
                    # See #2386.
                    raise NewConnectionError(
                        self, f"Failed to establish a new connection: {error}"
                    )
            else:
                raise NewConnectionError(
                    self, f"Failed to establish a new connection: {e}"
                ) from e

        except OSError as e:  # Defensive: PySocks should catch all these.
            raise NewConnectionError(
                self, f"Failed to establish a new connection: {e}"
            ) from e

        return conn

class SOCKSHTTPSConnection(SOCKSConnection, HTTPSConnection):
    pass