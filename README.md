# Hosttech DNS Modules

This repository provides an [Ansible](https://github.com/ansible/ansible) collection with modules to create, modify and delete DNS records for zones hosted at the Swiss provider [Hosttech](https://www.hosttech.ch/) using their [API](https://ns1.hosttech.eu/public/api?wsdl).

## Tested with Ansible

Tested with both Ansible 2.9 and the current development version of Ansible.

## External requirements

The [`lxml` Python module](https://pypi.org/project/lxml/) is needed.

## Included content

- ``hosttech_dns_record`` module
- ``hosttech_dns_record_info`` module

## Using this collection

See [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Release notes

See [here](https://github.com/felixfontein/ansible-hosttech_dns/tree/main/changelogs/CHANGELOG.rst).

## More information

- [Ansible Collection overview](https://github.com/ansible-collections/overview)
- [Ansible User guide](https://docs.ansible.com/ansible/latest/user_guide/index.html)
- [Ansible Developer guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
- [Ansible Community code of conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)

## Licensing

GNU General Public License v3.0 or later.

See [COPYING](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
