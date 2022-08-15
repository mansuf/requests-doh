# Changelog

## UNRELEASED

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

### Breaking changes

- Starting from UNRELEASED, requests-doh rely on [dnspython](https://github.com/rthalley/dnspython) module 
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