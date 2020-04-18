#
#   Copyright 2016 Intel Corporation
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

from osc_lib.tests import utils as oscutils

from ironicclient import exc
from ironicclient.osc.v1 import baremetal_chassis
from ironicclient.tests.unit.osc.v1 import fakes as baremetal_fakes


class TestChassis(baremetal_fakes.TestBaremetal):

    def setUp(self):
        super(TestChassis, self).setUp()

        # Get a shortcut to the baremetal manager mock
        self.baremetal_mock = self.app.client_manager.baremetal
        self.baremetal_mock.reset_mock()


class TestChassisCreate(TestChassis):
    def setUp(self):
        super(TestChassisCreate, self).setUp()

        self.baremetal_mock.chassis.create.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.BAREMETAL_CHASSIS),
                loaded=True,
            ))

        # Get the command object to test
        self.cmd = baremetal_chassis.CreateBaremetalChassis(self.app, None)
        self.arglist = []
        self.verifylist = []
        self.collist = (
            'description',
            'extra',
            'uuid',
        )
        self.datalist = (
            baremetal_fakes.baremetal_chassis_description,
            baremetal_fakes.baremetal_chassis_extra,
            baremetal_fakes.baremetal_chassis_uuid,
        )
        self.actual_kwargs = {}

    def check_with_options(self, addl_arglist, addl_verifylist, addl_kwargs):
        arglist = copy.copy(self.arglist) + addl_arglist
        verifylist = copy.copy(self.verifylist) + addl_verifylist

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        collist = copy.copy(self.collist)
        self.assertEqual(collist, columns)
        self.assertNotIn('nodes', columns)

        datalist = copy.copy(self.datalist)
        self.assertEqual(datalist, tuple(data))

        kwargs = copy.copy(self.actual_kwargs)
        kwargs.update(addl_kwargs)

        self.baremetal_mock.chassis.create.assert_called_once_with(**kwargs)

    def test_chassis_create_no_options(self):
        self.check_with_options([], [], {})

    def test_chassis_create_with_description(self):
        description = 'chassis description'
        self.check_with_options(['--description', description],
                                [('description', description)],
                                {'description': description})

    def test_chassis_create_with_extra(self):
        extra1 = 'arg1=val1'
        extra2 = 'arg2=val2'
        self.check_with_options(['--extra', extra1,
                                 '--extra', extra2],
                                [('extra', [extra1, extra2])],
                                {'extra': {
                                    'arg1': 'val1',
                                    'arg2': 'val2'}})

    def test_chassis_create_with_uuid(self):
        uuid = baremetal_fakes.baremetal_chassis_uuid
        self.check_with_options(['--uuid', uuid],
                                [('uuid', uuid)],
                                {'uuid': uuid})


class TestChassisDelete(TestChassis):
    def setUp(self):
        super(TestChassisDelete, self).setUp()

        self.baremetal_mock.chassis.get.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.BAREMETAL_CHASSIS),
                loaded=True,
            ))

        # Get the command object to test
        self.cmd = baremetal_chassis.DeleteBaremetalChassis(self.app, None)

    def test_chassis_delete(self):
        uuid = baremetal_fakes.baremetal_chassis_uuid
        arglist = [uuid]
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.chassis.delete.assert_called_with(uuid)

    def test_chassis_delete_multiple(self):
        uuid1 = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
        uuid2 = '11111111-2222-3333-4444-555555555555'
        arglist = [uuid1, uuid2]
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Set expected values
        args = [uuid1, uuid2]
        self.baremetal_mock.chassis.delete.assert_has_calls(
            [mock.call(x) for x in args]
        )
        self.assertEqual(2, self.baremetal_mock.chassis.delete.call_count)

    def test_chassis_delete_multiple_with_failure(self):
        uuid1 = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
        uuid2 = '11111111-2222-3333-4444-555555555555'
        arglist = [uuid1, uuid2]
        verifylist = []

        self.baremetal_mock.chassis.delete.side_effect = [
            '', exc.ClientException]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(exc.ClientException,
                          self.cmd.take_action,
                          parsed_args)

        # Set expected values
        args = [uuid1, uuid2]
        self.baremetal_mock.chassis.delete.assert_has_calls(
            [mock.call(x) for x in args]
        )
        self.assertEqual(2, self.baremetal_mock.chassis.delete.call_count)


