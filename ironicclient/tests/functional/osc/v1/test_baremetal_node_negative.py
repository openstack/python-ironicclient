#    Copyright (c) 2017 Mirantis, Inc.
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
import six
from tempest.lib import exceptions

from ironicclient.tests.functional.osc.v1 import base


@ddt.ddt
class BaremetalNodeNegativeTests(base.TestCase):
    """Negative tests for baremetal node commands."""

    def setUp(self):
        super(BaremetalNodeNegativeTests, self).setUp()
        self.node = self.node_create()

    @ddt.data(
        ('', '',
         'error: argument --driver is required' if six.PY2
         else 'error: the following arguments are required: --driver'),
        ('--driver', 'wrongdriver',
         'No valid host was found. Reason: No conductor service '
         'registered which supports driver wrongdriver.')
    )
    @ddt.unpack
    def test_create_driver(self, argument, value, ex_text):
        """Negative test for baremetal node driver options."""
        base_cmd = 'baremetal node create'
        command = self.construct_cmd(base_cmd, argument, value)
        six.assertRaisesRegex(self, exceptions.CommandFailed, ex_text,
                              self.openstack, command)

    def test_delete_no_node(self):
        """Test for baremetal node delete without node specified."""
        command = 'baremetal node delete'
        ex_text = 'error: too few arguments'
        if six.PY3:
            ex_text = ''
        six.assertRaisesRegex(self, exceptions.CommandFailed, ex_text,
                              self.openstack, command)

    def test_list_wrong_argument(self):
        """Test for baremetal node list with wrong argument."""
        command = 'baremetal node list --wrong_arg'
        ex_text = 'error: unrecognized arguments: --wrong_arg'
        six.assertRaisesRegex(self, exceptions.CommandFailed, ex_text,
                              self.openstack, command)

    @ddt.data(
        ('--property', '',
         'error: too few arguments' if six.PY2
         else 'error: the following arguments are required: <node>'),
        ('--property', 'prop', 'Attributes must be a list of PATH=VALUE')
    )
    @ddt.unpack
    def test_set_property(self, argument, value, ex_text):
        """Negative test for baremetal node set command options."""
        base_cmd = 'baremetal node set'
        command = self.construct_cmd(base_cmd, argument, value,
                                     self.node['uuid'])
        six.assertRaisesRegex(self, exceptions.CommandFailed, ex_text,
                              self.openstack, command)

    @ddt.data(
        ('--property', '',
         'error: too few arguments' if six.PY2
         else 'error: the following arguments are required: <node>'),
        ('--property', 'prop', "Reason: can't remove non-existent object")
    )
    @ddt.unpack
    def test_unset_property(self, argument, value, ex_text):
        """Negative test for baremetal node unset command options."""
        base_cmd = 'baremetal node unset'
        command = self.construct_cmd(base_cmd, argument, value,
                                     self.node['uuid'])
        six.assertRaisesRegex(self, exceptions.CommandFailed, ex_text,
                              self.openstack, command)
