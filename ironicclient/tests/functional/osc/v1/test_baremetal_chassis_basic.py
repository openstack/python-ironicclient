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

from ironicclient.tests.functional.osc.v1 import base


class BaremetalChassisTests(base.TestCase):
    """Functional tests for baremetal chassis commands."""

    def setUp(self):
        super(BaremetalChassisTests, self).setUp()
        self.chassis = self.chassis_create()

    def test_list(self):
        """Check baremetal chassis list command.

        Test steps:
        1) Create baremetal chassis in setUp.
        2) List baremetal chassis.
        3) Check chassis description and UUID in chassis list.
        """
        chassis_list = self.chassis_list()
        self.assertIn(self.chassis['uuid'],
                      [x['UUID'] for x in chassis_list])
        self.assertIn(self.chassis['description'],
                      [x['Description'] for x in chassis_list])

    def test_show(self):
        """Check baremetal chassis show command.

        Test steps:
        1) Create baremetal chassis in setUp.
        2) Show baremetal chassis.
        3) Check chassis in chassis show.
        """
        chassis = self.chassis_show(self.chassis['uuid'])
        self.assertEqual(self.chassis['uuid'], chassis['uuid'])
        self.assertEqual(self.chassis['description'], chassis['description'])

    def test_delete(self):
        """Check baremetal chassis delete command.

        Test steps:
        1) Create baremetal chassis in setUp.
        2) Delete baremetal chassis by UUID.
        3) Check that chassis deleted successfully.
        """
        output = self.chassis_delete(self.chassis['uuid'])
        self.assertIn('Deleted chassis {0}'.format(self.chassis['uuid']),
                      output)
        self.assertNotIn(self.chassis['uuid'], self.chassis_list(['UUID']))

    def test_set_unset_extra(self):
        """Check baremetal chassis set and unset commands.

        Test steps:
        1) Create baremetal chassis in setUp.
        2) Set extra data for chassis.
        3) Check that baremetal chassis extra data was set.
        4) Unset extra data for chassis.
        5) Check that baremetal chassis extra data was unset.
        """
        extra_key = 'ext'
        extra_value = 'testdata'
        self.openstack('baremetal chassis set --extra {0}={1} {2}'
                       .format(extra_key, extra_value, self.chassis['uuid']))

        show_prop = self.chassis_show(self.chassis['uuid'], ['extra'])
        self.assertEqual(extra_value, show_prop['extra'][extra_key])

        self.openstack('baremetal chassis unset --extra {0} {1}'
                       .format(extra_key, self.chassis['uuid']))

        show_prop = self.chassis_show(self.chassis['uuid'], ['extra'])
        self.assertNotIn(extra_key, show_prop['extra'])
