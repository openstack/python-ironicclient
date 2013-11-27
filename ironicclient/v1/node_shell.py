#!/usr/bin/env python
# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Red Hat, Inc.
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

from ironicclient.common import utils


def _print_node_show(node):
    fields = ['chassis_id', 'created_at', 'driver', 'driver_info', 'extra',
              'instance_uuid', 'last_error', 'power_state', 'properties',
              'provision_state', 'reservation', 'target_power_state',
              'target_provision_state', 'updated_at', 'uuid']
    data = dict([(f, getattr(node, f, '')) for f in fields])
    utils.print_dict(data, wrap=72)


@utils.arg('node', metavar='<id>',
           help="ID, UUID or instance UUID of node")
@utils.arg('--instance',
           dest='instance_uuid',
           action='store_true',
           default=False,
           help='The id is an instance UUID')
def do_node_show(cc, args):
    """Show a node."""
    if args.instance_uuid:
        node = cc.node.get_by_instance_uuid(args.node)
    else:
        node = cc.node.get(args.node)
    _print_node_show(node)


@utils.arg('--associated',
           metavar='<assoc>',
           choices=['true', 'True', 'false', 'False'],
           help="List nodes by instance association: 'true' or 'false'")
def do_node_list(cc, args):
    """List nodes."""
    if args.associated is None:
        nodes = cc.node.list()
    else:
        associated = args.associated.lower() == 'true'
        nodes = cc.node.list(associated)

    field_labels = ['UUID', 'Instance UUID',
                    'Power State', 'Provisioning State']
    fields = ['uuid', 'instance_uuid', 'power_state', 'provision_state']
    utils.print_list(nodes, fields, field_labels, sortby=1)


@utils.arg('-c', '--chassis_id',
           metavar='<chassis id>',
           help='UUID of the chassis that this node belongs to [REQUIRED]')
@utils.arg('-d', '--driver',
           metavar='<driver>',
           help='Driver used to control the node [REQUIRED]')
@utils.arg('-i', '--driver_info',
           metavar='<key=value>',
           action='append',
           help='Key/value pairs used by the driver. '
                'Can be specified multiple times')
@utils.arg('-p', '--properties',
           metavar='<key=value>',
           action='append',
           help='Key/value pairs describing the physical characteristics '
                'of the node. This is exported to Nova and used by the '
                'scheduler. Can be specified multiple times')
@utils.arg('-e', '--extra',
           metavar='<key=value>',
           action='append',
           help="Record arbitrary key/value metadata. "
                "Can be specified multiple times")
def do_node_create(cc, args):
    """Create a new node."""
    field_list = ['chassis_id', 'driver', 'driver_info', 'properties', 'extra']
    fields = dict((k, v) for (k, v) in vars(args).items()
                  if k in field_list and not (v is None))
    fields = utils.args_array_to_dict(fields, 'driver_info')
    fields = utils.args_array_to_dict(fields, 'extra')
    fields = utils.args_array_to_dict(fields, 'properties')
    node = cc.node.create(**fields)

    field_list.append('uuid')
    data = dict([(f, getattr(node, f, '')) for f in field_list])
    utils.print_dict(data, wrap=72)


@utils.arg('node',
           metavar='<node id>',
           nargs='+',
           help="UUID of node")
def do_node_delete(cc, args):
    """Delete a node."""
    for n in args.node:
        cc.node.delete(n)
        print(_('Deleted node %s') % n)


@utils.arg('node',
           metavar='<node id>',
           help="UUID of node")
@utils.arg('op',
           metavar='<op>',
           choices=['add', 'replace', 'remove'],
           help="Operations: 'add', 'replace' or 'remove'")
@utils.arg('attributes',
           metavar='<path=value>',
           nargs='+',
           action='append',
           default=[],
           help="Attributes to add/replace or remove "
                "(only PATH is necessary on remove)")
def do_node_update(cc, args):
    """Update a node."""
    patch = utils.args_array_to_patch(args.op, args.attributes[0])
    node = cc.node.update(args.node, patch)
    _print_node_show(node)


@utils.arg('node', metavar='<node id>', help="UUID of node")
def do_node_port_list(cc, args):
    """List the ports contained in the node."""
    ports = cc.node.list_ports(args.node)
    field_labels = ['UUID', 'Address']
    fields = ['uuid', 'address']
    utils.print_list(ports, fields, field_labels, sortby=1)


@utils.arg('node',
           metavar='<node id>',
           help="UUID of node")
@utils.arg('power_state',
           metavar='<power state>',
           choices=['on', 'off'],
           help="Supported states: 'on' or 'off'")
def do_node_set_power_state(cc, args):
    """Power the node on or off."""
    state = cc.node.set_power_state(args.node, args.power_state)
    field_list = ['current', 'target']
    data = dict([(f, getattr(state, f, '')) for f in field_list])
    utils.print_dict(data, wrap=72)


@utils.arg('node',
           metavar='<node uuid>',
           help="UUID of node")
def do_node_validate(cc, args):
    """Validate the node driver interfaces."""
    ifaces = cc.node.validate(args.node)
    field_list = ['power', 'deploy', 'console', 'rescue']
    data = dict([(f, getattr(ifaces, f, '')) for f in field_list])
    utils.print_dict(data, wrap=72)
