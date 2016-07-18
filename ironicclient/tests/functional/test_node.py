# Copyright (c) 2015 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from tempest.lib.common.utils import data_utils

from ironicclient.tests.functional import base
import ironicclient.tests.functional.utils as utils


class NodeSanityTestIronicClient(base.FunctionalTestBase):
    """Sanity tests for testing actions with Node.

    Smoke test for the Ironic CLI commands which checks basic actions with
    node command like create, delete etc.
    """

    def setUp(self):
        super(NodeSanityTestIronicClient, self).setUp()
        self.node = self.create_node()

    def test_node_create(self):
        """Test steps:

        1) create node
        2) check that node has been successfully created
        """
        self.assertIn(self.node['uuid'], self.get_nodes_uuids_from_node_list())

    def test_node_show(self):
        """Test steps:

        1) create node
        2) check that created node UUID equals to the one present
        in node-show output
        """
        node_show = self.show_node(self.node['uuid'])
        self.assertEqual(self.node['uuid'], node_show['uuid'])

    def test_node_show_field(self):
        """Test steps:

        1) create node
        2) show node with fields instance_uuid, driver, name, uuid
        3) check that only fields instance_uuid, driver, name,
        uuid are the output fields
        """
        fields = ['instance_uuid', 'driver', 'name', 'uuid']
        node_show = self.show_node(self.node['uuid'],
                                   params='--fields %s' % ' '.join(fields))
        self.assertTableHeaders(fields, node_show.keys())

    def test_node_delete(self):
        """Test steps:

        1) create node
        2) check that it was created
        3) delete node
        4) check that node has been successfully deleted
        """
        self.assertIn(self.node['uuid'], self.get_nodes_uuids_from_node_list())
        self.delete_node(self.node['uuid'])
        self.assertNotIn(self.node['uuid'],
                         self.get_nodes_uuids_from_node_list())

    def test_node_update(self):
        """Test steps:

        1) create node
        2) update node name
        3) check that node name has been successfully updated
        """
        node_name = data_utils.rand_name(prefix='test')
        updated_node = self.update_node(self.node['uuid'],
                                        'add name={0}'.format(node_name))
        self.assertEqual(node_name, updated_node['name'])

    def test_node_set_console_mode(self):
        """Test steps:

        1) create node
        2) check that console_enabled is False
        3) set node console mode to True
        4) check that node console mode has been successfully updated
        """
        node_show = self.show_node(self.node['uuid'])

        self.assertEqual('False', node_show['console_enabled'])

        self.ironic('node-set-console-mode',
                    params='{0} true'.format(self.node['uuid']))
        node_show = self.show_node(self.node['uuid'])

        self.assertEqual('True', node_show['console_enabled'])

    def test_node_get_console(self):
        """Test steps:

        1) create node
        2) check console mode using node-show
        3) get console mode using node-get-console
        4) check that node-get-console value equals node-show value
        """
        node_show = self.show_node(self.node['uuid'])
        node_get = self.ironic('node-get-console', params=self.node['uuid'])
        node_get = utils.get_dict_from_output(node_get)

        self.assertEqual(node_show['console_enabled'],
                         node_get['console_enabled'])

    def test_node_set_maintenance(self):
        """Test steps:

        1) create node
        2) check that maintenance is False
        3) put node to maintenance
        4) check that node is in maintenance
        5) check that maintenance reason has been successfully updated
        """
        node_show = self.show_node(self.node['uuid'])

        self.assertEqual('False', node_show['maintenance'])

        self.set_node_maintenance(
            self.node['uuid'],
            "true --reason 'Testing node-set power state command'")
        node_show = self.show_node(self.node['uuid'])

        self.assertEqual('True', node_show['maintenance'])
        self.assertEqual('Testing node-set power state command',
                         node_show['maintenance_reason'])

    def test_node_set_power_state(self):
        """Test steps:

        1) create node
        2) check that power state is None
        3) set power state to 'off'
        4) check that power state has been changed successfully
        """
        node_show = self.show_node(self.node['uuid'])

        self.assertEqual('None', node_show['power_state'])

        self.set_node_power_state(self.node['uuid'], "off")
        node_show = self.show_node(self.node['uuid'])

        self.assertEqual('power off', node_show['power_state'])

    def test_node_set_provision_state(self):
        """Test steps:

        1) create node
        2) check that provision state is 'available'
        3) set new provision state to the node
        4) check that provision state has been updated successfully
        """
        node_show = self.show_node(self.node['uuid'])

        self.assertEqual('available', node_show['provision_state'])

        self.set_node_provision_state(self.node['uuid'], 'active')
        node_show = self.show_node(self.node['uuid'])

        self.assertEqual('active', node_show['provision_state'])

    def test_node_validate(self):
        """Test steps:

        1) create node
        2) validate node
        """
        node_validate = self.validate_node(self.node['uuid'])
        self.assertNodeValidate(node_validate)

    def test_show_node_states(self):
        """Test steps:

        1) create node
        2) check that states returned by node-show and node-show-states
        are the same
        """
        node_show = self.show_node(self.node['uuid'])
        show_node_states = self.show_node_states(self.node['uuid'])
        self.assertNodeStates(node_show, show_node_states)

    def test_node_list(self):
        """Test steps:

            1) create node in setup and one more node explicitly
            2) check that both nodes are in list
        """
        other_node = self.create_node()
        node_list = self.list_nodes()
        uuids = [x['UUID'] for x in node_list]
        names = [x['Name'] for x in node_list]
        self.assertIn(self.node['uuid'], uuids)
        self.assertIn(other_node['uuid'], uuids)
        self.assertIn(self.node['name'], names)
        self.assertIn(other_node['name'], names)
