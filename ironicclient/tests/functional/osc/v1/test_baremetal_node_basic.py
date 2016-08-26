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
class BaremetalNodeTests(base.TestCase):
    """Functional tests for baremetal node commands."""

    def setUp(self):
        super(BaremetalNodeTests, self).setUp()
        self.node = self.node_create()

    def test_create_name_uuid(self):
        """Check baremetal node create command with name and UUID.

        Test steps:
        1) Create baremetal node in setUp.
        2) Create one more baremetal node explicitly
        with specified name and UUID.
        3) Check that node successfully created.
        """
        uuid = data_utils.rand_uuid()
        name = data_utils.rand_name('baremetal-node')
        node_info = self.node_create(name=name,
                                     params='--uuid {0}'.format(uuid))
        self.assertEqual(node_info['uuid'], uuid)
        self.assertEqual(node_info['name'], name)
        self.assertEqual(node_info['driver'], 'fake')
        self.assertEqual(node_info['maintenance'], False)
        node_list = self.node_list()
        self.assertIn(uuid, [x['UUID'] for x in node_list])
        self.assertIn(name, [x['Name'] for x in node_list])

    @ddt.data('name', 'uuid')
    def test_delete(self, key):
        """Check baremetal node delete command with name/UUID argument.

        Test steps:
        1) Create baremetal node in setUp.
        2) Delete baremetal node by name/UUID.
        3) Check that node deleted successfully.
        """
        output = self.node_delete(self.node[key])
        self.assertIn('Deleted node {0}'.format(self.node[key]), output)
        node_list = self.node_list()
        self.assertNotIn(self.node['name'], [x['Name'] for x in node_list])
        self.assertNotIn(self.node['uuid'], [x['UUID'] for x in node_list])

    def test_list(self):
        """Check baremetal node list command.

        Test steps:
        1) Create baremetal node in setUp.
        2) List baremetal nodes.
        3) Check node name in nodes list.
        """
        node_list = self.node_list()
        self.assertIn(self.node['name'], [x['Name'] for x in node_list])
        self.assertIn(self.node['uuid'], [x['UUID'] for x in node_list])

    @ddt.data('name', 'uuid')
    def test_set(self, key):
        """Check baremetal node set command calling it by name/UUID.

        Test steps:
        1) Create baremetal node in setUp.
        2) Set another name for node calling it by name/UUID.
        3) Check that baremetal node name was changed.
        """
        new_name = data_utils.rand_name('newnodename')
        self.openstack('baremetal node set --name {0} {1}'
                       .format(new_name, self.node[key]))
        show_prop = self.node_show(self.node['uuid'], ['name'])
        self.assertEqual(new_name, show_prop['name'])

    @ddt.data('name', 'uuid')
    def test_unset(self, key):
        """Check baremetal node unset command calling it by node name/UUID.

        Test steps:
        1) Create baremetal node in setUp.
        2) Unset name of baremetal node calling it by node name/UUID.
        3) Check that node has no more name.
        """
        self.openstack('baremetal node unset --name {0}'
                       .format(self.node[key]))
        show_prop = self.node_show(self.node['uuid'], ['name'])
        self.assertIsNone(show_prop['name'])

    @ddt.data('name', 'uuid')
    def test_show(self, key):
        """Check baremetal node show command with name and UUID arguments.

        Test steps:
        1) Create baremetal node in setUp.
        2) Show baremetal node calling it with name and UUID arguments.
        3) Check name, uuid and driver in node show output.
        """
        node = self.node_show(self.node[key],
                              ['name', 'uuid', 'driver'])
        self.assertEqual(self.node['name'], node['name'])
        self.assertEqual(self.node['uuid'], node['uuid'])
        self.assertEqual(self.node['driver'], node['driver'])
