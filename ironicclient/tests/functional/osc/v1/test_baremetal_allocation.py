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
from tempest.lib import exceptions

from ironicclient.tests.functional.osc.v1 import base


@ddt.ddt
class BaremetalAllocationTests(base.TestCase):
    """Functional tests for baremetal allocation commands."""

    def test_create(self):
        """Check baremetal allocation create command.

        Test steps:
        1) Create baremetal allocation in setUp.
        2) Check that allocation successfully created.
        """
        allocation_info = self.allocation_create()
        self.assertTrue(allocation_info['resource_class'])
        self.assertEqual(allocation_info['state'], 'allocating')

        allocation_list = self.allocation_list()
        self.assertIn(allocation_info['uuid'],
                      [x['UUID'] for x in allocation_list])

    def test_create_name_uuid(self):
        """Check baremetal allocation create command with name and UUID.

        Test steps:
        1) Create baremetal allocation with specified name and UUID.
        2) Check that allocation successfully created.
        """
        uuid = data_utils.rand_uuid()
        name = data_utils.rand_name('baremetal-allocation')
        allocation_info = self.allocation_create(
            params='--uuid {0} --name {1}'.format(uuid, name))
        self.assertEqual(allocation_info['uuid'], uuid)
        self.assertEqual(allocation_info['name'], name)
        self.assertTrue(allocation_info['resource_class'])
        self.assertEqual(allocation_info['state'], 'allocating')

        allocation_list = self.allocation_list()
        self.assertIn(uuid, [x['UUID'] for x in allocation_list])
        self.assertIn(name, [x['Name'] for x in allocation_list])

    def test_create_traits(self):
        """Check baremetal allocation create command with traits.

        Test steps:
        1) Create baremetal allocation with specified traits.
        2) Check that allocation successfully created.
        """
        allocation_info = self.allocation_create(
            params='--trait CUSTOM_1 --trait CUSTOM_2')
        self.assertTrue(allocation_info['resource_class'])
        self.assertEqual(allocation_info['state'], 'allocating')
        self.assertIn('CUSTOM_1', allocation_info['traits'])
        self.assertIn('CUSTOM_2', allocation_info['traits'])

    def test_create_candidate_nodes(self):
        """Check baremetal allocation create command with candidate nodes.

        Test steps:
        1) Create two nodes.
        2) Create baremetal allocation with specified traits.
        3) Check that allocation successfully created.
        """
        name = data_utils.rand_name('baremetal-allocation')
        node1 = self.node_create(name=name)
        node2 = self.node_create()
        allocation_info = self.allocation_create(
            params='--candidate-node {0} --candidate-node {1}'
            .format(node1['name'], node2['uuid']))
        self.assertEqual(allocation_info['state'], 'allocating')
        # NOTE(dtantsur): names are converted to uuids in the API
        self.assertIn(node1['uuid'], allocation_info['candidate_nodes'])
        self.assertIn(node2['uuid'], allocation_info['candidate_nodes'])

    @ddt.data('name', 'uuid')
    def test_delete(self, key):
        """Check baremetal allocation delete command with name/UUID argument.

        Test steps:
        1) Create baremetal allocation.
        2) Delete baremetal allocation by name/UUID.
        3) Check that allocation deleted successfully.
        """
        name = data_utils.rand_name('baremetal-allocation')
        allocation = self.allocation_create(params='--name {}'.format(name))
        output = self.allocation_delete(allocation[key])
        self.assertIn('Deleted allocation {0}'.format(allocation[key]), output)

        allocation_list = self.allocation_list()
        self.assertNotIn(allocation['name'],
                         [x['Name'] for x in allocation_list])
        self.assertNotIn(allocation['uuid'],
                         [x['UUID'] for x in allocation_list])

    @ddt.data('name', 'uuid')
    def test_show(self, key):
        """Check baremetal allocation show command with name and UUID.

        Test steps:
        1) Create baremetal allocation.
        2) Show baremetal allocation calling it with name and UUID arguments.
        3) Check name, uuid and resource_class in allocation show output.
        """
        name = data_utils.rand_name('baremetal-allocation')
        allocation = self.allocation_create(params='--name {}'.format(name))
        result = self.allocation_show(allocation[key],
                                      ['name', 'uuid', 'resource_class'])
        self.assertEqual(allocation['name'], result['name'])
        self.assertEqual(allocation['uuid'], result['uuid'])
        self.assertTrue(result['resource_class'])
        self.assertNotIn('state', result)

    @ddt.data(
        ('--uuid', '', 'expected one argument'),
        ('--uuid', '!@#$^*&%^', 'Expected UUID for uuid'),
        ('--extra', '', 'expected one argument'),
        ('--name', '', 'expected one argument'),
        ('--name', 'not/a/name', 'invalid name'),
        ('--resource-class', '', 'expected one argument'),
        ('--resource-class', 'x' * 81, 'is too long'),
        ('--trait', '', 'expected one argument'),
        ('--trait', 'foo', 'does not match'),
        ('--candidate-node', '', 'expected one argument'),
        ('--candidate-node', 'banana?', 'Nodes cannot be found'),
        ('--wait', 'meow', 'invalid int value'))
    @ddt.unpack
    def test_create_negative(self, argument, value, ex_text):
        """Check errors on invalid input parameters."""
        base_cmd = 'baremetal allocation create'
        if argument != '--resource-class':
            base_cmd += ' --resource-class allocation-test'
        command = self.construct_cmd(base_cmd, argument, value)
        self.assertRaisesRegex(exceptions.CommandFailed, ex_text,
                               self.openstack, command)

    def test_create_no_resource_class(self):
        """Check errors on missing resource class."""
        base_cmd = 'baremetal allocation create'
        self.assertRaisesRegex(exceptions.CommandFailed,
                               '--resource-class',
                               self.openstack, base_cmd)

    def test_set_unset(self):
        """Check baremetal allocation set and unset commands.

        Test steps:
        1) Create baremetal allocation in setUp.
        2) Set extra data for allocation.
        3) Check that baremetal allocation extra data was set.
        4) Unset extra data for allocation.
        5) Check that baremetal allocation  extra data was unset.
        """
        name = data_utils.rand_name('baremetal-allocation')
        allocation = self.allocation_create(params='--name {}'.format(name))
        extra_key = 'ext'
        extra_value = 'testdata'
        self.openstack(
            'baremetal allocation set --extra {0}={1} {2}'
            .format(extra_key, extra_value, allocation['uuid']))

        show_prop = self.allocation_show(allocation['uuid'],
                                         fields=['extra'])
        self.assertEqual(extra_value, show_prop['extra'][extra_key])

        self.openstack('baremetal allocation unset --extra {0} {1}'
                       .format(extra_key, allocation['uuid']))

        show_prop = self.allocation_show(allocation['uuid'],
                                         fields=['extra'])
        self.assertNotIn(extra_key, show_prop['extra'])
