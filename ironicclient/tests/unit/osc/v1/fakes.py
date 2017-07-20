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

import mock
from osc_lib.tests import utils

from ironicclient.tests.unit.osc import fakes

baremetal_chassis_uuid = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
baremetal_chassis_uuid_empty = ''
baremetal_properties_empty = ''
baremetal_chassis_description = 'chassis description'
baremetal_chassis_extra = {}
BAREMETAL_CHASSIS = {
    'uuid': baremetal_chassis_uuid,
    'description': baremetal_chassis_description,
    'extra': baremetal_chassis_extra,
}

baremetal_uuid = 'xxx-xxxxxx-xxxx'
baremetal_name = 'fake name'
baremetal_instance_uuid = 'yyy-yyyyyy-yyyy'
baremetal_power_state = None
baremetal_provision_state = None
baremetal_maintenance = False

BAREMETAL = {
    'uuid': baremetal_uuid,
    'name': baremetal_name,
    'instance_uuid': baremetal_instance_uuid,
    'power_state': baremetal_power_state,
    'provision_state': baremetal_provision_state,
    'maintenance': baremetal_maintenance,
    'links': [],
    'volume': [],
}

baremetal_port_uuid = 'zzz-zzzzzz-zzzz'
baremetal_port_address = 'AA:BB:CC:DD:EE:FF'
baremetal_port_extra = {'key1': 'value1',
                        'key2': 'value2'}
baremetal_port_physical_network = 'physnet1'

BAREMETAL_PORT = {
    'uuid': baremetal_port_uuid,
    'address': baremetal_port_address,
    'extra': baremetal_port_extra,
    'node_uuid': baremetal_uuid,
}

baremetal_driver_hosts = ['fake-host1', 'fake-host2']
baremetal_driver_name = 'fakedrivername'
baremetal_driver_type = 'classic'
baremetal_driver_default_boot_if = 'boot'
baremetal_driver_default_console_if = 'console'
baremetal_driver_default_deploy_if = 'deploy'
baremetal_driver_default_inspect_if = 'inspect'
baremetal_driver_default_management_if = 'management'
baremetal_driver_default_network_if = 'network'
baremetal_driver_default_power_if = 'power'
baremetal_driver_default_raid_if = 'raid'
baremetal_driver_default_storage_if = 'storage'
baremetal_driver_default_vendor_if = 'vendor'
baremetal_driver_enabled_boot_ifs = ['boot', 'boot2']
baremetal_driver_enabled_console_ifs = ['console', 'console2']
baremetal_driver_enabled_deploy_ifs = ['deploy', 'deploy2']
baremetal_driver_enabled_inspect_ifs = ['inspect', 'inspect2']
baremetal_driver_enabled_management_ifs = ['management', 'management2']
baremetal_driver_enabled_network_ifs = ['network', 'network2']
baremetal_driver_enabled_power_ifs = ['power', 'power2']
baremetal_driver_enabled_raid_ifs = ['raid', 'raid2']
baremetal_driver_enabled_storage_ifs = ['storage', 'storage2']
baremetal_driver_enabled_vendor_ifs = ['vendor', 'vendor2']

