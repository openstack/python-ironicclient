# Copyright 2013 IBM Corp
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import mock

from oslo_utils import uuidutils

from ironicclient.common.apiclient import exceptions
from ironicclient.common import cliutils
from ironicclient.common import utils as commonutils
from ironicclient.tests.unit import utils
import ironicclient.v1.port_shell as p_shell


class PortShellTest(utils.BaseTestCase):

    def test_port_show(self):
        actual = {}
        fake_print_dict = lambda data, *args, **kwargs: actual.update(data)
        with mock.patch.object(cliutils, 'print_dict', fake_print_dict):
            port = object()
            p_shell._print_port_show(port)
        exp = ['address', 'created_at', 'extra', 'node_uuid',
               'physical_network', 'updated_at', 'uuid', 'pxe_enabled',
               'local_link_connection', 'internal_info',
               'portgroup_uuid']
        act = actual.keys()
        self.assertEqual(sorted(exp), sorted(act))

    def test_do_port_show(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.port = 'port_uuid'
        args.address = False
        args.fields = None
        args.json = False

        p_shell.do_port_show(client_mock, args)
        client_mock.port.get.assert_called_once_with('port_uuid', fields=None)
        # assert get_by_address() wasn't called
        self.assertFalse(client_mock.port.get_by_address.called)

    def test_do_port_show_space_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.port = '   '
        args.address = False
        args.json = False
        self.assertRaises(exceptions.CommandError,
                          p_shell.do_port_show,
                          client_mock, args)

    def test_do_port_show_empty_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.port = ''
        args.address = False
        args.json = False
        self.assertRaises(exceptions.CommandError,
                          p_shell.do_port_show,
                          client_mock, args)

    def test_do_port_show_by_address(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.port = 'port_address'
        args.address = True
        args.fields = None
        args.json = False

        p_shell.do_port_show(client_mock, args)
        client_mock.port.get_by_address.assert_called_once_with('port_address',
                                                                fields=None)
        # assert get() wasn't called
        self.assertFalse(client_mock.port.get.called)

    def test_do_port_show_fields(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.port = 'port_uuid'
        args.address = False
        args.fields = [['uuid', 'address']]
        args.json = False
        p_shell.do_port_show(client_mock, args)
        client_mock.port.get.assert_called_once_with(
            'port_uuid', fields=['uuid', 'address'])

    def test_do_port_show_invalid_fields(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.port = 'port_uuid'
        args.address = False
        args.fields = [['foo', 'bar']]
        args.json = False
        self.assertRaises(exceptions.CommandError,
                          p_shell.do_port_show,
                          client_mock, args)

    def test_do_port_update(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.port = 'port_uuid'
        args.op = 'add'
        args.attributes = [['arg1=val1', 'arg2=val2']]
        args.json = False

        p_shell.do_port_update(client_mock, args)
        patch = commonutils.args_array_to_patch(args.op, args.attributes[0])
        client_mock.port.update.assert_called_once_with('port_uuid', patch)

    def test_do_port_update_wrong_op(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.port = 'port_uuid'
        args.op = 'foo'
        args.attributes = [['arg1=val1', 'arg2=val2']]
        args.json = False
        self.assertRaises(exceptions.CommandError,
                          p_shell.do_port_update,
                          client_mock, args)
        self.assertFalse(client_mock.port.update.called)

    def _get_client_mock_args(self, address=None, marker=None, limit=None,
                              sort_dir=None, sort_key=None, detail=False,
                              fields=None, json=False):
        args = mock.MagicMock(spec=True)
        args.address = address
        args.marker = marker
        args.limit = limit
        args.sort_dir = sort_dir
        args.sort_key = sort_key
        args.detail = detail
        args.fields = fields
        args.json = json

        return args

    def test_do_port_list(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args()

        p_shell.do_port_list(client_mock, args)
        client_mock.port.list.assert_called_once_with(detail=False)

    def test_do_port_list_detail(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(detail=True)

        p_shell.do_port_list(client_mock, args)
        client_mock.port.list.assert_called_once_with(detail=True)

    def test_do_port_list_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='uuid',
                                          detail=False)

        p_shell.do_port_list(client_mock, args)
        client_mock.port.list.assert_called_once_with(sort_key='uuid',
                                                      detail=False)

    def test_do_port_list_wrong_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='node_uuid', detail=False)

        self.assertRaises(exceptions.CommandError,
                          p_shell.do_port_list,
                          client_mock, args)
        self.assertFalse(client_mock.port.list.called)

    def test_do_port_list_detail_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='uuid',
                                          detail=True)

        p_shell.do_port_list(client_mock, args)
        client_mock.port.list.assert_called_once_with(sort_key='uuid',
                                                      detail=True)

    def test_do_port_list_detail_wrong_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='node_uuid',
                                          detail=True)

        self.assertRaises(exceptions.CommandError,
                          p_shell.do_port_list,
                          client_mock, args)
        self.assertFalse(client_mock.port.list.called)

    def test_do_port_list_fields(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(fields=[['uuid', 'address']])

        p_shell.do_port_list(client_mock, args)
        client_mock.port.list.assert_called_once_with(
            fields=['uuid', 'address'], detail=False)

    def test_do_port_list_invalid_fields(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(fields=[['foo', 'bar']])
        self.assertRaises(exceptions.CommandError,
                          p_shell.do_port_list,
                          client_mock, args)

    def test_do_port_list_sort_dir(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_dir='desc',
                                          detail=False)

        p_shell.do_port_list(client_mock, args)
        client_mock.port.list.assert_called_once_with(sort_dir='desc',
                                                      detail=False)

    def test_do_port_list_detail_sort_dir(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_dir='asc',
                                          detail=True)

        p_shell.do_port_list(client_mock, args)
        client_mock.port.list.assert_called_once_with(sort_dir='asc',
                                                      detail=True)

    def test_do_port_list_wrong_sort_dir(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_dir='abc',
                                          detail=False)
        self.assertRaises(exceptions.CommandError,
                          p_shell.do_port_list,
                          client_mock, args)
        self.assertFalse(client_mock.port.list.called)

    def test_do_port_create(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.json = False
        p_shell.do_port_create(client_mock, args)
        client_mock.port.create.assert_called_once_with()

    def test_do_port_create_with_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.uuid = uuidutils.generate_uuid()
        args.json = False

        p_shell.do_port_create(client_mock, args)
        client_mock.port.create.assert_called_once_with(uuid=args.uuid)

    def test_do_port_create_valid_fields_values(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.address = 'address'
        args.node_uuid = 'uuid'
        args.extra = ["key1=val1", "key2=val2"]
        args.json = False
        p_shell.do_port_create(client_mock, args)
        client_mock.port.create.assert_called_once_with(
            address='address', node_uuid='uuid', extra={'key1': 'val1',
                                                        'key2': 'val2'})

    def test_do_port_create_invalid_extra_fields_values(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.address = 'address'
        args.node_uuid = 'uuid'
        args.extra = ["foo"]
        args.json = False
        self.assertRaises(exceptions.CommandError,
                          p_shell.do_port_create, client_mock, args)

    def test_do_port_create_portgroup_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.address = 'address'
        args.node_uuid = 'uuid'
        args.portgroup_uuid = 'portgroup-uuid'
        args.json = False
        p_shell.do_port_create(client_mock, args)
        client_mock.port.create.assert_called_once_with(
            address='address', node_uuid='uuid',
            portgroup_uuid='portgroup-uuid')

    def test_do_port_create_physical_network(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.address = 'address'
        args.node_uuid = 'uuid'
        args.physical_network = 'physnet1'
        args.json = False
        p_shell.do_port_create(client_mock, args)
        client_mock.port.create.assert_called_once_with(
            address='address', node_uuid='uuid',
            physical_network='physnet1')

    def test_do_port_delete(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.port = ['port_uuid']
        p_shell.do_port_delete(client_mock, args)
        client_mock.port.delete.assert_called_once_with('port_uuid')

    def test_do_port_delete_multiple(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.port = ['port_uuid', 'port_uuid2']
        p_shell.do_port_delete(client_mock, args)
        client_mock.port.delete.assert_has_calls(
            [mock.call('port_uuid'), mock.call('port_uuid2')])

    def test_do_port_delete_multiple_with_exception(self):
        client_mock = mock.MagicMock()
        client_mock.port.delete.side_effect = (
            [exceptions.ClientException, None])
        args = mock.MagicMock()
        args.port = ['port_uuid', 'port_uuid2']

        self.assertRaises(exceptions.ClientException,
                          p_shell.do_port_delete, client_mock, args)
        client_mock.port.delete.assert_has_calls(
            [mock.call('port_uuid'), mock.call('port_uuid2')])
