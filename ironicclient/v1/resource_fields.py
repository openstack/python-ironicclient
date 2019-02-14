# Copyright 2014 Red Hat, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from ironicclient.common.i18n import _


class Resource(object):
    """Resource class

    This class is used to manage the various fields that a resource (e.g.
    Chassis, Node, Port) contains.  An individual field consists of a
    'field_id' (key) and a 'label' (value).  The caller only provides the
    'field_ids' when instantiating the object.

    Ordering of the 'field_ids' will be preserved as specified by the caller.

    It also provides the ability to exclude some of these fields when they are
    being used for sorting.
    """

    FIELDS = {
        'address': 'Address',
        'alive': 'Alive',
        'allocation_uuid': 'Allocation UUID',
        'async': 'Async',
        'automated_clean': 'Automated Clean',
        'attach': 'Response is attachment',
        'bios_name': 'BIOS setting name',
        'bios_value': 'BIOS setting value',
        'boot_index': 'Boot Index',
        'candidate_nodes': 'Candidate Nodes',
        'chassis_uuid': 'Chassis UUID',
        'clean_step': 'Clean Step',
        'conductor': 'Conductor',
        'conductor_group': 'Conductor Group',
        'console_enabled': 'Console Enabled',
        'created_at': 'Created At',
        'default_bios_interface': 'Default BIOS Interface',
        'default_boot_interface': 'Default Boot Interface',
        'default_console_interface': 'Default Console Interface',
        'default_deploy_interface': 'Default Deploy Interface',
        'default_inspect_interface': 'Default Inspect Interface',
        'default_management_interface': 'Default Management Interface',
        'default_network_interface': 'Default Network Interface',
        'default_power_interface': 'Default Power Interface',
        'default_raid_interface': 'Default RAID Interface',
        'default_rescue_interface': 'Default Rescue Interface',
        'default_storage_interface': 'Default Storage Interface',
        'default_vendor_interface': 'Default Vendor Interface',
        'deploy_step': 'Deploy Step',
        'description': 'Description',
        'driver': 'Driver',
        'driver_info': 'Driver Info',
        'driver_internal_info': 'Driver Internal Info',
        'drivers': 'Drivers',
        'enabled_bios_interfaces': 'Enabled BIOS Interfaces',
        'enabled_boot_interfaces': 'Enabled Boot Interfaces',
        'enabled_console_interfaces': 'Enabled Console Interfaces',
        'enabled_deploy_interfaces': 'Enabled Deploy Interfaces',
        'enabled_inspect_interfaces': 'Enabled Inspect Interfaces',
        'enabled_management_interfaces': 'Enabled Management Interfaces',
        'enabled_network_interfaces': 'Enabled Network Interfaces',
        'enabled_power_interfaces': 'Enabled Power Interfaces',
        'enabled_raid_interfaces': 'Enabled RAID Interfaces',
        'enabled_rescue_interfaces': 'Enabled Rescue Interfaces',
        'enabled_storage_interfaces': 'Enabled Storage Interfaces',
        'enabled_vendor_interfaces': 'Enabled Vendor Interfaces',
        'extra': 'Extra',
        'hostname': 'Hostname',
        'hosts': 'Active host(s)',
        'http_methods': 'Supported HTTP methods',
        'inspection_finished_at': 'Inspection Finished At',
        'inspection_started_at': 'Inspection Started At',
        'instance_info': 'Instance Info',
        'instance_uuid': 'Instance UUID',
        'internal_info': 'Internal Info',
        'last_error': 'Last Error',
        'maintenance': 'Maintenance',
        'maintenance_reason': 'Maintenance Reason',
        'fault': 'Fault',
        'mode': 'Mode',
        'name': 'Name',
        'node_uuid': 'Node UUID',
        'owner': 'Owner',
        'power_state': 'Power State',
        'properties': 'Properties',
        'protected': 'Protected',
        'protected_reason': 'Protected Reason',
        'provision_state': 'Provisioning State',
        'provision_updated_at': 'Provision Updated At',
        'raid_config': 'Current RAID configuration',
        'reservation': 'Reservation',
        'resource_class': 'Resource Class',
        'state': 'State',
        'steps': 'Steps',
        'target_power_state': 'Target Power State',
        'target_provision_state': 'Target Provision State',
        'target_raid_config': 'Target RAID configuration',
        'traits': 'Traits',
        'type': 'Type',
        'updated_at': 'Updated At',
        'uuid': 'UUID',
        'volume_id': 'Volume ID',
        'volume_type': 'Driver Volume Type',
        'local_link_connection': 'Local Link Connection',
        'pxe_enabled': 'PXE boot enabled',
        'portgroup_uuid': 'Portgroup UUID',
        'bios_interface': 'BIOS Interface',
        'boot_interface': 'Boot Interface',
        'console_interface': 'Console Interface',
        'deploy_interface': 'Deploy Interface',
        'inspect_interface': 'Inspect Interface',
        'management_interface': 'Management Interface',
        'network_interface': 'Network Interface',
        'power_interface': 'Power Interface',
        'raid_interface': 'RAID Interface',
        'rescue_interface': 'Rescue Interface',
        'storage_interface': 'Storage Interface',
        'vendor_interface': 'Vendor Interface',
        'standalone_ports_supported': 'Standalone Ports Supported',
        'physical_network': 'Physical Network',
        'id': 'ID',
        'connector_id': 'Connector ID',
        'is_smartnic': 'Is Smart NIC port',
    }

    def __init__(self, field_ids, sort_excluded=None, override_labels=None):
        """Create a Resource object

        :param field_ids:  A list of strings that the Resource object will
                           contain.  Each string must match an existing key in
                           FIELDS.
        :param sort_excluded: Optional. A list of strings that will not be used
                              for sorting.  Must be a subset of 'field_ids'.
        :param override_labels: Optional. A dictionary, where key is a field ID
                                and value is the label to be used. If
                                unspecified, uses the labels associated with
                                the fields from global FIELDS.

        :raises: ValueError if sort_excluded or override_labels contains values
                 not in field_ids
        """
        def check_param_fields(param_name, param_fields):
            not_existing = set(param_fields) - set(field_ids)
            if not_existing:
                raise ValueError(
                    _("%(param)s specified with value not contained in "
                      "field_ids.  Unknown value(s): %(unknown)s")
                    % {'param': param_name,
                       'unknown': ', '.join(not_existing)})

        if override_labels is None:
            override_labels = {}
        else:
            check_param_fields('override_labels', override_labels.keys())

        self._fields = tuple(field_ids)
        self._labels = tuple([override_labels.get(x) or self.FIELDS[x]
                             for x in field_ids])

        if sort_excluded is None:
            sort_excluded = []
        else:
            check_param_fields('sort_excluded', sort_excluded)
        self._sort_fields = tuple(
            [x for x in field_ids if x not in sort_excluded])
        self._sort_labels = tuple([override_labels.get(x) or self.FIELDS[x]
                                  for x in self._sort_fields])

    @property
    def fields(self):
        return self._fields

    @property
    def labels(self):
        return self._labels

    @property
    def sort_fields(self):
        return self._sort_fields

    @property
    def sort_labels(self):
        return self._sort_labels


