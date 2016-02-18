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

from ironicclient.common import cliutils
from ironicclient.common import utils
from ironicclient.v1 import resource_fields as res_fields


def _print_chassis_show(chassis, fields=None, json=False):
    if fields is None:
        fields = res_fields.CHASSIS_DETAILED_RESOURCE.fields

    data = dict([(f, getattr(chassis, f, '')) for f in fields])
    cliutils.print_dict(data, wrap=72, json_flag=json)


@cliutils.arg('chassis', metavar='<chassis>', help="UUID of the chassis.")
@cliutils.arg(
    '--fields',
    nargs='+',
    dest='fields',
    metavar='<field>',
    action='append',
    default=[],
    help="One or more chassis fields. Only these fields will be fetched from "
         "the server.")
def do_chassis_show(cc, args):
    """Show detailed information about a chassis."""
    utils.check_empty_arg(args.chassis, '<chassis>')
    fields = args.fields[0] if args.fields else None
    utils.check_for_invalid_fields(
        fields, res_fields.CHASSIS_DETAILED_RESOURCE.fields)
    chassis = cc.chassis.get(args.chassis, fields=fields)
    _print_chassis_show(chassis, fields=fields, json=args.json)


@cliutils.arg(
    '--detail',
    dest='detail',
    action='store_true',
    default=False,
    help="Show detailed information about the chassis.")
@cliutils.arg(
    '--limit',
    metavar='<limit>',
    type=int,
    help='Maximum number of chassis to return per request, '
         '0 for no limit. Default is the maximum number used '
         'by the Ironic API Service.')
@cliutils.arg(
    '--marker',
    metavar='<chassis>',
    help='Chassis UUID (for example, of the last chassis in the list '
         'from a previous request). Returns the list of chassis '
         'after this UUID.')
@cliutils.arg(
    '--sort-key',
    metavar='<field>',
    help='Chassis field that will be used for sorting.')
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
    help="One or more chassis fields. Only these fields will be fetched from "
         "the server. Can not be used when '--detail' is specified.")
def do_chassis_list(cc, args):
    """List the chassis."""
    if args.detail:
        fields = res_fields.CHASSIS_DETAILED_RESOURCE.fields
        field_labels = res_fields.CHASSIS_DETAILED_RESOURCE.labels
    elif args.fields:
        utils.check_for_invalid_fields(
            args.fields[0], res_fields.CHASSIS_DETAILED_RESOURCE.fields)
        resource = res_fields.Resource(args.fields[0])
        fields = resource.fields
        field_labels = resource.labels
    else:
        fields = res_fields.CHASSIS_RESOURCE.fields
        field_labels = res_fields.CHASSIS_RESOURCE.labels

    sort_fields = res_fields.CHASSIS_DETAILED_RESOURCE.sort_fields
    sort_field_labels = res_fields.CHASSIS_DETAILED_RESOURCE.sort_labels

    params = utils.common_params_for_list(args, sort_fields,
                                          sort_field_labels)

    chassis = cc.chassis.list(**params)
    cliutils.print_list(chassis, fields,
                        field_labels=field_labels,
                        sortby_index=None,
                        json_flag=args.json)


@cliutils.arg(
    '-d', '--description',
    metavar='<description>',
    help='Description of the chassis.')
@cliutils.arg(
    '-e', '--extra',
    metavar="<key=value>",
    action='append',
    help="Record arbitrary key/value metadata. "
         "Can be specified multiple times.")
@cliutils.arg(
    '-u', '--uuid',
    metavar='<uuid>',
    help="UUID of the chassis.")
def do_chassis_create(cc, args):
    """Create a new chassis."""
    field_list = ['description', 'extra', 'uuid']
    fields = dict((k, v) for (k, v) in vars(args).items()
                  if k in field_list and not (v is None))
    fields = utils.args_array_to_dict(fields, 'extra')
    chassis = cc.chassis.create(**fields)

    data = dict([(f, getattr(chassis, f, '')) for f in field_list])
    cliutils.print_dict(data, wrap=72, json_flag=args.json)


