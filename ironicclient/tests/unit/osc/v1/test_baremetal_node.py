#
#   Copyright 2015 Red Hat, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import copy
import mock

from osc_lib.tests import utils as oscutils

from ironicclient.common import utils as commonutils
from ironicclient import exc
from ironicclient.osc.v1 import baremetal_node
from ironicclient.tests.unit.osc.v1 import fakes as baremetal_fakes
from ironicclient.v1 import utils as v1_utils


class TestBaremetal(baremetal_fakes.TestBaremetal):

    def setUp(self):
        super(TestBaremetal, self).setUp()

        # Get a shortcut to the baremetal manager mock
        self.baremetal_mock = self.app.client_manager.baremetal
        self.baremetal_mock.reset_mock()


class TestAdopt(TestBaremetal):
    def setUp(self):
        super(TestAdopt, self).setUp()

        # Get the command object to test
        self.cmd = baremetal_node.AdoptBaremetalNode(self.app, None)

    def test_adopt(self):
        arglist = ['node_uuid']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'adopt'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.set_provision_state.assert_called_once_with(
            'node_uuid', 'adopt', cleansteps=None, configdrive=None)

    def test_adopt_no_wait(self):
        arglist = ['node_uuid']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'adopt')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.wait_for_provision_state.assert_not_called()

    def test_adopt_baremetal_provision_state_active_and_wait(self):
        arglist = ['node_uuid',
                   '--wait', '15']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'adopt'),
            ('wait_timeout', 15)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        test_node = self.baremetal_mock.node
        test_node.wait_for_provision_state.assert_called_once_with(
            'node_uuid', expected_state='active',
            poll_interval=2, timeout=15)

    def test_adopt_baremetal_provision_state_default_wait(self):
        arglist = ['node_uuid',
                   '--wait']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'adopt'),
            ('wait_timeout', 0)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        test_node = self.baremetal_mock.node
        test_node.wait_for_provision_state.assert_called_once_with(
            'node_uuid', expected_state='active',
            poll_interval=2, timeout=0)


