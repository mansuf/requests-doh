# Changelog

## Unreleased

### New features

- Added ability to connect to a custom DoH provider by IP address, skipping DNS
  resolution of the provider itself [#9](https://github.com/mansuf/requests-doh/issues/9)
    - `add_dns_provider()` now accepts `bootstrap_address` and `verify` parameters.
      The connection is made straight to `bootstrap_address` (bypassing DNS) while
      the TLS certificate is still verified against the hostname in the provider URL
    - `DNSOverHTTPSSession` and `DNSOverHTTPSAdapter` now accept optional
      `provider_url`, `provider_host` and `verify` parameters as a shortcut,
      which register the provider with `add_dns_provider()` under the hood

## v1.0.0

In summary, this update introduce some breaking changes to resolver session and update library dependencies.

### Breaking changes

Now function `requests_doh.resolver.set_resolver_session` only accept `httpx.Client` rather than `requests.Client`. 
This is because [dnspython changes](https://dnspython.readthedocs.io/en/stable/whatsnew.html#id6) makes it no longer 
accepting `requests.Client`

And `requests_doh.resolver.get_resolver_session` are now returning `httpx.Client` rather than `requests.Client`

### Dependencies

- Bump requests from v2.31.0 to v2.32.3 due to [CVE-2024-35195](https://github.com/advisories/GHSA-9wx4-h78v-vm56)
- Bump dnspython from v2.3.0 to v2.6.1 due to [CVE-2023-29483](https://github.com/advisories/GHSA-3rq5-2g8h-59hc)

## v0.3.3

### Fix bugs

- Fixed missing dependencies (`ModuleNotFoundError: No module named socks`)

## v0.3.2

### Fix bugs

- Fixed requests with socks proxy is not working #3

### Note: Potential breaking changes

Functions `set_dns_cache_expire_time()` and `purge_dns_cache()` imported from module `requests_doh.connector` are no longer exists. Instead you can import it from `requests_doh.cachemanager`

If you usually import those functions from `requests_doh` (root library), these changes doesn't affect you at all.

For example:

```python
# If you do this starting from v0.3.2, you will get `ImportError`
from requests_doh.connector import set_dns_cache_expire_time, purge_dns_cache

# Do this instead
from requests_doh.cachemanager import set_dns_cache_expire_time, purge_dns_cache

# Those changes doesn't affect you if you use this import method
from requests_doh import set_dns_cache_expire_time, purge_dns_cache
```

## v0.3.1

This update fix `requests` dependencies because of [CVE-202-32681](https://github.com/psf/requests/security/advisories/GHSA-j8r2-6x86-q33q)

### Dependencies

- Bump requests from v2.28.2 to v2.31.0

## v0.3.0

### New features

- Added ability to add custom DNS over HTTPS provider [#1](https://github.com/mansuf/requests-doh/issues/1)
- Added ability to remove DNS over HTTPS provider

### Improvements

- Improved performance for querying DNS over HTTPS

## v0.2.4

### Dependecies

- Updated requests from v2.28.1 to v2.28.2
- Updated dnspython from v2.2.1 to v2.3.0

## v0.2.3

### Fix bugs

- Fixed missing dependecies resulting error `dns.query.NoDOH: Neither httpx nor requests is available.`

## v0.2.2

### Improvements

- Improved DoH resolving

## v0.2.1

### Fix bugs

- Fixed unhandled exception if host doesn't contain AAAA type

## v0.2.0

```{warning}
Broken, do not use this version. Instead use `v0.2.1`
```

### New features

- Added `get_all_dns_provider()`, returning all available DoH providers.
- Added new DoH providers
    - cloudflare-security
    - cloudflare-family
    - opendns
    - opendns-family
    - adguard
    - adguard-family
    - adguard-unfiltered
    - quad9
    - quad9-unsecured
- Added `DNSOverHTTPSSession` for ready-to-use DoH requests session

### Breaking changes

- Starting from v0.2.0, requests-doh rely on [dnspython](https://github.com/rthalley/dnspython) module 
for extending it's library usage and query to many public and private DNS.

## v0.1.1

### Fix bugs

- Fix ipv6 addresses is not handled properly

## v0.1.0

### New features

- Added DoH local caching

### Fix bugs

- Fix requests for http prefix (`http://`) is hanging up

## v0.0.1

Initial release
