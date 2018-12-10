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

import copy

from osc_lib.tests import utils as oscutils

from ironicclient.osc.v1 import baremetal_conductor
from ironicclient.tests.unit.osc.v1 import fakes as baremetal_fakes


class TestBaremetalConductor(baremetal_fakes.TestBaremetal):

    def setUp(self):
        super(TestBaremetalConductor, self).setUp()

        # Get a shortcut to the baremetal manager mock
        self.baremetal_mock = self.app.client_manager.baremetal
        self.baremetal_mock.reset_mock()


class TestBaremetalConductorList(TestBaremetalConductor):

    def setUp(self):
        super(TestBaremetalConductorList, self).setUp()

        self.baremetal_mock.conductor.list.return_value = [
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.CONDUCTOR),
                loaded=True,
            ),
        ]

        # Get the command object to test
        self.cmd = baremetal_conductor.ListBaremetalConductor(self.app, None)

    def test_conductor_list_no_options(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'marker': None,
            'limit': None,
        }

        self.baremetal_mock.conductor.list.assert_called_with(
            **kwargs
        )

        collist = (
            "Hostname",
            "Conductor Group",
            "Alive",
        )
        self.assertEqual(collist, columns)
        datalist = ((
            baremetal_fakes.baremetal_hostname,
            baremetal_fakes.baremetal_conductor_group,
            baremetal_fakes.baremetal_alive,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_conductor_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'detail': True,
            'marker': None,
            'limit': None,
        }

        self.baremetal_mock.conductor.list.assert_called_with(
            **kwargs
        )

        collist = [
            'Hostname',
            'Conductor Group',
            'Alive',
            'Drivers',
            'Created At',
            'Updated At',
        ]
        self.assertEqual(tuple(collist), columns)

        fake_values = {
            'Hostname': baremetal_fakes.baremetal_hostname,
            'Conductor Group': baremetal_fakes.baremetal_conductor_group,
            'Alive': baremetal_fakes.baremetal_alive,
            'Drivers': baremetal_fakes.baremetal_drivers,
        }
        values = tuple(fake_values.get(name, '') for name in collist)
        self.assertEqual((values,), tuple(data))

    def test_conductor_list_fields(self):
        arglist = [
            '--fields', 'hostname', 'alive',
        ]
        verifylist = [
            ('fields', [['hostname', 'alive']]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'marker': None,
            'limit': None,
            'detail': False,
            'fields': ('hostname', 'alive'),
        }

        self.baremetal_mock.conductor.list.assert_called_with(
            **kwargs
        )

    def test_conductor_list_fields_multiple(self):
        arglist = [
            '--fields', 'hostname', 'alive',
            '--fields', 'conductor_group',
        ]
        verifylist = [
            ('fields', [['hostname', 'alive'], ['conductor_group']])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'marker': None,
            'limit': None,
            'detail': False,
            'fields': ('hostname', 'alive', 'conductor_group')
        }

        self.baremetal_mock.conductor.list.assert_called_with(
            **kwargs
        )

    def test_conductor_list_invalid_fields(self):
        arglist = [
            '--fields', 'hostname', 'invalid'
        ]
        verifylist = [
            ('fields', [['hostname', 'invalid']])
        ]

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestBaremetalConductorShow(TestBaremetalConductor):
    def setUp(self):
        super(TestBaremetalConductorShow, self).setUp()

        self.baremetal_mock.conductor.get.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.CONDUCTOR),
                loaded=True,
            ))

        # Get the command object to test
        self.cmd = baremetal_conductor.ShowBaremetalConductor(self.app, None)

    def test_conductor_show(self):
        arglist = ['xxxx.xxxx']
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        args = ['xxxx.xxxx']

        self.baremetal_mock.conductor.get.assert_called_with(
            *args, fields=None
        )

        collist = ('alive',
                   'conductor_group',
                   'drivers',
                   'hostname',
                   )
        self.assertEqual(collist, columns)
        datalist = (
            baremetal_fakes.baremetal_alive,
            baremetal_fakes.baremetal_conductor_group,
            baremetal_fakes.baremetal_drivers,
            baremetal_fakes.baremetal_hostname,
        )
        self.assertEqual(datalist, tuple(data))

    def test_conductor_show_no_conductor(self):
        arglist = []
        verifylist = []

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_conductor_show_fields(self):
        arglist = [
            'xxxxx',
            '--fields', 'hostname', 'alive',
        ]
        verifylist = [
            ('conductor', 'xxxxx'),
            ('fields', [['hostname', 'alive']]),
        ]

        fake_cond = copy.deepcopy(baremetal_fakes.CONDUCTOR)
        fake_cond.pop('conductor_group')
        fake_cond.pop('drivers')
        self.baremetal_mock.conductor.get.return_value = (
            baremetal_fakes.FakeBaremetalResource(None, fake_cond,
                                                  loaded=True))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)
        self.assertNotIn('conductor_group', columns)

        # Set expected values
        args = ['xxxxx']
        fields = ['hostname', 'alive']

        self.baremetal_mock.conductor.get.assert_called_with(
            *args, fields=fields
        )

    def test_conductor_show_fields_multiple(self):
        arglist = [
            'xxxxx',
            '--fields', 'hostname', 'alive',
            '--fields', 'conductor_group',
        ]
        verifylist = [
            ('conductor', 'xxxxx'),
            ('fields', [['hostname', 'alive'], ['conductor_group']])
        ]

        fake_cond = copy.deepcopy(baremetal_fakes.CONDUCTOR)
        fake_cond.pop('drivers')
        self.baremetal_mock.conductor.get.return_value = (
            baremetal_fakes.FakeBaremetalResource(None, fake_cond,
                                                  loaded=True))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.assertNotIn('drivers', columns)
        # Set expected values
        args = ['xxxxx']
        fields = ['hostname', 'alive', 'conductor_group']

        self.baremetal_mock.conductor.get.assert_called_with(
            *args, fields=fields
        )

    def test_conductor_show_invalid_fields(self):
        arglist = [
            'xxxxx',
            '--fields', 'hostname', 'invalid'
        ]
        verifylist = [
            ('conductor', 'xxxxx'),
            ('fields', [['hostname', 'invalid']])
        ]

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)
