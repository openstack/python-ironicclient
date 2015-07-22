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
        'chassis_uuid': 'Chassis UUID',
        'clean_step': 'Clean Step',
        'console_enabled': 'Console Enabled',
        'created_at': 'Created At',
        'description': 'Description',
        'driver': 'Driver',
        'driver_info': 'Driver Info',
        'driver_internal_info': 'Driver Internal Info',
        'extra': 'Extra',
        'inspection_finished_at': 'Inspection Finished At',
        'inspection_started_at': 'Inspection Started At',
        'instance_info': 'Instance Info',
        'instance_uuid': 'Instance UUID',
        'last_error': 'Last Error',
        'maintenance': 'Maintenance',
        'maintenance_reason': 'Maintenance Reason',
        'name': 'Name',
        'node_uuid': 'Node UUID',
        'power_state': 'Power State',
        'properties': 'Properties',
        'provision_state': 'Provisioning State',
        'provision_updated_at': 'Provision Updated At',
        'reservation': 'Reservation',
        'target_power_state': 'Target Power State',
        'target_provision_state': 'Target Provision State',
        'updated_at': 'Updated At',
        'uuid': 'UUID',
    }

    def __init__(self, field_ids, sort_excluded=None):
        """Create a Resource object

        :param field_ids:  A list of strings that the Resource object will
                           contain.  Each string must match an existing key in
                           FIELDS.
        :param sort_excluded: Optional. A list of strings that will not be used
                              for sorting.  Must be a subset of 'field_ids'.

        :raises: ValueError if sort_excluded contains value not in field_ids
        """
        self._fields = tuple(field_ids)
        self._labels = tuple([self.FIELDS[x] for x in field_ids])
        if sort_excluded is None:
            sort_excluded = []
        not_existing = set(sort_excluded) - set(field_ids)
        if not_existing:
            raise ValueError(
                _("sort_excluded specified with value not contained in "
                  "field_ids.  Unknown value(s): %s") % ','.join(not_existing))
        self._sort_fields = tuple(
            [x for x in field_ids if x not in sort_excluded])
        self._sort_labels = tuple([self.FIELDS[x] for x in self._sort_fields])

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
NODE_DETAILED_RESOURCE = Resource(
    ['chassis_uuid',
     'created_at',
     'clean_step',
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
     'uuid',
     'name',
     ],
    sort_excluded=[
        # The server cannot sort on "chassis_uuid" because it isn't a column in
        # the "nodes" database table. "chassis_id" is stored, but it is
        # internal to ironic. See bug #1443003 for more details.
        'chassis_uuid',
        'clean_step',
        'driver_info',
        'driver_internal_info',
        'extra',
        'instance_info',
        'properties',
    ])
NODE_RESOURCE = Resource(
    ['uuid',
     'name',
     'instance_uuid',
     'power_state',
     'provision_state',
     'maintenance',
     ])

# Ports
PORT_DETAILED_RESOURCE = Resource(
    ['uuid',
     'address',
     'created_at',
     'extra',
     'node_uuid',
     'updated_at',
     ],
    sort_excluded=[
        'extra',
        # The server cannot sort on "node_uuid" because it isn't a column in
        # the "ports" database table. "node_id" is stored, but it is internal
        # to ironic. See bug #1443003 for more details.
        'node_uuid',
    ])
PORT_RESOURCE = Resource(
    ['uuid',
     'address',
     ])
