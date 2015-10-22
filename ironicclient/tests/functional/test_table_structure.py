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


class TableStructureIronicCLITests(base.FunctionalTestBase):
    """Basic, read-only table structure tests for Ironic CLI commands.

    Basic smoke tests for the Ironic CLI commands to check table structure
    which do not require creating or modifying Ironic objects.
    """

    def test_chassis_list_table_structure(self):
        """Test scenario:

            1) get chassis-list
            2) check table structure
        """
        chassis_list = self.ironic('chassis-list')
        self.assertTableHeaders(['Description', 'UUID'], chassis_list)

    def test_node_list_table_structure(self):
        """Test scenario:

            1) get node-list
            2) check table structure
        """
        node_list = self.ironic('node-list')
        self.assertTableHeaders(['UUID', 'Name', 'Instance UUID',
                                 'Power State', 'Provisioning State',
                                 'Maintenance'], node_list)

    def test_port_list_table_structure(self):
        """Test scenario:

            1) get port-list
            2) check table structure
        """
        port_list = self.ironic('port-list')
        self.assertTableHeaders(['UUID', 'Address'], port_list)

    def test_driver_list_table_structure(self):
        """Test scenario:

            1) get driver-list
            2) check table structure
        """
        driver_list = self.ironic('driver-list')
        self.assertTableHeaders(['Supported driver(s)', 'Active host(s)'],
                                driver_list)
