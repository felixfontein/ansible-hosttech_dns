# (c) 2021 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import base64

import pytest

lxmletree = pytest.importorskip("lxml.etree")

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

from ansible_collections.felixfontein.hosttech_dns.plugins.modules import hosttech_dns_record_info

# This import is needed so patching below works
import ansible_collections.felixfontein.hosttech_dns.plugins.module_utils.wsdl


def validate_wsdl_call(conditions):
    def predicate(content):
        assert content.startswith(b"<?xml version='1.0' encoding='utf-8'?>\n")

        root = lxmletree.fromstring(content)
        header = None
        body = None

        for header_ in root.iter(lxmletree.QName('http://schemas.xmlsoap.org/soap/envelope/', 'Header').text):
            header = header_
        for body_ in root.iter(lxmletree.QName('http://schemas.xmlsoap.org/soap/envelope/', 'Body').text):
            body = body_

        for condition in conditions:
            if not condition(content, header, body):
                return False
        return True

    return predicate


def get_value(root, name):
    for auth in root.iter(name):
        return auth
    raise Exception('Cannot find child "{0}" in node {1}'.format(name, root))


def expect_authentication(username, password):
    def predicate(content, header, body):
        auth = get_value(header, lxmletree.QName('auth', 'authenticate').text)
        assert get_value(auth, 'UserName').text == username
        assert get_value(auth, 'Password').text == password
        return True

    return predicate


