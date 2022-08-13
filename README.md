# requests-doh

DNS over HTTPS resolver for python requests

## Installation

```shell
# For Linux / Mac OS
python3 -m pip install requests-doh

# For Windows
py -3 -m pip install requests-doh
```

## Usage

Basic usage

```python
import requests
from requests_doh import DNSOverHTTPSAdapter

adapter = DNSOverHTTPSAdapter(provider='cloudflare') # You can choose between 'google' and 'cloudflare'
session = requests.Session()
# For HTTPS
session.mount('https://', adapter)
# For HTTP
session.mount('http://', adapter)

r = session.get('https://google.com')
print(r.text)
```

Set a custom session for DoH resolver

```python
import requests
from requests_doh import set_resolver_session, DNSOverHTTPSAdapter

resolver_session = requests.Session()
# Insert some additional process here
# ...

set_resolver_session(resolver_session)

adapter = DNSOverHTTPSAdapter(provider='google')
session = requests.Session()
# For HTTPS
session.mount('https://', adapter)
# For HTTP
session.mount('http://', adapter)

r = session.get('https://google.com')
print(r.text)
```

Set an expire time (in seconds) for DoH caching

```python
import requests
from requests_doh import purge_dns_cache, DNSOverHTTPSAdapter

# Default value of `cache_expire_time` is 300
adapter = DNSOverHTTPSAdapter(provider='google', cache_expire_time=1500) 
session = requests.Session()
# For HTTPS
session.mount('https://', adapter)
# For HTTP
session.mount('http://', adapter)

r = session.get('https://google.com')
print(r.text)

# You can purge single DNS cache
purge_dns_cache('google.com')
# or all of them
purge_dns_cache()
```