# Chassis
CHASSIS_DETAILED_RESOURCE = Resource(
    ['uuid',
     'description',
     'created_at',
     'updated_at',
     'extra',
     ],
    sort_excluded=['extra'])
CHASSIS_RESOURCE = Resource(
    ['uuid',
     'description',
     ])

# Nodes
# NOTE(dtantsur): the sorting of the list must follow the sorting for the
# corresponding headings, so some items (like raid_config) may seem out of
# order here.
NODE_DETAILED_RESOURCE = Resource(
    ['allocation_uuid',
     'automated_clean',
     'bios_interface',
     'boot_interface',
     'chassis_uuid',
     'clean_step',
     'conductor',
     'conductor_group',
     'console_enabled',
     'console_interface',
     'created_at',
     'raid_config',
     'deploy_interface',
     'deploy_step',
     'description',
     'driver',
     'driver_info',
     'driver_internal_info',
     'extra',
     'fault',
     'inspect_interface',
     'inspection_finished_at',
     'inspection_started_at',
     'instance_info',
     'instance_uuid',
     'last_error',
     'maintenance',
     'maintenance_reason',
     'management_interface',
     'name',
     'network_interface',
     'owner',
     'power_interface',
     'power_state',
     'properties',
     'protected',
     'protected_reason',
     'provision_updated_at',
     'provision_state',
     'raid_interface',
     'rescue_interface',
     'reservation',
     'resource_class',
     'storage_interface',
     'target_power_state',
     'target_provision_state',
     'target_raid_config',
     'traits',
     'uuid',
     'updated_at',
     'vendor_interface',
     ],
    sort_excluded=[
        'allocation_uuid',
        # The server cannot sort on "chassis_uuid" because it isn't a column in
        # the "nodes" database table. "chassis_id" is stored, but it is
        # internal to ironic. See bug #1443003 for more details.
        'chassis_uuid',
        'clean_step',
        'deploy_step',
        'driver_info',
        'driver_internal_info',
        'extra',
        'instance_info',
        'properties',
        'raid_config',
        'target_raid_config',
        'traits',
    ])
NODE_RESOURCE = Resource(
    ['uuid',
     'name',
     'instance_uuid',
     'power_state',
     'provision_state',
     'maintenance',
     ])
VENDOR_PASSTHRU_METHOD_RESOURCE = Resource(
    ['name',
     'http_methods',
     'async',
     'description',
     'attach'
     ])

# Ports
PORT_DETAILED_RESOURCE = Resource(
    ['uuid',
     'address',
     'created_at',
     'extra',
     'node_uuid',
     'local_link_connection',
     'portgroup_uuid',
     'pxe_enabled',
     'physical_network',
     'updated_at',
     'internal_info',
     'is_smartnic',
     ],
    sort_excluded=[
        'extra',
        # The server cannot sort on "node_uuid" or "portgroup_uuid" because
        # they aren't columns in the "ports" database table. "node_id" and
        # "portgroup_id" are stored, but it is internal to ironic.
        # See bug #1443003 for more details.
        'node_uuid',
        'portgroup_uuid',
        'internal_info',
    ])
