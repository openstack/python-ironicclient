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

import json
from unittest import mock

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
baremetal_owner = 'fake-owner'
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
baremetal_driver_default_bios_if = 'bios'
baremetal_driver_default_boot_if = 'boot'
baremetal_driver_default_console_if = 'console'
baremetal_driver_default_deploy_if = 'deploy'
baremetal_driver_default_inspect_if = 'inspect'
baremetal_driver_default_firmware_if = 'firmware'
baremetal_driver_default_management_if = 'management'
baremetal_driver_default_network_if = 'network'
baremetal_driver_default_power_if = 'power'
baremetal_driver_default_raid_if = 'raid'
baremetal_driver_default_rescue_if = 'rescue'
baremetal_driver_default_storage_if = 'storage'
baremetal_driver_default_vendor_if = 'vendor'
baremetal_driver_enabled_bios_ifs = ['bios', 'bios2']
baremetal_driver_enabled_boot_ifs = ['boot', 'boot2']
baremetal_driver_enabled_console_ifs = ['console', 'console2']
baremetal_driver_enabled_deploy_ifs = ['deploy', 'deploy2']
baremetal_driver_enabled_firmware_ifs = ['firmware', 'firmware2']
baremetal_driver_enabled_inspect_ifs = ['inspect', 'inspect2']
baremetal_driver_enabled_management_ifs = ['management', 'management2']
baremetal_driver_enabled_network_ifs = ['network', 'network2']
baremetal_driver_enabled_power_ifs = ['power', 'power2']
baremetal_driver_enabled_raid_ifs = ['raid', 'raid2']
baremetal_driver_enabled_rescue_ifs = ['rescue', 'rescue2']
baremetal_driver_enabled_storage_ifs = ['storage', 'storage2']
baremetal_driver_enabled_vendor_ifs = ['vendor', 'vendor2']