def expect_value(path, value, type=None):
    def predicate(content, header, body):
        node = body
        for entry in path:
            node = get_value(node, entry)
        if type is not None:
            type_text = node.get(lxmletree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'))
            i = type_text.find(':')
            if i < 0:
                ns = None
            else:
                ns = node.nsmap.get(type_text[:i])
                type_text = type_text[i + 1:]
            assert ns == type[0] and type_text == type[1]
        assert node.text == value
        return True

    return predicate


GET_ALL_ZONES_ANSWER = ''.join([
    '<?xml version="1.0" encoding="UTF-8"?>\n',
    '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns1="https://ns1.hosttech.eu/public/api" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ns2="http://xml.apache.org/xml-soap" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">',
    '<SOAP-ENV:Header>',
    '<ns1:authenticateResponse>',
    '<return xsi:type="xsd:boolean">true</return>',
    '</ns1:authenticateResponse>',
    '</SOAP-ENV:Header>',
    '<SOAP-ENV:Body>',
    '<ns1:getZoneResponse>',
    '<return xsi:type="ns2:Map">',
    '<item><key xsi:type="xsd:string">id</key><value xsi:type="xsd:int">42</value></item>',
    '<item><key xsi:type="xsd:string">user</key><value xsi:type="xsd:int">23</value></item>',
    '<item><key xsi:type="xsd:string">name</key><value xsi:type="xsd:string">example.com</value></item>',
    '<item><key xsi:type="xsd:string">email</key><value xsi:type="xsd:string">dns@hosttech.eu</value></item>',
    '<item><key xsi:type="xsd:string">ttl</key><value xsi:type="xsd:int">10800</value></item>',
    '<item><key xsi:type="xsd:string">nameserver</key><value xsi:type="xsd:string">ns1.hostserv.eu</value></item>',
    '<item><key xsi:type="xsd:string">serial</key><value xsi:type="xsd:string">12345</value></item>',
    '<item><key xsi:type="xsd:string">serialLastUpdate</key><value xsi:type="xsd:int">0</value></item>',
    '<item><key xsi:type="xsd:string">refresh</key><value xsi:type="xsd:int">7200</value></item>',
    '<item><key xsi:type="xsd:string">retry</key><value xsi:type="xsd:int">120</value></item>',
    '<item><key xsi:type="xsd:string">expire</key><value xsi:type="xsd:int">1234567</value></item>',
    '<item><key xsi:type="xsd:string">template</key><value xsi:nil="true"/></item>',
    '<item><key xsi:type="xsd:string">ns3</key><value xsi:type="xsd:int">1</value></item>',
    '<item><key xsi:type="xsd:string">records</key><value SOAP-ENC:arrayType="ns2:Map[8]" xsi:type="SOAP-ENC:Array">',
    '<item xsi:type="ns2:Map">',
    '<item><key xsi:type="xsd:string">id</key><value xsi:type="xsd:int">125</value></item>',
    '<item><key xsi:type="xsd:string">zone</key><value xsi:type="xsd:int">42</value></item>',
    '<item><key xsi:type="xsd:string">type</key><value xsi:type="xsd:string">A</value></item>',
    '<item><key xsi:type="xsd:string">prefix</key><value xsi:type="xsd:string"></value></item>',
    '<item><key xsi:type="xsd:string">target</key><value xsi:type="xsd:string">1.2.3.4</value></item>',
    '<item><key xsi:type="xsd:string">ttl</key><value xsi:type="xsd:int">3600</value></item>',
    '<item><key xsi:type="xsd:string">comment</key><value xsi:nil="true"/></item>',
    '<item><key xsi:type="xsd:string">priority</key><value xsi:nil="true"/></item>',
    '</item>',
    '<item xsi:type="ns2:Map">',
    '<item><key xsi:type="xsd:string">id</key><value xsi:type="xsd:int">126</value></item>',
    '<item><key xsi:type="xsd:string">zone</key><value xsi:type="xsd:int">42</value></item>',
    '<item><key xsi:type="xsd:string">type</key><value xsi:type="xsd:string">A</value></item>',
    '<item><key xsi:type="xsd:string">prefix</key><value xsi:type="xsd:string">*</value></item>',
    '<item><key xsi:type="xsd:string">target</key><value xsi:type="xsd:string">1.2.3.5</value></item>',
    '<item><key xsi:type="xsd:string">ttl</key><value xsi:type="xsd:int">3600</value></item>',
    '<item><key xsi:type="xsd:string">comment</key><value xsi:nil="true"/></item>',
    '<item><key xsi:type="xsd:string">priority</key><value xsi:nil="true"/></item>',
    '</item>',
    '<item xsi:type="ns2:Map">',
    '<item><key xsi:type="xsd:string">id</key><value xsi:type="xsd:int">127</value></item>',
    '<item><key xsi:type="xsd:string">zone</key><value xsi:type="xsd:int">42</value></item>',
    '<item><key xsi:type="xsd:string">type</key><value xsi:type="xsd:string">AAAA</value></item>',
    '<item><key xsi:type="xsd:string">prefix</key><value xsi:type="xsd:string"></value></item>',
    '<item><key xsi:type="xsd:string">target</key><value xsi:type="xsd:string">2001:1:2::3</value></item>',
    '<item><key xsi:type="xsd:string">ttl</key><value xsi:type="xsd:int">3600</value></item>',
    '<item><key xsi:type="xsd:string">comment</key><value xsi:nil="true"/></item>',
    '<item><key xsi:type="xsd:string">priority</key><value xsi:nil="true"/></item>',
    '</item>',
    '<item xsi:type="ns2:Map">',
    '<item><key xsi:type="xsd:string">id</key><value xsi:type="xsd:int">128</value></item>',
    '<item><key xsi:type="xsd:string">zone</key><value xsi:type="xsd:int">42</value></item>',
    '<item><key xsi:type="xsd:string">type</key><value xsi:type="xsd:string">AAAA</value></item>',
    '<item><key xsi:type="xsd:string">prefix</key><value xsi:type="xsd:string">*</value></item>',
    '<item><key xsi:type="xsd:string">target</key><value xsi:type="xsd:string">2001:1:2::4</value></item>',
    '<item><key xsi:type="xsd:string">ttl</key><value xsi:type="xsd:int">3600</value></item>',
    '<item><key xsi:type="xsd:string">comment</key><value xsi:nil="true"/></item>',
    '<item><key xsi:type="xsd:string">priority</key><value xsi:nil="true"/></item>',
    '</item>',
    '<item xsi:type="ns2:Map">',
    '<item><key xsi:type="xsd:string">id</key><value xsi:type="xsd:int">129</value></item>',
    '<item><key xsi:type="xsd:string">zone</key><value xsi:type="xsd:int">42</value></item>',
    '<item><key xsi:type="xsd:string">type</key><value xsi:type="xsd:string">MX</value></item>',
    '<item><key xsi:type="xsd:string">prefix</key><value xsi:type="xsd:string"></value></item>',
    '<item><key xsi:type="xsd:string">target</key><value xsi:type="xsd:string">example.com</value></item>',
    '<item><key xsi:type="xsd:string">ttl</key><value xsi:type="xsd:int">3600</value></item>',
    '<item><key xsi:type="xsd:string">comment</key><value xsi:nil="true"/></item>',
    '<item><key xsi:type="xsd:string">priority</key><value xsi:type="xsd:int">10</value></item>',
    '</item>',
    '<item xsi:type="ns2:Map">',
    '<item><key xsi:type="xsd:string">id</key><value xsi:type="xsd:int">130</value></item>',
    '<item><key xsi:type="xsd:string">zone</key><value xsi:type="xsd:int">42</value></item>',
    '<item><key xsi:type="xsd:string">type</key><value xsi:type="xsd:string">NS</value></item>',
    '<item><key xsi:type="xsd:string">prefix</key><value xsi:type="xsd:string"></value></item>',
    '<item><key xsi:type="xsd:string">target</key><value xsi:type="xsd:string">ns3.hostserv.eu</value></item>',
    '<item><key xsi:type="xsd:string">ttl</key><value xsi:type="xsd:int">10800</value></item>',
    '<item><key xsi:type="xsd:string">comment</key><value xsi:nil="true"/></item>',
    '<item><key xsi:type="xsd:string">priority</key><value xsi:nil="true"/></item>',
    '</item>',
    '<item xsi:type="ns2:Map">',
    '<item><key xsi:type="xsd:string">id</key><value xsi:type="xsd:int">131</value></item>',
    '<item><key xsi:type="xsd:string">zone</key><value xsi:type="xsd:int">42</value></item>',
    '<item><key xsi:type="xsd:string">type</key><value xsi:type="xsd:string">NS</value></item>',
    '<item><key xsi:type="xsd:string">prefix</key><value xsi:type="xsd:string"></value></item>',
    '<item><key xsi:type="xsd:string">target</key><value xsi:type="xsd:string">ns2.hostserv.eu</value></item>',
    '<item><key xsi:type="xsd:string">ttl</key><value xsi:type="xsd:int">10800</value></item>',
    '<item><key xsi:type="xsd:string">comment</key><value xsi:nil="true"/></item>',
    '<item><key xsi:type="xsd:string">priority</key><value xsi:nil="true"/></item>',
    '</item>',
    '<item xsi:type="ns2:Map">',
    '<item><key xsi:type="xsd:string">id</key><value xsi:type="xsd:int">132</value></item>',
    '<item><key xsi:type="xsd:string">zone</key><value xsi:type="xsd:int">42</value></item>',
    '<item><key xsi:type="xsd:string">type</key><value xsi:type="xsd:string">NS</value></item>',
    '<item><key xsi:type="xsd:string">prefix</key><value xsi:type="xsd:string"></value></item>',
    '<item><key xsi:type="xsd:string">target</key><value xsi:type="xsd:string">ns1.hostserv.eu</value></item>',
    '<item><key xsi:type="xsd:string">ttl</key><value xsi:type="xsd:int">10800</value></item>',
    '<item><key xsi:type="xsd:string">comment</key><value xsi:nil="true"/></item>',
    '<item><key xsi:type="xsd:string">priority</key><value xsi:nil="true"/></item>',
    '</item>',
    '</value>',
    '</item>',
    '</return>',
    '</ns1:getZoneResponse>',
    '</SOAP-ENV:Body>',
    '</SOAP-ENV:Envelope>'
])


class TestHosttechDNSRecordInfo(ModuleTestCase):
    def test_get_single(self):
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
            .result_str(GET_ALL_ZONES_ANSWER),
        ])
        with patch('ansible_collections.felixfontein.hosttech_dns.plugins.module_utils.wsdl.open_url', open_url):
            with pytest.raises(AnsibleExitJson) as e:
                set_module_args({
                    'hosttech_username': 'foo',
                    'hosttech_password': 'bar',
                    'zone': 'example.com',
                    'record': '*.example.com',
                    'type': 'A',
                    '_ansible_remote_tmp': '/tmp/tmp',
                    '_ansible_keep_remote_files': True,
                })
                hosttech_dns_record_info.main()

        print(e.value.args[0])
        assert e.value.args[0]['changed'] is False
        assert 'set' in e.value.args[0]
        assert e.value.args[0]['set']['record'] == '*.example.com'
        assert e.value.args[0]['set']['ttl'] == 3600
        assert e.value.args[0]['set']['type'] == 'A'
        assert e.value.args[0]['set']['value'] == ['1.2.3.5']
        assert 'sets' not in e.value.args[0]

    def test_get_all_of_type(self):
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
            .result_str(GET_ALL_ZONES_ANSWER),
        ])
        with patch('ansible_collections.felixfontein.hosttech_dns.plugins.module_utils.wsdl.open_url', open_url):
            with pytest.raises(AnsibleExitJson) as e:
                set_module_args({
                    'hosttech_username': 'foo',
                    'hosttech_password': 'bar',
                    'what': 'all_types_for_record',
                    'zone': 'example.com',
                    'record': '*.example.com',
                    '_ansible_remote_tmp': '/tmp/tmp',
                    '_ansible_keep_remote_files': True,
                })
                hosttech_dns_record_info.main()

        print(e.value.args[0])
        assert e.value.args[0]['changed'] is False
        assert 'set' not in e.value.args[0]
        assert 'sets' in e.value.args[0]
        sets = e.value.args[0]['sets']
        assert len(sets) == 2
        assert sets[0] == {
            'record': '*.example.com',
            'ttl': 3600,
            'type': 'A',
            'value': ['1.2.3.5'],
        }
        assert sets[1] == {
            'record': '*.example.com',
            'ttl': 3600,
            'type': 'AAAA',
            'value': ['2001:1:2::4'],
        }

    def test_get_all(self):
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
            .result_str(GET_ALL_ZONES_ANSWER),
        ])
        with patch('ansible_collections.felixfontein.hosttech_dns.plugins.module_utils.wsdl.open_url', open_url):
            with pytest.raises(AnsibleExitJson) as e:
                set_module_args({
                    'hosttech_username': 'foo',
                    'hosttech_password': 'bar',
                    'what': 'all_records',
                    'zone': 'example.com',
                    '_ansible_remote_tmp': '/tmp/tmp',
                    '_ansible_keep_remote_files': True,
                })
                hosttech_dns_record_info.main()

        print(e.value.args[0])
        assert e.value.args[0]['changed'] is False
        assert 'set' not in e.value.args[0]
        assert 'sets' in e.value.args[0]
        sets = e.value.args[0]['sets']
        assert len(sets) == 6
        assert sets[0] == {
            'record': '*.example.com',
            'ttl': 3600,
            'type': 'A',
            'value': ['1.2.3.5'],
        }
        assert sets[1] == {
            'record': '*.example.com',
            'ttl': 3600,
            'type': 'AAAA',
            'value': ['2001:1:2::4'],
        }
        assert sets[2] == {
            'record': 'example.com',
            'ttl': 3600,
            'type': 'A',
            'value': ['1.2.3.4'],
        }
        assert sets[3] == {
            'record': 'example.com',
            'ttl': 3600,
            'type': 'AAAA',
            'value': ['2001:1:2::3'],
        }
        assert sets[4] == {
            'record': 'example.com',
            'ttl': 3600,
            'type': 'MX',
            'value': ['example.com'],
        }
        assert sets[5] == {
            'record': 'example.com',
            'ttl': 10800,
            'type': 'NS',
            'value': ['ns3.hostserv.eu', 'ns2.hostserv.eu', 'ns1.hostserv.eu'],
        }
