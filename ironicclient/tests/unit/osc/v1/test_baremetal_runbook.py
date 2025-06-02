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
import json
from unittest import mock

from osc_lib.tests import utils as osctestutils

from ironicclient import exc
from ironicclient.osc.v1 import baremetal_runbook
from ironicclient.tests.unit.osc.v1 import fakes as baremetal_fakes


class TestBaremetalRunbook(baremetal_fakes.TestBaremetal):

    def setUp(self):
        super(TestBaremetalRunbook, self).setUp()

        self.baremetal_mock = self.app.client_manager.baremetal
        self.baremetal_mock.reset_mock()


class TestCreateBaremetalRunbook(TestBaremetalRunbook):
    def setUp(self):
        super(TestCreateBaremetalRunbook, self).setUp()

        self.baremetal_mock.runbook.create.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.RUNBOOK),
                loaded=True,
            ))

        # Get the command object to test
        self.cmd = baremetal_runbook.CreateBaremetalRunbook(
            self.app, None)

    def test_baremetal_runbook_create(self):
        arglist = [
            '--name', baremetal_fakes.baremetal_runbook_name,
            '--steps', baremetal_fakes.baremetal_runbook_steps,
        ]

        verifylist = [
            ('name', baremetal_fakes.baremetal_runbook_name),
            ('steps', baremetal_fakes.baremetal_runbook_steps),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Set expected values
        args = {
            'name': baremetal_fakes.baremetal_runbook_name,
            'steps': json.loads(
                baremetal_fakes.baremetal_runbook_steps),
        }

        self.baremetal_mock.runbook.create.assert_called_once_with(
            **args)

    def test_baremetal_runbook_create_uuid(self):
        arglist = [
            '--name', baremetal_fakes.baremetal_runbook_name,
            '--steps', baremetal_fakes.baremetal_runbook_steps,
            '--uuid', baremetal_fakes.baremetal_runbook_uuid,
        ]

        verifylist = [
            ('name', baremetal_fakes.baremetal_runbook_name),
            ('steps', baremetal_fakes.baremetal_runbook_steps),
            ('uuid', baremetal_fakes.baremetal_runbook_uuid),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Set expected values
        args = {
            'name': baremetal_fakes.baremetal_runbook_name,
            'steps': json.loads(
                baremetal_fakes.baremetal_runbook_steps),
            'uuid': baremetal_fakes.baremetal_runbook_uuid,
        }

        self.baremetal_mock.runbook.create.assert_called_once_with(
            **args)

    def test_baremetal_runbook_create_no_name(self):
        arglist = [
            '--steps', baremetal_fakes.baremetal_runbook_steps,
        ]

        verifylist = [
            ('steps', baremetal_fakes.baremetal_runbook_steps),
        ]

        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)
        self.assertFalse(self.baremetal_mock.runbook.create.called)

    def test_baremetal_runbook_create_no_steps(self):
        arglist = [
            '--name', baremetal_fakes.baremetal_runbook_name,
        ]

        verifylist = [
            ('name', baremetal_fakes.baremetal_runbook_name),
        ]

        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)
        self.assertFalse(self.baremetal_mock.runbook.create.called)

    def test_baremetal_runbook_create_public_false(self):
        arglist = [
            '--name', baremetal_fakes.baremetal_runbook_name,
            '--steps', baremetal_fakes.baremetal_runbook_steps,
            '--public', 'false',
        ]
        verifylist = [
            ('name', baremetal_fakes.baremetal_runbook_name),
            ('steps', baremetal_fakes.baremetal_runbook_steps),
            ('public', 'false'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        expected = {
            'name': baremetal_fakes.baremetal_runbook_name,
            'steps': json.loads(baremetal_fakes.baremetal_runbook_steps),
            'public': False,
        }
        self.baremetal_mock.runbook.create.assert_called_once_with(**expected)


class TestShowBaremetalRunbook(TestBaremetalRunbook):
    def setUp(self):
        super(TestShowBaremetalRunbook, self).setUp()

        self.baremetal_mock.runbook.get.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.RUNBOOK),
                loaded=True))

        self.cmd = baremetal_runbook.ShowBaremetalRunbook(
            self.app, None)

    def test_baremetal_runbook_show(self):
        arglist = [baremetal_fakes.baremetal_runbook_uuid]
        verifylist = [('runbook',
                      baremetal_fakes.baremetal_runbook_uuid)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        args = [baremetal_fakes.baremetal_runbook_uuid]
        self.baremetal_mock.runbook.get.assert_called_with(
            *args, fields=None)

        collist = (
            'extra',
            'name',
            'owner',
            'public',
            'steps',
            'uuid')
        self.assertEqual(collist, columns)

        datalist = (
            baremetal_fakes.baremetal_runbook_extra,
            baremetal_fakes.baremetal_runbook_name,
            baremetal_fakes.baremetal_runbook_owner,
            baremetal_fakes.baremetal_runbook_public,
            baremetal_fakes.baremetal_runbook_steps,
            baremetal_fakes.baremetal_runbook_uuid)
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_runbook_show_no_template(self):
        arglist = []
        verifylist = []

        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestBaremetalRunbookSet(TestBaremetalRunbook):
    def setUp(self):
        super(TestBaremetalRunbookSet, self).setUp()

        self.baremetal_mock.runbook.update.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.RUNBOOK),
                loaded=True))

        self.cmd = baremetal_runbook.SetBaremetalRunbook(
            self.app, None)

    def test_baremetal_runbook_set_name(self):
        new_name = 'foo'
        arglist = [
            baremetal_fakes.baremetal_runbook_uuid,
            '--name', new_name]
        verifylist = [
            ('runbook', baremetal_fakes.baremetal_runbook_uuid),
            ('name', new_name)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.runbook.update.assert_called_once_with(
            baremetal_fakes.baremetal_runbook_uuid,
            [{'path': '/name', 'value': new_name, 'op': 'add'}])

    def test_baremetal_runbook_set_steps(self):
        arglist = [
            baremetal_fakes.baremetal_runbook_uuid,
            '--steps', baremetal_fakes.baremetal_runbook_steps]
        verifylist = [
            ('runbook', baremetal_fakes.baremetal_runbook_uuid),
            ('steps', baremetal_fakes.baremetal_runbook_steps)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        expected_steps = json.loads(
            baremetal_fakes.baremetal_runbook_steps)
        self.cmd.take_action(parsed_args)
        self.baremetal_mock.runbook.update.assert_called_once_with(
            baremetal_fakes.baremetal_runbook_uuid,
            [{'path': '/steps', 'value': expected_steps, 'op': 'add'}])

    def test_baremetal_runbook_set_no_options(self):
        arglist = []
        verifylist = []
        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestBaremetalRunbookUnset(TestBaremetalRunbook):
    def setUp(self):
        super(TestBaremetalRunbookUnset, self).setUp()

        self.baremetal_mock.runbook.update.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.RUNBOOK),
                loaded=True))

        self.cmd = baremetal_runbook.UnsetBaremetalRunbook(
            self.app, None)

    def test_baremetal_runbook_unset_extra(self):
        arglist = [
            baremetal_fakes.baremetal_runbook_uuid, '--extra', 'key1']
        verifylist = [('runbook',
                       baremetal_fakes.baremetal_runbook_uuid),
                      ('extra', ['key1'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.runbook.update.assert_called_once_with(
            baremetal_fakes.baremetal_runbook_uuid,
            [{'path': '/extra/key1', 'op': 'remove'}])

    def test_baremetal_runbook_unset_multiple_extras(self):
        arglist = [
            baremetal_fakes.baremetal_runbook_uuid,
            '--extra', 'key1', '--extra', 'key2']
        verifylist = [('runbook',
                       baremetal_fakes.baremetal_runbook_uuid),
                      ('extra', ['key1', 'key2'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.runbook.update.assert_called_once_with(
            baremetal_fakes.baremetal_runbook_uuid,
            [{'path': '/extra/key1', 'op': 'remove'},
             {'path': '/extra/key2', 'op': 'remove'}])

    def test_baremetal_runbook_unset_no_options(self):
        arglist = []
        verifylist = []
        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_runbook_unset_no_property(self):
        uuid = baremetal_fakes.baremetal_runbook_uuid
        arglist = [uuid]
        verifylist = [('runbook', uuid)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.assertFalse(self.baremetal_mock.runbook.update.called)


class TestBaremetalRunbookDelete(TestBaremetalRunbook):
    def setUp(self):
        super(TestBaremetalRunbookDelete, self).setUp()

        self.cmd = baremetal_runbook.DeleteBaremetalRunbook(
            self.app, None)

    def test_baremetal_runbook_delete(self):
        arglist = ['zzz-zzzzzz-zzzz']
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        args = 'zzz-zzzzzz-zzzz'
        self.baremetal_mock.runbook.delete.assert_called_with(args)

    def test_baremetal_runbook_delete_multiple(self):
        arglist = ['zzz-zzzzzz-zzzz', 'fakename']
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        args = ['zzz-zzzzzz-zzzz', 'fakename']
        self.baremetal_mock.runbook.delete.assert_has_calls(
            [mock.call(x) for x in args])
        self.assertEqual(
            2, self.baremetal_mock.runbook.delete.call_count)

    def test_baremetal_runbook_delete_multiple_with_fail(self):
        arglist = ['zzz-zzzzzz-zzzz', 'badname']
        verifylist = []

        self.baremetal_mock.runbook.delete.side_effect = [
            '', exc.ClientException]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exc.ClientException,
                          self.cmd.take_action,
                          parsed_args)

        args = ['zzz-zzzzzz-zzzz', 'badname']
        self.baremetal_mock.runbook.delete.assert_has_calls(
            [mock.call(x) for x in args])
        self.assertEqual(
            2, self.baremetal_mock.runbook.delete.call_count)

    def test_baremetal_runbook_delete_no_template(self):
        arglist = []
        verifylist = []

        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestBaremetalRunbookList(TestBaremetalRunbook):
    def setUp(self):
        super(TestBaremetalRunbookList, self).setUp()

        self.baremetal_mock.runbook.list.return_value = [
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.RUNBOOK),
                loaded=True)
        ]

        self.cmd = baremetal_runbook.ListBaremetalRunbook(
            self.app, None)

    def test_baremetal_runbook_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'marker': None,
            'limit': None}
        self.baremetal_mock.runbook.list.assert_called_with(**kwargs)

        collist = (
            "UUID",
            "Name")
        self.assertEqual(collist, columns)

        datalist = ((
            baremetal_fakes.baremetal_runbook_uuid,
            baremetal_fakes.baremetal_runbook_name
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_runbook_list_long(self):
        arglist = ['--long']
        verifylist = [('detail', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'detail': True,
            'marker': None,
            'limit': None,
        }
        self.baremetal_mock.runbook.list.assert_called_with(**kwargs)

        collist = ('UUID',
                   'Name',
                   'Owner',
                   'Public',
                   'Steps',
                   'Extra',
                   'Created At',
                   'Updated At')
        self.assertEqual(collist, columns)

        datalist = ((
            baremetal_fakes.baremetal_runbook_uuid,
            baremetal_fakes.baremetal_runbook_name,
            baremetal_fakes.baremetal_runbook_owner,
            baremetal_fakes.baremetal_runbook_public,
            baremetal_fakes.baremetal_runbook_steps,
            baremetal_fakes.baremetal_runbook_extra,
            '',
            '',
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_runbook_list_fields(self):
        arglist = ['--fields', 'uuid', 'steps']
        verifylist = [('fields', [['uuid', 'steps']])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        kwargs = {
            'marker': None,
            'limit': None,
            'detail': False,
            'fields': ('uuid', 'steps')
        }
        self.baremetal_mock.runbook.list.assert_called_with(**kwargs)

    def test_baremetal_runbook_list_fields_multiple(self):
        arglist = ['--fields', 'uuid', 'name', '--fields', 'steps']
        verifylist = [('fields', [['uuid', 'name'], ['steps']])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        kwargs = {
            'marker': None,
            'limit': None,
            'detail': False,
            'fields': ('uuid', 'name', 'steps')
        }
        self.baremetal_mock.runbook.list.assert_called_with(**kwargs)

    def test_baremetal_runbook_list_invalid_fields(self):
        arglist = ['--fields', 'uuid', 'invalid']
        verifylist = [('fields', [['uuid', 'invalid']])]
        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)
