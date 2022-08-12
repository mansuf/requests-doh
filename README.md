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