# -*- coding: utf-8 -*-

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
import ironicclient.v1.chassis

CHASSIS = {'id': 42,
           'uuid': 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee',
           'extra': {},
           'description': 'data-center-1-chassis'}

NODE = {'id': 123,
        'uuid': '66666666-7777-8888-9999-000000000000',
        'chassis_id': 42,
        'driver': 'fake',
        'driver_info': {'user': 'foo', 'password': 'bar'},
        'properties': {'num_cpu': 4},
        'extra': {}}

CREATE_CHASSIS = copy.deepcopy(CHASSIS)
del CREATE_CHASSIS['id']
del CREATE_CHASSIS['uuid']

UPDATED_CHASSIS = copy.deepcopy(CHASSIS)
NEW_DESCR = 'new-description'
UPDATED_CHASSIS['description'] = NEW_DESCR

fake_responses = {
    '/v1/chassis':
    {
        'GET': (
            {},
            {"chassis": [CHASSIS]},
        ),
        'POST': (
            {},
            CREATE_CHASSIS,
        ),
    },
    '/v1/chassis/%s' % CHASSIS['uuid']:
    {
        'GET': (
            {},
            CHASSIS,
        ),
        'DELETE': (
            {},
            None,
        ),
        'PATCH': (
            {},
            UPDATED_CHASSIS,
        ),
    },
    '/v1/chassis/%s/nodes' % CHASSIS['uuid']:
    {
        'GET': (
            {},
            {"nodes": [NODE]},
        ),
    },
}


class ChassisManagerTest(testtools.TestCase):

    def setUp(self):
        super(ChassisManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = ironicclient.v1.chassis.ChassisManager(self.api)

    def test_chassis_list(self):
        chassis = self.mgr.list()
        expect = [
            ('GET', '/v1/chassis', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(chassis))

    def test_chassis_show(self):
        chassis = self.mgr.get(CHASSIS['uuid'])
        expect = [
            ('GET', '/v1/chassis/%s' % CHASSIS['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(CHASSIS['uuid'], chassis.uuid)
        self.assertEqual(CHASSIS['description'], chassis.description)

    def test_create(self):
        chassis = self.mgr.create(**CREATE_CHASSIS)
        expect = [
            ('POST', '/v1/chassis', {}, CREATE_CHASSIS),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertTrue(chassis)

    def test_delete(self):
        chassis = self.mgr.delete(chassis_id=CHASSIS['uuid'])
        expect = [
            ('DELETE', '/v1/chassis/%s' % CHASSIS['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertIsNone(chassis)

    def test_update(self):
        patch = {'op': 'replace',
                 'value': NEW_DESCR,
                 'path': '/description'}
        chassis = self.mgr.update(chassis_id=CHASSIS['uuid'], patch=patch)
        expect = [
            ('PATCH', '/v1/chassis/%s' % CHASSIS['uuid'], {}, patch),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(NEW_DESCR, chassis.description)

    def test_chassis_node_list(self):
        nodes = self.mgr.list_nodes(CHASSIS['uuid'])
        expect = [
            ('GET', '/v1/chassis/%s/nodes' % CHASSIS['uuid'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(1, len(nodes))
        self.assertEqual(NODE['uuid'], nodes[0].uuid)
