# -*- coding: utf-8 -*-
#
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

import mock
import testtools
from testtools import matchers

from ironicclient.common import base
from ironicclient.tests import utils
import ironicclient.v1.driver


DRIVER1 = {'name': 'fake', 'hosts': ['fake-host1', 'fake-host2']}
DRIVER2 = {'name': 'pxe_ipminative', 'hosts': ['fake-host1', 'fake-host2']}

DRIVER2_PROPERTIES = {
  "username": "username. Required.",
  "password": "password. Optional.",
  "address": "IP of the node. Required.",
}

fake_responses = {
    '/v1/drivers':
    {
        'GET': (
            {},
            {'drivers': [DRIVER1]},
        ),
    },
    '/v1/drivers/%s' % DRIVER1['name']:
    {
        'GET': (
            {},
            DRIVER1
        ),
    },
    '/v1/drivers/%s/properties' % DRIVER2['name']:
    {
        'GET': (
            {},
            DRIVER2_PROPERTIES,
        ),
    }
}


class DriverManagerTest(testtools.TestCase):

    def setUp(self):
        super(DriverManagerTest, self).setUp()
        self.api = utils.FakeAPI(fake_responses)
        self.mgr = ironicclient.v1.driver.DriverManager(self.api)

    def test_driver_list(self):
        drivers = self.mgr.list()
        expect = [
            ('GET', '/v1/drivers', {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertThat(drivers, matchers.HasLength(1))

    def test_driver_show(self):
        driver = self.mgr.get(DRIVER1['name'])
        expect = [
            ('GET', '/v1/drivers/%s' % DRIVER1['name'], {}, None)
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(DRIVER1['name'], driver.name)
        self.assertEqual(DRIVER1['hosts'], driver.hosts)

    def test_driver_properties(self):
        properties = self.mgr.properties(DRIVER2['name'])
        expect = [
            ('GET', '/v1/drivers/%s/properties' % DRIVER2['name'], {}, None),
        ]
        self.assertEqual(expect, self.api.calls)
        self.assertEqual(DRIVER2_PROPERTIES, properties)

    @mock.patch.object(base.Manager, '_update')
    def test_vendor_passthru(self, update_mock):
        # For now just mock the tests because vendor-passthru doesn't return
        # anything to verify.
        vendor_passthru_args = {'arg1': 'val1'}
        kwargs = {
                  'driver_name': 'driver_name',
                  'method': 'method',
                  'args': vendor_passthru_args
                 }
        self.mgr.vendor_passthru(**kwargs)

        final_path = '/v1/drivers/driver_name/vendor_passthru/method'
        update_mock.assert_once_called_with(final_path,
                                            vendor_passthru_args,
                                            method='POST')
