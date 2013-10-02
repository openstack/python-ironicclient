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


def _print_port_show(port):
    fields = ['uuid', 'address', 'extra']
    data = dict([(f, getattr(port, f, '')) for f in fields])
    utils.print_dict(data, wrap=72)


@utils.arg('port', metavar='<PORT>', help="ID of port")
def do_port_show(cc, args):
    """Show a port."""
    try:
        port = cc.port.get(args.port)
    except exc.HTTPNotFound:
        raise exc.CommandError('Port not found: %s' % args.port)
    else:
        _print_port_show(port)


def do_port_list(cc, args):
    """List ports."""
    port = cc.port.list()
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
           metavar="<KEY=VALUE>",
           action='append',
           help="Record arbitrary key/value metadata. "
                "Can be specified multiple times.")
def do_port_create(cc, args):
    """Create a new port."""
    field_list = ['address', 'extra', 'node_id']
    fields = dict((k, v) for (k, v) in vars(args).items()
                  if k in field_list and not (v is None))
    fields = utils.args_array_to_dict(fields, 'extra')
    port = cc.port.create(**fields)

    field_list.append('uuid')
    data = dict([(f, getattr(port, f, '')) for f in field_list])
    utils.print_dict(data, wrap=72)


@utils.arg('port', metavar='<port>', help="ID of port")
def do_port_delete(cc, args):
    """Delete a port."""
    try:
        cc.port.delete(args.port)
    except exc.HTTPNotFound:
        raise exc.CommandError('Port not found: %s' % args.port)


@utils.arg('port',
           metavar='<PORT>',
           help="ID of port")
@utils.arg('op',
           metavar='<OP>',
           choices=['add', 'replace', 'remove'],
           help="Operations: 'add', 'replace' or 'remove'")
@utils.arg('attributes',
           metavar='<PATH=VALUE>',
           nargs='+',
           action='append',
           default=[],
           help="Attributes to add/replace or remove "
                "(only PATH is necessary on remove)")
def do_port_update(cc, args):
    """Update a port."""
    patch = utils.args_array_to_patch(args.op, args.attributes[0])
    try:
        port = cc.port.update(args.port, patch)
    except exc.HTTPNotFound:
        raise exc.CommandError('Port not found: %s' % args.port)
    _print_port_show(port)
