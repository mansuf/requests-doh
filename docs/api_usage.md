# API usage

## Easy usage

```python
# for convenience
from requests_doh import DNSOverHTTPSSession

# By default, DoH provider will set to `cloudflare`
session = DNSOverHTTPSSession(provider='google')
r = session.get('https://google.com')
print(r.status_code)
```

## Basic usage with adapters

```python
import requests
from requests_doh import DNSOverHTTPSAdapter

adapter = DNSOverHTTPSAdapter(provider='cloudflare-security')
session = requests.Session()
# For HTTPS
session.mount('https://', adapter)
# For HTTP
session.mount('http://', adapter)

r = session.get('https://google.com')
print(r.status_code)
```

## Add or remove custom DoH (DNS over HTTPS) provider

```python
import requests
from requests_doh import DNSOverHTTPSSession, add_dns_provider, remove_dns_provider

# Adding a new DoH provider
add_dns_provider("another-dns", "https://another-dns.example.com/dns-query")

session = DNSOverHTTPSSession("another-dns")
r = session.get("https://google.com/")
print(r.status_code)
```

```python
import requests
from requests_doh import DNSOverHTTPSSession, add_dns_provider, remove_dns_provider

# Remove DoH provider
remove_dns_provider("another-dns", fallback="cloudflare")
```

## Connect to a custom DoH provider by IP address

If you want to skip DNS entirely, including resolving the IP address of the DoH
provider itself, you can point `requests-doh` at a provider by IP address. Pass
the provider hostname as well so the TLS certificate is still verified against
the hostname (using the IP purely to connect).

```python
from requests_doh import DNSOverHTTPSSession

# Connect straight to Cloudflare's IP, verifying the certificate against
# `cloudflare-dns.com`. No DNS request is made to resolve the provider itself.
session = DNSOverHTTPSSession(
    provider_url="https://104.16.249.249/dns-query",
    provider_host="cloudflare-dns.com",
)

r = session.get("https://example.com")
print(r.status_code)
```

The same parameters are available on `DNSOverHTTPSAdapter`, or you can register
a provider with a bootstrap address yourself with `add_dns_provider`:

```python
from requests_doh import DNSOverHTTPSSession, add_dns_provider

# Connect to Cloudflare by IP, verifying the certificate against
# `cloudflare-dns.com`
add_dns_provider(
    "cloudflare-by-ip",
    "https://cloudflare-dns.com/dns-query",
    bootstrap_address="104.16.249.249",
)

session = DNSOverHTTPSSession("cloudflare-by-ip")
r = session.get("https://example.com")
print(r.status_code)
```

You can also point at a custom provider by URL without registering it first, and
disable certificate verification with `verify=False` if needed:

```python
from requests_doh import DNSOverHTTPSSession

session = DNSOverHTTPSSession(
    provider_url="https://doh.example.com/dns-query",
    verify=False,
)
```
