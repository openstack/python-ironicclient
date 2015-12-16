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

from ironicclient.tests.functional import base


class NodeSetPowerStateTestIronicClient(base.FunctionalTestBase):
    """Tests for testing node-set-power-state command.

    Tests for the Ironic CLI node-set-power-state command that checks that
    node can be set to 'on', 'off' or 'reboot' power states
   """

    def setUp(self):
        super(NodeSetPowerStateTestIronicClient, self).setUp()
        self.node = self.create_node()
        node_power_state = self.show_node_states(self.node['uuid'])
        self.assertEqual('None', node_power_state['power_state'])

    def test_node_set_power_state_on(self):
        """Test steps:

        1) create node
        2) set node power state to 'on'
        3) check node power state has been set to 'on'
        """
        self.set_node_power_state(self.node['uuid'], 'on')
        node_state = self.show_node_states(self.node['uuid'])
        self.assertEqual('power on', node_state['power_state'])

    def test_node_set_power_state_off(self):
        """Test steps:

        1) create node
        2) set node power state to 'off'
        3) check node power state has been set to 'off'
        """
        self.set_node_power_state(self.node['uuid'], 'off')
        node_state = self.show_node_states(self.node['uuid'])
        self.assertEqual('power off', node_state['power_state'])

    def test_node_set_power_state_reboot_node_off(self):
        """Test steps:

        1) create node
        2) set node power state to 'off'
        3) check node power state has been set to 'off'
        4) set node power state to 'reboot'
        5) check node power state has been set to 'on'
        """
        self.set_node_power_state(self.node['uuid'], 'off')
        node_state = self.show_node_states(self.node['uuid'])

        self.assertEqual('power off', node_state['power_state'])

        self.set_node_power_state(self.node['uuid'], 'reboot')
        node_state = self.show_node_states(self.node['uuid'])

        self.assertEqual('power on', node_state['power_state'])

    def test_node_set_power_state_reboot_node_on(self):
        """Test steps:

        1) create node
        2) set node power state to 'on'
        3) check node power state has been set to 'on'
        4) set node power state to 'reboot'
        5) check node power state has been set to 'on'
        """
        self.set_node_power_state(self.node['uuid'], 'on')
        node_state = self.show_node_states(self.node['uuid'])

        self.assertEqual('power on', node_state['power_state'])

        self.set_node_power_state(self.node['uuid'], 'reboot')
        node_state = self.show_node_states(self.node['uuid'])

        self.assertEqual('power on', node_state['power_state'])
