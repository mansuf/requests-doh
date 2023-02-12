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
remove_dns_provider("another-dns")
```
