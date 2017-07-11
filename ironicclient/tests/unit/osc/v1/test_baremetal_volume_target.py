# Copyright 2017 FUJITSU LIMITED
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

import copy

import mock
from osc_lib.tests import utils as osctestutils

from ironicclient import exc
from ironicclient.osc.v1 import baremetal_volume_target as bm_vol_target
from ironicclient.tests.unit.osc.v1 import fakes as baremetal_fakes


class TestBaremetalVolumeTarget(baremetal_fakes.TestBaremetal):

    def setUp(self):
        super(TestBaremetalVolumeTarget, self).setUp()

        self.baremetal_mock = self.app.client_manager.baremetal
        self.baremetal_mock.reset_mock()


class TestCreateBaremetalVolumeTarget(TestBaremetalVolumeTarget):

    def setUp(self):
        super(TestCreateBaremetalVolumeTarget, self).setUp()

        self.baremetal_mock.volume_target.create.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.VOLUME_TARGET),
                loaded=True,
            ))

        # Get the command object to test
        self.cmd = (
            bm_vol_target.CreateBaremetalVolumeTarget(self.app, None))

    def test_baremetal_volume_target_create(self):
        arglist = [
            '--node', baremetal_fakes.baremetal_uuid,
            '--type',
            baremetal_fakes.baremetal_volume_target_volume_type,
            '--boot-index',
            baremetal_fakes.baremetal_volume_target_boot_index,
            '--volume-id',
            baremetal_fakes.baremetal_volume_target_volume_id,
            '--uuid', baremetal_fakes.baremetal_volume_target_uuid,
        ]

        verifylist = [
            ('node_uuid', baremetal_fakes.baremetal_uuid),
            ('volume_type',
             baremetal_fakes.baremetal_volume_target_volume_type),
            ('boot_index',
             baremetal_fakes.baremetal_volume_target_boot_index),
            ('volume_id',
             baremetal_fakes.baremetal_volume_target_volume_id),
            ('uuid', baremetal_fakes.baremetal_volume_target_uuid),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        args = {
            'node_uuid': baremetal_fakes.baremetal_uuid,
            'volume_type':
                baremetal_fakes.baremetal_volume_target_volume_type,
            'boot_index':
                baremetal_fakes.baremetal_volume_target_boot_index,
            'volume_id':
                baremetal_fakes.baremetal_volume_target_volume_id,
            'uuid': baremetal_fakes.baremetal_volume_target_uuid,
        }

        self.baremetal_mock.volume_target.create.assert_called_once_with(
            **args)

    def test_baremetal_volume_target_create_without_uuid(self):
        arglist = [
            '--node', baremetal_fakes.baremetal_uuid,
            '--type',
            baremetal_fakes.baremetal_volume_target_volume_type,
            '--boot-index',
            baremetal_fakes.baremetal_volume_target_boot_index,
            '--volume-id',
            baremetal_fakes.baremetal_volume_target_volume_id,
        ]

        verifylist = [
            ('node_uuid', baremetal_fakes.baremetal_uuid),
            ('volume_type',
             baremetal_fakes.baremetal_volume_target_volume_type),
            ('boot_index',
             baremetal_fakes.baremetal_volume_target_boot_index),
            ('volume_id',
             baremetal_fakes.baremetal_volume_target_volume_id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        args = {
            'node_uuid': baremetal_fakes.baremetal_uuid,
            'volume_type':
                baremetal_fakes.baremetal_volume_target_volume_type,
            'boot_index':
                baremetal_fakes.baremetal_volume_target_boot_index,
            'volume_id':
                baremetal_fakes.baremetal_volume_target_volume_id,
        }

        self.baremetal_mock.volume_target.create.assert_called_once_with(
            **args)

    def test_baremetal_volume_target_create_extras(self):
        arglist = [
            '--node', baremetal_fakes.baremetal_uuid,
            '--type',
            baremetal_fakes.baremetal_volume_target_volume_type,
            '--boot-index',
            baremetal_fakes.baremetal_volume_target_boot_index,
            '--volume-id',
            baremetal_fakes.baremetal_volume_target_volume_id,
            '--extra', 'key1=value1',
            '--extra', 'key2=value2',
        ]

        verifylist = [
            ('node_uuid', baremetal_fakes.baremetal_uuid),
            ('volume_type',
             baremetal_fakes.baremetal_volume_target_volume_type),
            ('boot_index',
             baremetal_fakes.baremetal_volume_target_boot_index),
            ('volume_id',
             baremetal_fakes.baremetal_volume_target_volume_id),
            ('extra', ['key1=value1', 'key2=value2'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        args = {
            'node_uuid': baremetal_fakes.baremetal_uuid,
            'volume_type':
                baremetal_fakes.baremetal_volume_target_volume_type,
            'boot_index':
                baremetal_fakes.baremetal_volume_target_boot_index,
            'volume_id':
                baremetal_fakes.baremetal_volume_target_volume_id,
            'extra': baremetal_fakes.baremetal_volume_target_extra,
        }

        self.baremetal_mock.volume_target.create.assert_called_once_with(
            **args)

    def _test_baremetal_volume_target_missing_param(self, missing):
        argdict = {
            '--node': baremetal_fakes.baremetal_uuid,
            '--type':
                baremetal_fakes.baremetal_volume_target_volume_type,
            '--boot-index':
                baremetal_fakes.baremetal_volume_target_boot_index,
            '--volume-id':
                baremetal_fakes.baremetal_volume_target_volume_id,
            '--uuid': baremetal_fakes.baremetal_volume_target_uuid,
        }

        arglist = []
        for k, v in argdict.items():
            if k not in missing:
                arglist += [k, v]
        verifylist = None

        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_volume_target_create_missing_node(self):
        self._test_baremetal_volume_target_missing_param(['--node'])

    def test_baremetal_volume_target_create_missing_type(self):
        self._test_baremetal_volume_target_missing_param(['--type'])

    def test_baremetal_volume_target_create_missing_boot_index(self):
        self._test_baremetal_volume_target_missing_param(['--boot-index'])

    def test_baremetal_volume_target_create_missing_volume_id(self):
        self._test_baremetal_volume_target_missing_param(['--volume-id'])

    def test_baremetal_volume_target_create_invalid_boot_index(self):
        arglist = [
            '--node', baremetal_fakes.baremetal_uuid,
            '--type',
            baremetal_fakes.baremetal_volume_target_volume_type,
            '--boot-index', 'string',
            '--volume-id',
            baremetal_fakes.baremetal_volume_target_volume_id,
        ]
        verifylist = None

        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_volume_target_create_negative_boot_index(self):
        arglist = [
            '--node', baremetal_fakes.baremetal_uuid,
            '--type',
            baremetal_fakes.baremetal_volume_target_volume_type,
            '--boot-index', '-1',
            '--volume-id',
            baremetal_fakes.baremetal_volume_target_volume_id,
        ]

        verifylist = [
            ('node_uuid', baremetal_fakes.baremetal_uuid),
            ('volume_type',
             baremetal_fakes.baremetal_volume_target_volume_type),
            ('boot_index', -1),
            ('volume_id',
             baremetal_fakes.baremetal_volume_target_volume_id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(exc.CommandError, self.cmd.take_action, parsed_args)


class TestShowBaremetalVolumeTarget(TestBaremetalVolumeTarget):

    def setUp(self):
        super(TestShowBaremetalVolumeTarget, self).setUp()

        self.baremetal_mock.volume_target.get.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.VOLUME_TARGET),
                loaded=True))

        self.cmd = (
            bm_vol_target.ShowBaremetalVolumeTarget(self.app, None))

    def test_baremetal_volume_target_show(self):
        arglist = ['vvv-tttttt-vvvv']
        verifylist = [('volume_target',
                       baremetal_fakes.baremetal_volume_target_uuid)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        args = ['vvv-tttttt-vvvv']
        self.baremetal_mock.volume_target.get.assert_called_once_with(
            *args, fields=None)
        collist = ('boot_index', 'extra', 'node_uuid', 'properties', 'uuid',
                   'volume_id', 'volume_type')
        self.assertEqual(collist, columns)

        datalist = (
            baremetal_fakes.baremetal_volume_target_boot_index,
            baremetal_fakes.baremetal_volume_target_extra,
            baremetal_fakes.baremetal_uuid,
            baremetal_fakes.baremetal_volume_target_properties,
            baremetal_fakes.baremetal_volume_target_uuid,
            baremetal_fakes.baremetal_volume_target_volume_id,
            baremetal_fakes.baremetal_volume_target_volume_type,
        )
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_volume_target_show_no_options(self):
        arglist = []
        verifylist = []
        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_volume_target_show_fields(self):
        arglist = ['vvv-tttttt-vvvv', '--fields', 'uuid', 'volume_id']
        verifylist = [('fields', [['uuid', 'volume_id']]),
                      ('volume_target',
                       baremetal_fakes.baremetal_volume_target_uuid)]

        fake_vt = copy.deepcopy(baremetal_fakes.VOLUME_TARGET)
        fake_vt.pop('node_uuid')
        fake_vt.pop('volume_type')
        fake_vt.pop('boot_index')
        fake_vt.pop('extra')
        fake_vt.pop('properties')
        self.baremetal_mock.volume_target.get.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                fake_vt,
                loaded=True))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        args = ['vvv-tttttt-vvvv']
        fields = ['uuid', 'volume_id']
        self.baremetal_mock.volume_target.get.assert_called_once_with(
            *args, fields=fields)
        collist = ('uuid', 'volume_id')
        self.assertEqual(collist, columns)

        datalist = (
            baremetal_fakes.baremetal_volume_target_uuid,
            baremetal_fakes.baremetal_volume_target_volume_id,
        )
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_volume_target_show_fields_multiple(self):
        arglist = ['vvv-tttttt-vvvv', '--fields', 'uuid', 'volume_id',
                   '--fields', 'volume_type']
        verifylist = [('fields', [['uuid', 'volume_id'], ['volume_type']]),
                      ('volume_target',
                       baremetal_fakes.baremetal_volume_target_uuid)]

        fake_vt = copy.deepcopy(baremetal_fakes.VOLUME_TARGET)
        fake_vt.pop('node_uuid')
        fake_vt.pop('boot_index')
        fake_vt.pop('extra')
        fake_vt.pop('properties')
        self.baremetal_mock.volume_target.get.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                fake_vt,
                loaded=True))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        args = ['vvv-tttttt-vvvv']
        fields = ['uuid', 'volume_id', 'volume_type']
        self.baremetal_mock.volume_target.get.assert_called_once_with(
            *args, fields=fields)
        collist = ('uuid', 'volume_id', 'volume_type')
        self.assertEqual(collist, columns)

        datalist = (
            baremetal_fakes.baremetal_volume_target_uuid,
            baremetal_fakes.baremetal_volume_target_volume_id,
            baremetal_fakes.baremetal_volume_target_volume_type,
        )
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_volume_target_show_invalid_fields(self):
        arglist = ['vvv-tttttt-vvvv', '--fields', 'uuid', 'invalid']
        verifylist = None

        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestListBaremetalVolumeTarget(TestBaremetalVolumeTarget):
    def setUp(self):
        super(TestListBaremetalVolumeTarget, self).setUp()

        self.baremetal_mock.volume_target.list.return_value = [
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.VOLUME_TARGET),
                loaded=True)
        ]
        self.cmd = (
            bm_vol_target.ListBaremetalVolumeTarget(self.app, None))

    def test_baremetal_volume_target_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'marker': None,
            'limit': None}
        self.baremetal_mock.volume_target.list.assert_called_once_with(
            **kwargs)

        collist = (
            "UUID",
            "Node UUID",
            "Driver Volume Type",
            "Boot Index",
            "Volume ID")
        self.assertEqual(collist, columns)

        datalist = ((baremetal_fakes.baremetal_volume_target_uuid,
                     baremetal_fakes.baremetal_uuid,
                     baremetal_fakes.baremetal_volume_target_volume_type,
                     baremetal_fakes.baremetal_volume_target_boot_index,
                     baremetal_fakes.baremetal_volume_target_volume_id),)
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_volume_target_list_node(self):
        arglist = ['--node', baremetal_fakes.baremetal_uuid]
        verifylist = [('node', baremetal_fakes.baremetal_uuid)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'node': baremetal_fakes.baremetal_uuid,
            'marker': None,
            'limit': None}
        self.baremetal_mock.volume_target.list.assert_called_once_with(
            **kwargs)

        collist = (
            "UUID",
            "Node UUID",
            "Driver Volume Type",
            "Boot Index",
            "Volume ID")
        self.assertEqual(collist, columns)

        datalist = ((baremetal_fakes.baremetal_volume_target_uuid,
                     baremetal_fakes.baremetal_uuid,
                     baremetal_fakes.baremetal_volume_target_volume_type,
                     baremetal_fakes.baremetal_volume_target_boot_index,
                     baremetal_fakes.baremetal_volume_target_volume_id),)
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_volume_target_list_long(self):
        arglist = ['--long']
        verifylist = [('detail', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'detail': True,
            'marker': None,
            'limit': None,
        }
        self.baremetal_mock.volume_target.list.assert_called_with(**kwargs)

        collist = ('UUID', 'Node UUID', 'Driver Volume Type', 'Properties',
                   'Boot Index', 'Extra', 'Volume ID', 'Created At',
                   'Updated At')
        self.assertEqual(collist, columns)

        datalist = ((baremetal_fakes.baremetal_volume_target_uuid,
                     baremetal_fakes.baremetal_uuid,
                     baremetal_fakes.baremetal_volume_target_volume_type,
                     baremetal_fakes.baremetal_volume_target_properties,
                     baremetal_fakes.baremetal_volume_target_boot_index,
                     baremetal_fakes.baremetal_volume_target_extra,
                     baremetal_fakes.baremetal_volume_target_volume_id,
                     '',
                     ''),)
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_volume_target_list_fields(self):
        arglist = ['--fields', 'uuid', 'boot_index']
        verifylist = [('fields', [['uuid', 'boot_index']])]

        fake_vt = copy.deepcopy(baremetal_fakes.VOLUME_TARGET)
        fake_vt.pop('volume_type')
        fake_vt.pop('extra')
        fake_vt.pop('properties')
        fake_vt.pop('volume_id')
        fake_vt.pop('node_uuid')
        self.baremetal_mock.volume_target.list.return_value = [
            baremetal_fakes.FakeBaremetalResource(
                None,
                fake_vt,
                loaded=True)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'detail': False,
            'marker': None,
            'limit': None,
            'fields': ('uuid', 'boot_index')
        }
        self.baremetal_mock.volume_target.list.assert_called_with(**kwargs)

        collist = ('UUID', 'Boot Index')
        self.assertEqual(collist, columns)

        datalist = ((baremetal_fakes.baremetal_volume_target_uuid,
                     baremetal_fakes.baremetal_volume_target_boot_index),)
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_volume_target_list_fields_multiple(self):
        arglist = ['--fields', 'uuid', 'boot_index', '--fields', 'extra']
        verifylist = [('fields', [['uuid', 'boot_index'], ['extra']])]

        fake_vt = copy.deepcopy(baremetal_fakes.VOLUME_TARGET)
        fake_vt.pop('volume_type')
        fake_vt.pop('properties')
        fake_vt.pop('volume_id')
        fake_vt.pop('node_uuid')
        self.baremetal_mock.volume_target.list.return_value = [
            baremetal_fakes.FakeBaremetalResource(
                None,
                fake_vt,
                loaded=True)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'detail': False,
            'marker': None,
            'limit': None,
            'fields': ('uuid', 'boot_index', 'extra')
        }
        self.baremetal_mock.volume_target.list.assert_called_with(**kwargs)

        collist = ('UUID', 'Boot Index', 'Extra')
        self.assertEqual(collist, columns)

        datalist = ((baremetal_fakes.baremetal_volume_target_uuid,
                     baremetal_fakes.baremetal_volume_target_boot_index,
                     baremetal_fakes.baremetal_volume_target_extra),)
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_volume_target_list_invalid_fields(self):
        arglist = ['--fields', 'uuid', 'invalid']
        verifylist = [('fields', [['uuid', 'invalid']])]
        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_volume_target_list_marker(self):
        arglist = ['--marker', baremetal_fakes.baremetal_volume_target_uuid]
        verifylist = [
            ('marker', baremetal_fakes.baremetal_volume_target_uuid)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        kwargs = {
            'marker': baremetal_fakes.baremetal_volume_target_uuid,
            'limit': None}
        self.baremetal_mock.volume_target.list.assert_called_once_with(
            **kwargs)

    def test_baremetal_volume_target_list_limit(self):
        arglist = ['--limit', '10']
        verifylist = [('limit', 10)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        kwargs = {
            'marker': None,
            'limit': 10}
        self.baremetal_mock.volume_target.list.assert_called_once_with(
            **kwargs)

    def test_baremetal_volume_target_list_sort(self):
        arglist = ['--sort', 'boot_index']
        verifylist = [('sort', 'boot_index')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        kwargs = {
            'marker': None,
            'limit': None}
        self.baremetal_mock.volume_target.list.assert_called_once_with(
            **kwargs)

    def test_baremetal_volume_target_list_sort_desc(self):
        arglist = ['--sort', 'boot_index:desc']
        verifylist = [('sort', 'boot_index:desc')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        kwargs = {
            'marker': None,
            'limit': None}
        self.baremetal_mock.volume_target.list.assert_called_once_with(
            **kwargs)

    def test_baremetal_volume_target_list_exclusive_options(self):
        arglist = ['--fields', 'uuid', '--long']
        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, [])

    def test_baremetal_volume_target_list_negative_limit(self):
        arglist = ['--limit', '-1']
        verifylist = [('limit', -1)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exc.CommandError,
                          self.cmd.take_action,
                          parsed_args)


class TestDeleteBaremetalVolumeTarget(TestBaremetalVolumeTarget):

    def setUp(self):
        super(TestDeleteBaremetalVolumeTarget, self).setUp()

        self.cmd = bm_vol_target.DeleteBaremetalVolumeTarget(self.app, None)

    def test_baremetal_volume_target_delete(self):
        arglist = [baremetal_fakes.baremetal_volume_target_uuid]
        verifylist = [('volume_targets',
                       [baremetal_fakes.baremetal_volume_target_uuid])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.baremetal_mock.volume_target.delete.assert_called_with(
            baremetal_fakes.baremetal_volume_target_uuid)

    def test_baremetal_volume_target_delete_multiple(self):
        fake_volume_target_uuid2 = 'vvv-tttttt-tttt'
        arglist = [baremetal_fakes.baremetal_volume_target_uuid,
                   fake_volume_target_uuid2]
        verifylist = [('volume_targets',
                       [baremetal_fakes.baremetal_volume_target_uuid,
                        fake_volume_target_uuid2])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.baremetal_mock.volume_target.delete.has_calls(
            [mock.call(baremetal_fakes.baremetal_volume_target_uuid),
             mock.call(fake_volume_target_uuid2)])
        self.assertEqual(
            2, self.baremetal_mock.volume_target.delete.call_count)

    def test_baremetal_volume_target_delete_no_options(self):
        arglist = []
        verifylist = []
        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_volume_target_delete_error(self):
        arglist = [baremetal_fakes.baremetal_volume_target_uuid]
        verifylist = [('volume_targets',
                       [baremetal_fakes.baremetal_volume_target_uuid])]

        self.baremetal_mock.volume_target.delete.side_effect = (
            exc.NotFound())

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exc.ClientException,
                          self.cmd.take_action,
                          parsed_args)
        self.baremetal_mock.volume_target.delete.assert_called_with(
            baremetal_fakes.baremetal_volume_target_uuid)

    def test_baremetal_volume_target_delete_multiple_error(self):
        fake_volume_target_uuid2 = 'vvv-tttttt-tttt'
        arglist = [baremetal_fakes.baremetal_volume_target_uuid,
                   fake_volume_target_uuid2]
        verifylist = [('volume_targets',
                       [baremetal_fakes.baremetal_volume_target_uuid,
                        fake_volume_target_uuid2])]

        self.baremetal_mock.volume_target.delete.side_effect = [
            None, exc.NotFound()]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exc.ClientException,
                          self.cmd.take_action,
                          parsed_args)

        self.baremetal_mock.volume_target.delete.has_calls(
            [mock.call(baremetal_fakes.baremetal_volume_target_uuid),
             mock.call(fake_volume_target_uuid2)])
        self.assertEqual(
            2, self.baremetal_mock.volume_target.delete.call_count)


class TestSetBaremetalVolumeTarget(TestBaremetalVolumeTarget):
    def setUp(self):
        super(TestSetBaremetalVolumeTarget, self).setUp()

        self.cmd = (
            bm_vol_target.SetBaremetalVolumeTarget(self.app, None))

    def test_baremetal_volume_target_set_node_uuid(self):
        new_node_uuid = 'xxx-xxxxxx-zzzz'
        arglist = [
            baremetal_fakes.baremetal_volume_target_uuid,
            '--node', new_node_uuid]
        verifylist = [
            ('volume_target',
             baremetal_fakes.baremetal_volume_target_uuid),
            ('node_uuid', new_node_uuid)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.volume_target.update.assert_called_once_with(
            baremetal_fakes.baremetal_volume_target_uuid,
            [{'path': '/node_uuid', 'value': new_node_uuid, 'op': 'add'}])

    def test_baremetal_volume_target_set_volume_type(self):
        new_type = 'fibre_channel'
        arglist = [
            baremetal_fakes.baremetal_volume_target_uuid,
            '--type', new_type]
        verifylist = [
            ('volume_target',
             baremetal_fakes.baremetal_volume_target_uuid),
            ('volume_type', new_type)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.volume_target.update.assert_called_once_with(
            baremetal_fakes.baremetal_volume_target_uuid,
            [{'path': '/volume_type', 'value': new_type, 'op': 'add'}])

    def test_baremetal_volume_target_set_boot_index(self):
        new_boot_idx = '3'
        arglist = [
            baremetal_fakes.baremetal_volume_target_uuid,
            '--boot-index', new_boot_idx]
        verifylist = [
            ('volume_target',
             baremetal_fakes.baremetal_volume_target_uuid),
            ('boot_index', int(new_boot_idx))]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.volume_target.update.assert_called_once_with(
            baremetal_fakes.baremetal_volume_target_uuid,
            [{'path': '/boot_index', 'value': int(new_boot_idx), 'op': 'add'}])

    def test_baremetal_volume_target_set_negative_boot_index(self):
        new_boot_idx = '-3'
        arglist = [
            baremetal_fakes.baremetal_volume_target_uuid,
            '--boot-index', new_boot_idx]
        verifylist = [
            ('volume_target',
             baremetal_fakes.baremetal_volume_target_uuid),
            ('boot_index', int(new_boot_idx))]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(exc.CommandError, self.cmd.take_action, parsed_args)

    def test_baremetal_volume_target_set_invalid_boot_index(self):
        new_boot_idx = 'string'
        arglist = [
            baremetal_fakes.baremetal_volume_target_uuid,
            '--boot-index', new_boot_idx]
        verifylist = None

        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_volume_target_set_volume_id(self):
        new_volume_id = 'new-volume-id'
        arglist = [
            baremetal_fakes.baremetal_volume_target_uuid,
            '--volume-id', new_volume_id]
        verifylist = [
            ('volume_target',
             baremetal_fakes.baremetal_volume_target_uuid),
            ('volume_id', new_volume_id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.volume_target.update.assert_called_once_with(
            baremetal_fakes.baremetal_volume_target_uuid,
            [{'path': '/volume_id', 'value': new_volume_id, 'op': 'add'}])

    def test_baremetal_volume_target_set_volume_type_and_volume_id(self):
        new_volume_type = 'fibre_channel'
        new_volume_id = 'new-volume-id'
        arglist = [
            baremetal_fakes.baremetal_volume_target_uuid,
            '--type', new_volume_type,
            '--volume-id', new_volume_id]
        verifylist = [
            ('volume_target',
             baremetal_fakes.baremetal_volume_target_uuid),
            ('volume_type', new_volume_type),
            ('volume_id', new_volume_id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.volume_target.update.assert_called_once_with(
            baremetal_fakes.baremetal_volume_target_uuid,
            [{'path': '/volume_type', 'value': new_volume_type, 'op': 'add'},
             {'path': '/volume_id', 'value': new_volume_id, 'op': 'add'}])

    def test_baremetal_volume_target_set_extra(self):
        arglist = [
            baremetal_fakes.baremetal_volume_target_uuid,
            '--extra', 'foo=bar']
        verifylist = [
            ('volume_target',
             baremetal_fakes.baremetal_volume_target_uuid),
            ('extra', ['foo=bar'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.volume_target.update.assert_called_once_with(
            baremetal_fakes.baremetal_volume_target_uuid,
            [{'path': '/extra/foo', 'value': 'bar', 'op': 'add'}])

    def test_baremetal_volume_target_set_multiple_extras(self):
        arglist = [
            baremetal_fakes.baremetal_volume_target_uuid,
            '--extra', 'key1=val1', '--extra', 'key2=val2']
        verifylist = [
            ('volume_target',
             baremetal_fakes.baremetal_volume_target_uuid),
            ('extra', ['key1=val1', 'key2=val2'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.volume_target.update.assert_called_once_with(
            baremetal_fakes.baremetal_volume_target_uuid,
            [{'path': '/extra/key1', 'value': 'val1', 'op': 'add'},
             {'path': '/extra/key2', 'value': 'val2', 'op': 'add'}])

    def test_baremetal_volume_target_set_property(self):
        arglist = [
            baremetal_fakes.baremetal_volume_target_uuid,
            '--property', 'foo=bar']
        verifylist = [
            ('volume_target',
             baremetal_fakes.baremetal_volume_target_uuid),
            ('properties', ['foo=bar'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.volume_target.update.assert_called_once_with(
            baremetal_fakes.baremetal_volume_target_uuid,
            [{'path': '/properties/foo', 'value': 'bar', 'op': 'add'}])

    def test_baremetal_volume_target_set_multiple_properties(self):
        arglist = [
            baremetal_fakes.baremetal_volume_target_uuid,
            '--property', 'key1=val1', '--property', 'key2=val2']
        verifylist = [
            ('volume_target',
             baremetal_fakes.baremetal_volume_target_uuid),
            ('properties', ['key1=val1', 'key2=val2'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.volume_target.update.assert_called_once_with(
            baremetal_fakes.baremetal_volume_target_uuid,
            [{'path': '/properties/key1', 'value': 'val1', 'op': 'add'},
             {'path': '/properties/key2', 'value': 'val2', 'op': 'add'}])

    def test_baremetal_volume_target_set_no_options(self):
        arglist = []
        verifylist = []
        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_volume_target_set_no_property(self):
        arglist = [baremetal_fakes.baremetal_volume_target_uuid]
        verifylist = [('volume_target',
                       baremetal_fakes.baremetal_volume_target_uuid)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.baremetal_mock.volume_target.update.assert_not_called()


class TestUnsetBaremetalVolumeTarget(TestBaremetalVolumeTarget):
    def setUp(self):
        super(TestUnsetBaremetalVolumeTarget, self).setUp()

        self.cmd = bm_vol_target.UnsetBaremetalVolumeTarget(self.app, None)

    def test_baremetal_volume_target_unset_extra(self):
        arglist = [baremetal_fakes.baremetal_volume_target_uuid,
                   '--extra', 'key1']
        verifylist = [('volume_target',
                       baremetal_fakes.baremetal_volume_target_uuid),
                      ('extra', ['key1'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.volume_target.update.assert_called_once_with(
            baremetal_fakes.baremetal_volume_target_uuid,
            [{'path': '/extra/key1', 'op': 'remove'}])

    def test_baremetal_volume_target_unset_multiple_extras(self):
        arglist = [baremetal_fakes.baremetal_volume_target_uuid,
                   '--extra', 'key1', '--extra', 'key2']
        verifylist = [('volume_target',
                       baremetal_fakes.baremetal_volume_target_uuid),
                      ('extra', ['key1', 'key2'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.volume_target.update.assert_called_once_with(
            baremetal_fakes.baremetal_volume_target_uuid,
            [{'path': '/extra/key1', 'op': 'remove'},
             {'path': '/extra/key2', 'op': 'remove'}])

    def test_baremetal_volume_target_unset_property(self):
        arglist = [baremetal_fakes.baremetal_volume_target_uuid,
                   '--property', 'key11']
        verifylist = [('volume_target',
                       baremetal_fakes.baremetal_volume_target_uuid),
                      ('properties', ['key11'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.volume_target.update.assert_called_once_with(
            baremetal_fakes.baremetal_volume_target_uuid,
            [{'path': '/properties/key11', 'op': 'remove'}])

    def test_baremetal_volume_target_unset_multiple_properties(self):
        arglist = [baremetal_fakes.baremetal_volume_target_uuid,
                   '--property', 'key11', '--property', 'key22']
        verifylist = [('volume_target',
                       baremetal_fakes.baremetal_volume_target_uuid),
                      ('properties', ['key11', 'key22'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.volume_target.update.assert_called_once_with(
            baremetal_fakes.baremetal_volume_target_uuid,
            [{'path': '/properties/key11', 'op': 'remove'},
             {'path': '/properties/key22', 'op': 'remove'}])

    def test_baremetal_volume_target_unset_no_options(self):
        arglist = []
        verifylist = []
        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_volume_target_unset_no_property(self):
        arglist = [baremetal_fakes.baremetal_volume_target_uuid]
        verifylist = [('volume_target',
                       baremetal_fakes.baremetal_volume_target_uuid)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.baremetal_mock.volume_target.update.assert_not_called()
