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

import testtools

from ironicclient.tests import utils
import ironicclient.v1.chassis

CHASSIS = {'id': 42,
           'uuid': 'e74c40e0-d825-11e2-a28f-0800200c9a66',
           'extra': {},
           'description': 'data-center-1-chassis'}

fixtures = {
    '/v1/chassis':
    {
        'GET': (
            {},
            [CHASSIS],
        ),
    },
}


class ChassisManagerTest(testtools.TestCase):

    def setUp(self):
        super(ChassisManagerTest, self).setUp()
        self.api = utils.FakeAPI(fixtures)
        self.mgr = ironicclient.v1.chassis.ChassisManager(self.api)

    def test_list_all(self):
        chassis = list(self.mgr.list())
        expect = [
            ('GET', '/v1/chassis', {}, None),
        ]
        self.assertEqual(self.api.calls, expect)
        self.assertEqual(len(chassis), 1)
        self.assertEqual(chassis[0].description, 'data-center-1-chassis')
