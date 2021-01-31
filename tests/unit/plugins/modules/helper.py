# (c) 2021 Felix Fontein <felix@fontein.de>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

try:
    import lxml.etree
except ImportError:
    # should be handled in module importing this one
    pass


def validate_wsdl_call(conditions):
    def predicate(content):
        assert content.startswith(b"<?xml version='1.0' encoding='utf-8'?>\n")

        root = lxml.etree.fromstring(content)
        header = None
        body = None

        for header_ in root.iter(lxml.etree.QName('http://schemas.xmlsoap.org/soap/envelope/', 'Header').text):
            header = header_
        for body_ in root.iter(lxml.etree.QName('http://schemas.xmlsoap.org/soap/envelope/', 'Body').text):
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
        auth = get_value(header, lxml.etree.QName('auth', 'authenticate').text)
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
            type_text = node.get(lxml.etree.QName('http://www.w3.org/2001/XMLSchema-instance', 'type'))
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
