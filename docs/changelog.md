# Changelog

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