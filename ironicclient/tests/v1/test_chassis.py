# -*- encoding: utf-8 -*-
#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

CREATE_CHASSIS = copy.deepcopy(CHASSIS)
del CREATE_CHASSIS['id']
del CREATE_CHASSIS['uuid']

fixtures = {
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
    },
}


class ChassisManagerTest(testtools.TestCase):

    def setUp(self):
        super(ChassisManagerTest, self).setUp()
        self.api = utils.FakeAPI(fixtures)
        self.mgr = ironicclient.v1.chassis.ChassisManager(self.api)

    def test_chassis_list(self):
        chassis = self.mgr.list()
        expect = [
            ('GET', '/v1/chassis', {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(len(chassis), 1)

    def test_chassis_show(self):
        chassis = self.mgr.get(CHASSIS['uuid'])
        expect = [
            ('GET', '/v1/chassis/%s' % CHASSIS['uuid'], {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(chassis.uuid, CHASSIS['uuid'])
        self.assertEqual(chassis.description, CHASSIS['description'])

    def test_create(self):
        chassis = self.mgr.create(**CREATE_CHASSIS)
        expect = [
            ('POST', '/v1/chassis', {}, CREATE_CHASSIS),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertTrue(chassis)

    def test_delete(self):
        chassis = self.mgr.delete(chassis_id=CHASSIS['uuid'])
        expect = [
            ('DELETE', '/v1/chassis/%s' % CHASSIS['uuid'], {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertTrue(chassis is None)
