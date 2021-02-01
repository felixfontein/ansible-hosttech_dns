==================================
Hosttech DNS Modules Release Notes
==================================

.. contents:: Topics


v1.1.1
======

Bugfixes
--------

- hosttech_dns_record - fix ``diff`` mode: unchanged records were not included in ``after`` state (https://github.com/felixfontein/ansible-hosttech_dns/pull/3).
- hosttech_dns_record_info - when ``what`` was not ``single_record``, the return value ``sets`` was always empty (https://github.com/felixfontein/ansible-hosttech_dns/pull/2).

v1.1.0
======

Minor Changes
-------------

- hosttech_dns - add diff mode.

Bugfixes
--------

- hosttech_dns - fix error when creating records for new domain.

v1.0.2
======

Release Summary
---------------

Maintenance release for internal changes. Visible external change is that the changelog moved one directory up.


v1.0.1
======

Release Summary
---------------

Fix broken docs links.

v1.0.0
======

Release Summary
---------------

Initial version as a collection. Continues the `old git repository <https://github.com/felixfontein/ansible-hosttech/>`_.

New Modules
-----------

- felixfontein.hosttech_dns.hosttech_dns_record - Add or delete entries in Hosttech DNS service
- felixfontein.hosttech_dns.hosttech_dns_record_info - Retrieve entries in Hosttech DNS service
