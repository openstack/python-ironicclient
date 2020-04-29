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

import json

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
        self.assertEqual(node_info['driver'], self.driver_name)
        self.assertEqual(node_info['maintenance'], False)
        self.assertEqual(node_info['provision_state'], 'enroll')
        node_list = self.node_list()
        self.assertIn(uuid, [x['UUID'] for x in node_list])
        self.assertIn(name, [x['Name'] for x in node_list])

    def test_create_old_api_version(self):
        """Check baremetal node create command with name and UUID.

        Test steps:
        1) Create baremetal node in setUp.
        2) Create one more baremetal node explicitly with old API version
        3) Check that node successfully created.
        """
        node_info = self.node_create(
            params='--os-baremetal-api-version 1.5')
        self.assertEqual(node_info['driver'], self.driver_name)
        self.assertEqual(node_info['maintenance'], False)
        self.assertEqual(node_info['provision_state'], 'available')

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

    def test_baremetal_node_maintenance_set_unset(self):
        """Check baremetal node maintenance set command.

        Test steps:
        1) Create baremetal node in setUp.
        2) Check maintenance status of fresh node is False.
        3) Set maintenance status for node.
        4) Check maintenance status of node is True.
        5) Unset maintenance status for node.
        6) Check maintenance status of node is False back.
        """
        show_prop = self.node_show(self.node['name'], ['maintenance'])
        self.assertFalse(show_prop['maintenance'])

        self.openstack('baremetal node maintenance set {0}'.
                       format(self.node['name']))

        show_prop = self.node_show(self.node['name'], ['maintenance'])
        self.assertTrue(show_prop['maintenance'])

        self.openstack('baremetal node maintenance unset {0}'.
                       format(self.node['name']))

        show_prop = self.node_show(self.node['name'], ['maintenance'])
        self.assertFalse(show_prop['maintenance'])

    def test_baremetal_node_maintenance_set_unset_reason(self):
        """Check baremetal node maintenance set command.

        Test steps:
        1) Create baremetal node in setUp.
        2) Check initial maintenance reason is None.
        3) Set maintenance status for node with reason.
        4) Check maintenance reason of node equals to expected value.
           Also check maintenance status.
        5) Unset maintenance status for node. Recheck maintenance status.
        6) Check maintenance reason is None. Recheck maintenance status.
        """
        reason = "Hardware maintenance."
        show_prop = self.node_show(self.node['name'],
                                   ['maintenance_reason', 'maintenance'])
        self.assertIsNone(show_prop['maintenance_reason'])
        self.assertFalse(show_prop['maintenance'])

        self.openstack("baremetal node maintenance set --reason '{0}' {1}".
                       format(reason, self.node['name']))

        show_prop = self.node_show(self.node['name'],
                                   ['maintenance_reason', 'maintenance'])
        self.assertEqual(reason, show_prop['maintenance_reason'])
        self.assertTrue(show_prop['maintenance'])

        self.openstack('baremetal node maintenance unset {0}'.
                       format(self.node['name']))

        show_prop = self.node_show(self.node['name'],
                                   ['maintenance_reason', 'maintenance'])
        self.assertIsNone(show_prop['maintenance_reason'])
        self.assertFalse(show_prop['maintenance'])

    @ddt.data(
        (50, '1'),
        ('MAX', 'JBOD'),
        (300, '6+0')
    )
    @ddt.unpack
    def test_set_unset_target_raid_config(self, size, raid_level):
        """Set and unset node target RAID config data.

        Test steps:
        1) Create baremetal node in setUp.
        2) Set target RAID config data for the node
        3) Check target_raid_config of node equals to expected value.
        4) Unset target_raid_config data.
        5) Check that target_raid_config data is empty.
        """
        min_version = '--os-baremetal-api-version 1.12'
        argument_json = {"logical_disks":
                         [{"size_gb": size, "raid_level": raid_level}]}
        argument_string = json.dumps(argument_json)
        self.openstack("baremetal node set --target-raid-config '{}' {} {}"
                       .format(argument_string, self.node['uuid'],
                               min_version))

        show_prop = self.node_show(self.node['uuid'], ['target_raid_config'],
                                   min_version)
        self.assert_dict_is_subset(argument_json,
                                   show_prop['target_raid_config'])

        self.openstack("baremetal node unset --target-raid-config {} {}"
                       .format(self.node['uuid'], min_version))
        show_prop = self.node_show(self.node['uuid'], ['target_raid_config'],
                                   min_version)
        self.assertEqual({}, show_prop['target_raid_config'])
