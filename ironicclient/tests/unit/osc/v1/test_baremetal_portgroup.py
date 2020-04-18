#
#   Copyright 2016 Mirantis, Inc.
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
from unittest import mock

from osc_lib.tests import utils as osctestutils

from ironicclient.osc.v1 import baremetal_portgroup
from ironicclient.tests.unit.osc.v1 import fakes as baremetal_fakes


class TestBaremetalPortGroup(baremetal_fakes.TestBaremetal):

    def setUp(self):
        super(TestBaremetalPortGroup, self).setUp()

        self.baremetal_mock = self.app.client_manager.baremetal
        self.baremetal_mock.reset_mock()


class TestCreateBaremetalPortGroup(TestBaremetalPortGroup):

    def setUp(self):
        super(TestCreateBaremetalPortGroup, self).setUp()

        self.baremetal_mock.portgroup.create.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.PORTGROUP),
                loaded=True,
            ))

        # Get the command object to test
        self.cmd = baremetal_portgroup.CreateBaremetalPortGroup(self.app, None)

    def test_baremetal_portgroup_create(self):
        arglist = [
            '--node', baremetal_fakes.baremetal_uuid,
        ]

        verifylist = [
            ('node_uuid', baremetal_fakes.baremetal_uuid),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        args = {
            'node_uuid': baremetal_fakes.baremetal_uuid,
        }

        self.baremetal_mock.portgroup.create.assert_called_once_with(**args)

    def test_baremetal_portgroup_create_name_address_uuid(self):
        arglist = [
            '--address', baremetal_fakes.baremetal_portgroup_address,
            '--node', baremetal_fakes.baremetal_uuid,
            '--name', baremetal_fakes.baremetal_portgroup_name,
            '--uuid', baremetal_fakes.baremetal_portgroup_uuid,
        ]

        verifylist = [
            ('node_uuid', baremetal_fakes.baremetal_uuid),
            ('address', baremetal_fakes.baremetal_portgroup_address),
            ('name', baremetal_fakes.baremetal_portgroup_name),
            ('uuid', baremetal_fakes.baremetal_portgroup_uuid),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        args = {
            'address': baremetal_fakes.baremetal_portgroup_address,
            'node_uuid': baremetal_fakes.baremetal_uuid,
            'name': baremetal_fakes.baremetal_portgroup_name,
            'uuid': baremetal_fakes.baremetal_portgroup_uuid,
        }

        self.baremetal_mock.portgroup.create.assert_called_once_with(**args)

    def test_baremetal_portgroup_create_support_standalone_ports(self):
        arglist = [
            '--address', baremetal_fakes.baremetal_portgroup_address,
            '--node', baremetal_fakes.baremetal_uuid,
            '--support-standalone-ports'
        ]

        verifylist = [
            ('node_uuid', baremetal_fakes.baremetal_uuid),
            ('address', baremetal_fakes.baremetal_portgroup_address),
            ('support_standalone_ports', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        args = {
            'address': baremetal_fakes.baremetal_portgroup_address,
            'node_uuid': baremetal_fakes.baremetal_uuid,
            'standalone_ports_supported': True,
        }

        self.baremetal_mock.portgroup.create.assert_called_once_with(**args)

    def test_baremetal_portgroup_create_unsupport_standalone_ports(self):
        arglist = [
            '--address', baremetal_fakes.baremetal_portgroup_address,
            '--node', baremetal_fakes.baremetal_uuid,
            '--unsupport-standalone-ports'
        ]

        verifylist = [
            ('node_uuid', baremetal_fakes.baremetal_uuid),
            ('address', baremetal_fakes.baremetal_portgroup_address),
            ('unsupport_standalone_ports', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        args = {
            'address': baremetal_fakes.baremetal_portgroup_address,
            'node_uuid': baremetal_fakes.baremetal_uuid,
            'standalone_ports_supported': False,
        }

        self.baremetal_mock.portgroup.create.assert_called_once_with(**args)

    def test_baremetal_portgroup_create_name_extras(self):
        arglist = [
            '--address', baremetal_fakes.baremetal_portgroup_address,
            '--node', baremetal_fakes.baremetal_uuid,
            '--name', baremetal_fakes.baremetal_portgroup_name,
            '--extra', 'key1=value1',
            '--extra', 'key2=value2'
        ]

        verifylist = [
            ('node_uuid', baremetal_fakes.baremetal_uuid),
            ('address', baremetal_fakes.baremetal_portgroup_address),
            ('name', baremetal_fakes.baremetal_portgroup_name),
            ('extra', ['key1=value1', 'key2=value2'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        args = {
            'address': baremetal_fakes.baremetal_portgroup_address,
            'node_uuid': baremetal_fakes.baremetal_uuid,
            'name': baremetal_fakes.baremetal_portgroup_name,
            'extra': baremetal_fakes.baremetal_portgroup_extra
        }

        self.baremetal_mock.portgroup.create.assert_called_once_with(**args)

    def test_baremetal_portgroup_create_mode_properties(self):
        arglist = [
            '--node', baremetal_fakes.baremetal_uuid,
            '--mode', baremetal_fakes.baremetal_portgroup_mode,
            '--property', 'key1=value11',
            '--property', 'key2=value22'
        ]

        verifylist = [
            ('node_uuid', baremetal_fakes.baremetal_uuid),
            ('mode', baremetal_fakes.baremetal_portgroup_mode),
            ('properties', ['key1=value11', 'key2=value22'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        args = {
            'node_uuid': baremetal_fakes.baremetal_uuid,
            'mode': baremetal_fakes.baremetal_portgroup_mode,
            'properties': baremetal_fakes.baremetal_portgroup_properties
        }

        self.baremetal_mock.portgroup.create.assert_called_once_with(**args)

    def test_baremetal_portgroup_create_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestShowBaremetalPortGroup(TestBaremetalPortGroup):

    def setUp(self):
        super(TestShowBaremetalPortGroup, self).setUp()

        self.baremetal_mock.portgroup.get.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.PORTGROUP),
                loaded=True))

        self.baremetal_mock.portgroup.get_by_address.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.PORTGROUP),
                loaded=True))

        self.cmd = baremetal_portgroup.ShowBaremetalPortGroup(self.app, None)

    def test_baremetal_portgroup_show(self):
        arglist = ['ppp-gggggg-pppp']
        verifylist = [('portgroup', baremetal_fakes.baremetal_portgroup_uuid)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        args = ['ppp-gggggg-pppp']
        self.baremetal_mock.portgroup.get.assert_called_with(*args,
                                                             fields=None)

        collist = ('address', 'extra', 'mode', 'name', 'node_uuid',
                   'properties', 'uuid')
        self.assertEqual(collist, columns)

        datalist = (
            baremetal_fakes.baremetal_portgroup_address,
            baremetal_fakes.baremetal_portgroup_extra,
            baremetal_fakes.baremetal_portgroup_mode,
            baremetal_fakes.baremetal_portgroup_name,
            baremetal_fakes.baremetal_uuid,
            baremetal_fakes.baremetal_portgroup_properties,
            baremetal_fakes.baremetal_portgroup_uuid,
        )

        self.assertEqual(datalist, tuple(data))

    def test_baremetal_portgroup_show_address(self):
        arglist = ['--address', baremetal_fakes.baremetal_portgroup_address]
        verifylist = [('address', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        args = {baremetal_fakes.baremetal_portgroup_address}
        self.baremetal_mock.portgroup.get_by_address.assert_called_with(
            *args, fields=None)

    def test_baremetal_portgroup_show_no_options(self):
        arglist = []
        verifylist = []
        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestBaremetalPortGroupList(TestBaremetalPortGroup):
    def setUp(self):
        super(TestBaremetalPortGroupList, self).setUp()

        self.baremetal_mock.portgroup.list.return_value = [
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.PORTGROUP),
                loaded=True)
        ]
        self.cmd = baremetal_portgroup.ListBaremetalPortGroup(self.app, None)

    def test_baremetal_portgroup_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'marker': None,
            'limit': None}
        self.baremetal_mock.portgroup.list.assert_called_with(**kwargs)

        collist = (
            "UUID",
            "Address",
            "Name")
        self.assertEqual(collist, columns)

        datalist = ((baremetal_fakes.baremetal_portgroup_uuid,
                     baremetal_fakes.baremetal_portgroup_address,
                     baremetal_fakes.baremetal_portgroup_name),)
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_portgroup_list_address(self):
        arglist = ['--address', baremetal_fakes.baremetal_portgroup_address]
        verifylist = [('address', baremetal_fakes.baremetal_portgroup_address)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'address': baremetal_fakes.baremetal_portgroup_address,
            'marker': None,
            'limit': None}
        self.baremetal_mock.portgroup.list.assert_called_with(**kwargs)

        collist = (
            "UUID",
            "Address",
            "Name")
        self.assertEqual(collist, columns)

        datalist = ((baremetal_fakes.baremetal_portgroup_uuid,
                     baremetal_fakes.baremetal_portgroup_address,
                     baremetal_fakes.baremetal_portgroup_name),)
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_portgroup_list_node(self):
        arglist = ['--node', baremetal_fakes.baremetal_uuid]
        verifylist = [('node', baremetal_fakes.baremetal_uuid)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'node': baremetal_fakes.baremetal_uuid,
            'marker': None,
            'limit': None}
        self.baremetal_mock.portgroup.list.assert_called_with(**kwargs)

        collist = (
            "UUID",
            "Address",
            "Name")
        self.assertEqual(collist, columns)

        datalist = ((baremetal_fakes.baremetal_portgroup_uuid,
                     baremetal_fakes.baremetal_portgroup_address,
                     baremetal_fakes.baremetal_portgroup_name),)
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_portgroup_list_long(self):
        arglist = ['--long']
        verifylist = [('detail', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'detail': True,
            'marker': None,
            'limit': None,
        }
        self.baremetal_mock.portgroup.list.assert_called_with(**kwargs)

        collist = ('UUID', 'Address', 'Created At', 'Extra',
                   'Standalone Ports Supported', 'Node UUID', 'Name',
                   'Updated At', 'Internal Info', 'Mode', 'Properties')
        self.assertEqual(collist, columns)

        datalist = ((baremetal_fakes.baremetal_portgroup_uuid,
                     baremetal_fakes.baremetal_portgroup_address,
                     '',
                     baremetal_fakes.baremetal_portgroup_extra,
                     '',
                     baremetal_fakes.baremetal_uuid,
                     baremetal_fakes.baremetal_portgroup_name,
                     '',
                     '',
                     baremetal_fakes.baremetal_portgroup_mode,
                     baremetal_fakes.baremetal_portgroup_properties),)
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_portgroup_list_fields(self):
        arglist = ['--fields', 'uuid', 'address']
        verifylist = [('fields', [['uuid', 'address']])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        kwargs = {
            'marker': None,
            'limit': None,
            'detail': False,
            'fields': ('uuid', 'address')
        }
        self.baremetal_mock.portgroup.list.assert_called_with(**kwargs)

    def test_baremetal_portgroup_list_fields_multiple(self):
        arglist = ['--fields', 'uuid', 'address', '--fields', 'extra']
        verifylist = [('fields', [['uuid', 'address'], ['extra']])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        kwargs = {
            'marker': None,
            'limit': None,
            'detail': False,
            'fields': ('uuid', 'address', 'extra')
        }
        self.baremetal_mock.portgroup.list.assert_called_with(**kwargs)

    def test_baremetal_portgroup_list_invalid_fields(self):
        arglist = ['--fields', 'uuid', 'invalid']
        verifylist = [('fields', [['uuid', 'invalid']])]
        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestBaremetalPortGroupDelete(TestBaremetalPortGroup):

    def setUp(self):
        super(TestBaremetalPortGroupDelete, self).setUp()

        self.baremetal_mock.portgroup.get.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.PORTGROUP),
                loaded=True))

        self.cmd = baremetal_portgroup.DeleteBaremetalPortGroup(self.app, None)

    def test_baremetal_portgroup_delete(self):
        arglist = [baremetal_fakes.baremetal_portgroup_uuid]
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        args = baremetal_fakes.baremetal_portgroup_uuid
        self.baremetal_mock.portgroup.delete.assert_called_with(args)

    def test_baremetal_portgroup_delete_multiple(self):
        arglist = [baremetal_fakes.baremetal_portgroup_uuid,
                   baremetal_fakes.baremetal_portgroup_name]
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        args = [baremetal_fakes.baremetal_portgroup_uuid,
                baremetal_fakes.baremetal_portgroup_name]
        self.baremetal_mock.portgroup.delete.assert_has_calls(
            [mock.call(x) for x in args])
        self.assertEqual(2, self.baremetal_mock.portgroup.delete.call_count)

    def test_baremetal_portgroup_delete_no_options(self):
        arglist = []
        verifylist = []
        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestBaremetalPortGroupSet(TestBaremetalPortGroup):
    def setUp(self):
        super(TestBaremetalPortGroupSet, self).setUp()

        self.baremetal_mock.portgroup.update.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.PORTGROUP),
                loaded=True))

        self.cmd = baremetal_portgroup.SetBaremetalPortGroup(self.app, None)

    def test_baremetal_portgroup_set_name(self):
        new_portgroup_name = 'New-Portgroup-name'
        arglist = [
            baremetal_fakes.baremetal_portgroup_uuid,
            '--name', new_portgroup_name]
        verifylist = [
            ('portgroup', baremetal_fakes.baremetal_portgroup_uuid),
            ('name', new_portgroup_name)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.portgroup.update.assert_called_once_with(
            baremetal_fakes.baremetal_portgroup_uuid,
            [{'path': '/name', 'value': new_portgroup_name, 'op': 'add'}])

    def test_baremetal_portgroup_set_address(self):
        new_portgroup_address = '00:22:44:66:88:00'
        arglist = [
            baremetal_fakes.baremetal_portgroup_uuid,
            '--address', new_portgroup_address]
        verifylist = [
            ('portgroup', baremetal_fakes.baremetal_portgroup_uuid),
            ('address', new_portgroup_address)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.portgroup.update.assert_called_once_with(
            baremetal_fakes.baremetal_portgroup_uuid,
            [{'path': '/address', 'value': new_portgroup_address,
              'op': 'add'}])

    def test_baremetal_portgroup_set_mode(self):
        new_portgroup_mode = '802.3ad'
        arglist = [
            baremetal_fakes.baremetal_portgroup_uuid,
            '--mode', new_portgroup_mode]
        verifylist = [
            ('portgroup', baremetal_fakes.baremetal_portgroup_uuid),
            ('mode', new_portgroup_mode)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.portgroup.update.assert_called_once_with(
            baremetal_fakes.baremetal_portgroup_uuid,
            [{'path': '/mode', 'value': new_portgroup_mode,
              'op': 'add'}])

    def test_baremetal_portgroup_set_mode_int(self):
        new_portgroup_mode = '4'
        arglist = [
            baremetal_fakes.baremetal_portgroup_uuid,
            '--mode', new_portgroup_mode]
        verifylist = [
            ('portgroup', baremetal_fakes.baremetal_portgroup_uuid),
            ('mode', new_portgroup_mode)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.portgroup.update.assert_called_once_with(
            baremetal_fakes.baremetal_portgroup_uuid,
            [{'path': '/mode', 'value': new_portgroup_mode,
              'op': 'add'}])

    def test_baremetal_portgroup_set_node_uuid(self):
        new_node_uuid = 'nnnnnn-uuuuuuuu'
        arglist = [
            baremetal_fakes.baremetal_portgroup_uuid,
            '--node', new_node_uuid]
        verifylist = [
            ('portgroup', baremetal_fakes.baremetal_portgroup_uuid),
            ('node_uuid', new_node_uuid)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.portgroup.update.assert_called_once_with(
            baremetal_fakes.baremetal_portgroup_uuid,
            [{'path': '/node_uuid', 'value': new_node_uuid,
              'op': 'add'}])

    def test_baremetal_portgroup_set_support_standalone_ports(self):
        arglist = [
            baremetal_fakes.baremetal_portgroup_uuid,
            '--support-standalone-ports']
        verifylist = [
            ('portgroup', baremetal_fakes.baremetal_portgroup_uuid),
            ('support_standalone_ports', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.portgroup.update.assert_called_once_with(
            baremetal_fakes.baremetal_portgroup_uuid,
            [{'path': '/standalone_ports_supported', 'value': 'True',
              'op': 'add'}])

    def test_baremetal_portgroup_set_unsupport_standalone_ports(self):
        arglist = [
            baremetal_fakes.baremetal_portgroup_uuid,
            '--unsupport-standalone-ports']
        verifylist = [
            ('portgroup', baremetal_fakes.baremetal_portgroup_uuid),
            ('unsupport_standalone_ports', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.portgroup.update.assert_called_once_with(
            baremetal_fakes.baremetal_portgroup_uuid,
            [{'path': '/standalone_ports_supported', 'value': 'False',
              'op': 'add'}])

    def test_baremetal_set_extra(self):
        arglist = ['portgroup', '--extra', 'foo=bar']
        verifylist = [('portgroup', 'portgroup'),
                      ('extra', ['foo=bar'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.portgroup.update.assert_called_once_with(
            'portgroup',
            [{'path': '/extra/foo', 'value': 'bar', 'op': 'add'}])

    def test_baremetal_portgroup_set_multiple_extras(self):
        arglist = ['portgroup',
                   '--extra', 'key1=val1',
                   '--extra', 'key2=val2']
        verifylist = [('portgroup', 'portgroup'),
                      ('extra', ['key1=val1', 'key2=val2'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.portgroup.update.assert_called_once_with(
            'portgroup',
            [{'path': '/extra/key1', 'value': 'val1', 'op': 'add'},
             {'path': '/extra/key2', 'value': 'val2', 'op': 'add'}])

    def test_baremetal_portgroup_set_multiple_properties(self):
        arglist = ['portgroup',
                   '--property', 'key3=val3',
                   '--property', 'key4=val4']
        verifylist = [('portgroup', 'portgroup'),
                      ('properties', ['key3=val3', 'key4=val4'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.portgroup.update.assert_called_once_with(
            'portgroup',
            [{'path': '/properties/key3', 'value': 'val3', 'op': 'add'},
             {'path': '/properties/key4', 'value': 'val4', 'op': 'add'}])

    def test_baremetal_portgroup_set_no_options(self):
        arglist = []
        verifylist = []
        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_portgroup_set_no_property(self):
        uuid = baremetal_fakes.baremetal_portgroup_uuid
        arglist = [uuid]
        verifylist = [('portgroup', uuid)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.assertFalse(self.baremetal_mock.portgroup.update.called)


class TestBaremetalPortGroupUnset(TestBaremetalPortGroup):
    def setUp(self):
        super(TestBaremetalPortGroupUnset, self).setUp()

        self.baremetal_mock.portgroup.update.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.PORTGROUP),
                loaded=True))

        self.cmd = baremetal_portgroup.UnsetBaremetalPortGroup(self.app, None)

    def test_baremetal_portgroup_unset_extra(self):
        arglist = ['portgroup', '--extra', 'key1']
        verifylist = [('portgroup', 'portgroup'),
                      ('extra', ['key1'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.portgroup.update.assert_called_once_with(
            'portgroup',
            [{'path': '/extra/key1', 'op': 'remove'}])

    def test_baremetal_portgroup_unset_name(self):
        arglist = ['portgroup', '--name']
        verifylist = [('name', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.portgroup.update.assert_called_once_with(
            'portgroup',
            [{'path': '/name', 'op': 'remove'}])

    def test_baremetal_portgroup_unset_address(self):
        arglist = ['portgroup', '--address']
        verifylist = [('address', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.portgroup.update.assert_called_once_with(
            'portgroup',
            [{'path': '/address', 'op': 'remove'}])

    def test_baremetal_portgroup_unset_multiple_extras(self):
        arglist = ['portgroup',
                   '--extra', 'key1',
                   '--extra', 'key2']
        verifylist = [('portgroup', 'portgroup'),
                      ('extra', ['key1', 'key2'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.portgroup.update.assert_called_once_with(
            'portgroup',
            [{'path': '/extra/key1', 'op': 'remove'},
             {'path': '/extra/key2', 'op': 'remove'}])

    def test_baremetal_portgroup_unset_multiple_properties(self):
        arglist = ['portgroup',
                   '--property', 'key1',
                   '--property', 'key2']
        verifylist = [('portgroup', 'portgroup'),
                      ('properties', ['key1', 'key2'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.portgroup.update.assert_called_once_with(
            'portgroup',
            [{'path': '/properties/key1', 'op': 'remove'},
             {'path': '/properties/key2', 'op': 'remove'}])

    def test_baremetal_portgroup_unset_no_options(self):
        arglist = []
        verifylist = []
        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_portgroup_unset_no_property(self):
        uuid = baremetal_fakes.baremetal_portgroup_uuid
        arglist = [uuid]
        verifylist = [('portgroup', uuid)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.assertFalse(self.baremetal_mock.portgroup.update.called)
