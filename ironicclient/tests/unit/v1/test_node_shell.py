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
from ironicclient.openstack.common.apiclient import exceptions
from ironicclient.openstack.common import cliutils
from ironicclient.tests.unit import utils
import ironicclient.v1.node_shell as n_shell


class NodeShellTest(utils.BaseTestCase):
    def test_node_show(self):
        actual = {}
        fake_print_dict = lambda data, *args, **kwargs: actual.update(data)
        with mock.patch.object(cliutils, 'print_dict', fake_print_dict):
            node = object()
            n_shell._print_node_show(node)
        exp = ['chassis_uuid',
               'clean_step',
               'created_at',
               'console_enabled',
               'driver',
               'driver_info',
               'driver_internal_info',
               'extra',
               'instance_info',
               'instance_uuid',
               'last_error',
               'maintenance',
               'maintenance_reason',
               'name',
               'power_state',
               'properties',
               'provision_state',
               'provision_updated_at',
               'reservation',
               'target_power_state',
               'target_provision_state',
               'updated_at',
               'inspection_finished_at',
               'inspection_started_at',
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

    def test_do_node_update_wrong_op(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.op = 'foo'
        args.attributes = [['arg1=val1', 'arg2=val2']]
        self.assertRaises(exceptions.CommandError,
                          n_shell.do_node_update,
                          client_mock, args)
        self.assertFalse(client_mock.node.update.called)

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
        kwargs = {'driver_info': {'arg1': 'val1', 'arg2': 'val2'}}
        client_mock.node.create.assert_called_once_with(**kwargs)

    def test_do_node_create_with_properties(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.properties = ['arg1=val1', 'arg2=val2']

        n_shell.do_node_create(client_mock, args)
        kwargs = {'properties': {'arg1': 'val1', 'arg2': 'val2'}}
        client_mock.node.create.assert_called_once_with(**kwargs)

    def test_do_node_create_with_extra(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.driver = 'driver_name'
        args.extra = ['arg1=val1', 'arg2=val2']

        n_shell.do_node_create(client_mock, args)
        kwargs = {
            'driver': 'driver_name',
            'extra': {'arg1': 'val1', 'arg2': 'val2'},
        }
        client_mock.node.create.assert_called_once_with(**kwargs)

    def test_do_node_create_with_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.uuid = 'fef99cb8-a0d1-43df-b084-17b3b42b3cbd'

        n_shell.do_node_create(client_mock, args)
        client_mock.node.create.assert_called_once_with(uuid=args.uuid)

    def test_do_node_create_with_name(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.name = 'node_name'

        n_shell.do_node_create(client_mock, args)
        client_mock.node.create.assert_called_once_with(name=args.name)

    def test_do_node_show(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.instance_uuid = False
        args.fields = None

        n_shell.do_node_show(client_mock, args)
        client_mock.node.get.assert_called_once_with('node_uuid', fields=None)
        # assert get_by_instance_uuid() wasn't called
        self.assertFalse(client_mock.node.get_by_instance_uuid.called)

    def test_do_node_show_by_instance_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'instance_uuid'
        args.instance_uuid = True
        args.fields = None

        n_shell.do_node_show(client_mock, args)
        client_mock.node.get_by_instance_uuid.assert_called_once_with(
            'instance_uuid', fields=None)
        # assert get() wasn't called
        self.assertFalse(client_mock.node.get.called)

    def test_do_node_show_by_space_node_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = '   '
        args.instance_uuid = False
        self.assertRaises(exceptions.CommandError,
                          n_shell.do_node_show,
                          client_mock, args)

    def test_do_node_show_by_space_instance_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = '   '
        args.instance_uuid = True
        self.assertRaises(exceptions.CommandError,
                          n_shell.do_node_show,
                          client_mock, args)

    def test_do_node_show_by_empty_node_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = ''
        args.instance_uuid = False
        self.assertRaises(exceptions.CommandError,
                          n_shell.do_node_show,
                          client_mock, args)

    def test_do_node_show_by_empty_instance_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = ''
        args.instance_uuid = True
        self.assertRaises(exceptions.CommandError,
                          n_shell.do_node_show,
                          client_mock, args)

    def test_do_node_show_fields(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.instance_uuid = False
        args.fields = [['uuid', 'power_state']]
        n_shell.do_node_show(client_mock, args)
        client_mock.node.get.assert_called_once_with(
            'node_uuid', fields=['uuid', 'power_state'])

    def test_do_node_show_invalid_fields(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.instance_uuid = False
        args.fields = [['foo', 'bar']]
        self.assertRaises(exceptions.CommandError,
                          n_shell.do_node_show, client_mock, args)

    def test_do_node_set_maintenance_true(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.maintenance_mode = 'true'
        args.reason = 'reason'

        n_shell.do_node_set_maintenance(client_mock, args)
        client_mock.node.set_maintenance.assert_called_once_with(
            'node_uuid', True, maint_reason='reason')

    def test_do_node_set_maintenance_false(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.maintenance_mode = 'false'
        # NOTE(jroll) None is the default. <3 mock.
        args.reason = None

        n_shell.do_node_set_maintenance(client_mock, args)
        client_mock.node.set_maintenance.assert_called_once_with(
            'node_uuid', False, maint_reason=None)

    def test_do_node_set_maintenance_bad(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.maintenance_mode = 'yuck'
        # NOTE(jroll) None is the default. <3 mock.
        args.reason = None

        self.assertRaises(exceptions.CommandError,
                          n_shell.do_node_set_maintenance, client_mock, args)
        self.assertFalse(client_mock.node.set_maintenance.called)

    def test_do_node_set_maintenance_false_with_reason_fails(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.maintenance_mode = 'false'
        args.reason = 'reason'

        self.assertRaises(exceptions.CommandError,
                          n_shell.do_node_set_maintenance,
                          client_mock, args)

    def test_do_node_set_maintenance_on(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.maintenance_mode = 'on'
        args.reason = 'reason'

        n_shell.do_node_set_maintenance(client_mock, args)
        client_mock.node.set_maintenance.assert_called_once_with(
            'node_uuid', True, maint_reason='reason')

    def test_do_node_set_maintenance_off(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.maintenance_mode = 'off'
        # NOTE(jroll) None is the default. <3 mock.
        args.reason = None

        n_shell.do_node_set_maintenance(client_mock, args)
        client_mock.node.set_maintenance.assert_called_once_with(
            'node_uuid', False, maint_reason=None)

    def test_do_node_set_maintenance_off_with_reason_fails(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.maintenance_mode = 'off'
        args.reason = 'reason'

        self.assertRaises(exceptions.CommandError,
                          n_shell.do_node_set_maintenance,
                          client_mock, args)

    def _do_node_set_power_state_helper(self, power_state):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.power_state = power_state

        n_shell.do_node_set_power_state(client_mock, args)
        client_mock.node.set_power_state.assert_called_once_with('node_uuid',
                                                                 power_state)

    def test_do_node_set_power_state_on(self):
        self._do_node_set_power_state_helper('on')

    def test_do_node_set_power_state_off(self):
        self._do_node_set_power_state_helper('off')

    def test_do_node_set_power_state_reboot(self):
        self._do_node_set_power_state_helper('reboot')

    def test_do_node_validate(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'

        n_shell.do_node_validate(client_mock, args)
        client_mock.node.validate.assert_called_once_with('node_uuid')

    def test_do_node_vendor_passthru_with_args(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.http_method = 'POST'
        args.method = 'method'
        args.arguments = [['arg1=val1', 'arg2=val2']]

        n_shell.do_node_vendor_passthru(client_mock, args)
        client_mock.node.vendor_passthru.assert_called_once_with(
            args.node, args.method, args={'arg1': 'val1', 'arg2': 'val2'},
            http_method=args.http_method)

    def test_do_node_vendor_passthru_without_args(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.http_method = 'POST'
        args.method = 'method'
        args.arguments = [[]]

        n_shell.do_node_vendor_passthru(client_mock, args)
        client_mock.node.vendor_passthru.assert_called_once_with(
            args.node, args.method, args={}, http_method=args.http_method)

    def test_do_node_set_provision_state_active(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.provision_state = 'active'
        args.config_drive = 'foo'

        n_shell.do_node_set_provision_state(client_mock, args)
        client_mock.node.set_provision_state.assert_called_once_with(
            'node_uuid', 'active', configdrive='foo')

    def test_do_node_set_provision_state_deleted(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.provision_state = 'deleted'
        args.config_drive = None

        n_shell.do_node_set_provision_state(client_mock, args)
        client_mock.node.set_provision_state.assert_called_once_with(
            'node_uuid', 'deleted', configdrive=None)

    def test_do_node_set_provision_state_rebuild(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.provision_state = 'rebuild'
        args.config_drive = None

        n_shell.do_node_set_provision_state(client_mock, args)
        client_mock.node.set_provision_state.assert_called_once_with(
            'node_uuid', 'rebuild', configdrive=None)

    def test_do_node_set_provision_state_not_active_fails(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.provision_state = 'deleted'
        args.config_drive = 'foo'

        self.assertRaises(exceptions.CommandError,
                          n_shell.do_node_set_provision_state,
                          client_mock, args)
        self.assertFalse(client_mock.node.set_provision_state.called)

    def test_do_node_set_provision_state_inspect(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.provision_state = 'inspect'
        args.config_drive = None

        n_shell.do_node_set_provision_state(client_mock, args)
        client_mock.node.set_provision_state.assert_called_once_with(
            'node_uuid', 'inspect', configdrive=None)

    def test_do_node_set_provision_state_manage(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.provision_state = 'manage'
        args.config_drive = None

        n_shell.do_node_set_provision_state(client_mock, args)
        client_mock.node.set_provision_state.assert_called_once_with(
            'node_uuid', 'manage', configdrive=None)

    def test_do_node_set_provision_state_provide(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.provision_state = 'provide'
        args.config_drive = None

        n_shell.do_node_set_provision_state(client_mock, args)
        client_mock.node.set_provision_state.assert_called_once_with(
            'node_uuid', 'provide', configdrive=None)

    def test_do_node_set_provision_state_abort(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.provision_state = 'abort'
        args.config_drive = None

        n_shell.do_node_set_provision_state(client_mock, args)
        client_mock.node.set_provision_state.assert_called_once_with(
            'node_uuid', 'abort', configdrive=None)

    def test_do_node_set_console_mode(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.enabled = 'true'

        n_shell.do_node_set_console_mode(client_mock, args)
        client_mock.node.set_console_mode.assert_called_once_with(
            'node_uuid', True)

    def test_do_node_set_console_mode_bad(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.enabled = 'yuck'

        self.assertRaises(exceptions.CommandError,
                          n_shell.do_node_set_console_mode, client_mock, args)
        self.assertFalse(client_mock.node.set_console_mode.called)

    def test_do_node_set_boot_device(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.persistent = False
        args.device = 'pxe'

        n_shell.do_node_set_boot_device(client_mock, args)
        client_mock.node.set_boot_device.assert_called_once_with(
            'node_uuid', 'pxe', False)

    def test_do_node_set_boot_device_persistent(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.persistent = True
        args.device = 'disk'

        n_shell.do_node_set_boot_device(client_mock, args)
        client_mock.node.set_boot_device.assert_called_once_with(
            'node_uuid', 'disk', True)

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

    def _get_client_mock_args(self, node=None, associated=None,
                              maintenance=None, marker=None, limit=None,
                              sort_dir=None, sort_key=None, detail=False,
                              fields=None, provision_state=None):
        args = mock.MagicMock()
        args.node = node
        args.associated = associated
        args.maintenance = maintenance
        args.provision_state = provision_state
        args.marker = marker
        args.limit = limit
        args.sort_dir = sort_dir
        args.sort_key = sort_key
        args.detail = detail
        args.fields = fields

        return args

    def test_do_node_list(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args()

        n_shell.do_node_list(client_mock, args)
        client_mock.node.list.assert_called_once_with(detail=False)

    def test_do_node_list_provison_state(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(provision_state='wait call-back')

        n_shell.do_node_list(client_mock, args)
        client_mock.node.list.assert_called_once_with(
            provision_state='wait call-back',
            detail=False)

    def test_do_node_list_detail(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(detail=True)

        n_shell.do_node_list(client_mock, args)
        client_mock.node.list.assert_called_once_with(detail=True)

    def test_do_node_list_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='uuid',
                                          detail=False)

        n_shell.do_node_list(client_mock, args)
        client_mock.node.list.assert_called_once_with(sort_key='uuid',
                                                      detail=False)

    def test_do_node_list_wrong_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='chassis_uuid',
                                          detail=False)

        self.assertRaises(exceptions.CommandError,
                          n_shell.do_node_list,
                          client_mock, args)
        self.assertFalse(client_mock.node.list.called)

    def test_do_node_list_detail_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='created_at',
                                          detail=True)

        n_shell.do_node_list(client_mock, args)
        client_mock.node.list.assert_called_once_with(sort_key='created_at',
                                                      detail=True)

    def test_do_node_list_detail_wrong_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='chassis_uuid',
                                          detail=True)

        self.assertRaises(exceptions.CommandError,
                          n_shell.do_node_list,
                          client_mock, args)
        self.assertFalse(client_mock.node.list.called)

    def test_do_node_list_sort_dir(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_dir='desc',
                                          detail=False)

        n_shell.do_node_list(client_mock, args)
        client_mock.node.list.assert_called_once_with(sort_dir='desc',
                                                      detail=False)

    def test_do_node_list_detail_sort_dir(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_dir='asc',
                                          detail=True)

        n_shell.do_node_list(client_mock, args)
        client_mock.node.list.assert_called_once_with(sort_dir='asc',
                                                      detail=True)

    def test_do_node_list_wrong_sort_dir(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_dir='abc',
                                          detail=False)
        self.assertRaises(exceptions.CommandError,
                          n_shell.do_node_list,
                          client_mock, args)
        self.assertFalse(client_mock.node.list.called)

    def test_do_node_list_maintenance(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(maintenance=True,
                                          detail=False)

        n_shell.do_node_list(client_mock, args)
        client_mock.node.list.assert_called_once_with(maintenance=True,
                                                      detail=False)

    def test_do_node_list_detail_maintenance(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(maintenance=True,
                                          detail=True)

        n_shell.do_node_list(client_mock, args)
        client_mock.node.list.assert_called_once_with(maintenance=True,
                                                      detail=True)

    def test_do_node_list_associated(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(associated=True,
                                          detail=False)

        n_shell.do_node_list(client_mock, args)
        client_mock.node.list.assert_called_once_with(associated=True,
                                                      detail=False)

    def test_do_node_list_detail_associated(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(associated=True,
                                          detail=True)

        n_shell.do_node_list(client_mock, args)
        client_mock.node.list.assert_called_once_with(associated=True,
                                                      detail=True)

    def test_do_node_list_fields(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(fields=[['uuid', 'provision_state']])
        n_shell.do_node_list(client_mock, args)
        client_mock.node.list.assert_called_once_with(
            fields=['uuid', 'provision_state'], detail=False)

    def test_do_node_list_invalid_fields(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(fields=[['foo', 'bar']])
        self.assertRaises(exceptions.CommandError,
                          n_shell.do_node_list, client_mock, args)

    def test_do_node_show_states(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'

        n_shell.do_node_show_states(client_mock, args)
        client_mock.node.states.assert_called_once_with('node_uuid')

    def test_do_node_port_list(self):
        client_mock = mock.MagicMock()
        node_mock = mock.MagicMock(spec_set=[])
        args = self._get_client_mock_args(node=node_mock)

        n_shell.do_node_port_list(client_mock, args)
        client_mock.node.list_ports.assert_called_once_with(
            node_mock, detail=False)

    def test_do_node_port_list_detail(self):
        client_mock = mock.MagicMock()
        node_mock = mock.MagicMock(spec_set=[])
        args = self._get_client_mock_args(node=node_mock, detail=True)
        n_shell.do_node_port_list(client_mock, args)
        client_mock.node.list_ports.assert_called_once_with(
            node_mock, detail=True)

    def test_do_node_port_list_sort_key(self):
        client_mock = mock.MagicMock()
        node_mock = mock.MagicMock(spec_set=[])
        args = self._get_client_mock_args(node=node_mock, sort_key='uuid',
                                          detail=False)

        n_shell.do_node_port_list(client_mock, args)
        client_mock.node.list_ports.assert_called_once_with(
            node_mock, sort_key='uuid', detail=False)

    def test_do_node_port_list_wrong_sort_key(self):
        client_mock = mock.MagicMock()
        node_mock = mock.MagicMock(spec_set=[])
        args = self._get_client_mock_args(node=node_mock,
                                          sort_key='chassis_uuid',
                                          detail=False)

        self.assertRaises(exceptions.CommandError,
                          n_shell.do_node_port_list,
                          client_mock, args)
        self.assertFalse(client_mock.node.list_ports.called)

    def test_do_node_port_list_detail_sort_key(self):
        client_mock = mock.MagicMock()
        node_mock = mock.MagicMock(spec_set=[])
        args = self._get_client_mock_args(node=node_mock,
                                          sort_key='created_at',
                                          detail=True)

        n_shell.do_node_port_list(client_mock, args)
        client_mock.node.list_ports.assert_called_once_with(
            node_mock, sort_key='created_at', detail=True)

    def test_do_node_port_list_detail_wrong_sort_key(self):
        client_mock = mock.MagicMock()
        node_mock = mock.MagicMock(spec_set=[])
        args = self._get_client_mock_args(node=node_mock,
                                          sort_key='chassis_uuid',
                                          detail=True)

        self.assertRaises(exceptions.CommandError,
                          n_shell.do_node_port_list,
                          client_mock, args)
        self.assertFalse(client_mock.node.list_ports.called)

    def test_do_node_port_list_sort_dir(self):
        client_mock = mock.MagicMock()
        node_mock = mock.MagicMock(spec_set=[])
        args = self._get_client_mock_args(node=node_mock, sort_dir='desc',
                                          detail=False)

        n_shell.do_node_port_list(client_mock, args)
        client_mock.node.list_ports.assert_called_once_with(
            node_mock, sort_dir='desc', detail=False)

    def test_do_node_port_list_wrong_sort_dir(self):
        client_mock = mock.MagicMock()
        node_mock = mock.MagicMock(spec_set=[])
        args = self._get_client_mock_args(node=node_mock, sort_dir='abc',
                                          detail=False)
        self.assertRaises(exceptions.CommandError,
                          n_shell.do_node_port_list,
                          client_mock, args)
        self.assertFalse(client_mock.node.list_ports.called)

    def test_do_node_port_list_fields(self):
        client_mock = mock.MagicMock()
        node_mock = mock.MagicMock(spec_set=[])
        args = self._get_client_mock_args(node=node_mock,
                                          fields=[['uuid', 'address']])
        n_shell.do_node_port_list(client_mock, args)
        client_mock.node.list_ports.assert_called_once_with(
            node_mock, fields=['uuid', 'address'], detail=False)

    def test_do_node_port_list_invalid_fields(self):
        client_mock = mock.MagicMock()
        node_mock = mock.MagicMock(spec_set=[])
        args = self._get_client_mock_args(node=node_mock,
                                          fields=[['foo', 'bar']])
        self.assertRaises(exceptions.CommandError,
                          n_shell.do_node_port_list, client_mock, args)
