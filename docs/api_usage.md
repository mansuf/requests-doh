# API usage

## Easy usage

```python
# for convenience
from requests_doh import DNSOverHTTPSSession

# By default, DoH provider will set to `cloudflare`
session = DNSOverHTTPSSession(provider='google')
r = session.get('https://google.com')
print(r.content)
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
print(r.content)
```