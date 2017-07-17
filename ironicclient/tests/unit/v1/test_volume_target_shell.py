# Copyright 2017 Hitachi, Ltd.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock

from oslo_utils import uuidutils

from ironicclient.common.apiclient import exceptions
from ironicclient.common import cliutils
from ironicclient.common import utils as commonutils
from ironicclient.tests.unit import utils
import ironicclient.v1.volume_target_shell as vt_shell


class Volume_TargetShellTest(utils.BaseTestCase):

    def test_volume_target_show(self):
        actual = {}
        fake_print_dict = lambda data, *args, **kwargs: actual.update(data)
        with mock.patch.object(cliutils, 'print_dict', fake_print_dict):
            volume_target = object()
            vt_shell._print_volume_target_show(volume_target)
        exp = ['created_at', 'extra', 'node_uuid', 'volume_type',
               'updated_at', 'uuid', 'properties', 'boot_index',
               'volume_id']
        act = actual.keys()
        self.assertEqual(sorted(exp), sorted(act))

    def test_do_volume_target_show(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.volume_target = 'volume_target_uuid'
        args.fields = None
        args.json = False

        vt_shell.do_volume_target_show(client_mock, args)
        client_mock.volume_target.get.assert_called_once_with(
            'volume_target_uuid', fields=None)

    def test_do_volume_target_show_space_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.volume_target = '   '
        self.assertRaises(exceptions.CommandError,
                          vt_shell.do_volume_target_show,
                          client_mock, args)

    def test_do_volume_target_show_empty_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.volume_target = ''
        self.assertRaises(exceptions.CommandError,
                          vt_shell.do_volume_target_show,
                          client_mock, args)

    def test_do_volume_target_show_fields(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.volume_target = 'volume_target_uuid'
        args.fields = [['uuid', 'boot_index']]
        args.json = False
        vt_shell.do_volume_target_show(client_mock, args)
        client_mock.volume_target.get.assert_called_once_with(
            'volume_target_uuid', fields=['uuid', 'boot_index'])

    def test_do_volume_target_show_invalid_fields(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.volume_target = 'volume_target_uuid'
        args.fields = [['foo', 'bar']]
        args.json = False
        self.assertRaises(exceptions.CommandError,
                          vt_shell.do_volume_target_show,
                          client_mock, args)

    def test_do_volume_target_update(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.volume_target = 'volume_target_uuid'
        args.op = 'add'
        args.attributes = [['arg1=val1', 'arg2=val2']]
        args.json = False

        vt_shell.do_volume_target_update(client_mock, args)
        patch = commonutils.args_array_to_patch(args.op, args.attributes[0])
        client_mock.volume_target.update.assert_called_once_with(
            'volume_target_uuid', patch)

    def test_do_volume_target_update_wrong_op(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.volume_target = 'volume_target_uuid'
        args.op = 'foo'
        args.attributes = [['arg1=val1', 'arg2=val2']]
        self.assertRaises(exceptions.CommandError,
                          vt_shell.do_volume_target_update,
                          client_mock, args)
        self.assertFalse(client_mock.volume_target.update.called)

    def _get_client_mock_args(self, node=None, marker=None, limit=None,
                              sort_dir=None, sort_key=None, detail=False,
                              fields=None, json=False):
        args = mock.MagicMock(spec=True)
        args.node = node
        args.marker = marker
        args.limit = limit
        args.sort_dir = sort_dir
        args.sort_key = sort_key
        args.detail = detail
        args.fields = fields
        args.json = json

        return args

    def test_do_volume_target_list(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args()

        vt_shell.do_volume_target_list(client_mock, args)
        client_mock.volume_target.list.assert_called_once_with(detail=False)

    def test_do_volume_target_list_detail(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(detail=True)

        vt_shell.do_volume_target_list(client_mock, args)
        client_mock.volume_target.list.assert_called_once_with(detail=True)

    def test_do_volume_target_list_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='uuid', detail=False)

        vt_shell.do_volume_target_list(client_mock, args)
        client_mock.volume_target.list.assert_called_once_with(
            sort_key='uuid', detail=False)

    def test_do_volume_target_list_wrong_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='node_uuid', detail=False)

        self.assertRaises(exceptions.CommandError,
                          vt_shell.do_volume_target_list,
                          client_mock, args)
        self.assertFalse(client_mock.volume_target.list.called)

    def test_do_volume_target_list_detail_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='uuid', detail=True)

        vt_shell.do_volume_target_list(client_mock, args)
        client_mock.volume_target.list.assert_called_once_with(
            sort_key='uuid', detail=True)

    def test_do_volume_target_list_detail_wrong_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='node_uuid', detail=True)

        self.assertRaises(exceptions.CommandError,
                          vt_shell.do_volume_target_list,
                          client_mock, args)
        self.assertFalse(client_mock.volume_target.list.called)

    def test_do_volume_target_list_fields(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(fields=[['uuid', 'boot_index']])

        vt_shell.do_volume_target_list(client_mock, args)
        client_mock.volume_target.list.assert_called_once_with(
            fields=['uuid', 'boot_index'], detail=False)

    def test_do_volume_target_list_invalid_fields(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(fields=[['foo', 'bar']])
        self.assertRaises(exceptions.CommandError,
                          vt_shell.do_volume_target_list,
                          client_mock, args)

    def test_do_volume_target_list_sort_dir(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_dir='desc', detail=False)

        vt_shell.do_volume_target_list(client_mock, args)
        client_mock.volume_target.list.assert_called_once_with(
            sort_dir='desc', detail=False)

    def test_do_volume_target_list_detail_sort_dir(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_dir='asc', detail=True)

        vt_shell.do_volume_target_list(client_mock, args)
        client_mock.volume_target.list.assert_called_once_with(
            sort_dir='asc', detail=True)

    def test_do_volume_target_wrong_sort_dir(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_dir='abc', detail=False)

        self.assertRaises(exceptions.CommandError,
                          vt_shell.do_volume_target_list,
                          client_mock, args)
        self.assertFalse(client_mock.volume_target.list.called)

    def test_do_volume_target_create(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.json = False
        vt_shell.do_volume_target_create(client_mock, args)
        client_mock.volume_target.create.assert_called_once_with()

    def test_do_volume_target_create_with_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.uuid = uuidutils.generate_uuid()
        args.json = False

        vt_shell.do_volume_target_create(client_mock, args)
        client_mock.volume_target.create.assert_called_once_with(
            uuid=args.uuid)

    def test_do_volume_target_create_valid_fields_values(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.volume_type = 'volume_type'
        args.properties = ["key1=val1", "key2=val2"]
        args.boot_index = 100
        args.node_uuid = 'uuid'
        args.volume_id = 'volume_id'
        args.extra = ["key1=val1", "key2=val2"]
        args.json = False
        vt_shell.do_volume_target_create(client_mock, args)
        client_mock.volume_target.create.assert_called_once_with(
            volume_type='volume_type',
            properties={'key1': 'val1', 'key2': 'val2'},
            boot_index=100, node_uuid='uuid', volume_id='volume_id',
            extra={'key1': 'val1', 'key2': 'val2'})

    def test_do_volume_target_create_invalid_extra_fields(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.volume_type = 'volume_type'
        args.properties = ["key1=val1", "key2=val2"]
        args.boot_index = 100
        args.node_uuid = 'uuid'
        args.volume_id = 'volume_id'
        args.extra = ["foo"]
        args.json = False
        self.assertRaises(exceptions.CommandError,
                          vt_shell.do_volume_target_create,
                          client_mock, args)

    def test_do_volume_target_delete(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.volume_target = ['volume_target_uuid']
        vt_shell.do_volume_target_delete(client_mock, args)
        client_mock.volume_target.delete.assert_called_once_with(
            'volume_target_uuid')

    def test_do_volume_target_delete_multi(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.volume_target = ['uuid1', 'uuid2']
        vt_shell.do_volume_target_delete(client_mock, args)
        self.assertEqual([mock.call('uuid1'), mock.call('uuid2')],
                         client_mock.volume_target.delete.call_args_list)

    def test_do_volume_target_delete_multi_error(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.volume_target = ['uuid1', 'uuid2']
        client_mock.volume_target.delete.side_effect = [
            exceptions.ClientException('error'), None]
        self.assertRaises(exceptions.ClientException,
                          vt_shell.do_volume_target_delete,
                          client_mock, args)
        self.assertEqual([mock.call('uuid1'), mock.call('uuid2')],
                         client_mock.volume_target.delete.call_args_list)
