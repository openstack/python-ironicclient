# -*- encoding: utf-8 -*-
#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2013 Hewlett-Packard Development Company, L.P.
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
import ironicclient.v1.node
from testtools.matchers import HasLength

NODE1 = {'id': 123,
        'uuid': '66666666-7777-8888-9999-000000000000',
        'chassis_id': 42,
        'driver': 'fake',
        'driver_info': {'user': 'foo', 'password': 'bar'},
        'properties': {'num_cpu': 4},
        'extra': {}}
NODE2 = {'id': 456,
        'uuid': '66666666-7777-8888-9999-111111111111',
        'instance_uuid': '66666666-7777-8888-9999-222222222222',
        'chassis_id': 42,
        'driver': 'fake too',
        'driver_info': {'user': 'foo', 'password': 'bar'},
        'properties': {'num_cpu': 4},
        'extra': {}}
PORT = {'id': 456,
        'uuid': '11111111-2222-3333-4444-555555555555',
        'node_id': 123,
        'address': 'AA:AA:AA:AA:AA:AA',
        'extra': {}}

POWER_STATE = {'current': 'power off',
               'target': 'power on'}

DRIVER_IFACES = {'power': True, 'deploy': True,
                 'console': 'not supported',
                 'rescue': 'not supported'}

CREATE_NODE = copy.deepcopy(NODE1)
del CREATE_NODE['id']
del CREATE_NODE['uuid']

UPDATED_NODE = copy.deepcopy(NODE1)
NEW_DRIVER = 'new-driver'
UPDATED_NODE['driver'] = NEW_DRIVER

fake_responses = {
    '/v1/nodes':
    {
        'GET': (
            {},
            {"nodes": [NODE1, NODE2]},
        ),
        'POST': (
            {},
            CREATE_NODE,
        ),
    },
    '/v1/nodes/?associated=False':
    {
        'GET': (
            {},
            {"nodes": [NODE1]},
        )
    },
    '/v1/nodes/?associated=True':
    {
        'GET': (
            {},
            {"nodes": [NODE2]},
        )
    },
    '/v1/nodes/?instance_uuid=%s' % NODE2['instance_uuid']:
    {
        'GET': (
            {},
            {"nodes": [NODE2]},
        )
    },
    '/v1/nodes/%s' % NODE1['uuid']:
    {
        'GET': (
            {},
            NODE1,
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_NODE,
        ),
    },
    '/v1/nodes/%s' % NODE2['uuid']:
    {
        'GET': (
            {},
            NODE2,
        ),
    },
    '/v1/nodes/%s/ports' % NODE1['uuid']:
    {
        'GET': (
            {},
            {"ports": [PORT]},
        ),
    },
    '/v1/nodes/%s/state/power' % NODE1['uuid']:
    {
        'PUT': (
            {},
            POWER_STATE,
        ),
    },
    '/v1/nodes/%s/validate' % NODE1['uuid']:
    {
        'GET': (
            {},
            DRIVER_IFACES,
        ),
    },
}


class NodeManagerTest(testtools.TestCase):

    def setUp(self):
        super(NodeManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = ironicclient.v1.node.NodeManager(self.api)

    def test_node_list(self):
        nodes = self.mgr.list()
        expect = [
            ('GET', '/v1/nodes', {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(len(nodes), 2)

    def test_node_list_associated(self):
        nodes = self.mgr.list(associated=True)
        expect = [
            ('GET', '/v1/nodes/?associated=True', {}, None),
        ]
        self.assertEqual(expect, self.api.calls, )
        self.assertThat(nodes, HasLength(1))
        self.assertEqual(NODE2['uuid'], getattr(nodes[0], 'uuid'))

    def test_node_list_unassociated(self):
        nodes = self.mgr.list(associated=False)
        expect = [
            ('GET', '/v1/nodes/?associated=False', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(nodes, HasLength(1))
        self.assertEqual(NODE1['uuid'], getattr(nodes[0], 'uuid'))

    def test_node_show(self):
        node = self.mgr.get(NODE1['uuid'])
        expect = [
            ('GET', '/v1/nodes/%s' % NODE1['uuid'], {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(node.uuid, NODE1['uuid'])

    def test_node_show_by_instance(self):
        node = self.mgr.get_by_instance_uuid(NODE2['instance_uuid'])
        expect = [
            ('GET', '/v1/nodes/?instance_uuid=%s' % NODE2['instance_uuid'],
                     {}, None),
            ('GET', '/v1/nodes/%s' % NODE2['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NODE2['uuid'], node.uuid)

    def test_create(self):
        node = self.mgr.create(**CREATE_NODE)
        expect = [
            ('POST', '/v1/nodes', {}, CREATE_NODE),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertTrue(node)

    def test_delete(self):
        node = self.mgr.delete(node_id=NODE1['uuid'])
        expect = [
            ('DELETE', '/v1/nodes/%s' % NODE1['uuid'], {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertTrue(node is None)

    def test_update(self):
        patch = {'op': 'replace',
                 'value': NEW_DRIVER,
                 'path': '/driver'}
        node = self.mgr.update(node_id=NODE1['uuid'], patch=patch)
        expect = [
            ('PATCH', '/v1/nodes/%s' % NODE1['uuid'], {}, patch),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(node.driver, NEW_DRIVER)

    def test_node_port_list(self):
        ports = self.mgr.list_ports(NODE1['uuid'])
        expect = [
            ('GET', '/v1/nodes/%s/ports' % NODE1['uuid'], {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(len(ports), 1)
        self.assertEqual(ports[0].uuid, PORT['uuid'])
        self.assertEqual(ports[0].address, PORT['address'])

    def test_node_set_power_state(self):
        power_state = self.mgr.set_power_state(NODE1['uuid'], "on")
        body = {'target': 'power on'}
        expect = [
            ('PUT', '/v1/nodes/%s/state/power' % NODE1['uuid'], {}, body),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual('power on', power_state.target)

    def test_node_validate(self):
        ifaces = self.mgr.validate(NODE1['uuid'])
        expect = [
            ('GET', '/v1/nodes/%s/validate' % NODE1['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(DRIVER_IFACES['power'], ifaces.power)
        self.assertEqual(DRIVER_IFACES['deploy'], ifaces.deploy)
        self.assertEqual(DRIVER_IFACES['rescue'], ifaces.rescue)
        self.assertEqual(DRIVER_IFACES['console'], ifaces.console)
