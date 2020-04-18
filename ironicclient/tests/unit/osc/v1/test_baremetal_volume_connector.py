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
from unittest import mock

from osc_lib.tests import utils as osctestutils

from ironicclient import exc
from ironicclient.osc.v1 import baremetal_volume_connector as bm_vol_connector
from ironicclient.tests.unit.osc.v1 import fakes as baremetal_fakes


class TestBaremetalVolumeConnector(baremetal_fakes.TestBaremetal):

    def setUp(self):
        super(TestBaremetalVolumeConnector, self).setUp()

        self.baremetal_mock = self.app.client_manager.baremetal
        self.baremetal_mock.reset_mock()


class TestCreateBaremetalVolumeConnector(TestBaremetalVolumeConnector):

    def setUp(self):
        super(TestCreateBaremetalVolumeConnector, self).setUp()

        self.baremetal_mock.volume_connector.create.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.VOLUME_CONNECTOR),
                loaded=True,
            ))

        # Get the command object to test
        self.cmd = (
            bm_vol_connector.CreateBaremetalVolumeConnector(self.app, None))

    def test_baremetal_volume_connector_create(self):
        arglist = [
            '--node', baremetal_fakes.baremetal_uuid,
            '--type', baremetal_fakes.baremetal_volume_connector_type,
            '--connector-id',
            baremetal_fakes.baremetal_volume_connector_connector_id,
            '--uuid', baremetal_fakes.baremetal_volume_connector_uuid,
        ]

        verifylist = [
            ('node_uuid', baremetal_fakes.baremetal_uuid),
            ('type', baremetal_fakes.baremetal_volume_connector_type),
            ('connector_id',
             baremetal_fakes.baremetal_volume_connector_connector_id),
            ('uuid', baremetal_fakes.baremetal_volume_connector_uuid),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        args = {
            'node_uuid': baremetal_fakes.baremetal_uuid,
            'type': baremetal_fakes.baremetal_volume_connector_type,
            'connector_id':
                baremetal_fakes.baremetal_volume_connector_connector_id,
            'uuid': baremetal_fakes.baremetal_volume_connector_uuid,
        }

        self.baremetal_mock.volume_connector.create.assert_called_once_with(
            **args)

    def test_baremetal_volume_connector_create_without_uuid(self):
        arglist = [
            '--node', baremetal_fakes.baremetal_uuid,
            '--type', baremetal_fakes.baremetal_volume_connector_type,
            '--connector-id',
            baremetal_fakes.baremetal_volume_connector_connector_id,
        ]

        verifylist = [
            ('node_uuid', baremetal_fakes.baremetal_uuid),
            ('type', baremetal_fakes.baremetal_volume_connector_type),
            ('connector_id',
             baremetal_fakes.baremetal_volume_connector_connector_id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        args = {
            'node_uuid': baremetal_fakes.baremetal_uuid,
            'type': baremetal_fakes.baremetal_volume_connector_type,
            'connector_id':
                baremetal_fakes.baremetal_volume_connector_connector_id,
        }

        self.baremetal_mock.volume_connector.create.assert_called_once_with(
            **args)

    def test_baremetal_volume_connector_create_extras(self):
        arglist = [
            '--node', baremetal_fakes.baremetal_uuid,
            '--type', baremetal_fakes.baremetal_volume_connector_type,
            '--connector-id',
            baremetal_fakes.baremetal_volume_connector_connector_id,
            '--extra', 'key1=value1',
            '--extra', 'key2=value2',
        ]

        verifylist = [
            ('node_uuid', baremetal_fakes.baremetal_uuid),
            ('type', baremetal_fakes.baremetal_volume_connector_type),
            ('connector_id',
             baremetal_fakes.baremetal_volume_connector_connector_id),
            ('extra', ['key1=value1', 'key2=value2'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        args = {
            'node_uuid': baremetal_fakes.baremetal_uuid,
            'type': baremetal_fakes.baremetal_volume_connector_type,
            'connector_id':
                baremetal_fakes.baremetal_volume_connector_connector_id,
            'extra': baremetal_fakes.baremetal_volume_connector_extra,
        }

        self.baremetal_mock.volume_connector.create.assert_called_once_with(
            **args)

    def test_baremetal_volume_connector_create_invalid_type(self):
        arglist = [
            '--node', baremetal_fakes.baremetal_uuid,
            '--type', 'invalid',
            '--connector-id',
            baremetal_fakes.baremetal_volume_connector_connector_id,
            '--uuid', baremetal_fakes.baremetal_volume_connector_uuid,
        ]
        verifylist = None

        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_volume_connector_create_missing_node(self):
        arglist = [
            '--type', baremetal_fakes.baremetal_volume_connector_type,
            '--connector-id',
            baremetal_fakes.baremetal_volume_connector_connector_id,
            '--uuid', baremetal_fakes.baremetal_volume_connector_uuid,
        ]
        verifylist = None

        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_volume_connector_create_missing_type(self):
        arglist = [
            '--node', baremetal_fakes.baremetal_uuid,
            '--connector-id',
            baremetal_fakes.baremetal_volume_connector_connector_id,
            '--uuid', baremetal_fakes.baremetal_volume_connector_uuid,
        ]
        verifylist = None

        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_volume_connector_create_missing_connector_id(self):
        arglist = [
            '--node', baremetal_fakes.baremetal_uuid,
            '--type', baremetal_fakes.baremetal_volume_connector_type,
            '--uuid', baremetal_fakes.baremetal_volume_connector_uuid,
        ]
        verifylist = None

        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestShowBaremetalVolumeConnector(TestBaremetalVolumeConnector):

    def setUp(self):
        super(TestShowBaremetalVolumeConnector, self).setUp()

        self.baremetal_mock.volume_connector.get.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.VOLUME_CONNECTOR),
                loaded=True))

        self.cmd = (
            bm_vol_connector.ShowBaremetalVolumeConnector(self.app, None))

    def test_baremetal_volume_connector_show(self):
        arglist = ['vvv-cccccc-vvvv']
        verifylist = [('volume_connector',
                       baremetal_fakes.baremetal_volume_connector_uuid)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        args = ['vvv-cccccc-vvvv']
        self.baremetal_mock.volume_connector.get.assert_called_once_with(
            *args, fields=None)
        collist = ('connector_id', 'extra', 'node_uuid', 'type', 'uuid')
        self.assertEqual(collist, columns)

        datalist = (
            baremetal_fakes.baremetal_volume_connector_connector_id,
            baremetal_fakes.baremetal_volume_connector_extra,
            baremetal_fakes.baremetal_uuid,
            baremetal_fakes.baremetal_volume_connector_type,
            baremetal_fakes.baremetal_volume_connector_uuid,
        )
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_volume_connector_show_no_options(self):
        arglist = []
        verifylist = []
        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_volume_connector_show_fields(self):
        arglist = ['vvv-cccccc-vvvv', '--fields', 'uuid', 'connector_id']
        verifylist = [('fields', [['uuid', 'connector_id']]),
                      ('volume_connector',
                       baremetal_fakes.baremetal_volume_connector_uuid)]

        fake_vc = copy.deepcopy(baremetal_fakes.VOLUME_CONNECTOR)
        fake_vc.pop('type')
        fake_vc.pop('extra')
        fake_vc.pop('node_uuid')
        self.baremetal_mock.volume_connector.get.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                fake_vc,
                loaded=True))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        args = ['vvv-cccccc-vvvv']
        fields = ['uuid', 'connector_id']
        self.baremetal_mock.volume_connector.get.assert_called_once_with(
            *args, fields=fields)
        collist = ('connector_id', 'uuid')
        self.assertEqual(collist, columns)

        datalist = (
            baremetal_fakes.baremetal_volume_connector_connector_id,
            baremetal_fakes.baremetal_volume_connector_uuid,
        )
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_volume_connector_show_fields_multiple(self):
        arglist = ['vvv-cccccc-vvvv', '--fields', 'uuid', 'connector_id',
                   '--fields', 'type']
        verifylist = [('fields', [['uuid', 'connector_id'], ['type']]),
                      ('volume_connector',
                       baremetal_fakes.baremetal_volume_connector_uuid)]

        fake_vc = copy.deepcopy(baremetal_fakes.VOLUME_CONNECTOR)
        fake_vc.pop('extra')
        fake_vc.pop('node_uuid')
        self.baremetal_mock.volume_connector.get.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                fake_vc,
                loaded=True))

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        args = ['vvv-cccccc-vvvv']
        fields = ['uuid', 'connector_id', 'type']
        self.baremetal_mock.volume_connector.get.assert_called_once_with(
            *args, fields=fields)
        collist = ('connector_id', 'type', 'uuid')
        self.assertEqual(collist, columns)

        datalist = (
            baremetal_fakes.baremetal_volume_connector_connector_id,
            baremetal_fakes.baremetal_volume_connector_type,
            baremetal_fakes.baremetal_volume_connector_uuid,
        )
        self.assertEqual(datalist, tuple(data))


