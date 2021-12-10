# Hosttech DNS Modules
[![CI](https://github.com/felixfontein/ansible-hosttech_dns/workflows/CI/badge.svg?event=push&branch=main)](https://github.com/felixfontein/ansible-hosttech_dns/actions?query=workflow%3A%22CI%22+branch%3Amain)
[![Codecov](https://img.shields.io/codecov/c/github/felixfontein/ansible-hosttech_dns)](https://codecov.io/gh/felixfontein/ansible-hosttech_dns)

**This collection and its contents are depreated! Please use the [`community.dns`](https://galaxy.ansible.com/community/dns) collection and its HostTech DNS modules instead!**

This repository provides an [Ansible](https://github.com/ansible/ansible) collection with modules to create, modify and delete DNS records for zones hosted at the Swiss provider [Hosttech](https://www.hosttech.ch/) using their [API](https://ns1.hosttech.eu/public/api?wsdl).

You can find [documentation for this collection on my Ansible docsite](https://ansible.fontein.de/collections/felixfontein/hosttech_dns/).

## Tested with Ansible

Tested with the current Ansible 2.9, ansible-base 2.10, ansible-core 2.11 and ansible-core 2.12 releases. Ansible versions before 2.9.10 are not supported.

## External requirements

The [`lxml` Python module](https://pypi.org/project/lxml/) is needed.

## Included content

- ``hosttech_dns_record`` module
- ``hosttech_dns_record_info`` module

You can find [documentation for this collection on my Ansible docsite](https://ansible.fontein.de/collections/felixfontein/hosttech_dns/).

## Using this collection

See [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Release notes

See [here](https://github.com/felixfontein/ansible-hosttech_dns/tree/main/CHANGELOG.rst).

## Running integration tests

The CI (based on GitHub Actions) runs sanity and unit tests, but not integration tests. The integration tests need access to HostTech API credentials. If you have some, copy [`tests/integration/integration_config.yml.template`](https://github.com/felixfontein/ansible-hosttech_dns/blob/main/tests/integration/integration_config.yml.template) to `integration_config.yml` in the same directory, and insert username, key, a test zone (`domain.ch`) and test record (`foo.domain.ch`). Then run `ansible-test integration`. Please note that the test record will be deleted, (re-)created, and finally deleted, so do not use any record you actually need!

## Releasing, Deprecation and Versioning

We release new versions once there are new features or bugfixes. Deprecations can happen, and we try to announce them a long time in advance. We currently do not plan breaking changes, so there will be no new major release anytime soon.

## Contributing

Please create issues to report problems or request new features, and create PRs to fix bugs or add new features. If you want to do a refactoring PR, please create an issue first to discuss the refactoring.

Please follow the general Ansible contributor guidelines; see the [Ansible Community Guide](https://docs.ansible.com/ansible/latest/community/index.html).

## More information

- [Ansible Collection overview](https://github.com/ansible-collections/overview)
- [Ansible User guide](https://docs.ansible.com/ansible/latest/user_guide/index.html)
- [Ansible Developer guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
- [Ansible Community code of conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)

## Licensing

GNU General Public License v3.0 or later.

See [COPYING](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
