#
#   Copyright 2015 Red Hat, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import copy

from ironicclient.osc.v1 import baremetal_port
from ironicclient.tests.unit.osc.v1 import fakes as baremetal_fakes


class TestBaremetalPort(baremetal_fakes.TestBaremetal):

    def setUp(self):
        super(TestBaremetalPort, self).setUp()

        self.baremetal_mock = self.app.client_manager.baremetal
        self.baremetal_mock.reset_mock()


class TestCreateBaremetalPort(TestBaremetalPort):
    def setUp(self):
        super(TestCreateBaremetalPort, self).setUp()

        self.baremetal_mock.port.create.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.BAREMETAL_PORT),
                loaded=True,
            ))

        # Get the command object to test
        self.cmd = baremetal_port.CreateBaremetalPort(self.app, None)

    def test_baremetal_port_create(self):
        arglist = [
            baremetal_fakes.baremetal_port_address,
            '--node', baremetal_fakes.baremetal_uuid,
        ]

        verifylist = [
            ('node_uuid', baremetal_fakes.baremetal_uuid),
            ('address', baremetal_fakes.baremetal_port_address),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        args = {
            'address': baremetal_fakes.baremetal_port_address,
            'node_uuid': baremetal_fakes.baremetal_uuid,
        }

        self.baremetal_mock.port.create.assert_called_once_with(**args)
