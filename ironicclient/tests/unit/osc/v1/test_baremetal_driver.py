#  Copyright (c) 2016 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#

import copy

from osc_lib.tests import utils as oscutils

from ironicclient.osc.v1 import baremetal_driver
from ironicclient.tests.unit.osc.v1 import fakes as baremetal_fakes


class TestBaremetalDriver(baremetal_fakes.TestBaremetal):

    def setUp(self):
        super(TestBaremetalDriver, self).setUp()

        self.baremetal_mock = self.app.client_manager.baremetal
        self.baremetal_mock.reset_mock()


class TestListBaremetalDriver(TestBaremetalDriver):

    def setUp(self):
        super(TestListBaremetalDriver, self).setUp()

        self.baremetal_mock.driver.list.return_value = [
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.BAREMETAL_DRIVER),
                loaded=True)
        ]
        self.cmd = baremetal_driver.ListBaremetalDriver(self.app, None)

    def test_baremetal_driver_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        collist = (
            "Supported driver(s)",
            "Active host(s)")
        self.assertEqual(collist, tuple(columns))

        datalist = ((
            baremetal_fakes.baremetal_driver_name,
            ', '.join(baremetal_fakes.baremetal_driver_hosts)), )
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_driver_list_with_type(self):
        arglist = ['--type', baremetal_fakes.baremetal_driver_type]
        verifylist = [('type', baremetal_fakes.baremetal_driver_type)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        collist = (
            "Supported driver(s)",
            "Active host(s)")
        self.assertEqual(collist, tuple(columns))

        datalist = ((
            baremetal_fakes.baremetal_driver_name,
            ', '.join(baremetal_fakes.baremetal_driver_hosts)),)
        self.assertEqual(datalist, tuple(data))

    def test_baremetal_driver_list_with_detail(self):
        arglist = ['--long']
        verifylist = [('long', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        collist = (
            "Supported driver(s)",
            "Type",
            "Active host(s)",
            'Default Boot Interface',
            'Default Console Interface',
            'Default Deploy Interface',
            'Default Inspect Interface',
            'Default Management Interface',
            'Default Network Interface',
            'Default Power Interface',
            'Default RAID Interface',
            'Default Storage Interface',
            'Default Vendor Interface',
            'Enabled Boot Interfaces',
            'Enabled Console Interfaces',
            'Enabled Deploy Interfaces',
            'Enabled Inspect Interfaces',
            'Enabled Management Interfaces',
            'Enabled Network Interfaces',
            'Enabled Power Interfaces',
            'Enabled RAID Interfaces',
            'Enabled Storage Interfaces',
            'Enabled Vendor Interfaces'
        )
        self.assertEqual(collist, tuple(columns))

        datalist = ((
            baremetal_fakes.baremetal_driver_name,
            baremetal_fakes.baremetal_driver_type,
            ', '.join(baremetal_fakes.baremetal_driver_hosts),
            baremetal_fakes.baremetal_driver_default_boot_if,
            baremetal_fakes.baremetal_driver_default_console_if,
            baremetal_fakes.baremetal_driver_default_deploy_if,
            baremetal_fakes.baremetal_driver_default_inspect_if,
            baremetal_fakes.baremetal_driver_default_management_if,
            baremetal_fakes.baremetal_driver_default_network_if,
            baremetal_fakes.baremetal_driver_default_power_if,
            baremetal_fakes.baremetal_driver_default_raid_if,
            baremetal_fakes.baremetal_driver_default_storage_if,
            baremetal_fakes.baremetal_driver_default_vendor_if,
            ', '.join(baremetal_fakes.baremetal_driver_enabled_boot_ifs),
            ', '.join(baremetal_fakes.baremetal_driver_enabled_console_ifs),
            ', '.join(baremetal_fakes.baremetal_driver_enabled_deploy_ifs),
            ', '.join(baremetal_fakes.baremetal_driver_enabled_inspect_ifs),
            ', '.join(baremetal_fakes.baremetal_driver_enabled_management_ifs),
            ', '.join(baremetal_fakes.baremetal_driver_enabled_network_ifs),
            ', '.join(baremetal_fakes.baremetal_driver_enabled_power_ifs),
            ', '.join(baremetal_fakes.baremetal_driver_enabled_raid_ifs),
            ', '.join(baremetal_fakes.baremetal_driver_enabled_storage_ifs),
            ', '.join(baremetal_fakes.baremetal_driver_enabled_vendor_ifs),
        ),)
        self.assertEqual(datalist, tuple(data))


class TestListBaremetalDriverProperty(TestBaremetalDriver):

    def setUp(self):
        super(TestListBaremetalDriverProperty, self).setUp()

        self.baremetal_mock.driver.properties.return_value = {
            'property1': 'description1', 'property2': 'description2'}
        self.cmd = baremetal_driver.ListBaremetalDriverProperty(
            self.app, None)

    def test_baremetal_driver_property_list(self):
        arglist = ['fakedrivername']
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)
        self.baremetal_mock.driver.properties.assert_called_with(*arglist)

        collist = ['Property', 'Description']
        self.assertEqual(collist, columns)
        expected_data = [('property1', 'description1'),
                         ('property2', 'description2')]
        self.assertEqual(expected_data, data)

    def test_baremetal_driver_list_no_arg(self):
        arglist = []
        verifylist = []

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestListBaremetalDriverRaidProperty(TestBaremetalDriver):

    def setUp(self):
        super(TestListBaremetalDriverRaidProperty, self).setUp()

        (self.baremetal_mock.driver.
         raid_logical_disk_properties.return_value) = {
            'RAIDProperty1': 'driver_raid_property1',
            'RAIDProperty2': 'driver_raid_property2',
        }

        self.cmd = (
            baremetal_driver.ListBaremetalDriverRaidProperty(
                self.app, None))

    def test_baremetal_driver_raid_property_list(self):
        arglist = ['fakedrivername']
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        (self.baremetal_mock.driver.
         raid_logical_disk_properties.assert_called_with(*arglist))

        collist = ('Property', 'Description')
        self.assertEqual(collist, tuple(columns))

        expected_data = [('RAIDProperty1', 'driver_raid_property1'),
                         ('RAIDProperty2', 'driver_raid_property2')]
        self.assertEqual(expected_data, data)

    def test_baremetal_driver_raid_property_list_no_arg(self):
        arglist = []
        verifylist = []

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestPassthruCallBaremetalDriver(TestBaremetalDriver):

    def setUp(self):
        super(TestPassthruCallBaremetalDriver, self).setUp()

        self.baremetal_mock.driver.vendor_passthru.return_value = (
            baremetal_fakes.BAREMETAL_DRIVER_PASSTHRU
        )

        self.cmd = baremetal_driver.PassthruCallBaremetalDriver(self.app, None)

    def test_baremetal_driver_passthru_call_with_min_args(self):

        arglist = [
            baremetal_fakes.baremetal_driver_name,
            baremetal_fakes.baremetal_driver_passthru_method,
        ]

        verifylist = [
            ('driver', baremetal_fakes.baremetal_driver_name),
            ('method', baremetal_fakes.baremetal_driver_passthru_method),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        # Set expected values
        args = [
            baremetal_fakes.baremetal_driver_name,
            baremetal_fakes.baremetal_driver_passthru_method,
        ]
        kwargs = {
            'http_method': 'POST',
            'args': {}
        }
        (self.baremetal_mock.driver.vendor_passthru.
            assert_called_once_with(*args, **kwargs))

    def test_baremetal_driver_passthru_call_with_all_args(self):

        arglist = [
            baremetal_fakes.baremetal_driver_name,
            baremetal_fakes.baremetal_driver_passthru_method,
            '--arg', 'arg1=val1', '--arg', 'arg2=val2',
            '--http-method', 'POST'
        ]

        verifylist = [
            ('driver', baremetal_fakes.baremetal_driver_name),
            ('method', baremetal_fakes.baremetal_driver_passthru_method),
            ('arg', ['arg1=val1', 'arg2=val2']),
            ('http_method', 'POST')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        # Set expected values
        args = [
            baremetal_fakes.baremetal_driver_name,
            baremetal_fakes.baremetal_driver_passthru_method,
        ]
        kwargs = {
            'http_method': 'POST',
            'args': {'arg1': 'val1', 'arg2': 'val2'}
        }
        (self.baremetal_mock.driver.vendor_passthru.
            assert_called_once_with(*args, **kwargs))

    def test_baremetal_driver_passthru_call_no_arg(self):
        arglist = []
        verifylist = []

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestPassthruListBaremetalDriver(TestBaremetalDriver):

    def setUp(self):
        super(TestPassthruListBaremetalDriver, self).setUp()

        self.baremetal_mock.driver.get_vendor_passthru_methods.return_value = (
            baremetal_fakes.BAREMETAL_DRIVER_PASSTHRU
        )
        self.cmd = baremetal_driver.PassthruListBaremetalDriver(self.app, None)

    def test_baremetal_driver_passthru_list(self):
        arglist = ['fakedrivername']
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        args = ['fakedrivername']
        (self.baremetal_mock.driver.get_vendor_passthru_methods.
            assert_called_with(*args))

        collist = (
            "Name",
            "Supported HTTP methods",
            "Async",
            "Description",
            "Response is attachment",
        )
        self.assertEqual(collist, tuple(columns))

        datalist = (('lookup', 'POST', 'false', '', 'false'),)

        self.assertEqual(datalist, tuple(data))

    def test_baremetal_driver_passthru_list_no_arg(self):
        arglist = []
        verifylist = []

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)


class TestShowBaremetalDriver(TestBaremetalDriver):

    def setUp(self):
        super(TestShowBaremetalDriver, self).setUp()

        self.baremetal_mock.driver.get.return_value = (
            baremetal_fakes.FakeBaremetalResource(
                None,
                copy.deepcopy(baremetal_fakes.BAREMETAL_DRIVER),
                loaded=True))
        self.cmd = baremetal_driver.ShowBaremetalDriver(self.app, None)

    def test_baremetal_driver_show(self):
        arglist = ['fakedrivername']
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        args = ['fakedrivername']
        self.baremetal_mock.driver.get.assert_called_with(*args)
        self.assertFalse(self.baremetal_mock.driver.properties.called)

        collist = ('default_boot_interface', 'default_console_interface',
                   'default_deploy_interface', 'default_inspect_interface',
                   'default_management_interface', 'default_network_interface',
                   'default_power_interface', 'default_raid_interface',
                   'default_storage_interface', 'default_vendor_interface',
                   'enabled_boot_interfaces', 'enabled_console_interfaces',
                   'enabled_deploy_interfaces', 'enabled_inspect_interfaces',
                   'enabled_management_interfaces',
                   'enabled_network_interfaces', 'enabled_power_interfaces',
                   'enabled_raid_interfaces', 'enabled_storage_interfaces',
                   'enabled_vendor_interfaces', 'hosts', 'name', 'type')
        self.assertEqual(collist, columns)

        datalist = (
            baremetal_fakes.baremetal_driver_default_boot_if,
            baremetal_fakes.baremetal_driver_default_console_if,
            baremetal_fakes.baremetal_driver_default_deploy_if,
            baremetal_fakes.baremetal_driver_default_inspect_if,
            baremetal_fakes.baremetal_driver_default_management_if,
            baremetal_fakes.baremetal_driver_default_network_if,
            baremetal_fakes.baremetal_driver_default_power_if,
            baremetal_fakes.baremetal_driver_default_raid_if,
            baremetal_fakes.baremetal_driver_default_storage_if,
            baremetal_fakes.baremetal_driver_default_vendor_if,
            ', '.join(baremetal_fakes.baremetal_driver_enabled_boot_ifs),
            ', '.join(baremetal_fakes.baremetal_driver_enabled_console_ifs),
            ', '.join(baremetal_fakes.baremetal_driver_enabled_deploy_ifs),
            ', '.join(baremetal_fakes.baremetal_driver_enabled_inspect_ifs),
            ', '.join(baremetal_fakes.baremetal_driver_enabled_management_ifs),
            ', '.join(baremetal_fakes.baremetal_driver_enabled_network_ifs),
            ', '.join(baremetal_fakes.baremetal_driver_enabled_power_ifs),
            ', '.join(baremetal_fakes.baremetal_driver_enabled_raid_ifs),
            ', '.join(baremetal_fakes.baremetal_driver_enabled_storage_ifs),
            ', '.join(baremetal_fakes.baremetal_driver_enabled_vendor_ifs),
            ', '.join(baremetal_fakes.baremetal_driver_hosts),
            baremetal_fakes.baremetal_driver_name,
            baremetal_fakes.baremetal_driver_type)

        self.assertEqual(datalist, tuple(data))

    def test_baremetal_driver_show_no_arg(self):
        arglist = []
        verifylist = []

        self.assertRaises(oscutils.ParserException,
                          self.check_parser,
                          self.cmd, arglist, verifylist)