class TestBootdeviceSet(TestBaremetal):
    def setUp(self):
        super(TestBootdeviceSet, self).setUp()

        # Get the command object to test
        self.cmd = baremetal_node.BootdeviceSetBaremetalNode(self.app, None)

    def test_bootdevice_set(self):
        arglist = ['node_uuid', 'bios']
        verifylist = [('node', 'node_uuid'),
                      ('device', 'bios')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.set_boot_device.assert_called_once_with(
            'node_uuid', 'bios', False)

    def test_bootdevice_set_persistent(self):
        arglist = ['node_uuid', 'bios', '--persistent']
        verifylist = [('node', 'node_uuid'),
                      ('device', 'bios'),
                      ('persistent', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.set_boot_device.assert_called_once_with(
            'node_uuid', 'bios', True)

    def test_bootdevice_set_invalid_device(self):
        arglist = ['node_uuid', 'foo']
        verifylist = [('node', 'node_uuid'),
                      ('device', 'foo')]

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_bootdevice_set_device_only(self):
        arglist = ['bios']
        verifylist = [('device', 'bios')]

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestBootdeviceShow(TestBaremetal):
    def setUp(self):
        super(TestBootdeviceShow, self).setUp()

        # Get the command object to test
        self.cmd = baremetal_node.BootdeviceShowBaremetalNode(self.app, None)

        self.baremetal_mock.node.get_boot_device.return_value = {
            "boot_device": "pxe", "persistent": False}

        self.baremetal_mock.node.get_supported_boot_devices.return_value = {
            "supported_boot_devices": v1_utils.BOOT_DEVICES}

    def test_bootdevice_show(self):
        arglist = ['node_uuid']
        verifylist = [('node', 'node_uuid')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.get_boot_device.assert_called_once_with(
            'node_uuid')

    def test_bootdevice_supported_show(self):
        arglist = ['node_uuid', '--supported']
        verifylist = [('node', 'node_uuid'), ('supported', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        mock = self.baremetal_mock.node.get_supported_boot_devices
        mock.assert_called_once_with('node_uuid')


class TestConsoleDisable(TestBaremetal):
    def setUp(self):
        super(TestConsoleDisable, self).setUp()

        # Get the command object to test
        self.cmd = baremetal_node.ConsoleDisableBaremetalNode(self.app, None)

    def test_console_disable(self):
        arglist = ['node_uuid']
        verifylist = [('node', 'node_uuid')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.set_console_mode.assert_called_once_with(
            'node_uuid', False)


class TestConsoleEnable(TestBaremetal):
    def setUp(self):
        super(TestConsoleEnable, self).setUp()

        # Get the command object to test
        self.cmd = baremetal_node.ConsoleEnableBaremetalNode(self.app, None)

    def test_console_enable(self):
        arglist = ['node_uuid']
        verifylist = [('node', 'node_uuid')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.set_console_mode.assert_called_once_with(
            'node_uuid', True)


class TestConsoleShow(TestBaremetal):
    def setUp(self):
        super(TestConsoleShow, self).setUp()

        # Get the command object to test
        self.cmd = baremetal_node.ConsoleShowBaremetalNode(self.app, None)

        self.baremetal_mock.node.get_console.return_value = {
            "console_enabled": False, "console_info": None}

    def test_console_show(self):
        arglist = ['node_uuid']
        verifylist = [('node', 'node_uuid')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.get_console.assert_called_once_with(
            'node_uuid')


class TestBaremetalCreate(TestBaremetal):
    def setUp(self):
        super(TestBaremetalCreate, self).setUp()

        self.baremetal_mock.node.create.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.BAREMETAL),
                loaded=True,
            ))

        # Get the command object to test
        self.cmd = baremetal_node.CreateBaremetalNode(self.app, None)
        self.arglist = ['--driver', 'fake_driver']
        self.verifylist = [('driver', 'fake_driver')]
        self.collist = ('chassis_uuid',
                        'instance_uuid',
                        'maintenance',
                        'name',
                        'power_state',
                        'provision_state',
                        'uuid'
                        )
        self.datalist = (
            baremetal_fakes.baremetal_chassis_uuid_empty,
            baremetal_fakes.baremetal_instance_uuid,
            baremetal_fakes.baremetal_maintenance,
            baremetal_fakes.baremetal_name,
            baremetal_fakes.baremetal_power_state,
            baremetal_fakes.baremetal_provision_state,
            baremetal_fakes.baremetal_uuid,
        )
        self.actual_kwargs = {
            'driver': 'fake_driver',
        }

    def check_with_options(self, addl_arglist, addl_verifylist, addl_kwargs):
        arglist = copy.copy(self.arglist) + addl_arglist
        verifylist = copy.copy(self.verifylist) + addl_verifylist

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        collist = copy.copy(self.collist)
        self.assertEqual(collist, columns)

        datalist = copy.copy(self.datalist)
        self.assertEqual(datalist, tuple(data))

        kwargs = copy.copy(self.actual_kwargs)
        kwargs.update(addl_kwargs)

        self.baremetal_mock.node.create.assert_called_once_with(**kwargs)

    def test_baremetal_create_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_create_with_driver(self):
        arglist = copy.copy(self.arglist)

        verifylist = copy.copy(self.verifylist)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        collist = copy.copy(self.collist)
        self.assertEqual(collist, columns)
        self.assertNotIn('ports', columns)
        self.assertNotIn('states', columns)

        datalist = copy.copy(self.datalist)
        self.assertEqual(datalist, tuple(data))

        kwargs = copy.copy(self.actual_kwargs)

        self.baremetal_mock.node.create.assert_called_once_with(**kwargs)

    def test_baremetal_create_with_chassis(self):
        self.check_with_options(['--chassis-uuid', 'chassis_uuid'],
                                [('chassis_uuid', 'chassis_uuid')],
                                {'chassis_uuid': 'chassis_uuid'})

    def test_baremetal_create_with_driver_info(self):
        self.check_with_options(['--driver-info', 'arg1=val1',
                                 '--driver-info', 'arg2=val2'],
                                [('driver_info',
                                  ['arg1=val1',
                                   'arg2=val2'])],
                                {'driver_info': {
                                    'arg1': 'val1',
                                    'arg2': 'val2'}})

    def test_baremetal_create_with_properties(self):
        self.check_with_options(['--property', 'arg1=val1',
                                 '--property', 'arg2=val2'],
                                [('properties',
                                  ['arg1=val1',
                                   'arg2=val2'])],
                                {'properties': {
                                    'arg1': 'val1',
                                    'arg2': 'val2'}})

    def test_baremetal_create_with_extra(self):
        self.check_with_options(['--extra', 'arg1=val1',
                                 '--extra', 'arg2=val2'],
                                [('extra',
                                  ['arg1=val1',
                                   'arg2=val2'])],
                                {'extra': {
                                    'arg1': 'val1',
                                    'arg2': 'val2'}})

    def test_baremetal_create_with_uuid(self):
        self.check_with_options(['--uuid', 'uuid'],
                                [('uuid', 'uuid')],
                                {'uuid': 'uuid'})

    def test_baremetal_create_with_name(self):
        self.check_with_options(['--name', 'name'],
                                [('name', 'name')],
                                {'name': 'name'})

    def test_baremetal_create_with_boot_interface(self):
        self.check_with_options(['--boot-interface', 'boot'],
                                [('boot_interface', 'boot')],
                                {'boot_interface': 'boot'})

    def test_baremetal_create_with_console_interface(self):
        self.check_with_options(['--console-interface', 'console'],
                                [('console_interface', 'console')],
                                {'console_interface': 'console'})

    def test_baremetal_create_with_deploy_interface(self):
        self.check_with_options(['--deploy-interface', 'deploy'],
                                [('deploy_interface', 'deploy')],
                                {'deploy_interface': 'deploy'})

    def test_baremetal_create_with_inspect_interface(self):
        self.check_with_options(['--inspect-interface', 'inspect'],
                                [('inspect_interface', 'inspect')],
                                {'inspect_interface': 'inspect'})

    def test_baremetal_create_with_management_interface(self):
        self.check_with_options(['--management-interface', 'management'],
                                [('management_interface', 'management')],
                                {'management_interface': 'management'})

    def test_baremetal_create_with_network_interface(self):
        self.check_with_options(['--network-interface', 'neutron'],
                                [('network_interface', 'neutron')],
                                {'network_interface': 'neutron'})

    def test_baremetal_create_with_power_interface(self):
        self.check_with_options(['--power-interface', 'power'],
                                [('power_interface', 'power')],
                                {'power_interface': 'power'})

    def test_baremetal_create_with_raid_interface(self):
        self.check_with_options(['--raid-interface', 'raid'],
                                [('raid_interface', 'raid')],
                                {'raid_interface': 'raid'})

    def test_baremetal_create_with_storage_interface(self):
        self.check_with_options(['--storage-interface', 'storage'],
                                [('storage_interface', 'storage')],
                                {'storage_interface': 'storage'})

    def test_baremetal_create_with_vendor_interface(self):
        self.check_with_options(['--vendor-interface', 'vendor'],
                                [('vendor_interface', 'vendor')],
                                {'vendor_interface': 'vendor'})

    def test_baremetal_create_with_resource_class(self):
        self.check_with_options(['--resource-class', 'foo'],
                                [('resource_class', 'foo')],
                                {'resource_class': 'foo'})


class TestBaremetalDelete(TestBaremetal):
    def setUp(self):
        super(TestBaremetalDelete, self).setUp()

        self.baremetal_mock.node.get.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.BAREMETAL),
                loaded=True,
            ))

        # Get the command object to test
        self.cmd = baremetal_node.DeleteBaremetalNode(self.app, None)

    def test_baremetal_delete(self):
        arglist = ['xxx-xxxxxx-xxxx']
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Set expected values
        args = 'xxx-xxxxxx-xxxx'

        self.baremetal_mock.node.delete.assert_called_with(
            args
        )

    def test_baremetal_delete_multiple(self):
        arglist = ['xxx-xxxxxx-xxxx', 'fakename']
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Set expected values
        args = ['xxx-xxxxxx-xxxx', 'fakename']
        self.baremetal_mock.node.delete.has_calls(
            [mock.call(x) for x in args]
        )
        self.assertEqual(2, self.baremetal_mock.node.delete.call_count)

    def test_baremetal_delete_multiple_with_failure(self):
        arglist = ['xxx-xxxxxx-xxxx', 'badname']
        verifylist = []

        self.baremetal_mock.node.delete.side_effect = ['', exc.ClientException]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(exc.ClientException,
                          self.cmd.take_action,
                          parsed_args)

        # Set expected values
        args = ['xxx-xxxxxx-xxxx', 'badname']
        self.baremetal_mock.node.delete.has_calls(
            [mock.call(x) for x in args]
        )
        self.assertEqual(2, self.baremetal_mock.node.delete.call_count)


class TestBaremetalList(TestBaremetal):

    def setUp(self):
        super(TestBaremetalList, self).setUp()

        self.baremetal_mock.node.list.return_value = [
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.BAREMETAL),
                loaded=True,
            ),
        ]

        # Get the command object to test
        self.cmd = baremetal_node.ListBaremetalNode(self.app, None)

    def test_baremetal_list_no_options(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'marker': None,
            'limit': None,
        }

        self.baremetal_mock.node.list.assert_called_with(
            **kwargs
        )

        collist = (
            "UUID",
            "Name",
            "Instance UUID",
            "Power State",
            "Provisioning State",
            "Maintenance"
        )
        self.assertEqual(collist, columns)
        datalist = ((
            baremetal_fakes.baremetal_uuid,
            baremetal_fakes.baremetal_name,
            baremetal_fakes.baremetal_instance_uuid,
            baremetal_fakes.baremetal_power_state,
            baremetal_fakes.baremetal_provision_state,
            baremetal_fakes.baremetal_maintenance,
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'detail': True,
            'marker': None,
            'limit': None,
        }

        self.baremetal_mock.node.list.assert_called_with(
            **kwargs
        )

        collist = ('Chassis UUID', 'Created At', 'Clean Step',
                   'Console Enabled', 'Driver', 'Driver Info',
                   'Driver Internal Info', 'Extra', 'Instance Info',
                   'Instance UUID', 'Last Error', 'Maintenance',
                   'Maintenance Reason', 'Power State', 'Properties',
                   'Provisioning State', 'Provision Updated At',
                   'Current RAID configuration', 'Reservation',
                   'Resource Class',
                   'Target Power State', 'Target Provision State',
                   'Target RAID configuration',
                   'Updated At', 'Inspection Finished At',
                   'Inspection Started At', 'UUID', 'Name',
                   'Boot Interface', 'Console Interface',
                   'Deploy Interface', 'Inspect Interface',
                   'Management Interface', 'Network Interface',
                   'Power Interface', 'RAID Interface',
                   'Storage Interface', 'Vendor Interface')
        self.assertEqual(collist, columns)
        datalist = ((
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            baremetal_fakes.baremetal_instance_uuid,
            '',
            baremetal_fakes.baremetal_maintenance,
            '',
            baremetal_fakes.baremetal_power_state,
            '',
            baremetal_fakes.baremetal_provision_state,
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            baremetal_fakes.baremetal_uuid,
            baremetal_fakes.baremetal_name,
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
            '',
        ), )
        self.assertEqual(datalist, tuple(data))

    def _test_baremetal_list_maintenance(self, maint_option, maint_value):
        arglist = [
            maint_option,
        ]
        verifylist = [
            ('maintenance', maint_value),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'marker': None,
            'limit': None,
            'maintenance': maint_value,
        }

        self.baremetal_mock.node.list.assert_called_with(
            **kwargs
        )

    def test_baremetal_list_maintenance(self):
        self._test_baremetal_list_maintenance('--maintenance', True)

    def test_baremetal_list_no_maintenance(self):
        self._test_baremetal_list_maintenance('--no-maintenance', False)

    def test_baremetal_list_none_maintenance(self):
        arglist = [
        ]
        verifylist = [
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'marker': None,
            'limit': None,
        }

        self.baremetal_mock.node.list.assert_called_with(
            **kwargs
        )

    def test_baremetal_list_both_maintenances(self):
        arglist = [
            '--maintenance',
            '--no-maintenance',
        ]
        verifylist = []

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_list_associated(self):
        arglist = [
            '--associated',
        ]
        verifylist = [
            ('associated', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'marker': None,
            'limit': None,
            'associated': True,
        }

        self.baremetal_mock.node.list.assert_called_with(
            **kwargs
        )

    def test_baremetal_list_unassociated(self):
        arglist = [
            '--unassociated',
        ]
        verifylist = [
            ('associated', False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'marker': None,
            'limit': None,
            'associated': False,
        }

        self.baremetal_mock.node.list.assert_called_with(
            **kwargs
        )

    def test_baremetal_list_both_associated_unassociated_not_allowed(self):
        arglist = [
            '--associated', '--unassociated',
        ]
        verifylist = []

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_list_provision_state(self):
        arglist = [
            '--provision-state', 'active',
        ]
        verifylist = [
            ('provision_state', 'active'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'marker': None,
            'limit': None,
            'provision_state': 'active'
        }

        self.baremetal_mock.node.list.assert_called_with(
            **kwargs
        )

    def test_baremetal_list_driver(self):
        arglist = [
            '--driver', 'ipmi',
        ]
        verifylist = [
            ('driver', 'ipmi'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'marker': None,
            'limit': None,
            'driver': 'ipmi'
        }

        self.baremetal_mock.node.list.assert_called_with(
            **kwargs
        )

    def test_baremetal_list_resource_class(self):
        arglist = [
            '--resource-class', 'foo',
        ]
        verifylist = [
            ('resource_class', 'foo'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'marker': None,
            'limit': None,
            'resource_class': 'foo'
        }

        self.baremetal_mock.node.list.assert_called_with(
            **kwargs
        )

    def test_baremetal_list_chassis(self):
        chassis_uuid = 'aaaaaaaa-1111-bbbb-2222-cccccccccccc'
        arglist = [
            '--chassis', chassis_uuid,
        ]
        verifylist = [
            ('chassis', chassis_uuid),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'marker': None,
            'limit': None,
            'chassis': chassis_uuid
        }

        self.baremetal_mock.node.list.assert_called_with(
            **kwargs
        )

    def test_baremetal_list_fields(self):
        arglist = [
            '--fields', 'uuid', 'name',
        ]
        verifylist = [
            ('fields', [['uuid', 'name']]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'marker': None,
            'limit': None,
            'detail': False,
            'fields': ('uuid', 'name'),
        }

        self.baremetal_mock.node.list.assert_called_with(
            **kwargs
        )

    def test_baremetal_list_fields_multiple(self):
        arglist = [
            '--fields', 'uuid', 'name',
            '--fields', 'extra',
        ]
        verifylist = [
            ('fields', [['uuid', 'name'], ['extra']])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'marker': None,
            'limit': None,
            'detail': False,
            'fields': ('uuid', 'name', 'extra')
        }

        self.baremetal_mock.node.list.assert_called_with(
            **kwargs
        )

    def test_baremetal_list_invalid_fields(self):
        arglist = [
            '--fields', 'uuid', 'invalid'
        ]
        verifylist = [
            ('fields', [['uuid', 'invalid']])
        ]

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestBaremetalMaintenanceSet(TestBaremetal):
    def setUp(self):
        super(TestBaremetalMaintenanceSet, self).setUp()

        # Get the command object to test
        self.cmd = baremetal_node.MaintenanceSetBaremetalNode(self.app, None)

    def test_baremetal_maintenance_on(self):
        arglist = ['node_uuid',
                   '--reason', 'maintenance reason']
        verifylist = [
            ('node', 'node_uuid'),
            ('reason', 'maintenance reason'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.set_maintenance.assert_called_once_with(
            'node_uuid',
            True,
            maint_reason='maintenance reason'
        )

    def test_baremetal_maintenance_on_no_reason(self):
        arglist = ['node_uuid']
        verifylist = [
            ('node', 'node_uuid'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.set_maintenance.assert_called_once_with(
            'node_uuid',
            True,
            maint_reason=None
        )


class TestBaremetalMaintenanceUnset(TestBaremetal):
    def setUp(self):
        super(TestBaremetalMaintenanceUnset, self).setUp()

        # Get the command object to test
        self.cmd = baremetal_node.MaintenanceUnsetBaremetalNode(self.app, None)

    def test_baremetal_maintenance_off(self):
        arglist = ['node_uuid']
        verifylist = [('node', 'node_uuid')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.set_maintenance.assert_called_once_with(
            'node_uuid',
            False)


class TestPassthruCall(TestBaremetal):
    def setUp(self):
        super(TestPassthruCall, self).setUp()

        # Get the command object to test
        self.cmd = baremetal_node.PassthruCallBaremetalNode(self.app, None)

    def test_passthru_call(self):
        arglist = ['node_uuid', 'heartbeat']
        verifylist = [('node', 'node_uuid'),
                      ('method', 'heartbeat')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.node.vendor_passthru.assert_called_once_with(
            'node_uuid', 'heartbeat', http_method='POST', args={})

    def test_passthru_call_http_method(self):
        arglist = ['node_uuid', 'heartbeat', '--http-method', 'PUT']
        verifylist = [('node', 'node_uuid'),
                      ('method', 'heartbeat'),
                      ('http_method', 'PUT')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.baremetal_mock.node.vendor_passthru.assert_called_once_with(
            'node_uuid', 'heartbeat', http_method='PUT', args={})

    def test_passthru_call_args(self):
        arglist = ['node_uuid', 'heartbeat',
                   '--arg', 'key1=value1', '--arg', 'key2=value2']
        verifylist = [('node', 'node_uuid'),
                      ('method', 'heartbeat'),
                      ('arg', ['key1=value1', 'key2=value2'])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        expected_dict = {'key1': 'value1', 'key2': 'value2'}
        self.baremetal_mock.node.vendor_passthru.assert_called_once_with(
            'node_uuid', 'heartbeat', http_method='POST', args=expected_dict)


class TestPassthruList(TestBaremetal):
    def setUp(self):
        super(TestPassthruList, self).setUp()

        # Get the command object to test
        self.cmd = baremetal_node.PassthruListBaremetalNode(self.app, None)

        self.baremetal_mock.node.get_vendor_passthru_methods.return_value = {
            "send_raw": {"require_exclusive_lock": True, "attach": False,
                         "http_methods": ["POST"], "description": "",
                         "async": True},
            "bmc_reset": {"require_exclusive_lock": True, "attach": False,
                          "http_methods": ["POST"], "description": "",
                          "async": True}}

    def test_passthru_list(self):
        arglist = ['node_uuid']
        verifylist = [('node', 'node_uuid')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        mock = self.baremetal_mock.node.get_vendor_passthru_methods
        mock.assert_called_once_with('node_uuid')


class TestBaremetalPower(TestBaremetal):
    def setUp(self):
        super(TestBaremetalPower, self).setUp()

        # Get the command object to test
        self.cmd = baremetal_node.PowerBaremetalNode(self.app, None)

    def test_baremetal_power_just_on(self):
        arglist = ['on']
        verifylist = [('power_state', 'on')]

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_power_just_off(self):
        arglist = ['off']
        verifylist = [('power_state', 'off')]

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_power_uuid_only(self):
        arglist = ['node_uuid']
        verifylist = [('node', 'node_uuid')]

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_power_on(self):
        arglist = ['on', 'node_uuid']
        verifylist = [('power_state', 'on'),
                      ('node', 'node_uuid'),
                      ('soft', False),
                      ('power_timeout', None)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.set_power_state.assert_called_once_with(
            'node_uuid', 'on', False, timeout=None)

    def test_baremetal_power_on_timeout(self):
        arglist = ['on', 'node_uuid', '--power-timeout', '2']
        verifylist = [('power_state', 'on'),
                      ('node', 'node_uuid'),
                      ('soft', False),
                      ('power_timeout', 2)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.set_power_state.assert_called_once_with(
            'node_uuid', 'on', False, timeout=2)

    def test_baremetal_power_off(self):
        arglist = ['off', 'node_uuid']
        verifylist = [('power_state', 'off'),
                      ('node', 'node_uuid'),
                      ('soft', False),
                      ('power_timeout', None)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.set_power_state.assert_called_once_with(
            'node_uuid', 'off', False, timeout=None)

    def test_baremetal_power_off_timeout(self):
        arglist = ['off', 'node_uuid', '--power-timeout', '2']
        verifylist = [('power_state', 'off'),
                      ('node', 'node_uuid'),
                      ('soft', False),
                      ('power_timeout', 2)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.set_power_state.assert_called_once_with(
            'node_uuid', 'off', False, timeout=2)

    def test_baremetal_soft_power_off(self):
        arglist = ['off', 'node_uuid', '--soft']
        verifylist = [('power_state', 'off'),
                      ('node', 'node_uuid'),
                      ('soft', True),
                      ('power_timeout', None)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.set_power_state.assert_called_once_with(
            'node_uuid', 'off', True, timeout=None)

    def test_baremetal_soft_power_off_timeout(self):
        arglist = ['off', 'node_uuid', '--soft', '--power-timeout', '2']
        verifylist = [('power_state', 'off'),
                      ('node', 'node_uuid'),
                      ('soft', True),
                      ('power_timeout', 2)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.set_power_state.assert_called_once_with(
            'node_uuid', 'off', True, timeout=2)


class TestDeployBaremetalProvisionState(TestBaremetal):
    def setUp(self):
        super(TestDeployBaremetalProvisionState, self).setUp()

        # Get the command object to test
        self.cmd = baremetal_node.DeployBaremetalNode(self.app, None)

    def test_deploy_baremetal_provision_state_active_and_configdrive(self):
        arglist = ['node_uuid',
                   '--config-drive', 'path/to/drive']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'active'),
            ('config_drive', 'path/to/drive'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.set_provision_state.assert_called_once_with(
            'node_uuid', 'active',
            cleansteps=None, configdrive='path/to/drive')

    def test_deploy_no_wait(self):
        arglist = ['node_uuid']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'active')
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.baremetal_mock.node.wait_for_provision_state.assert_not_called()

    def test_deploy_baremetal_provision_state_active_and_wait(self):
        arglist = ['node_uuid',
                   '--wait', '15']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'active'),
            ('wait_timeout', 15)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        test_node = self.baremetal_mock.node
        test_node.wait_for_provision_state.assert_called_once_with(
            'node_uuid', expected_state='active',
            poll_interval=10, timeout=15)

    def test_deploy_baremetal_provision_state_default_wait(self):
        arglist = ['node_uuid',
                   '--wait']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'active'),
            ('wait_timeout', 0)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        test_node = self.baremetal_mock.node
        test_node.wait_for_provision_state.assert_called_once_with(
            'node_uuid', expected_state='active',
            poll_interval=10, timeout=0)

    def test_deploy_baremetal_provision_state_mismatch(self):
        arglist = ['node_uuid',
                   '--provision-state', 'abort']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'active'),
        ]

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestManageBaremetalProvisionState(TestBaremetal):
    def setUp(self):
        super(TestManageBaremetalProvisionState, self).setUp()

        # Get the command object to test
        self.cmd = baremetal_node.ManageBaremetalNode(self.app, None)

    def test_manage_no_wait(self):
        arglist = ['node_uuid']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'manage')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.wait_for_provision_state.assert_not_called()

    def test_manage_baremetal_provision_state_manageable_and_wait(self):
        arglist = ['node_uuid',
                   '--wait', '15']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'manage'),
            ('wait_timeout', 15)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        test_node = self.baremetal_mock.node
        test_node.wait_for_provision_state.assert_called_once_with(
            'node_uuid', expected_state='manageable',
            poll_interval=2, timeout=15)

    def test_manage_baremetal_provision_state_default_wait(self):
        arglist = ['node_uuid',
                   '--wait']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'manage'),
            ('wait_timeout', 0)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        test_node = self.baremetal_mock.node
        test_node.wait_for_provision_state.assert_called_once_with(
            'node_uuid', expected_state='manageable',
            poll_interval=2, timeout=0)


class TestCleanBaremetalProvisionState(TestBaremetal):
    def setUp(self):
        super(TestCleanBaremetalProvisionState, self).setUp()

        # Get the command object to test
        self.cmd = baremetal_node.CleanBaremetalNode(self.app, None)

    def test_clean_no_wait(self):
        arglist = ['node_uuid', '--clean-steps', '-']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'clean'),
            ('clean_steps', '-')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.wait_for_provision_state.assert_not_called()

    def test_clean_baremetal_provision_state_manageable_and_wait(self):
        arglist = ['node_uuid',
                   '--wait', '15',
                   '--clean-steps', '-']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'clean'),
            ('wait_timeout', 15),
            ('clean_steps', '-')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        test_node = self.baremetal_mock.node
        test_node.wait_for_provision_state.assert_called_once_with(
            'node_uuid', expected_state='manageable',
            poll_interval=10, timeout=15)

    def test_clean_baremetal_provision_state_default_wait(self):
        arglist = ['node_uuid',
                   '--wait',
                   '--clean-steps', '-']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'clean'),
            ('wait_timeout', 0),
            ('clean_steps', '-')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        test_node = self.baremetal_mock.node
        test_node.wait_for_provision_state.assert_called_once_with(
            'node_uuid', expected_state='manageable',
            poll_interval=10, timeout=0)


class TestInspectBaremetalProvisionState(TestBaremetal):
    def setUp(self):
        super(TestInspectBaremetalProvisionState, self).setUp()

        # Get the command object to test
        self.cmd = baremetal_node.InspectBaremetalNode(self.app, None)

    def test_inspect_no_wait(self):
        arglist = ['node_uuid']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'inspect')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.wait_for_provision_state.assert_not_called()

    def test_inspect_baremetal_provision_state_managable_and_wait(self):
        arglist = ['node_uuid',
                   '--wait', '15']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'inspect'),
            ('wait_timeout', 15)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        test_node = self.baremetal_mock.node
        test_node.wait_for_provision_state.assert_called_once_with(
            'node_uuid', expected_state='manageable',
            poll_interval=2, timeout=15)

    def test_inspect_baremetal_provision_state_default_wait(self):
        arglist = ['node_uuid',
                   '--wait']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'inspect'),
            ('wait_timeout', 0)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        test_node = self.baremetal_mock.node
        test_node.wait_for_provision_state.assert_called_once_with(
            'node_uuid', expected_state='manageable',
            poll_interval=2, timeout=0)


class TestProvideBaremetalProvisionState(TestBaremetal):
    def setUp(self):
        super(TestProvideBaremetalProvisionState, self).setUp()

        # Get the command object to test
        self.cmd = baremetal_node.ProvideBaremetalNode(self.app, None)

    def test_provide_no_wait(self):
        arglist = ['node_uuid']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'provide')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.wait_for_provision_state.assert_not_called()

    def test_provide_baremetal_provision_state_available_and_wait(self):
        arglist = ['node_uuid',
                   '--wait', '15']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'provide'),
            ('wait_timeout', 15)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        test_node = self.baremetal_mock.node
        test_node.wait_for_provision_state.assert_called_once_with(
            'node_uuid', expected_state='available',
            poll_interval=10, timeout=15)

    def test_provide_baremetal_provision_state_default_wait(self):
        arglist = ['node_uuid',
                   '--wait']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'provide'),
            ('wait_timeout', 0)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        test_node = self.baremetal_mock.node
        test_node.wait_for_provision_state.assert_called_once_with(
            'node_uuid', expected_state='available',
            poll_interval=10, timeout=0)


class TestRebuildBaremetalProvisionState(TestBaremetal):
    def setUp(self):
        super(TestRebuildBaremetalProvisionState, self).setUp()

        # Get the command object to test
        self.cmd = baremetal_node.RebuildBaremetalNode(self.app, None)

    def test_rebuild_no_wait(self):
        arglist = ['node_uuid']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'rebuild')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.wait_for_provision_state.assert_not_called()

    def test_rebuild_baremetal_provision_state_active_and_wait(self):
        arglist = ['node_uuid',
                   '--wait', '15']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'rebuild'),
            ('wait_timeout', 15)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        test_node = self.baremetal_mock.node
        test_node.wait_for_provision_state.assert_called_once_with(
            'node_uuid', expected_state='active',
            poll_interval=10, timeout=15)

    def test_rebuild_baremetal_provision_state_default_wait(self):
        arglist = ['node_uuid',
                   '--wait']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'rebuild'),
            ('wait_timeout', 0)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        test_node = self.baremetal_mock.node
        test_node.wait_for_provision_state.assert_called_once_with(
            'node_uuid', expected_state='active',
            poll_interval=10, timeout=0)


class TestUndeployBaremetalProvisionState(TestBaremetal):
    def setUp(self):
        super(TestUndeployBaremetalProvisionState, self).setUp()

        # Get the command object to test
        self.cmd = baremetal_node.UndeployBaremetalNode(self.app, None)

    def test_undeploy_no_wait(self):
        arglist = ['node_uuid']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'deleted')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.wait_for_provision_state.assert_not_called()

    def test_undeploy_baremetal_provision_state_available_and_wait(self):
        arglist = ['node_uuid',
                   '--wait', '15']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'deleted'),
            ('wait_timeout', 15)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        test_node = self.baremetal_mock.node
        test_node.wait_for_provision_state.assert_called_once_with(
            'node_uuid', expected_state='available',
            poll_interval=10, timeout=15)

    def test_undeploy_baremetal_provision_state_default_wait(self):
        arglist = ['node_uuid',
                   '--wait']
        verifylist = [
            ('node', 'node_uuid'),
            ('provision_state', 'deleted'),
            ('wait_timeout', 0)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        test_node = self.baremetal_mock.node
        test_node.wait_for_provision_state.assert_called_once_with(
            'node_uuid', expected_state='available',
            poll_interval=10, timeout=0)


class TestBaremetalReboot(TestBaremetal):
    def setUp(self):
        super(TestBaremetalReboot, self).setUp()

        # Get the command object to test
        self.cmd = baremetal_node.RebootBaremetalNode(self.app, None)

    def test_baremetal_reboot_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_reboot_uuid_only(self):
        arglist = ['node_uuid']
        verifylist = [('node', 'node_uuid'),
                      ('soft', False),
                      ('power_timeout', None)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.set_power_state.assert_called_once_with(
            'node_uuid', 'reboot', False, timeout=None)

    def test_baremetal_reboot_timeout(self):
        arglist = ['node_uuid', '--power-timeout', '2']
        verifylist = [('node', 'node_uuid'),
                      ('soft', False),
                      ('power_timeout', 2)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.set_power_state.assert_called_once_with(
            'node_uuid', 'reboot', False, timeout=2)

    def test_baremetal_soft_reboot(self):
        arglist = ['node_uuid', '--soft']
        verifylist = [('node', 'node_uuid'),
                      ('soft', True),
                      ('power_timeout', None)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.set_power_state.assert_called_once_with(
            'node_uuid', 'reboot', True, timeout=None)

    def test_baremetal_soft_reboot_timeout(self):
        arglist = ['node_uuid', '--soft', '--power-timeout', '2']
        verifylist = [('node', 'node_uuid'),
                      ('soft', True),
                      ('power_timeout', 2)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.set_power_state.assert_called_once_with(
            'node_uuid', 'reboot', True, timeout=2)


class TestBaremetalSet(TestBaremetal):
    def setUp(self):
        super(TestBaremetalSet, self).setUp()

        self.baremetal_mock.node.update.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.BAREMETAL),
                loaded=True,
            ))

        # Get the command object to test
        self.cmd = baremetal_node.SetBaremetalNode(self.app, None)

    def test_baremetal_set_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_set_no_property(self):
        arglist = ['node_uuid']
        verifylist = [
            ('node', 'node_uuid'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.assertFalse(self.baremetal_mock.node.update.called)

    def test_baremetal_set_one_property(self):
        arglist = ['node_uuid', '--property', 'path/to/property=value']
        verifylist = [
            ('node', 'node_uuid'),
            ('property', ['path/to/property=value']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.update.assert_called_once_with(
            'node_uuid',
            [{'path': '/properties/path/to/property',
              'value': 'value',
              'op': 'add'}])

    def test_baremetal_set_multiple_properties(self):
        arglist = [
            'node_uuid',
            '--property', 'path/to/property=value',
            '--property', 'other/path=value2'
        ]
        verifylist = [
            ('node', 'node_uuid'),
            ('property',
             [
                 'path/to/property=value',
                 'other/path=value2',
             ]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.update.assert_called_once_with(
            'node_uuid',
            [{'path': '/properties/path/to/property',
              'value': 'value',
              'op': 'add'},
             {'path': '/properties/other/path',
              'value': 'value2',
              'op': 'add'}]
        )

    def test_baremetal_set_instance_uuid(self):
        arglist = [
            'node_uuid',
            '--instance-uuid', 'xxxxx',
        ]
        verifylist = [
            ('node', 'node_uuid'),
            ('instance_uuid', 'xxxxx')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.update.assert_called_once_with(
            'node_uuid',
            [{'path': '/instance_uuid', 'value': 'xxxxx', 'op': 'add'}]
        )

    def test_baremetal_set_name(self):
        arglist = [
            'node_uuid',
            '--name', 'xxxxx',
        ]
        verifylist = [
            ('node', 'node_uuid'),
            ('name', 'xxxxx')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.update.assert_called_once_with(
            'node_uuid',
            [{'path': '/name', 'value': 'xxxxx', 'op': 'add'}]
        )

    def test_baremetal_set_chassis(self):
        chassis = '4f4135ea-7e58-4e3d-bcc4-b87ca16e980b'
        arglist = [
            'node_uuid',
            '--chassis-uuid', chassis,
        ]
        verifylist = [
            ('node', 'node_uuid'),
            ('chassis_uuid', chassis)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.update.assert_called_once_with(
            'node_uuid',
            [{'path': '/chassis_uuid', 'value': chassis, 'op': 'add'}]
        )

    def test_baremetal_set_driver(self):
        arglist = [
            'node_uuid',
            '--driver', 'xxxxx',
        ]
        verifylist = [
            ('node', 'node_uuid'),
            ('driver', 'xxxxx')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.update.assert_called_once_with(
            'node_uuid',
            [{'path': '/driver', 'value': 'xxxxx', 'op': 'add'}]
        )

    def _test_baremetal_set_hardware_interface(self, interface):
        arglist = [
            'node_uuid',
            '--%s-interface' % interface, 'xxxxx',
        ]
        verifylist = [
            ('node', 'node_uuid'),
            ('%s_interface' % interface, 'xxxxx')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.update.assert_called_once_with(
            'node_uuid',
            [{'path': '/%s_interface' % interface,
              'value': 'xxxxx', 'op': 'add'}]
        )

    def test_baremetal_set_boot_interface(self):
        self._test_baremetal_set_hardware_interface('boot')

    def test_baremetal_set_console_interface(self):
        self._test_baremetal_set_hardware_interface('console')

    def test_baremetal_set_deploy_interface(self):
        self._test_baremetal_set_hardware_interface('deploy')

    def test_baremetal_set_inspect_interface(self):
        self._test_baremetal_set_hardware_interface('inspect')

    def test_baremetal_set_management_interface(self):
        self._test_baremetal_set_hardware_interface('management')

    def test_baremetal_set_network_interface(self):
        self._test_baremetal_set_hardware_interface('network')

    def test_baremetal_set_power_interface(self):
        self._test_baremetal_set_hardware_interface('power')

    def test_baremetal_set_raid_interface(self):
        self._test_baremetal_set_hardware_interface('raid')

    def test_baremetal_set_storage_interface(self):
        self._test_baremetal_set_hardware_interface('storage')

    def test_baremetal_set_vendor_interface(self):
        self._test_baremetal_set_hardware_interface('vendor')

    def test_baremetal_set_resource_class(self):
        arglist = [
            'node_uuid',
            '--resource-class', 'foo',
        ]
        verifylist = [
            ('node', 'node_uuid'),
            ('resource_class', 'foo')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.update.assert_called_once_with(
            'node_uuid',
            [{'path': '/resource_class', 'value': 'foo', 'op': 'add'}]
        )

    def test_baremetal_set_extra(self):
        arglist = [
            'node_uuid',
            '--extra', 'foo=bar',
        ]
        verifylist = [
            ('node', 'node_uuid'),
            ('extra', ['foo=bar'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.update.assert_called_once_with(
            'node_uuid',
            [{'path': '/extra/foo', 'value': 'bar', 'op': 'add'}]
        )

    def test_baremetal_set_driver_info(self):
        arglist = [
            'node_uuid',
            '--driver-info', 'foo=bar',
        ]
        verifylist = [
            ('node', 'node_uuid'),
            ('driver_info', ['foo=bar'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.update.assert_called_once_with(
            'node_uuid',
            [{'path': '/driver_info/foo', 'value': 'bar', 'op': 'add'}]
        )

    def test_baremetal_set_instance_info(self):
        arglist = [
            'node_uuid',
            '--instance-info', 'foo=bar',
        ]
        verifylist = [
            ('node', 'node_uuid'),
            ('instance_info', ['foo=bar'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.update.assert_called_once_with(
            'node_uuid',
            [{'path': '/instance_info/foo', 'value': 'bar', 'op': 'add'}]
        )

    @mock.patch.object(commonutils, 'get_from_stdin', autospec=True)
    @mock.patch.object(commonutils, 'handle_json_or_file_arg', autospec=True)
    def test_baremetal_set_target_raid_config(self, mock_handle, mock_stdin):
        self.cmd.log = mock.Mock(autospec=True)
        target_raid_config_string = '{"raid": "config"}'
        expected_target_raid_config = {'raid': 'config'}
        mock_handle.return_value = expected_target_raid_config.copy()

        arglist = ['node_uuid',
                   '--target-raid-config', target_raid_config_string]
        verifylist = [('node', 'node_uuid'),
                      ('target_raid_config', target_raid_config_string)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.cmd.log.warning.assert_not_called()
        self.assertFalse(mock_stdin.called)
        mock_handle.assert_called_once_with(target_raid_config_string)
        self.baremetal_mock.node.set_target_raid_config.\
            assert_called_once_with('node_uuid', expected_target_raid_config)
        self.assertFalse(self.baremetal_mock.node.update.called)

    @mock.patch.object(commonutils, 'get_from_stdin', autospec=True)
    @mock.patch.object(commonutils, 'handle_json_or_file_arg', autospec=True)
    def test_baremetal_set_target_raid_config_and_name(
            self, mock_handle, mock_stdin):
        self.cmd.log = mock.Mock(autospec=True)
        target_raid_config_string = '{"raid": "config"}'
        expected_target_raid_config = {'raid': 'config'}
        mock_handle.return_value = expected_target_raid_config.copy()

        arglist = ['node_uuid',
                   '--name', 'xxxxx',
                   '--target-raid-config', target_raid_config_string]
        verifylist = [('node', 'node_uuid'),
                      ('name', 'xxxxx'),
                      ('target_raid_config', target_raid_config_string)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.cmd.log.warning.assert_not_called()
        self.assertFalse(mock_stdin.called)
        mock_handle.assert_called_once_with(target_raid_config_string)
        self.baremetal_mock.node.set_target_raid_config.\
            assert_called_once_with('node_uuid', expected_target_raid_config)
        self.baremetal_mock.node.update.assert_called_once_with(
            'node_uuid',
            [{'path': '/name', 'value': 'xxxxx', 'op': 'add'}])

    @mock.patch.object(commonutils, 'get_from_stdin', autospec=True)
    @mock.patch.object(commonutils, 'handle_json_or_file_arg', autospec=True)
    def test_baremetal_set_target_raid_config_stdin(self, mock_handle,
                                                    mock_stdin):
        self.cmd.log = mock.Mock(autospec=True)
        target_value = '-'
        target_raid_config_string = '{"raid": "config"}'
        expected_target_raid_config = {'raid': 'config'}
        mock_stdin.return_value = target_raid_config_string
        mock_handle.return_value = expected_target_raid_config.copy()

        arglist = ['node_uuid',
                   '--target-raid-config', target_value]
        verifylist = [('node', 'node_uuid'),
                      ('target_raid_config', target_value)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.cmd.log.warning.assert_not_called()
        mock_stdin.assert_called_once_with('target_raid_config')
        mock_handle.assert_called_once_with(target_raid_config_string)
        self.baremetal_mock.node.set_target_raid_config.\
            assert_called_once_with('node_uuid', expected_target_raid_config)
        self.assertFalse(self.baremetal_mock.node.update.called)

    @mock.patch.object(commonutils, 'get_from_stdin', autospec=True)
    @mock.patch.object(commonutils, 'handle_json_or_file_arg', autospec=True)
    def test_baremetal_set_target_raid_config_stdin_exception(
            self, mock_handle, mock_stdin):
        self.cmd.log = mock.Mock(autospec=True)
        target_value = '-'
        mock_stdin.side_effect = exc.InvalidAttribute('bad')

        arglist = ['node_uuid',
                   '--target-raid-config', target_value]
        verifylist = [('node', 'node_uuid'),
                      ('target_raid_config', target_value)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exc.InvalidAttribute,
                          self.cmd.take_action, parsed_args)

        self.cmd.log.warning.assert_not_called()
        mock_stdin.assert_called_once_with('target_raid_config')
        self.assertFalse(mock_handle.called)
        self.assertFalse(
            self.baremetal_mock.node.set_target_raid_config.called)
        self.assertFalse(self.baremetal_mock.node.update.called)


class TestBaremetalShow(TestBaremetal):
    def setUp(self):
        super(TestBaremetalShow, self).setUp()

        self.baremetal_mock.node.get.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.BAREMETAL),
                loaded=True,
            ))

        self.baremetal_mock.node.get_by_instance_uuid.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.BAREMETAL),
                loaded=True,
            ))

        # Get the command object to test
        self.cmd = baremetal_node.ShowBaremetalNode(self.app, None)

    def test_baremetal_show(self):
        arglist = ['xxx-xxxxxx-xxxx']
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        args = ['xxx-xxxxxx-xxxx']

        self.baremetal_mock.node.get.assert_called_with(
            *args, fields=None
        )

        collist = ('chassis_uuid',
                   'instance_uuid',
                   'maintenance',
                   'name',
                   'power_state',
                   'provision_state',
                   'uuid'
                   )
        self.assertEqual(collist, columns)
        self.assertNotIn('ports', columns)
        self.assertNotIn('states', columns)
        datalist = (
            baremetal_fakes.baremetal_chassis_uuid_empty,
            baremetal_fakes.baremetal_instance_uuid,
            baremetal_fakes.baremetal_maintenance,
            baremetal_fakes.baremetal_name,
            baremetal_fakes.baremetal_power_state,
            baremetal_fakes.baremetal_provision_state,
            baremetal_fakes.baremetal_uuid
        )
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_show_no_node(self):
        arglist = []
        verifylist = []

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_show_with_instance_uuid(self):
        arglist = [
            'xxx-xxxxxx-xxxx',
            '--instance',
        ]

        verifylist = [
            ('instance_uuid', True)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        self.cmd.take_action(parsed_args)

        # Set expected values
        args = ['xxx-xxxxxx-xxxx']

        self.baremetal_mock.node.get_by_instance_uuid.assert_called_with(
            *args, fields=None
        )

    def test_baremetal_show_fields(self):
        arglist = [
            'xxxxx',
            '--fields', 'uuid', 'name',
        ]
        verifylist = [
            ('node', 'xxxxx'),
            ('fields', [['uuid', 'name']]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)
        self.assertNotIn('chassis_uuid', columns)

        # Set expected values
        args = ['xxxxx']
        fields = ['uuid', 'name']

        self.baremetal_mock.node.get.assert_called_with(
            *args, fields=fields
        )

    def test_baremetal_show_fields_multiple(self):
        arglist = [
            'xxxxx',
            '--fields', 'uuid', 'name',
            '--fields', 'extra',
        ]
        verifylist = [
            ('node', 'xxxxx'),
            ('fields', [['uuid', 'name'], ['extra']])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.assertNotIn('chassis_uuid', columns)
        # Set expected values
        args = ['xxxxx']
        fields = ['uuid', 'name', 'extra']

        self.baremetal_mock.node.get.assert_called_with(
            *args, fields=fields
        )

    def test_baremetal_show_invalid_fields(self):
        arglist = [
            'xxxxx',
            '--fields', 'uuid', 'invalid'
        ]
        verifylist = [
            ('node', 'xxxxx'),
            ('fields', [['uuid', 'invalid']])
        ]

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestBaremetalUnset(TestBaremetal):
    def setUp(self):
        super(TestBaremetalUnset, self).setUp()

        self.baremetal_mock.node.update.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.BAREMETAL),
                loaded=True,
            ))

        # Get the command object to test
        self.cmd = baremetal_node.UnsetBaremetalNode(self.app, None)

    def test_baremetal_unset_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_unset_no_property(self):
        arglist = ['node_uuid']
        verifylist = [('node', 'node_uuid')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)
        self.assertFalse(self.baremetal_mock.node.update.called)

    def test_baremetal_unset_one_property(self):
        arglist = ['node_uuid', '--property', 'path/to/property']
        verifylist = [('node', 'node_uuid'),
                      ('property', ['path/to/property'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.update.assert_called_once_with(
            'node_uuid',
            [{'path': '/properties/path/to/property', 'op': 'remove'}])

    def test_baremetal_unset_multiple_properties(self):
        arglist = ['node_uuid',
                   '--property', 'path/to/property',
                   '--property', 'other/path']
        verifylist = [('node', 'node_uuid'),
                      ('property',
                       ['path/to/property',
                        'other/path'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.update.assert_called_once_with(
            'node_uuid',
            [{'path': '/properties/path/to/property', 'op': 'remove'},
             {'path': '/properties/other/path', 'op': 'remove'}]
        )

    def test_baremetal_unset_instance_uuid(self):
        arglist = [
            'node_uuid',
            '--instance-uuid',
        ]
        verifylist = [
            ('node', 'node_uuid'),
            ('instance_uuid', True)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.update.assert_called_once_with(
            'node_uuid',
            [{'path': '/instance_uuid', 'op': 'remove'}]
        )

    def test_baremetal_unset_name(self):
        arglist = [
            'node_uuid',
            '--name',
        ]
        verifylist = [
            ('node', 'node_uuid'),
            ('name', True)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.update.assert_called_once_with(
            'node_uuid',
            [{'path': '/name', 'op': 'remove'}]
        )

    def test_baremetal_unset_resource_class(self):
        arglist = [
            'node_uuid',
            '--resource-class',
        ]
        verifylist = [
            ('node', 'node_uuid'),
            ('resource_class', True)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.update.assert_called_once_with(
            'node_uuid',
            [{'path': '/resource_class', 'op': 'remove'}]
        )

    def test_baremetal_unset_extra(self):
        arglist = [
            'node_uuid',
            '--extra', 'foo',
        ]
        verifylist = [
            ('node', 'node_uuid'),
            ('extra', ['foo'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.update.assert_called_once_with(
            'node_uuid',
            [{'path': '/extra/foo', 'op': 'remove'}]
        )

    def test_baremetal_unset_driver_info(self):
        arglist = [
            'node_uuid',
            '--driver-info', 'foo',
        ]
        verifylist = [
            ('node', 'node_uuid'),
            ('driver_info', ['foo'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.update.assert_called_once_with(
            'node_uuid',
            [{'path': '/driver_info/foo', 'op': 'remove'}]
        )

    def test_baremetal_unset_instance_info(self):
        arglist = [
            'node_uuid',
            '--instance-info', 'foo',
        ]
        verifylist = [
            ('node', 'node_uuid'),
            ('instance_info', ['foo'])
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.update.assert_called_once_with(
            'node_uuid',
            [{'path': '/instance_info/foo', 'op': 'remove'}]
        )

    def test_baremetal_unset_target_raid_config(self):
        self.cmd.log = mock.Mock(autospec=True)
        arglist = [
            'node_uuid',
            '--target-raid-config',
        ]
        verifylist = [
            ('node', 'node_uuid'),
            ('target_raid_config', True)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.cmd.log.warning.assert_not_called()
        self.assertFalse(self.baremetal_mock.node.update.called)
        self.baremetal_mock.node.set_target_raid_config.\
            assert_called_once_with('node_uuid', {})

    def test_baremetal_unset_target_raid_config_and_name(self):
        self.cmd.log = mock.Mock(autospec=True)
        arglist = [
            'node_uuid',
            '--name',
            '--target-raid-config',
        ]
        verifylist = [
            ('node', 'node_uuid'),
            ('name', True),
            ('target_raid_config', True)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.cmd.log.warning.assert_not_called()
        self.baremetal_mock.node.set_target_raid_config.\
            assert_called_once_with('node_uuid', {})
        self.baremetal_mock.node.update.assert_called_once_with(
            'node_uuid',
            [{'path': '/name', 'op': 'remove'}]
        )

    def test_baremetal_unset_chassis_uuid(self):
        arglist = [
            'node_uuid',
            '--chassis-uuid',
        ]
        verifylist = [
            ('node', 'node_uuid'),
            ('chassis_uuid', True)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.update.assert_called_once_with(
            'node_uuid',
            [{'path': '/chassis_uuid', 'op': 'remove'}]
        )

    def _test_baremetal_unset_hw_interface(self, interface):
        arglist = [
            'node_uuid',
            '--%s-interface' % interface,
        ]
        verifylist = [
            ('node', 'node_uuid'),
            ('%s_interface' % interface, True)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.update.assert_called_once_with(
            'node_uuid',
            [{'path': '/%s_interface' % interface, 'op': 'remove'}]
        )

    def test_baremetal_unset_boot_interface(self):
        self._test_baremetal_unset_hw_interface('boot')

    def test_baremetal_unset_console_interface(self):
        self._test_baremetal_unset_hw_interface('console')

    def test_baremetal_unset_deploy_interface(self):
        self._test_baremetal_unset_hw_interface('deploy')

    def test_baremetal_unset_inspect_interface(self):
        self._test_baremetal_unset_hw_interface('inspect')

    def test_baremetal_unset_management_interface(self):
        self._test_baremetal_unset_hw_interface('management')

    def test_baremetal_unset_network_interface(self):
        self._test_baremetal_unset_hw_interface('network')

    def test_baremetal_unset_power_interface(self):
        self._test_baremetal_unset_hw_interface('power')

    def test_baremetal_unset_raid_interface(self):
        self._test_baremetal_unset_hw_interface('raid')

    def test_baremetal_unset_storage_interface(self):
        self._test_baremetal_unset_hw_interface('storage')

    def test_baremetal_unset_vendor_interface(self):
        self._test_baremetal_unset_hw_interface('vendor')


class TestValidate(TestBaremetal):
    def setUp(self):
        super(TestValidate, self).setUp()

        # Get the command object to test
        self.cmd = baremetal_node.ValidateBaremetalNode(self.app, None)

        self.baremetal_mock.node.validate.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                {'management': {'result': True},
                 'console': {'reason': "Missing 'ipmi_terminal_port'",
                             'result': False},
                 'network': {'result': True},
                 'power': {'result': True},
                 'deploy': {'result': True},
                 'inspect': {'reason': "not supported", 'result': None},
                 'boot': {'result': True},
                 'raid': {'result': True}},
                loaded=True,
            ))

    def test_baremetal_validate_no_arg(self):
        arglist = []
        verifylist = []

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_validate(self):
        arglist = ['node_uuid']
        verifylist = [('node', 'node_uuid')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.validate.assert_called_once_with('node_uuid')


class TestVifList(TestBaremetal):
    def setUp(self):
        super(TestVifList, self).setUp()

        self.baremetal_mock.node.vif_list.return_value = [
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.VIFS),
                loaded=True,
            ),
        ]

        # Get the command object to test
        self.cmd = baremetal_node.VifListBaremetalNode(self.app, None)

    def test_baremetal_vif_list(self):
        arglist = ['node_uuid']
        verifylist = [('node', 'node_uuid')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.vif_list.assert_called_once_with('node_uuid')


class TestVifAttach(TestBaremetal):
    def setUp(self):
        super(TestVifAttach, self).setUp()

        # Get the command object to test
        self.cmd = baremetal_node.VifAttachBaremetalNode(self.app, None)

    def test_baremetal_vif_attach(self):
        arglist = ['node_uuid', 'aaa-aaa']
        verifylist = [('node', 'node_uuid'),
                      ('vif_id', 'aaa-aaa')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.vif_attach.assert_called_once_with(
            'node_uuid', 'aaa-aaa')

    def test_baremetal_vif_attach_custom_fields(self):
        arglist = ['node_uuid', 'aaa-aaa', '--vif-info', 'foo=bar']
        verifylist = [('node', 'node_uuid'),
                      ('vif_id', 'aaa-aaa'),
                      ('vif_info', ['foo=bar'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.vif_attach.assert_called_once_with(
            'node_uuid', 'aaa-aaa', foo='bar')


class TestVifDetach(TestBaremetal):
    def setUp(self):
        super(TestVifDetach, self).setUp()

        # Get the command object to test
        self.cmd = baremetal_node.VifDetachBaremetalNode(self.app, None)

    def test_baremetal_vif_detach(self):
        arglist = ['node_uuid', 'aaa-aaa']
        verifylist = [('node', 'node_uuid'),
                      ('vif_id', 'aaa-aaa')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.vif_detach.assert_called_once_with(
            'node_uuid', 'aaa-aaa')


class TestBaremetalInject(TestBaremetal):
    def setUp(self):
        super(TestBaremetalInject, self).setUp()

        # Get the command object to test
        self.cmd = baremetal_node.InjectNmiBaremetalNode(self.app, None)

    def test_baremetal_inject_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_baremetal_inject_nmi_uuid(self):
        arglist = ['node_uuid']
        verifylist = [('node', 'node_uuid')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.baremetal_mock.node.inject_nmi.assert_called_once_with(
            'node_uuid')
