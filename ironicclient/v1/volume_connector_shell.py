# Copyright 2017 Hitachi Data Systems
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


def _print_volume_connector_show(volume_connector, fields=None, json=False):
    if fields is None:
        fields = res_fields.VOLUME_CONNECTOR_DETAILED_RESOURCE.fields

    data = dict([(f, getattr(volume_connector, f, '')) for f in fields])
    cliutils.print_dict(data, wrap=72, json_flag=json)


@cliutils.arg(
    'volume_connector',
    metavar='<id>',
    help=_("UUID of the volume connector."))
@cliutils.arg(
    '--fields',
    nargs='+',
    dest='fields',
    metavar='<field>',
    action='append',
    default=[],
    help=_("One or more volume connector fields. Only these fields will be "
           "fetched from the server."))
def do_volume_connector_show(cc, args):
    """Show detailed information about a volume connector."""
    fields = args.fields[0] if args.fields else None
    utils.check_for_invalid_fields(
        fields, res_fields.VOLUME_CONNECTOR_DETAILED_RESOURCE.fields)
    utils.check_empty_arg(args.volume_connector, '<id>')
    volume_connector = cc.volume_connector.get(args.volume_connector,
                                               fields=fields)
    _print_volume_connector_show(volume_connector, fields=fields,
                                 json=args.json)


@cliutils.arg(
    '--detail',
    dest='detail',
    action='store_true',
    default=False,
    help=_("Show detailed information about volume connectors."))
@cliutils.arg(
    '-n', '--node',
    metavar='<node>',
    help=_('Only list volume connectors of this node (name or UUID)'))
@cliutils.arg(
    '--limit',
    metavar='<limit>',
    type=int,
    help=_('Maximum number of volume connectors to return per request, '
           '0 for no limit. Default is the maximum number used '
           'by the Baremetal API Service.'))
@cliutils.arg(
    '--marker',
    metavar='<volume connector>',
    help=_('Volume connector UUID (for example, of the last volume connector '
           'in the list from a previous request). Returns the list of volume '
           'connectors after this UUID.'))
@cliutils.arg(
    '--sort-key',
    metavar='<field>',
    help=_('Volume connector field that will be used for sorting.'))
@cliutils.arg(
    '--sort-dir',
    metavar='<direction>',
    choices=['asc', 'desc'],
    help=_('Sort direction: "asc" (the default) or "desc".'))
@cliutils.arg(
    '--fields',
    nargs='+',
    dest='fields',
    metavar='<field>',
    action='append',
    default=[],
    help=_("One or more volume connector fields. Only these fields will be "
           "fetched from the server. Can not be used when '--detail' is "
           "specified."))
def do_volume_connector_list(cc, args):
    """List the volume connectors."""
    params = {}

    if args.node is not None:
        params['node'] = args.node

    if args.detail:
        fields = res_fields.VOLUME_CONNECTOR_DETAILED_RESOURCE.fields
        field_labels = res_fields.VOLUME_CONNECTOR_DETAILED_RESOURCE.labels
    elif args.fields:
        utils.check_for_invalid_fields(
            args.fields[0],
            res_fields.VOLUME_CONNECTOR_DETAILED_RESOURCE.fields)
        resource = res_fields.Resource(args.fields[0])
        fields = resource.fields
        field_labels = resource.labels
    else:
        fields = res_fields.VOLUME_CONNECTOR_RESOURCE.fields
        field_labels = res_fields.VOLUME_CONNECTOR_RESOURCE.labels

    sort_fields = res_fields.VOLUME_CONNECTOR_DETAILED_RESOURCE.sort_fields
    sort_field_labels = (
        res_fields.VOLUME_CONNECTOR_DETAILED_RESOURCE.sort_labels)

    params.update(utils.common_params_for_list(args,
                                               sort_fields,
                                               sort_field_labels))

    volume_connector = cc.volume_connector.list(**params)
    cliutils.print_list(volume_connector, fields,
                        field_labels=field_labels,
                        sortby_index=None,
                        json_flag=args.json)


@cliutils.arg(
    '-e', '--extra',
    metavar="<key=value>",
    action='append',
    help=_("Record arbitrary key/value metadata. "
           "Can be specified multiple times."))
@cliutils.arg(
    '-n', '--node',
    dest='node_uuid',
    metavar='<node>',
    required=True,
    help=_('UUID of the node that this volume connector belongs to.'))
@cliutils.arg(
    '-t', '--type',
    metavar="<type>",
    required=True,
    choices=['iqn', 'ip', 'mac', 'wwnn', 'wwpn'],
    help=_("Type of the volume connector. Can be 'iqn', 'ip', 'mac', 'wwnn', "
           "'wwpn'."))
@cliutils.arg(
    '-i', '--connector_id',
    metavar="<connector id>",
    required=True,
    help=_("ID of the Volume connector in the specified type."))
@cliutils.arg(
    '-u', '--uuid',
    metavar='<uuid>',
    help=_("UUID of the volume connector."))
def do_volume_connector_create(cc, args):
    """Create a new volume connector."""
    field_list = ['extra', 'type', 'connector_id', 'node_uuid', 'uuid']
    fields = dict((k, v) for (k, v) in vars(args).items()
                  if k in field_list and not (v is None))
    fields = utils.args_array_to_dict(fields, 'extra')
    volume_connector = cc.volume_connector.create(**fields)

    data = dict([(f, getattr(volume_connector, f, '')) for f in field_list])
    cliutils.print_dict(data, wrap=72, json_flag=args.json)


@cliutils.arg('volume_connector', metavar='<volume connector>', nargs='+',
              help=_("UUID of the volume connector."))
def do_volume_connector_delete(cc, args):
    """Delete a volume connector."""
    failures = []
    for vc in args.volume_connector:
        try:
            cc.volume_connector.delete(vc)
            print(_('Deleted volume connector %s') % vc)
        except exceptions.ClientException as e:
            failures.append(_("Failed to delete volume connector %(vc)s: "
                              "%(error)s")
                            % {'vc': vc, 'error': e})
    if failures:
        raise exceptions.ClientException("\n".join(failures))


@cliutils.arg('volume_connector', metavar='<volume connector>',
              help=_("UUID of the volume connector."))
@cliutils.arg(
    'op',
    metavar='<op>',
    choices=['add', 'replace', 'remove'],
    help=_("Operation: 'add', 'replace', or 'remove'."))
@cliutils.arg(
    'attributes',
    metavar='<path=value>',
    nargs='+',
    action='append',
    default=[],
    help=_("Attribute to add, replace, or remove. Can be specified multiple "
           "times. For 'remove', only <path> is necessary."))
def do_volume_connector_update(cc, args):
    """Update information about a volume connector."""
    patch = utils.args_array_to_patch(args.op, args.attributes[0])
    volume_connector = cc.volume_connector.update(args.volume_connector, patch)
    _print_volume_connector_show(volume_connector, json=args.json)