BAREMETAL_DRIVER = {
    'hosts': baremetal_driver_hosts,
    'name': baremetal_driver_name,
    'type': baremetal_driver_type,
    'default_bios_interface': baremetal_driver_default_bios_if,
    'default_boot_interface': baremetal_driver_default_boot_if,
    'default_console_interface': baremetal_driver_default_console_if,
    'default_deploy_interface': baremetal_driver_default_deploy_if,
    'default_firmware_interface': baremetal_driver_default_firmware_if,
    'default_inspect_interface': baremetal_driver_default_inspect_if,
    'default_management_interface': baremetal_driver_default_management_if,
    'default_network_interface': baremetal_driver_default_network_if,
    'default_power_interface': baremetal_driver_default_power_if,
    'default_raid_interface': baremetal_driver_default_raid_if,
    'default_rescue_interface': baremetal_driver_default_rescue_if,
    'default_storage_interface': baremetal_driver_default_storage_if,
    'default_vendor_interface': baremetal_driver_default_vendor_if,
    'enabled_bios_interfaces': baremetal_driver_enabled_bios_ifs,
    'enabled_boot_interfaces': baremetal_driver_enabled_boot_ifs,
    'enabled_console_interfaces': baremetal_driver_enabled_console_ifs,
    'enabled_deploy_interfaces': baremetal_driver_enabled_deploy_ifs,
    'enabled_firmware_interfaces': baremetal_driver_enabled_firmware_ifs,
    'enabled_inspect_interfaces': baremetal_driver_enabled_inspect_ifs,
    'enabled_management_interfaces': baremetal_driver_enabled_management_ifs,
    'enabled_network_interfaces': baremetal_driver_enabled_network_ifs,
    'enabled_power_interfaces': baremetal_driver_enabled_power_ifs,
    'enabled_raid_interfaces': baremetal_driver_enabled_raid_ifs,
    'enabled_rescue_interfaces': baremetal_driver_enabled_rescue_ifs,
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
TRAITS = ['CUSTOM_FOO', 'CUSTOM_BAR']
CHILDREN = ['53da080f-6de7-4a3e-bcb6-b7889b380ad0',
            '48467e9b-3cd1-45b5-a57e-169e01370169']
BIOS_SETTINGS = [{'name': 'bios_name_1', 'value': 'bios_value_1', 'links': []},
                 {'name': 'bios_name_2', 'value': 'bios_value_2', 'links': []}]

BIOS_DETAILED_SETTINGS = [{'name': 'SysName', 'value': 'my-system',
                           'links': [], 'attribute_type': 'String',
                           'min_length': '1', 'max_length': '16'},
                          {'name': 'NumCores', 'value': '10',
                           'links': [], 'attribute_type': 'Integer',
                           'lower_bound': '10', 'upper_bound': '20'},
                          {'name': 'ProcVirtualization', 'value': 'Enabled',
                           'links': [], 'attribute_type': 'Enumeration',
                           'allowable_values': ['Enabled', 'Disabled']}]

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

baremetal_hostname = 'compute1.localdomain'
baremetal_conductor_group = 'foo'
baremetal_alive = True
baremetal_drivers = ['fake-hardware']
CONDUCTOR = {
    'hostname': baremetal_hostname,
    'conductor_group': baremetal_conductor_group,
    'alive': baremetal_alive,
    'drivers': baremetal_drivers,
}

baremetal_allocation_state = 'active'
baremetal_resource_class = 'baremetal'
ALLOCATION = {
    'resource_class': baremetal_resource_class,
    'uuid': baremetal_uuid,
    'name': baremetal_name,
    'state': baremetal_allocation_state,
    'node_uuid': baremetal_uuid,
}

baremetal_deploy_template_uuid = 'ddd-tttttt-dddd'
baremetal_deploy_template_name = 'DeployTemplate-name'
baremetal_deploy_template_steps = json.dumps([{
    'interface': 'raid',
    'step': 'create_configuration',
    'args': {},
    'priority': 10
}])
baremetal_deploy_template_extra = {'key1': 'value1', 'key2': 'value2'}
DEPLOY_TEMPLATE = {
    'uuid': baremetal_deploy_template_uuid,
    'name': baremetal_deploy_template_name,
    'steps': baremetal_deploy_template_steps,
    'extra': baremetal_deploy_template_extra,
}

baremetal_runbook_uuid = 'ddd-tttttt-dddd'
baremetal_runbook_name = 'CUSTOM_AWESOME'
baremetal_runbook_owner = 'some_user'
baremetal_runbook_public = False
baremetal_runbook_steps = json.dumps([{
    'interface': 'raid',
    'step': 'create_configuration',
    'args': {},
    'order': 1
}])
baremetal_runbook_extra = {'key1': 'value1', 'key2': 'value2'}
RUNBOOK = {
    'uuid': baremetal_runbook_uuid,
    'name': baremetal_runbook_name,
    'owner': baremetal_runbook_owner,
    'public': baremetal_runbook_public,
    'steps': baremetal_runbook_steps,
    'extra': baremetal_runbook_extra,
}

baremetal_shard_name = 'example_shard'
baremetal_shard_count = 47
SHARD = {
    'name': baremetal_shard_name,
    'count': baremetal_shard_count,
}

NODE_HISTORY = [
    {
        'uuid': 'abcdef1',
        'created_at': 'time',
        'severity': 'info',
        'event': 'meow',
        'event_type': 'purring',
        'conductor': 'lap-conductor',
        'user': '0191',
        'links': {'href': 'url', 'rel': 'self'},
    }
]
NODE_INVENTORY = [
    {
        'inventory':
        {
            'memory': {'physical_mb': 3072},
            'cpu': {'count': 1,
                    'model_name': 'qemu64',
                    'architecture': 'x86_64'},
            'disks': [{'name': 'testvm2.qcow2',
                       'size': 11811160064}],
            'interfaces': [{'mac_address': '52:54:00:11:2d:26'}],
            'system_vendor': {'product_name': 'testvm2',
                              'manufacturer': 'Sushy Emulator'},
            'boot': {'current_boot_mode': 'uefi'}
        }
    }
]

FIRMWARE_COMPONENTS = [
    {
        "component": "bios",
        "initial_version": "v1.0.0.0 (01.02.2022)",
        "current_version": "v1.2.3.4 (01.02.2023)",
        "last_version_flashed": "v1.2.3.4 (01.02.2023)",
        "created_at": "2023-02-01 09:00:00",
        "updated_at": "2023-03-01 10:00:00"
    },
    {
        "component": "bmc",
        "initial_version": "v1.0.0",
        "current_version": "v1.0.0",
        "last_version_flashed": "",
        "created_at": "2023-02-01 09:00:00",
        "updated_at": ""
    }
]


baremetal_inspection_rule_uuid = 'ddd-tttttt-dddd'
baremetal_inspection_rule_description = 'Blah'
baremetal_inspection_rule_priority = 0
baremetal_inspection_rule_sensitive = False
baremetal_inspection_rule_phase = 'main'
baremetal_inspection_rule_actions = json.dumps([{
    'op': 'set-attribute',
    'args': ["/driver", "idrac"],
}])
baremetal_inspection_rule_conditions = json.dumps([{
    'op': 'is-true',
    'args': ["{node.auto_discovered}"],
    'multiple': 'any',
}])

INSPECTION_RULE = {
    'uuid': baremetal_inspection_rule_uuid,
    'description': baremetal_inspection_rule_description,
    'priority': baremetal_inspection_rule_priority,
    'sensitive': baremetal_inspection_rule_sensitive,
    'phase': baremetal_inspection_rule_phase,
    'actions': baremetal_inspection_rule_actions,
    'conditions': baremetal_inspection_rule_conditions,
}


class TestBaremetal(utils.TestCommand):

    def setUp(self):
        super(TestBaremetal, self).setUp()

        self.app.client_manager.auth_ref = mock.Mock(auth_token="TOKEN")
        self.app.client_manager.baremetal = mock.Mock()


class FakeBaremetalResource(fakes.FakeResource):

    def get_keys(self):
        return {'property': 'value'}
