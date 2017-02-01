# Copyright (c) 2016 Mirantis, Inc.
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


class PortGroupSanityTest(base.FunctionalTestBase):
    """Sanity tests for testing actions with port groups.

    Smoke test for the Ironic CLI port group subcommands:
    create, show, update, delete, list, port-list.
    """
    def setUp(self):
        super(PortGroupSanityTest, self).setUp()
        self.node = self.create_node()
        self.port_group = self.create_portgroup(self.node['uuid'])

    def test_portgroup_create(self):
        """Test steps:

        1) Create node and port group in setUp().
        2) Check that port group has been successfully created.
        """
        portgroup_list_uuid = self.get_portgroup_uuids_from_portgroup_list()
        self.assertIn(self.port_group['uuid'], portgroup_list_uuid)

    def test_portgroup_delete(self):
        """Test steps:

        1) Create node and port group in setUp().
        2) Delete port group.
        3) Check that port group has been successfully deleted.
        """
        self.delete_portgroup(self.port_group['uuid'])
        portgroup_list_uuid = self.get_portgroup_uuids_from_portgroup_list()
        self.assertNotIn(self.port_group['uuid'], portgroup_list_uuid)

    def test_portgroup_show(self):
        """Test steps:

        1) Create node and port group in setUp().
        2) Check that portgroup-show returns the same UUID as portgroup-create.
        """
        portgroup_show = self.show_portgroup(self.port_group['uuid'])
        self.assertEqual(self.port_group['uuid'], portgroup_show['uuid'])
        self.assertEqual(self.port_group['name'], portgroup_show['name'])

    def test_portgroup_list(self):
        """Test steps:

        1) Create node and port group in setUp().
        2) Create one more node and port group.
        3) Check that portgroup-list contains UUIDs
           of all created port groups.
        """
        other_node = self.create_node()
        other_portgroup = self.create_portgroup(other_node['uuid'])

        uuids = {x['UUID'] for x in self.list_portgroups()}

        self.assertTrue({self.port_group['uuid'],
                         other_portgroup['uuid']}.issubset(uuids))

    def test_portgroup_update(self):
        """Test steps:

        1) Create node and port group in setUp().
        2) Create node to replace.
        3) Set new node to maintenance.
        4) Update port group by replacing node.
        5) Check that port group has been successfully updated.
        """
        node_to_replace = self.create_node()
        self.set_node_maintenance(node_to_replace['uuid'], True)
        updated_portgroup = self.update_portgroup(
            self.port_group['uuid'], 'replace', params='node_uuid={0}'
                .format(node_to_replace['uuid'])
        )
        self.assertEqual(node_to_replace['uuid'],
                         updated_portgroup['node_uuid'])
        self.assertNotEqual(self.port_group['node_uuid'],
                            updated_portgroup['node_uuid'])

    def test_portgroup_port_list(self):
        """Test steps:

        1) Create node and port group in setUp().
        2) Create a port.
        3) Set node to maintenance.
        4) Attach port to the port group.
        5) List the ports associated with a port group.
        6) Check port UUID in list.
        7) Check port address in list.
        """
        port = self.create_port(self.node['uuid'])
        self.set_node_maintenance(self.node['uuid'], True)
        self.update_port(port['uuid'], 'replace',
                         flags='--ironic-api-version 1.25',
                         params='portgroup_uuid={0}'
                         .format(self.port_group['uuid']))
        pg_port_list = self.portgroup_port_list(self.port_group['uuid'])
        self.assertIn(port['uuid'], [x['UUID'] for x in pg_port_list])
        self.assertIn(port['address'], [x['Address'] for x in pg_port_list])