@cliutils.arg(
    'chassis',
    metavar='<chassis>',
    nargs='+',
    help="UUID of the chassis.")
def do_chassis_delete(cc, args):
    """Delete a chassis."""
    for c in args.chassis:
        cc.chassis.delete(c)
        print('Deleted chassis %s' % c)


@cliutils.arg('chassis', metavar='<chassis>', help="UUID of the chassis.")
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
    help="Attribute to add, replace, or remove. Can be specified "
         "multiple times. For 'remove', only <path> is necessary.")
def do_chassis_update(cc, args):
    """Update information about a chassis."""
    patch = utils.args_array_to_patch(args.op, args.attributes[0])
    chassis = cc.chassis.update(args.chassis, patch)
    _print_chassis_show(chassis, json=args.json)


@cliutils.arg(
    '--detail',
    dest='detail',
    action='store_true',
    default=False,
    help="Show detailed information about the nodes.")
@cliutils.arg(
    '--limit',
    metavar='<limit>',
    type=int,
    help='Maximum number of nodes to return per request, '
         '0 for no limit. Default is the maximum number used '
         'by the Ironic API Service.')
@cliutils.arg(
    '--marker',
    metavar='<node>',
    help='Node UUID (for example, of the last node in the list from '
         'a previous request). Returns the list of nodes after this UUID.')
@cliutils.arg(
    '--sort-key',
    metavar='<field>',
    help='Node field that will be used for sorting.')
@cliutils.arg(
    '--sort-dir',
    metavar='<direction>',
    choices=['asc', 'desc'],
    help='Sort direction: "asc" (the default) or "desc".')
@cliutils.arg('chassis', metavar='<chassis>', help="UUID of the chassis.")
@cliutils.arg(
    '--fields',
    nargs='+',
    dest='fields',
    metavar='<field>',
    action='append',
    default=[],
    help="One or more node fields. Only these fields will be fetched from "
         "the server. Can not be used when '--detail' is specified.")
@cliutils.arg(
    '--maintenance',
    metavar='<boolean>',
    help="List nodes in maintenance mode: 'true' or 'false'.")
@cliutils.arg(
    '--associated',
    metavar='<boolean>',
    help="List nodes by instance association: 'true' or 'false'.")
@cliutils.arg(
    '--provision-state',
    metavar='<provision-state>',
    help="List nodes in specified provision state.")
def do_chassis_node_list(cc, args):
    """List the nodes contained in a chassis."""
    params = {}
    if args.associated is not None:
        params['associated'] = utils.bool_argument_value("--associated",
                                                         args.associated)
    if args.maintenance is not None:
        params['maintenance'] = utils.bool_argument_value("--maintenance",
                                                          args.maintenance)
    if args.provision_state is not None:
        params['provision_state'] = args.provision_state

    if args.detail:
        fields = res_fields.NODE_DETAILED_RESOURCE.fields
        field_labels = res_fields.NODE_DETAILED_RESOURCE.labels
    elif args.fields:
        utils.check_for_invalid_fields(
            args.fields[0], res_fields.NODE_DETAILED_RESOURCE.fields)
        resource = res_fields.Resource(args.fields[0])
        fields = resource.fields
        field_labels = resource.labels
    else:
        fields = res_fields.NODE_RESOURCE.fields
        field_labels = res_fields.NODE_RESOURCE.labels

    sort_fields = res_fields.NODE_DETAILED_RESOURCE.sort_fields
    sort_field_labels = res_fields.NODE_DETAILED_RESOURCE.sort_labels

    params.update(utils.common_params_for_list(args,
                                               sort_fields,
                                               sort_field_labels))

    nodes = cc.chassis.list_nodes(args.chassis, **params)
    cliutils.print_list(nodes, fields,
                        field_labels=field_labels,
                        sortby_index=None,
                        json_flag=args.json)