class TestListBaremetalVolumeConnector(TestBaremetalVolumeConnector):
    def setUp(self):
        super(TestListBaremetalVolumeConnector, self).setUp()

        self.baremetal_mock.volume_connector.list.return_value = [
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.VOLUME_CONNECTOR),
                loaded=True)
        ]
        self.cmd = (
            bm_vol_connector.ListBaremetalVolumeConnector(self.app, None))

    def test_baremetal_volume_connector_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'marker': None,
            'limit': None}
        self.baremetal_mock.volume_connector.list.assert_called_once_with(
            **kwargs)

        collist = (
            "UUID",
            "Node UUID",
            "Type",
            "Connector ID")
        self.assertEqual(collist, columns)

        datalist = ((baremetal_fakes.baremetal_volume_connector_uuid,
                     baremetal_fakes.baremetal_uuid,
                     baremetal_fakes.baremetal_volume_connector_type,
                     baremetal_fakes.baremetal_volume_connector_connector_id),)
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_volume_connector_list_node(self):
        arglist = ['--node', baremetal_fakes.baremetal_uuid]
        verifylist = [('node', baremetal_fakes.baremetal_uuid)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'node': baremetal_fakes.baremetal_uuid,
            'marker': None,
            'limit': None}
        self.baremetal_mock.volume_connector.list.assert_called_once_with(
            **kwargs)

        collist = (
            "UUID",
            "Node UUID",
            "Type",
            "Connector ID")
        self.assertEqual(collist, columns)

        datalist = ((baremetal_fakes.baremetal_volume_connector_uuid,
                     baremetal_fakes.baremetal_uuid,
                     baremetal_fakes.baremetal_volume_connector_type,
                     baremetal_fakes.baremetal_volume_connector_connector_id),)
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_volume_connector_list_long(self):
        arglist = ['--long']
        verifylist = [('detail', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'detail': True,
            'marker': None,
            'limit': None,
        }
        self.baremetal_mock.volume_connector.list.assert_called_with(**kwargs)

        collist = ('UUID', 'Node UUID', 'Type', 'Connector ID', 'Extra',
                   'Created At', 'Updated At')
        self.assertEqual(collist, columns)

        datalist = ((baremetal_fakes.baremetal_volume_connector_uuid,
                     baremetal_fakes.baremetal_uuid,
                     baremetal_fakes.baremetal_volume_connector_type,
                     baremetal_fakes.baremetal_volume_connector_connector_id,
                     baremetal_fakes.baremetal_volume_connector_extra,
                     '',
                     ''),)
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_volume_connector_list_fields(self):
        arglist = ['--fields', 'uuid', 'connector_id']
        verifylist = [('fields', [['uuid', 'connector_id']])]

        fake_vc = copy.deepcopy(baremetal_fakes.VOLUME_CONNECTOR)
        fake_vc.pop('type')
        fake_vc.pop('extra')
        fake_vc.pop('node_uuid')
        self.baremetal_mock.volume_connector.list.return_value = [
            baremetal_fakes.FakeBaremetalResource(
                None,
                fake_vc,
                loaded=True)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'detail': False,
            'marker': None,
            'limit': None,
            'fields': ('uuid', 'connector_id')
        }
        self.baremetal_mock.volume_connector.list.assert_called_with(**kwargs)

        collist = ('UUID', 'Connector ID')
        self.assertEqual(collist, columns)

        datalist = ((baremetal_fakes.baremetal_volume_connector_uuid,
                     baremetal_fakes.baremetal_volume_connector_connector_id),)
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_volume_connector_list_fields_multiple(self):
        arglist = ['--fields', 'uuid', 'connector_id', '--fields', 'extra']
        verifylist = [('fields', [['uuid', 'connector_id'], ['extra']])]

        fake_vc = copy.deepcopy(baremetal_fakes.VOLUME_CONNECTOR)
        fake_vc.pop('type')
        fake_vc.pop('node_uuid')
        self.baremetal_mock.volume_connector.list.return_value = [
            baremetal_fakes.FakeBaremetalResource(
                None,
                fake_vc,
                loaded=True)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        kwargs = {
            'detail': False,
            'marker': None,
            'limit': None,
            'fields': ('uuid', 'connector_id', 'extra')
        }
        self.baremetal_mock.volume_connector.list.assert_called_with(**kwargs)

        collist = ('UUID', 'Connector ID', 'Extra')
        self.assertEqual(collist, columns)

        datalist = ((baremetal_fakes.baremetal_volume_connector_uuid,
                     baremetal_fakes.baremetal_volume_connector_connector_id,
                     baremetal_fakes.baremetal_volume_connector_extra),)
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_volume_connector_list_invalid_fields(self):
        arglist = ['--fields', 'uuid', 'invalid']
        verifylist = [('fields', [['uuid', 'invalid']])]
        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_volume_connector_list_marker(self):
        arglist = ['--marker', baremetal_fakes.baremetal_volume_connector_uuid]
        verifylist = [
            ('marker', baremetal_fakes.baremetal_volume_connector_uuid)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        kwargs = {
            'marker': baremetal_fakes.baremetal_volume_connector_uuid,
            'limit': None}
        self.baremetal_mock.volume_connector.list.assert_called_once_with(
            **kwargs)

    def test_baremetal_volume_connector_list_limit(self):
        arglist = ['--limit', '10']
        verifylist = [('limit', 10)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        kwargs = {
            'marker': None,
            'limit': 10}
        self.baremetal_mock.volume_connector.list.assert_called_once_with(
            **kwargs)

    def test_baremetal_volume_connector_list_sort(self):
        arglist = ['--sort', 'type']
        verifylist = [('sort', 'type')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        kwargs = {
            'marker': None,
            'limit': None}
        self.baremetal_mock.volume_connector.list.assert_called_once_with(
            **kwargs)

    def test_baremetal_volume_connector_list_sort_desc(self):
        arglist = ['--sort', 'type:desc']
        verifylist = [('sort', 'type:desc')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        kwargs = {
            'marker': None,
            'limit': None}
        self.baremetal_mock.volume_connector.list.assert_called_once_with(
            **kwargs)

    def test_baremetal_volume_connector_list_exclusive_options(self):
        arglist = ['--fields', 'uuid', '--long']
        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, [])

    def test_baremetal_volume_connector_list_negative_limit(self):
        arglist = ['--limit', '-1']
        verifylist = [('limit', -1)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exc.CommandError,
                          self.cmd.take_action,
                          parsed_args)


class TestDeleteBaremetalVolumeConnector(TestBaremetalVolumeConnector):

    def setUp(self):
        super(TestDeleteBaremetalVolumeConnector, self).setUp()

        self.cmd = (
            bm_vol_connector.DeleteBaremetalVolumeConnector(self.app, None))

    def test_baremetal_volume_connector_delete(self):
        arglist = [baremetal_fakes.baremetal_volume_connector_uuid]
        verifylist = [('volume_connectors',
                       [baremetal_fakes.baremetal_volume_connector_uuid])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.baremetal_mock.volume_connector.delete.assert_called_with(
            baremetal_fakes.baremetal_volume_connector_uuid)

    def test_baremetal_volume_connector_delete_multiple(self):
        fake_volume_connector_uuid2 = 'vvv-cccccc-cccc'
        arglist = [baremetal_fakes.baremetal_volume_connector_uuid,
                   fake_volume_connector_uuid2]
        verifylist = [('volume_connectors',
                       [baremetal_fakes.baremetal_volume_connector_uuid,
                        fake_volume_connector_uuid2])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.baremetal_mock.volume_connector.delete.assert_has_calls(
            [mock.call(baremetal_fakes.baremetal_volume_connector_uuid),
             mock.call(fake_volume_connector_uuid2)])
        self.assertEqual(
            2, self.baremetal_mock.volume_connector.delete.call_count)

    def test_baremetal_volume_connector_delete_no_options(self):
        arglist = []
        verifylist = []
        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_volume_connector_delete_error(self):
        arglist = [baremetal_fakes.baremetal_volume_connector_uuid]
        verifylist = [('volume_connectors',
                       [baremetal_fakes.baremetal_volume_connector_uuid])]

        self.baremetal_mock.volume_connector.delete.side_effect = (
            exc.NotFound())

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exc.ClientException,
                          self.cmd.take_action,
                          parsed_args)
        self.baremetal_mock.volume_connector.delete.assert_called_with(
            baremetal_fakes.baremetal_volume_connector_uuid)

    def test_baremetal_volume_connector_delete_multiple_error(self):
        fake_volume_connector_uuid2 = 'vvv-cccccc-cccc'
        arglist = [baremetal_fakes.baremetal_volume_connector_uuid,
                   fake_volume_connector_uuid2]
        verifylist = [('volume_connectors',
                       [baremetal_fakes.baremetal_volume_connector_uuid,
                        fake_volume_connector_uuid2])]

        self.baremetal_mock.volume_connector.delete.side_effect = [
            None, exc.NotFound()]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exc.ClientException,
                          self.cmd.take_action,
                          parsed_args)

        self.baremetal_mock.volume_connector.delete.assert_has_calls(
            [mock.call(baremetal_fakes.baremetal_volume_connector_uuid),
             mock.call(fake_volume_connector_uuid2)])
        self.assertEqual(
            2, self.baremetal_mock.volume_connector.delete.call_count)


class TestSetBaremetalVolumeConnector(TestBaremetalVolumeConnector):
    def setUp(self):
        super(TestSetBaremetalVolumeConnector, self).setUp()

        self.cmd = (
            bm_vol_connector.SetBaremetalVolumeConnector(self.app, None))

    def test_baremetal_volume_connector_set_node_uuid(self):
        new_node_uuid = 'xxx-xxxxxx-zzzz'
        arglist = [
            baremetal_fakes.baremetal_volume_connector_uuid,
            '--node', new_node_uuid]
        verifylist = [
            ('volume_connector',
             baremetal_fakes.baremetal_volume_connector_uuid),
            ('node_uuid', new_node_uuid)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.volume_connector.update.assert_called_once_with(
            baremetal_fakes.baremetal_volume_connector_uuid,
            [{'path': '/node_uuid', 'value': new_node_uuid, 'op': 'add'}])

    def test_baremetal_volume_connector_set_type(self):
        new_type = 'wwnn'
        arglist = [
            baremetal_fakes.baremetal_volume_connector_uuid,
            '--type', new_type]
        verifylist = [
            ('volume_connector',
             baremetal_fakes.baremetal_volume_connector_uuid),
            ('type', new_type)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.volume_connector.update.assert_called_once_with(
            baremetal_fakes.baremetal_volume_connector_uuid,
            [{'path': '/type', 'value': new_type, 'op': 'add'}])

    def test_baremetal_volume_connector_set_invalid_type(self):
        new_type = 'invalid'
        arglist = [
            baremetal_fakes.baremetal_volume_connector_uuid,
            '--type', new_type]
        verifylist = None

        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_volume_connector_set_connector_id(self):
        new_conn_id = '11:22:33:44:55:66:77:88'
        arglist = [
            baremetal_fakes.baremetal_volume_connector_uuid,
            '--connector-id', new_conn_id]
        verifylist = [
            ('volume_connector',
             baremetal_fakes.baremetal_volume_connector_uuid),
            ('connector_id', new_conn_id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.volume_connector.update.assert_called_once_with(
            baremetal_fakes.baremetal_volume_connector_uuid,
            [{'path': '/connector_id', 'value': new_conn_id, 'op': 'add'}])

    def test_baremetal_volume_connector_set_type_and_connector_id(self):
        new_type = 'wwnn'
        new_conn_id = '11:22:33:44:55:66:77:88'
        arglist = [
            baremetal_fakes.baremetal_volume_connector_uuid,
            '--type', new_type,
            '--connector-id', new_conn_id]
        verifylist = [
            ('volume_connector',
             baremetal_fakes.baremetal_volume_connector_uuid),
            ('type', new_type),
            ('connector_id', new_conn_id)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.volume_connector.update.assert_called_once_with(
            baremetal_fakes.baremetal_volume_connector_uuid,
            [{'path': '/type', 'value': new_type, 'op': 'add'},
             {'path': '/connector_id', 'value': new_conn_id, 'op': 'add'}])

    def test_baremetal_volume_connector_set_extra(self):
        arglist = [
            baremetal_fakes.baremetal_volume_connector_uuid,
            '--extra', 'foo=bar']
        verifylist = [
            ('volume_connector',
             baremetal_fakes.baremetal_volume_connector_uuid),
            ('extra', ['foo=bar'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.volume_connector.update.assert_called_once_with(
            baremetal_fakes.baremetal_volume_connector_uuid,
            [{'path': '/extra/foo', 'value': 'bar', 'op': 'add'}])

    def test_baremetal_volume_connector_set_multiple_extras(self):
        arglist = [
            baremetal_fakes.baremetal_volume_connector_uuid,
            '--extra', 'key1=val1', '--extra', 'key2=val2']
        verifylist = [
            ('volume_connector',
             baremetal_fakes.baremetal_volume_connector_uuid),
            ('extra', ['key1=val1', 'key2=val2'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.volume_connector.update.assert_called_once_with(
            baremetal_fakes.baremetal_volume_connector_uuid,
            [{'path': '/extra/key1', 'value': 'val1', 'op': 'add'},
             {'path': '/extra/key2', 'value': 'val2', 'op': 'add'}])

    def test_baremetal_volume_connector_set_no_options(self):
        arglist = []
        verifylist = []
        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_volume_connector_set_no_property(self):
        arglist = [baremetal_fakes.baremetal_volume_connector_uuid]
        verifylist = [('volume_connector',
                       baremetal_fakes.baremetal_volume_connector_uuid)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.baremetal_mock.volume_connector.update.assert_not_called()


class TestUnsetBaremetalVolumeConnector(TestBaremetalVolumeConnector):
    def setUp(self):
        super(TestUnsetBaremetalVolumeConnector, self).setUp()

        self.cmd = (
            bm_vol_connector.UnsetBaremetalVolumeConnector(self.app, None))

    def test_baremetal_volume_connector_unset_extra(self):
        arglist = [baremetal_fakes.baremetal_volume_connector_uuid,
                   '--extra', 'key1']
        verifylist = [('volume_connector',
                       baremetal_fakes.baremetal_volume_connector_uuid),
                      ('extra', ['key1'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.volume_connector.update.assert_called_once_with(
            baremetal_fakes.baremetal_volume_connector_uuid,
            [{'path': '/extra/key1', 'op': 'remove'}])

    def test_baremetal_volume_connector_unset_multiple_extras(self):
        arglist = [baremetal_fakes.baremetal_volume_connector_uuid,
                   '--extra', 'key1', '--extra', 'key2']
        verifylist = [('volume_connector',
                       baremetal_fakes.baremetal_volume_connector_uuid),
                      ('extra', ['key1', 'key2'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.volume_connector.update.assert_called_once_with(
            baremetal_fakes.baremetal_volume_connector_uuid,
            [{'path': '/extra/key1', 'op': 'remove'},
             {'path': '/extra/key2', 'op': 'remove'}])

    def test_baremetal_volume_connector_unset_no_options(self):
        arglist = []
        verifylist = []
        self.assertRaises(osctestutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_volume_connector_unset_no_property(self):
        arglist = [baremetal_fakes.baremetal_volume_connector_uuid]
        verifylist = [('volume_connector',
                       baremetal_fakes.baremetal_volume_connector_uuid)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.baremetal_mock.volume_connector.update.assert_not_called()
