# (c) 2021 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.internal_test_tools.tests.unit.compat.mock import patch

from ansible_collections.community.internal_test_tools.tests.unit.utils.open_url_framework import (
    OpenUrlCall,
    OpenUrlProxy,
)

from ansible_collections.community.internal_test_tools.tests.unit.plugins.modules.utils import (
    set_module_args,
    ModuleTestCase,
    AnsibleExitJson,
    # AnsibleFailJson,
)

from ansible_collections.felixfontein.hosttech_dns.plugins.modules import hosttech_dns_record

# This import is needed so patching below works
import ansible_collections.felixfontein.hosttech_dns.plugins.module_utils.wsdl

from .helper import (
    add_dns_record_lines,
    check_nil,
    check_value,
    create_zones_answer,
    expect_authentication,
    expect_value,
    find_map_entry,
    get_value,
    validate_wsdl_call,
    DEFAULT_ENTRIES,
    DEFAULT_ZONE_RESULT,
)

lxmletree = pytest.importorskip("lxml.etree")


def validate_add_request(zone, entry):
    def predicate(content, header, body):
        fn_data = get_value(body, lxmletree.QName('https://ns1.hosttech.eu/public/api', 'addRecord').text)
        check_value(get_value(fn_data, 'search'), zone, type=('http://www.w3.org/2001/XMLSchema', 'string'))
        record_data = get_value(fn_data, 'recorddata')
        check_value(find_map_entry(record_data, 'type'), entry[2], type=('http://www.w3.org/2001/XMLSchema', 'string'))
        prefix = find_map_entry(record_data, 'prefix')
        if entry[3]:
            check_value(prefix, entry[3], type=('http://www.w3.org/2001/XMLSchema', 'string'))
        elif prefix is not None:
            check_nil(prefix)
        check_value(find_map_entry(record_data, 'target'), entry[4], type=('http://www.w3.org/2001/XMLSchema', 'string'))
        check_value(find_map_entry(record_data, 'ttl'), str(entry[5]), type=('http://www.w3.org/2001/XMLSchema', 'int'))
        if entry[6] is None:
            comment = find_map_entry(record_data, 'comment', allow_non_existing=True)
            if comment is not None:
                check_nil(comment)
        else:
            check_value(find_map_entry(record_data, 'comment'), entry[6], type=('http://www.w3.org/2001/XMLSchema', 'string'))
        if entry[7] is None:
            check_nil(find_map_entry(record_data, 'priority'))
        else:
            check_value(find_map_entry(record_data, 'priority'), entry[7], type=('http://www.w3.org/2001/XMLSchema', 'string'))
        return True

    return predicate


def create_add_result(entry):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        ''.join([
            '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"'
            ' xmlns:ns1="https://ns1.hosttech.eu/public/api"'
            ' xmlns:xsd="http://www.w3.org/2001/XMLSchema"'
            ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"'
            ' xmlns:ns2="http://xml.apache.org/xml-soap"'
            ' xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"'
            ' SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">']),
        '<SOAP-ENV:Header>',
        '<ns1:authenticateResponse>',
        '<return xsi:type="xsd:boolean">true</return>',
        '</ns1:authenticateResponse>',
        '</SOAP-ENV:Header>',
        '<SOAP-ENV:Body>',
        '<ns1:addRecordResponse>',
    ]
    add_dns_record_lines(lines, entry, 'return')
    lines.extend([
        '</ns1:addRecordResponse>',
        '</SOAP-ENV:Body>',
        '</SOAP-ENV:Envelope>',
    ])
    return ''.join(lines)


