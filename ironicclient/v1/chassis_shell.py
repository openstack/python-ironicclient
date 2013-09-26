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


@utils.arg('chassis', metavar='<chassis>', help="ID of chassis")
def do_chassis_show(cc, args):
    """Show a chassis."""
    try:
        chassis = cc.chassis.get(args.chassis)
    except exc.HTTPNotFound:
        raise exc.CommandError('Chassis not found: %s' % args.chassis)
    else:
        fields = ['uuid', 'description', 'extra']
        data = dict([(f, getattr(chassis, f, '')) for f in fields])
        utils.print_dict(data, wrap=72)


def do_chassis_list(cc, args):
    """List chassis."""
    chassis = cc.chassis.list()
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
def do_chassis_create(cc, args):
    """Create a new chassis."""
    field_list = ['description', 'extra']
    fields = dict((k, v) for (k, v) in vars(args).items()
                  if k in field_list and not (v is None))
    fields = utils.args_array_to_dict(fields, 'extra')
    chassis = cc.chassis.create(**fields)

    field_list.append('uuid')
    data = dict([(f, getattr(chassis, f, '')) for f in field_list])
    utils.print_dict(data, wrap=72)


@utils.arg('chassis', metavar='<chassis>', help="ID of chassis")
def do_chassis_delete(cc, args):
    """Delete a chassis."""
    try:
        cc.chassis.delete(args.chassis)
    except exc.HTTPNotFound:
        raise exc.CommandError('Chassis not found: %s' % args.chassis)


@utils.arg('node', metavar='<node>', help="ID of node")
def do_node_show(cc, args):
    """Show a node."""
    try:
        node = cc.node.get(args.node)
    except exc.HTTPNotFound:
        raise exc.CommandError('Node not found: %s' % args.node)
    else:
        fields = ['uuid', 'instance_uuid', 'power_state', 'target_power_state',
                  'provision_state', 'target_provision_state', 'driver',
                  'driver_info', 'properties', 'extra',
                  'created_at', 'updated_at', 'reservation']
        data = dict([(f, getattr(node, f, '')) for f in fields])
        utils.print_dict(data, wrap=72)
