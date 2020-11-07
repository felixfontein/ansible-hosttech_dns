# -*- coding: utf-8 -*-
#
# Copyright (c) 2017-2020 Felix Fontein
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


import sys
import pytest

lxmletree = pytest.importorskip("lxml.etree")

from ansible.module_utils._text import to_native

from ansible_collections.felixfontein.hosttech_dns.plugins.module_utils.wsdl import (
    Composer,
)


def test_composer_generation():
    composer = Composer(api='https://example.com/api')
    composer.add_simple_command(
        'test',
        int_value=42,
        str_value='bar',
        list_value=[1, 2, 3],
        dict_value={
            'hello': 'world',
            'list': [2, 3, 5, 7],
        }
    )
    command = to_native(lxmletree.tostring(composer._root, pretty_print=True)).splitlines()

    print(command)

    expected_lines = [
        '  <SOAP-ENV:Header/>',
        '  <SOAP-ENV:Body>',
        '    <ns0:test xmlns:ns0="https://example.com/api">',
        '      <int_value xsi:type="xsd:int">42</int_value>',
        '      <str_value xsi:type="xsd:string">bar</str_value>',
        '      <list_value xsi:type="SOAP-ENC:Array">',
        '        <item xsi:type="xsd:int">1</item>',
        '        <item xsi:type="xsd:int">2</item>',
        '        <item xsi:type="xsd:int">3</item>',
        '      </list_value>',
        '      <dict_value xmlns:ns0="http://xml.apache.org/xml-soap" xsi:type="ns0:Map">',
        '        <item>',
        '          <key xsi:type="xsd:string">hello</key>',
        '          <value xsi:type="xsd:string">world</value>',
        '        </item>',
        '        <item>',
        '          <key xsi:type="xsd:string">list</key>',
        '          <value xsi:type="SOAP-ENC:Array">',
        '            <item xsi:type="xsd:int">2</item>',
        '            <item xsi:type="xsd:int">3</item>',
        '            <item xsi:type="xsd:int">5</item>',
        '            <item xsi:type="xsd:int">7</item>',
        '          </value>',
        '        </item>',
        '      </dict_value>',
        '    </ns0:test>',
        '  </SOAP-ENV:Body>',
        '</SOAP-ENV:Envelope>',
    ]

    if sys.version_info < (3, 7):
        assert sorted(command[1:]) == sorted(expected_lines)
    else:
        assert command[1:] == expected_lines

    for part in [
            '<SOAP-ENV:Envelope',
            ' xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"',
            ' xmlns:xsd="http://www.w3.org/2001/XMLSchema"',
            ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
            ' xmlns:ns2="auth"',
            ' xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"',
            ' SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"',
    ]:
        assert part in command[0]
