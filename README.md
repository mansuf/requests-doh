[![pypi-total-downloads](https://img.shields.io/pypi/dm/requests-doh?label=DOWNLOADS&style=for-the-badge)](https://pypi.org/project/requests-doh)
[![python-ver](https://img.shields.io/pypi/pyversions/requests-doh?style=for-the-badge)](https://pypi.org/project/requests-doh)
[![pypi-release-ver](https://img.shields.io/pypi/v/requests-doh?style=for-the-badge)](https://pypi.org/project/requests-doh)

# requests-doh

DNS over HTTPS resolver for python [requests](https://github.com/psf/requests) using [dnspython](https://github.com/rthalley/dnspython) module

## Key features

- Resolve hosts using [public DNS servers](https://adguard-dns.io/kb/general/dns-providers) over HTTPS
- DNS local cache, making faster to resolve hosts
- Easy to use

## Installation

You must have Python 3.8.x or up with Pip installed.

### PyPI (stable version)

```shell
# For Linux / Mac OS
python3 -m pip install requests-doh

# For Windows
py -3 -m pip install requests-doh
```

### Git (Development version)

```shell
git clone https://github.com/mansuf/requests-doh.git
cd requests-doh
python setup.py install
```

For more information about installation, see [Installation](https://requests-doh.mansuf.link/en/stable/installation.html)

## Usage

```python
# for convenience
from requests_doh import DNSOverHTTPSSession

# By default, DoH provider will set to `cloudflare`
session = DNSOverHTTPSSession(provider='google')
r = session.get('https://google.com')
print(r.content)
```

For more information about usage, see [API usage](https://requests-doh.mansuf.link/en/stable/api_usage.html)

## Links

- [PyPI](https://pypi.org/project/requests-doh/)
- [Docs](https://requests-doh.mansuf.link/)

## License

See [LICENSE](https://github.com/mansuf/requests-doh/blob/main/LICENSE)