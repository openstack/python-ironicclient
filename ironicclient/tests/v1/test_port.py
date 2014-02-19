# -*- encoding: utf-8 -*-

# Copyright 2013 Red Hat, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import copy

import testtools

from ironicclient.tests import utils
import ironicclient.v1.port

PORT = {'id': 987,
        'uuid': '11111111-2222-3333-4444-555555555555',
        'node_uuid': '55555555-4444-3333-2222-111111111111',
        'address': 'AA:BB:CC:DD:EE:FF',
        'extra': {}}

CREATE_PORT = copy.deepcopy(PORT)
del CREATE_PORT['id']
del CREATE_PORT['uuid']

UPDATED_PORT = copy.deepcopy(PORT)
NEW_ADDR = 'AA:AA:AA:AA:AA:AA'
UPDATED_PORT['address'] = NEW_ADDR

fake_responses = {
    '/v1/ports':
    {
        'GET': (
            {},
            {"ports": [PORT]},
        ),
        'POST': (
            {},
            CREATE_PORT,
        ),
    },
    '/v1/ports/%s' % PORT['uuid']:
    {
        'GET': (
            {},
            PORT,
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_PORT,
        ),
    },
}


class PortManagerTest(testtools.TestCase):

    def setUp(self):
        super(PortManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = ironicclient.v1.port.PortManager(self.api)

    def test_ports_list(self):
        ports = self.mgr.list()
        expect = [
            ('GET', '/v1/ports', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(ports))

    def test_ports_show(self):
        port = self.mgr.get(PORT['uuid'])
        expect = [
            ('GET', '/v1/ports/%s' % PORT['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(PORT['uuid'], port.uuid)
        self.assertEqual(PORT['address'], port.address)
        self.assertEqual(PORT['node_uuid'], port.node_uuid)

    def test_create(self):
        port = self.mgr.create(**CREATE_PORT)
        expect = [
            ('POST', '/v1/ports', {}, CREATE_PORT),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(port)

    def test_delete(self):
        port = self.mgr.delete(port_id=PORT['uuid'])
        expect = [
            ('DELETE', '/v1/ports/%s' % PORT['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(port is None)

    def test_update(self):
        patch = {'op': 'replace',
                 'value': NEW_ADDR,
                 'path': '/address'}
        port = self.mgr.update(port_id=PORT['uuid'], patch=patch)
        expect = [
            ('PATCH', '/v1/ports/%s' % PORT['uuid'], {}, patch),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NEW_ADDR, port.address)
