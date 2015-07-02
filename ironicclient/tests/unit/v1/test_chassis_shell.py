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

from ironicclient.openstack.common.apiclient import exceptions
from ironicclient.openstack.common import cliutils
from ironicclient.tests.unit import utils
import ironicclient.v1.chassis_shell as c_shell


class ChassisShellTest(utils.BaseTestCase):
    def _get_client_mock_args(self, chassis=None, marker=None, limit=None,
                              sort_dir=None, sort_key=None, detail=False):
        args = mock.MagicMock(spec=True)
        args.chassis = chassis
        args.marker = marker
        args.limit = limit
        args.sort_dir = sort_dir
        args.sort_key = sort_key
        args.detail = detail

        return args

    def test_chassis_show(self):
        actual = {}
        fake_print_dict = lambda data, *args, **kwargs: actual.update(data)
        with mock.patch.object(cliutils, 'print_dict', fake_print_dict):
            chassis = object()
            c_shell._print_chassis_show(chassis)
        exp = ['created_at', 'description', 'extra', 'updated_at', 'uuid']
        act = actual.keys()
        self.assertEqual(sorted(exp), sorted(act))

    def test_do_chassis_show_space_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.chassis = '   '
        self.assertRaises(exceptions.CommandError,
                          c_shell.do_chassis_show,
                          client_mock, args)

    def test_do_chassis_show_empty_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.chassis = ''
        self.assertRaises(exceptions.CommandError,
                          c_shell.do_chassis_show,
                          client_mock, args)

    def test_do_chassis_list(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args()

        c_shell.do_chassis_list(client_mock, args)
        client_mock.chassis.list.assert_called_once_with(detail=False)

    def test_do_chassis_list_detail(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(detail=True)

        c_shell.do_chassis_list(client_mock, args)
        client_mock.chassis.list.assert_called_once_with(detail=True)

    def test_do_chassis_list_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='uuid',
                                          detail=False)

        c_shell.do_chassis_list(client_mock, args)
        client_mock.chassis.list.assert_called_once_with(sort_key='uuid',
                                                         detail=False)

    def test_do_chassis_list_wrong_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='extra',
                                          detail=False)

        self.assertRaises(exceptions.CommandError,
                          c_shell.do_chassis_list,
                          client_mock, args)
        self.assertFalse(client_mock.chassis.list.called)

    def test_do_chassis_list_detail_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='created_at',
                                          detail=True)

        c_shell.do_chassis_list(client_mock, args)
        client_mock.chassis.list.assert_called_once_with(sort_key='created_at',
                                                         detail=True)

    def test_do_chassis_list_detail_wrong_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='extra',
                                          detail=True)

        self.assertRaises(exceptions.CommandError,
                          c_shell.do_chassis_list,
                          client_mock, args)
        self.assertFalse(client_mock.chassis.list.called)

    def test_do_chassis_node_list(self):
        client_mock = mock.MagicMock()
        chassis_mock = mock.MagicMock(spec_set=[])
        args = self._get_client_mock_args(chassis=chassis_mock)

        c_shell.do_chassis_node_list(client_mock, args)
        client_mock.chassis.list_nodes.assert_called_once_with(
            chassis_mock, detail=False)

    def test_do_chassis_node_list_details(self):
        client_mock = mock.MagicMock()
        chassis_mock = mock.MagicMock(spec_set=[])
        args = self._get_client_mock_args(chassis=chassis_mock, detail=True)

        c_shell.do_chassis_node_list(client_mock, args)
        client_mock.chassis.list_nodes.assert_called_once_with(
            chassis_mock, detail=True)
