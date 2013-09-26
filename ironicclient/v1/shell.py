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

from ironicclient.common import utils
from ironicclient import exc


@utils.arg('chassis', metavar='<chassis>', help="ID of chassis")
def do_chassis_show(self, args):
    """Show a chassis."""
    try:
        chassis = self.chassis.get(args.chassis)
    except exc.HTTPNotFound:
        raise exc.CommandError('Chassis not found: %s' % args.chassis)
    else:
        fields = ['uuid', 'description', 'extra']
        data = dict([(f, getattr(chassis, f, '')) for f in fields])
        utils.print_dict(data, wrap=72)


def do_chassis_list(self, args):
    """List chassis."""
    chassis = self.chassis.list()
    field_labels = ['UUID', 'Description']
    fields = ['uuid', 'description']
    utils.print_list(chassis, fields, field_labels, sortby=1)


@utils.arg('--description',
           metavar='<DESCRIPTION>',
           help='Free text description of the chassis')
@utils.arg('--extra',
           metavar="<key=value>",
           action='append',
           help="Record arbitrary key/value metadata. "
                "Can be specified multiple times.")
def do_chassis_create(self, args):
    """Create a new chassis."""
    field_list = ['description', 'extra']
    fields = dict((k, v) for (k, v) in vars(args).items()
                  if k in field_list and not (v is None))
    fields = utils.args_array_to_dict(fields, 'extra')
    chassis = self.chassis.create(**fields)

    field_list.append('uuid')
    data = dict([(f, getattr(chassis, f, '')) for f in field_list])
    utils.print_dict(data, wrap=72)


@utils.arg('chassis', metavar='<chassis>', help="ID of chassis")
def do_chassis_delete(self, args):
    """Delete a chassis."""
    try:
        self.chassis.delete(args.chassis)
    except exc.HTTPNotFound:
        raise exc.CommandError('Chassis not found: %s' % args.chassis)


@utils.arg('node', metavar='<node>', help="ID of node")
def do_node_show(self, args):
    """Show a node."""
    try:
        node = self.node.get(args.node)
    except exc.HTTPNotFound:
        raise exc.CommandError('Node not found: %s' % args.node)
    else:
        fields = ['uuid', 'instance_uuid', 'power_state', 'target_power_state',
                  'provision_state', 'target_provision_state', 'driver',
                  'driver_info', 'properties', 'extra',
                  'created_at', 'updated_at', 'reservation']
        data = dict([(f, getattr(node, f, '')) for f in fields])
        utils.print_dict(data, wrap=72)


def do_node_list(self, args):
    """List nodes."""
    nodes = self.node.list()
    field_labels = ['UUID', 'Instance UUID',
                    'Power State', 'Provisioning State']
    fields = ['uuid', 'instance_uuid', 'power_state', 'provision_state']
    utils.print_list(nodes, fields, field_labels, sortby=1)


@utils.arg('--driver',
           metavar='<DRIVER>',
           help='Driver used to control the node. [REQUIRED]')
@utils.arg('--driver_info',
           metavar='<key=value>',
           help='Key/value pairs used by the driver. '
                'Can be specified multiple times.')
@utils.arg('--properties',
           metavar='<key=value>',
           help='Key/value pairs describing the physical characteristics '
                'of the node. This is exported to Nova and used by the '
                'scheduler. Can be specified multiple times.')
@utils.arg('--extra',
           metavar='<key=value>',
           help="Record arbitrary key/value metadata. "
                "Can be specified multiple times.")
def do_node_create(self, args):
    """Create a new node."""
    field_list = ['chassis_id', 'driver', 'driver_info', 'properties', 'extra']
    fields = dict((k, v) for (k, v) in vars(args).items()
                  if k in field_list and not (v is None))
    fields = utils.args_array_to_dict(fields, 'driver_info')
    fields = utils.args_array_to_dict(fields, 'extra')
    fields = utils.args_array_to_dict(fields, 'properties')
    node = self.node.create(**fields)

    field_list.append('uuid')
    data = dict([(f, getattr(node, f, '')) for f in field_list])
    utils.print_dict(data, wrap=72)


@utils.arg('node', metavar='<node>', help="ID of node")
def do_node_delete(self, args):
    """Delete a node."""
    try:
        self.node.delete(args.node)
    except exc.HTTPNotFound:
        raise exc.CommandError('Node not found: %s' % args.node)


@utils.arg('port', metavar='<port>', help="ID of port")
def do_port_show(self, args):
    """Show a port."""
    try:
        port = self.port.get(args.port)
    except exc.HTTPNotFound:
        raise exc.CommandError('Port not found: %s' % args.port)
    else:
        fields = ['uuid', 'address', 'extra']
        data = dict([(f, getattr(port, f, '')) for f in fields])
        utils.print_dict(data, wrap=72)


def do_port_list(self, args):
    """List ports."""
    port = self.port.list()
    field_labels = ['UUID', 'Address']
    fields = ['uuid', 'address']
    utils.print_list(port, fields, field_labels, sortby=1)


@utils.arg('--address',
           metavar='<ADDRESS>',
           help='MAC Address for this port.')
@utils.arg('--node_id',
           metavar='<NODE_ID>',
           help='ID of the node that this port belongs to.')
@utils.arg('--extra',
           metavar="<key=value>",
           action='append',
           help="Record arbitrary key/value metadata. "
                "Can be specified multiple times.")
def do_port_create(self, args):
    """Create a new port."""
    field_list = ['address', 'extra', 'node_id']
    fields = dict((k, v) for (k, v) in vars(args).items()
                  if k in field_list and not (v is None))
    fields = utils.args_array_to_dict(fields, 'extra')
    port = self.port.create(**fields)

    field_list.append('uuid')
    data = dict([(f, getattr(port, f, '')) for f in field_list])
    utils.print_dict(data, wrap=72)


@utils.arg('port', metavar='<port>', help="ID of port")
def do_port_delete(self, args):
    """Delete a port."""
    try:
        self.port.delete(args.port)
    except exc.HTTPNotFound:
        raise exc.CommandError('Port not found: %s' % args.port)