class TestHosttechDNSRecord(ModuleTestCase):
    def test_idempotency_present(self):
        open_url = OpenUrlProxy([
            OpenUrlCall('POST', 200)
            .expect_content_predicate(validate_wsdl_call([
                expect_authentication('foo', 'bar'),
                expect_value(
                    [lxmletree.QName('https://ns1.hosttech.eu/public/api', 'getZone').text, 'sZoneName'],
                    'example.com',
                    ('http://www.w3.org/2001/XMLSchema', 'string')
                ),
            ]))
            .result_str(DEFAULT_ZONE_RESULT),
        ])
        with patch('ansible_collections.felixfontein.hosttech_dns.plugins.module_utils.wsdl.open_url', open_url):
            with pytest.raises(AnsibleExitJson) as e:
                set_module_args({
                    'hosttech_username': 'foo',
                    'hosttech_password': 'bar',
                    'state': 'present',
                    'zone': 'example.com',
                    'record': 'example.com',
                    'type': 'MX',
                    'ttl': 3600,
                    'value': [
                        '10 example.com',
                    ],
                    '_ansible_remote_tmp': '/tmp/tmp',
                    '_ansible_keep_remote_files': True,
                })
                hosttech_dns_record.main()

        print(e.value.args[0])
        assert e.value.args[0]['changed'] is False

    def test_idempotency_absent_value(self):
        open_url = OpenUrlProxy([
            OpenUrlCall('POST', 200)
            .expect_content_predicate(validate_wsdl_call([
                expect_authentication('foo', 'bar'),
                expect_value(
                    [lxmletree.QName('https://ns1.hosttech.eu/public/api', 'getZone').text, 'sZoneName'],
                    'example.com',
                    ('http://www.w3.org/2001/XMLSchema', 'string')
                ),
            ]))
            .result_str(DEFAULT_ZONE_RESULT),
        ])
        with patch('ansible_collections.felixfontein.hosttech_dns.plugins.module_utils.wsdl.open_url', open_url):
            with pytest.raises(AnsibleExitJson) as e:
                set_module_args({
                    'hosttech_username': 'foo',
                    'hosttech_password': 'bar',
                    'state': 'absent',
                    'zone': 'example.com',
                    'record': '*.example.com',
                    'type': 'A',
                    'ttl': 3600,
                    'value': [
                        '1.2.3.6',
                    ],
                    '_ansible_remote_tmp': '/tmp/tmp',
                    '_ansible_keep_remote_files': True,
                })
                hosttech_dns_record.main()

        print(e.value.args[0])
        assert e.value.args[0]['changed'] is False

    def test_idempotency_absent_ttl(self):
        open_url = OpenUrlProxy([
            OpenUrlCall('POST', 200)
            .expect_content_predicate(validate_wsdl_call([
                expect_authentication('foo', 'bar'),
                expect_value(
                    [lxmletree.QName('https://ns1.hosttech.eu/public/api', 'getZone').text, 'sZoneName'],
                    'example.com',
                    ('http://www.w3.org/2001/XMLSchema', 'string')
                ),
            ]))
            .result_str(DEFAULT_ZONE_RESULT),
        ])
        with patch('ansible_collections.felixfontein.hosttech_dns.plugins.module_utils.wsdl.open_url', open_url):
            with pytest.raises(AnsibleExitJson) as e:
                set_module_args({
                    'hosttech_username': 'foo',
                    'hosttech_password': 'bar',
                    'state': 'absent',
                    'zone': 'example.com',
                    'record': '*.example.com',
                    'type': 'A',
                    'ttl': 1800,
                    'value': [
                        '1.2.3.5',
                    ],
                    '_ansible_remote_tmp': '/tmp/tmp',
                    '_ansible_keep_remote_files': True,
                })
                hosttech_dns_record.main()

        print(e.value.args[0])
        assert e.value.args[0]['changed'] is False

    def test_idempotency_absent_type(self):
        open_url = OpenUrlProxy([
            OpenUrlCall('POST', 200)
            .expect_content_predicate(validate_wsdl_call([
                expect_authentication('foo', 'bar'),
                expect_value(
                    [lxmletree.QName('https://ns1.hosttech.eu/public/api', 'getZone').text, 'sZoneName'],
                    'example.com',
                    ('http://www.w3.org/2001/XMLSchema', 'string')
                ),
            ]))
            .result_str(DEFAULT_ZONE_RESULT),
        ])
        with patch('ansible_collections.felixfontein.hosttech_dns.plugins.module_utils.wsdl.open_url', open_url):
            with pytest.raises(AnsibleExitJson) as e:
                set_module_args({
                    'hosttech_username': 'foo',
                    'hosttech_password': 'bar',
                    'state': 'absent',
                    'zone': 'example.com',
                    'record': 'example.com',
                    'type': 'CAA',
                    'ttl': 3600,
                    'value': [
                        'something',
                    ],
                    '_ansible_remote_tmp': '/tmp/tmp',
                    '_ansible_keep_remote_files': True,
                })
                hosttech_dns_record.main()

        print(e.value.args[0])
        assert e.value.args[0]['changed'] is False

    def test_idempotency_absent_record(self):
        open_url = OpenUrlProxy([
            OpenUrlCall('POST', 200)
            .expect_content_predicate(validate_wsdl_call([
                expect_authentication('foo', 'bar'),
                expect_value(
                    [lxmletree.QName('https://ns1.hosttech.eu/public/api', 'getZone').text, 'sZoneName'],
                    'example.com',
                    ('http://www.w3.org/2001/XMLSchema', 'string')
                ),
            ]))
            .result_str(DEFAULT_ZONE_RESULT),
        ])
        with patch('ansible_collections.felixfontein.hosttech_dns.plugins.module_utils.wsdl.open_url', open_url):
            with pytest.raises(AnsibleExitJson) as e:
                set_module_args({
                    'hosttech_username': 'foo',
                    'hosttech_password': 'bar',
                    'state': 'absent',
                    'zone': 'example.com.',
                    'record': 'somewhere.example.com.',
                    'type': 'A',
                    'ttl': 3600,
                    'value': [
                        '1.2.3.6',
                    ],
                    '_ansible_remote_tmp': '/tmp/tmp',
                    '_ansible_keep_remote_files': True,
                })
                hosttech_dns_record.main()

        print(e.value.args[0])
        assert e.value.args[0]['changed'] is False

    def test_change_add_one_check_mode(self):
        open_url = OpenUrlProxy([
            OpenUrlCall('POST', 200)
            .expect_content_predicate(validate_wsdl_call([
                expect_authentication('foo', 'bar'),
                expect_value(
                    [lxmletree.QName('https://ns1.hosttech.eu/public/api', 'getZone').text, 'sZoneName'],
                    'example.com',
                    ('http://www.w3.org/2001/XMLSchema', 'string')
                ),
            ]))
            .result_str(DEFAULT_ZONE_RESULT),
        ])
        with patch('ansible_collections.felixfontein.hosttech_dns.plugins.module_utils.wsdl.open_url', open_url):
            with pytest.raises(AnsibleExitJson) as e:
                set_module_args({
                    'hosttech_username': 'foo',
                    'hosttech_password': 'bar',
                    'state': 'present',
                    'zone': 'example.com',
                    'record': 'example.com',
                    'type': 'CAA',
                    'ttl': 3600,
                    'value': [
                        'test',
                    ],
                    '_ansible_check_mode': True,
                    '_ansible_remote_tmp': '/tmp/tmp',
                    '_ansible_keep_remote_files': True,
                })
                hosttech_dns_record.main()

        print(e.value.args[0])
        assert e.value.args[0]['changed'] is True

    def test_change_add_one(self):
        new_entry = (131, 42, 'CAA', '', 'test', 3600, None, None)
        open_url = OpenUrlProxy([
            OpenUrlCall('POST', 200)
            .expect_content_predicate(validate_wsdl_call([
                expect_authentication('foo', 'bar'),
                expect_value(
                    [lxmletree.QName('https://ns1.hosttech.eu/public/api', 'getZone').text, 'sZoneName'],
                    'example.com',
                    ('http://www.w3.org/2001/XMLSchema', 'string')
                ),
            ]))
            .result_str(DEFAULT_ZONE_RESULT),
            OpenUrlCall('POST', 200)
            .expect_content_predicate(validate_wsdl_call([
                expect_authentication('foo', 'bar'),
                validate_add_request('example.com', new_entry),
            ]))
            .result_str(create_add_result(new_entry)),
        ])
        with patch('ansible_collections.felixfontein.hosttech_dns.plugins.module_utils.wsdl.open_url', open_url):
            with pytest.raises(AnsibleExitJson) as e:
                set_module_args({
                    'hosttech_username': 'foo',
                    'hosttech_password': 'bar',
                    'state': 'present',
                    'zone': 'example.com',
                    'record': 'example.com',
                    'type': 'CAA',
                    'ttl': 3600,
                    'value': [
                        'test',
                    ],
                    '_ansible_remote_tmp': '/tmp/tmp',
                    '_ansible_keep_remote_files': True,
                })
                hosttech_dns_record.main()

        print(e.value.args[0])
        assert e.value.args[0]['changed'] is True