class TestChassisList(TestChassis):

    def setUp(self):
        super(TestChassisList, self).setUp()

        self.baremetal_mock.chassis.list.return_value = [
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.BAREMETAL_CHASSIS),
                loaded=True,
            ),
        ]

        # Get the command object to test
        self.cmd = baremetal_chassis.ListBaremetalChassis(self.app, None)

    def test_chassis_list_no_options(self):
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

        self.baremetal_mock.chassis.list.assert_called_with(
            **kwargs
        )

        collist = (
            "UUID",
            "Description",
        )
        self.assertEqual(collist, columns)
        datalist = ((
            baremetal_fakes.baremetal_chassis_uuid,
            baremetal_fakes.baremetal_chassis_description,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_chassis_list_long(self):
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

        self.baremetal_mock.chassis.list.assert_called_with(
            **kwargs
        )

        collist = ('UUID', 'Description', 'Created At', 'Updated At', 'Extra')
        self.assertEqual(collist, columns)
        datalist = ((
            baremetal_fakes.baremetal_chassis_uuid,
            baremetal_fakes.baremetal_chassis_description,
            '',
            '',
            baremetal_fakes.baremetal_chassis_extra,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_chassis_list_fields(self):
        arglist = [
            '--fields', 'uuid', 'extra',
        ]
        verifylist = [
            ('fields', [['uuid', 'extra']]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'marker': None,
            'limit': None,
            'detail': False,
            'fields': ('uuid', 'extra'),
        }

        self.baremetal_mock.chassis.list.assert_called_with(
            **kwargs
        )

    def test_chassis_list_fields_multiple(self):
        arglist = [
            '--fields', 'uuid', 'description',
            '--fields', 'extra',
        ]
        verifylist = [
            ('fields', [['uuid', 'description'], ['extra']])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'marker': None,
            'limit': None,
            'detail': False,
            'fields': ('uuid', 'description', 'extra')
        }

        self.baremetal_mock.chassis.list.assert_called_with(
            **kwargs
        )

    def test_chassis_list_invalid_fields(self):
        arglist = [
            '--fields', 'uuid', 'invalid'
        ]
        verifylist = [
            ('fields', [['uuid', 'invalid']])
        ]

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_chassis_list_long_and_fields(self):
        arglist = [
            '--long',
            '--fields', 'uuid', 'invalid'
        ]
        verifylist = [
            ('long', True),
            ('fields', [['uuid', 'invalid']])
        ]

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestChassisSet(TestChassis):
    def setUp(self):
        super(TestChassisSet, self).setUp()

        self.baremetal_mock.chassis.update.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.BAREMETAL_CHASSIS),
                loaded=True,
            ))

        # Get the command object to test
        self.cmd = baremetal_chassis.SetBaremetalChassis(self.app, None)

    def test_chassis_set_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_chassis_set_no_property(self):
        uuid = baremetal_fakes.baremetal_chassis_uuid
        arglist = [uuid]
        verifylist = [('chassis', uuid)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.assertFalse(self.baremetal_mock.chassis.update.called)

    def test_chassis_set_description(self):
        description = 'new description'
        uuid = baremetal_fakes.baremetal_chassis_uuid
        arglist = [
            uuid,
            '--description', 'new description',
        ]
        verifylist = [
            ('chassis', uuid),
            ('description', description)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.chassis.update.assert_called_once_with(
            uuid,
            [{'path': '/description', 'value': description, 'op': 'add'}]
        )

    def test_chassis_set_extra(self):
        uuid = baremetal_fakes.baremetal_chassis_uuid
        extra = 'foo=bar'
        arglist = [
            uuid,
            '--extra', extra,
        ]
        verifylist = [
            ('chassis', uuid),
            ('extra', [extra])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.chassis.update.assert_called_once_with(
            uuid,
            [{'path': '/extra/foo', 'value': 'bar', 'op': 'add'}]
        )


class TestChassisShow(TestChassis):
    def setUp(self):
        super(TestChassisShow, self).setUp()

        self.baremetal_mock.chassis.get.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.BAREMETAL_CHASSIS),
                loaded=True,
            ))

        # Get the command object to test
        self.cmd = baremetal_chassis.ShowBaremetalChassis(self.app, None)

    def test_chassis_show(self):
        arglist = [baremetal_fakes.baremetal_chassis_uuid]
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        args = [baremetal_fakes.baremetal_chassis_uuid]

        self.baremetal_mock.chassis.get.assert_called_with(
            *args, fields=None
        )

        collist = (
            'description',
            'extra',
            'uuid'
        )
        self.assertEqual(collist, columns)
        self.assertNotIn('nodes', columns)
        datalist = (
            baremetal_fakes.baremetal_chassis_description,
            baremetal_fakes.baremetal_chassis_extra,
            baremetal_fakes.baremetal_chassis_uuid,
        )
        self.assertEqual(datalist, tuple(data))

    def test_chassis_show_no_chassis(self):
        arglist = []
        verifylist = []

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_chassis_show_fields(self):
        uuid = baremetal_fakes.baremetal_chassis_uuid
        arglist = [
            uuid,
            '--fields', 'uuid', 'description',
        ]
        verifylist = [
            ('chassis', uuid),
            ('fields', [['uuid', 'description']]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Set expected values
        args = [uuid]
        fields = ['uuid', 'description']

        self.baremetal_mock.chassis.get.assert_called_with(
            *args, fields=fields
        )

    def test_chassis_show_fields_multiple(self):
        uuid = baremetal_fakes.baremetal_chassis_uuid
        arglist = [
            uuid,
            '--fields', 'uuid', 'description',
            '--fields', 'extra',
        ]
        verifylist = [
            ('chassis', uuid),
            ('fields', [['uuid', 'description'], ['extra']])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Set expected values
        args = [uuid]
        fields = ['uuid', 'description', 'extra']

        self.baremetal_mock.chassis.get.assert_called_with(
            *args, fields=fields
        )

    def test_chassis_show_invalid_fields(self):
        uuid = baremetal_fakes.baremetal_chassis_uuid
        arglist = [
            uuid,
            '--fields', 'uuid', 'invalid'
        ]
        verifylist = [
            ('chassis', uuid),
            ('fields', [['uuid', 'invalid']])
        ]

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestChassisUnset(TestChassis):
    def setUp(self):
        super(TestChassisUnset, self).setUp()

        self.baremetal_mock.chassis.update.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.BAREMETAL_CHASSIS),
                loaded=True,
            ))

        # Get the command object to test
        self.cmd = baremetal_chassis.UnsetBaremetalChassis(self.app, None)

    def test_chassis_unset_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_chassis_unset_no_property(self):
        uuid = baremetal_fakes.baremetal_chassis_uuid
        arglist = [uuid]
        verifylist = [('chassis', uuid)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.assertFalse(self.baremetal_mock.chassis.update.called)

    def test_chassis_unset_description(self):
        uuid = baremetal_fakes.baremetal_chassis_uuid
        arglist = [
            uuid,
            '--description',
        ]
        verifylist = [
            ('chassis', uuid),
            ('description', True)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.chassis.update.assert_called_once_with(
            uuid,
            [{'path': '/description', 'op': 'remove'}]
        )

    def test_chassis_unset_extra(self):
        uuid = baremetal_fakes.baremetal_chassis_uuid
        arglist = [
            uuid,
            '--extra', 'foo',
        ]
        verifylist = [
            ('chassis', uuid),
            ('extra', ['foo'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.chassis.update.assert_called_once_with(
            uuid,
            [{'path': '/extra/foo', 'op': 'remove'}]
        )
