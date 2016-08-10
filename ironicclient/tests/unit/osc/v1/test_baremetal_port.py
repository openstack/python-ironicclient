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

from openstackclient.tests import utils as oscutils

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
        self.cmd.take_action(parsed_args)

        # Set expected values
        args = {
            'address': baremetal_fakes.baremetal_port_address,
            'node_uuid': baremetal_fakes.baremetal_uuid,
        }

        self.baremetal_mock.port.create.assert_called_once_with(**args)


class TestShowBaremetalPort(TestBaremetalPort):
    def setUp(self):
        super(TestShowBaremetalPort, self).setUp()

        self.baremetal_mock.port.get.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.BAREMETAL_PORT),
                loaded=True))

        self.baremetal_mock.port.get_by_address.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.BAREMETAL_PORT),
                loaded=True))

        self.cmd = baremetal_port.ShowBaremetalPort(self.app, None)

    def test_baremetal_port_show(self):
        arglist = ['zzz-zzzzzz-zzzz']
        verifylist = [('port', baremetal_fakes.baremetal_port_uuid)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        args = ['zzz-zzzzzz-zzzz']
        self.baremetal_mock.port.get.assert_called_with(*args, fields=None)

        collist = (
            'address',
            'extra',
            'node_uuid',
            'uuid')
        self.assertEqual(collist, columns)

        datalist = (
            baremetal_fakes.baremetal_port_address,
            baremetal_fakes.baremetal_port_extra,
            baremetal_fakes.baremetal_uuid,
            baremetal_fakes.baremetal_port_uuid)
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_port_show_address(self):

        arglist = ['--address', baremetal_fakes.baremetal_port_address]
        verifylist = [('address', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        args = {'AA:BB:CC:DD:EE:FF'}
        self.baremetal_mock.port.get_by_address.assert_called_with(
            *args, fields=None)

    def test_baremetal_port_show_no_port(self):
        arglist = []
        verifylist = []

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)
