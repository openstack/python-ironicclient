# -*- coding: utf-8 -*-
#
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
from ironicclient.openstack.common import cliutils


def _print_chassis_show(chassis):
    fields = ['uuid', 'description', 'created_at', 'updated_at', 'extra']
    data = dict([(f, getattr(chassis, f, '')) for f in fields])
    cliutils.print_dict(data, wrap=72)


@cliutils.arg('chassis', metavar='<chassis id>', help="UUID of chassis")
def do_chassis_show(cc, args):
    """Show a chassis."""
    chassis = cc.chassis.get(args.chassis)
    _print_chassis_show(chassis)


@cliutils.arg(
    '--limit',
    metavar='<limit>',
    type=int,
    help='Maximum number of chassis to return per request, '
         '0 for no limit. Default is the maximum number used '
         'by the Ironic API Service.')
@cliutils.arg(
    '--marker',
    metavar='<marker>',
    help='Chassis UUID (e.g of the last chassis in the list '
         'from a previous request). Returns the list of chassis '
         'after this UUID.')
def do_chassis_list(cc, args):
    """List chassis."""
    params = {}
    if args.marker is not None:
        params['marker'] = args.marker
    if args.limit is not None:
        params['limit'] = args.limit

    chassis = cc.chassis.list(**params)
    field_labels = ['UUID', 'Description']
    fields = ['uuid', 'description']
    cliutils.print_list(chassis, fields, field_labels, sortby_index=None)


@cliutils.arg(
    '-d', '--description',
    metavar='<description>',
    help='Free text description of the chassis')
@cliutils.arg(
    '-e', '--extra',
    metavar="<key=value>",
    action='append',
    help="Record arbitrary key/value metadata. "
         "Can be specified multiple times")
def do_chassis_create(cc, args):
    """Create a new chassis."""
    field_list = ['description', 'extra']
    fields = dict((k, v) for (k, v) in vars(args).items()
                  if k in field_list and not (v is None))
    fields = utils.args_array_to_dict(fields, 'extra')
    chassis = cc.chassis.create(**fields)

    field_list.append('uuid')
    data = dict([(f, getattr(chassis, f, '')) for f in field_list])
    cliutils.print_dict(data, wrap=72)


@cliutils.arg(
    'chassis',
    metavar='<chassis id>',
    nargs='+',
    help="UUID of chassis")
def do_chassis_delete(cc, args):
    """Delete a chassis."""
    for c in args.chassis:
        cc.chassis.delete(c)
        print('Deleted chassis %s' % c)


@cliutils.arg('chassis', metavar='<chassis id>', help="UUID of chassis")
@cliutils.arg(
    'op',
    metavar='<op>',
    choices=['add', 'replace', 'remove'],
    help="Operations: 'add', 'replace' or 'remove'")
@cliutils.arg(
    'attributes',
    metavar='<path=value>',
    nargs='+',
    action='append',
    default=[],
    help="Attributes to add/replace or remove "
         "(only PATH is necessary on remove)")
def do_chassis_update(cc, args):
    """Update a chassis."""
    patch = utils.args_array_to_patch(args.op, args.attributes[0])
    chassis = cc.chassis.update(args.chassis, patch)
    _print_chassis_show(chassis)


@cliutils.arg(
    '--limit',
    metavar='<limit>',
    type=int,
    help='Maximum number of nodes to return per request, '
         '0 for no limit. Default is the maximum number used '
         'by the Ironic API Service.')
@cliutils.arg(
    '--marker',
    metavar='<marker>',
    help='Node UUID (e.g of the last node in the list from '
         'a previous request). Returns the list of nodes '
         'after this UUID.')
@cliutils.arg('chassis', metavar='<chassis id>', help="UUID of chassis")
def do_chassis_node_list(cc, args):
    """List the nodes contained in the chassis."""
    params = {}
    if args.marker is not None:
        params['marker'] = args.marker
    if args.limit is not None:
        params['limit'] = args.limit

    nodes = cc.chassis.list_nodes(args.chassis, **params)
    field_labels = ['UUID', 'Instance UUID',
                    'Power State', 'Provisioning State']
    fields = ['uuid', 'instance_uuid', 'power_state', 'provision_state']
    cliutils.print_list(nodes, fields, field_labels, sortby_index=None)
