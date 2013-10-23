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
from ironicclient import exc


def _print_node_show(node):
    fields = ['uuid', 'instance_uuid', 'power_state', 'target_power_state',
              'provision_state', 'target_provision_state', 'driver',
              'driver_info', 'properties', 'extra',
              'created_at', 'updated_at', 'reservation']
    data = dict([(f, getattr(node, f, '')) for f in fields])
    utils.print_dict(data, wrap=72)


@utils.arg('node', metavar='<node id>', help="ID of node")
def do_node_show(cc, args):
    """Show a node."""
    try:
        node = cc.node.get(args.node)
    except exc.HTTPNotFound:
        raise exc.CommandError('Node not found: %s' % args.node)
    else:
        _print_node_show(node)


def do_node_list(cc, args):
    """List nodes."""
    nodes = cc.node.list()
    field_labels = ['UUID', 'Instance UUID',
                    'Power State', 'Provisioning State']
    fields = ['uuid', 'instance_uuid', 'power_state', 'provision_state']
    utils.print_list(nodes, fields, field_labels, sortby=1)


@utils.arg('-c', '--chassis_id',
           metavar='<chassis id>',
           help='ID of the chassis that this node belongs to [REQUIRED]')
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
           help="ID of node")
def do_node_delete(cc, args):
    """Delete a node."""
    for n in args.node:
        try:
            cc.node.delete(n)
        except exc.HTTPNotFound:
            raise exc.CommandError('Node not found: %s' % n)
        print 'Deleted node %s' % n


@utils.arg('node',
           metavar='<node id>',
           help="ID of node")
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
    try:
        node = cc.node.update(args.node, patch)
    except exc.HTTPNotFound:
        raise exc.CommandError('Node not found: %s' % args.node)
    _print_node_show(node)


@utils.arg('node', metavar='<node id>', help="ID of node")
def do_node_port_list(cc, args):
    """List the ports contained in the node."""
    try:
        ports = cc.node.list_ports(args.node)
    except exc.HTTPNotFound:
        raise exc.CommandError(_('Node not found: %s') % args.node)
    field_labels = ['UUID', 'Address']
    fields = ['uuid', 'address']
    utils.print_list(ports, fields, field_labels, sortby=1)


@utils.arg('node',
           metavar='<node id>',
           help="ID of node")
@utils.arg('power_state',
           metavar='<power state>',
           choices=['on', 'off'],
           help="Supported states: 'on' or 'off'")
def do_node_set_power_state(cc, args):
    """Power the node on or off."""
    try:
        state = cc.node.set_power_state(args.node, args.power_state)
    except exc.HTTPNotFound:
        raise exc.CommandError(_('Node not found: %s') % args.node)

    field_list = ['current', 'target']
    data = dict([(f, getattr(state, f, '')) for f in field_list])
    utils.print_dict(data, wrap=72)
