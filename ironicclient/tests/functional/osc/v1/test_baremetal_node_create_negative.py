# Copyright (c) 2016 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import ddt
import six
from tempest.lib import exceptions

from ironicclient.tests.functional.osc.v1 import base


@ddt.ddt
class BaremetalNodeCreateNegativeTests(base.TestCase):
    """Negative tests for node create command."""

    def setUp(self):
        super(BaremetalNodeCreateNegativeTests, self).setUp()

    @ddt.data(
        ('--uuid', '', 'expected one argument'),
        ('--uuid', '!@#$^*&%^', 'Expected a UUID'),
        ('--uuid', '0000 0000', 'unrecognized arguments'),
        ('--driver-info', '', 'expected one argument'),
        ('--driver-info', 'some info', 'unrecognized arguments'),
        ('--property', '', 'expected one argument'),
        ('--property', 'some property', 'unrecognized arguments'),
        ('--extra', '', 'expected one argument'),
        ('--extra', 'some extra', 'unrecognized arguments'),
        ('--name', '', 'expected one argument'),
        ('--name', 'some name', 'unrecognized arguments'),
        ('--network-interface', '', 'expected one argument'),
        ('--resource-class', '', 'expected one argument'))
    @ddt.unpack
    def test_baremetal_node_create(self, argument, value, ex_text):
        base_cmd = 'baremetal node create --driver fake'
        command = self.construct_cmd(base_cmd, argument, value)
        six.assertRaisesRegex(self, exceptions.CommandFailed, ex_text,
                              self.openstack, command)
