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


def _print_port_show(port):
    fields = ['address', 'created_at', 'extra', 'node_uuid', 'updated_at',
              'uuid']
    data = dict([(f, getattr(port, f, '')) for f in fields])
    cliutils.print_dict(data, wrap=72)


@cliutils.arg('port', metavar='<port id>', help="UUID of port")
@cliutils.arg(
    '--address',
    dest='address',
    action='store_true',
    default=False,
    help='Get the port by it\'s MAC address instead of UUID.')
def do_port_show(cc, args):
    """Show a port."""
    if args.address:
        port = cc.port.get_by_address(args.port)
    else:
        port = cc.port.get(args.port)
    _print_port_show(port)


@cliutils.arg(
    '--limit',
    metavar='<limit>',
    type=int,
    help='Maximum number of ports to return per request, '
         '0 for no limit. Default is the maximum number used '
         'by the Ironic API Service.')
@cliutils.arg(
    '--marker',
    metavar='<marker>',
    help='Port UUID (e.g of the last port in the list from '
         'a previous request). Returns the list of ports '
         'after this UUID.')
def do_port_list(cc, args):
    """List ports."""
    params = {}
    if args.marker is not None:
        params['marker'] = args.marker
    if args.limit is not None:
        params['limit'] = args.limit

    port = cc.port.list(**params)
    field_labels = ['UUID', 'Address']
    fields = ['uuid', 'address']
    cliutils.print_list(port, fields, field_labels, sortby_index=None)


@cliutils.arg(
    '-a', '--address',
    metavar='<address>',
    required=True,
    help='MAC Address for this port')
@cliutils.arg(
    '-n', '--node_uuid',
    metavar='<node uuid>',
    required=True,
    help='UUID of the node that this port belongs to')
@cliutils.arg(
    '-e', '--extra',
    metavar="<key=value>",
    action='append',
    help="Record arbitrary key/value metadata. "
         "Can be specified multiple times")
def do_port_create(cc, args):
    """Create a new port."""
    field_list = ['address', 'extra', 'node_uuid']
    fields = dict((k, v) for (k, v) in vars(args).items()
                  if k in field_list and not (v is None))
    fields = utils.args_array_to_dict(fields, 'extra')
    port = cc.port.create(**fields)

    field_list.append('uuid')
    data = dict([(f, getattr(port, f, '')) for f in field_list])
    cliutils.print_dict(data, wrap=72)


@cliutils.arg('port', metavar='<port id>', nargs='+', help="UUID of port")
def do_port_delete(cc, args):
    """Delete a port."""
    for p in args.port:
        cc.port.delete(p)
        print ('Deleted port %s' % p)


@cliutils.arg('port', metavar='<port id>', help="UUID of port")
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
def do_port_update(cc, args):
    """Update a port."""
    patch = utils.args_array_to_patch(args.op, args.attributes[0])
    port = cc.port.update(args.port, patch)
    _print_port_show(port)
