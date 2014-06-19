# -*- coding: utf-8 -*-
#
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

from ironicclient.openstack.common import cliutils
from ironicclient.tests import utils
import ironicclient.v1.node_shell as n_shell


class NodeShellTest(utils.BaseTestCase):
    def test_node_show(self):
        actual = {}
        fake_print_dict = lambda data, *args, **kwargs: actual.update(data)
        with mock.patch.object(cliutils, 'print_dict', fake_print_dict):
            node = object()
            n_shell._print_node_show(node)
        exp = ['chassis_uuid',
               'created_at',
               'console_enabled',
               'driver',
               'driver_info',
               'extra',
               'instance_info',
               'instance_uuid',
               'last_error',
               'maintenance',
               'power_state',
               'properties',
               'provision_state',
               'reservation',
               'target_power_state',
               'target_provision_state',
               'updated_at',
               'uuid']
        act = actual.keys()
        self.assertEqual(sorted(exp), sorted(act))

    def test_do_node_vendor_passthru_with_args(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.method = 'method'
        args.arguments = [['arg1=val1', 'arg2=val2']]

        n_shell.do_node_vendor_passthru(client_mock, args)
        kwargs = {
                  'node_id': 'node_uuid',
                  'method': 'method',
                  'args': {'arg1': 'val1', 'arg2': 'val2'}
                  }
        client_mock.node.vendor_passthru.assert_called_once_with(**kwargs)

    def test_do_node_vendor_passthru_without_args(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.method = 'method'
        args.arguments = [[]]

        n_shell.do_node_vendor_passthru(client_mock, args)
        kwargs = {
                  'node_id': 'node_uuid',
                  'method': 'method',
                  'args': {}
                  }
        client_mock.node.vendor_passthru.assert_called_once_with(**kwargs)
