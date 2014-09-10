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

from ironicclient.common import utils as commonutils
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

    def test_do_node_delete(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = ['node_uuid']

        n_shell.do_node_delete(client_mock, args)
        client_mock.node.delete.assert_called_once_with('node_uuid')

    def test_do_node_delete_multiple(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = ['node_uuid1', 'node_uuid2']

        n_shell.do_node_delete(client_mock, args)
        client_mock.node.delete.assert_has_calls(
            [mock.call('node_uuid1'), mock.call('node_uuid2')])

    def test_do_node_update(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.op = 'add'
        args.attributes = [['arg1=val1', 'arg2=val2']]

        n_shell.do_node_update(client_mock, args)
        patch = commonutils.args_array_to_patch(args.op, args.attributes[0])
        client_mock.node.update.assert_called_once_with('node_uuid', patch)

    def test_do_node_create(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()

        n_shell.do_node_create(client_mock, args)
        client_mock.node.create.assert_called_once_with()

    def test_do_node_create_with_driver(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.driver = 'driver'

        n_shell.do_node_create(client_mock, args)
        client_mock.node.create.assert_called_once_with(
            driver='driver')

    def test_do_node_create_with_chassis_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.chassis_uuid = 'chassis_uuid'

        n_shell.do_node_create(client_mock, args)
        client_mock.node.create.assert_called_once_with(
            chassis_uuid='chassis_uuid')

    def test_do_node_create_with_driver_info(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.driver_info = ['arg1=val1', 'arg2=val2']

        n_shell.do_node_create(client_mock, args)
        kwargs = {
                  'driver_info': {'arg1': 'val1', 'arg2': 'val2'}
                  }
        client_mock.node.create.assert_called_once_with(**kwargs)

    def test_do_node_create_with_properties(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.properties = ['arg1=val1', 'arg2=val2']

        n_shell.do_node_create(client_mock, args)
        kwargs = {
                  'properties': {'arg1': 'val1', 'arg2': 'val2'}
                  }
        client_mock.node.create.assert_called_once_with(**kwargs)

    def test_do_node_create_with_extra(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.driver = 'driver_name'
        args.extra = ['arg1=val1', 'arg2=val2']

        n_shell.do_node_create(client_mock, args)
        kwargs = {
                  'driver': 'driver_name',
                  'extra': {'arg1': 'val1', 'arg2': 'val2'}
                  }
        client_mock.node.create.assert_called_once_with(**kwargs)

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

    def test_do_node_set_provision_state_active(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.provision_state = 'active'

        n_shell.do_node_set_provision_state(client_mock, args)
        client_mock.node.set_provision_state.assert_called_once_with(
            'node_uuid', 'active')

    def test_do_node_set_provision_state_deleted(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.provision_state = 'deleted'

        n_shell.do_node_set_provision_state(client_mock, args)
        client_mock.node.set_provision_state.assert_called_once_with(
            'node_uuid', 'deleted')

    def test_do_node_set_provision_state_rebuild(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.provision_state = 'rebuild'

        n_shell.do_node_set_provision_state(client_mock, args)
        client_mock.node.set_provision_state.assert_called_once_with(
            'node_uuid', 'rebuild')

    def test_do_node_set_boot_device(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.persistent = False
        args.device = 'pxe'

        n_shell.do_node_set_boot_device(client_mock, args)
        client_mock.node.set_boot_device.assert_called_once_with(
                                                    'node_uuid', 'pxe', False)

    def test_do_node_get_boot_device(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'

        n_shell.do_node_get_boot_device(client_mock, args)
        client_mock.node.get_boot_device.assert_called_once_with('node_uuid')

    def test_do_node_get_supported_boot_devices(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'

        n_shell.do_node_get_supported_boot_devices(client_mock, args)
        client_mock.node.get_supported_boot_devices.assert_called_once_with(
                                                                   'node_uuid')
