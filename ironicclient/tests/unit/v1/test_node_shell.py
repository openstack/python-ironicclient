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

import json
import tempfile

import mock

from ironicclient.common.apiclient import exceptions
from ironicclient.common import cliutils
from ironicclient.common import utils as commonutils
from ironicclient import exc
from ironicclient.tests.unit import utils
import ironicclient.v1.node_shell as n_shell
import ironicclient.v1.utils as v1_utils


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
               'boot_interface',
               'console_interface',
               'deploy_interface',
               'inspect_interface',
               'management_interface',
               'network_interface',
               'power_interface',
               'raid_interface',
               'storage_interface',
               'vendor_interface',
               'power_state',
               'properties',
               'provision_state',
               'provision_updated_at',
               'reservation',
               'resource_class',
               'target_power_state',
               'target_provision_state',
               'updated_at',
               'inspection_finished_at',
               'inspection_started_at',
               'uuid',
               'raid_config',
               'target_raid_config']
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

    def test_do_node_delete_multiple_with_exception(self):
        client_mock = mock.MagicMock()
        client_mock.node.delete.side_effect = (
            [exceptions.ClientException, None])
        args = mock.MagicMock()
        args.node = ['node_uuid1', 'node_uuid2']

        self.assertRaises(exceptions.ClientException, n_shell.do_node_delete,
                          client_mock, args)
        client_mock.node.delete.assert_has_calls(
            [mock.call('node_uuid1'), mock.call('node_uuid2')])

    def test_do_node_update(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.op = 'add'
        args.attributes = [['arg1=val1', 'arg2=val2']]
        args.json = False

        n_shell.do_node_update(client_mock, args)
        patch = commonutils.args_array_to_patch(args.op, args.attributes[0])
        client_mock.node.update.assert_called_once_with('node_uuid', patch)

    def test_do_node_update_wrong_op(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.op = 'foo'
        args.attributes = [['arg1=val1', 'arg2=val2']]
        args.json = False
        self.assertRaises(exceptions.CommandError,
                          n_shell.do_node_update,
                          client_mock, args)
        self.assertFalse(client_mock.node.update.called)

    def test_do_node_create(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.json = False

        n_shell.do_node_create(client_mock, args)
        client_mock.node.create.assert_called_once_with()

    def test_do_node_create_with_driver(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.driver = 'driver'
        args.json = False

        n_shell.do_node_create(client_mock, args)
        client_mock.node.create.assert_called_once_with(
            driver='driver')

    def test_do_node_create_with_chassis_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.chassis_uuid = 'chassis_uuid'
        args.json = False

        n_shell.do_node_create(client_mock, args)
        client_mock.node.create.assert_called_once_with(
            chassis_uuid='chassis_uuid')

    def test_do_node_create_with_driver_info(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.driver_info = ['arg1=val1', 'arg2=val2']
        args.json = False

        n_shell.do_node_create(client_mock, args)
        kwargs = {'driver_info': {'arg1': 'val1', 'arg2': 'val2'}}
        client_mock.node.create.assert_called_once_with(**kwargs)

    def test_do_node_create_with_properties(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.properties = ['arg1=val1', 'arg2=val2']
        args.json = False

        n_shell.do_node_create(client_mock, args)
        kwargs = {'properties': {'arg1': 'val1', 'arg2': 'val2'}}
        client_mock.node.create.assert_called_once_with(**kwargs)

    def test_do_node_create_with_extra(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.driver = 'driver_name'
        args.extra = ['arg1=val1', 'arg2=val2']
        args.json = False

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
        args.json = False

        n_shell.do_node_create(client_mock, args)
        client_mock.node.create.assert_called_once_with(uuid=args.uuid)

    def test_do_node_create_with_name(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.name = 'node_name'
        args.json = False

        n_shell.do_node_create(client_mock, args)
        client_mock.node.create.assert_called_once_with(name=args.name)

    def test_do_node_create_with_boot_interface(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.boot_interface = 'boot'
        args.json = False

        n_shell.do_node_create(client_mock, args)
        client_mock.node.create.assert_called_once_with(
            boot_interface='boot')

    def test_do_node_create_with_console_interface(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.console_interface = 'console'
        args.json = False

        n_shell.do_node_create(client_mock, args)
        client_mock.node.create.assert_called_once_with(
            console_interface='console')

    def test_do_node_create_with_deploy_interface(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.deploy_interface = 'deploy'
        args.json = False

        n_shell.do_node_create(client_mock, args)
        client_mock.node.create.assert_called_once_with(
            deploy_interface='deploy')

    def test_do_node_create_with_inspect_interface(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.inspect_interface = 'inspect'
        args.json = False

        n_shell.do_node_create(client_mock, args)
        client_mock.node.create.assert_called_once_with(
            inspect_interface='inspect')

    def test_do_node_create_with_management_interface(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.management_interface = 'management'
        args.json = False

        n_shell.do_node_create(client_mock, args)
        client_mock.node.create.assert_called_once_with(
            management_interface='management')

    def test_do_node_create_with_network_interface(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.network_interface = 'neutron'
        args.json = False

        n_shell.do_node_create(client_mock, args)
        client_mock.node.create.assert_called_once_with(
            network_interface='neutron')

    def test_do_node_create_with_power_interface(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.power_interface = 'power'
        args.json = False

        n_shell.do_node_create(client_mock, args)
        client_mock.node.create.assert_called_once_with(
            power_interface='power')

    def test_do_node_create_with_raid_interface(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.raid_interface = 'raid'
        args.json = False

        n_shell.do_node_create(client_mock, args)
        client_mock.node.create.assert_called_once_with(
            raid_interface='raid')

    def test_do_node_create_with_storage_interface(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.storage_interface = 'storage'
        args.json = False

        n_shell.do_node_create(client_mock, args)
        client_mock.node.create.assert_called_once_with(
            storage_interface='storage')

    def test_do_node_create_with_vendor_interface(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.vendor_interface = 'vendor'
        args.json = False

        n_shell.do_node_create(client_mock, args)
        client_mock.node.create.assert_called_once_with(
            vendor_interface='vendor')

    def test_do_node_show(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.instance_uuid = False
        args.fields = None
        args.json = False

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
        args.json = False

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
        args.json = False
        self.assertRaises(exceptions.CommandError,
                          n_shell.do_node_show,
                          client_mock, args)

    def test_do_node_show_by_space_instance_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = '   '
        args.instance_uuid = True
        args.json = False
        self.assertRaises(exceptions.CommandError,
                          n_shell.do_node_show,
                          client_mock, args)

    def test_do_node_show_by_empty_node_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = ''
        args.instance_uuid = False
        args.json = False
        self.assertRaises(exceptions.CommandError,
                          n_shell.do_node_show,
                          client_mock, args)

    def test_do_node_show_by_empty_instance_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = ''
        args.instance_uuid = True
        args.json = False
        self.assertRaises(exceptions.CommandError,
                          n_shell.do_node_show,
                          client_mock, args)

    def test_do_node_show_fields(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.instance_uuid = False
        args.fields = [['uuid', 'power_state']]
        args.json = False
        n_shell.do_node_show(client_mock, args)
        client_mock.node.get.assert_called_once_with(
            'node_uuid', fields=['uuid', 'power_state'])

    def test_do_node_show_invalid_fields(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.instance_uuid = False
        args.fields = [['foo', 'bar']]
        args.json = False
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

    def _do_node_set_power_state_helper(self, power_state,
                                        soft=False, timeout=None, error=False):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.power_state = power_state
        args.soft = soft
        args.power_timeout = timeout

        if error:
            client_mock.node = mock.MagicMock()
            client_mock.node.set_power_state = mock.MagicMock()
            client_mock.node.set_power_state.side_effect = ValueError("fake")
            self.assertRaises(exc.CommandError,
                              n_shell.do_node_set_power_state,
                              client_mock, args)
        else:
            n_shell.do_node_set_power_state(client_mock, args)
            client_mock.node.set_power_state.assert_called_once_with(
                'node_uuid', power_state, soft, timeout=timeout)

    def test_do_node_set_power_state_on(self):
        self._do_node_set_power_state_helper('on')

    def test_do_node_set_power_state_off(self):
        self._do_node_set_power_state_helper('off')

    def test_do_node_set_power_state_reboot(self):
        self._do_node_set_power_state_helper('reboot')

    def test_do_node_set_power_state_on_timeout(self):
        self._do_node_set_power_state_helper('on', timeout=10)

    def test_do_node_set_power_state_on_timeout_fail(self):
        self._do_node_set_power_state_helper('on', timeout=0, error=True)

    def test_do_node_set_power_state_off_timeout(self):
        self._do_node_set_power_state_helper('off', timeout=10)

    def test_do_node_set_power_state_reboot_timeout(self):
        self._do_node_set_power_state_helper('reboot', timeout=10)

    def test_do_node_set_power_state_soft_on_fail(self):
        self._do_node_set_power_state_helper('on', soft=True, error=True)

    def test_do_node_set_power_state_soft_off(self):
        self._do_node_set_power_state_helper('off', soft=True)

    def test_do_node_set_power_state_soft_reboot(self):
        self._do_node_set_power_state_helper('reboot', soft=True)

    def test_do_node_set_power_state_soft_on_timeout_fail(self):
        self._do_node_set_power_state_helper('on', soft=True, timeout=10,
                                             error=True)

    def test_do_node_set_power_state_soft_off_timeout(self):
        self._do_node_set_power_state_helper('off', soft=True, timeout=10)

    def test_do_node_set_power_state_soft_reboot_timeout(self):
        self._do_node_set_power_state_helper('reboot', soft=True, timeout=10)

    def test_do_node_set_target_raid_config_file(self):
        contents = '{"raid": "config"}'

        with tempfile.NamedTemporaryFile(mode='w') as f:
            f.write(contents)
            f.flush()

            node_manager_mock = mock.MagicMock(spec=['set_target_raid_config'])
            client_mock = mock.MagicMock(spec=['node'], node=node_manager_mock)
            args = mock.MagicMock()
            args.node = 'node_uuid'
            args.target_raid_config = f.name

            n_shell.do_node_set_target_raid_config(client_mock, args)
            node_manager_mock.set_target_raid_config.assert_called_once_with(
                'node_uuid', json.loads(contents))

    def test_do_node_set_target_raid_config_string(self):
        node_manager_mock = mock.MagicMock(spec=['set_target_raid_config'])
        client_mock = mock.MagicMock(spec=['node'], node=node_manager_mock)
        target_raid_config_string = (
            '{"logical_disks": [{"size_gb": 100, "raid_level": "1"}]}')
        expected_target_raid_config_string = json.loads(
            target_raid_config_string)

        args = mock.MagicMock(node='node',
                              target_raid_config=target_raid_config_string)
        n_shell.do_node_set_target_raid_config(client_mock, args)

        node_manager_mock.set_target_raid_config.assert_called_once_with(
            'node', expected_target_raid_config_string)

    @mock.patch.object(commonutils, 'get_from_stdin', autospec=True)
    def test_set_target_raid_config_stdin(self, stdin_read_mock):
        node_manager_mock = mock.MagicMock(spec=['set_target_raid_config'])
        client_mock = mock.MagicMock(spec=['node'], node=node_manager_mock)
        target_raid_config_string = (
            '{"logical_disks": [{"size_gb": 100, "raid_level": "1"}]}')
        stdin_read_mock.return_value = target_raid_config_string
        args_mock = mock.MagicMock(node='node',
                                   target_raid_config='-')
        expected_target_raid_config_string = json.loads(
            target_raid_config_string)
        n_shell.do_node_set_target_raid_config(client_mock, args_mock)
        stdin_read_mock.assert_called_once_with('target_raid_config')
        client_mock.node.set_target_raid_config.assert_called_once_with(
            'node', expected_target_raid_config_string)

    @mock.patch.object(commonutils, 'get_from_stdin', autospec=True)
    def test_set_target_raid_config_stdin_exception(self, stdin_read_mock):
        client_mock = mock.MagicMock()
        stdin_read_mock.side_effect = exc.InvalidAttribute('bad')
        args_mock = mock.MagicMock(node='node',
                                   target_raid_config='-')

        self.assertRaises(exc.InvalidAttribute,
                          n_shell.do_node_set_target_raid_config,
                          client_mock, args_mock)

        stdin_read_mock.assert_called_once_with('target_raid_config')
        self.assertFalse(client_mock.set_target_raid_config.called)

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
        args.clean_steps = None
        args.wait_timeout = None

        n_shell.do_node_set_provision_state(client_mock, args)
        client_mock.node.set_provision_state.assert_called_once_with(
            'node_uuid', 'active', configdrive='foo', cleansteps=None)
        self.assertFalse(client_mock.node.wait_for_provision_state.called)

    def test_do_node_set_provision_state_active_wait(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.provision_state = 'active'
        args.config_drive = 'foo'
        args.clean_steps = None
        args.wait_timeout = 0

        n_shell.do_node_set_provision_state(client_mock, args)
        client_mock.node.set_provision_state.assert_called_once_with(
            'node_uuid', 'active', configdrive='foo', cleansteps=None)
        client_mock.node.wait_for_provision_state.assert_called_once_with(
            'node_uuid', expected_state='active', timeout=0,
            poll_interval=v1_utils._LONG_ACTION_POLL_INTERVAL)

    def test_do_node_set_provision_state_deleted(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.provision_state = 'deleted'
        args.config_drive = None
        args.clean_steps = None
        args.wait_timeout = None

        n_shell.do_node_set_provision_state(client_mock, args)
        client_mock.node.set_provision_state.assert_called_once_with(
            'node_uuid', 'deleted', configdrive=None, cleansteps=None)

    def test_do_node_set_provision_state_rebuild(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.provision_state = 'rebuild'
        args.config_drive = None
        args.clean_steps = None
        args.wait_timeout = None

        n_shell.do_node_set_provision_state(client_mock, args)
        client_mock.node.set_provision_state.assert_called_once_with(
            'node_uuid', 'rebuild', configdrive=None, cleansteps=None)

    def test_do_node_set_provision_state_not_active_fails(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.provision_state = 'deleted'
        args.config_drive = 'foo'
        args.clean_steps = None
        args.wait_timeout = None

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
        args.clean_steps = None
        args.wait_timeout = None

        n_shell.do_node_set_provision_state(client_mock, args)
        client_mock.node.set_provision_state.assert_called_once_with(
            'node_uuid', 'inspect', configdrive=None, cleansteps=None)

    def test_do_node_set_provision_state_manage(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.provision_state = 'manage'
        args.config_drive = None
        args.clean_steps = None
        args.wait_timeout = None

        n_shell.do_node_set_provision_state(client_mock, args)
        client_mock.node.set_provision_state.assert_called_once_with(
            'node_uuid', 'manage', configdrive=None, cleansteps=None)

    def test_do_node_set_provision_state_provide(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.provision_state = 'provide'
        args.config_drive = None
        args.clean_steps = None
        args.wait_timeout = None

        n_shell.do_node_set_provision_state(client_mock, args)
        client_mock.node.set_provision_state.assert_called_once_with(
            'node_uuid', 'provide', configdrive=None, cleansteps=None)

    def test_do_node_set_provision_state_clean(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.provision_state = 'clean'
        args.config_drive = None
        clean_steps = '[{"step": "upgrade", "interface": "deploy"}]'
        args.clean_steps = clean_steps
        args.wait_timeout = None

        n_shell.do_node_set_provision_state(client_mock, args)
        client_mock.node.set_provision_state.assert_called_once_with(
            'node_uuid', 'clean', configdrive=None,
            cleansteps=json.loads(clean_steps))

    @mock.patch.object(commonutils, 'get_from_stdin', autospec=True)
    def test_do_node_set_provision_state_clean_stdin(self, mock_stdin):
        clean_steps = '[{"step": "upgrade", "interface": "deploy"}]'
        mock_stdin.return_value = clean_steps
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.provision_state = 'clean'
        args.config_drive = None
        args.clean_steps = '-'
        args.wait_timeout = None

        n_shell.do_node_set_provision_state(client_mock, args)
        mock_stdin.assert_called_once_with('clean steps')
        client_mock.node.set_provision_state.assert_called_once_with(
            'node_uuid', 'clean', configdrive=None,
            cleansteps=json.loads(clean_steps))

    @mock.patch.object(commonutils, 'get_from_stdin', autospec=True)
    def test_do_node_set_provision_state_clean_stdin_fails(self, mock_stdin):
        mock_stdin.side_effect = exc.InvalidAttribute('bad')
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.provision_state = 'clean'
        args.config_drive = None
        args.clean_steps = '-'
        args.wait_timeout = None

        self.assertRaises(exc.InvalidAttribute,
                          n_shell.do_node_set_provision_state,
                          client_mock, args)
        mock_stdin.assert_called_once_with('clean steps')
        self.assertFalse(client_mock.node.set_provision_state.called)

    def test_do_node_set_provision_state_clean_file(self):
        contents = '[{"step": "upgrade", "interface": "deploy"}]'

        with tempfile.NamedTemporaryFile(mode='w') as f:
            f.write(contents)
            f.flush()

            client_mock = mock.MagicMock()
            args = mock.MagicMock()
            args.node = 'node_uuid'
            args.provision_state = 'clean'
            args.config_drive = None
            args.clean_steps = f.name
            args.wait_timeout = None

            n_shell.do_node_set_provision_state(client_mock, args)
            client_mock.node.set_provision_state.assert_called_once_with(
                'node_uuid', 'clean', configdrive=None,
                cleansteps=json.loads(contents))

    def test_do_node_set_provision_state_clean_fails(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.provision_state = 'clean'
        args.config_drive = None
        args.clean_steps = None
        args.wait_timeout = None

        # clean_steps isn't specified
        self.assertRaisesRegex(exceptions.CommandError,
                               'clean-steps.*must be specified',
                               n_shell.do_node_set_provision_state,
                               client_mock, args)
        self.assertFalse(client_mock.node.set_provision_state.called)

    def test_do_node_set_provision_state_not_clean_fails(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.provision_state = 'deleted'
        args.config_drive = None
        clean_steps = '[{"step": "upgrade", "interface": "deploy"}]'
        args.clean_steps = clean_steps
        args.wait_timeout = None

        # clean_steps specified but not cleaning
        self.assertRaisesRegex(exceptions.CommandError,
                               'clean-steps.*only valid',
                               n_shell.do_node_set_provision_state,
                               client_mock, args)
        self.assertFalse(client_mock.node.set_provision_state.called)

    def test_do_node_set_provision_state_abort(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.provision_state = 'abort'
        args.config_drive = None
        args.clean_steps = None
        args.wait_timeout = None

        n_shell.do_node_set_provision_state(client_mock, args)
        client_mock.node.set_provision_state.assert_called_once_with(
            'node_uuid', 'abort', configdrive=None, cleansteps=None)

    def test_do_node_set_provision_state_adopt(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.provision_state = 'adopt'
        args.config_drive = None
        args.clean_steps = None
        args.wait_timeout = 0

        n_shell.do_node_set_provision_state(client_mock, args)
        client_mock.node.set_provision_state.assert_called_once_with(
            'node_uuid', 'adopt', cleansteps=None, configdrive=None)

    def test_do_node_set_provision_state_abort_no_wait(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.provision_state = 'abort'
        args.config_drive = None
        args.clean_steps = None
        args.wait_timeout = 0

        self.assertRaisesRegex(exceptions.CommandError,
                               "not supported for provision state 'abort'",
                               n_shell.do_node_set_provision_state,
                               client_mock, args)
        self.assertFalse(client_mock.node.set_provision_state.called)
        self.assertFalse(client_mock.node.wait_for_provision_state.called)

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
        args.json = False

        n_shell.do_node_get_boot_device(client_mock, args)
        client_mock.node.get_boot_device.assert_called_once_with('node_uuid')

    def test_do_node_inject_nmi(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'

        n_shell.do_node_inject_nmi(client_mock, args)
        client_mock.node.inject_nmi.assert_called_once_with('node_uuid')

    def test_do_node_get_supported_boot_devices(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.json = False

        n_shell.do_node_get_supported_boot_devices(client_mock, args)
        client_mock.node.get_supported_boot_devices.assert_called_once_with(
            'node_uuid')

    def _get_client_mock_args(self, node=None, associated=None,
                              maintenance=None, marker=None, limit=None,
                              sort_dir=None, sort_key=None, detail=False,
                              fields=None, provision_state=None, driver=None,
                              json=False, resource_class=None):
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
        args.driver = driver
        args.json = json
        args.resource_class = resource_class

        return args

    def test_do_node_list(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args()

        n_shell.do_node_list(client_mock, args)
        client_mock.node.list.assert_called_once_with(detail=False)

    def test_do_node_list_detail(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(detail=True)

        n_shell.do_node_list(client_mock, args)
        client_mock.node.list.assert_called_once_with(detail=True)

    def test_do_node_list_provision_state(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(provision_state='wait call-back',
                                          detail=False)

        n_shell.do_node_list(client_mock, args)
        client_mock.node.list.assert_called_once_with(
            provision_state='wait call-back',
            detail=False)

    def test_do_node_list_detail_provision_state(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(provision_state='wait call-back',
                                          detail=True)

        n_shell.do_node_list(client_mock, args)
        client_mock.node.list.assert_called_once_with(
            provision_state='wait call-back',
            detail=True)

    def test_do_node_list_driver(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(driver='fake',
                                          detail=False)

        n_shell.do_node_list(client_mock, args)
        client_mock.node.list.assert_called_once_with(driver='fake',
                                                      detail=False)

    def test_do_node_list_detail_driver(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(driver='fake',
                                          detail=True)

        n_shell.do_node_list(client_mock, args)
        client_mock.node.list.assert_called_once_with(driver='fake',
                                                      detail=True)

    def test_do_node_list_resource_class(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(resource_class='foo',
                                          detail=False)

        n_shell.do_node_list(client_mock, args)
        client_mock.node.list.assert_called_once_with(resource_class='foo',
                                                      detail=False)

    def test_do_node_list_detail_resource_class(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(resource_class='foo',
                                          detail=True)

        n_shell.do_node_list(client_mock, args)
        client_mock.node.list.assert_called_once_with(resource_class='foo',
                                                      detail=True)

    def test_do_node_list_sort_key(self):
        client_mock = mock.MagicMock()
        args = self._get_client_mock_args(sort_key='created_at',
                                          detail=False)

        n_shell.do_node_list(client_mock, args)
        client_mock.node.list.assert_called_once_with(sort_key='created_at',
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
        args.json = False

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
        args = self._get_client_mock_args(node=node_mock,
                                          sort_key='created_at',
                                          detail=False)

        n_shell.do_node_port_list(client_mock, args)
        client_mock.node.list_ports.assert_called_once_with(
            node_mock, sort_key='created_at', detail=False)

    def test_do_node_port_list_wrong_sort_key(self):
        client_mock = mock.MagicMock()
        node_mock = mock.MagicMock(spec_set=[])
        args = self._get_client_mock_args(node=node_mock,
                                          sort_key='node_uuid',
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
                                          sort_key='node_uuid',
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

    def test_do_node_get_vendor_passthru_methods(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        n_shell.do_node_get_vendor_passthru_methods(client_mock, args)
        client_mock.node.get_vendor_passthru_methods.assert_called_once_with(
            'node_uuid')

    def test_do_node_vif_list(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        n_shell.do_node_vif_list(client_mock, args)
        client_mock.node.vif_list.assert_called_once_with(
            'node_uuid')

    def test_do_node_vif_attach(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.vif_id = 'aaa-aaa'
        n_shell.do_node_vif_attach(client_mock, args)
        client_mock.node.vif_attach.assert_called_once_with(
            'node_uuid', 'aaa-aaa')

    def test_do_node_vif_attach_custom_fields(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.vif_id = 'aaa-aaa'
        args.vif_info = ['aaa=bbb', 'ccc=ddd']
        n_shell.do_node_vif_attach(client_mock, args)
        client_mock.node.vif_attach.assert_called_once_with(
            'node_uuid', 'aaa-aaa', aaa='bbb', ccc='ddd')

    def test_do_node_vif_detach(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.node = 'node_uuid'
        args.vif_id = 'aaa-aaa'
        n_shell.do_node_vif_detach(client_mock, args)
        client_mock.node.vif_detach.assert_called_once_with(
            'node_uuid', 'aaa-aaa')