BAREMETAL_DRIVER = {
    'hosts': baremetal_driver_hosts,
    'name': baremetal_driver_name,
    'type': baremetal_driver_type,
    'default_boot_interface': baremetal_driver_default_boot_if,
    'default_console_interface': baremetal_driver_default_console_if,
    'default_deploy_interface': baremetal_driver_default_deploy_if,
    'default_inspect_interface': baremetal_driver_default_inspect_if,
    'default_management_interface': baremetal_driver_default_management_if,
    'default_network_interface': baremetal_driver_default_network_if,
    'default_power_interface': baremetal_driver_default_power_if,
    'default_raid_interface': baremetal_driver_default_raid_if,
    'default_storage_interface': baremetal_driver_default_storage_if,
    'default_vendor_interface': baremetal_driver_default_vendor_if,
    'enabled_boot_interfaces': baremetal_driver_enabled_boot_ifs,
    'enabled_console_interfaces': baremetal_driver_enabled_console_ifs,
    'enabled_deploy_interfaces': baremetal_driver_enabled_deploy_ifs,
    'enabled_inspect_interfaces': baremetal_driver_enabled_inspect_ifs,
    'enabled_management_interfaces': baremetal_driver_enabled_management_ifs,
    'enabled_network_interfaces': baremetal_driver_enabled_network_ifs,
    'enabled_power_interfaces': baremetal_driver_enabled_power_ifs,
    'enabled_raid_interfaces': baremetal_driver_enabled_raid_ifs,
    'enabled_storage_interfaces': baremetal_driver_enabled_storage_ifs,
    'enabled_vendor_interfaces': baremetal_driver_enabled_vendor_ifs,
}

baremetal_driver_passthru_method = 'lookup'

BAREMETAL_DRIVER_PASSTHRU = {"lookup": {"attach": "false",
                                        "http_methods": ["POST"],
                                        "description": "",
                                        "async": "false"}}

baremetal_portgroup_uuid = 'ppp-gggggg-pppp'
baremetal_portgroup_name = 'Portgroup-name'
baremetal_portgroup_address = 'AA:BB:CC:CC:BB:AA'
baremetal_portgroup_mode = 'active-backup'
baremetal_portgroup_extra = {'key1': 'value1',
                             'key2': 'value2'}
baremetal_portgroup_properties = {'key1': 'value11',
                                  'key2': 'value22'}

PORTGROUP = {'uuid': baremetal_portgroup_uuid,
             'name': baremetal_portgroup_name,
             'node_uuid': baremetal_uuid,
             'address': baremetal_portgroup_address,
             'extra': baremetal_portgroup_extra,
             'mode': baremetal_portgroup_mode,
             'properties': baremetal_portgroup_properties,
             }

VIFS = {'vifs': [{'id': 'aaa-aa'}]}

baremetal_volume_connector_uuid = 'vvv-cccccc-vvvv'
baremetal_volume_connector_type = 'iqn'
baremetal_volume_connector_connector_id = 'iqn.2017-01.connector'
baremetal_volume_connector_extra = {'key1': 'value1',
                                    'key2': 'value2'}
VOLUME_CONNECTOR = {
    'uuid': baremetal_volume_connector_uuid,
    'node_uuid': baremetal_uuid,
    'type': baremetal_volume_connector_type,
    'connector_id': baremetal_volume_connector_connector_id,
    'extra': baremetal_volume_connector_extra,
}

baremetal_volume_target_uuid = 'vvv-tttttt-vvvv'
baremetal_volume_target_volume_type = 'iscsi'
baremetal_volume_target_boot_index = 0
baremetal_volume_target_volume_id = 'vvv-tttttt-iii'
baremetal_volume_target_extra = {'key1': 'value1',
                                 'key2': 'value2'}
baremetal_volume_target_properties = {'key11': 'value11',
                                      'key22': 'value22'}
VOLUME_TARGET = {
    'uuid': baremetal_volume_target_uuid,
    'node_uuid': baremetal_uuid,
    'volume_type': baremetal_volume_target_volume_type,
    'boot_index': baremetal_volume_target_boot_index,
    'volume_id': baremetal_volume_target_volume_id,
    'extra': baremetal_volume_target_extra,
    'properties': baremetal_volume_target_properties,
}


class TestBaremetal(utils.TestCommand):

    def setUp(self):
        super(TestBaremetal, self).setUp()

        self.app.client_manager.auth_ref = mock.Mock(auth_token="TOKEN")
        self.app.client_manager.baremetal = mock.Mock()


class FakeBaremetalResource(fakes.FakeResource):

    def get_keys(self):
        return {'property': 'value'}
