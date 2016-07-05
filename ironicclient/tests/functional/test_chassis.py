#  Copyright (c) 2016 Mirantis, Inc.
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

import six
from tempest.lib.common.utils import data_utils
from tempest.lib import exceptions

from ironicclient.tests.functional import base


class ChassisSanityTestIronicClient(base.FunctionalTestBase):
    """Sanity tests for testing actions with Chassis.

    Smoke test for the Ironic CLI commands which checks basic actions with
    chassis command like create, show, update, delete etc.
    """
    def setUp(self):
        super(ChassisSanityTestIronicClient, self).setUp()
        self.chassis = self.create_chassis()

    def test_chassis_create(self):
        """Test steps:

        1) create chassis
        2) check that chassis has been successfully created
        """
        chassis_list_uuid = self.get_chassis_uuids_from_chassis_list()
        self.assertIn(self.chassis['uuid'], chassis_list_uuid)

    def test_chassis_delete(self):
        """Test steps:

        1) create chassis
        2) check that chassis has been successfully created
        3) delete chassis
        4) check that chassis has been successfully deleted
        """
        self.delete_chassis(self.chassis['uuid'])
        chassis_list_uuid = self.get_chassis_uuids_from_chassis_list()

        self.assertNotIn(self.chassis['uuid'], chassis_list_uuid)

    def test_chassis_show(self):
        """Test steps:

        1) create chassis
        2) check that chassis-show returns the same chassis UUID
        3) chassis-create
        """
        chassis_show = self.show_chassis(self.chassis['uuid'])
        self.assertEqual(self.chassis['uuid'], chassis_show['uuid'])

    def test_chassis_show_field(self):
        """Test steps:

        1) create chassis
        2) show chassis with fields uuid
        3) check that fields is exist
        """
        fields = ['uuid']
        chassis_show = self.show_chassis(self.chassis['uuid'],
                                         params='--fields {0}'
                                         .format(*fields))
        self.assertTableHeaders(fields, chassis_show.keys())

    def test_chassis_update(self):
        """Test steps:

        1) create chassis
        2) update chassis
        3) check that chassis has been successfully updated
        """
        updated_chassis = self.update_chassis(
            self.chassis['uuid'], 'add', 'description=test-chassis')
        self.assertEqual('test-chassis', updated_chassis['description'])
        self.assertNotEqual(self.chassis['description'],
                            updated_chassis['description'])

    def test_chassis_node_list(self):
        """Test steps:

        1) create chassis in setUp()
        2) create 3 nodes
        3) update 2 nodes to be included in chassis
        4) check if 2 nodes are added to chassis
        5) check if 1 nodes isn't added to chassis
        """
        node1 = self.create_node()
        node2 = self.create_node()

        # This node is created to show that it won't be present
        # in the chassis-node-list output

        node3 = self.create_node()
        updated_node1 = self.update_node(node1['uuid'],
                                         'add chassis_uuid={0}'
                                         .format(self.chassis['uuid']))
        updated_node2 = self.update_node(node2['uuid'],
                                         'add chassis_uuid={0}'
                                         .format(self.chassis['uuid']))
        nodes = [updated_node1['uuid'], updated_node2['uuid']]
        nodes.sort()
        nodes_uuids = self.get_nodes_uuids_from_chassis_node_list(
            self.chassis['uuid'])
        nodes_uuids.sort()
        self.assertEqual(nodes, nodes_uuids)
        self.assertNotIn(node3['uuid'], nodes_uuids)


class ChassisNegativeTestsIronicClient(base.FunctionalTestBase):
    """Negative tests for testing actions with Chassis.

    Negative tests for the Ironic CLI commands which checks actions with
    chassis command like show, update, delete either using with arguments
    or without arguments.
    """

    def test_chassis_delete_without_arguments(self):
        """Test step:

        1) check that chassis-delete command without arguments
        triggers an exception
        """
        ex_text = r'chassis-delete: error: too few arguments'

        six.assertRaisesRegex(self, exceptions.CommandFailed,
                              ex_text,
                              self.delete_chassis, '')

    def test_chassis_delete_with_incorrect_chassis_uuid(self):
        """Test step:

        1) check that deleting non-exist chassis triggers an exception
        triggers an exception
        """
        uuid = data_utils.rand_uuid()
        ex_text = (r"Chassis {0} "
                   r"could not be found. \(HTTP 404\)".format(uuid))

        six.assertRaisesRegex(self, exceptions.CommandFailed,
                              ex_text,
                              self.delete_chassis,
                              '{0}'.format(uuid))

    def test_chassis_show_without_arguments(self):
        """Test step:

        1) check that chassis-show command without arguments
        triggers an exception
        """
        ex_text = r'chassis-show: error: too few arguments'

        six.assertRaisesRegex(self, exceptions.CommandFailed,
                              ex_text,
                              self.show_chassis, '')

    def test_chassis_show_with_incorrect_chassis_uuid(self):
        """Test step:

        1) check that chassis-show command with incorrect chassis
        uuid triggers an exception
        """
        uuid = data_utils.rand_uuid()
        ex_text = (r"Chassis {0} "
                   r"could not be found. \(HTTP 404\)".format(uuid))

        six.assertRaisesRegex(self, exceptions.CommandFailed,
                              ex_text,
                              self.show_chassis,
                              '{0}'.format(uuid))

    def test_chassis_update_without_arguments(self):
        """Test steps:

        1) create chassis
        2) check that chassis-update command without arguments
        triggers an exception
        """
        ex_text = r'chassis-update: error: too few arguments'

        six.assertRaisesRegex(self, exceptions.CommandFailed,
                              ex_text,
                              self.update_chassis,
                              chassis_id='',
                              operation='')

    def test_chassis_update_with_incorrect_chassis_uuid(self):
        """Test steps:

        1) create chassis
        2) check that chassis-update command with incorrect arguments
        triggers an exception
        """
        uuid = data_utils.rand_uuid()
        ex_text = r'chassis-update: error: too few arguments'

        six.assertRaisesRegex(self,
                              exceptions.CommandFailed,
                              ex_text,
                              self.update_chassis,
                              chassis_id='{0}'.format(uuid),
                              operation='')
