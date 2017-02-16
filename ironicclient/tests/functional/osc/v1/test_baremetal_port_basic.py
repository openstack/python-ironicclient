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


class BaremetalPortTests(base.TestCase):
    """Functional tests for baremetal port commands."""

    def setUp(self):
        super(BaremetalPortTests, self).setUp()
        self.node = self.node_create()
        self.port = self.port_create(self.node['uuid'])

    def test_list(self):
        """Check baremetal port list command.

        Test steps:
        1) Create baremetal port in setUp.
        2) List baremetal ports.
        3) Check port address and UUID in ports list.
        """
        port_list = self.port_list()
        self.assertIn(self.port['address'],
                      [port['Address'] for port in port_list])
        self.assertIn(self.port['uuid'],
                      [port['UUID'] for port in port_list])

    def test_show_uuid(self):
        """Check baremetal port show command with UUID.

        Test steps:
        1) Create baremetal port in setUp.
        2) Show baremetal port calling it by UUID.
        3) Check port fields in output.
        """
        port = self.port_show(self.port['uuid'])
        self.assertEqual(self.port['address'], port['address'])
        self.assertEqual(self.port['uuid'], port['uuid'])
        self.assertEqual(self.port['node_uuid'], self.node['uuid'])

    def test_show_addr(self):
        """Check baremetal port show command with address.

        Test steps:
        1) Create baremetal port in setUp.
        2) Show baremetal port calling it by address.
        3) Check port fields in output.
        """
        port = self.port_show(
            uuid='', params='--address {}'.format(self.port['address']))
        self.assertEqual(self.port['address'], port['address'])
        self.assertEqual(self.port['uuid'], port['uuid'])
        self.assertEqual(self.port['node_uuid'], self.node['uuid'])

    def test_delete(self):
        """Check baremetal port delete command.

        Test steps:
        1) Create baremetal port in setUp.
        2) Delete baremetal port by UUID.
        3) Check that port deleted successfully and not in list.
        """
        output = self.port_delete(self.port['uuid'])
        self.assertIn('Deleted port {0}'.format(self.port['uuid']), output)
        port_list = self.port_list()
        self.assertNotIn(self.port['address'],
                         [port['Address'] for port in port_list])
        self.assertNotIn(self.port['uuid'],
                         [port['UUID'] for port in port_list])

    def test_set_unset_extra(self):
        """Check baremetal port set and unset commands.

        Test steps:
        1) Create baremetal port in setUp.
        2) Set extra data for port.
        3) Check that baremetal port extra data was set.
        4) Unset extra data for port.
        5) Check that baremetal port extra data was unset.
        """
        extra_key = 'ext'
        extra_value = 'testdata'
        self.openstack('baremetal port set --extra {0}={1} {2}'
                       .format(extra_key, extra_value, self.port['uuid']))

        show_prop = self.port_show(self.port['uuid'], ['extra'])
        self.assertEqual(extra_value, show_prop['extra'][extra_key])

        self.openstack('baremetal port unset --extra {0} {1}'
                       .format(extra_key, self.port['uuid']))

        show_prop = self.port_show(self.port['uuid'], ['extra'])
        self.assertNotIn(extra_key, show_prop['extra'])
