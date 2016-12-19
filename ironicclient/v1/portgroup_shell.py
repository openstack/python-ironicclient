# Copyright 2015 SAP Ltd.
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


def _print_portgroup_show(portgroup, fields=None, json=False):
    if fields is None:
        fields = res_fields.PORTGROUP_DETAILED_RESOURCE.fields

    data = dict([(f, getattr(portgroup, f, '')) for f in fields])
    cliutils.print_dict(data, wrap=72, json_flag=json)


@cliutils.arg(
    'portgroup',
    metavar='<id>',
    help="Name or UUID of the portgroup "
    "(or MAC address if --address is specified).")
@cliutils.arg(
    '--address',
    dest='address',
    action='store_true',
    default=False,
    help='<id> is the MAC address (instead of the UUID) of the portgroup.')
@cliutils.arg(
    '--fields',
    nargs='+',
    dest='fields',
    metavar='<field>',
    action='append',
    default=[],
    help="One or more portgroup fields. Only these fields will be fetched "
         "from the server.")
def do_portgroup_show(cc, args):
    """Show detailed information about a portgroup."""
    fields = args.fields[0] if args.fields else None
    utils.check_for_invalid_fields(
        fields, res_fields.PORTGROUP_DETAILED_RESOURCE.fields)
    if args.address:
        portgroup = cc.portgroup.get_by_address(args.portgroup, fields=fields)
    else:
        utils.check_empty_arg(args.portgroup, '<id>')
        portgroup = cc.portgroup.get(args.portgroup, fields=fields)
    _print_portgroup_show(portgroup, fields=fields, json=args.json)


@cliutils.arg(
    '--detail',
    dest='detail',
    action='store_true',
    default=False,
    help="Show detailed information about portgroups.")
@cliutils.arg(
    '-n', '--node',
    dest='node',
    metavar='<node>',
    help='UUID of the node that this portgroup belongs to.')
@cliutils.arg(
    '-a', '--address',
    metavar='<mac-address>',
    help='Only show information for the portgroup with this MAC address.')
@cliutils.arg(
    '--limit',
    metavar='<limit>',
    type=int,
    help='Maximum number of portgroups to return per request, '
         '0 for no limit. Default is the maximum number used '
         'by the Ironic API Service.')
@cliutils.arg(
    '--marker',
    metavar='<portgroup>',
    help='Portgroup UUID (for example, of the last portgroup in the list '
         'from a previous request). '
         'Returns the list of portgroups after this UUID.')
@cliutils.arg(
    '--sort-key',
    metavar='<field>',
    help='Portgroup field that will be used for sorting.')
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
    help="One or more portgroup fields. Only these fields will be fetched "
         "from the server. Can not be used when '--detail' is specified.")
def do_portgroup_list(cc, args):
    """List the portgroups."""
    params = {}

    if args.address is not None:
        params['address'] = args.address
    if args.node is not None:
        params['node'] = args.node

    if args.detail:
        fields = res_fields.PORTGROUP_DETAILED_RESOURCE.fields
        field_labels = res_fields.PORTGROUP_DETAILED_RESOURCE.labels
    elif args.fields:
        utils.check_for_invalid_fields(
            args.fields[0], res_fields.PORTGROUP_DETAILED_RESOURCE.fields)
        resource = res_fields.Resource(args.fields[0])
        fields = resource.fields
        field_labels = resource.labels
    else:
        fields = res_fields.PORTGROUP_RESOURCE.fields
        field_labels = res_fields.PORTGROUP_RESOURCE.labels

    sort_fields = res_fields.PORTGROUP_DETAILED_RESOURCE.sort_fields
    sort_field_labels = res_fields.PORTGROUP_DETAILED_RESOURCE.sort_labels

    params.update(utils.common_params_for_list(args,
                                               sort_fields,
                                               sort_field_labels))

    portgroup = cc.portgroup.list(**params)
    cliutils.print_list(portgroup, fields,
                        field_labels=field_labels,
                        sortby_index=None,
                        json_flag=args.json)


