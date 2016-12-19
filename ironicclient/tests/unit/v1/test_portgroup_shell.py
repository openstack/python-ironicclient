# Copyright 2016 SAP Ltd.
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

from ironicclient.common.apiclient import exceptions
from ironicclient.common import cliutils
from ironicclient.common import utils as commonutils
from ironicclient.tests.unit import utils
import ironicclient.v1.portgroup_shell as pg_shell


class PortgroupShellTest(utils.BaseTestCase):

    def test_portgroup_show(self):
        actual = {}
        fake_print_dict = lambda data, *args, **kwargs: actual.update(data)
        with mock.patch.object(cliutils, 'print_dict', fake_print_dict):
            portgroup = object()
            pg_shell._print_portgroup_show(portgroup)
        exp = ['address', 'created_at', 'extra', 'standalone_ports_supported',
               'node_uuid', 'updated_at', 'uuid', 'name', 'internal_info',
               'mode', 'properties']
        act = actual.keys()
        self.assertEqual(sorted(exp), sorted(act))

    def test_do_portgroup_show(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.portgroup = 'portgroup_uuid'
        args.address = False
        args.fields = None
        args.json = False

        pg_shell.do_portgroup_show(client_mock, args)
        client_mock.portgroup.get.assert_called_once_with('portgroup_uuid',
                                                          fields=None)
        self.assertFalse(client_mock.portgroup.get_by_address.called)

    def test_do_portgroup_show_space_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.portgroup = '   '
        args.address = False
        args.json = False
        self.assertRaises(exceptions.CommandError,
                          pg_shell.do_portgroup_show,
                          client_mock, args)

    def test_do_portgroup_show_empty_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.portgroup = ''
        args.address = False
        args.json = False
        self.assertRaises(exceptions.CommandError,
                          pg_shell.do_portgroup_show,
                          client_mock, args)

    def test_do_portgroup_show_by_address(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.portgroup = 'portgroup_address'
        args.address = True
        args.fields = None
        args.json = False

        pg_shell.do_portgroup_show(client_mock, args)
        client_mock.portgroup.get_by_address.assert_called_once_with(
            'portgroup_address', fields=None)
        self.assertFalse(client_mock.portgroup.get.called)

    def test_do_portgroup_update(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.portgroup = 'portgroup_uuid'
        args.op = 'add'
        args.attributes = [['arg1=val1', 'arg2=val2']]
        args.json = False

        pg_shell.do_portgroup_update(client_mock, args)
        patch = commonutils.args_array_to_patch(args.op, args.attributes[0])
        client_mock.portgroup.update.assert_called_once_with('portgroup_uuid',
                                                             patch)

    def _get_client_mock_args(self, address=None, marker=None, limit=None,
                              sort_dir=None, sort_key=None, detail=False,
                              fields=None, node=None, json=False,
                              portgroup=None):
        args = mock.MagicMock(spec=True)
        args.address = address
        args.node = node
        args.marker = marker
        args.limit = limit
        args.sort_dir = sort_dir
        args.sort_key = sort_key
        args.detail = detail
        args.fields = fields
        args.json = json
        args.portgroup = portgroup

        return args

    def test_do_portgroup_list(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args()

        pg_shell.do_portgroup_list(client_mock, args)
        client_mock.portgroup.list.assert_called_once_with(detail=False)

    def test_do_portgroup_list_detail(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(detail=True)

        pg_shell.do_portgroup_list(client_mock, args)
        client_mock.portgroup.list.assert_called_once_with(detail=True)

    def test_do_portgroup_list_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='uuid',
                                          detail=False)

        pg_shell.do_portgroup_list(client_mock, args)
        client_mock.portgroup.list.assert_called_once_with(sort_key='uuid',
                                                           detail=False)

    def test_do_portgroup_list_wrong_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='node_uuid',
                                          detail=False)

        self.assertRaises(exceptions.CommandError,
                          pg_shell.do_portgroup_list,
                          client_mock, args)
        self.assertFalse(client_mock.portgroup.list.called)

    def test_do_portgroup_list_detail_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='uuid',
                                          detail=True)

        pg_shell.do_portgroup_list(client_mock, args)
        client_mock.portgroup.list.assert_called_once_with(sort_key='uuid',
                                                           detail=True)

    def test_do_portgroup_list_detail_wrong_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='node_uuid',
                                          detail=True)

        self.assertRaises(exceptions.CommandError,
                          pg_shell.do_portgroup_list,
                          client_mock, args)
        self.assertFalse(client_mock.portgroup.list.called)

    def test_do_portgroup_port_list(self):
        client_mock = mock.MagicMock()
        pg_mock = mock.MagicMock(spec_set=[])
        args = self._get_client_mock_args(portgroup=pg_mock)

        pg_shell.do_portgroup_port_list(client_mock, args)
        client_mock.portgroup.list_ports.assert_called_once_with(
            pg_mock, detail=False)

    def test_do_portgroup_port_list_detail(self):
        client_mock = mock.MagicMock()
        pg_mock = mock.MagicMock(spec_set=[])
        args = self._get_client_mock_args(portgroup=pg_mock, detail=True)

        pg_shell.do_portgroup_port_list(client_mock, args)
        client_mock.portgroup.list_ports.assert_called_once_with(
            pg_mock, detail=True)

    def test_do_portgroup_port_list_sort_key(self):
        client_mock = mock.MagicMock()
        pg_mock = mock.MagicMock(spec_set=[])
        args = self._get_client_mock_args(portgroup=pg_mock,
                                          sort_key='created_at')

        pg_shell.do_portgroup_port_list(client_mock, args)
        client_mock.portgroup.list_ports.assert_called_once_with(
            pg_mock, detail=False, sort_key='created_at')

    def test_do_portgroup_port_list_wrong_sort_key(self):
        client_mock = mock.MagicMock()
        pg_mock = mock.MagicMock(spec_set=[])
        args = self._get_client_mock_args(portgroup=pg_mock,
                                          sort_key='node_uuid')
        self.assertRaises(exceptions.CommandError,
                          pg_shell.do_portgroup_port_list,
                          client_mock, args)
        self.assertFalse(client_mock.portgroup.list_ports.called)

    def test_do_portgroup_port_list_detail_sort_key(self):
        client_mock = mock.MagicMock()
        pg_mock = mock.MagicMock(spec_set=[])
        args = self._get_client_mock_args(portgroup=pg_mock,
                                          sort_key='created_at',
                                          detail=True)

        pg_shell.do_portgroup_port_list(client_mock, args)
        client_mock.portgroup.list_ports.assert_called_once_with(
            pg_mock, detail=True, sort_key='created_at')

    def test_do_portgroup_port_list_detail_wrong_sort_key(self):
        client_mock = mock.MagicMock()
        pg_mock = mock.MagicMock(spec_set=[])
        args = self._get_client_mock_args(portgroup=pg_mock,
                                          sort_key='node_uuid',
                                          detail=True)
        self.assertRaises(exceptions.CommandError,
                          pg_shell.do_portgroup_port_list,
                          client_mock, args)
        self.assertFalse(client_mock.portgroup.list_ports.called)

    def test_do_portgroup_port_list_sort_dir(self):
        client_mock = mock.MagicMock()
        pg_mock = mock.MagicMock(spec_set=[])
        args = self._get_client_mock_args(portgroup=pg_mock,
                                          sort_dir='desc')
        pg_shell.do_portgroup_port_list(client_mock, args)
        client_mock.portgroup.list_ports.assert_called_once_with(
            pg_mock, detail=False, sort_dir='desc')

    def test_do_portgroup_port_list_wrong_sort_dir(self):
        client_mock = mock.MagicMock()
        pg_mock = mock.MagicMock(spec_set=[])
        args = self._get_client_mock_args(portgroup=pg_mock,
                                          sort_dir='abc')
        self.assertRaises(exceptions.CommandError,
                          pg_shell.do_portgroup_port_list,
                          client_mock, args)
        self.assertFalse(client_mock.portgroup.list_ports.called)

    def test_do_portgroup_port_list_fields(self):
        client_mock = mock.MagicMock()
        pg_mock = mock.MagicMock(spec_set=[])
        args = self._get_client_mock_args(portgroup=pg_mock,
                                          fields=[['uuid', 'address']])
        pg_shell.do_portgroup_port_list(client_mock, args)
        client_mock.portgroup.list_ports.assert_called_once_with(
            pg_mock, detail=False, fields=['uuid', 'address'])

    def test_do_portgroup_port_list_wrong_fields(self):
        client_mock = mock.MagicMock()
        pg_mock = mock.MagicMock(spec_set=[])
        args = self._get_client_mock_args(portgroup=pg_mock,
                                          fields=[['foo', 'bar']])
        self.assertRaises(exceptions.CommandError,
                          pg_shell.do_portgroup_port_list,
                          client_mock, args)
        self.assertFalse(client_mock.portgroup.list_ports.called)

    def test_do_portgroup_create(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.json = False
        pg_shell.do_portgroup_create(client_mock, args)
        client_mock.portgroup.create.assert_called_once_with()

    def test_do_portgroup_address(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.address = 'aa:bb:cc:dd:ee:ff'
        args.mode = '802.3ad'
        args.properties = ['xmit_hash_policy=layer3+4', 'miimon=100']
        args.json = False
        pg_shell.do_portgroup_create(client_mock, args)
        client_mock.portgroup.create.assert_called_once_with(
            address='aa:bb:cc:dd:ee:ff', mode='802.3ad',
            properties={'xmit_hash_policy': 'layer3+4', 'miimon': 100})

    def test_do_portgroup_node_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node_uuid = 'node-uuid'
        args.json = False
        pg_shell.do_portgroup_create(client_mock, args)
        client_mock.portgroup.create.assert_called_once_with(
            node_uuid='node-uuid')

    def test_do_portgroup_delete(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.portgroup = ['portgroup_uuid']
        pg_shell.do_portgroup_delete(client_mock, args)
        client_mock.portgroup.delete.assert_called_once_with('portgroup_uuid')
