#    Copyright (c) 2016 Mirantis, Inc.
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

import ddt

from tempest.lib.common.utils import data_utils

from ironicclient.tests.functional.osc.v1 import base


@ddt.ddt
class BaremetalPortGroupTests(base.TestCase):
    """Functional tests for baremetal port group commands."""

    def setUp(self):
        super(BaremetalPortGroupTests, self).setUp()
        self.node = self.node_create()
        self.api_version = ' --os-baremetal-api-version 1.25'
        self.port_group = self.port_group_create(self.node['uuid'],
                                                 params=self.api_version)

    def test_create_with_address(self):
        """Check baremetal port group create command with address argument.

        Test steps:
        1) Create baremetal port group in setUp.
        2) Create baremetal port group with specific address argument.
        3) Check address of created port group.
        """
        mac_address = data_utils.rand_mac_address()
        port_group = self.port_group_create(
            self.node['uuid'],
            params='{0} --address {1}'.format(self.api_version, mac_address))
        self.assertEqual(mac_address, port_group['address'])

    def test_list(self):
        """Check baremetal port group list command.

        Test steps:
        1) Create baremetal port group in setUp.
        2) List baremetal port groups.
        3) Check port group address, UUID and name in port groups list.
        """
        port_group_list = self.port_group_list(params=self.api_version)

        self.assertIn(self.port_group['uuid'],
                      [x['UUID'] for x in port_group_list])
        self.assertIn(self.port_group['name'],
                      [x['Name'] for x in port_group_list])

    @ddt.data('name', 'uuid')
    def test_delete(self, key):
        """Check baremetal port group delete command.

        Test steps:
        1) Create baremetal port group in setUp.
        2) Delete baremetal port group by UUID.
        3) Check that port group deleted successfully and not in list.
        """
        output = self.port_group_delete(self.port_group[key],
                                        params=self.api_version)
        self.assertEqual('Deleted port group {0}'
                         .format(self.port_group[key]), output.strip())

        port_group_list = self.port_group_list(params=self.api_version)

        self.assertNotIn(self.port_group['uuid'],
                         [x['UUID'] for x in port_group_list])
        self.assertNotIn(self.port_group['name'],
                         [x['Name'] for x in port_group_list])

    @ddt.data('name', 'uuid')
    def test_show(self, key):
        """Check baremetal port group show command.

        Test steps:
        1) Create baremetal port group in setUp.
        2) Show baremetal port group.
        3) Check name, uuid and address in port group show output.
        """
        port_group = self.port_group_show(
            self.port_group[key],
            ['name', 'uuid', 'address'],
            params=self.api_version)

        self.assertEqual(self.port_group['name'], port_group['name'])
        self.assertEqual(self.port_group['uuid'], port_group['uuid'])
        self.assertEqual(self.port_group['address'], port_group['address'])

    @ddt.data('name', 'uuid')
    def test_set_unset(self, key):
        """Check baremetal port group set and unset commands.

        Test steps:
        1) Create baremetal port group in setUp.
        2) Set extra data for port group.
        3) Check that baremetal port group extra data was set.
        4) Unset extra data for port group.
        5) Check that baremetal port group extra data was unset.
        """
        extra_key = 'ext'
        extra_value = 'testdata'
        self.openstack(
            'baremetal port group set --extra {0}={1} {2} {3}'
            .format(extra_key, extra_value, self.port_group[key],
                    self.api_version))

        show_prop = self.port_group_show(self.port_group[key], ['extra'],
                                         params=self.api_version)
        self.assertEqual(extra_value, show_prop['extra'][extra_key])

        self.openstack('baremetal port group unset --extra {0} {1} {2}'
                       .format(extra_key, self.port_group[key],
                               self.api_version))

        show_prop = self.port_group_show(self.port_group[key], ['extra'],
                                         params=self.api_version)
        self.assertNotIn(extra_key, show_prop['extra'])
