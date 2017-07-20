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

from ironicclient.common.apiclient import exceptions
from ironicclient.common import cliutils
from ironicclient.common.i18n import _
from ironicclient.common import utils
from ironicclient.v1 import resource_fields as res_fields


def _print_port_show(port, fields=None, json=False):
    if fields is None:
        fields = res_fields.PORT_DETAILED_RESOURCE.fields

    data = dict([(f, getattr(port, f, '')) for f in fields])
    cliutils.print_dict(data, wrap=72, json_flag=json)


@cliutils.arg(
    'port',
    metavar='<id>',
    help="UUID of the port (or MAC address if --address is specified).")
@cliutils.arg(
    '--address',
    dest='address',
    action='store_true',
    default=False,
    help='<id> is the MAC address (instead of the UUID) of the port.')
@cliutils.arg(
    '--fields',
    nargs='+',
    dest='fields',
    metavar='<field>',
    action='append',
    default=[],
    help="One or more port fields. Only these fields will be fetched from "
         "the server.")
def do_port_show(cc, args):
    """Show detailed information about a port."""
    fields = args.fields[0] if args.fields else None
    utils.check_for_invalid_fields(
        fields, res_fields.PORT_DETAILED_RESOURCE.fields)
    if args.address:
        port = cc.port.get_by_address(args.port, fields=fields)
    else:
        utils.check_empty_arg(args.port, '<id>')
        port = cc.port.get(args.port, fields=fields)
    _print_port_show(port, fields=fields, json=args.json)


@cliutils.arg(
    '--detail',
    dest='detail',
    action='store_true',
    default=False,
    help="Show detailed information about ports.")
@cliutils.arg(
    '--address',
    metavar='<mac-address>',
    help='Only show information for the port with this MAC address.')
@cliutils.arg(
    '--limit',
    metavar='<limit>',
    type=int,
    help='Maximum number of ports to return per request, '
         '0 for no limit. Default is the maximum number used '
         'by the Ironic API Service.')
@cliutils.arg(
    '--marker',
    metavar='<port>',
    help='Port UUID (for example, of the last port in the list from a '
         'previous request). Returns the list of ports after this UUID.')
@cliutils.arg(
    '--sort-key',
    metavar='<field>',
    help='Port field that will be used for sorting.')
@cliutils.arg(
    '--sort-dir',
    metavar='<direction>',
    choices=['asc', 'desc'],
    help='Sort direction: "asc" (the default) or "desc".')
@cliutils.arg(
    '--fields',
    nargs='+',
    dest='fields',
    metavar='<field>',
    action='append',
    default=[],
    help="One or more port fields. Only these fields will be fetched from "
         "the server. Can not be used when '--detail' is specified.")
def do_port_list(cc, args):
    """List the ports."""
    params = {}

    if args.address is not None:
        params['address'] = args.address

    if args.detail:
        fields = res_fields.PORT_DETAILED_RESOURCE.fields
        field_labels = res_fields.PORT_DETAILED_RESOURCE.labels
    elif args.fields:
        utils.check_for_invalid_fields(
            args.fields[0], res_fields.PORT_DETAILED_RESOURCE.fields)
        resource = res_fields.Resource(args.fields[0])
        fields = resource.fields
        field_labels = resource.labels
    else:
        fields = res_fields.PORT_RESOURCE.fields
        field_labels = res_fields.PORT_RESOURCE.labels

    sort_fields = res_fields.PORT_DETAILED_RESOURCE.sort_fields
    sort_field_labels = res_fields.PORT_DETAILED_RESOURCE.sort_labels

    params.update(utils.common_params_for_list(args,
                                               sort_fields,
                                               sort_field_labels))

    port = cc.port.list(**params)
    cliutils.print_list(port, fields,
                        field_labels=field_labels,
                        sortby_index=None,
                        json_flag=args.json)


@cliutils.arg(
    '-a', '--address',
    metavar='<address>',
    required=True,
    help='MAC address for this port.')
@cliutils.arg(
    '-n', '--node', '--node_uuid',
    dest='node_uuid',
    metavar='<node>',
    required=True,
    help='UUID of the node that this port belongs to.')
@cliutils.arg(
    '-l', '--local-link-connection',
    metavar="<key=value>",
    action='append',
    help="Key/value metadata describing Local link connection information. "
    "Valid keys are switch_info, switch_id, port_id."
    "Can be specified multiple times.")
@cliutils.arg(
    '--portgroup',
    metavar="<portgroup>",
    dest='portgroup_uuid',
    help='UUID of the portgroup that this port belongs to.')
@cliutils.arg(
    '--pxe-enabled',
    metavar='<boolean>',
    help='Indicates whether this Port should be used when '
         'PXE booting this Node.')
@cliutils.arg(
    '--physical-network',
    metavar='<physical network>',
    help="Physical network of the port.")
@cliutils.arg(
    '-e', '--extra',
    metavar="<key=value>",
    action='append',
    help="Record arbitrary key/value metadata. "
         "Can be specified multiple times.")
@cliutils.arg(
    '-u', '--uuid',
    metavar='<uuid>',
    help="UUID of the port.")
def do_port_create(cc, args):
    """Create a new port."""
    field_list = ['address', 'extra', 'node_uuid', 'uuid',
                  'local_link_connection', 'portgroup_uuid',
                  'pxe_enabled', 'physical_network']
    fields = dict((k, v) for (k, v) in vars(args).items()
                  if k in field_list and not (v is None))
    fields = utils.args_array_to_dict(fields, 'extra')
    fields = utils.args_array_to_dict(fields, 'local_link_connection')
    port = cc.port.create(**fields)

    data = dict([(f, getattr(port, f, '')) for f in field_list])
    cliutils.print_dict(data, wrap=72, json_flag=args.json)


@cliutils.arg('port', metavar='<port>', nargs='+', help="UUID of the port.")
def do_port_delete(cc, args):
    """Delete a port."""
    failures = []
    for p in args.port:
        try:
            cc.port.delete(p)
            print(_('Deleted port %s') % p)
        except exceptions.ClientException as e:
            failures.append(_("Failed to delete port %(port)s: %(error)s")
                            % {'port': p, 'error': e})
    if failures:
        raise exceptions.ClientException("\n".join(failures))


@cliutils.arg('port', metavar='<port>', help="UUID of the port.")
@cliutils.arg(
    'op',
    metavar='<op>',
    choices=['add', 'replace', 'remove'],
    help="Operation: 'add', 'replace', or 'remove'.")
@cliutils.arg(
    'attributes',
    metavar='<path=value>',
    nargs='+',
    action='append',
    default=[],
    help="Attribute to add, replace, or remove. Can be specified multiple  "
         "times. For 'remove', only <path> is necessary.")
def do_port_update(cc, args):
    """Update information about a port."""
    patch = utils.args_array_to_patch(args.op, args.attributes[0])
    port = cc.port.update(args.port, patch)
    _print_port_show(port, json=args.json)