@cliutils.arg(
    '-a', '--address',
    metavar='<address>',
    help='MAC address for this portgroup.')
@cliutils.arg(
    '-n', '--node',
    dest='node_uuid',
    metavar='<node>',
    required=True,
    help='UUID of the node that this portgroup belongs to.')
@cliutils.arg(
    '--name',
    metavar="<name>",
    help='Name for the portgroup.')
@cliutils.arg(
    '-e', '--extra',
    metavar="<key=value>",
    action='append',
    help="Record arbitrary key/value metadata. "
         "Can be specified multiple times.")
@cliutils.arg(
    '--standalone-ports-supported',
    metavar="<boolean>",
    help='Specifies whether ports from this portgroup can be used '
         'in stand alone mode.')
@cliutils.arg(
    '-u', '--uuid',
    metavar='<uuid>',
    help="UUID of the portgroup.")
@cliutils.arg(
    '-m', '--mode',
    metavar='<mode>',
    help="Portgroup mode. For possible values, refer to "
         "https://www.kernel.org/doc/Documentation/networking/bonding.txt")
@cliutils.arg(
    '-p', '--properties',
    metavar="<key=value>",
    action='append',
    help="Record key/value properties related to this portgroup's "
         "configuration.")
def do_portgroup_create(cc, args):
    """Create a new portgroup."""
    field_list = ['address', 'extra', 'node_uuid', 'name', 'uuid',
                  'standalone_ports_supported', 'mode', 'properties']
    fields = dict((k, v) for (k, v) in vars(args).items()
                  if k in field_list and not (v is None))
    fields = utils.args_array_to_dict(fields, 'extra')
    fields = utils.args_array_to_dict(fields, 'properties')
    portgroup = cc.portgroup.create(**fields)

    data = dict([(f, getattr(portgroup, f, '')) for f in field_list])
    cliutils.print_dict(data, wrap=72, json_flag=args.json)


@cliutils.arg(
    '--detail',
    dest='detail',
    action='store_true',
    default=False,
    help="Show detailed information about the ports.")
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
    'portgroup',
    metavar='<portgroup>',
    help="Name or UUID of the portgroup.")
@cliutils.arg(
    '--fields',
    nargs='+',
    dest='fields',
    metavar='<field>',
    action='append',
    default=[],
    help="One or more port fields. Only these fields will be fetched from "
         "the server. Can not be used when '--detail' is specified.")
def do_portgroup_port_list(cc, args):
    """List the ports associated with a portgroup."""
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

    params = utils.common_params_for_list(args, sort_fields,
                                          sort_field_labels)

    ports = cc.portgroup.list_ports(args.portgroup, **params)

    cliutils.print_list(ports, fields,
                        field_labels=field_labels,
                        sortby_index=None,
                        json_flag=args.json)


@cliutils.arg('portgroup', metavar='<portgroup>', nargs='+',
              help="UUID or Name of the portgroup.")
def do_portgroup_delete(cc, args):
    """Delete a portgroup."""
    failures = []
    for p in args.portgroup:
        try:
            cc.portgroup.delete(p)
            print('Deleted portgroup %s' % p)
        except exceptions.ClientException as e:
            failures.append(_("Failed to delete portgroup %(pg)s: %(error)s")
                            % {'pg': p, 'error': e})
    if failures:
        raise exceptions.ClientException("\n".join(failures))


@cliutils.arg('portgroup', metavar='<portgroup>',
              help="UUID or Name of the portgroup.")
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
def do_portgroup_update(cc, args):
    """Update information about a portgroup."""
    patch = utils.args_array_to_patch(args.op, args.attributes[0])
    portgroup = cc.portgroup.update(args.portgroup, patch)
    _print_portgroup_show(portgroup, json=args.json)