PORT_RESOURCE = Resource(
    ['uuid',
     'address',
     ])

# Portgroups
PORTGROUP_DETAILED_RESOURCE = Resource(
    ['uuid',
     'address',
     'created_at',
     'extra',
     'standalone_ports_supported',
     'node_uuid',
     'name',
     'updated_at',
     'internal_info',
     'mode',
     'properties',
     ],
    sort_excluded=[
        'extra',
        # The server cannot sort on "node_uuid" because it isn't a column in
        # the "portgroups" database table. "node_id" is stored, but it is
        # internal to ironic. See bug #1443003 for more details.
        'node_uuid',
        'internal_info',
        'properties',
    ])
PORTGROUP_RESOURCE = Resource(
    ['uuid',
     'address',
     'name',
     ])

# VIFs
VIF_RESOURCE = Resource(
    ['id'],
)

TRAIT_RESOURCE = Resource(
    ['traits'],
)

BIOS_RESOURCE = Resource(
    ['bios_name', 'bios_value'],
)

# Drivers
DRIVER_DETAILED_RESOURCE = Resource(
    ['name',
     'type',
     'hosts',
     'default_bios_interface',
     'default_boot_interface',
     'default_console_interface',
     'default_deploy_interface',
     'default_inspect_interface',
     'default_management_interface',
     'default_network_interface',
     'default_power_interface',
     'default_raid_interface',
     'default_rescue_interface',
     'default_storage_interface',
     'default_vendor_interface',
     'enabled_bios_interfaces',
     'enabled_boot_interfaces',
     'enabled_console_interfaces',
     'enabled_deploy_interfaces',
     'enabled_inspect_interfaces',
     'enabled_management_interfaces',
     'enabled_network_interfaces',
     'enabled_power_interfaces',
     'enabled_raid_interfaces',
     'enabled_rescue_interfaces',
     'enabled_storage_interfaces',
     'enabled_vendor_interfaces'
     ],
    override_labels={'name': 'Supported driver(s)'}
)
DRIVER_RESOURCE = Resource(
    ['name',
     'hosts',
     ],
    override_labels={'name': 'Supported driver(s)'}
)

# Volume connectors
VOLUME_CONNECTOR_DETAILED_RESOURCE = Resource(
    ['uuid',
     'node_uuid',
     'type',
     'connector_id',
     'extra',
     'created_at',
     'updated_at',
     ],
    sort_excluded=[
        # The server cannot sort on "node_uuid" because it isn't a column in
        # the "volume_connectors" database table. "node_id" is stored, but it
        # is internal to ironic. See bug #1443003 for more details.
        'node_uuid',
        'extra',
    ])
VOLUME_CONNECTOR_RESOURCE = Resource(
    ['uuid',
     'node_uuid',
     'type',
     'connector_id',
     ],
    sort_excluded=['node_uuid']
)

# Volume targets
VOLUME_TARGET_DETAILED_RESOURCE = Resource(
    ['uuid',
     'node_uuid',
     'volume_type',
     'properties',
     'boot_index',
     'extra',
     'volume_id',
     'created_at',
     'updated_at',
     ],
    sort_excluded=[
        # The server cannot sort on "node_uuid" because it isn't a column in
        # the "volume_targets" database table. "node_id" is stored, but it
        # is internal to ironic. See bug #1443003 for more details.
        'node_uuid',
        'extra',
        'properties'
    ])
VOLUME_TARGET_RESOURCE = Resource(
    ['uuid',
     'node_uuid',
     'volume_type',
     'boot_index',
     'volume_id',
     ],
    sort_excluded=['node_uuid']
)

# Conductors
CONDUCTOR_DETAILED_RESOURCE = Resource(
    ['hostname',
     'conductor_group',
     'alive',
     'drivers',
     'created_at',
     'updated_at',
     ],
    sort_excluded=[
        'alive',
        'drivers',
    ])
CONDUCTOR_RESOURCE = Resource(
    ['hostname',
     'conductor_group',
     'alive',
     ],
    sort_excluded=['alive']
)

# Allocations
ALLOCATION_DETAILED_RESOURCE = Resource(
    ['uuid',
     'name',
     'state',
     'node_uuid',
     'last_error',
     'resource_class',
     'traits',
     'candidate_nodes',
     'extra',
     'created_at',
     'updated_at',
     ],
    sort_excluded=[
        'candidate_nodes',
        'traits',
    ])
ALLOCATION_RESOURCE = Resource(
    ['uuid',
     'name',
     'resource_class',
     'state',
     'node_uuid',
     ],
)

# Deploy templates
DEPLOY_TEMPLATE_DETAILED_RESOURCE = Resource(
    ['uuid',
     'name',
     'steps',
     'extra',
     'created_at',
     'updated_at',
     ],
    sort_excluded=['extra', 'steps']
)

DEPLOY_TEMPLATE_RESOURCE = Resource(
    ['uuid',
     'name',
     ],
)
