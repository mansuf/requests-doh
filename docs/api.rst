.. currentmodule:: requests_doh

API Reference
--------------

Session
========

.. autoclass:: DNSOverHTTPSSession

Adapters
==========

.. autoclass:: DNSOverHTTPSAdapter

DNS resolver session
=====================

.. autofunction:: set_resolver_session

.. autofunction:: get_resolver_session

DoH (DNS-over-HTTPS) Provider
==============================

.. autofunction:: set_dns_provider

.. autofunction:: get_dns_provider

.. autofunction:: get_all_dns_provider

DNS Cache
==========

.. autofunction:: set_dns_cache_expire_time

.. autofunction:: purge_dns_cache